import pandas as pd
import os
import json
from typing import Dict, List, Optional
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.scoring import rank_products, _parse_list_field


class RecommendationEngine:
    """Deterministic concern → ingredients → product scoring → ranked list."""

    def __init__(self, products_df: pd.DataFrame, mappings_dir: str = None):
        self.products = products_df.copy()
        self._prepare_products()
        if mappings_dir:
            self.ingredient_concern_map = ConditionRules.load_ingredient_concern_map(mappings_dir)
        else:
            self.ingredient_concern_map = {}

    def _prepare_products(self):
        for col in ["ingredients", "skin_types", "skin_concerns", "category"]:
            self.products[col] = self.products[col].apply(
                lambda x: _parse_list_field(x) if pd.notna(x) and str(x) != "None" else []
            )

    def recommend_concerns(self, concerns: List[Dict], skin_type: str = None, top_n: int = 5) -> Dict:
        present = [item for item in concerns if item.get("status") == "present"]
        rules = [(item, ConditionRules.get_concern_rule(item["name"])) for item in present]
        ingredients = list(dict.fromkeys(
            ingredient for _, rule in rules for ingredient in rule["recommended_ingredients"]
        ))
        categories = list(dict.fromkeys(
            category for _, rule in rules for category in rule["recommended_categories"]
        ))
        skin_type_rule = ConditionRules.get_skin_type_rule(skin_type) if skin_type else None
        texture_preferences = skin_type_rule.get("texture_preferences") if skin_type_rule else None

        results = {}
        for category in categories:
            category_products = self.products[
                self.products["category"].apply(lambda values: category in values if isinstance(values, list) else False)
            ]
            ranked = rank_products(
                category_products,
                ingredients,
                top_n=top_n,
                skin_type=skin_type,
                texture_preferences=texture_preferences,
            )
            if not ranked.empty:
                results[category] = self._format_recommendations(ranked, ingredients)

        return {
            "title": "Your Cosmetic Skin Overview" if present else "Basic Skin Care",
            "description": (
                "Recommendations are based on visible cosmetic concerns."
                if present else "No concern was confidently identified, so keep your routine simple."
            ),
            "skin_type": skin_type,
            "skin_type_title": skin_type_rule.get("title") if skin_type_rule else None,
            "recommendations": results,
            "routine_suggestion": list(dict.fromkeys(
                step for _, rule in rules for step in rule["routine_steps"]
            )) if present else ["gentle cleanser", "moisturizer", "broad-spectrum sunscreen"],
            "total_products_found": sum(len(items) for items in results.values()),
            "disclaimer": "Cosmetic observations only; this is not a medical diagnosis or medical advice.",
        }

    def _format_recommendations(self, ranked: pd.DataFrame, relevant_ingredients: List[str]) -> List[Dict]:
        recs = []
        for _, row in ranked.iterrows():
            product_ingredients = row["ingredients"] if isinstance(row["ingredients"], list) else []
            matching = [i for i in product_ingredients if i in relevant_ingredients]
            recs.append({
                "product_id": row["product_id"],
                "name": row["name"],
                "brand": row["brand"],
                "price": float(row["price"]) if pd.notna(row["price"]) else None,
                "discounted_price": float(row["discounted_price"]) if pd.notna(row.get("discounted_price")) else None,
                "rating": float(row["rating"]) if pd.notna(row["rating"]) else None,
                "review_count": int(row["review_count"]) if pd.notna(row["review_count"]) else 0,
                "score": float(row["score"]),
                "matching_ingredients": matching,
                "image_url": row["image_url"],
                "source": row["source"],
            })
        return recs

    def get_stats(self) -> Dict:
        return {
            "total_products": len(self.products),
            "categories": self.products["category"].explode().value_counts().to_dict(),
            "sources": self.products["source"].value_counts().to_dict(),
            "products_with_ingredients": int(self.products["ingredients"].apply(lambda x: len(x) > 0).sum()),
            "products_with_skin_types": int(self.products["skin_types"].apply(lambda x: len(x) > 0).sum()),
        }


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    products_path = os.path.join(base_dir, "data", "enriched", "unified_products.csv")
    mappings_dir = os.path.join(base_dir, "data", "mappings")

    df = pd.read_csv(products_path)
    engine = RecommendationEngine(df, mappings_dir)

    print("Product DB stats:")
    stats = engine.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    demo = engine.recommend_concerns([{"name": "blemishes", "status": "present"}], skin_type="oily")
    print(f"  Demo concern query products found: {demo['total_products_found']}")
