import json
import re
import os
import pandas as pd
from rapidfuzz import fuzz


class NLPEnricher:
    """NLP-based product enrichment pipeline."""

    def __init__(self, mappings_dir: str):
        self.category_kw = self._load_json(mappings_dir, "category_keywords.json")
        self.ingredient_kw = self._load_json(mappings_dir, "ingredient_keywords.json")
        self.skin_type_kw = self._load_json(mappings_dir, "skin_type_keywords.json")
        self.ingredient_concern = self._load_json(mappings_dir, "ingredient_concern_map.json")

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Running NLP enrichment pipeline...")
        df = df.copy()
        df["category"] = df["name"].apply(self.extract_category)
        df["ingredients"] = df["name"].apply(self.extract_ingredients)
        df["skin_types"] = df["name"].apply(self.extract_skin_types)
        df["skin_concerns"] = df["ingredients"].apply(self.infer_concerns)
        df["confidence_score"] = df.apply(self._calc_confidence, axis=1)
        print(f"Enrichment complete. {len(df)} products processed.")
        return df

    def extract_category(self, name: str) -> str:
        name_lower = name.lower()
        best_match = None
        best_score = 0
        for category, keywords in self.category_kw.items():
            for kw in keywords:
                if kw in name_lower:
                    score = len(kw) / len(name_lower)
                    if score > best_score:
                        best_score = score
                        best_match = category
        return best_match

    def extract_ingredients(self, name: str) -> list:
        name_lower = name.lower()
        found = []
        for ingredient, keywords in self.ingredient_kw.items():
            for kw in keywords:
                if kw in name_lower:
                    found.append(ingredient)
                    break
        return found if found else None

    def extract_skin_types(self, name: str) -> list:
        name_lower = name.lower()
        found = []
        for skin_type, keywords in self.skin_type_kw.items():
            for kw in keywords:
                if kw in name_lower:
                    found.append(skin_type)
                    break
        return found if found else None

    def infer_concerns(self, ingredients: list) -> list:
        if not ingredients:
            return None
        found_concerns = set()
        for concern, data in self.ingredient_concern.items():
            if any(ing in data["ingredients"] for ing in ingredients):
                found_concerns.add(concern)
        return list(found_concerns) if found_concerns else None

    def _calc_confidence(self, row: pd.Series) -> float:
        score = 0.0
        if row["category"]:
            score += 0.35
        if row["ingredients"]:
            score += 0.30
        if row["skin_types"]:
            score += 0.20
        if row["skin_concerns"]:
            score += 0.15
        return round(score, 2)

    @staticmethod
    def _load_json(mappings_dir: str, filename: str) -> dict:
        path = os.path.join(mappings_dir, filename)
        with open(path, "r") as f:
            return json.load(f)


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    mappings_dir = os.path.join(base_dir, "data", "mappings")
    merged_path = os.path.join(base_dir, "data", "enriched", "merged_products.csv")

    df = pd.read_csv(merged_path)
    enricher = NLPEnricher(mappings_dir)
    enriched = enricher.enrich(df)
    enriched.to_csv(merged_path, index=False)
    print(f"\nSaved enriched products to {merged_path}")
    print(f"\nCategory distribution:\n{enriched['category'].value_counts(dropna=False)}")
    print(f"\nAvg confidence: {enriched['confidence_score'].mean():.2f}")
