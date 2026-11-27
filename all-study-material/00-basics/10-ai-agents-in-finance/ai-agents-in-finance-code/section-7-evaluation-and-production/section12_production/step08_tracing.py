"""
Section 12 lab — traces, fleet metrics and a drift alarm
========================================================
Every agent run becomes a TRACE: a tree of SPANS (the run → each model call →
each tool call), each with timing, tokens and status. We write one JSON line
per span, the same shape tracing tools (OpenTelemetry, Langfuse, LangSmith…)
collect, then roll the spans up into fleet metrics and compare this week with
a baseline week.

How to run
----------
No installs, no API key:   python step08_tracing.py
It simulates 40 normal runs, then 40 runs during a news-API outage, prints one
trace as a tree, the metrics for both windows, and the alerts that fire.
"""

from __future__ import annotations

import json
import random
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str                       # "agent" | "llm" | "tool"
    start: float
    end: float = 0.0
    status: str = "ok"
    attrs: dict = field(default_factory=dict)


class Tracer:
    """Records nested spans. The clock is injectable so the demo is repeatable."""

    def __init__(self, path: Path, clock):
        self.path, self.clock, self.spans, self._stack, self._n = path, clock, [], [], 0
        path.write_text("", encoding="utf-8")

    @contextmanager
    def span(self, name: str, kind: str, **attrs):
        parent = self._stack[-1] if self._stack else None
        self._n += 1
        s = Span(trace_id=parent.trace_id if parent else f"t{self._n:05d}", span_id=f"s{self._n:05d}",
                 parent_id=parent.span_id if parent else None, name=name, kind=kind,
                 start=round(self.clock(), 3), attrs=dict(attrs))
        self._stack.append(s)
        try:
            yield s
        finally:
            s.end = round(self.clock(), 3)
            self._stack.pop()
            self.spans.append(s)
            with self.path.open("a", encoding="utf-8") as f:     # one JSON line per span
                f.write(json.dumps(asdict(s)) + "\n")

class SimClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, seconds: float):
        self.t += seconds


def simulate_run(tracer: Tracer, clock: SimClock, ticker: str, rng: random.Random, news_down: bool):
    with tracer.span("analyst_run", "agent", ticker=ticker) as run:
        with tracer.span("llm.plan", "llm", input_tokens=900, output_tokens=60):
            clock.advance(rng.uniform(0.8, 1.6))
        with tracer.span("tool.get_quote", "tool", ticker=ticker):
            clock.advance(rng.uniform(0.1, 0.4))
        with tracer.span("tool.get_news", "tool", ticker=ticker) as news:
            clock.advance(rng.uniform(0.2, 0.6) if not news_down else 5.0)    # waits for its timeout
            if news_down or rng.random() < 0.02:
                news.status, news.attrs["error"] = "error", "ConnectionError: news service unavailable"
        with tracer.span("llm.write", "llm", input_tokens=1900, output_tokens=rng.randint(150, 260)):
            clock.advance(rng.uniform(1.5, 3.0))
        run.attrs["verdict"] = ("INSUFFICIENT_EVIDENCE" if news.status == "error"
                                else rng.choice(["POSITIVE", "NEUTRAL", "NEUTRAL", "NEGATIVE"]))
    clock.advance(rng.uniform(5, 30))                          # idle time between runs

PRICE_IN, PRICE_OUT = 3.0 / 1e6, 15.0 / 1e6                  # example $ per token; check real prices


def rollup(spans: list[Span]) -> list[dict]:
    """One row per run: latency, tokens, cost, tool errors, verdict."""
    rows = []
    for root in (s for s in spans if s.parent_id is None):
        kids = [s for s in spans if s.trace_id == root.trace_id and s.parent_id is not None]
        tin = sum(s.attrs.get("input_tokens", 0) for s in kids)
        tout = sum(s.attrs.get("output_tokens", 0) for s in kids)
        tools = [s for s in kids if s.kind == "tool"]
        rows.append({"trace_id": root.trace_id, "latency": root.end - root.start,
                     "cost": tin * PRICE_IN + tout * PRICE_OUT,
                     "tool_calls": len(tools), "tool_errors": sum(s.status == "error" for s in tools),
                     "verdict": root.attrs.get("verdict")})
    return rows


def window_metrics(rows: list[dict]) -> dict:
    lat = sorted(r["latency"] for r in rows)
    return {"runs": len(rows),
            "p95_latency_s": lat[int(0.95 * (len(lat) - 1))],
            "tool_error_rate": sum(r["tool_errors"] for r in rows) / sum(r["tool_calls"] for r in rows),
            "insufficient_share": sum(r["verdict"] == "INSUFFICIENT_EVIDENCE" for r in rows) / len(rows),
            "cost_per_run": sum(r["cost"] for r in rows) / len(rows)}


def drift_alerts(base: dict, cur: dict) -> list[str]:
    """Simple, explainable rules. Each alert names the metric, both values and the rule."""
    alerts = []
    if cur["tool_error_rate"] - base["tool_error_rate"] > 0.05:
        alerts.append(f"tool_error_rate {base['tool_error_rate']:.3f} → {cur['tool_error_rate']:.3f} (rule: +0.05)")
    if cur["insufficient_share"] - base["insufficient_share"] > 0.10:
        alerts.append(f"insufficient_share {base['insufficient_share']:.3f} → {cur['insufficient_share']:.3f} (rule: +0.10)")
    if cur["p95_latency_s"] > 1.5 * base["p95_latency_s"]:
        alerts.append(f"p95_latency {base['p95_latency_s']:.1f}s → {cur['p95_latency_s']:.1f}s (rule: ×1.5)")
    if cur["cost_per_run"] > 1.3 * base["cost_per_run"]:
        alerts.append(f"cost_per_run ${base['cost_per_run']:.4f} → ${cur['cost_per_run']:.4f} (rule: ×1.3)")
    return alerts


def print_tree(spans: list[Span], trace_id: str):
    def walk(parent_id, depth):
        for s in sorted((s for s in spans if s.trace_id == trace_id and s.parent_id == parent_id), key=lambda s: s.start):
            extra = " ".join(f"{k}={v}" for k, v in s.attrs.items())
            flag = "  ✗ " + s.status.upper() if s.status != "ok" else ""
            print(f"   {'  ' * depth}{s.name:<{22 - 2 * depth}} {s.end - s.start:5.2f}s  {extra}{flag}")
            walk(s.span_id, depth + 1)
    walk(None, 0)

if __name__ == "__main__":
    rng, clock = random.Random(11), SimClock()
    tracer = Tracer(Path(__file__).with_name("traces.jsonl"), clock)
    names = ["ACME", "BOLT", "CRUX", "DYNA", "EVRO"]
    for i in range(40):
        simulate_run(tracer, clock, names[i % 5], rng, news_down=False)
    baseline_spans = list(tracer.spans)
    for i in range(40):
        simulate_run(tracer, clock, names[i % 5], rng, news_down=rng.random() < 0.8)
    current_spans = tracer.spans[len(baseline_spans):]

    print("One trace during the outage:")
    print_tree(current_spans, current_spans[-1].trace_id)
    base, cur = window_metrics(rollup(baseline_spans)), window_metrics(rollup(current_spans))
    print(f"\n{'metric':<20}{'baseline':>12}{'this week':>12}")
    for k in base:
        f = "{:>12}" if k == "runs" else "{:>12.3f}"
        print(f"{k:<20}" + f.format(base[k]) + f.format(cur[k]))
    print("\nALERTS:" if drift_alerts(base, cur) else "\nno alerts")
    for a in drift_alerts(base, cur):
        print("  ⚠", a)
    print(f"\n{len(tracer.spans)} spans written to {tracer.path.name}")
