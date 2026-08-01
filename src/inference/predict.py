import tensorflow as tf
import numpy as np
import os
from PIL import Image
from typing import Dict, Tuple
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.engine import RecommendationEngine


IMG_SIZE = 224


class SkinAnalyzer:
    """End-to-end: image → condition prediction → product recommendations."""

    def __init__(
        self,
        model_path: str,
        products_df=None,
        mappings_dir: str = None,
    ):
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = None

        if products_df is not None and mappings_dir is not None:
            self.engine = RecommendationEngine(products_df, mappings_dir)
        else:
            self.engine = None

    def predict_condition(self, image_input) -> Tuple[str, float, bool]:
        """Predict skin condition from image path, numpy array, or PIL Image."""
        img = self._preprocess(image_input)
        predictions = self.model.predict(img, verbose=0)
        pred_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][pred_idx])
        condition = self.class_names[pred_idx] if self.class_names else str(pred_idx)
        is_medical = ConditionRules.is_medical(condition)
        return condition, confidence, is_medical

    def analyze(self, image_input) -> Dict:
        """Full analysis: predict condition + get recommendations."""
        condition, confidence, is_medical = self.predict_condition(image_input)

        if self.engine is None:
            return {
                "condition": condition,
                "confidence": confidence,
                "is_medical": is_medical,
                "recommendations": None,
                "message": "Recommendation engine not loaded.",
            }

        recs = self.engine.recommend(condition)
        recs["model_confidence"] = confidence
        return recs

    def _preprocess(self, image_input) -> np.ndarray:
        if isinstance(image_input, str):
            img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            img = Image.fromarray(image_input).convert("RGB")
        else:
            img = image_input.convert("RGB")

        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = tf.keras.applications.efficientnet.preprocess_input(np.array(img))
        return np.expand_dims(img_array, axis=0)

    def set_class_names(self, class_names: list):
        self.class_names = class_names
