import os

import tensorflow as tf


CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def weighted_masked_bce(labels, predictions, weights):
    """Weighted BCE averaged over known labels; -1 labels are ignored."""
    labels = tf.cast(labels, tf.float32)
    weights = tf.cast(weights, tf.float32) * tf.cast(labels >= 0, tf.float32)
    safe_labels = tf.maximum(labels, 0.0)
    loss = tf.keras.backend.binary_crossentropy(safe_labels, predictions)
    return tf.math.divide_no_nan(tf.reduce_sum(loss * weights), tf.reduce_sum(weights))


class ConcernModel(tf.keras.Model):
    def __init__(self, img_size=224, dropout=0.3, pretrained=True, **kwargs):
        super().__init__(name="skin_concern", **kwargs)
        self.backbone = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights="imagenet" if pretrained else None,
            input_shape=(img_size, img_size, 3),
        )
        self.backbone.trainable = False
        self.head = tf.keras.Sequential(
            [
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dropout(dropout),
                tf.keras.layers.Dense(128, activation="relu"),
                tf.keras.layers.Dense(len(CONCERNS), activation="sigmoid"),
            ],
            name="concern_head",
        )
        self.loss_tracker = tf.keras.metrics.Mean(name="loss")

    @property
    def metrics(self):
        return [self.loss_tracker]

    def call(self, images, training=False):
        return self.head(self.backbone(images, training=training), training=training)

    def _step(self, data, training):
        images, targets, _ = tf.keras.utils.unpack_x_y_sample_weight(data)
        with tf.GradientTape() as tape:
            predictions = self(images, training=training)
            loss = weighted_masked_bce(targets["labels"], predictions, targets["weights"])
            if self.losses:
                loss += tf.add_n(self.losses)
        if training:
            gradients = tape.gradient(loss, self.trainable_variables)
            self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def train_step(self, data):
        return self._step(data, True)

    def test_step(self, data):
        return self._step(data, False)

    def unfreeze_top(self, layers=30):
        self.backbone.trainable = True
        for layer in self.backbone.layers[:-layers]:
            layer.trainable = False

    def save_concern_weights(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.save_weights(path)


def build_concern_model(img_size=224, dropout=0.3, pretrained=True):
    return ConcernModel(img_size=img_size, dropout=dropout, pretrained=pretrained)


def load_concern_model(path, img_size=224, dropout=0.3):
    model = build_concern_model(img_size, dropout, pretrained=False)
    model(tf.zeros((1, img_size, img_size, 3)))
    model.load_weights(path)
    return model
