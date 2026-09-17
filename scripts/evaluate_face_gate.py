#!/usr/bin/env python3
"""Evaluate YuNet invalid-input rejection on the OOD image manifest."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/vision/manifests/ood_test.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/face_detection/face_detection_yunet_2023mar.onnx"))
    parser.add_argument("--output", type=Path, default=Path("data/vision/reports/face_gate_ood.json"))
    parser.add_argument("--score-threshold", type=float, default=0.8)
    args = parser.parse_args()

    detector = cv2.FaceDetectorYN.create(str(args.model), "", (320, 320), args.score_threshold)
    with args.manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    accepted, false_accepts = 0, []
    groups = Counter()
    for row in rows:
        image = cv2.imread(row["original_path"])
        if image is None:
            continue
        height, width = image.shape[:2]
        scale = min(1.0, 1024 / max(width, height))
        if scale < 1:
            image = cv2.resize(image, (round(width * scale), round(height * scale)))
        detector.setInputSize((image.shape[1], image.shape[0]))
        _, faces = detector.detect(image)
        if faces is not None and len(faces):
            accepted += 1
            groups[row["ood_group"]] += 1
            false_accepts.append({"image_id": row["image_id"], "group": row["ood_group"], "labels": row["object_labels"]})
    report = {
        "total": len(rows),
        "rejected": len(rows) - accepted,
        "rejection_rate": (len(rows) - accepted) / len(rows),
        "false_accepts": accepted,
        "false_accepts_by_group": groups,
        "false_accept_examples": false_accepts[:25],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
