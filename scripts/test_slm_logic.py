import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommendation.engine import RecommendationEngine  # noqa: E402
from src.slm.recommender import SlmRecommender  # noqa: E402

df = pd.read_csv(os.path.join("data", "enriched", "unified_products.csv"))
engine = RecommendationEngine(df, os.path.join("data", "mappings"))
result = engine.recommend_concerns([
    {"name": "dark_spots", "score": 0.8, "status": "present"}
], skin_type="dry")

rec = SlmRecommender()
out = rec.recommend(result)
print("fallback chosen:", len(out["chosen"]))
print("first:", out["chosen"][0]["name"])

candidates = rec._build_candidates(result, 3)
msg = rec._build_messages(result, candidates, 3)
print("prompt ok:", len(msg) == 2 and "candidate_products" in msg[1]["content"])

mock = (
    '{"chosen": [{"category": "cleanser", "product_id": 9999, '
    '"name": "Fake", "reason": "x"}], "routine": {"am": ["a"], "pm": ["b"]}, '
    '"summary": "s"}'
)
parsed = rec._parse_response(mock, candidates)
guarded = parsed is None or all(c["product_id"] != 9999 for c in parsed["chosen"])
print("guardrail dropped fake product_id:", guarded)
