#!/usr/bin/env python3
"""End-to-end pipeline: data enrichment → multitask training → evaluation → inference."""

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


def run_training_pipeline(conditions_dir: str, types_dir: str, model_dir: str):
    from src.model.dataset_multitask import prepare_multitask_datasets
    from src.model.evaluate_multitask import evaluate_multitask
    from src.model.multitask import load_multitask_model
    from src.model.train_multitask import train_multitask

    print("\n" + "=" * 60)
    print("MULTITASK MODEL TRAINING (condition + skin type)")
    print("=" * 60)

    datasets = prepare_multitask_datasets(conditions_dir, types_dir, quick=True)
    model = train_multitask(conditions_dir, types_dir, model_dir, quick=False)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    model = load_multitask_model(
        os.path.join(model_dir, "skin_classifier_multitask.weights.h5"),
        num_conditions=datasets["num_conditions"],
        num_skin_types=datasets["num_skin_types"],
    )
    metrics = evaluate_multitask(
        model, datasets["test"], datasets["class_names"],
        os.path.join(model_dir, "..", "outputs"),
    )
    return model, metrics


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
    analyzer = SkinAnalyzer(model_path, products_df, mappings_dir, use_slm=use_slm)

    if image_path:
        print(f"\nAnalyzing image: {image_path}")
        result = analyzer.analyze(image_path)
        _print_analysis(result)
    else:
        print("\nNo image provided. Testing recommendation engine for all conditions:")
        for condition in analyzer.condition_names:
            result = analyzer.engine.recommend(condition, skin_type="normal")
            print(f"\n  {condition}: {result['total_products_found']} products")
        for skin_type in analyzer.skin_type_names:
            result = analyzer.engine.recommend("Acne", skin_type=skin_type)
            print(f"\n  Acne + {skin_type}: {result['total_products_found']} products")


def _print_analysis(result: dict):
    print(f"\nCondition: {result['detected_condition']} "
          f"(conf={result.get('condition_confidence', 0):.3f})")
    if result.get("skin_type"):
        print(f"Skin type: {result['skin_type']} "
              f"(conf={result.get('skin_type_confidence', 0):.3f})")
    print(f"Medical: {result['is_medical']}")
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
    parser.add_argument("--step", choices=["data", "train", "inference", "all"], default="data")
    parser.add_argument("--conditions-dir", default=os.path.join(os.path.dirname(__file__), "..", "dataset", "Conditions"))
    parser.add_argument("--types-dir", default=os.path.join(os.path.dirname(__file__), "..", "dataset", "Types"))
    parser.add_argument("--model-dir", default=os.path.join(os.path.dirname(__file__), "models"))
    parser.add_argument("--image", default=None, help="Path to skin image for inference test")
    parser.add_argument("--use-slm", action="store_true", help="Enable local SLM explanation layer")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_path = os.path.join(base_dir, "data", "enriched", "unified_products.csv")
    mappings_dir = os.path.join(base_dir, "data", "mappings")

    if args.step in ("data", "all"):
        run_data_pipeline()

    if args.step in ("train", "all"):
        run_training_pipeline(args.conditions_dir, args.types_dir, args.model_dir)

    if args.step in ("inference", "all"):
        model_path = os.path.join(args.model_dir, "skin_classifier_multitask.weights.h5")
        if os.path.exists(model_path):
            run_test_inference(model_path, products_path, mappings_dir, args.image, args.use_slm)
        else:
            print(f"Model not found at {model_path}. Run training first.")
