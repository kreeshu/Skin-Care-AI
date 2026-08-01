import pandas as pd
import os
import json
from typing import Dict, List, Optional
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.scoring import rank_products, _parse_list_field


class RecommendationEngine:
    """Core recommendation logic: condition → ingredients → product scoring → ranked list."""

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

    def recommend(self, condition: str, top_n: int = 5) -> Dict:
        rule = ConditionRules.get_rule(condition)
        relevant_ingredients = rule["recommended_ingredients"]
        recommended_categories = rule["recommended_categories"]

        if rule["is_medical"] and condition == "Carcinoma":
            return self._build_medical_response(condition, rule)

        results = {}
        for category in recommended_categories:
            category_products = self.products[
                self.products["category"].apply(lambda x: category in x if isinstance(x, list) else False)
            ]
            ranked = rank_products(category_products, relevant_ingredients, top_n=top_n)
            if not ranked.empty:
                results[category] = self._format_recommendations(ranked, relevant_ingredients)

        response = {
            "detected_condition": condition,
            "is_medical": rule["is_medical"],
            "title": rule["title"],
            "description": rule["description"],
            "recommendations": results,
            "routine_suggestion": rule["routine_steps"],
            "total_products_found": sum(len(v) for v in results.values()),
            "disclaimer": (
                "These are cosmetic recommendations only and do not constitute medical advice. "
                "Please consult a dermatologist for medical concerns."
            ),
        }
        return response

    def _build_medical_response(self, condition: str, rule: Dict) -> Dict:
        return {
            "detected_condition": condition,
            "is_medical": True,
            "title": rule["title"],
            "description": rule["description"],
            "recommendations": {},
            "routine_suggestion": rule["routine_steps"],
            "total_products_found": 0,
            "disclaimer": (
                "This appears to be a medical condition. "
                "Please consult a dermatologist immediately. "
                "Cosmetic products are not a substitute for medical treatment."
            ),
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

    for condition in ConditionRules.all_conditions():
        print(f"\n{'=' * 50}")
        print(f"Testing: {condition}")
        result = engine.recommend(condition)
        print(f"  Medical: {result['is_medical']}")
        print(f"  Products found: {result['total_products_found']}")
        for cat, recs in result["recommendations"].items():
            print(f"  {cat}: {len(recs)} products")
            if recs:
                print(f"    Top: {recs[0]['name']} (score={recs[0]['score']:.3f})")
