import json
import os
from typing import Dict, List


class ConditionRules:
    """Cosmetic concern + questionnaire skin-type rules for recommendations."""

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
    def get_concern_rule(cls, concern: str) -> Dict:
        if concern not in cls.CONCERN_MAP:
            raise ValueError(f"Unknown concern: {concern}")
        return cls.CONCERN_MAP[concern]

    @classmethod
    def get_skin_type_rule(cls, skin_type: str) -> Dict:
        return cls.SKIN_TYPE_MAP.get(skin_type, {})

    @classmethod
    def all_skin_types(cls) -> List[str]:
        return list(cls.SKIN_TYPE_MAP.keys())

    @classmethod
    def load_ingredient_concern_map(cls, mappings_dir: str) -> Dict:
        path = os.path.join(mappings_dir, "ingredient_concern_map.json")
        with open(path, "r") as f:
            return json.load(f)
