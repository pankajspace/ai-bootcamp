"""Unified Test Runner for NPS Analyst in a Box (Milestones M0–M4 & Stretch Goals).

Mirrors `projects/01-fundamental-analysis/test_financial_agent.py` so every layer can be
verified independently or end-to-end:

Usage:
    python projects/02-nps-analyst/test_nps_agent.py --tools       # Milestone M1: All 7 tools
    python projects/02-nps-analyst/test_nps_agent.py --score       # Milestone M2: ScoreAnalystAgent
    python projects/02-nps-analyst/test_nps_agent.py --voc         # VoiceOfCustomerAgent
    python projects/02-nps-analyst/test_nps_agent.py --churn       # ChurnRiskAgent
    python projects/02-nps-analyst/test_nps_agent.py --planner     # ActionPlannerAgent
    python projects/02-nps-analyst/test_nps_agent.py --writer      # ReportWriterAgent + Fact Check
    python projects/02-nps-analyst/test_nps_agent.py --parallel    # Milestone M3: Phase 1 parallel trace
    python projects/02-nps-analyst/test_nps_agent.py --supervisor  # Full 3-phase pipeline + Fact Check
    python projects/02-nps-analyst/test_nps_agent.py --fact-check  # Milestone M4: Auditor unit tests
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from nps_insights_agent.agents import (
    action_planner_agent,
    churn_risk_agent,
    report_writer_agent,
    score_analyst_agent,
    voice_of_customer_agent,
)
from nps_insights_agent.config import get_model_description
from nps_insights_agent.fact_check import fact_check_brief, format_fact_check_report
from nps_insights_agent.main import run_with_guardrail
from nps_insights_agent.tools import _compute_nps_by_segment_cached, load_survey_df
from try_tools import main as run_try_tools


def test_tools() -> None:
    """Milestone M1: Test all 7 deterministic tools directly."""
    run_try_tools()


def test_score_agent() -> str:
    """Milestone M2: Test ScoreAnalystAgent in isolation."""
    print(f"\n{'=' * 75}")
    print("STEP 2: Testing ScoreAnalystAgent ('How bad is it?')")
    print(f"{'=' * 75}")
    prompt = (
        "Compute the overall Q3 2026 NPS scorecard, monthly trend (2026-07 to 2026-09), "
        "segment slices (product, channel, tenure), and drill down into 2026-09 by channel and product."
    )
    t0 = time.perf_counter()
    resp = str(score_analyst_agent(prompt)).strip()
    elapsed = time.perf_counter() - t0
    print(resp)
    print("-" * 75)
    print(f"✓ ScoreAnalystAgent completed in {elapsed:.2f}s")
    return resp


def test_voc_agent() -> str:
    """Test VoiceOfCustomerAgent in isolation."""
    print(f"\n{'=' * 75}")
    print("STEP 3: Testing VoiceOfCustomerAgent ('Why did it happen?')")
    print(f"{'=' * 75}")
    prompt = (
        "Analyze customer comments across detractors (overall and 2026-09), passives, and promoters. "
        "Identify the root cause of the September drop and include verbatim customer quotes."
    )
    t0 = time.perf_counter()
    resp = str(voice_of_customer_agent(prompt)).strip()
    elapsed = time.perf_counter() - t0
    print(resp)
    print("-" * 75)
    print(f"✓ VoiceOfCustomerAgent completed in {elapsed:.2f}s")
    return resp


def test_churn_agent() -> str:
    """Test ChurnRiskAgent ('How much money is at risk? Can we trust the scores?') in isolation."""
    print(f"\n{'=' * 75}")
    print("STEP 4: Testing ChurnRiskAgent ('The Sceptic · Revenue at Risk & Mismatches')")
    print(f"{'=' * 75}")
    prompt = (
        "Quantify expected revenue at risk in ₹ lakh by product and channel, explain where the money "
        "at risk sits, and audit the survey for score-comment mismatches."
    )
    t0 = time.perf_counter()
    resp = str(churn_risk_agent(prompt)).strip()
    elapsed = time.perf_counter() - t0
    print(resp)
    print("-" * 75)
    print(f"✓ ChurnRiskAgent completed in {elapsed:.2f}s")
    return resp


def test_planner_agent() -> str:
    """Test ActionPlannerAgent ('What do we fix first, and who do we call back?') in isolation."""
    print(f"\n{'=' * 75}")
    print("STEP 5: Testing ActionPlannerAgent ('What-if Dual Ranking & Callbacks')")
    print(f"{'=' * 75}")
    prompt = (
        "Context: Overall NPS is +18.5 (dropped from +32.0 in July to -6.5 in September due to 45 otp_login "
        "complaints; Wealth has ₹31.51 lakh revenue at risk driven by 24 fees_and_charges complaints). "
        "Run `estimate_fix_impact(theme='all')` and `get_callback_list(limit=10, exclude_mismatches=True)` "
        "to rank fixes both ways (NPS points vs. ₹ lakh saved) and list who to call back this week."
    )
    t0 = time.perf_counter()
    resp = str(action_planner_agent(prompt)).strip()
    elapsed = time.perf_counter() - t0
    print(resp)
    print("-" * 75)
    print(f"✓ ActionPlannerAgent completed in {elapsed:.2f}s")
    return resp


def test_writer_agent() -> str:
    """Test ReportWriterAgent ('One page for the CEO') + Fact Check in isolation."""
    print(f"\n{'=' * 75}")
    print("STEP 6: Testing ReportWriterAgent (Synthesis Only) + Fact Check")
    print(f"{'=' * 75}")
    prompt = """Synthesize the four specialist findings below into the definitive one-page Executive NPS Brief for the CEO:
1. ScoreAnalystAgent: Overall NPS +18.5 (±6.6, NEEDS WORK) on 600 responses (536 comments, 268 promoters 44.7%, 175 passives 29.2%, 157 detractors 26.2%). Monthly trend: 2026-07 +32.0 (±10.6), 2026-08 +30.0 (±10.9), 2026-09 -6.5 (±11.8). By product: Savings Account +23.1, Credit Card +20.5, Wealth +1.0. By channel: Branch +33.0, Mobile App +12.3, Call Centre +10.2. In 2026-09: Mobile App collapsed to -33.6 (n=113), Branch +34.4 (n=61), Call Centre +15.4 (n=26, low_sample < 30, MOE ±31.4).
2. VoiceOfCustomerAgent: Top detractor themes: otp_login (45 comments, 42 in 2026-09, ₹3.94L risk), fees_and_charges (24 comments, ₹10.66L risk), app_performance (21 comments, ₹0.74L risk), call_centre_ivr (18 comments, ₹1.68L risk), general_sentiment (12), interest_rates_rewards (10), positive_mismatch (9).
3. ChurnRiskAgent: Total revenue ₹304.43 lakh; Total revenue at risk ₹37.98 lakh (12.5%, HIGH risk verdict; Detractors ₹24.54 lakh, Passives ₹10.36 lakh, Promoters ₹3.08 lakh) under 3%/10%/25% churn assumptions. Wealth holds ₹31.51 lakh of total risk (83.0%, and ₹20.53 lakh detractor risk) across 31 detractors, vs Credit Card ₹3.75 lakh and Savings Account ₹2.73 lakh. Data quality audit: 9 score-comment mismatches (8 in Branch, 1 in Call Centre, including Wealth R0191 ₹3.48L and R0262 ₹3.03L) gave 0-1 with glowing praise; excluding them lifts NPS to +20.3, reclassifying as promoters lifts NPS to +21.5 and cuts overstated risk by ₹1.84 lakh.
4. ActionPlannerAgent: Cautious what-if (Detractor -> Passive): Ranking A by NPS points: #1 otp_login (+7.5 pts to +26.0, saves ₹2.36 lakh), #2 fees_and_charges (+4.0 pts to +22.5, saves ₹6.39 lakh), #3 app_performance (+3.5 pts, saves ₹0.45 lakh), #4 call_centre_ivr (+3.0 pts, saves ₹1.01 lakh). Ranking B by Rupees Saved: #1 fees_and_charges (₹6.39 lakh saved), #2 otp_login (₹2.36 lakh saved), #3 call_centre_ivr (₹1.01 lakh saved). Top callbacks (excluding mismatches): R0314 (Wealth, Score 6, ₹5.45L), R0182 (Wealth, Score 3, ₹5.04L), R0087 (Wealth, Score 4, ₹5.01L), R0364 (Wealth, Score 4, ₹4.79L), R0070 (Wealth, Score 3, ₹4.55L), R0471 (Wealth, Score 4, ₹4.49L), R0479 (Wealth, Score 5, ₹3.41L), R0457 (Wealth, Score 5, ₹3.24L)."""

    t0 = time.perf_counter()
    brief = str(report_writer_agent(prompt)).strip()
    elapsed = time.perf_counter() - t0
    print(brief)
    print("-" * 75)
    print(f"✓ ReportWriterAgent completed in {elapsed:.2f}s")

    audit = fact_check_brief(brief, label_aware=True)
    print(format_fact_check_report(audit))
    return brief


async def _run_parallel_phase1_async() -> None:
    """Benchmark Phase 1 (3 concurrent specialists) and verify trace ordering."""
    print(f"\n{'=' * 75}")
    print("PARALLEL EXECUTION: Phase ① (Three Concurrent Specialist Calls at Once)")
    print(f"{'=' * 75}")
    t_start = time.perf_counter()
    trace_events: list[str] = []

    async def _invoke(agent_obj, name: str, prompt: str) -> str:
        t_call = time.perf_counter() - t_start
        line_call = f"[{t_call:6.2f}s] CALL   -> {name}"
        trace_events.append(line_call)
        print(line_call)
        res = await asyncio.to_thread(agent_obj, prompt)
        t_out = time.perf_counter() - t_start
        line_out = f"[{t_out:6.2f}s] OUTPUT <- {name} ({len(str(res))} chars)"
        trace_events.append(line_out)
        print(line_out)
        return str(res)

    results = await asyncio.gather(
        _invoke(
            score_analyst_agent,
            "ScoreAnalystAgent",
            "Compute overall NPS, monthly trend, segment breakdowns, and 2026-09 drill-down.",
        ),
        _invoke(
            voice_of_customer_agent,
            "VoiceOfCustomerAgent",
            "Analyze comment themes for detractors, passives, and promoters with quotes.",
        ),
        _invoke(
            churn_risk_agent,
            "ChurnRiskAgent",
            "Quantify revenue at risk in ₹ lakh and find score-comment mismatches.",
        ),
    )
    wall_time = time.perf_counter() - t_start
    # Verify all 3 CALL lines appeared before the first OUTPUT line
    first_three_are_calls = all("CALL" in ev for ev in trace_events[:3])
    print("-" * 75)
    print(f"⚡ All 3 Phase 1 specialists completed concurrently in {wall_time:.2f}s")
    print(f"✓ Trace verified 3 CALLs before any OUTPUT: {first_three_are_calls}")
    assert first_three_are_calls, "Expected all 3 CALL events before any OUTPUT event!"
    _ = results


def test_parallel() -> None:
    asyncio.run(_run_parallel_phase1_async())


def test_fact_check_unit() -> None:
    """Milestone M4: Unit test `fact_check.py` on both a valid brief and a tampered brief."""
    print(f"\n{'=' * 75}")
    print("MILESTONE M4 · FACT CHECKER UNIT TESTS (Valid vs. Tampered Brief)")
    print(f"{'=' * 75}")

    sample_valid_brief = """
    # Future with Shivank Bank — Q3 2026 Executive NPS Brief
    Alert Level: RED | Overall Q3 2026 NPS: +18.5 (±6.6 at 95% confidence) across 600 responses.
    Monthly trend: 2026-07 (July) was +32.0, 2026-08 (August) was +30.0, and 2026-09 (September) fell to -6.5.
    Hidden Story 1: In 2026-09, Mobile App collapsed to -33.6 due to 45 otp_login complaints after the app update.
    Hidden Story 2: Total revenue at risk is ₹37.98 lakh (out of ₹304.43 lakh), and Wealth holds ₹31.51 lakh of risk (₹20.53 lakh detractor risk).
    Hidden Story 3: 9 score-comment mismatches in Branch/Call Centre; excluding them gives +20.3 and reclassifying as promoters gives +21.5.
    Action Plan: Fixing otp_login gains +7.5 NPS points; fixing fees_and_charges saves ₹6.39 lakh.
    Data Caveats:
    1. Call Centre in 2026-09 had n=26 (<30, low_sample, ±31.4).
    2. Churn rate assumptions are 3% promoter, 10% passive, and 25% detractor.
    3. Alternative NPS is +20.3 (if excluded) or +21.5 (if promoters).
    """
    valid_report = fact_check_brief(sample_valid_brief, label_aware=True)
    print(format_fact_check_report(valid_report))
    assert valid_report["passed"], "Valid brief should pass all 16 checks!"

    tampered_brief = sample_valid_brief.replace("+18.5", "+18.5%").replace("37.98", "99.99")
    tampered_report = fact_check_brief(tampered_brief, label_aware=True)
    assert not tampered_report["passed"], "Tampered brief must fail fact check!"
    print(
        f"✓ Tampered brief rightly caught by auditor ({len(tampered_report['failed_checks'])} failed checks: "
        f"{[c['id'] for c in tampered_report['failed_checks']]})"
    )


def test_supervisor() -> None:
    """Milestone M3 & M4: Full end-to-end 3-phase run with trace and guardrail fact check."""
    print(f"\n{'=' * 75}")
    print("FULL END-TO-END PIPELINE (3 Phases + Trace + Fact-Check Guardrail)")
    print(f"{'=' * 75}")
    res = run_with_guardrail(
        user_query="Analyze Future with Shivank Bank's Q3 2026 NPS survey and produce the executive brief for the CEO.",
        trace=True,
        verbose=False,
        stream=False,
        max_retries=2,
    )
    print("\n" + "=" * 75)
    print("FINAL CEO EXECUTIVE NPS BRIEF:")
    print("=" * 75)
    print(res["brief"])
    print("\n" + format_fact_check_report(res["fact_check"]))
    assert res["fact_check"]["passed"], "End-to-end brief must pass fact check!"


def test_cache_stats() -> None:
    print(f"\n{'=' * 75}")
    print("SHARED TOOL CACHE STATS (* in architecture diagram)")
    print(f"{'=' * 75}")
    df_info = load_survey_df.cache_info()
    seg_info = _compute_nps_by_segment_cached.cache_info()
    print(f"Survey CSV Cache       : hits={df_info.hits}, misses={df_info.misses}, currsize={df_info.currsize}")
    print(f"Segment Slice Cache (*): hits={seg_info.hits}, misses={seg_info.misses}, currsize={seg_info.currsize}")


def main() -> None:
    args = [a.lower() for a in sys.argv[1:]]
    mode = args[0] if args else "all"

    print("\n" + "#" * 75)
    print(" NPS ANALYST IN A BOX — UNIFIED TEST SUITE")
    print(f" Model: {get_model_description()} | Mode: {mode}")
    print("#" * 75)

    if mode in {"all", "--tools"}:
        test_tools()
    if mode in {"all", "--fact-check"}:
        test_fact_check_unit()
    if mode in {"--score"}:
        test_score_agent()
    if mode in {"--voc"}:
        test_voc_agent()
    if mode in {"--churn"}:
        test_churn_agent()
    if mode in {"--planner"}:
        test_planner_agent()
    if mode in {"--writer"}:
        test_writer_agent()
    if mode in {"--parallel"}:
        test_parallel()
    if mode in {"all", "--supervisor"}:
        test_supervisor()

    test_cache_stats()
    print("\n" + "#" * 75)
    print(" ALL REQUESTED NPS ANALYST TESTS COMPLETED SUCCESSFULLY")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()

