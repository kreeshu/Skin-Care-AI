import os

import numpy as np
import pandas as pd
import tensorflow as tf

from src.model.concern_model import CONCERNS


def read_manifest(path):
    frame = pd.read_csv(path)
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


def build_concern_dataset(manifest, img_size=224, batch_size=32, augment=False, shuffle=False):
    paths, labels, weights = read_manifest(manifest)
    augmentation = tf.keras.Sequential(
        [tf.keras.layers.RandomFlip("horizontal"), tf.keras.layers.RandomRotation(0.03),
         tf.keras.layers.RandomContrast(0.1)],
        name="mild_augmentation",
    )

    def load(path, label, weight):
        image = tf.io.decode_image(tf.io.read_file(path), channels=3, expand_animations=False)
        image.set_shape((None, None, 3))
        image = tf.image.resize(image, (img_size, img_size))
        if augment:
            image = augmentation(image, training=True)
        image = tf.keras.applications.efficientnet.preprocess_input(image)
        return image, {"labels": label, "weights": weight}

    dataset = tf.data.Dataset.from_tensor_slices((paths, labels, weights))
    if shuffle:
        dataset = dataset.shuffle(max(1, len(paths)), reshuffle_each_iteration=True)
    dataset = dataset.map(load, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
