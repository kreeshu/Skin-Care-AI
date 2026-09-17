import json
import re
from typing import Dict, List, Optional

from src.recommendation.engine import RecommendationEngine
from src.slm.engine import SlmEngine

SYSTEM_PROMPT = (
    "You are a friendly, factual skincare assistant working inside a skin-analysis app. "
    "You only recommend cosmetic products and never give medical advice. "
    "RULES:\n"
    "1. Recommend ONLY products listed in CANDIDATE_PRODUCTS. NEVER invent products, "
    "brands, prices or links.\n"
    "2. Choose up to {top_n} products per category and give a short reason "
    "(1-2 sentences) for each that references its matching ingredients.\n"
    "3. Build a personalized AM/PM routine for the user's stated skin type and only concerns marked present. "
    "Scores are cosmetic observations, not diagnoses. Never infer a disease or skin type.\n"
    "4. Reply with valid JSON only, exactly matching this schema:\n"
    '{{"chosen": [{{"category": "...", "product_id": "fng_19052", "name": "...", "reason": "..."}}], '
    '"routine": {{"am": ["..."], "pm": ["..."]}}, "summary": "..."}}'
)


class SlmRecommender:
    """Hybrid step: deterministic candidates in, SLM-reranked explanation out.

    Guardrails enforced in code, not just the prompt: every chosen product_id
    must exist in the candidate shortlist, otherwise it is dropped.
    """

    def __init__(self, engine: SlmEngine = None, config: Dict = None):
        self.engine = engine
        self.config = config or {}

    def recommend(self, engine_result: Dict, top_n: int = 3) -> Dict:
        candidates = self._build_candidates(engine_result, top_n)
        if not candidates:
            return self._fallback_response(engine_result, [])

        messages = self._build_messages(engine_result, candidates, top_n)
        raw = self.engine.generate(messages) if self.engine else None
        parsed = self._parse_response(raw, candidates) if raw else None
        if parsed is None:
            return self._fallback_response(engine_result, candidates)
        return parsed

    def _build_candidates(self, engine_result: Dict, top_n: int) -> List[Dict]:
        allowed_ids = set()
        candidates = []
        limit = self.config.get("max_candidates_per_category", top_n)
        for category, recs in engine_result.get("recommendations", {}).items():
            for rec in recs[:limit]:
                pid = rec["product_id"]
                if pid in allowed_ids:
                    continue
                allowed_ids.add(pid)
                candidates.append({
                    "product_id": pid,
                    "name": rec["name"],
                    "brand": rec["brand"],
                    "category": category,
                    "price": rec["price"],
                    "rating": rec["rating"],
                    "matching_ingredients": rec.get("matching_ingredients", []),
                })
        return candidates

    def _build_messages(self, engine_result: Dict, candidates: List[Dict], top_n: int) -> List[Dict]:
        user_payload = {
            "concerns": engine_result.get("concerns", []),
            "analysis_quality": engine_result.get("analysis_quality"),
            "skin_type": engine_result.get("skin_type"),
            "skin_type_title": engine_result.get("skin_type_title"),
            "candidate_products": candidates,
        }
        return [
            {"role": "system", "content": SYSTEM_PROMPT.format(top_n=top_n)},
            {"role": "user", "content": "Here is my skin analysis:\n" + json.dumps(user_payload, ensure_ascii=False)},
        ]

    def _parse_response(self, raw: str, candidates: List[Dict]) -> Optional[Dict]:
        # IDs are strings (e.g. "fng_19052") but the model may echo them back
        # as numbers — compare normalized, keep the canonical candidate ID.
        allowed = {str(c["product_id"]): c for c in candidates}
        data = self._extract_json(raw)
        if data is None:
            return None
        try:
            chosen = []
            seen = set()
            max_total = self.config.get("max_total_products", 9)
            for item in data.get("chosen", [])[:max_total]:
                candidate = allowed.get(str(item.get("product_id")))
                if candidate is None or candidate["product_id"] in seen:
                    continue
                seen.add(candidate["product_id"])
                chosen.append({
                    "category": candidate["category"],
                    "product_id": candidate["product_id"],
                    "name": candidate["name"],
                    "reason": str(item.get("reason", ""))[:300],
                })
            routine = data.get("routine", {})
            return {
                "chosen": chosen,
                "routine": {
                    "am": self._clean_steps(routine.get("am", [])),
                    "pm": self._clean_steps(routine.get("pm", [])),
                },
                "summary": str(data.get("summary", ""))[:500],
                "generated_by": "slm",
            }
        except (AttributeError, TypeError):
            return None

    @staticmethod
    def _extract_json(raw: str) -> Optional[dict]:
        if not raw:
            return None
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _clean_steps(steps) -> List[str]:
        if not isinstance(steps, list):
            return []
        return [str(step)[:200] for step in steps[:6] if isinstance(step, str) and step.strip()]

    def _fallback_response(self, engine_result: Dict, candidates: List[Dict]) -> Dict:
        chosen = []
        max_total = self.config.get("max_total_products", 9)
        for cat, recs in engine_result.get("recommendations", {}).items():
            for rec in recs[: self.config.get("max_candidates_per_category", 3)]:
                if len(chosen) >= max_total:
                    break
                chosen.append({
                    "category": cat,
                    "product_id": rec["product_id"],
                    "name": rec["name"],
                    "reason": "Matched recommended ingredients: "
                    + ", ".join(rec.get("matching_ingredients", []) or ["none"]),
                })
            if len(chosen) >= max_total:
                break
        return {
            "chosen": chosen,
            "routine": {
                "am": [],
                "pm": [],
            },
            "summary": "Here are the top matched products for your skin.",
            "generated_by": "deterministic_fallback",
        }


if __name__ == "__main__":
    import logging
    import os

    import pandas as pd

    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    df = pd.read_csv(os.path.join(base_dir, "data", "enriched", "unified_products.csv"))
    rec_engine = RecommendationEngine(df, os.path.join(base_dir, "data", "mappings"))
    result = rec_engine.recommend("Acne", skin_type="oily")
    recommender = SlmRecommender()
    response = recommender.recommend(result)
    print(json.dumps(response, indent=2))
