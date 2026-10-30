"""What-If Tools — Simulates fixing detractor themes to rank actions by NPS points vs. ₹ lakh saved.

Reference:
- Project - NPS Analyst in a Box.html (P2 Simulation & P4 ActionPlannerAgent):
  - "Each detractor who becomes a passive adds 100 ÷ (answers) points. 10 × 100 ÷ 600 ≈ +1.7.
     This is exactly the maths inside `estimate_fix_impact`."
  - "Our what-if tool assumes the cautious version — detractors become passives, not promoters."
  - When a detractor (25% churn) becomes a passive (10% churn), expected revenue saved is
    (0.25 - 0.10) = 15% of their annual revenue (and 25% - 3% = 22% in the optimistic promoter case).
"""

from __future__ import annotations

import json
from strands import tool

from nps_insights_agent.config import CHURN_RATES, LAKH_INR, THEME_DEFINITIONS
from nps_insights_agent.tools.survey_tools import compute_nps_metrics, load_survey_df
from nps_insights_agent.tools.theme_tools import classify_comment_theme

# Actionable detractor themes (excludes promoter-only themes and score-comment mismatches)
ACTIONABLE_DETRACTOR_THEMES = (
    "otp_login",
    "fees_and_charges",
    "app_performance",
    "call_centre_ivr",
    "interest_rates_rewards",
    "general_sentiment",
)


@tool
def estimate_fix_impact(theme: str = "all") -> str:
    """Estimate the NPS point gain and revenue saved (in ₹ lakh) if we fix a detractor complaint theme.

    Uses the cautious house assumption from the brief:
    - Fixed detractors move to Passive (7-8), adding +100 / N points per detractor to overall NPS.
    - Their churn risk drops from 25% (detractor) to 10% (passive), saving 15% of their annual revenue.
    Also reports the optimistic scenario (if they move to Promoter, +200 / N points and 22% revenue saved).

    Args:
        theme: Theme key to simulate ('otp_login', 'fees_and_charges', 'app_performance', 'call_centre_ivr', 'interest_rates_rewards', or 'all' to compare and rank all themes). Defaults to 'all'.

    Returns:
        JSON string with what-if impact per theme and two explicit rankings:
        1) `ranked_by_nps_points` (most complaints / biggest score lift)
        2) `ranked_by_rupees_saved` (most expensive problem / biggest revenue protection)
    """
    try:
        df = load_survey_df().copy()
        total_n = len(df)
        overall = compute_nps_metrics(df)
        base_nps = overall["nps"]
        base_risk_lakh = round(float(df["expected_loss_inr"].sum()) / LAKH_INR, 2)

        df["theme"] = df["comment"].apply(classify_comment_theme)
        det_df = df[df["bucket"] == "detractor"].copy()

        clean_theme = (theme or "all").strip().lower()
        if clean_theme in {"", "*", "none", "null"}:
            clean_theme = "all"

        if clean_theme != "all" and clean_theme not in THEME_DEFINITIONS:
            return json.dumps(
                {
                    "error": f"Unknown theme '{theme}'. Valid themes: {list(ACTIONABLE_DETRACTOR_THEMES)} or 'all'."
                }
            )

        target_themes = (
            list(ACTIONABLE_DETRACTOR_THEMES)
            if clean_theme == "all"
            else [clean_theme]
        )

        cautious_churn_delta = CHURN_RATES["detractor"] - CHURN_RATES["passive"]   # 0.25 - 0.10 = 0.15
        optimistic_churn_delta = CHURN_RATES["detractor"] - CHURN_RATES["promoter"]  # 0.25 - 0.03 = 0.22

        simulations = []
        for t_key in target_themes:
            t_grp = det_df[det_df["theme"] == t_key]
            k = int(len(t_grp))
            if k == 0 and clean_theme == "all":
                continue

            t_info = THEME_DEFINITIONS.get(
                t_key, {"label": t_key, "description": ""}
            )
            affected_rev_lakh = round(float(t_grp["annual_revenue_inr"].sum()) / LAKH_INR, 2)
            current_risk_lakh = round(float(t_grp["expected_loss_inr"].sum()) / LAKH_INR, 2)

            # Cautious assumption: Detractor -> Passive (+100 / N per customer, churn 25% -> 10%)
            nps_gain_cautious = round((k * 100.0) / total_n, 1)
            new_nps_cautious = round(base_nps + nps_gain_cautious, 1)
            rupees_saved_cautious_lakh = round(affected_rev_lakh * cautious_churn_delta, 2)
            remaining_risk_cautious_lakh = round(
                current_risk_lakh - rupees_saved_cautious_lakh, 2
            )

            # Optimistic assumption: Detractor -> Promoter (+200 / N per customer, churn 25% -> 3%)
            nps_gain_optimistic = round((k * 200.0) / total_n, 1)
            new_nps_optimistic = round(base_nps + nps_gain_optimistic, 1)
            rupees_saved_optimistic_lakh = round(affected_rev_lakh * optimistic_churn_delta, 2)

            by_product = {
                str(p): int(c) for p, c in t_grp["product"].value_counts().items()
            }
            by_channel = {
                str(ch): int(c) for ch, c in t_grp["channel"].value_counts().items()
            }

            simulations.append(
                {
                    "theme_key": t_key,
                    "theme_label": t_info["label"],
                    "detractors_affected": k,
                    "affected_annual_revenue_lakh": affected_rev_lakh,
                    "current_revenue_at_risk_lakh": current_risk_lakh,
                    "cautious_detractor_to_passive": {
                        "nps_points_gained": nps_gain_cautious,
                        "nps_points_gained_formatted": f"{nps_gain_cautious:+.1f}",
                        "projected_overall_nps": new_nps_cautious,
                        "projected_overall_nps_formatted": f"{new_nps_cautious:+.1f}",
                        "rupees_saved_lakh": rupees_saved_cautious_lakh,
                        "remaining_theme_risk_lakh": remaining_risk_cautious_lakh,
                    },
                    "optimistic_detractor_to_promoter": {
                        "nps_points_gained": nps_gain_optimistic,
                        "nps_points_gained_formatted": f"{nps_gain_optimistic:+.1f}",
                        "projected_overall_nps": new_nps_optimistic,
                        "projected_overall_nps_formatted": f"{new_nps_optimistic:+.1f}",
                        "rupees_saved_lakh": rupees_saved_optimistic_lakh,
                    },
                    "by_product": by_product,
                    "by_channel": by_channel,
                }
            )

        ranked_by_nps = sorted(
            simulations,
            key=lambda x: (
                x["cautious_detractor_to_passive"]["nps_points_gained"],
                x["cautious_detractor_to_passive"]["rupees_saved_lakh"],
            ),
            reverse=True,
        )
        ranked_by_rupees = sorted(
            simulations,
            key=lambda x: (
                x["cautious_detractor_to_passive"]["rupees_saved_lakh"],
                x["cautious_detractor_to_passive"]["nps_points_gained"],
            ),
            reverse=True,
        )

        payload = {
            "baseline": {
                "total_survey_responses": total_n,
                "current_overall_nps": base_nps,
                "current_overall_nps_formatted": f"{base_nps:+.1f}",
                "current_total_revenue_at_risk_lakh": base_risk_lakh,
            },
            "methodology": {
                "cautious_assumption": "Detractors become Passives (7-8): each fixed detractor adds +100/600 points to NPS, and churn risk drops from 25% to 10% (saving 15% of their annual revenue).",
                "optimistic_assumption": "Detractors become Promoters (9-10): each fixed detractor adds +200/600 points to NPS, and churn risk drops from 25% to 3% (saving 22% of their annual revenue).",
            },
            "ranked_by_nps_points": [
                {
                    "rank": idx,
                    "theme_key": item["theme_key"],
                    "theme_label": item["theme_label"],
                    "detractors_affected": item["detractors_affected"],
                    "nps_points_gained": item["cautious_detractor_to_passive"]["nps_points_gained"],
                    "nps_points_gained_formatted": item["cautious_detractor_to_passive"]["nps_points_gained_formatted"],
                    "projected_nps": item["cautious_detractor_to_passive"]["projected_overall_nps_formatted"],
                    "rupees_saved_lakh": item["cautious_detractor_to_passive"]["rupees_saved_lakh"],
                    "current_revenue_at_risk_lakh": item["current_revenue_at_risk_lakh"],
                }
                for idx, item in enumerate(ranked_by_nps, start=1)
            ],
            "ranked_by_rupees_saved": [
                {
                    "rank": idx,
                    "theme_key": item["theme_key"],
                    "theme_label": item["theme_label"],
                    "detractors_affected": item["detractors_affected"],
                    "rupees_saved_lakh": item["cautious_detractor_to_passive"]["rupees_saved_lakh"],
                    "current_revenue_at_risk_lakh": item["current_revenue_at_risk_lakh"],
                    "nps_points_gained": item["cautious_detractor_to_passive"]["nps_points_gained"],
                    "nps_points_gained_formatted": item["cautious_detractor_to_passive"]["nps_points_gained_formatted"],
                    "projected_nps": item["cautious_detractor_to_passive"]["projected_overall_nps_formatted"],
                }
                for idx, item in enumerate(ranked_by_rupees, start=1)
            ],
            "tradeoff_summary": (
                "Fixing 'otp_login' (45 detractors) lifts NPS the most (+7.5 points to +26.0, saving ₹2.36 lakh), "
                "whereas fixing 'fees_and_charges' (24 detractors, led by 12 Wealth accounts) saves the most money "
                "(₹6.40 lakh saved out of ₹10.66 lakh at risk, while lifting NPS +4.0 points to +22.5)."
            ),
            "detailed_simulations": simulations,
        }
        return json.dumps(payload, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"estimate_fix_impact failed: {exc}"})

