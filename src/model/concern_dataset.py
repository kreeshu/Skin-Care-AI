import os

import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image

from src.model.concern_model import CONCERNS
from src.model.concern_preprocessing import preprocess_concern_image


def read_manifest(path):
    frame = pd.read_csv(path)
    for name in CONCERNS:
        # Reviewed gold manifests carry no weights: every label is human-verified.
        if name + "_weight" not in frame:
            frame[name + "_weight"] = 1.0
    required = ["original_path"] + list(CONCERNS) + [name + "_weight" for name in CONCERNS]
    missing = [column for column in required if column not in frame]
    if missing:
        raise ValueError("Missing manifest columns: " + ", ".join(missing))
    paths = frame["original_path"].astype(str).tolist()
    base = os.path.dirname(os.path.abspath(path))
    paths = [value if os.path.isabs(value) else os.path.join(base, value) for value in paths]
    labels = frame[list(CONCERNS)].to_numpy(dtype=np.float32)
    weights = frame[[name + "_weight" for name in CONCERNS]].to_numpy(dtype=np.float32)
    weights[labels < 0] = 0.0
    return paths, labels, weights


def balanced_label_weights(labels, weights):
    """Balance observed classes per concern; never turn unknowns into negatives."""
    result = weights.copy()
    for index in range(len(CONCERNS)):
        counts = [np.count_nonzero((labels[:, index] == value) & (weights[:, index] > 0))
                  for value in (0, 1)]
        if min(counts) == 0:
            continue
        for value, count in enumerate(counts):
            result[labels[:, index] == value, index] *= sum(counts) / (2.0 * count)
    result[labels < 0] = 0.0
    return result


def build_concern_dataset(manifest, img_size=224, batch_size=32, augment=False, shuffle=False,
                          balance_labels=False):
    paths, labels, weights = read_manifest(manifest)
    if balance_labels:
        weights = balanced_label_weights(labels, weights)
    augmentation = tf.keras.Sequential(
        [tf.keras.layers.RandomFlip("horizontal"), tf.keras.layers.RandomRotation(0.03),
         tf.keras.layers.RandomContrast(0.1)],
        name="mild_augmentation",
    )

    def load(path, label, weight):
        # PIL, not tf.io.decode_image: some source files are WebP saved with a .png extension.
        image = tf.numpy_function(lambda p: np.asarray(Image.open(p.decode()).convert("RGB")), [path], tf.uint8)
        image.set_shape((None, None, 3))  # numpy_function loses static shape
        image = preprocess_concern_image(image, img_size)
        if augment:
            image = augmentation(image, training=True)
        return image, {"labels": label, "weights": weight}

    dataset = tf.data.Dataset.from_tensor_slices((paths, labels, weights))
    if shuffle:
        dataset = dataset.shuffle(max(1, len(paths)), reshuffle_each_iteration=True)
    dataset = dataset.map(load, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
