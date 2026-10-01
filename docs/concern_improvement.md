# Concern model improvement experiment

## Changes

- Training, evaluation, and inference use the same RGB / TensorFlow bilinear resize / EfficientNet preprocessing (`src/model/concern_preprocessing.py`).
- Optional `--balance-labels` gives each observed positive/negative class equal total weight within a concern. Counts come from training only; unknown labels remain masked.
- `--selection-metric roc_auc` selects for discrimination instead of relying on PR-AUC on highly positive-skewed data.
- Final checkpoint selection compares the warm-start baseline and both training phases using validation only. Fine-tuning cannot silently replace a better checkpoint.
- Evaluation records accuracy, balanced accuracy, confusion matrices, manifest paths, and a weight hash. Thresholds still maximize validation Youden J; test labels never select thresholds.

## Separate candidate (original model preserved)

```bash
./venv/bin/python src/model/train_concern.py \
  --manifests-dir data/vision/manifests_v2 \
  --model-dir models/concern_balanced_20260930 \
  --initial-weights models/concern_v2/skin_concern_pilot.weights.h5 \
  --balance-labels --selection-metric roc_auc \
  --frozen-epochs 3 --fine-tune-epochs 7 --patience 3 --seed 42

./venv/bin/python src/model/evaluate_concern.py \
  --validation-manifest data/vision/manifests_v2/validation.csv \
  --test-manifest data/vision/manifests_v2/test.csv \
  --weights models/concern_balanced_20260930/skin_concern_pilot.weights.h5 \
  --output models/concern_balanced_20260930/evaluation.json
```

Choose a new model directory for each run; training refuses to overwrite final weights. Compare against `baseline_evaluation.json` in the candidate directory. Backend configuration remains on `concern_v2`; candidate performance is not a promise of improvement. Restart a running backend to pick up the preprocessing fix.

The existing test set has already been inspected. It remains useful for a regression comparison, but a new independent test set is needed for final generalization claims. Binary evaluation does not measure the face gate or the app's uncertain state.

## Completed experiment results

| Concern | Baseline accuracy | Balanced candidate accuracy |
| --- | ---: | ---: |
| Blemishes | 94.06% | 85.15% |
| Dark spots | 64.37% | 31.03% |
| Redness | 55.24% | 88.57% |
| Visible pores | 56.36% | 63.64% |
| Fine lines | 79.49% | 82.48% |

The candidate improved validation macro ROC-AUC from 0.6855 to 0.6975, but test macro F1 fell from 77.95% to 73.59% and test macro balanced accuracy fell from 63.49% to 61.68%. Its redness specificity was 0% (all eight negative examples were falsely positive). **Do not deploy this candidate as an overall improvement.** Original model weights and backend model configuration were preserved. No further experiments were selected using these test results.

The shared preprocessing fix remains useful independently: before the fix, backend-style resizing produced 70.27% pooled label accuracy; evaluation-consistent resizing produces the baseline's 73.20%. These are regression-set results, not a guarantee on new uploads.

## Human label review

The audit found only 19 training negatives each for redness and pores, and 9 for blemishes. Class weights cannot manufacture missing diversity.

`data/vision/manifests_v2/additional_training_review.csv` contains 200 existing training images with unknown dark-spot, redness, and pore labels. It excludes held-out duplicate groups and FFHQ's fine-lines-only source. Review may yield additional known labels; unclear concerns must remain unknown. These images are not new independent data.

Open the existing annotation UI with a separate queue and output:

```bash
VISION_REVIEW_QUEUE=data/vision/manifests_v2/additional_training_review.csv \
VISION_ANNOTATION_OUTPUT=data/vision/annotations/additional_training_labels.csv \
./venv/bin/streamlit run app/annotate_vision_dataset.py
```

No original annotations or manifests are changed by preparing the queue. After human review, merge into a **new training manifest** by image ID: only fill previously unknown labels with human-verified values, preserve known labels and duplicate groups, and exclude images marked unusable. Do not run the default finalizer against this training-only queue: it would not preserve the complete validation/test manifests.

## Checks

```bash
./venv/bin/python -m unittest scripts.test_concern_training scripts.test_concern_pipeline
./venv/bin/python scripts/validate_vision_manifests.py data/vision/manifests_v2
```
