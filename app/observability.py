"""Sentry Agent Tracing. Prompts are never sent: the friend's brain-dumps stay on the box."""
import contextlib
import os

import sentry_sdk


def init():
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    from sentry_sdk.integrations.openai import OpenAIIntegration

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=1.0,
        send_default_pii=False,
        integrations=[OpenAIIntegration(include_prompts=False)],
        environment=os.getenv("APP_ENV", "dev"),
    )


@contextlib.contextmanager
def agent_span(name: str = "actually"):
    with sentry_sdk.start_span(op="gen_ai.invoke_agent", name=f"invoke_agent {name}") as span:
        span.set_data("gen_ai.operation.name", "invoke_agent")
        span.set_data("gen_ai.agent.name", name)
        yield span


@contextlib.contextmanager
def tool_span(tool: str):
    with sentry_sdk.start_span(op="gen_ai.execute_tool", name=f"execute_tool {tool}") as span:
        span.set_data("gen_ai.operation.name", "execute_tool")
        span.set_data("gen_ai.tool.name", tool)
        yield span
