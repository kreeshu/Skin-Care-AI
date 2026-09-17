#!/usr/bin/env python3
"""Inventory image datasets and report corruption, duplicates, and weak labels."""

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageOps

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = np = None


EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")
LABEL_MAP = {
    "acne": "blemishes",
    "inflammatory_acne": "blemishes",
    "non_inflammatory_acne_blackheads": "blemishes",
    "non_inflammatory_acne_black_heads": "blemishes",
    "non_inflammatory_acne_whiteheads": "blemishes",
    "non_inflammatory_acne_white_heads": "blemishes",
    "blackheads": "blemishes",
    "blackheades": "blemishes",
    "whiteheads": "blemishes",
    "dark_spot": "dark_spots",
    "dark_spots": "dark_spots",
    "pigmentation": "dark_spots",
    "rosacea": "redness",
    "redness": "redness",
    "pores": "visible_pores",
    "wrinkle": "fine_lines",
    "wrinkles": "fine_lines",
}
GENERATED_RE = re.compile(r"(^|[_-])(aug|augment|generated|synthetic)([_-]|\d)", re.I)


def hamming(left, right):
    return bin(left ^ right).count("1")


def normalized_label(value):
    value = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"^class\d+_", "", value)


def dhash(image):
    pixels = list(ImageOps.grayscale(image).resize((9, 8)).getdata())
    bits = [pixels[row * 9 + col] > pixels[row * 9 + col + 1] for row in range(8) for col in range(8)]
    return sum(bit << index for index, bit in enumerate(bits))


class BKTree:
    def __init__(self):
        self.root = None

    def add(self, value, index):
        if self.root is None:
            self.root = [value, [index], {}]
            return
        node = self.root
        while True:
            distance = hamming(value, node[0])
            if distance == 0:
                node[1].append(index)
                return
            if distance not in node[2]:
                node[2][distance] = [value, [index], {}]
                return
            node = node[2][distance]

    def search(self, value, radius):
        if self.root is None:
            return []
        matches, stack = [], [self.root]
        while stack:
            node = stack.pop()
            distance = hamming(value, node[0])
            if distance <= radius:
                matches.extend(node[1])
            stack.extend(child for edge, child in node[2].items() if distance - radius <= edge <= distance + radius)
        return matches


def image_quality(image, detector):
    array = np.asarray(image.convert("RGB"))
    height, width = array.shape[:2]
    scale = min(1.0, 1024 / max(width, height))
    if scale < 1:
        array = cv2.resize(array, (round(width * scale), round(height * scale)))
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    brightness = float(gray.mean())
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    detector.setInputSize((array.shape[1], array.shape[0]))
    _, faces = detector.detect(cv2.cvtColor(array, cv2.COLOR_RGB2BGR))
    faces = [] if faces is None else faces
    face_ratio = max((face[2] * face[3] / (array.shape[0] * array.shape[1]) for face in faces), default=0.0)
    if len(faces) == 0:
        status = "no_face"
    elif len(faces) > 1:
        status = "multiple_faces"
    elif face_ratio < 0.08:
        status = "face_too_small"
    elif brightness < 45:
        status = "underexposed"
    elif brightness > 220:
        status = "overexposed"
    elif blur < 80:
        status = "blurry"
    else:
        status = "pass"
    return len(faces), round(face_ratio, 4), round(brightness, 2), round(blur, 2), status


def scan_source(name, root, detector=None):
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS):
        relative = path.relative_to(root)
        label = relative.parts[-2] if len(relative.parts) > 1 else root.name
        normalized = normalized_label(label)
        weak_concern = LABEL_MAP.get(normalized, "")
        acne_zero = normalized.startswith("acne0_")
        if normalized.startswith(("acne1_", "acne2_", "acne3_")):
            weak_concern = "blemishes"
        row = {
            "image_id": hashlib.sha1(f"{name}:{relative}".encode()).hexdigest()[:16],
            "source": name,
            "source_image_id": relative.as_posix(),
            "original_path": str(path.resolve()),
            "original_label": label,
            "sha256": "",
            "dhash": "",
            "exact_group": "",
            "duplicate_group": "",
            "width": "",
            "height": "",
            "format": "",
            "usable": 1,
            "quality_status": "pending_face_quality_check",
            "face_count": "",
            "face_ratio": "",
            "brightness": "",
            "blur_score": "",
            "is_generated": int(bool(GENERATED_RE.search(path.stem))),
            "weak_concern": weak_concern,
            "label_origin": "source_folder" if weak_concern else "unmapped",
            "review_status": "pending",
            **{concern: 0 if concern == "blemishes" and acne_zero else 1 if concern == weak_concern else -1 for concern in CONCERNS},
        }
        try:
            data = path.read_bytes()
            row["sha256"] = hashlib.sha256(data).hexdigest()
            with Image.open(path) as image:
                image.load()
                row.update(width=image.width, height=image.height, format=image.format or "", dhash=f"{dhash(image):016x}")
                if min(image.size) < 128:
                    row["quality_status"] = "too_small"
                elif detector is not None:
                    face_count, face_ratio, brightness, blur, status = image_quality(image, detector)
                    row.update(
                        face_count=face_count,
                        face_ratio=face_ratio,
                        brightness=brightness,
                        blur_score=blur,
                        quality_status=status,
                    )
        except (OSError, ValueError):
            row.update(usable=0, quality_status="corrupt")
        rows.append(row)
    return rows


def assign_duplicate_groups(rows, radius):
    parent = list(range(len(rows)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    exact = defaultdict(list)
    tree = BKTree()
    for index, row in enumerate(rows):
        if not row["sha256"] or not row["dhash"]:
            continue
        exact[row["sha256"]].append(index)
        value = int(row["dhash"], 16)
        for match in tree.search(value, radius):
            union(index, match)
        tree.add(value, index)
    for indices in exact.values():
        for index in indices[1:]:
            union(indices[0], index)
    exact_groups = [indices for indices in exact.values() if len(indices) > 1]
    for number, indices in enumerate(sorted(exact_groups, key=lambda item: (-len(item), item[0])), 1):
        for index in indices:
            rows[index]["exact_group"] = f"exact_{number:05d}"

    groups = defaultdict(list)
    for index in range(len(rows)):
        groups[find(index)].append(index)
    duplicate_groups = [indices for indices in groups.values() if len(indices) > 1]
    for number, indices in enumerate(sorted(duplicate_groups, key=lambda item: (-len(item), item[0])), 1):
        group_id = f"dup_{number:05d}"
        for index in indices:
            rows[index]["duplicate_group"] = group_id
    return duplicate_groups


def write_outputs(rows, duplicate_groups, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "all_images.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "total_images": len(rows),
        "sources": dict(Counter(row["source"] for row in rows)),
        "labels": dict(Counter(f"{row['source']}:{row['original_label']}" for row in rows)),
        "corrupt": sum(not row["usable"] for row in rows),
        "too_small": sum(row["quality_status"] == "too_small" for row in rows),
        "pre_generated": sum(row["is_generated"] for row in rows),
        "quality_statuses": dict(Counter(row["quality_status"] for row in rows)),
        "duplicate_groups": len(duplicate_groups),
        "images_in_duplicate_groups": sum(map(len, duplicate_groups)),
        "exact_duplicate_groups": len({row["exact_group"] for row in rows if row["exact_group"]}),
        "images_in_exact_duplicate_groups": sum(bool(row["exact_group"]) for row in rows),
        "cross_source_duplicate_groups": sum(
            len({rows[index]["source"] for index in indices}) > 1 for indices in duplicate_groups
        ),
        "weak_concerns": dict(Counter(row["weak_concern"] or "unmapped" for row in rows)),
    }
    (output_dir / "dataset_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return manifest, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/reports"))
    parser.add_argument("--near-duplicate-distance", type=int, default=3)
    parser.add_argument("--face-model", type=Path)
    args = parser.parse_args()

    detector = None
    if args.face_model:
        if cv2 is None:
            parser.error("OpenCV is required for --face-model")
        if not args.face_model.is_file():
            parser.error(f"face model not found: {args.face_model}")
        detector = cv2.FaceDetectorYN.create(str(args.face_model), "", (320, 320), score_threshold=0.8)

    rows = []
    for spec in args.source:
        name, separator, path = spec.partition("=")
        root = Path(path)
        if not separator or not name or not root.is_dir():
            parser.error(f"invalid source {spec!r}; expected NAME=EXISTING_DIRECTORY")
        rows.extend(scan_source(name, root, detector))
    if not rows:
        parser.error("no supported images found")

    duplicates = assign_duplicate_groups(rows, args.near_duplicate_distance)
    manifest, report = write_outputs(rows, duplicates, args.output_dir)
    print(json.dumps(report, indent=2))
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
