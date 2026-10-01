"""Regression checks for shared preprocessing, masking, and evaluation."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
from PIL import Image

from src.inference.predict import SkinAnalyzer
from src.model.concern_dataset import balanced_label_weights, build_concern_dataset
from src.model.concern_model import CONCERNS
from src.model.evaluate_concern import best_thresholds, evaluate, summary


class ConcernTrainingTest(unittest.TestCase):
    def test_serving_and_dataset_use_identical_pixels(self):
        image = Image.fromarray(np.random.default_rng(42).integers(0, 256, (91, 153, 3), dtype=np.uint8))
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            image.save(path)
            manifest = Path(directory) / "manifest.csv"
            pd.DataFrame([{"original_path": str(path), **dict.fromkeys(CONCERNS, 0)}]).to_csv(manifest, index=False)
            images, _ = next(iter(build_concern_dataset(str(manifest), 64, 1)))
            analyzer = SkinAnalyzer.__new__(SkinAnalyzer)
            analyzer.img_size = 64
            np.testing.assert_array_equal(analyzer._preprocess(image), images.numpy())

    def test_balancing_preserves_unknowns_and_equalizes_known_classes(self):
        labels = np.tile(np.array([0, 1, 1, 1, -1], dtype=np.float32)[:, None], (1, 5))
        weights = np.ones_like(labels)
        balanced = balanced_label_weights(labels, weights)
        np.testing.assert_array_equal(weights, np.ones_like(labels))
        np.testing.assert_array_equal(balanced[-1], np.zeros(5))
        np.testing.assert_allclose(balanced[0], balanced[1:4].sum(axis=0))

    def test_thresholds_ignore_unknown_labels(self):
        labels = np.tile(np.array([0] * 5 + [1] * 5 + [-1], dtype=np.float32)[:, None], (1, 5))
        scores = np.tile(np.array([0.1] * 5 + [0.8] * 5 + [0.99])[:, None], (1, 5))
        thresholds = best_thresholds(labels, scores)
        self.assertEqual(thresholds, dict.fromkeys(CONCERNS, 0.8))
        metrics = evaluate(labels, scores, thresholds)
        for item in metrics.values():
            self.assertEqual(item["samples"], 10)
            self.assertEqual(item["balanced_accuracy"], 1.0)
        self.assertEqual(summary(metrics)["pooled_label_accuracy"], 1.0)

    def test_missing_training_class_does_not_create_invalid_weights(self):
        labels = np.tile(np.array([1, 1, -1], dtype=np.float32)[:, None], (1, 5))
        balanced = balanced_label_weights(labels, np.ones_like(labels))
        np.testing.assert_array_equal(balanced[:2], np.ones((2, 5)))
        np.testing.assert_array_equal(balanced[-1], np.zeros(5))

    def test_accuracy_does_not_hide_all_positive_predictions(self):
        labels = np.tile(np.array([0] + [1] * 9, dtype=np.float32)[:, None], (1, 5))
        metrics = evaluate(labels, np.ones_like(labels), dict.fromkeys(CONCERNS, 0.5))
        for item in metrics.values():
            self.assertEqual(item["accuracy"], 0.9)
            self.assertEqual(item["balanced_accuracy"], 0.5)
            self.assertEqual(item["specificity"], 0.0)


if __name__ == "__main__":
    unittest.main()
