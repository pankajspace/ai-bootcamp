"""Milestone M0 · NPS by Hand (Plain Pandas Baseline, No LLM).

Computes Future with Shivank Bank's Q3 2026 Net Promoter Score (NPS),
95% margin of error, monthly trend (July to September 2026), segment slices,
revenue at risk in ₹ lakh, and score-comment mismatches.

Run:
    python projects/02-nps-analyst/nps_by_hand.py
"""

from __future__ import annotations

import math
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "nps_survey.csv"

CHURN_RATES = {
    "promoter": 0.03,
    "passive": 0.10,
    "detractor": 0.25,
}


def classify_bucket(score: int | float) -> str:
    """Map 0-10 score to promoter (9-10), passive (7-8), or detractor (0-6)."""
    if score >= 9:
        return "promoter"
    if score >= 7:
        return "passive"
    return "detractor"


def compute_nps_stats(df: pd.DataFrame) -> dict:
    """Compute NPS, bucket counts/shares, and 95% margin of error."""
    n = len(df)
    if n == 0:
        return {"n": 0, "nps": 0.0, "moe_95": 0.0}
    promoters = int((df["score"] >= 9).sum())
    passives = int(((df["score"] >= 7) & (df["score"] <= 8)).sum())
    detractors = int((df["score"] <= 6).sum())

    p_share = promoters / n
    pa_share = passives / n
    d_share = detractors / n
    nps = (p_share - d_share) * 100.0

    # Variance of (+1, 0, -1) variable: E[X^2] - (E[X])^2 = (p + d) - (p - d)^2
    variance = max(0.0, (p_share + d_share) - (p_share - d_share) ** 2)
    moe_95 = 1.96 * math.sqrt(variance / n) * 100.0

    return {
        "n": n,
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "promoter_pct": round(p_share * 100, 1),
        "passive_pct": round(pa_share * 100, 1),
        "detractor_pct": round(d_share * 100, 1),
        "nps": round(nps, 1),
        "moe_95": round(moe_95, 1),
        "low_sample": n < 30,
    }


def main(csv_path: Path = DATA_PATH) -> None:
    df = pd.read_csv(csv_path)
    df["bucket"] = df["score"].apply(classify_bucket)
    df["churn_prob"] = df["bucket"].map(CHURN_RATES)
    df["revenue_at_risk_inr"] = df["annual_revenue_inr"] * df["churn_prob"]

    overall = compute_nps_stats(df)

    print("=" * 72)
    print("MILESTONE M0 · NPS BY HAND (Plain Pandas Baseline)")
    print("=" * 72)
    print(f"Survey File     : {csv_path}")
    print(f"Total Responses : {overall['n']} ({df['comment'].notna().sum()} written comments)")
    print(
        f"Buckets         : {overall['promoters']} Promoters ({overall['promoter_pct']}%) | "
        f"{overall['passives']} Passives ({overall['passive_pct']}%) | "
        f"{overall['detractors']} Detractors ({overall['detractor_pct']}%)"
    )
    print(f"Overall NPS     : {overall['nps']:+.1f} (±{overall['moe_95']:.1f} at 95% confidence)")

    print("\n--- Monthly Trend (July – September 2026) ---")
    for month, grp in df.groupby("month"):
        st = compute_nps_stats(grp)
        print(
            f"  {month}: NPS {st['nps']:+6.1f} (±{st['moe_95']:4.1f}) | "
            f"n={st['n']:3d} (P={st['promoters']:3d}, Pa={st['passives']:2d}, D={st['detractors']:2d})"
        )

    for seg_col in ["product", "channel", "tenure"]:
        print(f"\n--- NPS by {seg_col.upper()} ---")
        for seg_val, grp in df.groupby(seg_col):
            st = compute_nps_stats(grp)
            flag = " [LOW SAMPLE <30]" if st["low_sample"] else ""
            print(
                f"  {seg_val:18s}: NPS {st['nps']:+6.1f} (±{st['moe_95']:4.1f}) | "
                f"n={st['n']:3d} (P={st['promoters']:3d}, Pa={st['passives']:2d}, D={st['detractors']:2d}){flag}"
            )

    print("\n--- September (2026-09) Drill-Down by Channel ---")
    sep_df = df[df["month"] == "2026-09"]
    for ch_val, grp in sep_df.groupby("channel"):
        st = compute_nps_stats(grp)
        flag = " [LOW SAMPLE <30]" if st["low_sample"] else ""
        print(
            f"  {ch_val:18s}: NPS {st['nps']:+6.1f} (±{st['moe_95']:4.1f}) | "
            f"n={st['n']:3d} (P={st['promoters']:2d}, Pa={st['passives']:2d}, D={st['detractors']:2d}){flag}"
        )

    print("\n--- Expected Revenue at Risk (in ₹ Lakh, 1 Lakh = ₹1,00,000) ---")
    total_rev_lakh = df["annual_revenue_inr"].sum() / 1e5
    total_risk_lakh = df["revenue_at_risk_inr"].sum() / 1e5
    det_risk_lakh = df.loc[df["bucket"] == "detractor", "revenue_at_risk_inr"].sum() / 1e5
    print(f"  Total Annual Revenue       : ₹{total_rev_lakh:.2f} lakh")
    print(f"  Total Revenue at Risk      : ₹{total_risk_lakh:.2f} lakh (Detractors alone: ₹{det_risk_lakh:.2f} lakh)")
    for prod, grp in df.groupby("product"):
        p_rev = grp["annual_revenue_inr"].sum() / 1e5
        p_risk = grp["revenue_at_risk_inr"].sum() / 1e5
        p_det_risk = grp.loc[grp["bucket"] == "detractor", "revenue_at_risk_inr"].sum() / 1e5
        print(
            f"  {prod:18s}: Total Rev ₹{p_rev:6.2f}L | "
            f"At Risk ₹{p_risk:5.2f}L (Detractor Risk ₹{p_det_risk:5.2f}L)"
        )
    print("=" * 72)


if __name__ == "__main__":
    main()

