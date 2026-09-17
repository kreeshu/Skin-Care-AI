import unittest

import numpy as np
import tensorflow as tf
import pandas as pd

from src.model.concern_model import weighted_masked_bce
from src.recommendation.condition_rules import ConditionRules
from src.recommendation.engine import RecommendationEngine


class ConcernPipelineTest(unittest.TestCase):
    def test_weighted_masked_bce_ignores_unknown_labels(self):
        labels = tf.constant([[1.0, 0.0, -1.0]])
        predictions = tf.constant([[0.8, 0.25, 0.001]])
        weights = tf.constant([[2.0, 1.0, 1000.0]])
        actual = weighted_masked_bce(labels, predictions, weights).numpy()
        expected = (-2.0 * np.log(0.8) - np.log(0.75)) / 3.0
        self.assertAlmostEqual(float(actual), expected, places=5)

    def test_unknown_concern_fails_closed(self):
        with self.assertRaises(ValueError):
            ConditionRules.get_concern_rule("rosacea")

    def test_only_present_concerns_drive_recommendations(self):
        products = pd.DataFrame([{
            "product_id": "1", "name": "Calm Serum", "brand": "Test", "price": 10,
            "discounted_price": None, "rating": 4.5, "review_count": 10,
            "availability": "in_stock", "ingredients": ["niacinamide"],
            "skin_types": ["sensitive"], "skin_concerns": ["redness"],
            "category": ["serum"], "image_url": "", "source": "test",
        }])
        engine = RecommendationEngine(products)
        result = engine.recommend_concerns([
            {"name": "redness", "status": "uncertain", "score": 0.5},
            {"name": "dark_spots", "status": "absent", "score": 0.1},
        ])
        self.assertEqual(result["recommendations"], {})
        self.assertIn("gentle cleanser", result["routine_suggestion"])


if __name__ == "__main__":
    unittest.main()
