import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.inference.predict import SkinAnalyzer
from backend.config import (
    MAPPINGS_DIR,
    MODEL_EVALUATION_PATH,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    PRODUCTS_PATH,
)

logger = logging.getLogger(__name__)

_analyzers = {}
_chat_engine = None
_derma_chat = None


def get_analyzer(use_slm: bool = False) -> SkinAnalyzer:
    if use_slm not in _analyzers:
        products_df = pd.read_csv(PRODUCTS_PATH)
        _analyzers[use_slm] = SkinAnalyzer(
            MODEL_PATH,
            products_df,
            MAPPINGS_DIR,
            metadata_path=MODEL_METADATA_PATH,
            evaluation_path=MODEL_EVALUATION_PATH,
            use_slm=use_slm,
        )
        logger.info("SkinAnalyzer loaded (slm=%s)", use_slm)
    return _analyzers[use_slm]


def get_derma_chat():
    """Lazy singleton DermaChat reusing one loaded SlmEngine (None on failure -> fallback)."""
    global _chat_engine, _derma_chat
    if _derma_chat is None:
        from src.slm import DermaChat, SlmEngine, SLM_CONFIG

        try:
            _chat_engine = SlmEngine(SLM_CONFIG).load()
        except Exception as exc:
            logger.warning("SLM unavailable, chat falls back: %s", exc)
            _chat_engine = None
        _derma_chat = DermaChat(_chat_engine, SLM_CONFIG)
    return _derma_chat
