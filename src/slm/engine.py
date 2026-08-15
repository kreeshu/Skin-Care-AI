import logging
from typing import Dict, List

import torch

from src.slm.config import SLM_CONFIG

logger = logging.getLogger(__name__)


class SlmEngine:
    """Loads and runs a small local LLM (HuggingFace transformers).

    Uses Qwen2.5-Instruct by default, with an automatic fallback to a smaller
    model if the primary cannot be loaded (e.g. out of memory on CPU).
    """

    def __init__(self, config: Dict = None):
        self.config = config or SLM_CONFIG
        self.model = None
        self.tokenizer = None
        self.model_name = None

    def load(self):
        cfg = self.config
        for model_name in [cfg["model_name"], cfg["fallback_model"]]:
            try:
                self._load_model(model_name, cfg)
                self.model_name = model_name
                logger.info("SLM loaded: %s", model_name)
                return self
            except Exception as exc:
                logger.warning("Failed to load %s: %s", model_name, exc)
        raise RuntimeError("Could not load any SLM model")

    def _load_model(self, model_name: str, cfg: Dict):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cfg.get("cache_dir"))
        kwargs = {"device_map": cfg.get("device", "cpu")}
        dtype_name = cfg.get("dtype", "float32")
        kwargs["dtype"] = getattr(torch, dtype_name, torch.float32)

        if cfg.get("use_bnb_4bit"):
            try:
                import bitsandbytes  # noqa: F401

                from transformers import BitsAndBytesConfig

                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
            except ImportError:
                logger.warning("bitsandbytes unavailable; loading full precision")

        model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cfg.get("cache_dir"), **kwargs)
        model.eval()
        self.tokenizer = tokenizer
        self.model = model

    def generate(self, messages: List[Dict], max_new_tokens: int = None) -> str:
        if self.model is None:
            raise RuntimeError("SlmEngine not loaded; call load() first")

        cfg = self.config
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(text, return_tensors="pt")
        gen_kwargs = dict(
            max_new_tokens=max_new_tokens or cfg.get("max_new_tokens", 512),
            do_sample=cfg.get("do_sample", False),
        )
        if cfg.get("do_sample", False) and cfg.get("temperature") is not None:
            gen_kwargs["temperature"] = cfg["temperature"]

        with torch.no_grad():
            output = self.model.generate(**inputs, **gen_kwargs)
        prompt_len = inputs["input_ids"].shape[1]
        return self.tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)

    def unload(self):
        self.model = None
        self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
