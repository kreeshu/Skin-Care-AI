#!/usr/bin/env python3
"""5-fold cross-validation for the skin-type task using linear probing.

The shared backbone embeddings of the trained multi-task model are frozen and a
small logistic regression classifier is cross-validated on top. This gives a
robust estimate of skin-type head performance despite the tiny dataset (~112
images), without retraining the deep network per fold.

Usage:
    python scripts/evaluate_types_kfold.py --model-dir models --types-dir ../dataset/Types
"""

import os
import sys
import json
import argparse
import numpy as np
import tensorflow as tf
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.dataset_multitask import load_dataset, build_data_pipeline
from src.model.multitask import build_multitask_model


def extract_embeddings(model, paths, labels, img_size=224, batch_size=32):
    ds = build_data_pipeline(paths, labels, img_size=img_size, batch_size=batch_size, augment=False)
    feats, ys = [], []
    for images, lbls in ds:
        feats.append(model.embeddings(images).numpy())
        ys.append(np.asarray(lbls))
    return np.concatenate(feats), np.concatenate(ys)


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default=os.path.join(base_dir, "models"))
    parser.add_argument("--types-dir", default=os.path.join(base_dir, "..", "dataset", "Types"))
    parser.add_argument("--num-conditions", type=int, default=7)
    parser.add_argument("--num-skin-types", type=int, default=3)
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()

    model_path = os.path.join(args.model_dir, "skin_classifier_multitask.weights.h5")
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        sys.exit(1)

    print("Loading skin-type dataset...")
    paths, labels, class_names = load_dataset(args.types_dir)
    model = build_multitask_model(args.num_conditions, args.num_skin_types, pretrained=False)
    model.load_weights(model_path)
    print("Extracting shared backbone embeddings...")
    X, y = extract_embeddings(model, paths, labels)

    skf = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    clf = LogisticRegression(max_iter=2000, C=1.0)
    y_pred = cross_val_predict(clf, X, y, cv=skf)

    acc = accuracy_score(y, y_pred)
    f1_macro = f1_score(y, y_pred, average="macro")
    print(f"\n{args.folds}-fold CV accuracy: {acc:.4f} (+/- confidence below)")
    print(f"Macro F1: {f1_macro:.4f}")
    print("\nClassification report:\n")
    print(classification_report(y, y_pred, target_names=class_names, zero_division=0))

    per_fold = []
    for fold, (tr, te) in enumerate(skf.split(X, y), 1):
        clf.fit(X[tr], y[tr])
        per_fold.append(accuracy_score(y[te], clf.predict(X[te])))
    per_fold = np.asarray(per_fold)
    print(f"Per-fold accuracies: {[f'{a:.4f}' for a in per_fold]}")
    print(f"Mean: {per_fold.mean():.4f} +- {per_fold.std():.4f}")

    os.makedirs("outputs", exist_ok=True)
    out = os.path.join(base_dir, "outputs", "skin_type_kfold.json")
    with open(out, "w") as f:
        json.dump({
            "folds": args.folds,
            "mean_accuracy": float(per_fold.mean()),
            "std_accuracy": float(per_fold.std()),
            "per_fold": per_fold.tolist(),
            "macro_f1": float(f1_macro),
            "class_names": class_names,
            "report": classification_report(y, y_pred, target_names=class_names, output_dict=True, zero_division=0),
        }, f, indent=2)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
