import io
import logging
import uuid
from typing import Dict, Optional

from PIL import Image

from backend.services import get_analyzer

logger = logging.getLogger(__name__)


def analyze_image(image_bytes: bytes, use_slm: bool = False) -> Dict:
    """Analyze a skin image and return full results."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    analyzer = get_analyzer(use_slm=use_slm)
    result = analyzer.analyze(img)
    result["id"] = str(uuid.uuid4())[:8]
    return result


def analyze_image_from_path(image_path: str, use_slm: bool = False) -> Dict:
    """Analyze a skin image from file path."""
    analyzer = get_analyzer(use_slm=use_slm)
    result = analyzer.analyze(image_path)
    result["id"] = str(uuid.uuid4())[:8]
    return result
