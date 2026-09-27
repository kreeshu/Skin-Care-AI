#!/usr/bin/env python3
"""Add FFHQ-Wrinkle faces to the reviewed manifests as fine_lines labels.

FFHQ-Wrinkle (CC BY-NC-SA 4.0) provides 1,000 human-drawn wrinkle masks on FFHQ faces.
Every mask marks some wrinkles, so the wrinkle-pixel fraction is split into tertiles:
lowest third = absent (0), highest third = present (1), middle third = unknown (-1).
Positives and negatives share one source, which breaks the "wrinkles folder" shortcut.
Other concerns stay -1 because they were not annotated.
"""

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("dataset_sources/extracted/ffhq_wrinkle"))
    parser.add_argument("--manifests-dir", type=Path, default=Path("data/vision/manifests"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/manifests_v2"))
    args = parser.parse_args()

    rows = []
    for mask_path in sorted((args.source / "manual_wrinkle_masks").glob("*.png")):
        image_id = mask_path.stem
        image_path = args.source / "images" / f"Part{int(image_id) // 10000 + 1}" / f"{image_id}.png"
        if not image_path.exists():
            continue
        # Deterministic 60/20/20 split from the id, so reruns give the same split.
        bucket = int(hashlib.sha256(image_id.encode()).hexdigest(), 16) % 10
        rows.append({
            "image_id": "ffhq_" + image_id,
            "original_path": str(image_path.resolve()),
            "source": "ffhq_wrinkle",
            "original_label": "ffhq",
            "duplicate_group": "ffhq_" + image_id,
            "image_scope": "full_face",
            "split": "train" if bucket < 6 else "validation" if bucket < 8 else "test",
            "coverage": (np.asarray(Image.open(mask_path)) > 0).mean(),
        })
    ffhq = pd.DataFrame(rows)
    low, high = ffhq["coverage"].quantile([1 / 3, 2 / 3])
    for name in CONCERNS:
        ffhq[name] = -1
    ffhq["fine_lines"] = np.select([ffhq["coverage"] <= low, ffhq["coverage"] >= high], [0, 1], -1)
    print(f"{len(ffhq)} FFHQ faces; absent <= {low:.4f}, present >= {high:.4f}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ffhq.drop(columns="coverage").to_csv(args.output_dir / "ffhq_wrinkle.csv", index=False)
    for split in ("train", "validation", "test"):
        reviewed = pd.read_csv(args.manifests_dir / f"{split}.csv")
        added = ffhq[ffhq["split"] == split][reviewed.columns]
        pd.concat([reviewed, added]).to_csv(args.output_dir / f"{split}.csv", index=False)
        counts = added["fine_lines"].value_counts().to_dict()
        print(f"{split}: {len(reviewed)} reviewed + {len(added)} FFHQ (fine_lines {counts})")


if __name__ == "__main__":
    main()
