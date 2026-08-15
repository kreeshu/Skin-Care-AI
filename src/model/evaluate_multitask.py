import os
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from typing import Dict, List

from src.model.multitask import IGNORE_LABEL


def evaluate_task_dataset(model, dataset, task: str, class_weight=None) -> Dict:
    """Evaluate one task's head on its own (dict-labelled) dataset.

    Returns accuracy, mean loss, mean confidence and the true/pred labels.
    """
    ce_fn = tf.keras.losses.SparseCategoricalCrossentropy(reduction="none")
    y_true, y_pred, losses, probs = [], [], [], []
    for images, labels in dataset:
        cond_probs, type_probs = model.predict_heads(images)
        p = cond_probs if task == "condition" else type_probs
        lbl = tf.cast(labels[task], tf.int32).numpy()
        valid = lbl != IGNORE_LABEL
        if not valid.any():
            continue
        lbl_safe = np.maximum(lbl, 0)
        per_sample = ce_fn(lbl_safe, p).numpy()
        preds = np.argmax(p.numpy(), axis=-1)
        for i in range(len(valid)):
            if valid[i]:
                y_true.append(int(lbl[i]))
                y_pred.append(int(preds[i]))
                losses.append(float(per_sample[i]))
                probs.append(float(np.max(p[i])))

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)) if len(y_true) else 0.0,
        "loss": float(np.mean(losses)) if losses else 0.0,
        "mean_confidence": float(np.mean(probs)) if probs else 0.0,
        "y_true": y_true,
        "y_pred": y_pred,
    }


def _plot_confusion(y_true, y_pred, class_names, title, path):
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names, ax=axes[0])
    axes[0].set_title(f"{title} (Counts)")
    sns.heatmap(cm_norm, annot=True, fmt=".2%", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names, ax=axes[1])
    axes[1].set_title(f"{title} (Normalized)")
    for ax in axes:
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def _plot_class_accuracies(report: Dict, class_names: List[str], title, path):
    accs = [report[c]["recall"] for c in class_names]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(class_names, accs, color=plt.cm.Set2(np.linspace(0, 1, len(class_names))))
    ax.set_title(f"{title} (Per-class recall)")
    ax.set_ylim(0, 1.1)
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{acc:.2%}", ha="center", va="bottom")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def evaluate_multitask(model, test_sets: Dict, class_names: Dict, output_dir: str) -> Dict:
    """Per-task evaluation on held-out test sets, with plots + metrics JSON."""
    os.makedirs(output_dir, exist_ok=True)
    metrics = {"config": {"tasks": list(test_sets.keys())}}

    for task, ds in test_sets.items():
        print(f"\n{'=' * 50}\nEvaluating task: {task}")
        res = evaluate_task_dataset(model, ds, task)
        acc = res["accuracy"]
        report = classification_report(
            res["y_true"], res["y_pred"],
            labels=list(range(len(class_names[task]))),
            target_names=class_names[task], output_dict=True, zero_division=0,
        )
        report_str = classification_report(
            res["y_true"], res["y_pred"],
            labels=list(range(len(class_names[task]))),
            target_names=class_names[task], zero_division=0,
        )
        print(f"Accuracy: {acc:.4f}")
        print(report_str)

        _plot_confusion(
            res["y_true"], res["y_pred"], class_names[task], task.capitalize(),
            os.path.join(output_dir, f"confusion_matrix_{task}.png"),
        )
        _plot_class_accuracies(
            report, class_names[task], task.capitalize(),
            os.path.join(output_dir, f"per_class_accuracy_{task}.png"),
        )

        metrics[task] = {
            "accuracy": float(acc),
            "loss": float(res["loss"]),
            "mean_confidence": float(res["mean_confidence"]),
            "classification_report": report,
        }

    path = os.path.join(output_dir, "evaluation_metrics_multitask.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {path}")
    return metrics
