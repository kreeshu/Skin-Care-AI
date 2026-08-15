import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.inference.predict import SkinAnalyzer

MODELS = "models"
products = pd.read_csv(os.path.join("data", "enriched", "unified_products.csv"))
mappings = os.path.join("data", "mappings")

analyzer = SkinAnalyzer(
    os.path.join(MODELS, "skin_classifier_multitask.weights.h5"),
    products,
    mappings,
)
print("multitask:", analyzer.multitask)
print("condition names:", analyzer.condition_names)
print("skin type names:", analyzer.skin_type_names)

sample = os.path.join("..", "dataset", "Conditions", "Acne")
imgs = [f for f in os.listdir(sample) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
if imgs:
    result = analyzer.analyze(os.path.join(sample, imgs[0]))
    print("condition:", result["detected_condition"],
          round(result["condition_confidence"], 3))
    print("skin_type:", result["skin_type"],
          round(result["skin_type_confidence"], 3))
    print("is_medical:", result["is_medical"])
    cats = {k: len(v) for k, v in result["recommendations"].items()}
    print("recommendation categories:", cats)
    print("slm:", result["slm"])
