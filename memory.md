# memory.md — Actually brain
> Read this first every task. Update it last. Keep it terse.

## What this is
"Actually": time-blindness helper for a friend with ADHD. Brain-dump text -> Tinker-fine-tuned Qwen3.5-4B parses into tasks -> TabPFN (local) predicts how long each task ACTUALLY takes him (+range, +P(done today), +Shapley why) -> plan that fits his free time.
Hackathon: DEV Hacktoberfest Weekend "Build for a Friend". Deadline 2026-10-05 06:59 UTC (11:59 AM PKT). Publish target 10:30 AM PKT.
Categories: Tinker, TabPFN, DigitalOcean, Sentry Agent Tracing, Entire (+Temporal/Copilot stretch).
Strategy + full plan: ~/theodinproject/repos/research/outputs/hackathon-research/hacktoberfest-weekend-2026-10/03-PLAYBOOK-actually.md

## Stack
Python 3.12 (uv), FastAPI, SQLite, tinker SDK, tabpfn (local, CPU torch), openai client, sentry-sdk. Serving: Ollama/llama.cpp GGUF on a DO Droplet. Single HTML page UI.

## Status snapshot
- Phase: scaffold done (app/, train/, eval/, demo data). Blocked on keys.
- Next: keys (Tinker promo needs MyMLH phone+GitHub; TabPFN license at ux.priorlabs.ai), then gen_synthetic -> sft -> eval. Host = HF Spaces free (user: $0 budget, no DO).

## Key decisions (why)
- Qwen3.5-4B (Tinker) — fits CPU droplet; tune closes gap to 9B.
- Local TabPFN-3.5 not API — friend's health data stays on box.
- Model export/merge happens ON THE DROPLET — local disk has ~2.6 GB free.
- NEVER fabricate friend data, quotes, or metrics. Real friend data lives in data/private/ (git-ignored).

## Open questions / TODO
- Friend data (brain-dumps + task sheet) — pending from user.

## File map
- app/ — FastAPI app (parse, forecast, plan, UI)
- train/ — synthetic data gen, Tinker SFT, export
- eval/ — parser eval + TabPFN CV eval -> results/
- deploy/ — droplet setup, Caddy, systemd, Modelfile
