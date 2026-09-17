import json
import os
from typing import Dict, List, Set


class ConditionRules:
    """Maps detected skin conditions to recommended ingredients and product categories.

    Note: CONDITION_MAP is kept in alphabetical order to stay aligned with the
    class-name order produced by the dataset loader (sorted folder names).
    """

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
        "Dark Spot": {
            "is_medical": False,
            "title": "Hyperpigmentation / Dark Spots",
            "description": "Your skin shows signs of hyperpigmentation and dark spots.",
            "recommended_ingredients": [
                "vitamin_c", "niacinamide", "kojic_acid", "arbutin",
                "glycolic_acid", "retinol", "azelaic_acid"
            ],
            "recommended_categories": [
                "cleanser", "serum", "moisturizer", "spot_treatment", "sunscreen"
            ],
            "avoid_ingredients": [],
            "routine_steps": [
                "vitamin C serum (AM)", "niacinamide serum",
                "broad-spectrum sunscreen (essential, daily)",
                "gentle chemical exfoliant (1-2x/week)"
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
    }

    CONCERN_MAP = {
        "blemishes": {
            "title": "Visible Blemishes",
            "description": "Visible blemishes and congestion may benefit from gentle, non-comedogenic care.",
            "recommended_ingredients": ["salicylic_acid", "niacinamide", "tea_tree", "zinc", "glycolic_acid"],
            "recommended_categories": ["cleanser", "serum", "moisturizer", "spot_treatment", "toner"],
            "routine_steps": ["gentle cleanser", "niacinamide serum", "lightweight moisturizer", "sunscreen"],
        },
        "dark_spots": {
            "title": "Visible Dark Spots",
            "description": "Visible uneven tone may benefit from brightening ingredients and daily sun protection.",
            "recommended_ingredients": ["vitamin_c", "niacinamide", "kojic_acid", "arbutin", "glycolic_acid", "azelaic_acid"],
            "recommended_categories": ["cleanser", "serum", "moisturizer", "spot_treatment", "sunscreen"],
            "routine_steps": ["vitamin C serum", "moisturizer", "broad-spectrum sunscreen", "gentle exfoliant 1-2x weekly"],
        },
        "redness": {
            "title": "Visible Redness",
            "description": "Visible redness may benefit from a simple, soothing routine that supports the skin barrier.",
            "recommended_ingredients": ["centella_asiatica", "ceramides", "aloe_vera", "niacinamide", "panthenol"],
            "recommended_categories": ["cleanser", "moisturizer", "sunscreen", "serum"],
            "routine_steps": ["gentle cleanser", "soothing serum", "barrier moisturizer", "mineral sunscreen"],
        },
        "visible_pores": {
            "title": "Visible Pores",
            "description": "The appearance of visible pores may benefit from oil-balancing and gentle exfoliating care.",
            "recommended_ingredients": ["niacinamide", "salicylic_acid", "zinc", "glycolic_acid"],
            "recommended_categories": ["cleanser", "toner", "serum", "moisturizer"],
            "routine_steps": ["gentle cleanser", "niacinamide serum", "lightweight moisturizer", "sunscreen"],
        },
        "fine_lines": {
            "title": "Visible Fine Lines",
            "description": "Visible fine lines may benefit from hydration, sun protection, and gradual use of supportive ingredients.",
            "recommended_ingredients": ["retinol", "hyaluronic_acid", "peptides", "ceramides", "vitamin_c"],
            "recommended_categories": ["cleanser", "serum", "moisturizer", "sunscreen"],
            "routine_steps": ["gentle cleanser", "hydrating serum", "moisturizer", "broad-spectrum sunscreen"],
        },
    }

    SKIN_TYPE_MAP = {
        "dry": {
            "title": "Dry Skin",
            "description": "Your skin lacks moisture and may feel tight, rough or flaky.",
            "recommended_ingredients": [
                "hyaluronic_acid", "ceramides", "squalane", "aloe_vera",
                "panthenol", "allantoin", "vitamin_e"
            ],
            "texture_preferences": ["cream", "rich", "nourishing", "hydrating", "deep moisture"],
            "avoid_ingredients": ["alcohol", "sulfates", "fragrance"],
            "routine_steps": [
                "gentle cream cleanser", "hyaluronic acid serum",
                "rich ceramide moisturizer", "night oil or occlusive"
            ],
        },
        "normal": {
            "title": "Normal Skin",
            "description": "Your skin is balanced with few imperfections.",
            "recommended_ingredients": [
                "niacinamide", "hyaluronic_acid", "vitamin_c", "squalane"
            ],
            "texture_preferences": ["balanced", "all skin types", "lightweight", "daily"],
            "avoid_ingredients": [],
            "routine_steps": [
                "gentle cleanser", "vitamin C serum (AM)",
                "lightweight moisturizer", "sunscreen"
            ],
        },
        "oily": {
            "title": "Oily Skin",
            "description": "Your skin produces excess sebum and may look shiny.",
            "recommended_ingredients": [
                "niacinamide", "salicylic_acid", "zinc", "tea_tree",
                "glycolic_acid", "witch_hazel"
            ],
            "texture_preferences": ["gel", "oil-free", "non-comedogenic", "matte", "lightweight", "water-based"],
            "avoid_ingredients": ["coconut oil", "mineral oil", "heavy creams"],
            "routine_steps": [
                "foaming or gel cleanser", "niacinamide serum",
                "oil-free gel moisturizer", "sunscreen (non-comedogenic)"
            ],
        },
        "combination": {
            "title": "Combination Skin",
            "description": "Your skin has both oilier and drier areas.",
            "recommended_ingredients": ["niacinamide", "hyaluronic_acid", "ceramides"],
            "texture_preferences": ["lightweight", "balancing", "gel-cream"],
            "avoid_ingredients": [],
            "routine_steps": ["gentle cleanser", "hydrating serum", "lightweight moisturizer", "sunscreen"],
        },
        "sensitive": {
            "title": "Sensitive Skin",
            "description": "Your skin is easily irritated and benefits from simple, fragrance-free products.",
            "recommended_ingredients": ["ceramides", "panthenol", "allantoin", "centella_asiatica"],
            "texture_preferences": ["gentle", "fragrance-free", "soothing", "barrier"],
            "avoid_ingredients": ["fragrance", "essential oils", "alcohol"],
            "routine_steps": ["gentle cleanser", "soothing serum", "barrier moisturizer", "sunscreen"],
        },
    }

    @classmethod
    def get_rule(cls, condition: str) -> Dict:
        if condition not in cls.CONDITION_MAP:
            raise ValueError(f"Unknown condition: {condition}")
        return cls.CONDITION_MAP[condition]

    @classmethod
    def get_concern_rule(cls, concern: str) -> Dict:
        if concern not in cls.CONCERN_MAP:
            raise ValueError(f"Unknown concern: {concern}")
        return cls.CONCERN_MAP[concern]

    @classmethod
    def get_skin_type_rule(cls, skin_type: str) -> Dict:
        return cls.SKIN_TYPE_MAP.get(skin_type, {})

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
    def all_skin_types(cls) -> List[str]:
        return list(cls.SKIN_TYPE_MAP.keys())

    @classmethod
    def load_ingredient_concern_map(cls, mappings_dir: str) -> Dict:
        path = os.path.join(mappings_dir, "ingredient_concern_map.json")
        with open(path, "r") as f:
            return json.load(f)
