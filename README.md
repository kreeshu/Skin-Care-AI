# SkinCare AI

AI-assisted cosmetic skin-concern observations and product recommendations for the Nepal market.

Upload a facial image and the system independently scores five visible cosmetic concerns: blemishes, dark spots, redness, visible pores, and fine lines. A user-provided skin type can refine deterministic catalog recommendations. A backend-hosted local Qwen SLM explains approved products, builds AM/PM routines, and answers grounded skincare questions.

> **Disclaimer:** This project is for educational/academic purposes only. Detections are not medical diagnoses and product suggestions are cosmetic recommendations only. Always consult a dermatologist for medical concerns.

---

## Features

- **Multi-label cosmetic concern model** with an EfficientNetB0 backbone and five independent sigmoid outputs.
- **Explicit uncertainty**: each concern is present, absent, or uncertain using per-label deployment thresholds.
- **Questionnaire skin type**: skin type is user-provided, never inferred from a photo.
- **Skin-type-aware recommendation engine**: deterministic concern-to-ingredient candidate generation with catalog scoring.
- **Hybrid RAG-style SLM layer (optional)**: a small local LLM (Qwen2.5-Instruct) reranks the deterministic shortlist and writes reasons + a personalized AM/PM routine. It can only pick products that already passed the rule engine — it never invents products.
- **Product catalog enrichment**: merges, deduplicates (fuzzy matching) and enriches products with ingredient/skin-type/concern data from three Nepal retailers.
- **Cosmetic-only safety boundary**: the vision model does not diagnose diseases; chat uses symptom red flags only to recommend professional care.
- **Streamlit and Expo apps** for analysis, routines, grounded chat, and catalog browsing.

---

## How It Works

```
                 ┌────────────────────────────────────────────┐
    skin image → │  Multi-label EfficientNetB0                │ → five concern scores
                 │  (independent sigmoid outputs)             │    + uncertainty states
                 └────────────────────────────────────────────┘
                              │
                              ▼
             ┌────────────────────────────────────────────┐
                 │  Rule-based engine (deterministic):        │
                 │  concerns + stated skin type → ingredients  │
                 │  → product scoring/ranking (candidates)     │
                 └────────────────────────────────────────────┘
                              │
                              ▼
                 ┌────────────────────────────────────────────┐
                 │  SLM layer (optional, backend-hosted):     │
                 │  rerank shortlist + reasons + AM/PM routine │
                 └────────────────────────────────────────────┘
                              │
                              ▼
                   ranked product recommendations
                   + suggested routine (+ AI explanation)
```

**Guardrails:** the SLM receives only present cosmetic concerns and the deterministic candidate shortlist. Product IDs, names, and categories are canonicalized against that shortlist; symptom red flags are handled in code rather than inferred from image scores.

---

## Tech Stack

- **Deep learning**: TensorFlow / Keras (EfficientNetB0, multi-label)
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
│   ├── model/                    # Concern model pipeline (EfficientNetB0 multi-label)
│   │   ├── concern_model.py      # ConcernModel + build/load (5x sigmoid)
│   │   ├── concern_dataset.py    # Manifest tf.data pipeline
│   │   ├── train_concern.py      # Two-phase concern training
│   │   ├── evaluate_concern.py   # PR/ROC-AUC, thresholds
│   │   └── augmentations.py      # Data augmentation transforms
│   ├── inference/
│   │   └── predict.py            # SkinAnalyzer: image → concerns → recs (+ SLM)
│   ├── recommendation/
│   │   ├── condition_rules.py    # Concern + skin-type rules
│   │   ├── scoring.py            # Product scoring (ingredient + skin-type match)
│   │   └── engine.py             # Recommendation engine (deterministic candidates)
│   └── slm/
│       ├── config.py             # SLM model/device/generation config
│       ├── engine.py             # HuggingFace loader + generate wrapper
│       └── recommender.py        # Prompt building, JSON parsing, guardrails
├── scripts/
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

**Dataset note:** Vision training manifests live at `data/vision/manifests/` (`train|validation|test.csv`). `dataset/Conditions/` images are kept as a frozen image source referenced by those manifests.

---

## Usage

### Run the Streamlit web app

```bash
streamlit run app/streamlit_app.py
```

Upload a skin image, click **Analyze**, and view the detected cosmetic concerns, product recommendations, and a suggested routine. Tick **AI explanations (local SLM)** in the sidebar to enable on-device explanation (first use downloads the model).

### Train the concern model

```bash
python src/model/train_concern.py --model-dir models/concern_new
# quick sanity run:
python src/model/train_concern.py --quick --model-dir models/concern_quick
```

### Run the pipeline (CLI)

```bash
# Data enrichment only
python run_pipeline.py --step data

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

- **Architecture**: EfficientNetB0 (ImageNet weights) + GAP + dropout + Dense(128, relu) + 5x sigmoid (blemishes, dark_spots, redness, visible_pores, fine_lines)
- **Input**: 224×224 RGB images, EfficientNet preprocessing
- **Training**: `src/model/train_concern.py`, Phase A frozen base (lr=1e-3) → Phase B unfreeze top 30 layers (lr=1e-5), weighted masked BCE, early stopping on `val_macro_pr_auc`
- **Weights**: `models/concern_human_reviewed/skin_concern_pilot.weights.h5` + `skin_concern_pilot.json` + `evaluation.json`

---

## SLM Details

- **Default model**: `Qwen/Qwen2.5-1.5B-Instruct` (CPU bfloat16), fallback `Qwen/Qwen2.5-0.5B-Instruct`
- **Flow**: rule engine shortlist → prompt with candidate facts → JSON output (chosen products + reasons + AM/PM routine)
- **Guardrails**: output JSON validated against the candidate shortlist; invented product IDs are dropped; medical conditions bypass the SLM

---

## Disclaimer

This project is intended for academic/research purposes. Skin condition predictions should not be used as a substitute for professional medical diagnosis or treatment. Always seek the advice of a qualified healthcare provider with any questions about a medical condition.
