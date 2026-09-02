import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "skin_classifier_multitask.weights.h5")
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "enriched", "unified_products.csv")
MAPPINGS_DIR = os.path.join(BASE_DIR, "data", "mappings")
CONDITIONS_DIR = os.path.join(BASE_DIR, "..", "dataset", "Conditions")

CONDITION_COLORS = {
    "Acne": "#FF6B6B",
    "Carcinoma": "#D32F2F",
    "Dark Spot": "#795548",
    "Eczema": "#FF9800",
    "Keratosis": "#9C27B0",
    "Milia": "#2196F3",
    "Rosacea": "#E91E63",
}

CONDITION_INFO = {
    "Acne": {
        "description": "Acne is a skin condition that occurs when hair follicles become clogged with oil and dead skin cells. It causes pimples, blackheads, and whiteheads.",
        "causes": ["Excess oil production", "Clogged pores", "Bacteria", "Hormonal changes"],
        "tips": [
            "Wash face twice daily with a gentle cleanser",
            "Use non-comedogenic moisturizers",
            "Apply sunscreen daily",
            "Avoid touching your face frequently",
        ],
    },
    "Carcinoma": {
        "description": "Possible skin cancer detected. This requires immediate medical attention from a dermatologist.",
        "causes": ["UV exposure", "Genetic factors", "Weakened immune system"],
        "tips": [
            "Consult a dermatologist immediately",
            "Avoid sun exposure",
            "Document the area for your doctor",
        ],
    },
    "Dark Spot": {
        "description": "Hyperpigmentation occurs when melanin is overproduced in certain areas, leading to dark patches on the skin.",
        "causes": ["Sun exposure", "Hormonal changes", "Post-inflammatory hyperpigmentation", "Aging"],
        "tips": [
            "Use vitamin C serum in the morning",
            "Apply SPF 30+ sunscreen daily",
            "Use gentle chemical exfoliants",
            "Be patient - results take 8-12 weeks",
        ],
    },
    "Eczema": {
        "description": "Eczema (atopic dermatitis) causes dry, itchy, and inflamed skin. It is a chronic condition that flares up periodically.",
        "causes": ["Dry skin", "Irritants", "Allergens", "Stress", "Weather changes"],
        "tips": [
            "Moisturize immediately after bathing",
            "Use fragrance-free products",
            "Keep skin cool and avoid sweating",
            "Use a humidifier in dry environments",
        ],
    },
    "Keratosis": {
        "description": "Keratosis refers to rough, scaly patches on the skin caused by excess keratin production.",
        "causes": ["Sun damage", "Genetic factors", "Dry skin"],
        "tips": [
            "Use chemical exfoliants (AHA/BHA)",
            "Moisturize with urea-based creams",
            "Avoid harsh physical scrubs",
            "Apply sunscreen to prevent worsening",
        ],
    },
    "Milia": {
        "description": "Milia are small, white bumps that appear on the skin, often around the eyes and cheeks. They are caused by trapped keratin.",
        "causes": ["Trapped keratin", "Heavy skincare products", "Sun damage", "Skin trauma"],
        "tips": [
            "Use retinol-based products at night",
            "Apply chemical exfoliants regularly",
            "Avoid heavy, pore-clogging creams",
            "Use lightweight, non-comedogenic products",
        ],
    },
    "Rosacea": {
        "description": "Rosacea is a chronic skin condition that causes facial redness, visible blood vessels, and sometimes pimples.",
        "causes": ["Sun exposure", "Hot drinks", "Spicy foods", "Stress", "Exercise"],
        "tips": [
            "Use gentle, cream-based cleansers",
            "Apply mineral-based sunscreen",
            "Avoid alcohol and fragrance",
            "Keep skin cool and calm",
        ],
    },
}

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
