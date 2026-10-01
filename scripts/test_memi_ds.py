import unittest

import numpy as np

from scripts.add_memi_ds import mask_labels
from src.model.concern_model import CONCERNS


class MemiDsTest(unittest.TestCase):
    def test_melasma_mask_marks_only_dark_spots(self):
        mask = np.zeros((8, 8), dtype=np.uint8)
        mask[2:4, 2:4] = 1
        labels = mask_labels(mask)
        self.assertEqual(labels["dark_spots"], 1)
        self.assertEqual({labels[name] for name in CONCERNS if name != "dark_spots"}, {-1})

    def test_empty_mask_is_not_a_negative_label(self):
        self.assertIsNone(mask_labels(np.zeros((8, 8), dtype=np.uint8)))


if __name__ == "__main__":
    unittest.main()
