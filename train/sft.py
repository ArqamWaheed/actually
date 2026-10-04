"""LoRA SFT of Qwen3.5-4B on Tinker. Loss only on the assistant JSON tokens.

Usage: python -m train.sft --data data/synthetic/train.jsonl --epochs 3
Prints the sampler path (tinker://...) to put in .env as TINKER_SAMPLER_PATH.
"""
import argparse
import json
import random

import tinker
from dotenv import load_dotenv

from app.parser import messages, render_prompt

load_dotenv()
BASE = "Qwen/Qwen3.5-4B"


def make_datum(tok, note: str, gold: dict) -> tinker.types.Datum:
    prompt = render_prompt(tok, messages(note))
    completion = tok.encode(json.dumps(gold, ensure_ascii=False) + "<|im_end|>", add_special_tokens=False)
    full = prompt + completion
    weights = [0.0] * (len(prompt) - 1) + [1.0] * len(completion)
    return tinker.types.Datum(
        model_input=tinker.types.ModelInput.from_ints(full[:-1]),
        loss_fn_inputs={"target_tokens": full[1:], "weights": weights},
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic/train.jsonl")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--name", default="actually-v1")
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.data)]
    tc = tinker.ServiceClient().create_lora_training_client(base_model=BASE, rank=a.rank)
    tok = tc.get_tokenizer()
    data = [make_datum(tok, r["note"], r["gold"]) for r in rows]
    steps = a.epochs * ((len(data) + a.batch - 1) // a.batch)
    step, log = 0, open("results/train_log.jsonl", "w")
    for epoch in range(a.epochs):
        random.shuffle(data)
        for i in range(0, len(data), a.batch):
            lr = a.lr * (1 - step / steps)  # linear decay
            fb = tc.forward_backward(data[i:i + a.batch], loss_fn="cross_entropy")
            tc.optim_step(adam_params=tinker.types.AdamParams(learning_rate=lr)).result()
            out = fb.result()
            metrics = getattr(out, "metrics", {}) or {}
            log.write(json.dumps({"step": step, "epoch": epoch, "lr": lr, **metrics}) + "\n")
            log.flush()
            print(step, epoch, {k: round(v, 4) if isinstance(v, float) else v for k, v in metrics.items()})
            step += 1
    path = tc.save_weights_for_sampler(name=a.name).result().path
    print("SAMPLER_PATH", path)
    with open("results/sampler_path.txt", "w") as f:
        f.write(path + "\n")


if __name__ == "__main__":
    main()
