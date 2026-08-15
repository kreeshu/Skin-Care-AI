import math
import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple

IMG_SIZE = 224
BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE
IGNORE = -1  # masked-task label sentinel


def load_dataset(data_dir: str) -> Tuple[List[str], List[int], List[str]]:
    """Load images from a class-folder structure. Returns (paths, labels, class_names)."""
    class_names = sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
    ])
    if not class_names:
        raise ValueError(f"No class folders found under {data_dir}")
    class_to_idx = {name: i for i, name in enumerate(class_names)}

    paths, labels = [], []
    for name in class_names:
        class_dir = os.path.join(data_dir, name)
        for fname in os.listdir(class_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                paths.append(os.path.join(class_dir, fname))
                labels.append(class_to_idx[name])

    print(f"[{os.path.basename(data_dir)}] {len(paths)} images, "
          f"{len(class_names)} classes: {class_names}")
    return paths, labels, class_names


def split_dataset(
    paths: List[str],
    labels: List[int],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
):
    """Stratified split into train/val/test."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    train_paths, temp_paths, train_labels, temp_labels = train_test_split(
        paths, labels, test_size=(1 - train_ratio), stratify=labels, random_state=random_state
    )
    relative_test = test_ratio / (val_ratio + test_ratio)
    val_paths, test_paths, val_labels, test_labels = train_test_split(
        temp_paths, temp_labels, test_size=relative_test, stratify=temp_labels, random_state=random_state
    )
    print(f"  split: train={len(train_paths)}, val={len(val_paths)}, test={len(test_paths)}")
    return (train_paths, train_labels), (val_paths, val_labels), (test_paths, test_labels)


def build_data_pipeline(
    paths: List[str],
    labels: List[int],
    img_size: int = IMG_SIZE,
    batch_size: int = BATCH_SIZE,
    augment: bool = False,
) -> tf.data.Dataset:
    """tf.data pipeline with decode (jpg+png), resize, EfficientNet preprocessing."""

    def load_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img = tf.image.resize(img, [img_size, img_size])
        img = tf.keras.applications.efficientnet.preprocess_input(img)
        return img, label

    path_tensor = tf.constant(paths, dtype=tf.string)
    label_tensor = tf.constant(labels, dtype=tf.int32)
    ds = tf.data.Dataset.from_tensor_slices((path_tensor, label_tensor))
    ds = ds.map(load_and_preprocess, num_parallel_calls=AUTOTUNE)

    if augment:
        from src.model.augmentations import get_augmentation_pipeline
        aug = get_augmentation_pipeline()
        ds = ds.map(lambda img, lbl: (aug(img, training=True), lbl), num_parallel_calls=AUTOTUNE)

    ds = ds.shuffle(buffer_size=min(len(paths), 1024))
    ds = ds.batch(batch_size).prefetch(AUTOTUNE)
    return ds


def _tag(ds: tf.data.Dataset, task: str) -> tf.data.Dataset:
    """Attach dict labels {condition, skin_type} with the other task masked to IGNORE."""

    def map_fn(img, lbl):
        ignored = tf.zeros_like(lbl) - 1  # int32 sentinel, same shape as lbl
        if task == "condition":
            return img, {"condition": lbl, "skin_type": ignored}
        return img, {"condition": ignored, "skin_type": lbl}

    return ds.map(map_fn, num_parallel_calls=AUTOTUNE)


def _class_weights(labels: List[int], num_classes: int) -> np.ndarray:
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.arange(num_classes)
    return compute_class_weight("balanced", classes=classes, y=np.asarray(labels)).astype(np.float32)


def prepare_multitask_datasets(
    conditions_dir: str,
    types_dir: str,
    img_size: int = IMG_SIZE,
    batch_size: int = BATCH_SIZE,
    cond_sample_weight: float = 1.0,
    type_sample_weight: float = 4.0,
) -> Dict:
    """Build per-task pipelines, then interleave them into one training stream.

    The skin-type dataset is tiny (~112 images), so it is over-sampled so that
    each epoch covers all condition batches plus `type_sample_weight` passes of
    the type batches. Batches are then shuffled at batch level and the stream is
    repeated for multi-epoch iteration. Every batch is homogeneous (one task)
    and only the owning head receives gradient signal for it.
    """
    cond_paths, cond_labels, cond_names = load_dataset(conditions_dir)
    type_paths, type_labels, type_names = load_dataset(types_dir)

    (ctr_p, ctr_l), (cva_p, cva_l), (cte_p, cte_l) = split_dataset(cond_paths, cond_labels)
    (ttr_p, ttr_l), (tva_p, tva_l), (tte_p, tte_l) = split_dataset(type_paths, type_labels)

    cond_train = _tag(build_data_pipeline(ctr_p, ctr_l, img_size, batch_size, augment=True), "condition")
    cond_val = _tag(build_data_pipeline(cva_p, cva_l, img_size, batch_size, augment=False), "condition")
    cond_test = _tag(build_data_pipeline(cte_p, cte_l, img_size, batch_size, augment=False), "condition")

    type_train = _tag(build_data_pipeline(ttr_p, ttr_l, img_size, batch_size, augment=True), "skin_type")
    type_val = _tag(build_data_pipeline(tva_p, tva_l, img_size, batch_size, augment=False), "skin_type")
    type_test = _tag(build_data_pipeline(tte_p, tte_l, img_size, batch_size, augment=False), "skin_type")

    # The skin-type dataset is tiny. Oversample it so each epoch sees all
    # condition batches plus `type_sample_weight` passes of the type batches,
    # then shuffle at batch level and repeat for multi-epoch iteration.
    cond_batches = math.ceil(len(ctr_p) / batch_size)
    type_batches = math.ceil(len(ttr_p) / batch_size)
    type_repeats = max(1, int(round(type_sample_weight)))
    steps_per_epoch = cond_batches + type_batches * type_repeats

    train_ds = cond_train.concatenate(type_train.repeat(type_repeats))
    train_ds = train_ds.shuffle(buffer_size=min(steps_per_epoch, 512)).repeat()

    cond_class_weight = _class_weights(ctr_l, len(cond_names))

    return {
        "train": train_ds,
        "val_sets": {"condition": cond_val, "skin_type": type_val},
        "test": {"condition": cond_test, "skin_type": type_test},
        "class_names": {"condition": cond_names, "skin_type": type_names},
        "cond_class_weight": cond_class_weight,
        "steps_per_epoch": steps_per_epoch,
        "num_conditions": len(cond_names),
        "num_skin_types": len(type_names),
    }
