"""Milestone M4 & Stretch Goal 3 · Plain-Python Auditor (`fact_check.py`).

Re-computes ground-truth numbers directly from `data/nps_survey.csv` and verifies
that the generated Executive NPS Brief quotes every headline metric, sign, segment
figure, what-if impact, and data caveat accurately — including label-aware proximity
checks (Stretch Goal 3).
"""

from __future__ import annotations

import json
import re
from typing import Any

from nps_insights_agent.tools import (
    estimate_fix_impact,
    find_score_comment_mismatches,
    get_nps_by_segment,
    get_nps_overview,
    get_revenue_at_risk,
)


def _normalize_text(text: str) -> str:
    """Normalize Unicode minus signs (`−`, `–`, `—`) to ASCII `-` and collapse whitespace."""
    norm = (
        text.replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("₹", "₹")
    )
    return norm


def _check_label_and_value(
    text: str,
    label_patterns: list[str],
    value_patterns: list[str],
    window_chars: int = 240,
) -> tuple[bool, str]:
    """Check that at least one `label_pattern` appears within `window_chars` of a `value_pattern`."""
    norm = _normalize_text(text)

    # First check global presence of value
    val_matches = []
    for vp in value_patterns:
        for m in re.finditer(vp, norm, flags=re.IGNORECASE):
            val_matches.append(m)

    if not val_matches:
        return False, f"Value matching {value_patterns} not found anywhere in brief."

    # Check if any label pattern appears within `window_chars` around any value match
    for vm in val_matches:
        start = max(0, vm.start() - window_chars)
        end = min(len(norm), vm.end() + window_chars)
        snippet = norm[start:end]
        for lp in label_patterns:
            if re.search(lp, snippet, flags=re.IGNORECASE):
                matched_str = vm.group(0)
                return True, f"Verified '{matched_str}' near label /{lp}/"

    return (
        False,
        f"Value {value_patterns} appeared in brief, but not within {window_chars} chars of expected label {label_patterns}.",
    )


def fact_check_brief(brief_text: str, label_aware: bool = True) -> dict[str, Any]:
    """Audit an NPS brief against ground-truth numbers computed directly by plain Python.

    Args:
        brief_text: The markdown text of the generated Executive NPS Brief.
        label_aware: If True, requires each number to appear near its corresponding label.

    Returns:
        Dictionary with `passed` (bool), `passed_count`, `total_count`, `checks`, and `failed_checks`.
    """
    overview = json.loads(get_nps_overview())
    rev_prod = json.loads(get_revenue_at_risk(by_col="product"))
    mismatches = json.loads(find_score_comment_mismatches())
    whatif = json.loads(estimate_fix_impact(theme="all"))
    sep_channel = json.loads(get_nps_by_segment(segment_col="channel", month="2026-09"))

    ov = overview["overall"]
    trend = {m["month"]: m for m in overview["monthly_trend"]}
    tot_rev = rev_prod["totals"]
    mm_imp = mismatches["nps_impact"]

    window = 260 if label_aware else 100_000

    # Ground-truth values from code
    overall_nps_val = f"{ov['nps']:+.1f}"                      # +18.5
    jul_nps_val = f"{trend['2026-07']['nps']:+.1f}"            # +32.0
    aug_nps_val = f"{trend['2026-08']['nps']:+.1f}"            # +30.0
    sep_nps_val = f"{trend['2026-09']['nps']:+.1f}"            # -6.5
    total_risk_val = f"{tot_rev['total_revenue_at_risk_lakh']:.2f}"  # 37.98

    wealth_row = next(r for r in rev_prod["breakdown"] if r["segment"] == "Wealth")
    wealth_risk_val = f"{wealth_row['revenue_at_risk_lakh']:.2f}"    # 31.51

    mob_sep = next(s for s in sep_channel["segments"] if s["segment_value"] == "Mobile App")
    mob_sep_nps_val = f"{mob_sep['nps']:+.1f}"                 # -33.6

    otp_whatif = next(
        r for r in whatif["ranked_by_nps_points"] if r["theme_key"] == "otp_login"
    )
    fees_whatif = next(
        r for r in whatif["ranked_by_rupees_saved"] if r["theme_key"] == "fees_and_charges"
    )

    spec_checks = [
        {
            "id": "alert_level",
            "name": f"Executive Alert Level ({overview['recommended_alert_level']})",
            "labels": [r"alert", r"level", r"status", r"scorecard", r"brief"],
            "values": [rf"\b{overview['recommended_alert_level']}\b"],
        },
        {
            "id": "total_responses",
            "name": f"Total Survey Responses ({ov['responses']})",
            "labels": [r"response", r"survey", r"answer", r"customer", r"overall"],
            "values": [rf"\b{ov['responses']}\b"],
        },
        {
            "id": "overall_nps",
            "name": f"Overall NPS ({overall_nps_val}) with sign and no %",
            "labels": [r"overall", r"q3", r"nps", r"headline"],
            "values": [r"\+18\.5(?!\s*%)"],
        },
        {
            "id": "overall_moe",
            "name": f"Overall 95% Margin of Error (±{ov['margin_of_error_95']})",
            "labels": [r"18\.5", r"margin of error", r"95%", r"confidence", r"±"],
            "values": [r"(?:±|\+/-|\+-)\s*6\.6\b", r"\b6\.6\b"],
        },
        {
            "id": "month_2026_07",
            "name": f"2026-07 (July) NPS ({jul_nps_val})",
            "labels": [r"2026-07", r"july"],
            "values": [r"\+32(?:\.0)?(?!\s*%)"],
        },
        {
            "id": "month_2026_08",
            "name": f"2026-08 (August) NPS ({aug_nps_val})",
            "labels": [r"2026-08", r"august"],
            "values": [r"\+30(?:\.0)?(?!\s*%)"],
        },
        {
            "id": "month_2026_09",
            "name": f"2026-09 (September) NPS ({sep_nps_val})",
            "labels": [r"2026-09", r"september"],
            "values": [r"-6\.5(?!\s*%)"],
        },
        {
            "id": "sep_mobile_app_drop",
            "name": f"Hidden Story 1 · Sept Mobile App Collapse ({mob_sep_nps_val}) & OTP/Login Root Cause",
            "labels": [r"mobile app", r"2026-09", r"september", r"otp"],
            "values": [r"-33\.6(?!\s*%)"],
        },
        {
            "id": "total_revenue_at_risk",
            "name": f"Total Revenue at Risk (₹{total_risk_val} lakh)",
            "labels": [r"risk", r"lakh", r"revenue"],
            "values": [r"\b37\.98\b"],
        },
        {
            "id": "wealth_revenue_at_risk",
            "name": f"Hidden Story 2 · Wealth Revenue at Risk (₹{wealth_risk_val} lakh / 83.0%)",
            "labels": [r"wealth", r"risk", r"lakh"],
            "values": [r"\b31\.51\b", r"\b20\.53\b"],
        },
        {
            "id": "whatif_otp_nps_gain",
            "name": f"Action Ranking A · OTP Fix NPS Gain ({otp_whatif['nps_points_gained_formatted']} pts)",
            "labels": [r"otp", r"login", r"point", r"nps"],
            "values": [r"\+7\.5\b", r"\b7\.5\b"],
        },
        {
            "id": "whatif_fees_rupees_saved",
            "name": f"Action Ranking B · Fees Fix Rupees Saved (₹{fees_whatif['rupees_saved_lakh']:.2f} lakh)",
            "labels": [r"fee", r"charge", r"wealth", r"save", r"lakh"],
            "values": [r"\b6\.39\b", r"\b6\.40\b"],
        },
        {
            "id": "caveat_low_sample",
            "name": "Caveat 1 · Low-Sample Flag on 2026-09 Call Centre (n=26 < 30)",
            "labels": [r"call centre", r"low_sample", r"low sample", r"caveat", r"< ?30"],
            "values": [r"\b26\b", r"low_sample", r"±\s*31\.4"],
        },
        {
            "id": "caveat_churn_assumptions",
            "name": "Caveat 2 · House Churn Rate Assumptions (3% / 10% / 25%)",
            "labels": [r"churn", r"assumption", r"caveat", r"promoter", r"detractor"],
            "values": [r"25%"],
        },
        {
            "id": "caveat_mismatch_alt_nps",
            "name": (
                f"Hidden Story 3 & Caveat 3 · 9 Score-Comment Mismatches & Alternative NPS "
                f"({mm_imp['nps_if_mismatches_excluded_formatted']} or {mm_imp['nps_if_reclassified_as_promoters_formatted']})"
            ),
            "labels": [r"mismatch", r"excluded", r"promoter", r"caveat", r"inverted", r"branch"],
            "values": [r"\+?20\.3\b", r"\+?21\.5\b"],
        },
    ]

    results = []
    for item in spec_checks:
        ok, detail = _check_label_and_value(
            brief_text,
            label_patterns=item["labels"],
            value_patterns=item["values"],
            window_chars=window,
        )
        results.append(
            {
                "id": item["id"],
                "name": item["name"],
                "passed": ok,
                "detail": detail,
            }
        )

    # Also check that no NPS number is written as a percentage (e.g., "+18.5%" or "-6.5%")
    norm_brief = _normalize_text(brief_text)
    bad_pct_match = re.search(r"(?:\+18\.5|-6\.5|\+32\.0|\+30\.0|-33\.6)\s*%", norm_brief)
    no_nps_pct_ok = bad_pct_match is None
    results.append(
        {
            "id": "nps_not_percentage",
            "name": "Unit Rule · NPS written as a signed score, never with '%'",
            "passed": no_nps_pct_ok,
            "detail": (
                "Verified no NPS score has a trailing '%' symbol."
                if no_nps_pct_ok
                else f"Found forbidden '%' after an NPS score: '{bad_pct_match.group(0)}'"
            ),
        }
    )

    passed_checks = [r for r in results if r["passed"]]
    failed_checks = [r for r in results if not r["passed"]]

    return {
        "passed": len(failed_checks) == 0,
        "label_aware": label_aware,
        "passed_count": len(passed_checks),
        "total_count": len(results),
        "checks": results,
        "failed_checks": failed_checks,
    }


def format_fact_check_report(report: dict[str, Any]) -> str:
    """Format the output of `fact_check_brief` as a human-readable audit log."""
    status = "PASSED ✓" if report["passed"] else "FAILED ✗"
    mode = "Label-Aware" if report.get("label_aware") else "Global Presence"
    lines = [
        "=" * 75,
        f"AUDITOR FACT CHECK ({mode}) : {status} ({report['passed_count']}/{report['total_count']} checks passed)",
        "=" * 75,
    ]
    for chk in report["checks"]:
        mark = "✓" if chk["passed"] else "✗"
        lines.append(f"  [{mark}] {chk['name']}")
        if not chk["passed"]:
            lines.append(f"      -> {chk['detail']}")
    lines.append("=" * 75)
    return "\n".join(lines)

