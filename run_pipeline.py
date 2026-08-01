#!/usr/bin/env python3
"""End-to-end pipeline: data enrichment → model training → evaluation → test inference."""

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


def run_training_pipeline(data_dir: str, model_dir: str):
    from src.model.train import train_model
    from src.model.evaluate import plot_training_curves, evaluate_model
    from src.model.dataset import prepare_datasets

    print("\n" + "=" * 60)
    print("MODEL TRAINING PIPELINE")
    print("=" * 60)

    model, history = train_model(data_dir, model_dir)

    output_dir = os.path.join(os.path.dirname(model_dir), "outputs")
    plot_training_curves(history, output_dir)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    train_ds, val_ds, test_ds, class_names = prepare_datasets(data_dir)
    metrics = evaluate_model(model, test_ds, class_names, output_dir)

    return model, history, metrics


def run_test_inference(model_path: str, products_path: str, mappings_dir: str, image_path: str = None):
    from src.inference.predict import SkinAnalyzer
    from src.recommendation.condition_rules import ConditionRules

    print("\n" + "=" * 60)
    print("TEST INFERENCE")
    print("=" * 60)

    products_df = pd.read_csv(products_path)
    analyzer = SkinAnalyzer(model_path, products_df, mappings_dir)
    analyzer.set_class_names(ConditionRules.all_conditions())

    if image_path:
        print(f"\nAnalyzing image: {image_path}")
        result = analyzer.analyze(image_path)
        _print_analysis(result)
    else:
        print("\nNo image provided. Testing all conditions:")
        for condition in ConditionRules.all_conditions():
            result = analyzer.engine.recommend(condition)
            print(f"\n  {condition}: {result['total_products_found']} products")


def _print_analysis(result: dict):
    print(f"\nCondition: {result['detected_condition']}")
    print(f"Confidence: {result.get('model_confidence', 'N/A')}")
    print(f"Medical: {result['is_medical']}")
    print(f"Title: {result['title']}")
    print(f"Description: {result['description']}")
    if result["recommendations"]:
        for cat, recs in result["recommendations"].items():
            print(f"\n  {cat.upper()}:")
            for rec in recs[:3]:
                print(f"    - {rec['name']} ({rec['brand']}) - Rs.{rec['price']} - score={rec['score']:.3f}")
    print(f"\nDisclaimer: {result['disclaimer']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skin Care AI Pipeline")
    parser.add_argument("--step", choices=["data", "train", "eval", "inference", "all"], default="data")
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "Skin_Conditions"))
    parser.add_argument("--model-dir", default=os.path.join(os.path.dirname(__file__), "models"))
    parser.add_argument("--image", default=None, help="Path to skin image for inference test")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_path = os.path.join(base_dir, "data", "enriched", "unified_products.csv")
    mappings_dir = os.path.join(base_dir, "data", "mappings")

    if args.step in ("data", "all"):
        run_data_pipeline()

    if args.step in ("train", "all"):
        run_training_pipeline(args.data_dir, args.model_dir)

    if args.step in ("eval", "all"):
        run_training_pipeline(args.data_dir, args.model_dir)

    if args.step in ("inference", "all"):
        model_path = os.path.join(args.model_dir, "skin_classifier.keras")
        if os.path.exists(model_path):
            run_test_inference(model_path, products_path, mappings_dir, args.image)
        else:
            print(f"Model not found at {model_path}. Run training first.")
