import pandas as pd
from rapidfuzz import fuzz, process


class ProductDeduplicator:
    """Cross-source product deduplication using fuzzy name matching."""

    def __init__(self, threshold: int = 80):
        self.threshold = threshold

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"Running deduplication (threshold={self.threshold})...")
        df = df.copy()
        df["_norm_name"] = df["name"].str.lower().str.strip()
        df["_norm_brand"] = df["brand"].str.lower().str.strip()
        df["_key"] = df["_norm_name"] + "|" + df["_norm_brand"]

        duplicates = []
        seen = set()

        groups = df.groupby(["_norm_name", "_norm_brand"])
        for (name, brand), group in groups:
            if len(group) > 1:
                duplicates.append({
                    "indices": group.index.tolist(),
                    "name": name,
                    "brand": brand,
                    "count": len(group)
                })

        for idx, row in df.iterrows():
            if idx in seen:
                continue
            matches = process.extract(
                row["_key"],
                df.loc[df.index != idx, "_key"].tolist(),
                scorer=fuzz.token_sort_ratio,
                limit=5
            )
            for match_key, score, match_idx in matches:
                if score >= self.threshold:
                    original_idx = df.index[df["_key"] == match_key][0]
                    if original_idx not in seen:
                        duplicates.append({
                            "indices": [idx, original_idx],
                            "name": row["_norm_name"],
                            "brand": row["_norm_brand"],
                            "score": score
                        })

        kept = set()
        to_drop = set()
        for dup in duplicates:
            indices = dup["indices"]
            best_idx = max(indices, key=lambda i: self._completeness_score(df.loc[i]))
            for idx in indices:
                if idx != best_idx:
                    to_drop.add(idx)
            kept.add(best_idx)

        df_clean = df.drop(to_drop).drop(columns=["_norm_name", "_norm_brand", "_key"])
        print(f"Removed {len(to_drop)} duplicates. {len(df_clean)} products remaining.")
        return df_clean.reset_index(drop=True)

    def _completeness_score(self, row: pd.Series) -> int:
        score = 0
        for col in ["category", "ingredients", "skin_types", "skin_concerns"]:
            val = row.get(col)
            if val is not None and str(val) not in ("None", "nan", ""):
                score += 1
        rating = row.get("rating")
        if rating is not None and not pd.isna(rating) and float(rating) > 0:
            score += 1
        review_count = row.get("review_count")
        if review_count is not None and not pd.isna(review_count) and float(review_count) > 0:
            score += 1
        return score


if __name__ == "__main__":
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "enriched", "merged_products.csv")
    df = pd.read_csv(path)
    dedup = ProductDeduplicator(threshold=85)
    clean = dedup.deduplicate(df)
    clean.to_csv(path, index=False)
    print(f"Saved deduplicated products to {path}")
