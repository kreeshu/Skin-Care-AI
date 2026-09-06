import os


SLM_CONFIG = {
    "model_name": os.environ.get("SKIN_SLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct"),
    "fallback_model": "Qwen/Qwen2.5-0.5B-Instruct",
    "device": "cpu",
    "dtype": "bfloat16",
    "use_bnb_4bit": False,
    "max_new_tokens": 512,
    "do_sample": False,
    "temperature": 0.3,
    "cache_dir": None,
    "max_candidates_per_category": 3,
    # Free-form dermachat (single-turn generate with injected context + history).
    "chat_max_new_tokens": 256,
    "chat_temperature": 0.5,
    "chat_history_limit": 10,
    "chat_context_top_n": 2,
    "chat_max_fact_products": 3,
}
