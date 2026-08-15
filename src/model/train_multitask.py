import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

import tensorflow as tf
from typing import Dict, Tuple

from src.model.dataset_multitask import prepare_multitask_datasets
from src.model.evaluate_multitask import evaluate_task_dataset
from src.model.multitask import (
    build_multitask_model,
    save_multitask_model,
    MultiTaskSkinModel,
)


class MultiTaskValCallback(tf.keras.callbacks.Callback):
    """Computes honest per-task validation metrics at the end of every epoch.

    The training stream mixes batches from both tasks, so accuracy reported by
    the mixed validation stream would be dominated by masked (ignored) labels.
    This callback evaluates each head on its own validation set instead.
    """

    def __init__(self, val_sets: Dict, cond_loss_weight: float = 1.0, type_loss_weight: float = 3.0):
        super().__init__()
        self.val_sets = val_sets
        self.cond_w = cond_loss_weight
        self.type_w = type_loss_weight

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        cond = evaluate_task_dataset(self.model, self.val_sets["condition"], "condition")
        typ = evaluate_task_dataset(self.model, self.val_sets["skin_type"], "skin_type")
        logs["val_condition_accuracy"] = cond["accuracy"]
        logs["val_skin_type_accuracy"] = typ["accuracy"]
        logs["val_loss"] = self.cond_w * cond["loss"] + self.type_w * typ["loss"]
        print(f"  [val] condition acc: {cond['accuracy']:.4f} | "
              f"skin-type acc: {typ['accuracy']:.4f}")


def train_multitask(
    conditions_dir: str,
    types_dir: str,
    model_save_dir: str,
    img_size: int = 224,
    batch_size: int = 32,
    phase_a_epochs: int = 20,
    phase_b_epochs: int = 15,
    learning_rate_a: float = 1e-3,
    learning_rate_b: float = 1e-5,
    fine_tune_layers: int = 30,
    patience: int = 5,
    cond_loss_weight: float = 1.0,
    type_loss_weight: float = 3.0,
    cond_sample_weight: float = 1.0,
    type_sample_weight: float = 4.0,
    quick: bool = False,
) -> Tuple[MultiTaskSkinModel, Dict, Dict]:
    """Two-phase multi-task training: frozen backbone, then fine-tuned top layers.

    Returns (model, combined history dict, dataset info).
    """
    os.makedirs(model_save_dir, exist_ok=True)

    print("Loading datasets (conditions + skin types)...")
    datasets = prepare_multitask_datasets(
        conditions_dir, types_dir, img_size, batch_size,
        cond_sample_weight, type_sample_weight,
    )
    print(f"\nConditions: {datasets['num_conditions']}, Skin types: {datasets['num_skin_types']}")

    model = build_multitask_model(
        num_conditions=datasets["num_conditions"],
        num_skin_types=datasets["num_skin_types"],
        img_size=img_size,
        cond_loss_weight=cond_loss_weight,
        type_loss_weight=type_loss_weight,
        cond_class_weight=datasets["cond_class_weight"],
        pretrained=True,
    )

    # Build explicitly (custom train_step bypasses call(), which Keras needs
    # before callbacks can save weights).
    _ = model(tf.zeros((1, img_size, img_size, 3)))

    val_cb = MultiTaskValCallback(datasets["val_sets"], cond_loss_weight, type_loss_weight)

    steps_per_epoch = datasets["steps_per_epoch"]
    if quick:
        steps_per_epoch = min(steps_per_epoch, 20)
        phase_a_epochs = min(phase_a_epochs, 2)
        phase_b_epochs = min(phase_b_epochs, 2)

    print("\n" + "=" * 60)
    print("PHASE A: Feature Extraction (frozen base)")
    print("=" * 60)

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate_a))
    callbacks_a = [
        val_cb,
        tf.keras.callbacks.EarlyStopping(
            monitor="val_condition_accuracy", mode="max", patience=patience, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(model_save_dir, "best_phase_a_multitask.weights.h5"),
            monitor="val_condition_accuracy", mode="max",
            save_best_only=True, save_weights_only=True,
        ),
    ]
    history_a = model.fit(
        datasets["train"],
        epochs=phase_a_epochs,
        steps_per_epoch=steps_per_epoch,
        callbacks=callbacks_a,
    )

    print("\n" + "=" * 60)
    print("PHASE B: Fine-tuning (unfrozen top layers)")
    print("=" * 60)

    model.unfreeze_base(fine_tune_layers)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate_b))
    callbacks_b = [
        MultiTaskValCallback(datasets["val_sets"], cond_loss_weight, type_loss_weight),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_condition_accuracy", mode="max", patience=patience, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7
        ),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(model_save_dir, "best_phase_b_multitask.weights.h5"),
            monitor="val_condition_accuracy", mode="max",
            save_best_only=True, save_weights_only=True,
        ),
    ]
    history_b = model.fit(
        datasets["train"],
        epochs=phase_b_epochs,
        steps_per_epoch=steps_per_epoch,
        callbacks=callbacks_b,
    )

    final_path = os.path.join(model_save_dir, "skin_classifier_multitask.weights.h5")
    save_multitask_model(model, final_path)

    history = {
        "phase_a": history_a.history,
        "phase_b": history_b.history,
        "class_names": datasets["class_names"],
        "config": {
            "num_conditions": datasets["num_conditions"],
            "num_skin_types": datasets["num_skin_types"],
            "img_size": img_size,
            "cond_loss_weight": cond_loss_weight,
            "type_loss_weight": type_loss_weight,
        },
    }
    return model, history, datasets


if __name__ == "__main__":
    import argparse

    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    default_cond = os.path.join(base_dir, "..", "dataset", "Conditions")
    default_types = os.path.join(base_dir, "..", "dataset", "Types")

    parser = argparse.ArgumentParser(description="Multi-task skin model training")
    parser.add_argument("--conditions-dir", default=default_cond)
    parser.add_argument("--types-dir", default=default_types)
    parser.add_argument("--model-dir", default=os.path.join(base_dir, "models"))
    parser.add_argument("--phase-a-epochs", type=int, default=20)
    parser.add_argument("--phase-b-epochs", type=int, default=15)
    parser.add_argument("--quick", action="store_true", help="Tiny run to sanity-check the pipeline")
    args = parser.parse_args()

    t0 = time.time()
    model, history, datasets = train_multitask(
        args.conditions_dir, args.types_dir, args.model_dir,
        phase_a_epochs=args.phase_a_epochs,
        phase_b_epochs=args.phase_b_epochs,
        quick=args.quick,
    )

    ca = history["phase_a"]["val_condition_accuracy"][-1]
    ta = history["phase_a"]["val_skin_type_accuracy"][-1]
    cb = history["phase_b"]["val_condition_accuracy"][-1]
    tb = history["phase_b"]["val_skin_type_accuracy"][-1]
    print(f"\nElapsed: {time.time() - t0:.0f}s")
    print(f"Phase A  -> condition val acc: {ca:.4f}, skin-type val acc: {ta:.4f}")
    print(f"Phase B  -> condition val acc: {cb:.4f}, skin-type val acc: {tb:.4f}")
