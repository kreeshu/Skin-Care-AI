import json
import csv
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# --- Oriflame ---
with open(DATA_RAW / "oriflame.json", "r", encoding="utf-8") as f:
    oriflame = json.load(f)

oriflame_headers = [
    "id", "name", "slug", "brand_name", "price", "strikePrice",
    "offPercent", "variantType", "ratings", "totalRatings", "ratedBy", "image_url"
]

oriflame_products = oriflame.get("data", {}).get("docs", [])
with open(DATA_RAW / "oriflame.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=oriflame_headers)
    writer.writeheader()
    for p in oriflame_products:
        writer.writerow({
            "id": p.get("_id"),
            "name": p.get("title"),
            "slug": p.get("slug"),
            "brand_name": (p.get("brand") or {}).get("name"),
            "price": p.get("price"),
            "strikePrice": p.get("strikePrice"),
            "offPercent": p.get("offPercent"),
            "variantType": p.get("variantType"),
            "ratings": p.get("ratings"),
            "totalRatings": p.get("totalRatings"),
            "ratedBy": p.get("ratedBy"),
            "image_url": p.get("images", [None])[0] if p.get("images") else "",
        })

print(f"Oriflame: {len(oriflame_products)} products -> oriflame.csv")

# --- Jeevee ---
import re

with open(DATA_RAW / "jevee.json", "r", encoding="utf-8") as f:
    raw = f.read()

# File may be truncated. Find the "data" array and parse complete objects.
try:
    jeevee = json.loads(raw)
    jeevee_products = jeevee.get("data", [])
except json.JSONDecodeError:
    # Extract the data array by finding complete product objects
    # Find where "data" array starts
    data_match = re.search(r'"data"\s*:\s*\[', raw)
    if data_match:
        data_start = data_match.end()
        # Find all complete product objects by tracking braces
        products = []
        i = data_start
        while i < len(raw):
            # Find next opening brace
            brace_pos = raw.find('{', i)
            if brace_pos == -1:
                break
            # Count braces to find matching close
            depth = 0
            j = brace_pos
            while j < len(raw):
                if raw[j] == '{':
                    depth += 1
                elif raw[j] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            obj = json.loads(raw[brace_pos:j+1])
                            if "default_product_id" in obj:
                                products.append(obj)
                        except json.JSONDecodeError:
                            pass
                        i = j + 1
                        break
                j += 1
            else:
                break
        jeevee_products = products
    else:
        jeevee_products = []

jeevee_headers = [
    "id", "name", "sku_code", "brand_name", "price", "discount_percent",
    "avg_rating", "rating_count", "review_count", "sold_out", "has_variants", "image_url"
]

with open(DATA_RAW / "jevee.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=jeevee_headers)
    writer.writeheader()
    for p in jeevee_products:
        review = p.get("review_and_rating", {})
        images = p.get("image", [])
        first_image = ""
        if images and isinstance(images[0], dict):
            first_image = images[0].get("512", "")
        writer.writerow({
            "id": p.get("default_product_id"),
            "name": p.get("label"),
            "sku_code": p.get("sku_code"),
            "brand_name": (p.get("brand") or {}).get("name"),
            "price": p.get("price"),
            "discount_percent": p.get("discount"),
            "avg_rating": review.get("avg_rating"),
            "rating_count": review.get("rating_count"),
            "review_count": review.get("review_count"),
            "sold_out": p.get("sold_out"),
            "has_variants": p.get("has_variants"),
            "image_url": first_image,
        })

print(f"Jeevee: {len(jeevee_products)} products -> jevee.csv")
