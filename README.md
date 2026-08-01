# SkinCare AI

AI-powered skin condition detection and cosmetic product recommendations for the Nepal market.

Upload or pick a skin image and the system detects one of six skin conditions using a deep learning model, then recommends ranked products (cleanser, serum, moisturizer, etc.) from a unified catalog of Nepal retailers.

> **Disclaimer:** This project is for educational/academic purposes only. Detections are not medical diagnoses and product suggestions are cosmetic recommendations only. Always consult a dermatologist for medical concerns.

---

## Features

- **Skin condition classification** with an EfficientNetB0 transfer-learning model (88.6% test accuracy) across 6 classes:
  Acne, Carcinoma, Eczema, Keratosis, Milia, Rosacea.
- **Two-phase training**: feature extraction with a frozen base, then fine-tuning of the top layers.
- **Rule-based recommendation engine** mapping each condition to beneficial/avoid ingredients and product categories, with scoring-based ranking.
- **Product catalog enrichment**: merges, deduplicates (fuzzy matching) and enriches products with ingredient/skin-type/concern data from three Nepal retailers.
- **Medical-condition handling**: Carcinoma predictions surface a strong dermatologist warning and no product suggestions.
- **Streamlit web app** for interactive image upload / sample browsing and results visualization.

---

## How It Works

```
                 ┌──────────────────────────────┐
   skin image → │  EfficientNetB0 classifier   │ → condition + confidence
                 └──────────────────────────────┘
                              │
                              ▼
                 ┌──────────────────────────────┐
                 │  Rule-based engine:         │
                 │  condition → ingredients     │
                 │  → product scoring/ranking   │
                 └──────────────────────────────┘
                              │
                              ▼
                   ranked product recommendations
                   + suggested routine
```

---

## Tech Stack

- **Deep learning**: TensorFlow / Keras (EfficientNetB0)
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
│   ├── model/                    # Model pipeline
│   │   ├── dataset.py            # Load/split/tf.data pipelines + augmentation
│   │   ├── efficientnet.py       # EfficientNetB0 builder + fine-tuning
│   │   ├── train.py              # Two-phase training
│   │   ├── evaluate.py           # Metrics, confusion matrix, plots
│   │   └── augmentations.py      # Data augmentation transforms
│   ├── inference/
│   │   └── predict.py            # SkinAnalyzer: image → condition → recs
│   └── recommendation/
│       ├── condition_rules.py    # Condition → ingredient/category rules
│       ├── scoring.py            # Product scoring
│       └── engine.py             # Recommendation engine
├── models/                       # Trained .keras checkpoints (gitignored)
├── data/
│   ├── raw/                      # Raw scraped data
│   ├── mappings/                 # Ingredient/category/skin-type keyword maps
│   └── enriched/
│       └── unified_products.csv  # Final merged catalog
├── outputs/                      # Evaluation artifacts (gitignored)
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
```

**Dataset note:** The training data (`Skin_Conditions/`) is expected as a folder of class-named subfolders (e.g. `Skin_Conditions/Acne/*.jpg`) at the repo root. It is not stored in this repository.

---

## Usage

### Run the Streamlit web app

```bash
streamlit run app/streamlit_app.py
```

Upload a skin image or pick a sample condition, click **Analyze**, and view the detection with product recommendations and a suggested routine.

### Run the pipeline (CLI)

```bash
# Data enrichment only
python run_pipeline.py --step data

# Train the model
python run_pipeline.py --step train --data-dir Skin_Conditions --model-dir models

# Evaluate + plots
python run_pipeline.py --step eval

# Test inference on an image (or all conditions)
python run_pipeline.py --step inference --image path/to/image.jpg

# Everything end-to-end
python run_pipeline.py --step all
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

- **Architecture**: EfficientNetB0 (ImageNet weights) + global average pooling + dropout + dense head
- **Input**: 224×224 RGB images, EfficientNet preprocessing
- **Training**: Phase A (frozen base, lr=1e-3, 20 epochs) → Phase B (unfreeze top 30 layers, lr=1e-5, 15 epochs), early stopping + ReduceLROnPlateau + best-checkpoint saving
- **Data split**: 70% train / 15% val / 15% test (stratified)
- **Result**: 88.6% test accuracy (see `outputs/` for confusion matrix, per-class accuracy, and metrics)

---

## Disclaimer

This project is intended for academic/research purposes. Skin condition predictions should not be used as a substitute for professional medical diagnosis or treatment. Always seek the advice of a qualified healthcare provider with any questions about a medical condition.
