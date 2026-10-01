#!/usr/bin/env python3
"""Add MEMI-DS melasma photos to a new training manifest as dark_spots positives.

MEMI-DS (Zhai, 2025; CC BY 4.0) pairs facial photos with binary melasma segmentation masks.
Melasma is facial hyperpigmentation, so a non-empty mask means dark_spots=1. An empty mask
does not prove that every other kind of dark spot is absent, so those photos are left out.
The other four concerns were never annotated and stay -1 (unknown), never 0.
Photos must pass the serving face gate and must not duplicate any existing image.
Additions go to training only; validation and test manifests are copied unchanged.
"""

import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
import pandas as pd
from PIL import Image

from scripts.audit_vision_dataset import BKTree, dhash
from src.model.concern_model import CONCERNS

ARTICLE_URL = "https://api.figshare.com/v2/articles/29209229"


def fetch(url):
    with urlopen(url, timeout=120) as response:
        return response.read()


def download(metadata, root):
    """Fetch each photo and mask once; Figshare's MD5 lets reruns reuse verified local files."""
    for entry in metadata["files"]:
        folder = "masks" if entry["name"].lower().endswith(".png") else "images"
        path = root / folder / entry["name"]
        if path.exists() and hashlib.md5(path.read_bytes()).hexdigest() == entry["computed_md5"]:
            continue
        data = fetch(entry["download_url"])
        if hashlib.md5(data).hexdigest() != entry["computed_md5"]:
            raise ValueError(f"Checksum mismatch for {entry['name']}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def mask_labels(mask):
    """Melasma mask -> concern labels, or None when the mask supports no label."""
    if not (np.asarray(mask) > 0).any():
        return None
    return {**dict.fromkeys(CONCERNS, -1), "dark_spots": 1}


def face_status(image, detector):
    # Same gate as serving (src/inference/predict.py): YuNet on a <=320px copy, score >= 0.9.
    scale = min(1.0, 320 / max(image.size))
    resized = image.resize((round(image.width * scale), round(image.height * scale)))
    bgr = np.ascontiguousarray(np.asarray(resized)[:, :, ::-1])
    detector.setInputSize((bgr.shape[1], bgr.shape[0]))
    _, faces = detector.detect(bgr)
    if faces is None or len(faces) == 0:
        return "no_face"
    if len(faces) > 1:
        return "multiple_faces"
    if faces[0][2] * faces[0][3] / (bgr.shape[0] * bgr.shape[1]) < 0.08:
        return "face_too_small"
    return "pass"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("dataset_sources/extracted/memi_ds"))
    parser.add_argument("--base-dir", type=Path, default=Path("data/vision/manifests_human_reviewed"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--face-model", type=Path,
                        default=Path("models/face_detection/face_detection_yunet_2023mar.onnx"))
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("Output directory exists; choose a new directory to preserve existing work")

    metadata_path = args.root / "figshare_metadata.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
    else:
        metadata = json.loads(fetch(ARTICLE_URL))
        args.root.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    if metadata["license"]["name"] != "CC BY 4.0":
        parser.error("Unexpected MEMI-DS license; re-check the terms before use")
    download(metadata, args.root)

    train = pd.read_csv(args.base_dir / "train.csv", dtype=str, keep_default_na=False)
    exact, tree = set(), BKTree()
    for split in ("train", "validation", "test"):
        for value in pd.read_csv(args.base_dir / f"{split}.csv").original_path:
            path = Path(value)
            if not path.is_absolute():
                parser.error("Base manifests must use absolute image paths to copy splits unchanged")
            exact.add(hashlib.sha256(path.read_bytes()).hexdigest())
            with Image.open(path) as image:
                tree.add(dhash(image), str(path))

    detector = cv2.FaceDetectorYN.create(str(args.face_model), "", (320, 320), 0.9)
    photos = sorted((args.root / "images").glob("*.jpg"))
    rows, outcomes = [], Counter()
    for photo in photos:
        mask_path = args.root / "masks" / (photo.stem + ".png")
        if not mask_path.exists():
            outcomes["missing_mask"] += 1
            continue
        digest = hashlib.sha256(photo.read_bytes()).hexdigest()
        with Image.open(photo) as opened:
            image = opened.convert("RGB")
        with Image.open(mask_path) as opened:
            mask = np.asarray(opened)
        if mask.shape[:2] != (image.height, image.width):
            outcomes["mask_size_mismatch"] += 1
            continue
        labels = mask_labels(mask)
        if labels is None:
            outcomes["empty_mask"] += 1
            continue
        # Exact or near-duplicates of any existing image (including held-out) are skipped.
        if digest in exact or tree.search(dhash(image), 4):
            outcomes["duplicate_of_existing_image"] += 1
            continue
        status = face_status(image, detector)
        if status != "pass":
            outcomes[status] += 1
            continue
        exact.add(digest)
        rows.append({
            "image_id": "memi_" + photo.stem,
            "original_path": str(photo.resolve()),
            "source": "memi_ds",
            "original_label": "melasma_mask",
            # Front/left/right views of one person share a group.
            "duplicate_group": "memi_subject_" + photo.stem.split("_")[0],
            "image_scope": "full_face",
            "split": "train",
            **labels,
            "mask_coverage": float((mask > 0).mean()),
            "sha256": digest,
        })
        outcomes["added"] += 1
    if not rows:
        parser.error("No usable MEMI-DS photos; nothing to add")

    additions = pd.DataFrame(rows)
    args.output_dir.mkdir(parents=True)
    additions.to_csv(args.output_dir / "memi_ds.csv", index=False)
    pd.concat([train, additions[train.columns]], ignore_index=True).to_csv(args.output_dir / "train.csv", index=False)
    for split in ("validation", "test"):
        shutil.copyfile(args.base_dir / f"{split}.csv", args.output_dir / f"{split}.csv")
    coverage = additions.mask_coverage
    report = {
        "source": metadata["url_public_html"], "doi": metadata["doi"],
        "license": metadata["license"]["name"], "license_url": metadata["license"]["url"],
        "attribution": metadata["citation"], "base_dir": str(args.base_dir),
        "photos": len(photos), "outcomes": dict(outcomes),
        "added_training_images": len(additions), "added_subjects": int(additions.duplicate_group.nunique()),
        "mask_coverage": {"min": float(coverage.min()), "median": float(coverage.median()),
                          "max": float(coverage.max())},
        "labels": "dark_spots=1 from a non-empty melasma mask; other concerns -1 (not annotated)",
        "heldout_files_copied_unchanged": True,
        "note": "Melasma is only one kind of dark spot. Exact/dHash checks do not prove subject independence.",
    }
    (args.output_dir / "memi_ds_merge.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
