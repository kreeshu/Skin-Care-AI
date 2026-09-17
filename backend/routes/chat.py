import asyncio
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services import get_derma_chat
from backend.services.product_service import _load_products, get_product
from src.slm.chat import match_products
from src.slm.config import SLM_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])
_lock = asyncio.Lock()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatContext(BaseModel):
    concerns: List[Dict] = Field(default_factory=list)
    analysis_quality: Optional[Dict] = None
    skin_type: Optional[str] = None
    product_ids: List[str] = Field(default_factory=list)
    recommendations: Optional[Dict] = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: List[ChatMessage] = Field(default_factory=list)
    context: Optional[ChatContext] = None


def _context_products(ctx: Optional[ChatContext], user_message: str) -> List[Dict]:
    """Catalog facts: explicit context ids/recs first, then name matches in message."""
    cfg_top = SLM_CONFIG.get("chat_context_top_n", 2)
    cfg_max = SLM_CONFIG.get("chat_max_fact_products", 3)
    facts: List[Dict] = []
    seen = set()

    def add(pid: Optional[str]):
        if not pid or str(pid) in seen:
            return
        p = get_product(str(pid))
        if p:
            seen.add(str(pid))
            facts.append(p)

    if ctx:
        for pid in (ctx.product_ids or [])[:cfg_max]:
            add(pid)
        if ctx.recommendations:
            for recs in ctx.recommendations.values():
                for rec in (recs or [])[:cfg_top]:
                    add(rec.get("product_id"))
                    if len(facts) >= cfg_max:
                        break
    if len(facts) < cfg_max:
        catalog = _load_products().to_dict("records")
        # normalize rows the way product_service formats them
        for hit in match_products(user_message, [
            {"product_id": str(r.get("product_id")), "name": r.get("name"),
             "brand": r.get("brand")} for r in catalog
        ], limit=cfg_max - len(facts)):
            add(hit["product_id"])
    # re-resolve to full product dicts already added via get_product
    return facts[:cfg_max]


@router.post("")
async def chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        return {"reply": "Please type a question.", "product_cards": [],
                "disclaimer": "Cosmetic advice only."}
    ctx = req.context.model_dump() if req.context else None
    facts = _context_products(req.context, message)
    derma = get_derma_chat()
    history = [m.model_dump() for m in req.history]
    async with _lock:
        result = await asyncio.to_thread(derma.reply, message, history, ctx, facts)
    return result
