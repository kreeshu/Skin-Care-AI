#!/usr/bin/env python3
"""Download a bounded, consented SCIN facial candidate pool, not cosmetic ground truth.

Case-level diagnoses only select candidates. Every cosmetic label stays unknown
until review. Do not infer negatives from absent differential diagnoses.
"""

import argparse
import ast
import hashlib
import io
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from scripts.audit_vision_dataset import BKTree, dhash
from src.model.concern_model import CONCERNS

BUCKET = "https://storage.googleapis.com/dx-scin-public-data/"
RELEVANT_DIAGNOSES = {"Acne", "Rosacea", "Post-Inflammatory hyperpigmentation", "Melasma"}
MAX_BYTES = 10 * 1024 * 1024


def candidate_image(row):
    if row.get("body_parts_head_or_neck") != "YES":
        return None
    if any(value == "YES" for name, value in row.items()
           if name.startswith("body_parts_") and name != "body_parts_head_or_neck"):
        return None
    raw = row.get("weighted_skin_condition_label", "")
    diagnoses = ast.literal_eval(raw) if isinstance(raw, str) and raw else {}
    if not isinstance(diagnoses, dict):
        raise ValueError("Expected a differential diagnosis dictionary")
    if not RELEVANT_DIAGNOSES.intersection(diagnoses) and row.get("related_category") not in {
        "ACNE", "PIGMENTARY_PROBLEM", "LOOKS_HEALTHY"
    }:
        return None
    images = []
    for index in (1, 2, 3):
        path = row.get(f"image_{index}_path")
        if isinstance(path, str) and path:
            images.append((row.get(f"image_{index}_shot_type") != "AT_DISTANCE", index, path))
    return min(images)[2] if images else None


def image_url(path):
    if not path.startswith("dataset/images/") or ".." in path.split("/"):
        raise ValueError("Image must be an object in SCIN's published image directory")
    return BUCKET + quote(path, safe="/")


def download_bytes(url):
    with urlopen(url, timeout=45) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Download exceeds the 10 MiB per-file limit")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("dataset_sources/extracted/scin_cosmetic_candidates"))
    parser.add_argument("--manifests-dir", type=Path, default=Path("data/vision/manifests_v2"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/scin_review"))
    parser.add_argument("--limit", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.limit <= 200:
        parser.error("--limit must be between 1 and 200")
    if (args.output_dir / "review_queue.csv").exists():
        parser.error("Review queue exists; choose a new output directory")
    args.root.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.root).free < 2 * 1024**3 + args.limit * MAX_BYTES:
        parser.error("Insufficient free space for the bounded download plus 2 GiB reserve")
    sources = {
        "LICENSE.txt": "https://raw.githubusercontent.com/google-research-datasets/scin/main/LICENSE",
        "README.source.md": "https://raw.githubusercontent.com/google-research-datasets/scin/main/README.md",
        "scin_cases.csv": BUCKET + "dataset/scin_cases.csv",
        "scin_labels.csv": BUCKET + "dataset/scin_labels.csv",
    }
    for name, url in sources.items():
        path = args.root / name
        if not path.exists():
            path.write_bytes(download_bytes(url))

    frame = pd.read_csv(args.root / "scin_cases.csv", dtype={"case_id": str}).merge(
        pd.read_csv(args.root / "scin_labels.csv", dtype={"case_id": str}),
        on="case_id", validate="one_to_one").fillna("")
    selected = [(row, candidate_image(row)) for row in frame.to_dict("records")]
    selected = [(row, path) for row, path in selected if path]
    selected.sort(key=lambda item: hashlib.sha256(item[0]["case_id"].encode()).hexdigest())

    exact, tree = set(), BKTree()
    for split in ("train", "validation", "test"):
        manifest = args.manifests_dir / f"{split}.csv"
        for value in pd.read_csv(manifest).original_path:
            path = Path(value)
            if not path.is_absolute():
                path = manifest.resolve().parent / path
            exact.add(hashlib.sha256(path.read_bytes()).hexdigest())
            with Image.open(path) as image:
                tree.add(dhash(image), str(path))

    detector = cv2.FaceDetectorYN.create(
        "models/face_detection/face_detection_yunet_2023mar.onnx", "", (320, 320), 0.9)
    images_dir = args.root / "images"
    images_dir.mkdir(exist_ok=True)
    rows, quarantine, outcomes, failures = [], [], Counter(), []
    downloaded_bytes = 0
    for case, object_path in selected[:args.limit]:
        identifier = hashlib.sha256(object_path.encode()).hexdigest()[:24]
        local = images_dir / (identifier + ".png")
        try:
            data = local.read_bytes() if local.exists() else download_bytes(image_url(object_path))
            with Image.open(io.BytesIO(data)) as opened:
                opened.load()
                image = opened.convert("RGB")
            digest = hashlib.sha256(data).hexdigest()
            perceptual = dhash(image)
            if digest in exact or tree.search(perceptual, 4):
                outcomes["duplicate_or_near_duplicate"] += 1
                continue
            if not local.exists():
                local.write_bytes(data)
                downloaded_bytes += len(data)
            exact.add(digest)
            tree.add(perceptual, identifier)
            record = {
                "image_id": "scin_" + identifier,
                "case_id": case["case_id"],
                "original_path": str(local.resolve()),
                "source": "scin_review_only", "original_label": "withheld; review pixels independently",
                "duplicate_group": "scin_case_" + case["case_id"], "split": "train",
                "image_scope": "unverified", "quality_status": "human review required",
                "review_concern": "Review scope first; then all five concerns independently",
                "label_origin": "unannotated_cosmetic_candidate",
                "source_url": image_url(object_path), "sha256": digest,
                "dhash": f"{perceptual:016x}", **dict.fromkeys(CONCERNS, -1),
            }
            if min(image.size) < 64:
                outcomes["too_small"] += 1
                quarantine.append({**record, "quality_status": "too_small"})
                continue
            scale = min(1.0, 320 / max(image.size))
            resized = image.resize((round(image.width * scale), round(image.height * scale)))
            bgr = np.ascontiguousarray(np.asarray(resized)[:, :, ::-1])
            detector.setInputSize((bgr.shape[1], bgr.shape[0]))
            _, faces = detector.detect(bgr)
            if faces is None or len(faces) != 1:
                outcomes["not_one_detected_face"] += 1
                quarantine.append({**record, "quality_status": "no single detected face; may be privacy-masked or a close-up; review scope"})
                continue
            if faces[0][2] * faces[0][3] / (bgr.shape[0] * bgr.shape[1]) < 0.08:
                outcomes["face_too_small"] += 1
                quarantine.append({**record, "quality_status": "face_too_small"})
                continue
            rows.append({**record, "image_scope": "full_face_candidate",
                         "quality_status": "one detected face; human review required"})
            outcomes["queued_for_review"] += 1
        except (OSError, ValueError) as error:
            outcomes["download_or_decode_error"] += 1
            failures.append({"object_path": object_path, "error": str(error)})
        print(f"processed {sum(outcomes.values())}/{min(args.limit, len(selected))}; review images {len(rows)}", flush=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["image_id", "case_id", "original_path", "source", "original_label", "duplicate_group", "split",
              "image_scope", "quality_status", "review_concern", "label_origin", "source_url", "sha256", "dhash", *CONCERNS]
    pd.DataFrame(rows, columns=fields).to_csv(args.output_dir / "review_queue.csv", index=False)
    pd.DataFrame(quarantine, columns=fields).to_csv(args.output_dir / "quarantine_review.csv", index=False)
    report = {"source": "https://github.com/google-research-datasets/scin",
              "license": sources["LICENSE.txt"], "eligible_cases": len(selected),
              "attempted_cases": min(args.limit, len(selected)), "outcomes": dict(outcomes),
              "new_download_bytes": downloaded_bytes, "failures": failures,
              "cosmetic_labels_created": 0, "training_manifests_modified": False,
              "note": "Diagnoses are case-level differentials, not independent cosmetic labels. All concern labels remain unknown. Exact/dHash filtering is not proof of subject independence."}
    (args.output_dir / "download_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
