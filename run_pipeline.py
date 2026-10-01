#!/usr/bin/env python3
"""End-to-end pipeline: data enrichment → concern inference."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import pandas as pd


def run_data_pipeline():
    from src.data.run_enrichment import run_enrichment_pipeline
    print("\n" + "=" * 60)
    print("DATA ENRICHMENT PIPELINE")
    print("=" * 60)
    return run_enrichment_pipeline()


def run_test_inference(
    model_path: str,
    products_path: str,
    mappings_dir: str,
    image_path: str = None,
    use_slm: bool = False,
):
    from src.inference.predict import SkinAnalyzer

    print("\n" + "=" * 60)
    print("TEST INFERENCE")
    print("=" * 60)

    products_df = pd.read_csv(products_path)
    model_dir = os.path.dirname(model_path)
    analyzer = SkinAnalyzer(
        model_path,
        products_df,
        mappings_dir,
        metadata_path=os.path.join(model_dir, "skin_concern_pilot.json"),
        evaluation_path=os.path.join(model_dir, "evaluation.json"),
        use_slm=use_slm,
    )

    if image_path:
        print(f"\nAnalyzing image: {image_path}")
        result = analyzer.analyze(image_path)
        _print_analysis(result)
    else:
        print("\nProvide --image to run concern inference.")


def _print_analysis(result: dict):
    print("\nCosmetic concerns:")
    for concern in result["concerns"]:
        print(f"  {concern['name']}: {concern['status']} (score={concern['score']:.3f})")
    if result.get("skin_type"):
        print(f"User-provided skin type: {result['skin_type']}")
    print(f"Title: {result['title']}")
    print(f"Description: {result['description']}")
    if result["recommendations"]:
        for cat, recs in result["recommendations"].items():
            print(f"\n  {cat.upper()}:")
            for rec in recs[:3]:
                print(f"    - {rec['name']} ({rec['brand']}) - Rs.{rec['price']} - score={rec['score']:.3f}")
    if result.get("slm"):
        print("\n  SLM EXPLANATION:")
        for item in result["slm"].get("chosen", [])[:3]:
            print(f"    * {item['name']}: {item['reason']}")
        routine = result["slm"].get("routine", {})
        if routine.get("am") or routine.get("pm"):
            print(f"    AM: {'; '.join(routine['am'])}")
            print(f"    PM: {'; '.join(routine['pm'])}")
    print(f"\nDisclaimer: {result['disclaimer']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skin Care AI Pipeline")
    parser.add_argument("--step", choices=["data", "inference", "all"], default="data")
    parser.add_argument("--model-dir", default=os.path.join(os.path.dirname(__file__), "models"))
    parser.add_argument("--image", default=None, help="Path to skin image for inference test")
    parser.add_argument("--use-slm", action="store_true", help="Enable local SLM explanation layer")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_path = os.path.join(base_dir, "data", "enriched", "unified_products.csv")
    mappings_dir = os.path.join(base_dir, "data", "mappings")

    if args.step in ("data", "all"):
        run_data_pipeline()

    if args.step in ("inference", "all"):
        model_path = os.path.join(args.model_dir, "concern_pilot", "skin_concern_pilot.weights.h5")
        if os.path.exists(model_path):
            run_test_inference(model_path, products_path, mappings_dir, args.image, args.use_slm)
        else:
            print(f"Model not found at {model_path}. Run training first.")
