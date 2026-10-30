"""Stretch Goal 1 · LLM Theme Tagger vs. Keyword Rules (`stretch/llm_theme_tagger.py`).

Tags unique survey comments using an LLM constrained to a fixed `Literal[...]` theme
taxonomy, caches the tagged results to `data/llm_theme_cache.csv` so repeat runs cost
zero tokens, and compares the resulting theme counts against `theme_tools.py` keyword rules.

Run:
    python projects/02-nps-analyst/stretch/llm_theme_tagger.py
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Literal
import pandas as pd
from pydantic import BaseModel, Field
from strands import Agent

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nps_insights_agent.config import THEME_DEFINITIONS, get_model, get_model_description
from nps_insights_agent.tools.survey_tools import load_survey_df
from nps_insights_agent.tools.theme_tools import classify_comment_theme

CACHE_CSV_PATH = PROJECT_ROOT / "data" / "llm_theme_cache.csv"

ThemeLiteral = Literal[
    "otp_login",
    "fees_and_charges",
    "app_performance",
    "call_centre_ivr",
    "interest_rates_rewards",
    "positive_mismatch",
    "fast_digital_payments",
    "branch_and_rm_service",
    "card_cashback_rewards",
    "general_sentiment",
]


class CommentThemeTag(BaseModel):
    comment: str = Field(description="Exact customer comment text")
    llm_theme: ThemeLiteral = Field(description="Selected theme key from the allowed Literal list")
    rationale: str = Field(description="Short 1-sentence reason for selecting this theme")


class BatchThemeResult(BaseModel):
    items: list[CommentThemeTag]


def _tag_unique_comments_with_llm(unique_comments: list[str]) -> dict[str, CommentThemeTag]:
    """Tag a list of unique comments using the configured Strands LLM and validate with Pydantic."""
    taxonomy_lines = [
        f"- `{k}`: {v['label']} — {v['description']}"
        for k, v in THEME_DEFINITIONS.items()
    ]
    taxonomy_str = "\n".join(taxonomy_lines)

    tagger_agent = Agent(
        name="llm_theme_tagger",
        model=get_model(),
        callback_handler=None,
        tools=[],
        system_prompt=(
            "You are a customer experience text classifier for Future with Shivank Bank.\n"
            "Classify each customer survey comment into EXACTLY ONE of these allowed theme keys:\n"
            f"{taxonomy_str}\n\n"
            "Important rules:\n"
            "- If a comment is glowing praise ('Amazing support from the branch team', 'Excellent service, very happy', "
            "'Best bank I have used, love the app') that appears on detractor rows, classify it as `positive_mismatch`.\n"
            "- Return ONLY valid JSON with top-level key `items`, where each item has keys: "
            "`comment`, `llm_theme`, `rationale`."
        ),
    )

    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(unique_comments))
    prompt = f"Classify all {len(unique_comments)} unique survey comments below into the allowed theme keys:\n\n{numbered}"
    raw_resp = str(tagger_agent(prompt)).strip()

    # Extract JSON object from response
    match = re.search(r"\{[\s\S]*\}", raw_resp)
    json_str = match.group(0) if match else raw_resp
    parsed = json.loads(json_str)
    validated = BatchThemeResult.model_validate(parsed)

    return {item.comment.strip(): item for item in validated.items}


def run_llm_vs_keyword_comparison(force_refresh: bool = False) -> pd.DataFrame:
    """Tag all unique comments (loading from CSV cache when available) and compare with keyword rules."""
    df = load_survey_df().copy()
    commented = df.dropna(subset=["comment"]).copy()
    commented["comment_clean"] = commented["comment"].astype(str).str.strip()
    unique_comments = sorted(commented["comment_clean"].unique().tolist())

    if CACHE_CSV_PATH.exists() and not force_refresh:
        cache_df = pd.read_csv(CACHE_CSV_PATH)
        cached_map = dict(zip(cache_df["comment"], cache_df["llm_theme"]))
    else:
        cached_map = {}

    missing = [c for c in unique_comments if c not in cached_map]
    if missing:
        print(f">> Tagging {len(missing)} unique comments via LLM ({get_model_description()})...")
        tagged = _tag_unique_comments_with_llm(missing)
        rows = []
        for c in unique_comments:
            kw_theme = classify_comment_theme(c)
            if c in tagged:
                llm_t = tagged[c].llm_theme
                rat = tagged[c].rationale
            else:
                llm_t = cached_map.get(c, kw_theme)
                rat = "Cached / fallback"
            rows.append(
                {
                    "comment": c,
                    "keyword_theme": kw_theme,
                    "llm_theme": llm_t,
                    "agree": kw_theme == llm_t,
                    "rationale": rat,
                }
            )
        cache_df = pd.DataFrame(rows)
        cache_df.to_csv(CACHE_CSV_PATH, index=False)
        cached_map = dict(zip(cache_df["comment"], cache_df["llm_theme"]))
    else:
        print(f">> Loaded {len(cached_map)} cached LLM theme tags from {CACHE_CSV_PATH}")

    commented["keyword_theme"] = commented["comment_clean"].apply(classify_comment_theme)
    commented["llm_theme"] = commented["comment_clean"].map(cached_map)
    commented["agree"] = commented["keyword_theme"] == commented["llm_theme"]
    return commented


def main() -> None:
    print("=" * 75)
    print("STRETCH GOAL 1 · LLM THEME TAGGER VS. KEYWORD RULES")
    print("=" * 75)
    commented = run_llm_vs_keyword_comparison(force_refresh=False)
    total = len(commented)
    agree_cnt = int(commented["agree"].sum())
    print(f"Total Written Comments : {total}")
    print(f"Agreement Rate         : {agree_cnt}/{total} ({agree_cnt / total * 100:.1f}%)")
    print(f"Cache File             : {CACHE_CSV_PATH}\n")

    det = commented[commented["bucket"] == "detractor"]
    kw_counts = det["keyword_theme"].value_counts()
    llm_counts = det["llm_theme"].value_counts()
    all_themes = sorted(set(kw_counts.index).union(set(llm_counts.index)))

    print("--- Detractor Theme Comparison (139 Written Detractor Comments) ---")
    print(f"{'Theme Key':25s} | {'Keyword Rules':>13s} | {'LLM Tagger':>10s} | {'Diff':>6s}")
    print("-" * 64)
    for t in all_themes:
        k_c = int(kw_counts.get(t, 0))
        l_c = int(llm_counts.get(t, 0))
        diff = l_c - k_c
        print(f"{t:25s} | {k_c:13d} | {l_c:10d} | {diff:+6d}")
    print("=" * 75)


if __name__ == "__main__":
    main()

