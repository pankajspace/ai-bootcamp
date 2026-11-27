"""
Section 12 lab — what exactly is "version 2" of an agent?
=========================================================
An agent's behaviour depends on FOUR things, and changing any one of them is a
release: the model, the prompts, the tool definitions and the config (limits,
temperature-like settings, thresholds). This file fingerprints all four, shows
what changed between two versions, and makes a canary decision by replaying
past cases through the new version.

How to run
----------
No installs, no API key:   python step09_release_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import random


def fingerprint(obj) -> str:
    """Short, stable hash of anything JSON-serialisable (sorted keys → same input, same hash)."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]


def build_manifest(model_id: str, prompts: dict, tools: list, config: dict) -> dict:
    parts = {"model": fingerprint(model_id),
             **{f"prompt:{name}": fingerprint(text) for name, text in prompts.items()},
             "tools": fingerprint(tools),
             "config": fingerprint(config)}
    return {"model_id": model_id, "parts": parts, "version": fingerprint(parts)}


def diff_manifests(old: dict, new: dict) -> list[str]:
    keys = sorted(set(old["parts"]) | set(new["parts"]))
    return [k for k in keys if old["parts"].get(k) != new["parts"].get(k)]


def pin_warnings(model_id: str) -> list[str]:
    """A moving alias can change behaviour without any change on your side."""
    return [f"'{model_id}' looks like a moving alias; pin an exact model version"] if "latest" in model_id else []

def verdict_shift(old: list[str], new: list[str]) -> float:
    return sum(a != b for a, b in zip(old, new)) / len(old)


def canary_decision(shift: float, error_rate: float, max_shift: float = 0.05, max_errors: float = 0.02) -> str:
    """ROLLBACK on errors; HOLD for human review if too many answers changed; else PROMOTE."""
    if error_rate > max_errors:
        return "ROLLBACK"
    if shift > max_shift:
        return "HOLD"
    return "PROMOTE"

if __name__ == "__main__":
    tools = [{"name": "get_quote"}, {"name": "get_news"}]
    config = {"max_iterations": 6, "max_usd_per_run": 0.50}
    v1 = build_manifest("claude-sonnet-5-5", {"system": "You are a research assistant… Prefer NEUTRAL when evidence is mixed."}, tools, config)
    v2 = build_manifest("claude-sonnet-5-5", {"system": "You are a research assistant…"}, tools, config)   # one sentence removed
    print(f"v1 = {v1['version']}   v2 = {v2['version']}")
    print("changed parts:", diff_manifests(v1, v2))
    print("pinning:", pin_warnings("claude-latest") or "ok", "|", pin_warnings(v2["model_id"]) or "ok")

    # replay 200 stored cases through both versions (simulated here)
    rng = random.Random(5)
    old = [rng.choice(["POSITIVE", "NEUTRAL", "NEUTRAL", "NEGATIVE"]) for _ in range(200)]
    new = list(old)
    for i in rng.sample(range(200), 36):                  # the edit moved 36 answers
        new[i] = "POSITIVE" if old[i] == "NEUTRAL" else "NEUTRAL"
    shift = verdict_shift(old, new)
    moves = {}
    for a, b in zip(old, new):
        if a != b:
            moves[f"{a}→{b}"] = moves.get(f"{a}→{b}", 0) + 1
    print(f"\nreplay: {shift:.0%} of verdicts changed  {moves}")
    print("canary decision:", canary_decision(shift, error_rate=0.005))
