"""Parser eval on hand-labelled brain-dumps (the friend's REAL dumps = the test set that matters).

Gold file: JSONL of {"note": str, "gold": {"tasks": [...]}}  (data/private/test_gold.jsonl)
Usage: python -m eval.parser_eval --gold data/private/test_gold.jsonl --label friend [--backends base-4b,tuned-4b]
"""
import argparse
import json
import os
import statistics
from difflib import SequenceMatcher

from dotenv import load_dotenv

from app.parser import OpenAIParser, TinkerParser

load_dotenv()


def sim(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match(pred, gold, thr=0.5):
    """Greedy title matching -> list of (pred_task, gold_task)."""
    pairs, used = [], set()
    for g in gold:
        best, bi = 0, None
        for i, p in enumerate(pred):
            if i not in used and (s := sim(p["title"], g["title"])) > best:
                best, bi = s, i
        if bi is not None and best >= thr:
            used.add(bi)
            pairs.append((pred[bi], g))
    return pairs


def backends(names, shots):
    sp = os.getenv("TINKER_SAMPLER_PATH")
    table = {
        "base-4b": lambda: TinkerParser("Qwen/Qwen3.5-4B"),
        "base-4b-5shot": lambda: TinkerParser("Qwen/Qwen3.5-4B", shots=shots),
        "base-9b": lambda: TinkerParser("Qwen/Qwen3.5-9B"),
        "tuned-4b": lambda: TinkerParser("Qwen/Qwen3.5-4B", model_path=sp),
        "tuned-4b-local": lambda: OpenAIParser(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), "ollama",
                                               os.getenv("OLLAMA_MODEL", "actually")),
    }
    return {n: table[n]() for n in names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--label", default="friend")
    ap.add_argument("--backends", default="base-4b,base-4b-5shot,base-9b,tuned-4b")
    ap.add_argument("--shots", default="data/synthetic/train.jsonl")
    a = ap.parse_args()
    gold = [json.loads(l) for l in open(a.gold)]
    shots = [(r["note"], r["gold"]) for r in map(json.loads, open(a.shots).readlines()[:5])] if os.path.exists(a.shots) else None
    out = {}
    for name, parser in backends(a.backends.split(","), shots).items():
        tp = fp = fn = 0
        field_hits = {"kind": [0, 0], "guess_min": [0, 0], "deadline": [0, 0], "dreaded": [0, 0], "optional": [0, 0]}
        valid, lat, all_ok = 0, [], 0
        for row in gold:
            r = parser.parse(row["note"])
            lat.append(r.latency_s)
            pred = r.tasks.model_dump()["tasks"] if r.tasks else []
            valid += r.valid_json
            g = row["gold"]["tasks"]
            pairs = match(pred, g)
            tp += len(pairs); fp += len(pred) - len(pairs); fn += len(g) - len(pairs)
            perfect = len(pairs) == len(g) == len(pred)
            for p, gg in pairs:
                for k in field_hits:
                    ok = p.get(k) == gg.get(k)
                    field_hits[k][0] += ok; field_hits[k][1] += 1
                    perfect &= ok
            all_ok += perfect
        prec, rec = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
        out[name] = {
            "valid_json": valid / len(gold), "task_f1": 2 * prec * rec / max(prec + rec, 1e-9),
            "all_correct": all_ok / len(gold), "p50_latency_s": statistics.median(lat),
            **{f"{k}_acc": h[0] / max(h[1], 1) for k, h in field_hits.items()},
        }
        print(name, json.dumps(out[name]))
    json.dump(out, open(f"results/parser_eval_{a.label}.json", "w"), indent=2)
    cols = ["valid_json", "task_f1", "kind_acc", "guess_min_acc", "deadline_acc", "all_correct", "p50_latency_s"]
    lines = ["| Parser | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for n, v in out.items():
        lines.append(f"| {n} | " + " | ".join(f"{v[c]:.2f}" if c == "p50_latency_s" else f"{v[c]:.0%}" for c in cols) + " |")
    open(f"results/parser_eval_{a.label}.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
