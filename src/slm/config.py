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
}
