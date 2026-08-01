import tensorflow as tf


def get_augmentation_pipeline() -> tf.keras.Sequential:
    """Medium augmentation: flip, rotation, zoom, brightness, contrast."""
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.15),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.1),
        tf.keras.layers.RandomContrast(0.1),
    ], name="data_augmentation")
