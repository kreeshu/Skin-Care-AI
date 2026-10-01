"""Checks that probe cross-validation keeps duplicates together and never trains on unknowns."""

import unittest

import numpy as np

from src.model.concern_probe import concern_oof, grouped_folds


class ConcernProbeTest(unittest.TestCase):
    def test_duplicate_groups_share_a_fold(self):
        groups = [f"group{index // 3}" for index in range(60)]
        folds = grouped_folds(groups, k=5)
        for group in set(groups):
            self.assertEqual(len({fold for fold, name in zip(folds, groups) if name == group}), 1)
        self.assertEqual(set(folds), set(range(5)))

    def test_unknown_labels_are_not_scored_or_used_as_negatives(self):
        rng = np.random.default_rng(0)
        labels = np.array([0, 1] * 20 + [-1] * 10)
        features = rng.normal(size=(len(labels), 4)) + labels[:, None].clip(0)
        folds = grouped_folds([str(index) for index in range(len(labels))], k=5)
        oof, heads = concern_oof(features, labels, folds, (1.0, None))
        self.assertTrue(np.isnan(oof[labels < 0]).all())
        self.assertFalse(np.isnan(oof[labels >= 0]).any())
        for head in heads:
            self.assertEqual(head.classes_.tolist(), [0, 1])


if __name__ == "__main__":
    unittest.main()
