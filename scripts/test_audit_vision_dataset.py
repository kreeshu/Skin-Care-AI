import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.audit_vision_dataset import assign_duplicate_groups, scan_source
from scripts.build_vision_review_queue import build_queue, split_for
from scripts.validate_vision_manifests import validate


class AuditVisionDatasetTest(unittest.TestCase):
    def test_maps_labels_and_groups_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Acne").mkdir()
            image = Image.new("RGB", (224, 224), "white")
            image.save(root / "Acne" / "one.jpg")
            image.save(root / "Acne" / "two.jpg")

            rows = scan_source("test", root)
            groups = assign_duplicate_groups(rows, radius=0)

            self.assertEqual({row["weak_concern"] for row in rows}, {"blemishes"})
            self.assertEqual(len(groups), 1)
            self.assertEqual(len({row["duplicate_group"] for row in rows}), 1)

    def test_review_queue_rejects_generated_and_exact_duplicates(self):
        base = {
            "source": "facial_skin_concerns", "original_label": "acne", "usable": "1",
            "quality_status": "pass", "weak_concern": "blemishes", "face_count": "1",
        }
        rows = [
            {**base, "image_id": "one", "sha256": "same", "is_generated": "0"},
            {**base, "image_id": "two", "sha256": "same", "is_generated": "0"},
            {**base, "image_id": "three", "sha256": "other", "is_generated": "1"},
        ]
        queue = build_queue(rows, {"facial_skin_concerns": {"status": "partial_review"}}, 10)
        self.assertEqual(len(queue), 1)
        self.assertIn(queue[0]["image_id"], {"one", "two"})

    def test_duplicate_group_cannot_cross_splits(self):
        left = {"duplicate_group": "dup_1", "sha256": "a"}
        right = {"duplicate_group": "dup_1", "sha256": "b"}
        self.assertEqual(split_for(left), split_for(right))

    def test_validator_detects_split_leakage(self):
        rows = []
        for split in ("train", "validation", "test"):
            for value in ("0", "1"):
                rows.append({
                    "image_id": f"{split}_{value}", "original_path": __file__,
                    "duplicate_group": "leak" if value == "1" else f"{split}_{value}", "split": split,
                    **{concern: value for concern in ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")},
                })
        errors, _ = validate(rows)
        self.assertTrue(any("crosses splits" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
