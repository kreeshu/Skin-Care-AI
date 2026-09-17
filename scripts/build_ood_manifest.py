#!/usr/bin/env python3
"""Select person-free PASCAL VOC scenes for invalid-input evaluation."""

import argparse
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


GROUPS = {
    "animal": {"bird", "cat", "cow", "dog", "horse", "sheep"},
    "vehicle": {"aeroplane", "bicycle", "boat", "bus", "car", "motorbike", "train"},
    "object": {"bottle", "chair", "diningtable", "pottedplant", "sofa", "tvmonitor"},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("voc_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/vision/manifests/ood_test.csv"))
    parser.add_argument("--per-group", type=int, default=100)
    args = parser.parse_args()

    candidates = defaultdict(list)
    for annotation in sorted((args.voc_root / "Annotations").glob("*.xml")):
        root = ET.parse(annotation).getroot()
        labels = sorted({node.text for node in root.findall("object/name")})
        if "person" in labels:
            continue
        image = args.voc_root / "JPEGImages" / root.findtext("filename")
        for group, classes in GROUPS.items():
            if classes.intersection(labels):
                candidates[group].append((image, labels))
                break

    rows = []
    for group, items in candidates.items():
        items.sort(key=lambda item: hashlib.sha1(item[0].name.encode()).hexdigest())
        for image, labels in items[: args.per_group]:
            rows.append({
                "image_id": f"voc_{image.stem}",
                "original_path": str(image.resolve()),
                "ood_group": group,
                "object_labels": ";".join(labels),
                "expected_valid_face": 0,
                "split": "ood_test",
            })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"total": len(rows), "groups": Counter(row["ood_group"] for row in rows)}, indent=2))


if __name__ == "__main__":
    main()
