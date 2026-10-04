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

## 2026-10-05 00:55 PKT update
- Entire: logged in (github:ArqamWaheed). Tinker/TabPFN/HF/Sentry keys in .env.
- SFT v1 done on 400 synthetic dumps: sampler path in results/sampler_path.txt. Parser eval on data/synthetic/dev_gold.jsonl NOT yet run.
- Friend's REAL stated problems (data/private/friend_words.txt): (1) out of sight = out of mind ("if in front I remember, else gone — person or task"); (2) hyperfocus ("if I addict I addict too much").
  -> Reframe: nothing from a dump disappears (carry-over list keeps tasks + people in front of him); real durations show when one thing will eat the day (hyperfocus).
- No friend task history (tasks.csv) and NO friend reaction. NEVER simulate/invent his reaction or quote. Post uses only his real words above; say honestly the handover hasn't happened yet unless Arqam gets one.
- User asleep until ~8 AM PKT. Do NOT publish the DEV post.
