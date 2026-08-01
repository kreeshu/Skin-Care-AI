import tensorflow as tf
from typing import Tuple


def build_efficientnet_model(
    num_classes: int,
    img_size: int = 224,
    dropout_rate: float = 0.3,
) -> tf.keras.Model:
    """Build EfficientNetB0 with transfer learning head."""
    base_model = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(img_size, img_size, 3),
        pooling=None,
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(img_size, img_size, 3))
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(dropout_rate)(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs, name="skin_classifier")
    return model, base_model


def unfreeze_base_model(model: tf.keras.Model, base_model: tf.keras.Model, num_layers: int = 30):
    """Unfreeze the last `num_layers` layers of the base model for fine-tuning."""
    base_model.trainable = True
    for layer in base_model.layers[:-num_layers]:
        layer.trainable = False

    trainable = sum(1 for l in model.layers if l.trainable)
    total = len(model.layers)
    print(f"Unfroze last {num_layers} layers. Trainable: {trainable}/{total}")
