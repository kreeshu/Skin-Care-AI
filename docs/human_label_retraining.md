# Human-reviewed labels before retraining

## Download outcome

A bounded subset was downloaded from the consented [SCIN dataset](https://github.com/google-research-datasets/scin). License text, source documentation, and metadata are retained in `dataset_sources/extracted/scin_cosmetic_candidates/`. The [SCIN Data Use License](https://raw.githubusercontent.com/google-research-datasets/scin/main/LICENSE) requires attribution and prohibits attempts to re-identify/re-link contributors. Privacy masks must not be removed or reconstructed.

72 head/neck cases were selected using diagnoses or self-reported cosmetic categories **for candidate selection only**. Two were excluded by exact/perceptual duplicate filtering. 70 images (82,132,103 bytes) were retained, but none passed the existing full-face detector. An inspected sample includes privacy-masked faces, facial close-ups, necks, and non-face skin. Thus this is a **quarantined review pool**, not 70 usable training images. Exact/perceptual checks do not establish subject independence.

Every cosmetic label remains unknown. Case-level differentials are not presence/absence annotations for the five concerns. No diagnoses, missing diagnoses, or self-reported "healthy" categories were turned into cosmetic ground truth. No new labels were added to training and no retraining was started on this unreviewed pool.

Download reports: `data/vision/scin_review/download_report.json` (first download) and `data/vision/scin_review_20260930/download_report.json` (cached re-audit). The latter correctly reports zero new downloaded bytes.

## Review the existing training images first

These already match the project's accepted sources and do not touch held-out data:

```bash
VISION_REVIEW_QUEUE=data/vision/manifests_v2/additional_training_review.csv \
VISION_ANNOTATION_OUTPUT=data/vision/annotations/additional_training_labels.csv \
./venv/bin/streamlit run app/annotate_vision_dataset.py --server.address 127.0.0.1 --server.port 8502
```

Review independently visible blemishes, dark spots, redness, visible pores, and fine lines. If resolution, lighting, occlusion, or framing prevents assessment, choose unknown—not absent. Mark unusable or non-facial images accordingly. Existing known labels are preserved by the merger; disagreements are counted, not silently substituted.

To review downloaded images separately, use `VISION_REVIEW_QUEUE=data/vision/scin_review_20260930/quarantine_review.csv` and `VISION_ANNOTATION_OUTPUT=data/vision/annotations/scin_cosmetic_labels.csv`. Most may be unsuitable for the full-face application. Do not remove privacy masking or infer cosmetic labels from medical conditions.

## After actual human review

Partial review is supported; unreviewed images never receive inferred labels. The merge writes a new directory, fills only unknown training labels, excludes human-rejected training images, checks newly added images for exact/perceptual overlap, and copies validation/test CSVs byte-for-byte. It refuses to proceed when there are no usable changes.

```bash
./venv/bin/python scripts/merge_training_review.py \
  data/vision/manifests_v2/additional_training_review.csv \
  data/vision/annotations/additional_training_labels.csv \
  --output-dir data/vision/manifests_human_reviewed

./venv/bin/python scripts/validate_vision_manifests.py data/vision/manifests_human_reviewed

./venv/bin/python src/model/train_concern.py \
  --manifests-dir data/vision/manifests_human_reviewed \
  --model-dir models/concern_human_reviewed \
  --initial-weights models/concern_v2/skin_concern_pilot.weights.h5 \
  --selection-metric roc_auc --seed 42

./venv/bin/python src/model/evaluate_concern.py \
  --validation-manifest data/vision/manifests_human_reviewed/validation.csv \
  --test-manifest data/vision/manifests_human_reviewed/test.csv \
  --weights models/concern_human_reviewed/skin_concern_pilot.weights.h5 \
  --output models/concern_human_reviewed/evaluation.json
```

Choose new output directories for subsequent runs. The earlier class-balanced candidate regressed several labels, so balancing is **not** enabled by default here. Keep the deployed weights until validated improvements justify replacement. The inspected test set is a regression set, not a fresh independent benchmark; 85%+ performance cannot be promised.

## Completed human-review experiment

All 200 existing training images were reviewed. The merge filled 868 unknown labels and removed five human-rejected images, leaving 1,217 training images. Seven disagreements with existing fine-line labels were recorded and the original known labels were preserved. The annotation snapshot and input hashes are in `data/vision/manifests_human_reviewed/`.

Training used the existing weights, no class balancing, seed 42, up to 12 frozen-backbone epochs and seven fine-tuning epochs. The phase-B checkpoint won on validation macro ROC-AUC (0.7057 versus the original 0.6855). Thresholds were selected on validation only. Actual `SkinAnalyzer` preprocessing and binary scores were verified against evaluation on all 479 test images.

| Test metric | Original | Human-reviewed candidate |
| --- | ---: | ---: |
| Pooled known-label accuracy | 73.20% | 76.29% |
| Macro F1 | 77.95% | 78.94% |
| Macro balanced accuracy | 63.49% | 67.00% |
| Macro ROC-AUC | 0.7174 | 0.7338 |

| Concern | Original accuracy | Candidate accuracy |
| --- | ---: | ---: |
| Blemishes | 94.06% | 90.10% |
| Dark spots | 64.37% | 50.57% |
| Redness | 55.24% | 77.14% |
| Visible pores | 56.36% | 60.00% |
| Fine lines | 79.49% | 83.33% |

**85% pooled accuracy was not reached. The candidate was not deployed** because individual-label tradeoffs need review. Original weights and held-out manifest bytes were verified unchanged. These metrics exclude the face gate and uncertain-state handling; the test set is still the previously inspected regression set, not new independent evidence.

Artifacts: `models/concern_human_reviewed/evaluation.json`, `comparison.json`, and `training_selection.json`; training log: `training_concern_human_reviewed.log`.
