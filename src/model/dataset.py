import tensorflow as tf
import os
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple, List


IMG_SIZE = 224
BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE


def load_dataset(data_dir: str, img_size: int = IMG_SIZE) -> Tuple[List[str], List[int], List[str]]:
    """Load images from class-folder structure. Returns (paths, labels, class_names)."""
    class_names = sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
    ])
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}

    paths, labels = [], []
    for class_name in class_names:
        class_dir = os.path.join(data_dir, class_name)
        for fname in os.listdir(class_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                paths.append(os.path.join(class_dir, fname))
                labels.append(class_to_idx[class_name])

    print(f"Loaded {len(paths)} images across {len(class_names)} classes: {class_names}")
    return paths, labels, class_names


def split_dataset(
    paths: List[str],
    labels: List[int],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Tuple:
    """Stratified split into train/val/test."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    train_paths, temp_paths, train_labels, temp_labels = train_test_split(
        paths, labels, test_size=(1 - train_ratio), stratify=labels, random_state=random_state
    )
    relative_test = test_ratio / (val_ratio + test_ratio)
    val_paths, test_paths, val_labels, test_labels = train_test_split(
        temp_paths, temp_labels, test_size=relative_test, stratify=temp_labels, random_state=random_state
    )

    print(f"Split: train={len(train_paths)}, val={len(val_paths)}, test={len(test_paths)}")
    return (train_paths, train_labels), (val_paths, val_labels), (test_paths, test_labels)


def build_data_pipeline(
    paths: List[str],
    labels: List[int],
    img_size: int = IMG_SIZE,
    batch_size: int = BATCH_SIZE,
    augment: bool = False,
) -> tf.data.Dataset:
    """Build a tf.data pipeline with optional augmentation."""
    label_tensor = tf.constant(labels, dtype=tf.int32)

    def load_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, [img_size, img_size])
        img = tf.keras.applications.efficientnet.preprocess_input(img)
        return img, label

    path_tensor = tf.constant(paths, dtype=tf.string)
    dataset = tf.data.Dataset.from_tensor_slices((path_tensor, label_tensor))
    dataset = dataset.map(load_and_preprocess, num_parallel_calls=AUTOTUNE)

    if augment:
        from src.model.augmentations import get_augmentation_pipeline
        aug_pipeline = get_augmentation_pipeline()
        dataset = dataset.map(
            lambda img, label: (aug_pipeline(img, training=True), label),
            num_parallel_calls=AUTOTUNE
        )

    dataset = dataset.shuffle(buffer_size=len(paths))
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(AUTOTUNE)
    return dataset


def prepare_datasets(
    data_dir: str,
    img_size: int = IMG_SIZE,
    batch_size: int = BATCH_SIZE,
) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset, List[str]]:
    """Full pipeline: load → split → build datasets."""
    paths, labels, class_names = load_dataset(data_dir, img_size)
    (train_paths, train_labels), (val_paths, val_labels), (test_paths, test_labels) = split_dataset(paths, labels)

    train_ds = build_data_pipeline(train_paths, train_labels, img_size, batch_size, augment=True)
    val_ds = build_data_pipeline(val_paths, val_labels, img_size, batch_size, augment=False)
    test_ds = build_data_pipeline(test_paths, test_labels, img_size, batch_size, augment=False)

    return train_ds, val_ds, test_ds, class_names
