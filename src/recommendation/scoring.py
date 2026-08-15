import pandas as pd
import numpy as np
from typing import List, Optional


def score_product(
    product: pd.Series,
    relevant_ingredients: List[str],
    rating_weight: float = 0.25,
    review_weight: float = 0.20,
    ingredient_weight: float = 0.40,
    availability_weight: float = 0.10,
    discount_weight: float = 0.05,
    skin_type: Optional[str] = None,
    skin_type_weight: float = 0.0,
    texture_preferences: Optional[List[str]] = None,
) -> float:
    """Score a product based on ingredient match, rating, reviews, availability,
    discount and (optionally) skin-type match. Weights should sum to 1."""
    ingredient_score = _ingredient_match_score(product["ingredients"], relevant_ingredients)
    rating_score = _normalize_rating(product["rating"])
    review_score = _normalize_review_count(product["review_count"])
    availability_score = 1.0 if product["availability"] == "in_stock" else 0.0
    discount_score = _discount_appeal(product["price"], product.get("discounted_price"))

    score = (
        ingredient_weight * ingredient_score
        + rating_weight * rating_score
        + review_weight * review_score
        + availability_weight * availability_score
        + discount_weight * discount_score
    )
    if skin_type_weight > 0:
        skin_type_score = _skin_type_match_score(product, skin_type, texture_preferences)
        score += skin_type_weight * skin_type_score
    return round(score, 4)


def rank_products(
    products: pd.DataFrame,
    relevant_ingredients: List[str],
    top_n: int = 10,
    skin_type: Optional[str] = None,
    texture_preferences: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Rank products by composite score and return top N.

    When skin_type is provided, the composite score also rewards products
    matched to that skin type (ingredient weight reduced accordingly)."""
    if products.empty:
        return products

    use_skin_type = bool(skin_type)
    if use_skin_type:
        weights = dict(
            ingredient_weight=0.35,
            rating_weight=0.20,
            review_weight=0.12,
            availability_weight=0.06,
            discount_weight=0.02,
            skin_type_weight=0.25,
        )
    else:
        weights = dict(
            ingredient_weight=0.40,
            rating_weight=0.25,
            review_weight=0.20,
            availability_weight=0.10,
            discount_weight=0.05,
            skin_type_weight=0.0,
        )

    scored = products.copy()
    scored["score"] = scored.apply(
        lambda row: score_product(
            row,
            relevant_ingredients,
            skin_type=skin_type,
            texture_preferences=texture_preferences,
            **weights,
        ),
        axis=1,
    )
    scored = scored.sort_values("score", ascending=False)
    return scored.head(top_n).reset_index(drop=True)


def _ingredient_match_score(product_ingredients, relevant_ingredients: List[str]) -> float:
    if not product_ingredients or not relevant_ingredients:
        return 0.0
    if isinstance(product_ingredients, str):
        product_ingredients = _parse_list_field(product_ingredients)
    if isinstance(relevant_ingredients, str):
        relevant_ingredients = _parse_list_field(relevant_ingredients)

    product_set = set(product_ingredients)
    relevant_set = set(relevant_ingredients)
    matches = product_set & relevant_set
    if not relevant_set:
        return 0.0
    return min(len(matches) / len(relevant_set), 1.0)


def _normalize_rating(rating) -> float:
    if pd.isna(rating) or rating is None:
        return 0.0
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        return 0.0
    return min(max(rating / 5.0, 0.0), 1.0)


def _normalize_review_count(review_count) -> float:
    if pd.isna(review_count) or review_count is None:
        return 0.0
    try:
        review_count = float(review_count)
    except (ValueError, TypeError):
        return 0.0
    if review_count <= 0:
        return 0.0
    return min(np.log1p(review_count) / np.log1p(1000), 1.0)


def _discount_appeal(price, discounted_price) -> float:
    if pd.isna(price) or price is None or price <= 0:
        return 0.0
    if pd.isna(discounted_price) or discounted_price is None:
        return 0.0
    try:
        price = float(price)
        discounted_price = float(discounted_price)
    except (ValueError, TypeError):
        return 0.0
    if discounted_price >= price:
        return 0.0
    discount_pct = (price - discounted_price) / price
    return min(discount_pct * 2, 1.0)


def _parse_list_field(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip("[]").strip()
        if not val:
            return []
        return [item.strip().strip("'\"") for item in val.split(",")]
    return []


def _skin_type_match_score(product, skin_type: Optional[str], texture_preferences: Optional[List[str]]) -> float:
    if not skin_type:
        return 0.0

    product_skin_types = product.get("skin_types")
    if isinstance(product_skin_types, str):
        product_skin_types = _parse_list_field(product_skin_types)
    if isinstance(product_skin_types, list) and product_skin_types:
        sts = {str(s).strip().lower() for s in product_skin_types}
        if skin_type.lower() in sts:
            return 1.0
        if "all" in sts:
            return 0.7
        if "combination" in sts or "normal" in sts:
            return 0.6

    if texture_preferences:
        name = str(product.get("name", "")).lower()
        description = product.get("description")
        desc = str(description).lower() if description is not None else ""
        text = f"{name} {desc}"
        for pref in texture_preferences:
            if pref.lower() in text:
                return 0.8
    return 0.0
