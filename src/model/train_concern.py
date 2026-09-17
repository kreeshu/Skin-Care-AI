import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import numpy as np
import tensorflow as tf
from sklearn.metrics import average_precision_score

from src.model.concern_dataset import build_concern_dataset
from src.model.concern_model import CONCERNS, build_concern_model


class MacroPRAUC(tf.keras.callbacks.Callback):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset

    def on_epoch_end(self, epoch, logs=None):
        truths, scores = [], []
        for images, targets in self.dataset:
            truths.append(targets["labels"].numpy())
            scores.append(self.model(images, training=False).numpy())
        y_true, y_score = np.concatenate(truths), np.concatenate(scores)
        values = []
        for index in range(len(CONCERNS)):
            valid = y_true[:, index] >= 0
            if valid.any() and np.unique(y_true[valid, index]).size == 2:
                values.append(average_precision_score(y_true[valid, index], y_score[valid, index]))
        value = float(np.mean(values)) if values else 0.0
        logs["val_macro_pr_auc"] = value
        print(" - val_macro_pr_auc: %.4f" % value)


def callbacks(validation, checkpoint, patience):
    return [
        MacroPRAUC(validation),
        tf.keras.callbacks.ModelCheckpoint(checkpoint, monitor="val_macro_pr_auc", mode="max",
                                           save_best_only=True, save_weights_only=True),
        tf.keras.callbacks.EarlyStopping(monitor="val_macro_pr_auc", mode="max", patience=patience,
                                         restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_macro_pr_auc", mode="max", patience=2),
    ]


def main():
    parser = argparse.ArgumentParser(description="Train the five-label cosmetic concern model")
    parser.add_argument("--manifests-dir", default="data/vision/manifests")
    parser.add_argument("--train-manifest")
    parser.add_argument("--validation-manifest")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--frozen-epochs", type=int, default=12)
    parser.add_argument("--fine-tune-epochs", type=int, default=7)
    parser.add_argument("--fine-tune-layers", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    train_path = args.train_manifest or os.path.join(args.manifests_dir, "train.csv")
    val_path = args.validation_manifest or os.path.join(args.manifests_dir, "validation.csv")
    train = build_concern_dataset(train_path, args.img_size, args.batch_size, True, True)
    validation = build_concern_dataset(val_path, args.img_size, args.batch_size)
    model = build_concern_model(args.img_size)
    model(tf.zeros((1, args.img_size, args.img_size, 3)))
    os.makedirs(args.model_dir, exist_ok=True)
    steps = 20 if args.quick else None
    frozen_epochs = 2 if args.quick else args.frozen_epochs
    fine_epochs = 2 if args.quick else args.fine_tune_epochs

    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3))
    model.fit(train.repeat() if steps else train, validation_data=validation, epochs=frozen_epochs,
              steps_per_epoch=steps, callbacks=callbacks(validation, os.path.join(args.model_dir, "concern_phase_a.weights.h5"), args.patience))
    model.unfreeze_top(args.fine_tune_layers)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-5))
    model.fit(train.repeat() if steps else train, validation_data=validation, epochs=fine_epochs,
              steps_per_epoch=steps, callbacks=callbacks(validation, os.path.join(args.model_dir, "concern_phase_b.weights.h5"), args.patience))

    output = os.path.join(args.model_dir, "skin_concern_pilot.weights.h5")
    model.save_concern_weights(output)
    with open(os.path.join(args.model_dir, "skin_concern_pilot.json"), "w") as handle:
        json.dump({"labels": list(CONCERNS), "img_size": args.img_size,
                   "fine_tune_layers": args.fine_tune_layers}, handle, indent=2)


if __name__ == "__main__":
    main()
