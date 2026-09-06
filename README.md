# SkinCare AI

AI-powered skin condition + skin type detection and cosmetic product recommendations for the Nepal market.

Upload or pick a skin image and the system detects one of seven skin conditions **and** the skin type (dry / normal / oily) using a multi-task deep learning model, then recommends ranked products (cleanser, serum, moisturizer, etc.) from a unified catalog of Nepal retailers. A local on-device SLM (small language model) can explain the picks and build a personalized AM/PM routine.

> **Disclaimer:** This project is for educational/academic purposes only. Detections are not medical diagnoses and product suggestions are cosmetic recommendations only. Always consult a dermatologist for medical concerns.

---

## Features

- **Multi-task classification** with a shared EfficientNetB0 backbone and two heads:
  - Condition head (7 classes): Acne, Carcinoma, Dark Spot, Eczema, Keratosis, Milia, Rosacea.
  - Skin-type head (3 classes): dry, normal, oily.
- **Two-phase training**: frozen-base feature extraction, then fine-tuning of the top layers (per-task masked losses + class weights for imbalanced conditions).
- **Skin-type-aware recommendation engine**: deterministic rule-based candidate generation (condition → ingredients → product scoring), with skin-type match boosting in the ranking.
- **Hybrid RAG-style SLM layer (optional)**: a small local LLM (Qwen2.5-Instruct) reranks the deterministic shortlist and writes reasons + a personalized AM/PM routine. It can only pick products that already passed the rule engine — it never invents products.
- **Product catalog enrichment**: merges, deduplicates (fuzzy matching) and enriches products with ingredient/skin-type/concern data from three Nepal retailers.
- **Medical-condition handling**: Carcinoma predictions surface a strong dermatologist warning, bypass the SLM, and return no product suggestions.
- **Streamlit web app** for interactive image upload / sample browsing and results visualization.

---

## How It Works

```
                 ┌────────────────────────────────────────────┐
   skin image → │  Multi-task EfficientNetB0                 │ → condition + skin type
                 │  (shared backbone, two heads)             │    + confidences
                 └────────────────────────────────────────────┘
                              │
                              ▼
             ┌────────────────────────────────────────────┐
                 │  Rule-based engine (deterministic):        │
                 │  condition + skin type → ingredients        │
                 │  → product scoring/ranking (candidates)     │
                 └────────────────────────────────────────────┘
                              │
                              ▼
                 ┌────────────────────────────────────────────┐
                 │  SLM layer (optional, on-device):          │
                 │  rerank shortlist + reasons + AM/PM routine │
                 └────────────────────────────────────────────┘
                              │
                              ▼
                   ranked product recommendations
                   + suggested routine (+ AI explanation)
```

**Guardrails:** the SLM receives only the deterministic candidate shortlist, its output is validated in code (any product not in the shortlist is dropped), and Carcinoma bypasses the SLM entirely.

---

## Tech Stack

- **Deep learning**: TensorFlow / Keras (EfficientNetB0, multi-task)
- **SLM**: PyTorch + HuggingFace transformers (Qwen2.5-1.5B-Instruct, 0.5B fallback), CPU-optimized
- **Data**: pandas, numpy, scikit-learn
- **Matching/dedup**: rapidfuzz
- **Visualization**: matplotlib, seaborn
- **Web UI**: Streamlit

---

## Repository Structure

```
skin-care-ai-v2/
├── app/
│   └── streamlit_app.py          # Streamlit web UI
├── src/
│   ├── data/                     # Product data pipeline
│   │   ├── merge_sources.py      # Merge scraped catalogs
│   │   ├── deduplicator.py       # Fuzzy deduplication
│   │   ├── enricher.py           # Ingredient/skin-type/concern enrichment
│   │   └── run_enrichment.py     # Enrichment pipeline entry point
│   ├── model/                    # Multi-task model pipeline
│   │   ├── dataset_multitask.py  # Load/split/tf.data + mixed-task stream
│   │   ├── multitask.py          # MultiTaskSkinModel + build/save/load
│   │   ├── train_multitask.py    # Two-phase multi-task training
│   │   ├── evaluate_multitask.py # Per-task metrics, confusion matrix, plots
│   │   └── augmentations.py      # Data augmentation transforms
│   ├── inference/
│   │   └── predict.py            # SkinAnalyzer: image → condition + type → recs (+ SLM)
│   ├── recommendation/
│   │   ├── condition_rules.py    # Condition + skin-type rules
│   │   ├── scoring.py            # Product scoring (ingredient + skin-type match)
│   │   └── engine.py             # Recommendation engine (deterministic candidates)
│   └── slm/
│       ├── config.py             # SLM model/device/generation config
│       ├── engine.py             # HuggingFace loader + generate wrapper
│       └── recommender.py        # Prompt building, JSON parsing, guardrails
├── scripts/
│   ├── evaluate_types_kfold.py   # 5-fold CV linear probing (skin types)
│   └── test_slm_logic.py         # SLM logic/guardrail tests (no model needed)
├── models/                       # Trained .weights.h5 checkpoints (gitignored)
├── data/
│   ├── raw/                      # Raw scraped data
│   ├── mappings/                 # Ingredient/category/skin-type keyword maps
│   └── enriched/
│       └── unified_products.csv  # Final merged catalog
├── outputs/                      # Training/eval artifacts (gitignored)
├── fetch_products.py             # ForEveryNG catalog scraper
├── convert_json_to_csv.py        # Jeevee / Oriflame JSON → CSV
├── run_pipeline.py               # End-to-end pipeline CLI
└── requirements.txt
```

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt
# Optional: install CPU-only PyTorch wheels for the SLM layer
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Dataset note:** Training data lives at `dataset/` (inside this repo):
- `dataset/Conditions/<Condition>/*.jpg` — 7 condition folders.
- `dataset/Types/<type>/*.jpg` — 3 skin-type folders (dry / normal / oily).

---

## Usage

### Run the Streamlit web app

```bash
streamlit run app/streamlit_app.py
```

Upload a skin image or pick a sample condition, click **Analyze**, and view the detection (condition + skin type), product recommendations, and a suggested routine. Tick **AI explanations (local SLM)** in the sidebar to enable on-device explanation (first use downloads the model).

### Train the multi-task model

```bash
python src/model/train_multitask.py --model-dir models
# quick sanity run:
python src/model/train_multitask.py --quick --model-dir models
```

### Run the pipeline (CLI)

```bash
# Data enrichment only
python run_pipeline.py --step data

# Train + evaluate
python run_pipeline.py --step train

# Test inference on an image (add --use-slm for AI explanations)
python run_pipeline.py --step inference --image path/to/image.jpg
python run_pipeline.py --step inference --image path/to/image.jpg --use-slm
```

---

## Data Sources

Product catalogs are scraped from three Nepal skincare retailers:

| Source       | Scraper                  | Output |
|--------------|--------------------------|--------|
| ForEveryNG   | `fetch_products.py`      | `products.csv` |
| Jeevee       | `convert_json_to_csv.py` | `jevee.csv` |
| Oriflame     | `convert_json_to_csv.py` | `oriflame.csv` |

These are merged, deduplicated, and enriched into `data/enriched/unified_products.csv`.

---

## Model Details

- **Architecture**: EfficientNetB0 (ImageNet weights) + GAP + dropout + shared dense features, two softmax heads (condition, skin type)
- **Input**: 224×224 RGB images, EfficientNet preprocessing
- **Training**: mixed per-task batch stream (types over-sampled), Phase A (frozen base, lr=1e-3, 20 epochs) → Phase B (unfreeze top 30 layers, lr=1e-5, 15 epochs), early stopping on condition validation accuracy, per-task masked losses + sklearn balanced class weights
- **Data split**: 70% train / 15% val / 15% test (stratified per task)
- **Weights**: `models/skin_classifier_multitask.weights.h5` (weights-only; architecture rebuilt in code)

---

## SLM Details

- **Default model**: `Qwen/Qwen2.5-1.5B-Instruct` (CPU bfloat16), fallback `Qwen/Qwen2.5-0.5B-Instruct`
- **Flow**: rule engine shortlist → prompt with candidate facts → JSON output (chosen products + reasons + AM/PM routine)
- **Guardrails**: output JSON validated against the candidate shortlist; invented product IDs are dropped; medical conditions bypass the SLM

---

## Disclaimer

This project is intended for academic/research purposes. Skin condition predictions should not be used as a substitute for professional medical diagnosis or treatment. Always seek the advice of a qualified healthcare provider with any questions about a medical condition.
