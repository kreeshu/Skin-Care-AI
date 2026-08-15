import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch

torch.set_num_threads(2)

from src.slm.config import SLM_CONFIG  # noqa: E402
from src.slm.engine import SlmEngine  # noqa: E402

cfg = dict(SLM_CONFIG)
cfg["model_name"] = "Qwen/Qwen2.5-0.5B-Instruct"
cfg["max_new_tokens"] = 64

engine = SlmEngine(cfg).load()
print("loaded:", engine.model_name)

messages = [
    {"role": "system", "content": "Reply with the single word: yes."},
    {"role": "user", "content": "Are you working?"},
]
out = engine.generate(messages)
print("generation:", repr(out))
engine.unload()
