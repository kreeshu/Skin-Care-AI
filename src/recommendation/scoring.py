import pandas as pd
import numpy as np
from typing import List


def score_product(
    product: pd.Series,
    relevant_ingredients: List[str],
    rating_weight: float = 0.25,
    review_weight: float = 0.20,
    ingredient_weight: float = 0.40,
    availability_weight: float = 0.10,
    discount_weight: float = 0.05,
) -> float:
    """Score a product based on ingredient match, rating, reviews, availability, discount."""
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
    return round(score, 4)


def rank_products(
    products: pd.DataFrame,
    relevant_ingredients: List[str],
    top_n: int = 10,
) -> pd.DataFrame:
    """Rank products by composite score and return top N."""
    if products.empty:
        return products

    scored = products.copy()
    scored["score"] = scored.apply(
        lambda row: score_product(row, relevant_ingredients), axis=1
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
