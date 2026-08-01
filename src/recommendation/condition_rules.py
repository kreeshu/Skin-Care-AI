import json
import os
from typing import Dict, List, Set


class ConditionRules:
    """Maps detected skin conditions to recommended ingredients and product categories."""

    CONDITION_MAP = {
        "Acne": {
            "is_medical": False,
            "title": "Acne-Prone Skin",
            "description": "Your skin is prone to breakouts and clogged pores.",
            "recommended_ingredients": [
                "salicylic_acid", "niacinamide", "tea_tree", "retinol",
                "zinc", "benzoyl_peroxide", "glycolic_acid"
            ],
            "recommended_categories": [
                "cleanser", "serum", "moisturizer", "spot_treatment", "toner"
            ],
            "avoid_ingredients": ["coconut oil", "mineral oil"],
            "routine_steps": [
                "gentle cleanser", "niacinamide serum", "lightweight moisturizer",
                "sunscreen (non-comedogenic)"
            ],
        },
        "Rosacea": {
            "is_medical": False,
            "title": "Rosacea-Prone Skin",
            "description": "Your skin is prone to redness and flushing.",
            "recommended_ingredients": [
                "centella_asiatica", "ceramides", "azelaic_acid", "aloe_vera",
                "niacinamide", "panthenol"
            ],
            "recommended_categories": [
                "cleanser", "moisturizer", "sunscreen", "serum"
            ],
            "avoid_ingredients": ["alcohol", "fragrance", "essential oils", "witch hazel"],
            "routine_steps": [
                "gentle cream cleanser", "soothing serum", "barrier repair moisturizer",
                "mineral sunscreen"
            ],
        },
        "Eczema": {
            "is_medical": True,
            "title": "Eczema-Prone Skin",
            "description": "Your skin shows signs of eczema. Consider consulting a dermatologist.",
            "recommended_ingredients": [
                "ceramides", "hyaluronic_acid", "colloidal_oatmeal", "aloe_vera",
                "panthenol", "allantoin"
            ],
            "recommended_categories": [
                "cleanser", "moisturizer", "serum"
            ],
            "avoid_ingredients": ["fragrance", "sulfates", "alcohol"],
            "routine_steps": [
                "gentle non-foaming cleanser", "hyaluronic acid serum",
                "rich ceramide moisturizer", "occlusive layer at night"
            ],
        },
        "Keratosis": {
            "is_medical": True,
            "title": "Keratosis-Prone Skin",
            "description": "Your skin shows signs of keratosis. Consider consulting a dermatologist.",
            "recommended_ingredients": [
                "glycolic_acid", "lactic_acid", "urea", "salicylic_acid",
                "retinol", "squalane"
            ],
            "recommended_categories": [
                "exfoliant", "moisturizer", "serum"
            ],
            "avoid_ingredients": ["harsh scrubs", "physical exfoliants"],
            "routine_steps": [
                "chemical exfoliant (AHA/BHA)", "hydrating serum",
                "rich moisturizer with urea", "sunscreen"
            ],
        },
        "Milia": {
            "is_medical": False,
            "title": "Milia-Prone Skin",
            "description": "Your skin is prone to small white bumps (milia).",
            "recommended_ingredients": [
                "retinol", "salicylic_acid", "glycolic_acid", "niacinamide"
            ],
            "recommended_categories": [
                "cleanser", "exfoliant", "serum", "moisturizer"
            ],
            "avoid_ingredients": ["heavy creams", "coconut oil", "lanolin"],
            "routine_steps": [
                "gentle cleanser", "retinol serum (at night)",
                "chemical exfoliant (1-2x/week)", "lightweight moisturizer"
            ],
        },
        "Carcinoma": {
            "is_medical": True,
            "title": "Possible Skin Cancer",
            "description": (
                "This may indicate a serious skin condition. "
                "Please consult a dermatologist immediately."
            ),
            "recommended_ingredients": [],
            "recommended_categories": [],
            "avoid_ingredients": [],
            "routine_steps": [
                "Consult a dermatologist immediately"
            ],
        },
    }

    @classmethod
    def get_rule(cls, condition: str) -> Dict:
        return cls.CONDITION_MAP.get(condition, cls.CONDITION_MAP["Carcinoma"])

    @classmethod
    def get_recommended_ingredients(cls, condition: str) -> List[str]:
        return cls.get_rule(condition)["recommended_ingredients"]

    @classmethod
    def get_recommended_categories(cls, condition: str) -> List[str]:
        return cls.get_rule(condition)["recommended_categories"]

    @classmethod
    def is_medical(cls, condition: str) -> bool:
        return cls.get_rule(condition)["is_medical"]

    @classmethod
    def all_conditions(cls) -> List[str]:
        return list(cls.CONDITION_MAP.keys())

    @classmethod
    def load_ingredient_concern_map(cls, mappings_dir: str) -> Dict:
        path = os.path.join(mappings_dir, "ingredient_concern_map.json")
        with open(path, "r") as f:
            return json.load(f)
