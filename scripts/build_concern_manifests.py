#!/usr/bin/env python3
"""Build confidence-weighted concern manifests from audited and gold labels."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")
ALLOWED_STATUSES = {"accepted_academic", "partial_review"}
ALLOWED_EXISTING_LABELS = {"Acne", "Dark Spot", "Rosacea"}


def split_for(row):
    key = row["duplicate_group"] or row["sha256"]
    bucket = int(hashlib.sha1(key.encode()).hexdigest()[:8], 16) % 100
    return "train" if bucket < 70 else "validation" if bucket < 85 else "test"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_manifest", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("data/vision/source_registry.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/manifests"))
    parser.add_argument("--positive-weight", type=float, default=0.8)
    parser.add_argument("--weak-negative-weight", type=float, default=0.15)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    with args.annotations.open(newline="", encoding="utf-8") as handle:
        annotations = {row["image_id"]: row for row in csv.DictReader(handle)}
    with args.audit_manifest.open(newline="", encoding="utf-8") as handle:
        audited = list(csv.DictReader(handle))

    candidates = []
    for row in audited:
        source = row["source"]
        if registry.get(source, {}).get("status") not in ALLOWED_STATUSES:
            continue
        if source == "existing_conditions" and row["original_label"] not in ALLOWED_EXISTING_LABELS:
            continue
        if row["usable"] != "1" or row["is_generated"] == "1" or row["quality_status"] in {"corrupt", "too_small"}:
            continue
        if row["format"].upper() not in {"JPEG", "PNG", "BMP", "GIF"}:
            continue

        gold = annotations.get(row["image_id"])
        if gold and (gold["usable"] != "1" or gold["image_scope"] == "not_facial"):
            continue
        concern = row["weak_concern"]
        acne_zero = source == "acne04_level0"
        labels = {name: 0 for name in CONCERNS}
        weights = {name: args.weak_negative_weight for name in CONCERNS}
        if concern:
            labels[concern] = 1
            weights[concern] = args.positive_weight
        elif acne_zero:
            labels["blemishes"] = 0
            weights["blemishes"] = args.positive_weight
        else:
            continue
        if gold:
            for name in CONCERNS:
                labels[name] = int(gold[name])
                weights[name] = 0.0 if labels[name] < 0 else 1.0

        candidates.append({
            "image_id": row["image_id"],
            "original_path": row["original_path"],
            "source": source,
            "original_label": row["original_label"],
            "duplicate_group": row["duplicate_group"] or row["sha256"],
            "split": split_for(row),
            "label_origin": "gold" if gold else "weak",
            **labels,
            **{f"{name}_weight": weights[name] for name in CONCERNS},
        })

    # Keep one copy of exact duplicates, preferring reviewed and higher-resolution audit order.
    by_hash = {}
    audit_by_id = {row["image_id"]: row for row in audited}
    for row in candidates:
        audit = audit_by_id[row["image_id"]]
        key = audit["sha256"]
        rank = (row["label_origin"] == "gold", int(audit["width"]) * int(audit["height"]))
        if key not in by_hash or rank > by_hash[key][0]:
            by_hash[key] = rank, row
    rows = [item[1] for item in by_hash.values()]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    for split in ("train", "validation"):
        selected = [row for row in rows if row["split"] == split]
        with (args.output_dir / f"{split}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(selected)
    for split in ("validation", "test"):
        selected = [row for row in rows if row["split"] == split and row["label_origin"] == "gold"]
        with (args.output_dir / f"gold_{split}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(selected)

    summary = {
        "total": len(rows),
        "splits": Counter(row["split"] for row in rows),
        "origins": Counter(row["label_origin"] for row in rows),
        "sources": Counter(row["source"] for row in rows),
    }
    (args.output_dir / "concern_manifest_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
