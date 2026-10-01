#!/usr/bin/env python3
"""Merge human-reviewed training labels into a new dataset; freeze held-out files."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from PIL import Image

from scripts.audit_vision_dataset import BKTree, dhash

CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def reviewed_labels(row):
    labels = {name: str(row[name]) for name in CONCERNS}
    if any(value not in {"-1", "0", "1"} for value in labels.values()):
        raise ValueError("Reviewed labels must be -1, 0, or 1")
    if str(row["usable"]) not in {"0", "1"}:
        raise ValueError("Usable must be 0 or 1")
    scope = row["image_scope"]
    if scope not in {"full_face", "facial_closeup", "not_facial"}:
        raise ValueError("Unexpected reviewed image scope")
    if str(row["usable"]) != "1" or scope == "not_facial":
        return None
    return labels if any(value != "-1" for value in labels.values()) else None


def fill_unknown_labels(original, reviewed):
    result, changes = original.copy(), 0
    for name in CONCERNS:
        if str(original[name]) == "-1" and str(reviewed[name]) != "-1":
            result[name] = str(reviewed[name])
            changes += 1
    return result, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--base-dir", type=Path, default=Path("data/vision/manifests_v2"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("Output directory exists; choose a new directory to preserve existing work")
    queue = pd.read_csv(args.queue, dtype=str).fillna("")
    annotations = pd.read_csv(args.annotations, dtype=str).fillna("")
    if queue.image_id.duplicated().any() or annotations.image_id.duplicated().any():
        parser.error("Duplicate image IDs in review files")
    if not set(annotations.image_id).issubset(set(queue.image_id)):
        parser.error("Annotations contain IDs outside this queue")
    if not queue.split.eq("train").all():
        parser.error("This merger accepts training-only queues")

    train = pd.read_csv(args.base_dir / "train.csv", dtype=str).fillna("")
    heldout_groups, heldout_ids = set(), set()
    for split in ("validation", "test"):
        heldout = pd.read_csv(args.base_dir / f"{split}.csv", dtype=str)
        heldout_groups.update(heldout.duplicate_group)
        heldout_ids.update(heldout.image_id)
    if set(queue.image_id) & heldout_ids or set(queue.duplicate_group) & heldout_groups:
        parser.error("Review queue overlaps held-out IDs or duplicate groups")

    exact, tree = set(), BKTree()
    for split in ("train", "validation", "test"):
        manifest = args.base_dir / f"{split}.csv"
        for path in pd.read_csv(manifest).original_path:
            path = Path(path)
            if not path.is_absolute():
                parser.error("Base manifests must use absolute image paths to copy splits unchanged")
            exact.add(hashlib.sha256(path.read_bytes()).hexdigest())
            with Image.open(path) as image:
                tree.add(dhash(image), str(path))

    positions = {value: index for index, value in enumerate(train.image_id)}
    queue_rows = queue.set_index("image_id").to_dict("index")
    additions, removed, filled, skipped, retained_known = [], [], 0, 0, 0
    for annotation in annotations.to_dict("records"):
        image_id = annotation["image_id"]
        labels = reviewed_labels(annotation)
        if labels is None:
            if image_id in positions and (annotation["usable"] == "0" or annotation["image_scope"] == "not_facial"):
                removed.append(positions[image_id])
            skipped += 1
            continue
        row = queue_rows[image_id]
        if image_id in positions:
            index = positions[image_id]
            original = train.loc[index].to_dict()
            if original["duplicate_group"] != row["duplicate_group"]:
                parser.error("Existing image's duplicate group differs from the queue")
            if Path(original["original_path"]).resolve() != Path(row["original_path"]).resolve():
                parser.error("Existing image's path differs from the queue")
            merged, changes = fill_unknown_labels(original, labels)
            retained_known += sum(str(original[name]) != "-1" and labels[name] != "-1"
                                  and str(original[name]) != labels[name] for name in CONCERNS)
            for name in CONCERNS:
                train.loc[index, name] = merged[name]
                weight = name + "_weight"
                if str(original[name]) == "-1" and labels[name] != "-1" and weight in train.columns:
                    train.loc[index, weight] = "1.0"
            filled += changes
        else:
            path = Path(row["original_path"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if row.get("sha256") and digest != row["sha256"]:
                parser.error("Downloaded image changed since review queue creation")
            with Image.open(path) as image:
                perceptual = dhash(image)
            if digest in exact or tree.search(perceptual, 4):
                skipped += 1
                continue
            exact.add(digest)
            tree.add(perceptual, image_id)
            addition = {name: row.get(name, "") for name in train.columns}
            addition.update(image_id=image_id, original_path=str(path.resolve()),
                            image_scope=annotation["image_scope"], **labels)
            for name in CONCERNS:
                if name + "_weight" in train.columns:
                    addition[name + "_weight"] = "1.0" if labels[name] != "-1" else "0.0"
            additions.append(addition)
    if not additions and not filled and not removed:
        parser.error("No new usable human-reviewed labels; do not retrain on unchanged/unknown data")
    args.output_dir.mkdir(parents=True)
    pd.concat([train.drop(index=removed), pd.DataFrame(additions)], ignore_index=True).to_csv(args.output_dir / "train.csv", index=False)
    for split in ("validation", "test"):
        shutil.copyfile(args.base_dir / f"{split}.csv", args.output_dir / f"{split}.csv")
    report = {"annotation_source": str(args.annotations), "review_queue": str(args.queue),
              "filled_unknown_training_labels": filled, "added_training_images": len(additions),
              "removed_human_rejected_training_images": len(removed),
              "skipped_unusable_unknown_or_duplicate": skipped,
              "retained_original_known_labels_despite_review_disagreement": retained_known,
              "unreviewed_images": len(queue) - len(annotations), "heldout_files_copied_unchanged": True}
    (args.output_dir / "human_review_merge.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
