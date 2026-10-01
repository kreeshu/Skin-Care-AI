import unittest
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
from PIL import Image

from scripts.download_scin_review import candidate_image, image_url
from scripts.merge_training_review import CONCERNS, fill_unknown_labels, reviewed_labels


class ScinReviewTest(unittest.TestCase):
    def test_diagnosis_selects_candidate_not_a_cosmetic_label(self):
        row = {"body_parts_head_or_neck": "YES", "weighted_skin_condition_label": "{'Rosacea': 1.0}",
               "image_1_path": "dataset/images/a.png", "image_1_shot_type": "CLOSE_UP",
               "image_2_path": "dataset/images/b.png", "image_2_shot_type": "AT_DISTANCE"}
        self.assertEqual(candidate_image(row), "dataset/images/b.png")
        self.assertNotIn("redness", row)
        row["body_parts_arm"] = "YES"
        self.assertIsNone(candidate_image(row))

    def test_missing_diagnosis_does_not_mean_healthy(self):
        row = {"body_parts_head_or_neck": "YES", "weighted_skin_condition_label": "",
               "image_1_path": "dataset/images/a.png"}
        self.assertIsNone(candidate_image(row))

    def test_download_paths_cannot_escape_published_bucket(self):
        for path in ("../a.png", "dataset/images/../a.png", "https://example.com/a.png"):
            with self.assertRaises(ValueError):
                image_url(path)
        self.assertTrue(image_url("dataset/images/a.png").startswith(
            "https://storage.googleapis.com/dx-scin-public-data/dataset/images/"))

    def test_human_review_only_fills_unknown_training_labels(self):
        original = dict.fromkeys(CONCERNS, "-1")
        original["blemishes"] = "1"
        reviewed = dict.fromkeys(CONCERNS, "0")
        result, changes = fill_unknown_labels(original, reviewed)
        self.assertEqual(result["blemishes"], "1")
        self.assertEqual(result["redness"], "0")
        self.assertEqual(changes, 4)
        self.assertEqual(original["redness"], "-1")

    def test_unusable_and_unknown_reviews_cannot_become_training_labels(self):
        row = {"usable": "1", "image_scope": "full_face", **dict.fromkeys(CONCERNS, "-1")}
        self.assertIsNone(reviewed_labels(row))
        row["redness"] = "1"
        self.assertEqual(reviewed_labels(row)["redness"], "1")
        row["image_scope"] = "not_facial"
        self.assertIsNone(reviewed_labels(row))
        row["redness"] = "2"
        with self.assertRaises(ValueError):
            reviewed_labels(row)

    def test_merge_writes_new_train_and_preserves_heldout_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            base.mkdir()
            rows = []
            for index, split in enumerate(("train", "validation", "test")):
                image_path = root / f"{split}.png"
                Image.fromarray(np.random.default_rng(index).integers(0, 256, (64, 64, 3), dtype=np.uint8)).save(image_path)
                row = {"image_id": split, "original_path": str(image_path), "duplicate_group": split,
                       "split": split, "image_scope": "full_face", **dict.fromkeys(CONCERNS, "-1")}
                pd.DataFrame([row]).to_csv(base / f"{split}.csv", index=False)
                rows.append(row)
            original_bytes = {split: (base / f"{split}.csv").read_bytes() for split in ("train", "validation", "test")}
            pd.DataFrame([rows[0]]).to_csv(root / "queue.csv", index=False)
            annotation = {"image_id": "train", "usable": "1", "image_scope": "full_face",
                          **dict.fromkeys(CONCERNS, "-1"), "redness": "0"}
            pd.DataFrame([annotation]).to_csv(root / "annotations.csv", index=False)
            subprocess.run([sys.executable, "scripts/merge_training_review.py", str(root / "queue.csv"),
                            str(root / "annotations.csv"), "--base-dir", str(base),
                            "--output-dir", str(root / "new")], check=True, capture_output=True)
            self.assertEqual(str(pd.read_csv(root / "new/train.csv").iloc[0].redness), "0")
            for split in ("train", "validation", "test"):
                self.assertEqual((base / f"{split}.csv").read_bytes(), original_bytes[split])
            for split in ("validation", "test"):
                self.assertEqual((root / "new" / f"{split}.csv").read_bytes(), original_bytes[split])


if __name__ == "__main__":
    unittest.main()
