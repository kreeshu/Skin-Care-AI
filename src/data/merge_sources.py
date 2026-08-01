import pandas as pd
import os


def merge_sources(raw_dir: str) -> pd.DataFrame:
    """Merge products.csv, jevee.csv, oriflame.csv into unified schema."""
    products_df = _load_for_every_ng(os.path.join(raw_dir, "products.csv"))
    jevee_df = _load_jevee(os.path.join(raw_dir, "jevee.csv"))
    oriflame_df = _load_oriflame(os.path.join(raw_dir, "oriflame.csv"))

    merged = pd.concat([products_df, jevee_df, oriflame_df], ignore_index=True)
    print(f"Merged: {len(merged)} products ({len(products_df)} ForEveryNG + "
          f"{len(jevee_df)} Jeevee + {len(oriflame_df)} Oriflame)")
    return merged


def _load_for_every_ng(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["source"] = "for_every_ng"
    df["brand"] = df["name"].apply(_extract_brand_from_name)
    df["product_id"] = "fng_" + df["id"].astype(str)
    df["discounted_price"] = pd.to_numeric(
        df["discountedPrice"].astype(str).str.replace("[^0-9.]", "", regex=True),
        errors="coerce"
    )
    df["availability"] = df["stockQuantity"].apply(
        lambda x: "in_stock" if pd.notna(x) and x > 0 else "out_of_stock"
    )
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return pd.DataFrame({
        "product_id": df["product_id"],
        "name": df["name"],
        "brand": df["brand"],
        "price": df["price"],
        "discounted_price": df["discounted_price"],
        "rating": df["rating"],
        "review_count": df["review_count"],
        "availability": df["availability"],
        "image_url": df["coverImage"],
        "source": df["source"],
        "category": None,
        "skin_types": None,
        "skin_concerns": None,
        "ingredients": None,
    })


def _load_jevee(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["source"] = "jeevee"
    df["product_id"] = "jv_" + df["id"].astype(str)
    df["discounted_price"] = df.apply(
        lambda r: r["price"] * (1 - r["discount_percent"] / 100)
        if pd.notna(r["discount_percent"]) and r["discount_percent"] > 0
        else r["price"],
        axis=1
    )
    df["availability"] = df["sold_out"].apply(
        lambda x: "out_of_stock" if x else "in_stock"
    )
    df["rating"] = pd.to_numeric(df["avg_rating"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return pd.DataFrame({
        "product_id": df["product_id"],
        "name": df["name"],
        "brand": df["brand_name"],
        "price": df["price"],
        "discounted_price": df["discounted_price"],
        "rating": df["rating"],
        "review_count": df["review_count"],
        "availability": df["availability"],
        "image_url": df["image_url"],
        "source": df["source"],
        "category": None,
        "skin_types": None,
        "skin_concerns": None,
        "ingredients": None,
    })


def _load_oriflame(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["source"] = "oriflame"
    df["product_id"] = "ori_" + df["id"].astype(str)
    df["discounted_price"] = df.apply(
        lambda r: r["price"] * (1 - r["offPercent"] / 100)
        if pd.notna(r["offPercent"]) and r["offPercent"] > 0
        else r["price"],
        axis=1
    )
    df["availability"] = "in_stock"
    df["rating"] = pd.to_numeric(df["ratings"], errors="coerce")
    df["review_count"] = pd.to_numeric(df["ratedBy"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return pd.DataFrame({
        "product_id": df["product_id"],
        "name": df["name"],
        "brand": df["brand_name"],
        "price": df["price"],
        "discounted_price": df["discounted_price"],
        "rating": df["rating"],
        "review_count": df["review_count"],
        "availability": df["availability"],
        "image_url": df["image_url"],
        "source": df["source"],
        "category": None,
        "skin_types": None,
        "skin_concerns": None,
        "ingredients": None,
    })


def _extract_brand_from_name(name: str) -> str:
    brand_separators = [" - ", " | ", " By "]
    for sep in brand_separators:
        if sep in name:
            return name.split(sep)[0].strip()
    words = name.split()
    if len(words) >= 2:
        return " ".join(words[:2])
    return words[0] if words else "Unknown"


if __name__ == "__main__":
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    merged = merge_sources(raw_dir)
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "enriched", "merged_products.csv")
    merged.to_csv(out_path, index=False)
    print(f"Saved merged products to {out_path}")
    print(f"\nColumns: {list(merged.columns)}")
    print(f"\nSource distribution:\n{merged['source'].value_counts()}")
