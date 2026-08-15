import os
import numpy as np
import tensorflow as tf
from typing import Dict, List, Optional, Tuple

IGNORE_LABEL = -1


class MultiTaskSkinModel(tf.keras.Model):
    """Shared EfficientNetB0 backbone with two classification heads.

    Condition head: 7 skin conditions.
    Skin-type head: 3 skin types.

    Training uses sample-masked losses: every training sample carries a label
    for exactly one task (the other is set to IGNORE_LABEL). A batch is
    therefore dominated by a single task, and only that task's head receives
    gradient signal for its samples, while the shared backbone learns from
    both tasks.
    """

    def __init__(
        self,
        num_conditions: int,
        num_skin_types: int,
        img_size: int = 224,
        dropout_rate: float = 0.3,
        cond_loss_weight: float = 1.0,
        type_loss_weight: float = 3.0,
        cond_class_weight: Optional[np.ndarray] = None,
        pretrained: bool = True,
        **kwargs,
    ):
        super().__init__(name="skin_multitask", **kwargs)
        self.num_conditions = num_conditions
        self.num_skin_types = num_skin_types
        self.cond_loss_weight = cond_loss_weight
        self.type_loss_weight = type_loss_weight

        self.base = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights="imagenet" if pretrained else None,
            input_shape=(img_size, img_size, 3),
            pooling=None,
        )
        self.base.trainable = False

        self.shared = tf.keras.Sequential(
            [
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dropout(dropout_rate),
                tf.keras.layers.Dense(256, activation="relu"),
                tf.keras.layers.Dropout(0.2),
            ],
            name="shared_features",
        )

        self.condition_head = tf.keras.layers.Dense(
            num_conditions, activation="softmax", name="condition_output"
        )
        self.skin_type_head = tf.keras.layers.Dense(
            num_skin_types, activation="softmax", name="skin_type_output"
        )

        self._ce = tf.keras.losses.SparseCategoricalCrossentropy(reduction="none")
        if cond_class_weight is not None:
            self.cond_class_weight = tf.constant(
                np.asarray(cond_class_weight, dtype=np.float32)
            )
        else:
            self.cond_class_weight = None

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
    def call(self, inputs, training=False):
        x = self.base(inputs, training=training)
        x = self.shared(x, training=training)
        return {
            "condition": self.condition_head(x, training=training),
            "skin_type": self.skin_type_head(x, training=training),
        }

    def predict_heads(self, image_batch: tf.Tensor):
        """Return (condition_probs, skin_type_probs) for a preprocessed batch."""
        out = self(image_batch, training=False)
        return out["condition"], out["skin_type"]

    def embeddings(self, image_batch: tf.Tensor):
        """Shared feature vector used for cheap linear probing / k-fold analysis."""
        return self.shared(self.base(image_batch, training=False), training=False)

    # ------------------------------------------------------------------ #
    # Training helpers
    # ------------------------------------------------------------------ #
    def _features(self, images, training):
        return self.shared(self.base(images, training=training), training=training)

    def _masked_ce(self, labels, logits, class_weight=None):
        labels = tf.cast(labels, tf.int32)
        safe_labels = tf.maximum(labels, 0)  # clamp IGNORE to a valid index
        per_sample = self._ce(safe_labels, logits)
        weights = tf.cast(tf.not_equal(labels, IGNORE_LABEL), tf.float32)
        if class_weight is not None:
            weights = weights * tf.gather(class_weight, safe_labels)
        denom = tf.maximum(tf.reduce_sum(weights), 1.0)
        return tf.reduce_sum(per_sample * weights) / denom

    @staticmethod
    def _masked_accuracy(labels, logits):
        labels = tf.cast(labels, tf.int32)
        valid = tf.not_equal(labels, IGNORE_LABEL)
        preds = tf.argmax(logits, axis=-1, output_type=tf.int32)
        correct = tf.logical_and(tf.equal(preds, labels), valid)
        return tf.reduce_sum(tf.cast(correct, tf.float32)) / tf.maximum(
            tf.reduce_sum(tf.cast(valid, tf.float32)), 1.0
        )

    def train_step(self, data):
        images, labels = data
        cond_labels = labels["condition"]
        type_labels = labels["skin_type"]

        with tf.GradientTape() as tape:
            features = self._features(images, training=True)
            cond_logits = self.condition_head(features, training=True)
            type_logits = self.skin_type_head(features, training=True)

            cond_loss = self._masked_ce(cond_labels, cond_logits, self.cond_class_weight)
            type_loss = self._masked_ce(type_labels, type_logits)
            reg_loss = tf.add_n(self.losses) if self.losses else tf.constant(0.0, dtype=tf.float32)
            total_loss = (
                self.cond_loss_weight * cond_loss
                + self.type_loss_weight * type_loss
                + reg_loss
            )

        trainable_vars = self.trainable_variables
        grads = tape.gradient(total_loss, trainable_vars)
        self.optimizer.apply_gradients(zip(grads, trainable_vars))

        return {
            "loss": total_loss,
            "condition_loss": cond_loss,
            "skin_type_loss": type_loss,
            "condition_accuracy": self._masked_accuracy(cond_labels, cond_logits),
            "skin_type_accuracy": self._masked_accuracy(type_labels, type_logits),
        }

    def test_step(self, data):
        images, labels = data
        cond_labels = labels["condition"]
        type_labels = labels["skin_type"]

        features = self._features(images, training=False)
        cond_logits = self.condition_head(features, training=False)
        type_logits = self.skin_type_head(features, training=False)

        cond_loss = self._masked_ce(cond_labels, cond_logits, self.cond_class_weight)
        type_loss = self._masked_ce(type_labels, type_logits)
        total_loss = self.cond_loss_weight * cond_loss + self.type_loss_weight * type_loss

        return {
            "loss": total_loss,
            "condition_loss": cond_loss,
            "skin_type_loss": type_loss,
            "condition_accuracy": self._masked_accuracy(cond_labels, cond_logits),
            "skin_type_accuracy": self._masked_accuracy(type_labels, type_logits),
        }

    def unfreeze_base(self, num_layers: int = 30):
        self.base.trainable = True
        for layer in self.base.layers[:-num_layers]:
            layer.trainable = False
        trainable = sum(1 for l in self.base.layers if l.trainable)
        total = len(self.base.layers)
        print(f"Unfroze last {num_layers} base layers. Trainable: {trainable}/{total}")


def build_multitask_model(
    num_conditions: int,
    num_skin_types: int,
    img_size: int = 224,
    dropout_rate: float = 0.3,
    cond_loss_weight: float = 1.0,
    type_loss_weight: float = 3.0,
    cond_class_weight: Optional[np.ndarray] = None,
    pretrained: bool = True,
) -> MultiTaskSkinModel:
    return MultiTaskSkinModel(
        num_conditions=num_conditions,
        num_skin_types=num_skin_types,
        img_size=img_size,
        dropout_rate=dropout_rate,
        cond_loss_weight=cond_loss_weight,
        type_loss_weight=type_loss_weight,
        cond_class_weight=cond_class_weight,
        pretrained=pretrained,
    )


def save_multitask_model(model: MultiTaskSkinModel, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not path.endswith(".weights.h5"):
        path = path + ".weights.h5"
    model.save_weights(path)
    print(f"Model weights saved to {path}")


def load_multitask_model(
    path: str,
    num_conditions: int,
    num_skin_types: int,
    img_size: int = 224,
) -> MultiTaskSkinModel:
    """Rebuild the multi-task model from its class config and load weights."""
    model = build_multitask_model(
        num_conditions=num_conditions,
        num_skin_types=num_skin_types,
        img_size=img_size,
        pretrained=False,
    )
    _ = model(tf.zeros((1, img_size, img_size, 3)))
    model.load_weights(path)
    return model
