"""Shared training, evaluation, and serving preprocessing."""

import tensorflow as tf


def preprocess_concern_image(image, img_size=224):
    image = tf.convert_to_tensor(image)
    image = tf.image.resize(image, (img_size, img_size), method="bilinear")
    return tf.keras.applications.efficientnet.preprocess_input(image)
