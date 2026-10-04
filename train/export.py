"""Download the Tinker LoRA, convert it to a PEFT adapter (HF names), for llama.cpp / vLLM / PEFT.

Usage: python -m train.export --out out/peft_adapter
"""
import argparse
import os

from dotenv import load_dotenv
from tinker_cookbook import weights

load_dotenv()

ap = argparse.ArgumentParser()
ap.add_argument("--sampler-path", default=os.getenv("TINKER_SAMPLER_PATH"))
ap.add_argument("--out", default="out/peft_adapter")
a = ap.parse_args()
raw = weights.download(tinker_path=a.sampler_path, output_dir="out/adapter_raw")
weights.build_lora_adapter(base_model="Qwen/Qwen3.5-4B", adapter_path=raw, output_path=a.out)
print("PEFT adapter ->", a.out)
