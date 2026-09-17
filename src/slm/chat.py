"""Free-form dermachat: normal LLM conversation grounded in catalog facts.

Sits next to SlmRecommender (single-turn JSON rerank). Reuses SlmEngine.
Catalog-grounded: the model only sees injected CATALOG_FACTS, and the API
only attaches product cards for IDs already in the catalog.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a friendly skincare assistant inside a skin-analysis app, "
    "talking like a helpful skincare educator. You give cosmetic advice only and "
    "never diagnose, prescribe, or replace a doctor. "
    "RULES:\n"
    "1. Recommend or compare ONLY products listed under CATALOG_FACTS. "
    "NEVER invent product names, brands, prices or links. If asked about a "
    "product not in CATALOG_FACTS, say it is not in our catalog.\n"
    "2. For comparisons, use a short table or bullet list on price, rating, "
    "matching ingredients and skin-type fit.\n"
    "3. Keep replies short (under 150 words) unless asked for a routine.\n"
    "4. Reply in plain text or simple markdown, never JSON."
)

DISCLAIMER = (
    "Cosmetic advice only — not medical advice. "
    "See a dermatologist for medical concerns."
)

MEDICAL_ESCALATION = (
    "This looks like it may need medical attention. "
    "Please consult a dermatologist promptly — "
    "I can only suggest general cosmetic info, not treatment."
)


def truncate_history(history: List[Dict], limit: int = 10) -> List[Dict]:
    """Keep only the last `limit` valid {role, content} turns."""
    clean = [m for m in history or [] if m.get("role") in ("user", "assistant") and m.get("content")]
    return clean[-limit:]


def fact_block(p: Dict) -> str:
    ingredients = ", ".join(p.get("matching_ingredients") or p.get("ingredients") or []) or "n/a"
    price = p.get("discounted_price") or p.get("price")
    return (
        f"- id={p.get('product_id')} | {p.get('name')} ({p.get('brand')}) | "
        f"price={price} | rating={p.get('rating')} | ingredients: {ingredients}"
    )


def match_products(message: str, catalog: List[Dict], limit: int = 3) -> List[Dict]:
    """Substring match of catalog product names in the user message.

    # ponytail: naive substring scan, rapidfuzz fuzzy match if typos matter.
    """
    msg = (message or "").lower()
    if not msg or not catalog:
        return []
    hits = []
    for p in catalog:
        name = str(p.get("name", "")).lower()
        if not name:
            continue
        # match on any distinctive word (>3 chars) to catch "CeraVe cleanser" style refs
        words = [w for w in name.split() if len(w) > 3]
        if name in msg or any(w in msg for w in words):
            hits.append(p)
        if len(hits) >= limit:
            break
    return hits[:limit]


def mentioned_cards(reply: str, allowed: List[Dict]) -> List[Dict]:
    """Return allowed products actually named in the reply (for UI cards)."""
    text = (reply or "").lower()
    cards = []
    for p in allowed:
        name = str(p.get("name", "")).lower()
        if name and (name in text or str(p.get("product_id")) in text):
            cards.append({
                "product_id": str(p.get("product_id")),
                "name": p.get("name"),
                "brand": p.get("brand"),
            })
    return cards


class DermaChat:
    """Context-aware chat over SlmEngine. Engine may be None (fallback mode)."""

    def __init__(self, engine=None, config: Dict = None):
        self.engine = engine
        self.config = config or {}

    def build_messages(
        self,
        message: str,
        history: List[Dict] = None,
        analysis: Dict = None,
        facts: List[Dict] = None,
    ) -> List[Dict]:
        cfg = self.config
        hist = truncate_history(history or [], cfg.get("chat_history_limit", 10))
        lines = []
        if analysis:
            present = [
                item.get("name") for item in analysis.get("concerns", [])
                if item.get("status") == "present"
            ]
            lines.append("User skin context: visible_concerns=%s, stated_skin_type=%s."
                         % (present, analysis.get("skin_type")))
        if facts:
            lines.append("CATALOG_FACTS (only recommend/compare these):")
            lines.extend(fact_block(p) for p in facts)
        elif analysis:
            lines.append("CATALOG_FACTS: none provided; give general ingredient advice, no product names.")
        context_prefix = "\n".join(lines)
        user_content = f"{context_prefix}\n\nUser: {message}" if context_prefix else message
        return [{"role": "system", "content": SYSTEM_PROMPT},
                *hist,
                {"role": "user", "content": user_content}]

    def reply(
        self,
        message: str,
        history: List[Dict] = None,
        analysis: Dict = None,
        facts: List[Dict] = None,
    ) -> Dict:
        facts = facts or []
        is_medical = has_red_flags(message)
        if self.engine is None:
            return self._fallback(message, facts, is_medical)
        messages = self.build_messages(message, history, analysis, facts)
        try:
            text = self.engine.generate(
                messages,
                max_new_tokens=self.config.get("chat_max_new_tokens", 256),
            ).strip()
        except Exception as exc:
            logger.warning("chat generate failed: %s", exc)
            return self._fallback(message, facts, is_medical)
        if not text:
            return self._fallback(message, facts, is_medical)
        cards = mentioned_cards(text, facts)
        if is_medical:
            text = MEDICAL_ESCALATION + "\n\n" + text
        return {"reply": text, "product_cards": cards,
                "disclaimer": DISCLAIMER, "generated_by": "slm_chat"}

    def _fallback(self, message: str, facts: List[Dict], is_medical: bool) -> Dict:
        if is_medical:
            return {"reply": MEDICAL_ESCALATION, "product_cards": [],
                    "disclaimer": DISCLAIMER, "generated_by": "medical_guardrail"}
        if facts:
            top = facts[0]
            reply = ("Based on your skin context, a catalog match is "
                     f"{top.get('name')} ({top.get('brand')}). "
                     "Ask me to compare items or explain ingredients.")
            cards = [{"product_id": str(top.get("product_id")),
                      "name": top.get("name"), "brand": top.get("brand")}]
        else:
            reply = ("I can explain ingredients, routines, or compare products "
                     "from our catalog. Tell me your skin type or paste an analysis result.")
            cards = []
        return {"reply": reply, "product_cards": cards,
                "disclaimer": DISCLAIMER, "generated_by": "deterministic_fallback"}


RED_FLAG_TERMS = (
    "bleeding", "rapidly changing", "rapid change", "severe pain", "severe swelling",
    "infected", "infection", "eye swelling", "can't breathe", "cannot breathe",
)


def has_red_flags(message: str) -> bool:
    text = (message or "").lower()
    return any(term in text for term in RED_FLAG_TERMS)

    # assert-based self-check: `python src/slm/chat.py`
    @staticmethod
    def demo():
        c = DermaChat(config={"chat_history_limit": 2})
        h = [{"role": "user", "content": str(i)} for i in range(5)]
        assert len(truncate_history(h, 2)) == 2
        facts = [{"product_id": "1", "name": "Gentle Foam Cleanser",
                  "brand": "X", "price": 500, "rating": 4.5,
                  "matching_ingredients": ["niacinamide"]}]
        assert match_products("compare Gentle Foam Cleanser vs other?", facts)
        assert not match_products("what is retinol?", facts)
        assert mentioned_cards("Try Gentle Foam Cleanser daily", facts)
        out = c.reply("This is bleeding and rapidly changing")
        assert out["generated_by"] == "medical_guardrail"
        print("chat demo ok")


if __name__ == "__main__":
    DermaChat.demo()
