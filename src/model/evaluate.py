import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from sklearn.metrics import classification_report, confusion_matrix
from typing import List, Tuple, Dict


def evaluate_model(
    model: tf.keras.Model,
    test_ds: tf.data.Dataset,
    class_names: List[str],
    output_dir: str,
) -> Dict:
    """Full evaluation: loss, accuracy, F1, confusion matrix, plots."""
    os.makedirs(output_dir, exist_ok=True)

    y_true, y_pred = _get_predictions(model, test_ds)
    loss, accuracy = model.evaluate(test_ds, verbose=0)

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    report_str = classification_report(y_true, y_pred, target_names=class_names)

    print(f"\nTest Loss: {loss:.4f}")
    print(f"Test Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:\n{report_str}")

    _plot_confusion_matrix(y_true, y_pred, class_names, output_dir)
    _plot_class_accuracies(report, class_names, output_dir)

    metrics = {
        "test_loss": float(loss),
        "test_accuracy": float(accuracy),
        "classification_report": report,
    }

    metrics_path = os.path.join(output_dir, "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

    return metrics


def plot_training_curves(history: Dict, output_dir: str):
    """Plot training/validation loss and accuracy curves."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for phase_name, phase_data in [("phase_a", history["phase_a"]), ("phase_b", history["phase_b"])]:
        epochs = range(1, len(phase_data["loss"]) + 1)
        offset = 0 if phase_name == "phase_a" else len(history["phase_a"]["loss"])

        axes[0, 0].plot(epochs, phase_data["loss"], label=f"{phase_name} train")
        axes[0, 1].plot(epochs, phase_data["val_loss"], label=f"{phase_name} val")
        axes[1, 0].plot(epochs, phase_data["accuracy"], label=f"{phase_name} train")
        axes[1, 1].plot(epochs, phase_data["val_accuracy"], label=f"{phase_name} val")

    axes[0, 0].set_title("Training Loss")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    axes[0, 1].set_title("Validation Loss")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Loss")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    axes[1, 0].set_title("Training Accuracy")
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel("Accuracy")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    axes[1, 1].set_title("Validation Accuracy")
    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylabel("Accuracy")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    path = os.path.join(output_dir, "training_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Training curves saved to {path}")


def _get_predictions(model: tf.keras.Model, dataset: tf.data.Dataset) -> Tuple[np.ndarray, np.ndarray]:
    y_true, y_pred = [], []
    for images, labels in dataset:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy())
        y_pred.extend(np.argmax(preds, axis=1))
    return np.array(y_true), np.array(y_pred)


def _plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, class_names: List[str], output_dir: str):
    cm = confusion_matrix(y_true, y_pred)
    cm_normalized = cm.astype("float") / cm.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names, ax=axes[0])
    axes[0].set_title("Confusion Matrix (Counts)")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("True")

    sns.heatmap(cm_normalized, annot=True, fmt=".2%", cmap="Blues", xticklabels=class_names, yticklabels=class_names, ax=axes[1])
    axes[1].set_title("Confusion Matrix (Normalized)")
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("True")

    plt.tight_layout()
    path = os.path.join(output_dir, "confusion_matrix.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Confusion matrix saved to {path}")


def _plot_class_accuracies(report: Dict, class_names: List[str], output_dir: str):
    accuracies = [report[c]["recall"] for c in class_names]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(class_names, accuracies, color=plt.cm.Set2(np.linspace(0, 1, len(class_names))))
    ax.set_title("Per-Class Accuracy (Recall)")
    ax.set_xlabel("Skin Condition")
    ax.set_ylabel("Recall")
    ax.set_ylim(0, 1.1)

    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{acc:.2%}", ha="center", va="bottom")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = os.path.join(output_dir, "per_class_accuracy.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Per-class accuracy plot saved to {path}")
