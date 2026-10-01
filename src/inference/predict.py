import json
import logging
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

from src.model.concern_model import CONCERNS, load_concern_model
from src.model.concern_preprocessing import preprocess_concern_image
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.engine import RecommendationEngine

logger = logging.getLogger(__name__)


class SkinAnalyzer:
    """Cosmetic concern inference, recommendations, and optional grounded SLM notes."""

    def __init__(
        self,
        model_path: str,
        products_df=None,
        mappings_dir: str = None,
        metadata_path: str = None,
        evaluation_path: str = None,
        uncertainty_margin: float = 0.05,
        use_slm: bool = False,
        slm_config: Optional[Dict] = None,
        slm_top_n: int = 3,
        face_detector_path: Optional[str] = None,
        face_score_threshold: float = 0.9,
    ):
        metadata = json.loads(Path(metadata_path).read_text()) if metadata_path else {}
        self.labels = tuple(metadata.get("labels", CONCERNS))
        if self.labels != CONCERNS:
            raise ValueError(f"Model labels must be {CONCERNS}, got {self.labels}")
        self.img_size = int(metadata.get("img_size", 224))
        self.model = load_concern_model(model_path, self.img_size)
        output_width = int(self.model(tf.zeros((1, self.img_size, self.img_size, 3))).shape[-1])
        if output_width != len(self.labels):
            raise ValueError("Concern model output does not match metadata labels")

        evaluation = json.loads(Path(evaluation_path).read_text()) if evaluation_path else {}
        metrics = evaluation.get("metrics", {})
        self.thresholds = {
            label: float(metrics.get(label, {}).get("threshold", 0.5)) for label in self.labels
        }
        self.uncertainty_margin = uncertainty_margin
        self.model_version = Path(model_path).stem
        self.engine = RecommendationEngine(products_df, mappings_dir) if products_df is not None else None
        # 0.9 rejected all 300 OOD images in data/vision/reports/face_gate_ood_090.json.
        self.face_detector = (
            cv2.FaceDetectorYN.create(str(face_detector_path), "", (320, 320), face_score_threshold)
            if face_detector_path else None
        )

        self.slm_recommender = None
        self.slm_top_n = slm_top_n
        if use_slm:
            try:
                from src.slm import SLM_CONFIG, SlmEngine, SlmRecommender

                config = slm_config or SLM_CONFIG
                self.slm_recommender = SlmRecommender(SlmEngine(config).load(), config)
            except Exception as exc:
                logger.warning("SLM unavailable, continuing without it: %s", exc)

    def predict(self, image_input) -> Dict:
        scores = np.asarray(self.model.predict(self._preprocess(image_input), verbose=0))[0]
        if scores.shape != (len(self.labels),) or not np.isfinite(scores).all():
            raise ValueError("Concern model returned invalid scores")

        concerns = []
        for label, raw_score in zip(self.labels, scores):
            score = float(np.clip(raw_score, 0.0, 1.0))
            threshold = self.thresholds[label]
            if abs(score - threshold) <= self.uncertainty_margin:
                status = "uncertain"
            else:
                status = "present" if score > threshold else "absent"
            concerns.append({
                "name": label,
                "score": score,
                "threshold": threshold,
                "status": status,
            })
        return {
            "schema_version": 2,
            "model_version": self.model_version,
            "analysis_quality": {"status": "usable", "reasons": []},
            "concerns": concerns,
        }

    def analyze(self, image_input, skin_type: str = None) -> Dict:
        if skin_type and skin_type not in ConditionRules.all_skin_types():
            raise ValueError(f"Unknown skin type: {skin_type}")
        if self.face_detector is not None and not self._has_face(image_input):
            return {
                "schema_version": 2,
                "model_version": self.model_version,
                "analysis_quality": {"status": "rejected", "reasons": ["No face found. Retake a clear, front-facing photo in daylight."]},
                "concerns": [],
                "skin_type": skin_type,
                "skin_type_title": None,
                "title": "No face found",
                "description": "We only analyse clear photos of a face.",
                "recommendations": {},
                "routine_suggestion": [],
                "total_products_found": 0,
                "disclaimer": "Cosmetic observations only; this is not a medical diagnosis or medical advice.",
                "slm": None,
            }
        pred = self.predict(image_input)
        if self.engine is None:
            return {**pred, "skin_type": skin_type, "recommendations": {}, "slm": None}

        result = self.engine.recommend_concerns(pred["concerns"], skin_type=skin_type)
        result.update(pred)
        if self.slm_recommender is not None:
            try:
                result["slm"] = self.slm_recommender.recommend(result, top_n=self.slm_top_n)
            except Exception as exc:
                logger.warning("SLM recommendation failed: %s", exc)
                result["slm"] = None
        else:
            result["slm"] = None
        return result

    def _has_face(self, image_input) -> bool:
        image = self._load_rgb(image_input)
        # YuNet misses faces that fill a large frame; 320px scored an FFHQ face 0.94 vs 0.70 at 1024px.
        scale = min(1.0, 320 / max(image.size))
        if scale < 1:
            image = image.resize((round(image.width * scale), round(image.height * scale)))
        bgr = np.ascontiguousarray(np.asarray(image)[:, :, ::-1])
        self.face_detector.setInputSize((bgr.shape[1], bgr.shape[0]))
        _, faces = self.face_detector.detect(bgr)
        return faces is not None and len(faces) > 0

    @staticmethod
    def _load_rgb(image_input) -> Image.Image:
        if isinstance(image_input, (str, Path)):
            return Image.open(image_input).convert("RGB")
        if isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input).convert("RGB")
        return image_input.convert("RGB")

    def _preprocess(self, image_input) -> np.ndarray:
        image = self._load_rgb(image_input)
        if min(image.size) < 64:
            raise ValueError("Image is too small; use a clear facial photo")
        array = preprocess_concern_image(np.asarray(image), self.img_size).numpy()
        return np.expand_dims(array, axis=0)
