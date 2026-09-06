import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.inference.predict import SkinAnalyzer
from src.recommendation.condition_rules import ConditionRules

from backend.config import MODEL_PATH, PRODUCTS_PATH, MAPPINGS_DIR

logger = logging.getLogger(__name__)

_analyzer = None
_chat_engine = None
_derma_chat = None


def get_analyzer(use_slm: bool = False) -> SkinAnalyzer:
    global _analyzer
    if _analyzer is None or (_analyzer.slm_recommender is None) != (not use_slm):
        products_df = pd.read_csv(PRODUCTS_PATH)
        _analyzer = SkinAnalyzer(
            MODEL_PATH,
            products_df,
            MAPPINGS_DIR,
            condition_names=ConditionRules.all_conditions(),
            skin_type_names=ConditionRules.all_skin_types(),
            use_slm=use_slm,
        )
        logger.info("SkinAnalyzer loaded (slm=%s)", use_slm)
    return _analyzer


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
