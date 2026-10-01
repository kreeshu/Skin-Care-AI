import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models", "concern_human_reviewed")
MODEL_PATH = os.path.join(MODEL_DIR, "skin_concern_pilot.weights.h5")
MODEL_METADATA_PATH = os.path.join(MODEL_DIR, "skin_concern_pilot.json")
MODEL_EVALUATION_PATH = os.path.join(MODEL_DIR, "evaluation.json")
FACE_DETECTOR_PATH = os.path.join(BASE_DIR, "models", "face_detection", "face_detection_yunet_2023mar.onnx")
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "enriched", "unified_products.csv")
MAPPINGS_DIR = os.path.join(BASE_DIR, "data", "mappings")

SKIN_TYPE_INFO = {
    "dry": {
        "description": "Dry skin lacks moisture and may feel tight, rough, or flaky. It can be prone to fine lines and irritation.",
        "tips": [
            "Use rich, creamy moisturizers",
            "Apply hyaluronic acid serum on damp skin",
            "Avoid hot water when washing face",
            "Use a humidifier at night",
        ],
    },
    "normal": {
        "description": "Normal skin is well-balanced with few imperfections. It has a smooth texture and even tone.",
        "tips": [
            "Maintain a consistent routine",
            "Use lightweight moisturizers",
            "Always apply sunscreen",
            "Use vitamin C serum for antioxidant protection",
        ],
    },
    "oily": {
        "description": "Oily skin produces excess sebum, leading to a shiny appearance. It is prone to enlarged pores and breakouts.",
        "tips": [
            "Use gel-based or foaming cleansers",
            "Apply niacinamide serum to control oil",
            "Use oil-free, non-comedogenic products",
            "Don't skip moisturizer - use lightweight formulas",
        ],
    },
}
