#!/usr/bin/env python3
"""Create deterministic image grids for fast dataset label and quality review."""

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/vision/reports/contact_sheets"))
    parser.add_argument("--per-group", type=int, default=20)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    groups = defaultdict(list)
    for row in rows:
        groups[(row["source"], row["original_label"], row["quality_status"])].append(row)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for (source, label, status), candidates in sorted(groups.items()):
        candidates.sort(key=lambda row: hashlib.sha1(row["image_id"].encode()).hexdigest())
        selected = candidates[: args.per_group]
        sheet = Image.new("RGB", (5 * 220, 4 * 190), "white")
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(selected):
            try:
                with Image.open(row["original_path"]) as image:
                    thumb = ImageOps.fit(image.convert("RGB"), (210, 155))
            except OSError:
                continue
            x, y = (index % 5) * 220 + 5, (index // 5) * 190 + 5
            sheet.paste(thumb, (x, y))
            draw.text((x, y + 158), row["source_image_id"][-31:], fill="black")
        safe = lambda value: "_".join(value.lower().replace("/", "_").split())
        sheet.save(args.output_dir / f"{safe(source)}__{safe(label)}__{safe(status)}.jpg", quality=88)
        written += 1
    print(f"Wrote {written} contact sheets to {args.output_dir}")


if __name__ == "__main__":
    main()
