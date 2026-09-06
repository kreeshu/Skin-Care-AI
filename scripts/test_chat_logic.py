import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.slm.chat import (  # noqa: E402
    DermaChat,
    match_products,
    mentioned_cards,
    truncate_history,
)

chat = DermaChat(config={"chat_history_limit": 10})

# history truncation keeps last N valid turns
hist = [{"role": "user", "content": str(i)} for i in range(15)]
assert len(truncate_history(hist, 10)) == 10
mixed = hist + [{"role": "system", "content": "x"}, {"role": "user", "content": ""}]
assert all(m["role"] in ("user", "assistant") and m["content"] for m in truncate_history(mixed, 20))

# context injected into prompt
facts = [{"product_id": "7", "name": "Gentle Foam Cleanser", "brand": "X",
          "price": 500, "rating": 4.5, "matching_ingredients": ["niacinamide"]}]
msgs = chat.build_messages("Is this good for me?",
                           [{"role": "user", "content": "hi"}],
                           {"condition": "Acne", "skin_type": "oily"}, facts)
assert msgs[0]["role"] == "system" and msgs[-1]["role"] == "user"
assert "Gentle Foam Cleanser" in msgs[-1]["content"] and "Acne" in msgs[-1]["content"]

# no facts -> no product names promised
msgs = chat.build_messages("what is retinol?", [], {"condition": "Acne", "skin_type": "oily"}, [])
assert "no product names" in msgs[-1]["content"]

# grounding: substring match + card filter
assert match_products("compare Gentle Foam Cleanser vs others?", facts)
assert not match_products("what is retinol?", facts)
assert mentioned_cards("Try Gentle Foam Cleanser daily", facts)
assert not mentioned_cards("Try Magic Cream 3000", facts)

# guardrails without model
out = chat.reply("hi", analysis={"is_medical": True, "condition": "Carcinoma"})
assert out["product_cards"] == [] and "dermatologist" in out["reply"]
out = chat.reply("hi", facts=facts)
assert out["product_cards"] and out["disclaimer"]

print("chat logic ok")
