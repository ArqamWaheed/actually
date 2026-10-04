"""Synthetic training data for the parser, made by a large OPEN teacher model on Tinker.

1. The teacher writes brain-dumps in the friend's style (style seeds = a few of his real dumps,
   never the held-out test dumps).
2. The teacher labels each dump with the exact schema in app/prompts.py.
Output: data/synthetic/train.jsonl  ({"note": str, "gold": {"tasks": [...]}})

Usage: python -m train.gen_synthetic --n 400 --seeds data/private/style_seeds.txt
"""
import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import tinker
from dotenv import load_dotenv

from app.parser import TinkerParser, render_prompt

load_dotenv()
TEACHER = "Qwen/Qwen3.5-397B-A17B"   # labels (quality matters)
WRITER = "Qwen/Qwen3.6-35B-A3B"      # writes dumps (cheap, varied)

SCENARIOS = [
    "a uni student the night before a deadline", "a lazy sunday with chores piling up",
    "a monday with classes, gym and family calls", "a day full of admin they keep avoiding",
    "a freelance + study day", "exam week panic", "after a bad night's sleep", "a day with errands across town",
    "a weekend with a wedding to attend", "a guilt-heavy day after skipping yesterday's plans",
]
WRITE_PROMPT = """Write ONE realistic, messy brain-dump (a to-do rant) by a young person in Pakistan with ADHD, for: {scenario}.
Style rules: write like these real examples (casual, run-on, lowercase, some Urdu/English mix, "maybe", "ugh", tangents):
{seeds}
Mention {k} distinct tasks. Sometimes state a duration ("should take 20 min"), sometimes not. Output only the brain-dump text."""


def write_dump(sampler, tok, seeds: list[str]) -> str:
    seed_txt = "\n---\n".join(random.sample(seeds, min(3, len(seeds))))
    msgs = [{"role": "user", "content": WRITE_PROMPT.format(scenario=random.choice(SCENARIOS), seeds=seed_txt,
                                                           k=random.randint(2, 8))}]
    res = sampler.sample(prompt=tinker.types.ModelInput.from_ints(render_prompt(tok, msgs)), num_samples=1,
                         sampling_params=tinker.types.SamplingParams(max_tokens=400, temperature=0.9)).result()
    return tok.decode(res.sequences[0].tokens, skip_special_tokens=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seeds", default="data/synthetic/style_seeds_generic.txt")
    ap.add_argument("--out", default="data/synthetic/train.jsonl")
    a = ap.parse_args()
    seeds = [s.strip() for s in Path(a.seeds).read_text().split("---") if s.strip()]
    sampler = tinker.ServiceClient().create_sampling_client(base_model=WRITER)
    tok = sampler.get_tokenizer()
    labeler = TinkerParser(TEACHER)

    def one(_):
        dump = write_dump(sampler, tok, seeds)
        r = labeler.parse(dump)
        return {"note": dump, "gold": r.tasks.model_dump()} if r.tasks and r.tasks.tasks else None

    with ThreadPoolExecutor(16) as ex:
        rows = [r for r in ex.map(one, range(a.n)) if r]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)}/{a.n} -> {a.out}")


if __name__ == "__main__":
    main()
