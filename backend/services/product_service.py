import logging
import math
import os
import sys
from typing import Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.recommendation.condition_rules import ConditionRules

from backend.config import PRODUCTS_PATH, MAPPINGS_DIR

logger = logging.getLogger(__name__)

_products_df = None


def _load_products() -> pd.DataFrame:
    global _products_df
    if _products_df is None:
        _products_df = pd.read_csv(PRODUCTS_PATH)
        for col in ["ingredients", "skin_types", "skin_concerns", "category"]:
            _products_df[col] = _products_df[col].apply(
                lambda x: _parse_list(x) if pd.notna(x) and str(x) != "None" else []
            )
    return _products_df


def _parse_list(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip("[]").strip()
        if not val:
            return []
        return [item.strip().strip("'\"") for item in val.split(",")]
    return []


def get_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skin_type: Optional[str] = None,
    sort_by: str = "rating",
    page: int = 1,
    page_size: int = 20,
) -> Dict:
    df = _load_products()

    if search:
        mask = df["name"].str.contains(search, case=False, na=False) | df["brand"].str.contains(
            search, case=False, na=False
        )
        df = df[mask]

    if category:
        df = df[df["category"].apply(lambda x: category in x if isinstance(x, list) else False)]

    if skin_type:
        df = df[
            df["skin_types"].apply(
                lambda x: skin_type in [str(s).lower() for s in x] if isinstance(x, list) else False
            )
        ]

    if sort_by == "price_low":
        df = df.sort_values("price", ascending=True, na_position="last")
    elif sort_by == "price_high":
        df = df.sort_values("price", ascending=False, na_position="last")
    elif sort_by == "reviews":
        df = df.sort_values("review_count", ascending=False, na_position="last")
    else:
        df = df.sort_values("rating", ascending=False, na_position="last")

    total = len(df)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    page_df = df.iloc[start : start + page_size]

    products = []
    for _, row in page_df.iterrows():
        products.append(_format_product(row))

    return {
        "products": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_product(product_id: int) -> Optional[Dict]:
    df = _load_products()
    match = df[df["product_id"] == product_id]
    if match.empty:
        return None
    return _format_product(match.iloc[0])


def get_categories() -> List[str]:
    df = _load_products()
    cats = set()
    for cat_list in df["category"]:
        if isinstance(cat_list, list):
            cats.update(cat_list)
    return sorted(cats)


def get_conditions() -> List[Dict]:
    conditions = []
    for name in ConditionRules.all_conditions():
        rule = ConditionRules.get_rule(name)
        conditions.append({
            "name": name,
            "title": rule["title"],
            "description": rule["description"],
            "is_medical": rule["is_medical"],
            "recommended_ingredients": rule["recommended_ingredients"],
            "recommended_categories": rule["recommended_categories"],
            "routine_steps": rule["routine_steps"],
        })
    return conditions


def get_condition(name: str) -> Optional[Dict]:
    if name not in ConditionRules.all_conditions():
        return None
    rule = ConditionRules.get_rule(name)
    from backend.config import CONDITION_INFO, CONDITION_COLORS

    extra = CONDITION_INFO.get(name, {})
    return {
        "name": name,
        "title": rule["title"],
        "description": rule["description"],
        "is_medical": rule["is_medical"],
        "color": CONDITION_COLORS.get(name, "#666666"),
        "recommended_ingredients": rule["recommended_ingredients"],
        "recommended_categories": rule["recommended_categories"],
        "avoid_ingredients": rule.get("avoid_ingredients", []),
        "routine_steps": rule["routine_steps"],
        "causes": extra.get("causes", []),
        "tips": extra.get("tips", []),
    }


def get_skin_types() -> List[Dict]:
    from backend.config import SKIN_TYPE_INFO

    types = []
    for name in ConditionRules.all_skin_types():
        rule = ConditionRules.get_skin_type_rule(name)
        extra = SKIN_TYPE_INFO.get(name, {})
        types.append({
            "name": name,
            "title": rule.get("title", name),
            "description": rule.get("description", extra.get("description", "")),
            "recommended_ingredients": rule.get("recommended_ingredients", []),
            "texture_preferences": rule.get("texture_preferences", []),
            "tips": extra.get("tips", []),
        })
    return types


def _format_product(row) -> Dict:
    return {
        "product_id": int(row["product_id"]),
        "name": row["name"],
        "brand": row["brand"],
        "price": float(row["price"]) if pd.notna(row["price"]) else None,
        "discounted_price": float(row["discounted_price"]) if pd.notna(row.get("discounted_price")) else None,
        "rating": float(row["rating"]) if pd.notna(row["rating"]) else None,
        "review_count": int(row["review_count"]) if pd.notna(row["review_count"]) else 0,
        "availability": row.get("availability", "unknown"),
        "image_url": row.get("image_url", ""),
        "source": row.get("source", ""),
        "category": row["category"] if isinstance(row["category"], list) else [],
        "skin_types": row["skin_types"] if isinstance(row["skin_types"], list) else [],
        "skin_concerns": row["skin_concerns"] if isinstance(row["skin_concerns"], list) else [],
        "ingredients": row["ingredients"] if isinstance(row["ingredients"], list) else [],
    }
