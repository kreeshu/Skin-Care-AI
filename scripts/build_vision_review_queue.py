#!/usr/bin/env python3
"""Build a balanced, deduplicated gold-label review queue from an audit manifest."""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")
ALLOWED_STATUSES = {"accepted_academic", "partial_review"}
ALLOWED_EXISTING_LABELS = {"Acne", "Dark Spot", "Rosacea"}


def split_for(row):
    group = row.get("duplicate_group") or row["sha256"]
    bucket = int(hashlib.sha1(group.encode()).hexdigest()[:8], 16) % 100
    return "train" if bucket < 55 else "validation" if bucket < 75 else "test"


def priority(row):
    source_rank = 0 if row["source"].startswith("acne04_") else 1 if row["source"] == "facial_skin_concerns" else 2
    quality_rank = {"pass": 0, "blurry": 1, "no_face": 2}.get(row["quality_status"], 3)
    stable = hashlib.sha1(row["image_id"].encode()).hexdigest()
    return source_rank, quality_rank, stable


def build_queue(rows, registry, per_concern):
    exact_seen = set()
    candidates = defaultdict(list)
    for row in sorted(rows, key=priority):
        source = row["source"]
        if registry.get(source, {}).get("status") not in ALLOWED_STATUSES:
            continue
        if source == "existing_conditions" and row["original_label"] not in ALLOWED_EXISTING_LABELS:
            continue
        if row["usable"] != "1" or row["is_generated"] == "1" or row["quality_status"] in {"corrupt", "too_small"}:
            continue
        exact_key = row["sha256"]
        if exact_key in exact_seen:
            continue
        exact_seen.add(exact_key)
        concern = row["weak_concern"]
        if concern in CONCERNS:
            row["image_scope"] = "full_face" if row["face_count"] == "1" else "closeup_or_unverified"
            candidates[concern].append(row)

    queue = []
    for concern in CONCERNS:
        pool = candidates[concern]
        by_source = defaultdict(list)
        for row in pool:
            by_source[row["source"]].append(row)
        while len([row for row in queue if row["review_concern"] == concern]) < per_concern and any(by_source.values()):
            for source in sorted(by_source, key=lambda item: (len(by_source[item]), item), reverse=True):
                if by_source[source]:
                    row = by_source[source].pop(0).copy()
                    row["review_concern"] = concern
                    row["split"] = split_for(row)
                    queue.append(row)
                    if len([item for item in queue if item["review_concern"] == concern]) >= per_concern:
                        break
    return queue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("data/vision/source_registry.json"))
    parser.add_argument("--output", type=Path, default=Path("data/vision/manifests/review_queue.csv"))
    parser.add_argument("--per-concern", type=int, default=280)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    queue = build_queue(rows, registry, args.per_concern)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(queue[0])
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(queue)
    print(json.dumps({"total": len(queue), "concerns": Counter(row["review_concern"] for row in queue), "sources": Counter(row["source"] for row in queue)}, indent=2))


if __name__ == "__main__":
    main()
