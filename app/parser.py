"""Brain-dump -> TaskList. Two backends behind one interface:

- "openai": any OpenAI-compatible server (Ollama on the host box in prod, or Tinker's
  OpenAI-compatible endpoint with a tinker:// sampler path). Auto-traced by Sentry.
- "tinker": Tinker SamplingClient (used by eval for base models + tuned checkpoints).
"""
import json
import os
import re
import time
from dataclasses import dataclass
from functools import lru_cache

from pydantic import ValidationError

from app.prompts import MODEL_STOP, SYSTEM_PROMPT
from app.schema import TaskList

TINKER_OAI_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1"


@dataclass
class ParseResult:
    tasks: TaskList | None
    raw: str
    latency_s: float
    valid_json: bool
    out_tokens: int | None = None


def extract_json(text: str) -> dict | None:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def to_tasklist(text: str) -> TaskList | None:
    data = extract_json(text)
    if data is None:
        return None
    try:
        return TaskList.model_validate(data)
    except ValidationError:
        return None


def messages(note: str, shots: list[tuple[str, dict]] | None = None) -> list[dict]:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for dump, gold in shots or []:
        msgs += [{"role": "user", "content": dump}, {"role": "assistant", "content": json.dumps(gold)}]
    msgs.append({"role": "user", "content": note})
    return msgs


class OpenAIParser:
    def __init__(self, base_url: str, api_key: str, model: str, shots=None):
        from openai import OpenAI

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model, self.shots = model, shots

    def parse(self, note: str) -> ParseResult:
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages(note, self.shots), temperature=0, max_tokens=900
        )
        raw = resp.choices[0].message.content or ""
        tl = to_tasklist(raw)
        usage = getattr(resp, "usage", None)
        return ParseResult(tl, raw, time.perf_counter() - t0, tl is not None,
                           getattr(usage, "completion_tokens", None))


class TinkerParser:
    def __init__(self, base_model: str, model_path: str | None = None, shots=None):
        import tinker

        self.label = "actually-lora (Qwen3.5-4B)" if model_path else base_model
        sc = tinker.ServiceClient()
        self.client = sc.create_sampling_client(base_model=base_model, model_path=model_path)
        self.tok = self.client.get_tokenizer()
        self.shots = shots

    def parse(self, note: str) -> ParseResult:
        import tinker

        import sentry_sdk

        ids = render_prompt(self.tok, messages(note, self.shots))
        t0 = time.perf_counter()
        with sentry_sdk.start_span(op="gen_ai.chat", name=f"chat {self.label}") as span:
            span.set_data("gen_ai.operation.name", "chat")
            span.set_data("gen_ai.system", "tinker")
            span.set_data("gen_ai.request.model", self.label)
            span.set_data("gen_ai.request.temperature", 0.0)
            res = self.client.sample(
                prompt=tinker.types.ModelInput.from_ints(ids), num_samples=1,
                sampling_params=tinker.types.SamplingParams(max_tokens=900, temperature=0.0, stop=MODEL_STOP),
            ).result()
            toks = res.sequences[0].tokens
            span.set_data("gen_ai.usage.input_tokens", len(ids))
            span.set_data("gen_ai.usage.output_tokens", len(toks))
            span.set_data("gen_ai.usage.total_tokens", len(ids) + len(toks))
        raw = self.tok.decode(toks, skip_special_tokens=True)
        tl = to_tasklist(raw)
        return ParseResult(tl, raw, time.perf_counter() - t0, tl is not None, len(toks))


def render_prompt(tok, msgs: list[dict]) -> list[int]:
    """Chat-template the prompt with thinking disabled (Qwen3.x templates accept enable_thinking)."""
    try:
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok.encode(text, add_special_tokens=False)


@lru_cache(maxsize=1)
def default_parser():
    backend = os.getenv("PARSER_BACKEND", "ollama")
    if backend == "ollama":
        return OpenAIParser(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), "ollama",
                            os.getenv("OLLAMA_MODEL", "actually"))
    if backend == "tinker-oai":
        return OpenAIParser(TINKER_OAI_URL, os.environ["TINKER_API_KEY"], os.environ["TINKER_SAMPLER_PATH"])
    return TinkerParser(os.getenv("BASE_MODEL", "Qwen/Qwen3.5-4B"), os.getenv("TINKER_SAMPLER_PATH"))
