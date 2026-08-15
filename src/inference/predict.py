import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf
from PIL import Image

from src.model.multitask import load_multitask_model
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.engine import RecommendationEngine

IMG_SIZE = 224


class SkinAnalyzer:
    """End-to-end: image → condition + skin type → recommendations (+ SLM)."""

    def __init__(
        self,
        model_path: str,
        products_df=None,
        mappings_dir: str = None,
        num_conditions: int = 7,
        num_skin_types: int = 3,
        img_size: int = IMG_SIZE,
        condition_names: Optional[List[str]] = None,
        skin_type_names: Optional[List[str]] = None,
        use_slm: bool = False,
        slm_config: Optional[Dict] = None,
        slm_top_n: int = 3,
    ):
        if model_path.endswith(".weights.h5"):
            self.model = load_multitask_model(
                model_path, num_conditions, num_skin_types, img_size
            )
            self.multitask = True
        else:
            self.model = tf.keras.models.load_model(model_path)
            self.multitask = False

        self.condition_names = condition_names or ConditionRules.all_conditions()
        self.skin_type_names = skin_type_names or ConditionRules.all_skin_types()
        self.img_size = img_size

        if products_df is not None and mappings_dir is not None:
            self.engine = RecommendationEngine(products_df, mappings_dir)
        else:
            self.engine = None

        self.slm_recommender = None
        self.slm_top_n = slm_top_n
        if use_slm:
            from src.slm import SlmEngine, SlmRecommender

            self.slm_recommender = SlmRecommender(SlmEngine(slm_config).load())

    # ------------------------------------------------------------------ #
    # Predictions
    # ------------------------------------------------------------------ #
    def predict(self, image_input) -> Dict:
        """Predict condition and skin type from image path, array, or PIL image."""
        img_batch = self._preprocess(image_input)
        condition, cond_conf = self._predict_condition(img_batch)
        skin_type, type_conf = self._predict_skin_type(img_batch)
        return {
            "condition": condition,
            "condition_confidence": cond_conf,
            "skin_type": skin_type,
            "skin_type_confidence": type_conf,
            "is_medical": ConditionRules.is_medical(condition),
        }

    def _predict_condition(self, img_batch: np.ndarray) -> Tuple[str, float]:
        if self.multitask:
            cond_probs, _ = self.model.predict_heads(tf.constant(img_batch))
            cond_probs = cond_probs.numpy()[0]
        else:
            out = self.model.predict(img_batch, verbose=0)
            cond_probs = np.asarray(out[0]) if isinstance(out, list) else np.asarray(out)
        idx = int(np.argmax(cond_probs))
        return self.condition_names[idx], float(cond_probs[idx])

    def _predict_skin_type(self, img_batch: np.ndarray) -> Tuple[str, float]:
        if not self.multitask:
            return None, 0.0
        _, type_probs = self.model.predict_heads(tf.constant(img_batch))
        type_probs = type_probs.numpy()[0]
        idx = int(np.argmax(type_probs))
        return self.skin_type_names[idx], float(type_probs[idx])

    # ------------------------------------------------------------------ #
    # Full analysis
    # ------------------------------------------------------------------ #
    def analyze(self, image_input) -> Dict:
        pred = self.predict(image_input)
        condition = pred["condition"]
        skin_type = pred["skin_type"]

        if self.engine is None:
            return {**pred, "recommendations": None, "message": "Recommendation engine not loaded."}

        recs = self.engine.recommend(condition, skin_type=skin_type)
        recs["condition_confidence"] = pred["condition_confidence"]
        recs["skin_type_confidence"] = pred["skin_type_confidence"]

        if self.slm_recommender is not None and not pred["is_medical"]:
            try:
                recs["slm"] = self.slm_recommender.recommend(recs, top_n=self.slm_top_n)
            except Exception:
                recs["slm"] = None
        else:
            recs["slm"] = None

        return recs

    # ------------------------------------------------------------------ #
    # Preprocessing
    # ------------------------------------------------------------------ #
    def _preprocess(self, image_input) -> np.ndarray:
        if isinstance(image_input, str):
            img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            img = Image.fromarray(image_input).convert("RGB")
        else:
            img = image_input.convert("RGB")

        img = img.resize((self.img_size, self.img_size))
        img_array = tf.keras.applications.efficientnet.preprocess_input(np.array(img))
        return np.expand_dims(img_array, axis=0)
