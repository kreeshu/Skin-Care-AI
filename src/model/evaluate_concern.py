import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             precision_recall_fscore_support, roc_auc_score)

from src.model.concern_dataset import build_concern_dataset
from src.model.concern_model import CONCERNS, load_concern_model


def collect(model, dataset):
    labels, scores = [], []
    for images, targets in dataset:
        labels.append(targets["labels"].numpy())
        scores.append(model(images, training=False).numpy())
    return np.concatenate(labels), np.concatenate(scores)


def best_thresholds(labels, scores):
    thresholds = {}
    for index, name in enumerate(CONCERNS):
        valid = labels[:, index] >= 0
        y = labels[valid, index]
        positives = int(y.sum())
        negatives = int(len(y) - positives)
        if positives < 5 or negatives < 5:
            thresholds[name] = 0.5
            continue
        # Youden's J (TPR - FPR), not F1: with few negatives, max-F1 picks t=0 and marks every face "present".
        candidates = np.unique(np.r_[0.0, scores[valid, index], 1.0])
        j = [(scores[valid, index][y == 1] >= t).mean() - (scores[valid, index][y == 0] >= t).mean() for t in candidates]
        thresholds[name] = float(candidates[int(np.argmax(j))])
    return thresholds


def evaluate(labels, scores, thresholds):
    report = {}
    for index, name in enumerate(CONCERNS):
        valid = labels[:, index] >= 0
        y, score = labels[valid, index].astype(int), scores[valid, index]
        positives, negatives = int(y.sum()), int(len(y) - y.sum())
        item = {"samples": int(len(y)), "positives": positives, "negatives": negatives,
                "threshold": thresholds[name], "precision": None, "recall": None, "f1": None,
                "pr_auc": None, "roc_auc": None}
        if not len(y):
            item["note"] = "No labeled test samples; metrics unavailable."
        else:
            precision, recall, f1, _ = precision_recall_fscore_support(
                y, score >= thresholds[name], average="binary", zero_division=0)
            item.update(precision=float(precision), recall=float(recall), f1=float(f1))
            tn, fp, fn, tp = confusion_matrix(y, score >= thresholds[name], labels=[0, 1]).ravel()
            item.update(accuracy=float(accuracy_score(y, score >= thresholds[name])),
                        confusion_matrix={"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)})
            if positives and negatives:
                item.update(specificity=float(tn / negatives),
                            balanced_accuracy=float((recall + tn / negatives) / 2))
                item.update(pr_auc=float(average_precision_score(y, score)),
                            roc_auc=float(roc_auc_score(y, score)))
                if positives < 5 or negatives < 5:
                    item["note"] = "Preliminary only: fewer than five positive or negative gold samples."
            else:
                item["note"] = "Unavailable: both positive and negative gold samples are required."
                item.update(precision=None, recall=None, f1=None)
        report[name] = item
    return report


def summary(metrics):
    result = {}
    for key in ("accuracy", "balanced_accuracy", "precision", "recall", "f1", "pr_auc", "roc_auc"):
        values = [item[key] for item in metrics.values() if item.get(key) is not None]
        result["macro_" + key] = float(np.mean(values)) if values else None
    decisions = sum(item["samples"] for item in metrics.values())
    correct = sum(item.get("confusion_matrix", {}).get("tp", 0) +
                  item.get("confusion_matrix", {}).get("tn", 0) for item in metrics.values())
    result.update(known_label_decisions=decisions,
                  pooled_label_accuracy=correct / decisions if decisions else None)
    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate the cosmetic concern model")
    parser.add_argument("--manifests-dir", default="data/vision/manifests")
    parser.add_argument("--validation-manifest")
    parser.add_argument("--test-manifest")
    parser.add_argument("--weights", default="models/skin_concern_pilot.weights.h5")
    parser.add_argument("--output", default="models/skin_concern_evaluation.json")
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    validation_path = args.validation_manifest or os.path.join(args.manifests_dir, "gold_validation.csv")
    test_path = args.test_manifest or os.path.join(args.manifests_dir, "gold_test.csv")
    model = load_concern_model(args.weights, args.img_size)
    val_labels, val_scores = collect(model, build_concern_dataset(validation_path, args.img_size, args.batch_size))
    test_labels, test_scores = collect(model, build_concern_dataset(test_path, args.img_size, args.batch_size))
    thresholds = best_thresholds(val_labels, val_scores)
    metrics = evaluate(test_labels, test_scores, thresholds)
    with open(args.weights, "rb") as handle:
        weight_hash = hashlib.sha256(handle.read()).hexdigest()
    result = {"threshold_source": validation_path, "test_source": test_path,
              "weights": args.weights, "weights_sha256": weight_hash,
              "preprocessing": "RGB, TensorFlow bilinear resize, EfficientNet preprocessing",
              "threshold_objective": "Youden J (balanced accuracy), validation only",
              "metrics": metrics, "summary": summary(metrics),
              "validation_metrics": evaluate(val_labels, val_scores, thresholds)}
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
