# Actually

**How long will it *actually* take you?** A planning aid built for one friend with ADHD.

My friend described his two problems like this:

> "if infront remember or else gone from brain. person or task"
> "if i addict i addict too much"

Out of sight is out of mind, and when he does lock in, one thing eats the day. So Actually does two things:

1. **Nothing you dump disappears.** Type a messy brain-dump. A small open model, fine-tuned on [Tinker](https://thinkingmachines.ai/tinker/), splits it into tasks. Every task and every person you mention stays on a "Still on your plate" list until you tick it off.
2. **It shows the real cost of each task.** [TabPFN](https://priorlabs.ai), a tabular foundation model, reads your own history of guessed vs real durations and predicts how long each task will take *you*, with a range, the chance you finish it today, and a warning when one task could swallow your free time.

Built for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).

## How it works

```
brain-dump ──▶ Qwen3.5-4B + LoRA (Tinker) ──▶ tasks (JSON) ──▶ TabPFN-3.5 (local) ──▶ plan + carry-over list
                    "parse"                                    "how long, for you?"
```

| Piece | What it does | Where it runs |
|---|---|---|
| Parser | Qwen3.5-4B with a LoRA fine-tuned on Tinker. Brain-dump in, strict JSON task list out. | Tinker sampling (the adapter is downloaded and owned, 291 MB) |
| Forecaster | `TabPFNRegressor` (log-duration, 10/50/90% quantiles) + `TabPFNClassifier` (done the same day?) | Locally, CPU, open weights (TabPFN-3.5 license) |
| App | FastAPI + one HTML page + SQLite | Locally |
| Tracing | Sentry Agent Tracing: `invoke_agent` → `chat` (model, tokens) → `execute_tool tabpfn_forecast`. Prompts are never sent. | Sentry |
| Build provenance | Every Claude Code session captured as Entire checkpoints | Entire |

## Results (all reproducible from `eval/`)

**Parser, 48 held-out brain-dumps (synthetic, labelled by a 397B open teacher):**

| Parser | valid JSON | task F1 | kind | deadline | p50 latency |
|---|---|---|---|---|---|
| Qwen3.5-4B zero-shot | 98% | 95% | 78% | 69% | 3.19 s |
| Qwen3.5-4B 5-shot | 96% | 93% | 82% | 55% | 3.28 s |
| Qwen3.5-9B zero-shot | 100% | 94% | 88% | 61% | 4.53 s |
| **Qwen3.5-4B + LoRA** | **100%** | **97%** | **93%** | **76%** | **3.28 s** |

Training: 400 examples, 3 epochs, LoRA rank 32, 75 steps; loss 335.5 → 43.3.

Caveat: the test set is synthetic and its labels come from the teacher model, so this measures agreement with a much larger model, not accuracy against a human.

**Forecaster latency (the bug Sentry found):** the TabPFN tool span was the slowest step, because `predict()` re-attends over every history row on each request. `fit_mode="fit_with_cache"` computes that once:

| TabPFN fit_mode | fit | predict p50 |
|---|---|---|
| `fit_preprocessors` (default) | 2.50 s | 2.43 s |
| `fit_with_cache` | 3.43 s | **0.27 s** |

**Duration forecast on the demo profile:** see `results/tabpfn_eval_demo.md`. The demo history is **synthetic** (`scripts/make_demo_data.py`), so it only proves the pipeline runs. It is not evidence about any real person.

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env      # TINKER_API_KEY, TABPFN_TOKEN, TINKER_SAMPLER_PATH, optional SENTRY_DSN
python scripts/make_demo_data.py
PARSER_BACKEND=tinker .venv/bin/uvicorn app.main:app --port 8000
```

Reproduce the training and evals:

```bash
python -m train.gen_synthetic --n 450          # teacher-written + teacher-labelled brain-dumps
python -m train.sft --data data/synthetic/sft_train.jsonl --epochs 3
python -m eval.parser_eval --gold data/synthetic/dev_gold.jsonl --label synthetic-dev
python -m eval.tabpfn_eval --csv data/demo/tasks_demo.csv --label demo
python -m eval.bench_forecast
```

Your own history: put a CSV at `data/private/tasks.csv` (git-ignored) with
`date,task,kind,guess_min,actual_min,done_same_day,start_hour,dreaded,left_house` and set `APP_PASSPHRASE`.

## What's not done yet

- **Self-hosted parser.** The LoRA is downloaded, but merging it into Qwen3.5-4B and quantizing to GGUF needs ~25 GB of scratch disk I didn't have this weekend. Until then the parser is served from Tinker, and the app's footer says so.
- **Real history.** The forecast numbers use synthetic data. My friend's own history is next.
- **Shapley explanations.** The "why" chips come from the user's own history (per-kind overrun ratios), not Shapley values yet.

## License

MIT. TabPFN weights are under the [TABPFN-3.5 License](https://huggingface.co/Prior-Labs/tabpfn_3_5/blob/main/LICENSE) (non-commercial). Qwen3.5 is under its own license.
