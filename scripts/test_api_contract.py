import io
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app


class ApiContractTest(unittest.TestCase):
    def test_analysis_accepts_questionnaire_skin_type(self):
        image = io.BytesIO()
        Image.new("RGB", (64, 64)).save(image, "JPEG")
        expected = {
            "schema_version": 2,
            "id": "test",
            "model_version": "pilot",
            "analysis_quality": {"status": "usable", "reasons": []},
            "concerns": [],
            "skin_type": "sensitive",
            "recommendations": {},
            "routine_suggestion": [],
            "slm": None,
        }
        with patch("backend.routes.analyze_image", return_value=expected) as analyze:
            response = TestClient(app).post(
                "/api/analyze",
                files={"image": ("face.jpg", image.getvalue(), "image/jpeg")},
                data={"skin_type": "sensitive"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["schema_version"], 2)
        analyze.assert_called_once_with(image.getvalue(), use_slm=False, skin_type="sensitive")

    def test_non_image_is_rejected(self):
        response = TestClient(app).post(
            "/api/analyze", files={"image": ("notes.txt", b"hello", "text/plain")}
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
