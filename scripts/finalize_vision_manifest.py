#!/usr/bin/env python3
"""Merge completed gold annotations into leakage-safe train/validation/test manifests."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("queue", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/manifests"))
    args = parser.parse_args()

    with args.queue.open(newline="", encoding="utf-8") as handle:
        queue = list(csv.DictReader(handle))
    with args.annotations.open(newline="", encoding="utf-8") as handle:
        annotations = {row["image_id"]: row for row in csv.DictReader(handle)}
    missing = [row["image_id"] for row in queue if row["image_id"] not in annotations]
    if missing:
        parser.error(f"{len(missing)} images are not annotated; finish the review queue first")

    finalized = []
    for row in queue:
        annotation = annotations[row["image_id"]]
        if annotation["usable"] != "1" or annotation["image_scope"] == "not_facial":
            continue
        finalized.append({
            "image_id": row["image_id"],
            "original_path": row["original_path"],
            "source": row["source"],
            "original_label": row["original_label"],
            "duplicate_group": row["duplicate_group"] or row["sha256"],
            "image_scope": annotation["image_scope"],
            "split": row["split"],
            **{concern: annotation[concern] for concern in CONCERNS},
        })

    if not finalized:
        parser.error("all reviewed images were rejected")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for split in ("train", "validation", "test"):
        selected = [row for row in finalized if row["split"] == split]
        with (args.output_dir / f"{split}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(finalized[0]))
            writer.writeheader()
            writer.writerows(selected)
    summary = {
        "reviewed": len(queue),
        "accepted": len(finalized),
        "splits": Counter(row["split"] for row in finalized),
        "known_labels": {concern: Counter(row[concern] for row in finalized) for concern in CONCERNS},
    }
    (args.output_dir / "gold_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
