# Cosmetic Vision Dataset

The revised vision dataset targets five non-medical visible concerns: `blemishes`, `dark_spots`, `redness`, `visible_pores`, and `fine_lines`. Skin type is questionnaire-led and medical condition labels are excluded.

## Current Audit

The combined audit contains 26,847 files from the original repository and four downloaded candidate collections.

| Finding | Count |
|---|---:|
| Pre-generated images | 2,670 |
| Exact duplicate groups | 3,220 |
| Images in exact duplicate groups | 7,276 |
| Perceptual duplicate groups | 5,285 |
| Images in perceptual duplicate groups | 14,983 |
| Cross-source perceptual duplicate groups | 2,462 |
| Images passing the strict full-face quality gate | 3,940 |

`no_face` does not always mean unusable training data: pore and blemish sources contain legitimate facial close-ups. It does mean that the image is not representative of the full-face upload contract and therefore requires review.

The old `SKIN_PROJECT_CLEANED` split is rejected because it contains repeated stock imagery and pre-generated augmentations. It must not be used for evaluation.

## Reproduce

Audit all accepted and candidate sources:

```bash
./venv/bin/python scripts/audit_vision_dataset.py \
  --source existing_conditions=dataset/Conditions \
  --source existing_types=dataset/Types \
  --source existing_clean_train=dataset/SKIN_PROJECT_CLEANED/train \
  --source existing_clean_val=dataset/SKIN_PROJECT_CLEANED/val \
  --source facial_skin_concerns=dataset_sources/extracted/facial_skin_concerns/dataset \
  --source skin_issues_v2="dataset_sources/extracted/skin_issues_v2/Skin v2" \
  --source rajesh_skin=dataset_sources/extracted/rajesh_skin/skin_dataset \
  --source acne04_level0=dataset_sources/extracted/acne04/acne0_1024 \
  --source acne04_level1=dataset_sources/extracted/acne04/acne1_1024 \
  --source acne04_level2=dataset_sources/extracted/acne04/acne2_1024 \
  --source acne04_level3=dataset_sources/extracted/acne04/acne3_1024 \
  --face-model models/face_detection/face_detection_yunet_2023mar.onnx
```

Build the balanced 1,400-image review queue:

```bash
./venv/bin/python scripts/build_vision_review_queue.py data/vision/reports/all_images.csv
```

Review labels locally:

```bash
./venv/bin/streamlit run app/annotate_vision_dataset.py
```

Follow `docs/dataset_annotation_guide.md`. The source label is hidden by default to reduce anchoring.

After all images are reviewed, create final manifests:

```bash
./venv/bin/python scripts/finalize_vision_manifest.py \
  data/vision/manifests/review_queue.csv \
  data/vision/annotations/gold_labels.csv

./venv/bin/python scripts/validate_vision_manifests.py
```

## Split Policy

The review queue uses approximately 55% training, 20% validation, and 25% final test data. Exact and perceptual duplicate groups are assigned atomically, so related images cannot cross splits. Augmentation will happen only at training time.

PASCAL VOC contributes 300 person-free animal, vehicle, and indoor-object images to `ood_test.csv`; these are evaluation-only and never enter concern training.

Source licensing and acceptance decisions are recorded in `data/vision/source_registry.json`. Raw archives, extracted images, generated reports, manifests, and annotations remain local and are ignored by Git.
