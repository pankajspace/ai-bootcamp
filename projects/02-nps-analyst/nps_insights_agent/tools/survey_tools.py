"""Survey Tools — Plain Python + Pandas tools for NPS, segments, revenue at risk, mismatches & callbacks.

Reference:
- Project - NPS Analyst in a Box.html (P4 Architecture & P5 Tools)
- Tools return JSON strings and never crash on bad input.
- `load_survey_df` and `_compute_nps_by_segment_cached` use `@lru_cache` so the CSV
  is loaded once and shared across `ScoreAnalystAgent` and `ChurnRiskAgent`.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
import os
from pathlib import Path
from typing import Any
import pandas as pd
from strands import tool

from nps_insights_agent.config import (
    CHURN_RATES,
    DEFAULT_SURVEY_PATH,
    LAKH_INR,
    MIN_SAMPLE_SIZE,
    NEGATIVE_COMPLAINT_PATTERNS,
    PASSIVE_MIN_SCORE,
    POSITIVE_PRAISE_PATTERNS,
    PROMOTER_MIN_SCORE,
    REQUIRED_COLUMNS,
    SEGMENT_COLUMNS,
    get_alert_level,
    get_nps_health_verdict,
    get_revenue_risk_verdict,
)


def _classify_bucket(score: int | float) -> str:
    if score >= PROMOTER_MIN_SCORE:
        return "promoter"
    if score >= PASSIVE_MIN_SCORE:
        return "passive"
    return "detractor"


def _resolve_survey_path(survey_path: str | None = None) -> str:
    if survey_path and survey_path.strip():
        return str(Path(survey_path).resolve())
    env_path = os.getenv("NPS_SURVEY_PATH")
    if env_path and env_path.strip():
        return str(Path(env_path).resolve())
    return str(DEFAULT_SURVEY_PATH.resolve())


@lru_cache(maxsize=8)
def load_survey_df(survey_path_str: str | None = None) -> pd.DataFrame:
    """Load and enrich the NPS survey CSV once (cached in memory)."""
    resolved = _resolve_survey_path(survey_path_str)
    df = pd.read_csv(resolved)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Survey CSV is missing required columns: {missing}")

    df = df.copy()
    df["bucket"] = df["score"].apply(_classify_bucket)
    df["churn_prob"] = df["bucket"].map(CHURN_RATES)
    df["expected_loss_inr"] = df["annual_revenue_inr"] * df["churn_prob"]
    return df


def compute_nps_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute exact NPS, bucket counts/percentages, 95% MOE, and low-sample flag."""
    n = int(len(df))
    if n == 0:
        return {
            "responses": 0,
            "promoters": 0,
            "passives": 0,
            "detractors": 0,
            "promoter_pct": 0.0,
            "passive_pct": 0.0,
            "detractor_pct": 0.0,
            "nps": 0.0,
            "nps_formatted": "+0.0",
            "margin_of_error_95": 0.0,
            "low_sample": True,
            "health_verdict": "NEEDS WORK",
        }

    promoters = int((df["score"] >= PROMOTER_MIN_SCORE).sum())
    passives = int(
        ((df["score"] >= PASSIVE_MIN_SCORE) & (df["score"] < PROMOTER_MIN_SCORE)).sum()
    )
    detractors = int((df["score"] < PASSIVE_MIN_SCORE).sum())

    p_share = promoters / n
    pa_share = passives / n
    d_share = detractors / n
    nps = round((p_share - d_share) * 100.0, 1)

    variance = max(0.0, (p_share + d_share) - (p_share - d_share) ** 2)
    moe_95 = round(1.96 * math.sqrt(variance / n) * 100.0, 1)

    return {
        "responses": n,
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "promoter_pct": round(p_share * 100.0, 1),
        "passive_pct": round(pa_share * 100.0, 1),
        "detractor_pct": round(d_share * 100.0, 1),
        "nps": nps,
        "nps_formatted": f"{nps:+.1f}",
        "margin_of_error_95": moe_95,
        "low_sample": n < MIN_SAMPLE_SIZE,
        "health_verdict": get_nps_health_verdict(nps),
    }


@tool
def get_nps_overview() -> str:
    """Compute overall NPS, 95% margin of error, health verdict, and monthly trend (July to September 2026).

    Returns:
        JSON string with overall NPS metrics, monthly trend, drop magnitude, and recommended alert level.
    """
    try:
        df = load_survey_df()
        overall = compute_nps_metrics(df)
        comments_count = int(df["comment"].notna().sum())

        monthly_trend = []
        for month_val, grp in df.groupby("month", sort=True):
            m_stats = compute_nps_metrics(grp)
            monthly_trend.append({"month": str(month_val), **m_stats})

        first_month_nps = monthly_trend[0]["nps"] if monthly_trend else overall["nps"]
        latest_month_nps = monthly_trend[-1]["nps"] if monthly_trend else overall["nps"]
        nps_change = round(latest_month_nps - first_month_nps, 1)
        worst_month = min(monthly_trend, key=lambda x: x["nps"]) if monthly_trend else None
        best_month = max(monthly_trend, key=lambda x: x["nps"]) if monthly_trend else None

        total_risk_lakh = round(float(df["expected_loss_inr"].sum()) / LAKH_INR, 2)
        alert_level = get_alert_level(
            overall_nps=overall["nps"],
            latest_month_nps=latest_month_nps,
            nps_drop_pts=abs(min(0.0, nps_change)),
            revenue_at_risk_lakh=total_risk_lakh,
        )

        payload = {
            "overall": {
                **overall,
                "written_comments": comments_count,
                "blank_comments": int(len(df) - comments_count),
            },
            "monthly_trend": monthly_trend,
            "trend_summary": {
                "start_month": monthly_trend[0]["month"] if monthly_trend else None,
                "start_nps": first_month_nps,
                "start_nps_formatted": f"{first_month_nps:+.1f}",
                "latest_month": monthly_trend[-1]["month"] if monthly_trend else None,
                "latest_nps": latest_month_nps,
                "latest_nps_formatted": f"{latest_month_nps:+.1f}",
                "change_points": nps_change,
                "change_formatted": f"{nps_change:+.1f}",
                "best_month": best_month["month"] if best_month else None,
                "worst_month": worst_month["month"] if worst_month else None,
            },
            "recommended_alert_level": alert_level,
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"get_nps_overview failed: {exc}"})


@lru_cache(maxsize=32)
def _compute_nps_by_segment_cached(
    segment_col: str, month_filter: str = "", survey_path_str: str = ""
) -> str:
    """Cached helper for `get_nps_by_segment` (* shared tool across ScoreAnalyst & ChurnRisk)."""
    df = load_survey_df(survey_path_str or None)
    col = segment_col.strip().lower()
    if col not in SEGMENT_COLUMNS:
        return json.dumps(
            {
                "error": f"Invalid segment_col '{segment_col}'. Must be one of {list(SEGMENT_COLUMNS)}."
            }
        )

    if month_filter:
        available_months = sorted(df["month"].astype(str).unique().tolist())
        if month_filter not in available_months:
            return json.dumps(
                {
                    "error": f"Invalid month '{month_filter}'. Available months: {available_months}."
                }
            )
        df = df[df["month"].astype(str) == month_filter]

    segments = []
    for val, grp in df.groupby(col, sort=True):
        stats = compute_nps_metrics(grp)
        rev_lakh = round(float(grp["annual_revenue_inr"].sum()) / LAKH_INR, 2)
        risk_lakh = round(float(grp["expected_loss_inr"].sum()) / LAKH_INR, 2)
        segments.append(
            {
                "segment_value": str(val),
                **stats,
                "total_revenue_lakh": rev_lakh,
                "revenue_at_risk_lakh": risk_lakh,
            }
        )

    # Best and worst segments MUST exclude `low_sample` segments (< 30 responses)
    valid_segments = [s for s in segments if not s["low_sample"]]
    low_sample_segments = [s["segment_value"] for s in segments if s["low_sample"]]

    best_seg = max(valid_segments, key=lambda x: x["nps"]) if valid_segments else None
    worst_seg = min(valid_segments, key=lambda x: x["nps"]) if valid_segments else None

    result = {
        "segment_column": col,
        "month_filter": month_filter if month_filter else "ALL (2026-07 to 2026-09)",
        "min_sample_size_rule": MIN_SAMPLE_SIZE,
        "segments": segments,
        "best_valid_segment": (
            {"segment_value": best_seg["segment_value"], "nps": best_seg["nps"], "nps_formatted": best_seg["nps_formatted"], "responses": best_seg["responses"]}
            if best_seg
            else None
        ),
        "worst_valid_segment": (
            {"segment_value": worst_seg["segment_value"], "nps": worst_seg["nps"], "nps_formatted": worst_seg["nps_formatted"], "responses": worst_seg["responses"]}
            if worst_seg
            else None
        ),
        "low_sample_warnings": [
            f"{s['segment_value']} has only {s['responses']} answers (<{MIN_SAMPLE_SIZE}, MOE ±{s['margin_of_error_95']}): flagged low_sample — never call it best or worst."
            for s in segments
            if s["low_sample"]
        ],
        "low_sample_segments": low_sample_segments,
    }
    return json.dumps(result, indent=2)


@tool
def get_nps_by_segment(segment_col: str = "product", month: str = "") -> str:
    """Slice NPS, 95% margin of error, and low-sample flags by a segment column, optionally filtered to one month.

    Args:
        segment_col: One of 'product', 'channel', 'tenure', or 'month'. Defaults to 'product'.
        month: Optional month filter ('2026-07', '2026-08', or '2026-09') to drill down into a specific month. Leave empty for all months.

    Returns:
        JSON string containing NPS metrics per segment, best/worst valid segments (n >= 30), and low_sample warnings.
    """
    try:
        clean_month = (month or "").strip()
        if clean_month.lower() in {"all", "none", "null", "*"}:
            clean_month = ""
        return _compute_nps_by_segment_cached(
            segment_col=(segment_col or "product").strip().lower(),
            month_filter=clean_month,
            survey_path_str=_resolve_survey_path(),
        )
    except Exception as exc:
        return json.dumps({"error": f"get_nps_by_segment failed: {exc}"})


@tool
def get_revenue_at_risk(by_col: str = "product") -> str:
    """Calculate expected annual revenue at risk in ₹ lakh using house churn assumptions (3% promoter, 10% passive, 25% detractor).

    Args:
        by_col: Segment column to group revenue at risk by ('product', 'channel', 'tenure', 'month', or 'bucket'). Defaults to 'product'.

    Returns:
        JSON string with total annual revenue, expected revenue at risk in ₹ lakh, breakdown by segment, churn assumptions, and risk verdict.
    """
    try:
        df = load_survey_df()
        col = (by_col or "product").strip().lower()
        valid_cols = (*SEGMENT_COLUMNS, "bucket")
        if col not in valid_cols:
            return json.dumps(
                {
                    "error": f"Invalid by_col '{by_col}'. Must be one of {list(valid_cols)}."
                }
            )

        total_rev_lakh = round(float(df["annual_revenue_inr"].sum()) / LAKH_INR, 2)
        total_risk_lakh = round(float(df["expected_loss_inr"].sum()) / LAKH_INR, 2)
        det_df = df[df["bucket"] == "detractor"]
        det_rev_lakh = round(float(det_df["annual_revenue_inr"].sum()) / LAKH_INR, 2)
        det_risk_lakh = round(float(det_df["expected_loss_inr"].sum()) / LAKH_INR, 2)

        bucket_breakdown = []
        for b_name in ("detractor", "passive", "promoter"):
            b_grp = df[df["bucket"] == b_name]
            b_rev = round(float(b_grp["annual_revenue_inr"].sum()) / LAKH_INR, 2)
            b_risk = round(float(b_grp["expected_loss_inr"].sum()) / LAKH_INR, 2)
            bucket_breakdown.append(
                {
                    "bucket": b_name,
                    "responses": int(len(b_grp)),
                    "churn_rate_assumption": CHURN_RATES[b_name],
                    "churn_rate_pct": f"{CHURN_RATES[b_name] * 100:.0f}%",
                    "annual_revenue_lakh": b_rev,
                    "revenue_at_risk_lakh": b_risk,
                    "share_of_total_risk_pct": round(
                        (b_risk / total_risk_lakh * 100.0) if total_risk_lakh else 0.0, 1
                    ),
                }
            )

        segment_breakdown = []
        for val, grp in df.groupby(col, sort=True):
            s_rev = round(float(grp["annual_revenue_inr"].sum()) / LAKH_INR, 2)
            s_risk = round(float(grp["expected_loss_inr"].sum()) / LAKH_INR, 2)
            s_det = grp[grp["bucket"] == "detractor"]
            s_det_rev = round(float(s_det["annual_revenue_inr"].sum()) / LAKH_INR, 2)
            s_det_risk = round(float(s_det["expected_loss_inr"].sum()) / LAKH_INR, 2)
            segment_breakdown.append(
                {
                    "segment": str(val),
                    "responses": int(len(grp)),
                    "detractors": int(len(s_det)),
                    "avg_revenue_per_customer_inr": round(float(grp["annual_revenue_inr"].mean()), 0),
                    "total_revenue_lakh": s_rev,
                    "revenue_at_risk_lakh": s_risk,
                    "detractor_revenue_lakh": s_det_rev,
                    "detractor_revenue_at_risk_lakh": s_det_risk,
                    "share_of_total_risk_pct": round(
                        (s_risk / total_risk_lakh * 100.0) if total_risk_lakh else 0.0, 1
                    ),
                }
            )

        segment_breakdown.sort(key=lambda x: x["revenue_at_risk_lakh"], reverse=True)
        highest_risk_seg = segment_breakdown[0] if segment_breakdown else None
        most_detractors_seg = (
            max(segment_breakdown, key=lambda x: x["detractors"]) if segment_breakdown else None
        )

        verdict = get_revenue_risk_verdict(total_risk_lakh, total_rev_lakh)

        payload = {
            "unit": "INR lakh (1 lakh = ₹1,00,000; 100 lakh = 1 crore)",
            "churn_rate_assumptions": {
                "promoter": "3% (0.03)",
                "passive": "10% (0.10)",
                "detractor": "25% (0.25)",
                "note": "House assumptions configured in config.py; must be stated under DATA CAVEATS.",
            },
            "totals": {
                "total_annual_revenue_lakh": total_rev_lakh,
                "total_revenue_at_risk_lakh": total_risk_lakh,
                "risk_as_pct_of_total_revenue": round(
                    (total_risk_lakh / total_rev_lakh * 100.0) if total_rev_lakh else 0.0, 1
                ),
                "detractor_annual_revenue_lakh": det_rev_lakh,
                "detractor_revenue_at_risk_lakh": det_risk_lakh,
                "risk_verdict": verdict,
            },
            "by_bucket": bucket_breakdown,
            "grouped_by": col,
            "breakdown": segment_breakdown,
            "loud_vs_expensive_insight": {
                "most_detractors_segment": (
                    {
                        "segment": most_detractors_seg["segment"],
                        "detractors": most_detractors_seg["detractors"],
                        "revenue_at_risk_lakh": most_detractors_seg["revenue_at_risk_lakh"],
                    }
                    if most_detractors_seg
                    else None
                ),
                "most_money_at_risk_segment": (
                    {
                        "segment": highest_risk_seg["segment"],
                        "detractors": highest_risk_seg["detractors"],
                        "revenue_at_risk_lakh": highest_risk_seg["revenue_at_risk_lakh"],
                        "share_of_total_risk_pct": highest_risk_seg["share_of_total_risk_pct"],
                    }
                    if highest_risk_seg
                    else None
                ),
            },
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"get_revenue_at_risk failed: {exc}"})


@tool
def find_score_comment_mismatches() -> str:
    """Detect data-quality anomalies where a customer's numeric score contradicts their written comment.

    Specifically checks:
    1. Low scores (0-6, Detractor) paired with glowing positive praise (e.g., 'Amazing support', 'Excellent service', 'Best bank').
    2. High scores (9-10, Promoter) paired with severe negative complaints.
    Also computes the alternative NPS if mismatched rows are excluded or treated as inverted scores (9-10).

    Returns:
        JSON string listing mismatched responses, affected revenue in ₹ lakh, and alternative NPS calculations.
    """
    try:
        df = load_survey_df()
        total_n = len(df)
        base_promoters = int((df["score"] >= PROMOTER_MIN_SCORE).sum())
        base_detractors = int((df["score"] < PASSIVE_MIN_SCORE).sum())
        reported_nps = round((base_promoters - base_detractors) / total_n * 100.0, 1)

        low_score_positive = []
        high_score_negative = []

        for _, row in df.dropna(subset=["comment"]).iterrows():
            comment_lower = str(row["comment"]).lower()
            score = int(row["score"])
            rev_inr = int(row["annual_revenue_inr"])
            rev_lakh = round(rev_inr / LAKH_INR, 2)

            if score <= 6 and any(pat in comment_lower for pat in POSITIVE_PRAISE_PATTERNS):
                low_score_positive.append(
                    {
                        "response_id": str(row["response_id"]),
                        "date": str(row["date"]),
                        "month": str(row["month"]),
                        "product": str(row["product"]),
                        "channel": str(row["channel"]),
                        "tenure": str(row["tenure"]),
                        "score": score,
                        "annual_revenue_inr": rev_inr,
                        "annual_revenue_lakh": rev_lakh,
                        "false_detractor_risk_lakh": round(rev_lakh * CHURN_RATES["detractor"], 2),
                        "comment": str(row["comment"]),
                        "issue": "Detractor score (0-1) with glowing positive comment — likely scale inversion (thought 0/1 meant #1/best).",
                    }
                )
            elif score >= 9 and any(pat in comment_lower for pat in NEGATIVE_COMPLAINT_PATTERNS):
                high_score_negative.append(
                    {
                        "response_id": str(row["response_id"]),
                        "date": str(row["date"]),
                        "month": str(row["month"]),
                        "product": str(row["product"]),
                        "channel": str(row["channel"]),
                        "tenure": str(row["tenure"]),
                        "score": score,
                        "annual_revenue_inr": rev_inr,
                        "annual_revenue_lakh": rev_lakh,
                        "comment": str(row["comment"]),
                        "issue": "Promoter score (9-10) with negative complaint.",
                    }
                )

        k_inverted = len(low_score_positive)
        # Alternative 1: Exclude the inverted responses from the calculation
        rem_n = total_n - k_inverted
        nps_if_excluded = (
            round((base_promoters - (base_detractors - k_inverted)) / rem_n * 100.0, 1)
            if rem_n > 0
            else reported_nps
        )
        # Alternative 2: Treat inverted responses as Promoters (score 9-10)
        nps_if_flipped_to_promoter = round(
            ((base_promoters + k_inverted) - (base_detractors - k_inverted)) / total_n * 100.0,
            1,
        )

        mismatched_rev_lakh = round(
            sum(item["annual_revenue_inr"] for item in low_score_positive) / LAKH_INR, 2
        )
        false_risk_if_excluded_lakh = round(
            mismatched_rev_lakh * CHURN_RATES["detractor"], 2
        )
        false_risk_if_promoter_lakh = round(
            mismatched_rev_lakh * (CHURN_RATES["detractor"] - CHURN_RATES["promoter"]), 2
        )

        # Channel concentration of mismatches
        channel_counts: dict[str, int] = {}
        product_counts: dict[str, int] = {}
        for item in low_score_positive:
            channel_counts[item["channel"]] = channel_counts.get(item["channel"], 0) + 1
            product_counts[item["product"]] = product_counts.get(item["product"], 0) + 1

        payload = {
            "mismatch_count": k_inverted + len(high_score_negative),
            "low_score_positive_comment_count": k_inverted,
            "high_score_negative_comment_count": len(high_score_negative),
            "channel_breakdown_of_mismatches": channel_counts,
            "product_breakdown_of_mismatches": product_counts,
            "nps_impact": {
                "reported_nps": reported_nps,
                "reported_nps_formatted": f"{reported_nps:+.1f}",
                "nps_if_mismatches_excluded": nps_if_excluded,
                "nps_if_mismatches_excluded_formatted": f"{nps_if_excluded:+.1f}",
                "nps_if_reclassified_as_promoters": nps_if_flipped_to_promoter,
                "nps_if_reclassified_as_promoters_formatted": f"{nps_if_flipped_to_promoter:+.1f}",
                "point_difference_if_promoter": round(nps_if_flipped_to_promoter - reported_nps, 1),
            },
            "revenue_impact": {
                "mismatched_customers_annual_revenue_lakh": mismatched_rev_lakh,
                "overstated_detractor_risk_lakh_if_excluded": false_risk_if_excluded_lakh,
                "overstated_risk_lakh_if_promoter": false_risk_if_promoter_lakh,
            },
            "house_rule": "Never silently alter reported scores. Report official NPS (+18.5) and state the alternative NPS (+20.3 if excluded, +21.5 if treated as promoters) in DATA CAVEATS.",
            "mismatched_responses": low_score_positive + high_score_negative,
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"find_score_comment_mismatches failed: {exc}"})


@tool
def get_callback_list(limit: int = 10, exclude_mismatches: bool = True) -> str:
    """Return the priority callback list of highest-revenue detractors to phone back this week.

    Args:
        limit: Number of priority detractors to return (1 to 25). Defaults to 10.
        exclude_mismatches: Whether to exclude false detractors whose comments are glowing praise. Defaults to True.

    Returns:
        JSON string containing the ranked detractor callback list with response_id, product, channel, score, revenue, and comment.
    """
    try:
        df = load_survey_df()
        safe_limit = max(1, min(int(limit or 10), 25))
        det = df[df["bucket"] == "detractor"].copy()

        # Identify positive-comment mismatches so RMs don't make awkward apology calls to happy customers
        def _is_positive_mismatch(comment_val: Any) -> bool:
            if pd.isna(comment_val):
                return False
            c_low = str(comment_val).lower()
            return any(pat in c_low for pat in POSITIVE_PRAISE_PATTERNS)

        det["is_score_mismatch"] = det["comment"].apply(_is_positive_mismatch)
        excluded_ids = det.loc[det["is_score_mismatch"], "response_id"].astype(str).tolist()

        if exclude_mismatches:
            det_filtered = det[~det["is_score_mismatch"]].copy()
        else:
            det_filtered = det.copy()

        # Sort by annual_revenue_inr descending, then score ascending (most unhappy first)
        det_filtered.sort_values(
            by=["annual_revenue_inr", "score", "response_id"],
            ascending=[False, True, True],
            inplace=True,
        )

        top_rows = det_filtered.head(safe_limit)
        callbacks = []
        for rank, (_, row) in enumerate(top_rows.iterrows(), start=1):
            rev_inr = int(row["annual_revenue_inr"])
            rev_lakh = round(rev_inr / LAKH_INR, 2)
            risk_lakh = round(float(row["expected_loss_inr"]) / LAKH_INR, 2)
            comment_text = (
                str(row["comment"])
                if pd.notna(row["comment"]) and str(row["comment"]).strip()
                else "(No written comment provided — high-value detractor score)"
            )
            callbacks.append(
                {
                    "rank": rank,
                    "response_id": str(row["response_id"]),
                    "date": str(row["date"]),
                    "month": str(row["month"]),
                    "product": str(row["product"]),
                    "channel": str(row["channel"]),
                    "tenure": str(row["tenure"]),
                    "score": int(row["score"]),
                    "annual_revenue_inr": rev_inr,
                    "annual_revenue_lakh": rev_lakh,
                    "revenue_at_risk_lakh": risk_lakh,
                    "comment": comment_text,
                }
            )

        top_rev_lakh = round(sum(c["annual_revenue_inr"] for c in callbacks) / LAKH_INR, 2)
        top_risk_lakh = round(sum(c["revenue_at_risk_lakh"] for c in callbacks), 2)

        payload = {
            "callback_count": len(callbacks),
            "exclude_mismatches": exclude_mismatches,
            "excluded_mismatch_response_ids": excluded_ids if exclude_mismatches else [],
            "excluded_mismatch_note": (
                "Excluded 9 score-comment mismatch rows (e.g., R0191, R0262 who wrote 'Amazing support' with score 0) from apology calls; verify their scores separately."
                if exclude_mismatches
                else "Included all detractor rows."
            ),
            "total_annual_revenue_in_callback_list_lakh": top_rev_lakh,
            "total_revenue_at_risk_in_callback_list_lakh": top_risk_lakh,
            "callbacks": callbacks,
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"get_callback_list failed: {exc}"})

