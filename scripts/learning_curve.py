#!/usr/bin/env python3
"""Train the concern model on growing fractions of the training set and plot test ROC-AUC.

A curve still rising at 100% is evidence that more labelled data would improve the model.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")


def run(*args):
    subprocess.run([sys.executable, *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifests-dir", type=Path, default=Path("data/vision/manifests"))
    parser.add_argument("--work-dir", type=Path, default=Path("models/learning_curve"))
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.25, 0.5, 0.75, 1.0])
    parser.add_argument("--seeds", type=int, default=2)
    args = parser.parse_args()

    train = pd.read_csv(args.manifests_dir / "train.csv")
    results = []
    for fraction in args.fractions:
        for seed in range(args.seeds):
            name = f"f{int(fraction * 100)}_s{seed}"
            run_dir = args.work_dir / name
            evaluation = run_dir / "evaluation.json"
            if not evaluation.exists():  # resumable: skip finished runs
                run_dir.mkdir(parents=True, exist_ok=True)
                subset = run_dir / "train.csv"
                train.sample(frac=fraction, random_state=seed).to_csv(subset, index=False)
                run("src/model/train_concern.py", "--train-manifest", str(subset),
                    "--validation-manifest", str(args.manifests_dir / "validation.csv"), "--model-dir", str(run_dir))
                run("src/model/evaluate_concern.py", "--validation-manifest", str(args.manifests_dir / "validation.csv"),
                    "--test-manifest", str(args.manifests_dir / "test.csv"),
                    "--weights", str(run_dir / "skin_concern_pilot.weights.h5"), "--output", str(evaluation))
            metrics = json.loads(evaluation.read_text())["metrics"]
            results.append({"fraction": fraction, "seed": seed, "train_images": round(len(train) * fraction),
                            **{c: metrics[c]["roc_auc"] for c in CONCERNS}})
            print(results[-1], flush=True)

    frame = pd.DataFrame(results)
    summary = frame.groupby(["fraction", "train_images"])[list(CONCERNS)].agg(["mean", "std"])
    summary.to_csv(args.work_dir / "learning_curve.csv")
    print(summary.round(3).to_string())

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    means = frame.groupby("train_images")[list(CONCERNS)].mean()
    stds = frame.groupby("train_images")[list(CONCERNS)].std().fillna(0)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for concern in CONCERNS:
        ax.errorbar(means.index, means[concern], yerr=stds[concern], marker="o", capsize=3, label=concern)
    ax.axhline(0.5, color="grey", linestyle="--", linewidth=1, label="chance")
    ax.set(xlabel="Training images", ylabel="Test ROC-AUC", title="Learning curve (mean ± std over seeds)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(args.work_dir / "learning_curve.png", dpi=150)
    print("saved", args.work_dir / "learning_curve.png")


if __name__ == "__main__":
    main()
