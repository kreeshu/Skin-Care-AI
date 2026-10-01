import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import numpy as np
import tensorflow as tf
from sklearn.metrics import average_precision_score, roc_auc_score

from src.model.concern_dataset import build_concern_dataset
from src.model.concern_model import CONCERNS, build_concern_model


def validation_metrics(model, dataset):
    truths, scores = [], []
    for images, targets in dataset:
        truths.append(targets["labels"].numpy())
        scores.append(model(images, training=False).numpy())
    y_true, y_score = np.concatenate(truths), np.concatenate(scores)
    pr, roc = [], []
    for index in range(len(CONCERNS)):
        valid = y_true[:, index] >= 0
        if valid.any() and np.unique(y_true[valid, index]).size == 2:
            pr.append(average_precision_score(y_true[valid, index], y_score[valid, index]))
            roc.append(roc_auc_score(y_true[valid, index], y_score[valid, index]))
    if not pr:
        raise ValueError("Validation requires known positive and negative labels")
    return {"val_macro_pr_auc": float(np.mean(pr)), "val_macro_roc_auc": float(np.mean(roc))}


class MacroPRAUC(tf.keras.callbacks.Callback):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset

    def on_epoch_end(self, epoch, logs=None):
        values = validation_metrics(self.model, self.dataset)
        logs.update(values)
        print(" - " + " - ".join("%s: %.4f" % item for item in values.items()))


def callbacks(validation, checkpoint, patience, monitor="val_macro_pr_auc"):
    return [
        MacroPRAUC(validation),
        tf.keras.callbacks.ModelCheckpoint(checkpoint, monitor=monitor, mode="max",
                                           save_best_only=True, save_weights_only=True),
        tf.keras.callbacks.EarlyStopping(monitor=monitor, mode="max", patience=patience,
                                         restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor=monitor, mode="max", patience=2),
        tf.keras.callbacks.CSVLogger(checkpoint.replace(".weights.h5", "_history.csv")),
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
    parser.add_argument("--initial-weights", help="Warm-start a separate candidate from existing weights")
    parser.add_argument("--balance-labels", action="store_true", help="Balance known classes using training labels only")
    parser.add_argument("--selection-metric", choices=("pr_auc", "roc_auc"), default="pr_auc")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if os.path.exists(os.path.join(args.model_dir, "skin_concern_pilot.weights.h5")):
        parser.error("Model directory already contains final weights; choose a new --model-dir")
    tf.keras.utils.set_random_seed(args.seed)

    train_path = args.train_manifest or os.path.join(args.manifests_dir, "train.csv")
    val_path = args.validation_manifest or os.path.join(args.manifests_dir, "validation.csv")
    train = build_concern_dataset(train_path, args.img_size, args.batch_size, True, True,
                                  balance_labels=args.balance_labels)
    validation = build_concern_dataset(val_path, args.img_size, args.batch_size)
    model = build_concern_model(args.img_size, pretrained=not bool(args.initial_weights))
    model(tf.zeros((1, args.img_size, args.img_size, 3)))
    os.makedirs(args.model_dir, exist_ok=True)
    monitor = "val_macro_" + args.selection_metric
    candidates = []
    if args.initial_weights:
        model.load_weights(args.initial_weights)
        initial_path = os.path.join(args.model_dir, "initial.weights.h5")
        model.save_weights(initial_path)
        candidates.append(initial_path)
    steps = 20 if args.quick else None
    frozen_epochs = 2 if args.quick else args.frozen_epochs
    fine_epochs = 2 if args.quick else args.fine_tune_epochs

    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3))
    phase_a = os.path.join(args.model_dir, "concern_phase_a.weights.h5")
    model.fit(train.repeat() if steps else train, validation_data=validation, epochs=frozen_epochs,
              steps_per_epoch=steps, callbacks=callbacks(validation, phase_a, args.patience, monitor))
    candidates.append(phase_a)
    model.unfreeze_top(args.fine_tune_layers)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-5))
    phase_b = os.path.join(args.model_dir, "concern_phase_b.weights.h5")
    model.fit(train.repeat() if steps else train, validation_data=validation, epochs=fine_epochs,
              steps_per_epoch=steps, callbacks=callbacks(validation, phase_b, args.patience, monitor))
    candidates.append(phase_b)

    # The fine-tuning phase can regress; select across both phases and the warm-start baseline.
    comparisons = []
    for checkpoint in candidates:
        model.load_weights(checkpoint)
        comparisons.append({"checkpoint": checkpoint, **validation_metrics(model, validation)})
    selected = max(comparisons, key=lambda item: item[monitor])
    model.load_weights(selected["checkpoint"])
    with open(os.path.join(args.model_dir, "training_selection.json"), "w") as handle:
        json.dump({"monitor": monitor, "selected": selected, "candidates": comparisons,
                   "train_manifest": train_path, "validation_manifest": val_path,
                   "balance_labels": args.balance_labels, "seed": args.seed}, handle, indent=2)
    print("Selected using validation only:", selected)

    output = os.path.join(args.model_dir, "skin_concern_pilot.weights.h5")
    model.save_concern_weights(output)
    with open(os.path.join(args.model_dir, "skin_concern_pilot.json"), "w") as handle:
        json.dump({"labels": list(CONCERNS), "img_size": args.img_size,
                   "fine_tune_layers": args.fine_tune_layers}, handle, indent=2)


if __name__ == "__main__":
    main()
