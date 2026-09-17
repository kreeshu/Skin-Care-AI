#!/usr/bin/env python3
"""Repair annotations affected by persistent Streamlit widget state."""

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("annotations", type=Path)
    args = parser.parse_args()

    backup = args.annotations.with_name(
        f"{args.annotations.stem}.before_state_repair_{datetime.now():%Y%m%d_%H%M%S}.csv"
    )
    shutil.copy2(args.annotations, backup)

    with args.annotations.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    repaired = 0
    for row in rows:
        expected = "0" if row["image_scope"] == "not_facial" else "1"
        if row["usable"] != expected:
            row["usable"] = expected
            repaired += 1

    fieldnames = list(rows[0])
    with args.annotations.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Backed up to {backup}")
    print(f"Repaired usable state on {repaired} of {len(rows)} annotations")


if __name__ == "__main__":
    main()
