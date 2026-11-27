"""
step06_tot_hedge.py — Friday morning: pick a hedge for a big NVDA position before
earnings, using a two-level Tree of Thoughts (beam search).

    Level 1: which hedge?   4 ideas → score each → keep the best 2
    Level 2: how big?       for each kept idea: 3 sizings → score → keep the best 1

Run it:
    pip install anthropic python-dotenv
    python step06_tot_hedge.py
"""
import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"


HEDGES_SCHEMA = {                       # "give me a list of named ideas"
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["name", "rationale"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["candidates"],
    "additionalProperties": False,
}

SCORE_SCHEMA = {                        # "give me one number and why"
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "reasoning": {"type": "string"},
    },
    "required": ["score", "reasoning"],
    "additionalProperties": False,
}


def ask_json(prompt: str, schema: dict) -> dict:
    """One LLM call whose reply MUST match `schema` (structured outputs)."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    text = next(b.text for b in response.content if b.type == "text")  # first text block
    return json.loads(text)                                            # JSON text → dict


def generate_hedges(portfolio: str, scenario: str, n: int) -> list[dict]:
    """Thought generator, level 1: n hedge ideas in ONE call."""
    prompt = (
        f"Portfolio: {portfolio}\nStress scenario: {scenario}\n"
        f"Propose {n} distinct hedge candidates, each with a short rationale."
    )
    return ask_json(prompt, HEDGES_SCHEMA)["candidates"]


def score_hedge(portfolio: str, scenario: str, hedge: dict) -> dict:
    """State evaluator, level 1: score one idea from 1 to 10."""
    prompt = (
        f"Portfolio: {portfolio}\nStress scenario: {scenario}\n"
        f"Candidate hedge: {hedge['name']} ({hedge['rationale']})\n"
        f"Score this hedge from 1 to 10 on protection, cost, and basis risk."
    )
    return ask_json(prompt, SCORE_SCHEMA)


def generate_sizings(portfolio: str, scenario: str, hedge: dict, n: int) -> list[dict]:
    """Thought generator, level 2: n ways to size ONE parent hedge."""
    prompt = (
        f"Portfolio: {portfolio}\nScenario: {scenario}\n"
        f"Parent hedge: {hedge['name']} ({hedge['rationale']})\n"
        f"Propose {n} distinct sizings or structures for this hedge "
        f"(e.g. strike, notional, expiry, spread width), each with a short rationale."
    )
    return ask_json(prompt, HEDGES_SCHEMA)["candidates"]


def score_sizing(portfolio: str, scenario: str, hedge: dict, sizing: dict) -> dict:
    """State evaluator, level 2: judged together with its parent."""
    prompt = (
        f"Portfolio: {portfolio}\nScenario: {scenario}\n"
        f"Parent hedge: {hedge['name']} ({hedge['rationale']})\n"
        f"Candidate sizing: {sizing['name']} ({sizing['rationale']})\n"
        f"Score this sizing from 1 to 10 on residual exposure to the catalyst, "
        f"premium cost, and how cleanly it complements the parent hedge."
    )
    return ask_json(prompt, SCORE_SCHEMA)


def best_hedges(portfolio: str, scenario: str, beam_width: int = 2) -> list[dict]:
    # Level 1: pick the best hedge instruments
    candidates = generate_hedges(portfolio, scenario, n=4)                   # ① 4 ideas
    scored = [{**c, **score_hedge(portfolio, scenario, c)} for c in candidates]  # ② + score
    scored.sort(key=lambda x: x["score"], reverse=True)                      # ③ best first
    retained = scored[:beam_width]                                           # ④ prune

    # Level 2: for each retained hedge, pick its best sizing
    for hedge in retained:                                                   # ⑤ per branch
        sizings = generate_sizings(portfolio, scenario, hedge, n=3)
        scored_sizings = [
            {**s, **score_sizing(portfolio, scenario, hedge, s)} for s in sizings
        ]
        scored_sizings.sort(key=lambda x: x["score"], reverse=True)
        hedge["best_sizing"] = scored_sizings[0]                             # ⑥ keep 1
    return retained


if __name__ == "__main__":
    portfolio = "5,000 shares of NVDA held outright (~$5M concentrated single-name position)"
    scenario = ("NVDA reports earnings tonight after the close; "
                "weekly implied volatility is elevated")
    for h in best_hedges(portfolio, scenario):
        print(f"{h['score']:>2}  {h['name']}: {h['reasoning']}")
        s = h["best_sizing"]
        print(f"    └─ best sizing ({s['score']}): {s['name']}: {s['reasoning']}")
