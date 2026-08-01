import os
import pandas as pd
from src.data.merge_sources import merge_sources
from src.data.enricher import NLPEnricher
from src.data.deduplicator import ProductDeduplicator


def run_enrichment_pipeline(raw_dir: str = None, output_dir: str = None) -> pd.DataFrame:
    """End-to-end: merge 3 CSVs, NLP enrich, deduplicate."""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    if raw_dir is None:
        raw_dir = os.path.join(base_dir, "data", "raw")
    if output_dir is None:
        output_dir = os.path.join(base_dir, "data", "enriched")

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("STEP 1: Merging product sources")
    print("=" * 60)
    merged = merge_sources(raw_dir)

    print("\n" + "=" * 60)
    print("STEP 2: NLP enrichment")
    print("=" * 60)
    mappings_dir = os.path.join(base_dir, "data", "mappings")
    enricher = NLPEnricher(mappings_dir)
    enriched = enricher.enrich(merged)

    print("\n" + "=" * 60)
    print("STEP 3: Deduplication")
    print("=" * 60)
    dedup = ProductDeduplicator(threshold=85)
    final = dedup.deduplicate(enriched)

    out_path = os.path.join(output_dir, "unified_products.csv")
    final.to_csv(out_path, index=False)
    print(f"\nSaved unified products to {out_path}")

    _print_summary(final)
    return final


def _print_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"Total products: {len(df)}")
    print(f"\nSource distribution:")
    print(df["source"].value_counts().to_string())
    print(f"\nCategory distribution:")
    print(df["category"].value_counts(dropna=False).to_string())
    print(f"\nAvg confidence score: {df['confidence_score'].mean():.2f}")
    print(f"Products with ingredients: {df['ingredients'].notna().sum()}")
    print(f"Products with skin types: {df['skin_types'].notna().sum()}")
    print(f"Products with skin concerns: {df['skin_concerns'].notna().sum()}")


if __name__ == "__main__":
    run_enrichment_pipeline()
