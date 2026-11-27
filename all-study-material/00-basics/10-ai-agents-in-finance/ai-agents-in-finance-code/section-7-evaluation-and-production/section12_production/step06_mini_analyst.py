"""
Section 12 lab — the harness: an agent loop with no framework
=============================================================
Every agent framework hides the same few dozen lines. Writing them yourself
shows exactly where production problems live: the iteration cap, tool errors,
and what goes back to the model.

    question → model → wants a tool? → run it → result back to the model → … → answer
                 ↑______________________________________________|   (max MAX_ITERATIONS)

How to run
----------
Free, offline (a scripted model plays Claude's part, no installs):
    python step06_mini_analyst.py --offline ACME        # normal run
    python step06_mini_analyst.py --offline CRUX        # the news tool fails → visible gap
    python step06_mini_analyst.py --offline ACME --stubborn   # a model that never stops → cap
With Claude:
    pip install anthropic python-dotenv          # and ANTHROPIC_API_KEY=... in .env
    python step06_mini_analyst.py "Write a short note on ACME"
The market data is fictional and built in, so live runs need no other service.
"""

from __future__ import annotations

import argparse
import json
import re
from types import SimpleNamespace

FAKE_QUOTES = {"ACME": {"price": 41.20, "change_pct": -2.4, "pe": 18.5},
               "BOLT": {"price": 12.75, "change_pct": 0.8, "pe": 31.0},
               "CRUX": {"price": 88.10, "change_pct": 1.9, "pe": 22.4}}
FAKE_NEWS = {"ACME": ["Acme raises full-year revenue guidance", "Supplier delay pushes humanoid launch to Q2"],
             "BOLT": ["Bolt wins regional grid contract"],
             "CRUX": ["(unavailable)"]}
NEWS_OUTAGE = {"CRUX"}                     # simulate a news service that is down for CRUX

TOOLS = [
    {"name": "get_quote",
     "description": "Latest price, today's % change and P/E ratio for one ticker in the research universe.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string", "description": "Upper-case ticker, e.g. ACME"}},
                      "required": ["ticker"]}},
    {"name": "get_news",
     "description": "Up to three recent headlines for one ticker.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}},
]


def get_quote(ticker: str) -> dict:
    return {"ticker": ticker, **FAKE_QUOTES[ticker]}          # KeyError for unknown tickers


def get_news(ticker: str) -> dict:
    if ticker in NEWS_OUTAGE:
        raise ConnectionError("news service unavailable")
    return {"ticker": ticker, "headlines": FAKE_NEWS[ticker][:3]}


REGISTRY = {"get_quote": get_quote, "get_news": get_news}


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Run one tool. NEVER raise: an error goes back to the model as text, flagged is_error."""
    fn = REGISTRY.get(name)
    if fn is None:
        return f"Unknown tool {name!r}", True
    try:
        return json.dumps(fn(**args)), False
    except Exception as exc:                                  # the model must SEE the failure
        return f"{type(exc).__name__}: {exc}", True

SYSTEM = ("You are a research assistant at an investment bank. Use the tools for every fact; "
          "never invent numbers. If a tool fails, say what is missing. End with exactly one line: "
          "VERDICT: POSITIVE | NEUTRAL | NEGATIVE | INSUFFICIENT_EVIDENCE")
MAX_ITERATIONS = 6


def run_agent(question: str, model, max_iterations: int = MAX_ITERATIONS, log=print) -> dict:
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_iterations + 1):
        reply = model(system=SYSTEM, messages=messages, tools=TOOLS)
        messages.append({"role": "assistant", "content": reply.content})
        if reply.stop_reason != "tool_use":                   # the model is done talking
            text = "".join(b.text for b in reply.content if b.type == "text")
            return {"answer": text, "steps": step, "stopped": "done", "messages": messages}
        results = []
        for block in reply.content:                           # it may ask for several tools at once
            if block.type == "tool_use":
                output, is_error = run_tool(block.name, block.input)
                log(f"  step {step}: {block.name}({block.input}) → {'ERROR ' if is_error else ''}{output[:70]}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})  # results go back as a USER turn
    return {"answer": "Stopped at the iteration limit.\nVERDICT: INSUFFICIENT_EVIDENCE",
            "steps": max_iterations, "stopped": "limit", "messages": messages}   # fail closed

def claude_model(model_id: str = "claude-sonnet-5-5"):
    """A real model call. The API key is read from the environment, never put in a prompt."""
    import anthropic
    from dotenv import load_dotenv
    load_dotenv()
    client = anthropic.Anthropic()

    def call(system, messages, tools):
        return client.messages.create(model=model_id, max_tokens=1024, system=system,
                                      messages=messages, tools=tools, timeout=30)
    return call


class ScriptedModel:
    """Plays the model's part offline, with replies shaped like the real API's."""

    def __init__(self, stubborn: bool = False):
        self.stubborn, self.calls = stubborn, 0

    def __call__(self, system, messages, tools):
        self.calls += 1
        ticker = re.findall(r"\b[A-Z]{2,5}\b", messages[0]["content"])[-1]
        results = [b for m in messages if m["role"] == "user" and isinstance(m["content"], list) for b in m["content"]]
        if self.stubborn or len(results) == 0:
            return self._tool("get_quote", ticker)
        if len(results) == 1:
            return self._tool("get_news", ticker)
        quote, news = json.loads(results[0]["content"]), results[1]
        line = f"{ticker} trades at ${quote['price']:.2f} ({quote['change_pct']:+.1f}% today), P/E {quote['pe']}."
        if news["is_error"]:
            text = f"{line} News could not be retrieved ({news['content']}), so the picture is incomplete.\nVERDICT: INSUFFICIENT_EVIDENCE"
        else:
            heads = "; ".join(json.loads(news["content"])["headlines"])
            text = f"{line} Recent news: {heads}. Mixed signals.\nVERDICT: NEUTRAL"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    def _tool(self, name, ticker):
        block = SimpleNamespace(type="tool_use", id=f"toolu_{self.calls:03d}", name=name, input={"ticker": ticker})
        return SimpleNamespace(stop_reason="tool_use", content=[block])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?", default="Write a short note on ACME")
    ap.add_argument("--offline", action="store_true", help="use the scripted model (free)")
    ap.add_argument("--stubborn", action="store_true", help="offline model that never stops calling tools")
    args = ap.parse_args()
    question = args.question if not re.fullmatch(r"[A-Z]{2,5}", args.question) else f"Write a short note on {args.question}"
    model = ScriptedModel(args.stubborn) if args.offline else claude_model()
    out = run_agent(question, model)
    print(f"\n{out['answer']}\n\n(steps: {out['steps']}, stopped: {out['stopped']})")
