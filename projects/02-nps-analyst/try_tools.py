"""Milestone M1 · Try Every Tool Without an LLM.

Calls every tool in `nps_insights_agent.tools`, prints its structured summary,
verifies exact agreement with `nps_by_hand.py`, and confirms that invalid inputs
return JSON error payloads instead of crashing.

Run:
    python projects/02-nps-analyst/try_tools.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from nps_by_hand import compute_nps_stats
from nps_insights_agent.tools import (
    _compute_nps_by_segment_cached,
    estimate_fix_impact,
    find_score_comment_mismatches,
    get_callback_list,
    get_comment_themes,
    get_nps_by_segment,
    get_nps_overview,
    get_revenue_at_risk,
    load_survey_df,
)


def main() -> None:
    print("=" * 75)
    print("MILESTONE M1 · TESTING ALL 7 NPS TOOLS (No LLM Required)")
    print("=" * 75)

    # 1. get_nps_overview
    print("\n1. [Tool] get_nps_overview()")
    overview = json.loads(get_nps_overview())
    ov = overview["overall"]
    print(
        f"   Overall NPS   : {ov['nps_formatted']} (±{ov['margin_of_error_95']}) "
        f"| Verdict: {ov['health_verdict']} | Alert: {overview['recommended_alert_level']}"
    )
    print(
        f"   Buckets       : {ov['promoters']} Promoters ({ov['promoter_pct']}%), "
        f"{ov['passives']} Passives ({ov['passive_pct']}%), "
        f"{ov['detractors']} Detractors ({ov['detractor_pct']}%)"
    )
    for m in overview["monthly_trend"]:
        print(
            f"   Month {m['month']} : {m['nps_formatted']} (±{m['margin_of_error_95']}) "
            f"[n={m['responses']}, P={m['promoters']}, Pa={m['passives']}, D={m['detractors']}]"
        )

    # Cross-check with nps_by_hand.py
    hand_stats = compute_nps_stats(load_survey_df())
    assert ov["nps"] == hand_stats["nps"] == 18.5, "NPS mismatch with nps_by_hand.py!"
    assert ov["margin_of_error_95"] == hand_stats["moe_95"] == 6.6, "MOE mismatch!"
    print("   ✓ Verified exact agreement with nps_by_hand.py (+18.5 ±6.6)")

    # 2. get_nps_by_segment (* shared & cached)
    print("\n2. [Tool] get_nps_by_segment(segment_col, month) [* shared & cached]")
    for col in ("product", "channel", "tenure"):
        seg_res = json.loads(get_nps_by_segment(segment_col=col))
        best = seg_res["best_valid_segment"]
        worst = seg_res["worst_valid_segment"]
        print(
            f"   By {col:8s} -> Best: {best['segment_value']} ({best['nps_formatted']}, n={best['responses']}) | "
            f"Worst: {worst['segment_value']} ({worst['nps_formatted']}, n={worst['responses']})"
        )

    sep_ch = json.loads(get_nps_by_segment(segment_col="channel", month="2026-09"))
    print("   2026-09 Drill-Down by Channel:")
    for s in sep_ch["segments"]:
        low_tag = " [LOW_SAMPLE <30]" if s["low_sample"] else ""
        print(
            f"     - {s['segment_value']:12s}: {s['nps_formatted']} (±{s['margin_of_error_95']}, n={s['responses']}){low_tag}"
        )
    if sep_ch["low_sample_warnings"]:
        print(f"     ⚠️  {sep_ch['low_sample_warnings'][0]}")

    # 3. get_comment_themes
    print("\n3. [Tool] get_comment_themes(bucket='detractor')")
    det_themes = json.loads(get_comment_themes(bucket="detractor"))
    print(
        f"   Detractor slice: {det_themes['total_responses_in_slice']} responses "
        f"({det_themes['written_comments_count']} written comments, {det_themes['blank_comments_count']} blank)"
    )
    for t in det_themes["themes"]:
        print(
            f"   - {t['theme_key']:23s}: {t['comment_count']:2d} comments ({t['share_of_commented_pct']:4.1f}%) | "
            f"Rev at Risk: ₹{t['revenue_at_risk_lakh']:5.2f}L | {t['theme_label']}"
        )

    # 4. get_revenue_at_risk
    print("\n4. [Tool] get_revenue_at_risk(by_col='product')")
    rev_risk = json.loads(get_revenue_at_risk(by_col="product"))
    tot = rev_risk["totals"]
    print(
        f"   Total Revenue : ₹{tot['total_annual_revenue_lakh']:.2f} lakh | "
        f"Total Risk: ₹{tot['total_revenue_at_risk_lakh']:.2f} lakh ({tot['risk_as_pct_of_total_revenue']}%) | "
        f"Verdict: {tot['risk_verdict']}"
    )
    for item in rev_risk["breakdown"]:
        print(
            f"   - {item['segment']:16s}: Total Risk ₹{item['revenue_at_risk_lakh']:6.2f}L "
            f"({item['share_of_total_risk_pct']:4.1f}% of risk) | "
            f"Detractors: {item['detractors']:2d} (Detractor Risk ₹{item['detractor_revenue_at_risk_lakh']:5.2f}L)"
        )

    # 5. find_score_comment_mismatches
    print("\n5. [Tool] find_score_comment_mismatches()")
    mm = json.loads(find_score_comment_mismatches())
    imp = mm["nps_impact"]
    print(
        f"   Mismatches Found : {mm['mismatch_count']} responses "
        f"(Channel breakdown: {mm['channel_breakdown_of_mismatches']})"
    )
    print(
        f"   NPS Impact       : Reported {imp['reported_nps_formatted']} -> "
        f"Excluded {imp['nps_if_mismatches_excluded_formatted']} -> "
        f"If Promoters {imp['nps_if_reclassified_as_promoters_formatted']}"
    )
    print(
        f"   Affected Revenue : ₹{mm['revenue_impact']['mismatched_customers_annual_revenue_lakh']:.2f} lakh "
        f"(Overstated detractor risk: ₹{mm['revenue_impact']['overstated_detractor_risk_lakh_if_excluded']:.2f} lakh)"
    )

    # 6. estimate_fix_impact
    print("\n6. [Tool] estimate_fix_impact(theme='all')")
    whatif = json.loads(estimate_fix_impact(theme="all"))
    print("   Ranking A — By NPS Points Gained (Cautious: Detractor -> Passive):")
    for r in whatif["ranked_by_nps_points"][:4]:
        print(
            f"     #{r['rank']} {r['theme_key']:23s}: {r['nps_points_gained_formatted']} pts "
            f"(new NPS {r['projected_nps']}) | Saves ₹{r['rupees_saved_lakh']:.2f}L ({r['detractors_affected']} detractors)"
        )
    print("   Ranking B — By Rupees Saved (Cautious: 25% -> 10% Churn):")
    for r in whatif["ranked_by_rupees_saved"][:4]:
        print(
            f"     #{r['rank']} {r['theme_key']:23s}: Saves ₹{r['rupees_saved_lakh']:.2f}L "
            f"(out of ₹{r['current_revenue_at_risk_lakh']:.2f}L risk) | {r['nps_points_gained_formatted']} NPS pts ({r['detractors_affected']} detractors)"
        )

    # 7. get_callback_list
    print("\n7. [Tool] get_callback_list(limit=8)")
    cb = json.loads(get_callback_list(limit=8))
    print(
        f"   Top {cb['callback_count']} Genuine Detractors to Call This Week "
        f"(Total Rev: ₹{cb['total_annual_revenue_in_callback_list_lakh']:.2f}L, "
        f"Risk: ₹{cb['total_revenue_at_risk_in_callback_list_lakh']:.2f}L):"
    )
    for row in cb["callbacks"]:
        print(
            f"   #{row['rank']} {row['response_id']} | {row['product']:15s} | Score {row['score']} | "
            f"Rev ₹{row['annual_revenue_lakh']:5.2f}L (Risk ₹{row['revenue_at_risk_lakh']:4.2f}L) | \"{row['comment'][:55]}\""
        )

    # 8. Defensive error handling check (no crashes on bad inputs)
    print("\n8. [Defensive Check] Verifying bad inputs return JSON errors without crashing:")
    bad_seg = json.loads(get_nps_by_segment(segment_col="invalid_col"))
    bad_theme = json.loads(estimate_fix_impact(theme="nonexistent_theme"))
    assert "error" in bad_seg and "error" in bad_theme
    print(f"   ✓ Invalid segment_col -> {bad_seg['error']}")
    print(f"   ✓ Invalid theme       -> {bad_theme['error']}")
    print(f"   ✓ Segment cache stats -> {_compute_nps_by_segment_cached.cache_info()}")
    print("=" * 75)


if __name__ == "__main__":
    main()

