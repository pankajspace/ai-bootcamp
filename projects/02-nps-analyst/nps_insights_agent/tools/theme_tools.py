"""Theme Tools — Keyword-based comment theme classification, counts, revenue at risk & verbatim quotes.

Reference:
- Project - NPS Analyst in a Box.html (P4 VoiceOfCustomerAgent & P5 `theme_tools.py`)
- Categorizes the 536 written comments across detractor, passive, and promoter buckets.
"""

from __future__ import annotations

import json
from typing import Any
import pandas as pd
from strands import tool

from nps_insights_agent.config import LAKH_INR, THEME_DEFINITIONS
from nps_insights_agent.tools.survey_tools import load_survey_df


def classify_comment_theme(comment: Any) -> str:
    """Deterministically map a single comment string to a theme key using keyword rules."""
    if pd.isna(comment) or not str(comment).strip():
        return "blank"
    text = str(comment).strip().lower()

    # Check specific themes in priority order before falling back to general_sentiment
    priority_order = (
        "positive_mismatch",
        "otp_login",
        "fees_and_charges",
        "app_performance",
        "call_centre_ivr",
        "interest_rates_rewards",
        "fast_digital_payments",
        "branch_and_rm_service",
        "card_cashback_rewards",
        "general_sentiment",
    )
    for theme_key in priority_order:
        keywords: list[str] = THEME_DEFINITIONS[theme_key]["keywords"]  # type: ignore[assignment]
        if any(kw in text for kw in keywords):
            return theme_key
    return "other"


@tool
def get_comment_themes(bucket: str = "detractor", month: str = "") -> str:
    """Group written survey comments into root-cause themes with counts, revenue at risk, and verbatim quotes.

    Args:
        bucket: Score bucket to analyze: 'detractor' (0-6), 'passive' (7-8), 'promoter' (9-10), or 'all'. Defaults to 'detractor'.
        month: Optional month filter ('2026-07', '2026-08', or '2026-09'). Leave empty for all months.

    Returns:
        JSON string with theme counts, share of comments, monthly distribution, revenue at risk in ₹ lakh, and sample quotes.
    """
    try:
        df = load_survey_df().copy()
        clean_bucket = (bucket or "detractor").strip().lower()
        valid_buckets = ("detractor", "passive", "promoter", "all")
        if clean_bucket not in valid_buckets:
            return json.dumps(
                {
                    "error": f"Invalid bucket '{bucket}'. Must be one of {list(valid_buckets)}."
                }
            )

        if clean_bucket != "all":
            df = df[df["bucket"] == clean_bucket]

        clean_month = (month or "").strip()
        if clean_month.lower() in {"all", "none", "null", "*"}:
            clean_month = ""
        if clean_month:
            available_months = sorted(df["month"].astype(str).unique().tolist())
            if clean_month not in available_months:
                return json.dumps(
                    {
                        "error": f"Invalid month '{month}'. Available months: {available_months}."
                    }
                )
            df = df[df["month"].astype(str) == clean_month]

        total_rows = int(len(df))
        df["theme"] = df["comment"].apply(classify_comment_theme)
        commented_df = df[df["theme"] != "blank"]
        commented_count = int(len(commented_df))
        blank_count = total_rows - commented_count

        themes_out = []
        for theme_key, grp in commented_df.groupby("theme"):
            t_info = THEME_DEFINITIONS.get(
                str(theme_key),
                {"label": str(theme_key), "description": "Other comments"},
            )
            count = int(len(grp))
            rev_lakh = round(float(grp["annual_revenue_inr"].sum()) / LAKH_INR, 2)
            risk_lakh = round(float(grp["expected_loss_inr"].sum()) / LAKH_INR, 2)

            # Monthly breakdown of this theme
            by_month = {
                str(m): int(c) for m, c in grp["month"].value_counts().sort_index().items()
            }
            by_product = {
                str(p): int(c) for p, c in grp["product"].value_counts().items()
            }
            by_channel = {
                str(ch): int(c) for ch, c in grp["channel"].value_counts().items()
            }

            # Sample verbatim quotes with response_id, product, score, and revenue
            sample_rows = grp.sort_values(
                by=["annual_revenue_inr", "score"], ascending=[False, True]
            ).head(4)
            quotes = [
                {
                    "response_id": str(r["response_id"]),
                    "month": str(r["month"]),
                    "product": str(r["product"]),
                    "channel": str(r["channel"]),
                    "score": int(r["score"]),
                    "annual_revenue_lakh": round(float(r["annual_revenue_inr"]) / LAKH_INR, 2),
                    "quote": str(r["comment"]),
                }
                for _, r in sample_rows.iterrows()
            ]

            themes_out.append(
                {
                    "theme_key": str(theme_key),
                    "theme_label": t_info["label"],
                    "description": t_info["description"],
                    "comment_count": count,
                    "share_of_commented_pct": round(
                        (count / commented_count * 100.0) if commented_count else 0.0, 1
                    ),
                    "share_of_total_bucket_pct": round(
                        (count / total_rows * 100.0) if total_rows else 0.0, 1
                    ),
                    "annual_revenue_lakh": rev_lakh,
                    "revenue_at_risk_lakh": risk_lakh,
                    "by_month": by_month,
                    "by_product": by_product,
                    "by_channel": by_channel,
                    "sample_quotes": quotes,
                }
            )

        themes_out.sort(key=lambda x: (x["comment_count"], x["revenue_at_risk_lakh"]), reverse=True)

        payload = {
            "bucket": clean_bucket,
            "month_filter": clean_month if clean_month else "ALL (2026-07 to 2026-09)",
            "total_responses_in_slice": total_rows,
            "written_comments_count": commented_count,
            "blank_comments_count": blank_count,
            "themes_count": len(themes_out),
            "themes": themes_out,
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"get_comment_themes failed: {exc}"})

