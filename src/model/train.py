import tensorflow as tf
import os
from typing import List, Tuple
from src.model.dataset import prepare_datasets
from src.model.efficientnet import build_efficientnet_model, unfreeze_base_model


def train_model(
    data_dir: str,
    model_save_dir: str,
    img_size: int = 224,
    batch_size: int = 32,
    phase_a_epochs: int = 20,
    phase_b_epochs: int = 15,
    learning_rate_a: float = 1e-3,
    learning_rate_b: float = 1e-5,
    fine_tune_layers: int = 30,
    patience: int = 5,
) -> Tuple[tf.keras.Model, dict]:
    """Two-phase training: feature extraction then fine-tuning."""
    os.makedirs(model_save_dir, exist_ok=True)

    print("Loading and preparing datasets...")
    train_ds, val_ds, test_ds, class_names = prepare_datasets(data_dir, img_size, batch_size)
    num_classes = len(class_names)

    print(f"\nClasses ({num_classes}): {class_names}")

    print("\n" + "=" * 60)
    print("PHASE A: Feature Extraction (frozen base)")
    print("=" * 60)

    model, base_model = build_efficientnet_model(num_classes, img_size)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate_a),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    model.summary()

    callbacks_a = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=patience, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(model_save_dir, "best_phase_a.keras"),
            monitor="val_accuracy", save_best_only=True
        ),
    ]

    history_a = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=phase_a_epochs,
        callbacks=callbacks_a,
    )

    print("\n" + "=" * 60)
    print("PHASE B: Fine-tuning (unfrozen top layers)")
    print("=" * 60)

    unfreeze_base_model(model, base_model, fine_tune_layers)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate_b),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    callbacks_b = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=patience, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7
        ),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(model_save_dir, "best_phase_b.keras"),
            monitor="val_accuracy", save_best_only=True
        ),
    ]

    history_b = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=phase_b_epochs,
        callbacks=callbacks_b,
    )

    final_path = os.path.join(model_save_dir, "skin_classifier.keras")
    model.save(final_path)
    print(f"\nModel saved to {final_path}")

    history = {
        "phase_a": history_a.history,
        "phase_b": history_b.history,
        "class_names": class_names,
    }

    return model, history


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    data_dir = os.path.join(base_dir, "Skin_Conditions")
    model_dir = os.path.join(base_dir, "models")

    model, history = train_model(data_dir, model_dir)
    print("\nTraining complete!")
    print(f"Final val accuracy (Phase A): {max(history['phase_a']['val_accuracy']):.4f}")
    print(f"Final val accuracy (Phase B): {max(history['phase_b']['val_accuracy']):.4f}")
