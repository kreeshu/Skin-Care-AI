import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.inference.predict import SkinAnalyzer

MODELS = "models"
products = pd.read_csv(os.path.join("data", "enriched", "unified_products.csv"))
mappings = os.path.join("data", "mappings")

analyzer = SkinAnalyzer(
    os.path.join(MODELS, "concern_v2", "skin_concern_pilot.weights.h5"),
    products,
    mappings,
    metadata_path=os.path.join(MODELS, "concern_v2", "skin_concern_pilot.json"),
    evaluation_path=os.path.join(MODELS, "concern_v2", "evaluation.json"),
)
print("concerns:", analyzer.labels)

sample = os.path.join("dataset", "Conditions", "Acne")
imgs = [f for f in os.listdir(sample) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
if imgs:
    result = analyzer.analyze(os.path.join(sample, imgs[0]))
    print("concerns:", [(item["name"], item["status"], round(item["score"], 3))
                         for item in result["concerns"]])
    cats = {k: len(v) for k, v in result["recommendations"].items()}
    print("recommendation categories:", cats)
    print("slm:", result["slm"])
