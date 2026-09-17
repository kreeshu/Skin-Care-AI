#!/usr/bin/env python3
"""Validate finalized vision manifests before model training."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def validate(rows):
    errors = []
    ids = Counter(row["image_id"] for row in rows)
    errors.extend(f"duplicate image_id: {image_id}" for image_id, count in ids.items() if count > 1)

    group_splits = defaultdict(set)
    label_counts = {split: {concern: Counter() for concern in CONCERNS} for split in ("train", "validation", "test")}
    for row in rows:
        split = row["split"]
        if split not in label_counts:
            errors.append(f"invalid split for {row['image_id']}: {split}")
            continue
        group_splits[row["duplicate_group"]].add(split)
        if not Path(row["original_path"]).is_file():
            errors.append(f"missing image: {row['original_path']}")
        for concern in CONCERNS:
            value = row[concern]
            if value not in {"-1", "0", "1"}:
                errors.append(f"invalid {concern} label for {row['image_id']}: {value}")
            else:
                label_counts[split][concern][value] += 1

    errors.extend(
        f"duplicate group crosses splits: {group}"
        for group, splits in group_splits.items()
        if len(splits) > 1
    )
    for split in label_counts:
        for concern, counts in label_counts[split].items():
            if not counts["1"]:
                errors.append(f"{split} has no positive {concern} labels")
            if not counts["0"]:
                errors.append(f"{split} has no negative {concern} labels")
    return errors, label_counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_dir", type=Path, nargs="?", default=Path("data/vision/manifests"))
    args = parser.parse_args()

    rows = []
    for split in ("train", "validation", "test"):
        path = args.manifest_dir / f"{split}.csv"
        if not path.is_file():
            parser.error(f"missing finalized manifest: {path}")
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))

    errors, counts = validate(rows)
    report = {
        "valid": not errors,
        "total": len(rows),
        "errors": errors,
        "label_counts": counts,
    }
    output = args.manifest_dir / "validation_report.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
