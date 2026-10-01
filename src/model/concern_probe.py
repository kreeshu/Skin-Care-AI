"""Concern model on frozen foundation-model features with per-concern logistic heads.

Features are extracted once per backbone and cached, so heads can be tuned with grouped
cross-validation in seconds instead of retraining a CNN for every setting. Unknown (-1)
labels are skipped per concern and never become negatives. Heads train on train +
validation; thresholds come from out-of-fold predictions; only `final` scores the test split.
"""

import argparse
import itertools
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import joblib
import numpy as np
import pandas as pd
import torch
from joblib import Parallel, delayed
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CONCERNS = ("blemishes", "dark_spots", "redness", "visible_pores", "fine_lines")
BACKBONES = {
    # name: (Hugging Face model id, family, square input size, patch pooling)
    "dinov2_base_224": ("facebook/dinov2-base", "dinov2", 224, "mean"),
    "dinov2_base_448": ("facebook/dinov2-base", "dinov2", 448, "mean"),
    "dinov2_large_224": ("facebook/dinov2-large", "dinov2", 224, "mean"),
    "dinov2_large_448": ("facebook/dinov2-large", "dinov2", 448, "mean"),
    "monet_224": ("suinleelab/monet", "clip", 224, "mean"),
    "monet_224_max": ("suinleelab/monet", "clip", 224, "mean+max"),
    "siglip_so400m_384": ("google/siglip-so400m-patch14-384", "siglip", 384, "mean"),
    "convnextv2_base_384": ("facebook/convnextv2-base-22k-384", "convnext", 384, "mean"),
    "convnextv2_base_384_max": ("facebook/convnextv2-base-22k-384", "convnext", 384, "mean+max"),
    "convnextv2_large_384": ("facebook/convnextv2-large-22k-384", "convnext", 384, "mean"),
}
SETTINGS = [(C, weight) for C in (0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3) for weight in (None, "balanced")]
CACHE_DIR = Path("outputs/concern_features")


def square_rgb(image, size):
    # Whole photo squashed to a square, like the CNN pipeline; PIL bicubic resizing is antialiased.
    return image.convert("RGB").resize((size, size), Image.BICUBIC)


def load_rgb(path, size):
    with Image.open(path) as image:
        return square_rgb(image, size)


class FeatureExtractor:
    def __init__(self, name, device=None):
        from transformers import AutoImageProcessor, AutoModel, CLIPVisionModel, SiglipVisionModel

        model_id, self.family, self.size, self.pooling = BACKBONES[name]
        self.device = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        processor = AutoImageProcessor.from_pretrained(model_id)
        self.mean = torch.tensor(processor.image_mean).view(1, 3, 1, 1)
        self.std = torch.tensor(processor.image_std).view(1, 3, 1, 1)
        model_class = {"clip": CLIPVisionModel, "siglip": SiglipVisionModel}.get(self.family, AutoModel)
        self.model = model_class.from_pretrained(model_id).eval().to(self.device)

    @torch.no_grad()
    def embed(self, images):
        """Average of the original and mirrored embeddings (flip test-time augmentation)."""
        batch = torch.from_numpy(np.stack([np.asarray(image) for image in images])).permute(0, 3, 1, 2)
        batch = (batch.float() / 255.0 - self.mean) / self.std
        views = [self._features(view.to(self.device)) for view in (batch, batch.flip(-1))]
        return ((views[0] + views[1]) / 2).cpu().numpy()

    def _features(self, pixels):
        output = self.model(pixel_values=pixels)
        if self.family == "convnext":
            patches = output.last_hidden_state.flatten(2).transpose(1, 2)  # (B, C, H, W) -> (B, HW, C)
            parts = [output.pooler_output]
        else:
            # Pooled token plus mean patch token: the patch average keeps local texture detail.
            patches = output.last_hidden_state[:, 1:] if self.family in ("dinov2", "clip") else output.last_hidden_state
            parts = [output.pooler_output, patches.mean(1)]
        if self.pooling == "mean+max":
            # Small local findings (a spot, a pore cluster) can vanish in an average; the max keeps them.
            parts.append(patches.amax(1))
        return torch.cat(parts, dim=1)


def extract_features(name, paths, cache_dir=CACHE_DIR, batch_size=16):
    cache = Path(cache_dir) / f"{name}.npz"
    stored = {}
    if cache.exists():
        data = np.load(cache)
        stored = dict(zip(data["paths"].tolist(), data["features"]))
    missing = [path for path in dict.fromkeys(paths) if path not in stored]
    if missing:
        extractor = FeatureExtractor(name)
        computed = []
        with ThreadPoolExecutor(8) as pool:
            images = pool.map(lambda path: load_rgb(path, extractor.size), missing)
            while batch := list(itertools.islice(images, batch_size)):
                computed.append(extractor.embed(batch))
                print(f"{name}: {sum(map(len, computed))}/{len(missing)}", end="\r", flush=True)
        print()
        stored.update(zip(missing, np.concatenate(computed).astype(np.float32)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez(cache, paths=np.array(list(stored)), features=np.stack(list(stored.values())))
    return np.stack([stored[path] for path in paths])


def grouped_folds(groups, k=5, seed=0):
    unique = sorted(set(groups))
    order = np.random.default_rng(seed).permutation(len(unique))
    fold = {unique[index]: rank % k for rank, index in enumerate(order)}
    return np.array([fold[group] for group in groups])


def fit_head(features, labels, C, class_weight):
    model = make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight=class_weight, max_iter=5000))
    return model.fit(features, labels)


def concern_oof(features, labels, folds, setting):
    """Out-of-fold probabilities for one concern (NaN where unknown) and the per-fold heads."""
    known = labels >= 0
    oof, heads = np.full(len(labels), np.nan), []
    for fold in range(folds.max() + 1):
        fit, held = known & (folds != fold), known & (folds == fold)
        heads.append(fit_head(features[fit], labels[fit], *setting))
        oof[held] = heads[-1].predict_proba(features[held])[:, 1]
    return oof, heads


def tune(features, labels, folds):
    """Choose C and class weighting per concern by out-of-fold ROC-AUC."""
    chosen = {}
    for index, name in enumerate(CONCERNS):
        known = labels[:, index] >= 0
        oofs = Parallel(n_jobs=-1)(delayed(concern_oof)(features, labels[:, index], folds, setting)
                                   for setting in SETTINGS)
        aucs = [roc_auc_score(labels[known, index], oof[known]) for oof, _ in oofs]
        chosen[name] = SETTINGS[int(np.argmax(aucs))]
    return chosen


def out_of_fold(features, labels, folds, settings):
    oof, heads = np.full(labels.shape, np.nan), {}
    for index, name in enumerate(CONCERNS):
        oof[:, index], heads[name] = concern_oof(features, labels[:, index], folds, settings[name])
    return oof, heads


def predict(heads, features):
    """Average the per-fold heads (a small bagged ensemble) for unseen images."""
    return np.stack([np.mean([head.predict_proba(features)[:, 1] for head in heads[name]], axis=0)
                     for name in CONCERNS], axis=1)


class ProbeConcernModel:
    """Serving wrapper: frozen backbones, saved heads, and out-of-fold thresholds."""

    def __init__(self, model_dir, device=None):
        model_dir = Path(model_dir)
        self.metadata = json.loads((model_dir / "probe_model.json").read_text())
        self.thresholds = self.metadata["thresholds"]
        self.heads = joblib.load(model_dir / "heads.joblib")
        self.extractors = {name: FeatureExtractor(name, device) for name in self.metadata["backbones"]}

    def predict_scores(self, image):
        """PIL image -> {concern: probability}, averaged over backbones as in training."""
        scores = [predict(self.heads[name]["heads"], extractor.embed([square_rgb(image, extractor.size)]))
                  for name, extractor in self.extractors.items()]
        return dict(zip(CONCERNS, np.mean(scores, axis=0)[0].tolist()))


def scored(labels, scores, thresholds=None):
    from src.model.evaluate_concern import best_thresholds, evaluate, summary

    thresholds = thresholds or best_thresholds(labels, scores)
    metrics = evaluate(labels, scores, thresholds)
    return thresholds, metrics, summary(metrics)


def pool_and_test(manifests_dir):
    pool = pd.concat([pd.read_csv(Path(manifests_dir) / f"{split}.csv") for split in ("train", "validation")],
                     ignore_index=True)
    return pool, pd.read_csv(Path(manifests_dir) / "test.csv")


def cross_validate(args):
    pool, test = pool_and_test(args.manifests_dir)
    labels = pool[list(CONCERNS)].to_numpy(int)
    folds = grouped_folds(pool.duplicate_group, seed=args.fold_seed)
    paths = pool.original_path.tolist() + test.original_path.tolist()
    # Extract every backbone before scoring: metric code imports TensorFlow, so keep the GPU users apart.
    all_features = {name: extract_features(name, paths)[:len(pool)] for name in args.backbones}
    results, oofs = {}, {}
    for name, features in all_features.items():
        settings = tune(features, labels, folds)
        oofs[name], _ = out_of_fold(features, labels, folds, settings)
        _, metrics, summary = scored(labels, oofs[name])
        results[name] = {"settings": settings, "summary": summary,
                         "roc_auc": {concern: metrics[concern]["roc_auc"] for concern in CONCERNS}}
        print(name, json.dumps(results[name]["roc_auc"]), "macro", round(summary["macro_roc_auc"], 4), flush=True)
    for size in range(2, len(args.backbones) + 1):
        for combo in itertools.combinations(args.backbones, size):
            _, metrics, summary = scored(labels, np.mean([oofs[name] for name in combo], axis=0))
            results["+".join(combo)] = {"summary": summary,
                                        "roc_auc": {concern: metrics[concern]["roc_auc"] for concern in CONCERNS}}
    ranking = sorted(results, key=lambda key: results[key]["summary"]["macro_roc_auc"], reverse=True)
    for key in ranking:
        summary = results[key]["summary"]
        print(f"{key:70} oof macro ROC-AUC {summary['macro_roc_auc']:.4f}  bal acc {summary['macro_balanced_accuracy']:.4f}"
              f"  acc {summary['macro_accuracy']:.4f}")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"manifests_dir": args.manifests_dir, "fold_seed": args.fold_seed,
                                  "selection": "out-of-fold ROC-AUC on train+validation; test not used",
                                  "results": results, "ranking": ranking}, indent=2, default=str) + "\n")


def final(args):
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        raise SystemExit("Output directory exists; choose a new one to preserve existing work")
    pool, test = pool_and_test(args.manifests_dir)
    labels, test_labels = pool[list(CONCERNS)].to_numpy(int), test[list(CONCERNS)].to_numpy(int)
    folds = grouped_folds(pool.duplicate_group, seed=args.fold_seed)
    paths = pool.original_path.tolist() + test.original_path.tolist()
    all_features = {name: extract_features(name, paths) for name in args.backbones}
    oofs, test_scores, models = [], [], {}
    for name, features in all_features.items():
        settings = tune(features[:len(pool)], labels, folds)
        oof, heads = out_of_fold(features[:len(pool)], labels, folds, settings)
        oofs.append(oof)
        test_scores.append(predict(heads, features[len(pool):]))
        models[name] = {"settings": settings, "heads": heads}
    thresholds, oof_metrics, oof_summary = scored(labels, np.mean(oofs, axis=0))
    _, metrics, summary = scored(test_labels, np.mean(test_scores, axis=0), thresholds)
    output_dir.mkdir(parents=True)
    joblib.dump(models, output_dir / "heads.joblib")
    metadata = {"labels": list(CONCERNS), "backbones": args.backbones,
                "settings": {name: models[name]["settings"] for name in args.backbones},
                "thresholds": thresholds, "manifests_dir": args.manifests_dir, "fold_seed": args.fold_seed}
    (output_dir / "probe_model.json").write_text(json.dumps(metadata, indent=2, default=str) + "\n")
    evaluation = {"test_source": str(Path(args.manifests_dir) / "test.csv"),
                  "threshold_source": "out-of-fold predictions on train+validation",
                  "threshold_objective": "Youden J (balanced accuracy), out-of-fold only",
                  "preprocessing": "RGB, PIL bicubic square resize, per-backbone normalization, flip-averaged features",
                  "metrics": metrics, "summary": summary,
                  "out_of_fold_metrics": oof_metrics, "out_of_fold_summary": oof_summary}
    (output_dir / "evaluation.json").write_text(json.dumps(evaluation, indent=2) + "\n")
    print(json.dumps({"test": summary, "out_of_fold": oof_summary}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cv = commands.add_parser("cv", help="Tune and compare backbones by out-of-fold metrics; test unused")
    cv.add_argument("--output", default="outputs/concern_probe/cv.json")
    done = commands.add_parser("final", help="Fit the chosen backbones and score the test split once")
    done.add_argument("--output-dir", required=True)
    for command in (cv, done):
        command.add_argument("--backbones", nargs="+", required=True, choices=sorted(BACKBONES))
        command.add_argument("--manifests-dir", default="data/vision/manifests_human_reviewed")
        command.add_argument("--fold-seed", type=int, default=0)
    args = parser.parse_args()
    cross_validate(args) if args.command == "cv" else final(args)


if __name__ == "__main__":
    main()
