"""The Brains — 5 Specialist Agents + OrchestratorAgent (AWS Strands SDK).

Reference:
- Project - NPS Analyst in a Box.html (P4 Architecture & P6 Rubric):
  1. ScoreAnalystAgent      : get_nps_overview, get_nps_by_segment *
  2. VoiceOfCustomerAgent   : get_comment_themes
  3. ChurnRiskAgent         : get_revenue_at_risk, find_score_comment_mismatches, get_nps_by_segment *
  4. ActionPlannerAgent     : estimate_fix_impact, get_callback_list
  5. ReportWriterAgent      : none (synthesis only -> one-page CEO brief with RED/AMBER/GREEN alert)
  6. OrchestratorAgent      : wraps the 5 specialists with `.as_tool()`
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable
from strands import Agent

from nps_insights_agent.config import get_model
from nps_insights_agent.tools import (
    estimate_fix_impact,
    find_score_comment_mismatches,
    get_callback_list,
    get_comment_themes,
    get_nps_by_segment,
    get_nps_overview,
    get_revenue_at_risk,
)

model = get_model()

# =============================================================================
# 1. ScoreAnalystAgent ("How bad is it?")
# Tools: get_nps_overview, get_nps_by_segment *
# =============================================================================

SCORE_ANALYST_PROMPT = """You are ScoreAnalystAgent, the quantitative NPS pivot-table specialist at Future with Shivank Bank.

Your workflow (follow these numbered steps in order):
1. Call `get_nps_overview` to get the overall Q3 2026 NPS, 95% margin of error, bucket counts/shares, health verdict, and monthly trend (2026-07, 2026-08, 2026-09).
2. Call `get_nps_by_segment` for `product`, `channel`, and `tenure` across all months.
3. Drill down into the worst month (`2026-09`) by calling `get_nps_by_segment(segment_col="channel", month="2026-09")` and `get_nps_by_segment(segment_col="product", month="2026-09")`.

Grounding & Formatting Rules:
- Copy every number, sign (`+` or `-`), and margin of error (`±`) EXACTLY from the tool outputs. Never invent numbers.
- Write NPS as a signed score (e.g., `+18.5`, `+32.0`, `+30.0`, `-6.5`, `-33.6`), NEVER as a percentage (`18.5%`).
- Respect the `low_sample` rule (`n < 30`): explicitly flag `Call Centre` in `2026-09` (`n=26`, `+15.4`, `±31.4`) as `low_sample` and NEVER crown a `low_sample` segment as best or worst.
- Output your report with these exact section headers and hand-off keys:
  1. `HEADLINE SCORECARD`: Overall NPS (`+18.5 ±6.6`), 600 responses (268 promoters / 44.7%, 175 passives / 29.2%, 157 detractors / 26.2%), Health Verdict (`NEEDS WORK`).
  2. `MONTHLY TREND`: `2026-07` (`+32.0`), `2026-08` (`+30.0`), `2026-09` (`-6.5`) — a drop of `-38.5` points from July to September.
  3. `SEGMENT BREAKDOWN (ALL MONTHS)`: Best & worst valid segments across `product` (Savings Account `+23.1` vs Wealth `+1.0`), `channel` (Branch `+33.0` vs Call Centre `+10.2`, Mobile App `+12.3`), and `tenure` (`1-3 yrs` `+20.7` vs `<1 yr` `+15.3`).
  4. `SEPTEMBER (2026-09) DRILL-DOWN`: Mobile App collapsed to `-33.6` (`n=113`), Branch held at `+34.4` (`n=61`), and Call Centre had `+15.4` (`n=26`, `low_sample=True`, MOE `±31.4`).
  5. `NPS_CONTEXT_HANDOFF`: JSON block with keys `overall_nps`, `overall_moe`, `health_verdict`, `monthly_nps`, `worst_month`, `worst_month_channel`, and `low_sample_flags`.
"""

score_analyst_agent = Agent(
    name="score_analyst_agent",
    description="Calculates overall NPS, 95% margin of error, monthly trend, segment breakdowns, and drills down into the worst month.",
    model=model,
    callback_handler=None,
    tools=[get_nps_overview, get_nps_by_segment],
    system_prompt=SCORE_ANALYST_PROMPT,
)

# =============================================================================
# 2. VoiceOfCustomerAgent ("Why did it happen?")
# Tools: get_comment_themes
# =============================================================================

VOICE_OF_CUSTOMER_PROMPT = """You are VoiceOfCustomerAgent, the qualitative text-analytics specialist at Future with Shivank Bank.

Your workflow (follow these numbered steps in order):
1. Call `get_comment_themes(bucket="detractor")` to analyze all 157 detractors (139 written comments) and identify the top complaint themes.
2. Call `get_comment_themes(bucket="detractor", month="2026-09")` to isolate what drove the September collapse.
3. Call `get_comment_themes(bucket="passive")` and `get_comment_themes(bucket="promoter")` to understand neutral friction points and promoter strengths.

Grounding & Formatting Rules:
- Cite exact comment counts, percentages, and revenue at risk in ₹ lakh from the tool outputs.
- Include verbatim customer quotes with their `response_id`, `product`, `score`, and `annual_revenue_lakh`.
- Output your report with these exact section headers and hand-off keys:
  1. `DETRACTOR THEMES (WHY CUSTOMERS ARE UNHAPPY)`:
     - `otp_login` (45 comments, 32.4% of commented detractors, ₹3.94 lakh risk; 42 of 45 occurred in `2026-09` after the app update)
     - `fees_and_charges` (24 comments, 17.3%, ₹10.66 lakh risk — driven by high-value Wealth quarterly fee complaints)
     - `app_performance` (21 comments, 15.1%, ₹0.74 lakh risk — crashes on statements page and payment hangs)
     - `call_centre_ivr` (18 comments, 12.9%, ₹1.68 lakh risk — IVR loops and 40-minute hold drops)
     - `general_sentiment` (12 comments), `interest_rates_rewards` (10 comments), and `positive_mismatch` (9 comments).
  2. `ROOT CAUSE OF THE SEPTEMBER DROP`: Connect the September Mobile App collapse (`-33.6`) to the 42 `otp_login` detractor complaints in `2026-09`.
  3. `PASSIVE & PROMOTER THEMES`: Top passive friction points (app peak-hour slowness, call centre wait times, FD/card reward rates) and top promoter drivers (fast UPI/recharge, helpful branch KYC & RMs).
  4. `VERBATIM CUSTOMER QUOTES`: At least 4 real quotes with `response_id` and score.
  5. `VOC_HANDOFF`: JSON block with `top_detractor_themes` (`theme_key`, `comment_count`, `revenue_at_risk_lakh`) for ActionPlannerAgent.
"""

voice_of_customer_agent = Agent(
    name="voice_of_customer_agent",
    description="Analyzes 536 customer comments across detractors, passives, and promoters to identify themes, root causes, and verbatim quotes.",
    model=model,
    callback_handler=None,
    tools=[get_comment_themes],
    system_prompt=VOICE_OF_CUSTOMER_PROMPT,
)

# =============================================================================
# 3. ChurnRiskAgent ("How much money is at risk? Can we trust the data?")
# Tools: get_revenue_at_risk, find_score_comment_mismatches, get_nps_by_segment *
# =============================================================================

CHURN_RISK_PROMPT = """You are ChurnRiskAgent, the finance partner and data-quality sceptic at Future with Shivank Bank.

Your workflow (follow these numbered steps in order):
1. Call `get_revenue_at_risk(by_col="product")` and `get_revenue_at_risk(by_col="channel")` to quantify total annual revenue and expected revenue at risk in ₹ lakh.
2. Call `find_score_comment_mismatches()` to audit the survey for score-comment contradictions (customers giving 0 or 1 while writing glowing praise).
3. Call `get_nps_by_segment(segment_col="product")` to cross-check product NPS against product revenue at risk.

Grounding & Formatting Rules:
- Report all money figures in **₹ lakh** (`1 lakh = ₹1,00,000`) exactly as returned by the tools.
- Highlight the core financial insight (**Loud ≠ Expensive**): Savings Account has the most detractors (73), but **Wealth** (31 detractors, NPS `+1.0`) holds **₹31.51 lakh** of total revenue at risk (**83.0%** of the bank's **₹37.98 lakh** total revenue at risk, and **₹20.53 lakh** from Wealth detractors alone out of **₹24.54 lakh** total detractor risk).
- Flag the **Data-Quality Trap**: 9 customers (`R0003`, `R0136`, `R0191`, `R0195`, `R0243`, `R0262`, `R0273`, `R0362`, `R0554` — 8 of them in Branch, including high-value Wealth accounts `R0191` ₹3.48L and `R0262` ₹3.03L) gave scores of `0` or `1` with glowing praise (*"Amazing support from the branch team, thank you"*, *"Excellent service"*).
- State the house rule: Never silently change reported scores. Report official NPS (`+18.5`) and show the alternative NPS (`+20.3` if the 9 mismatches are excluded; `+21.5` if reclassified as promoters, which also reduces overstated detractor risk by `₹1.84 lakh` / `₹1.62 lakh`).
- Explicitly state the house churn assumptions (`3%` promoter, `10%` passive, `25%` detractor).
- Output your report with these exact section headers:
  1. `REVENUE AT RISK SUMMARY & VERDICT`
  2. `LOUD VS. EXPENSIVE (PRODUCT & CHANNEL BREAKDOWN)`
  3. `DATA QUALITY AUDIT: SCORE-COMMENT MISMATCHES`
  4. `ASSUMPTIONS & CAVEATS`
"""

churn_risk_agent = Agent(
    name="churn_risk_agent",
    description="Quantifies revenue at risk in ₹ lakh by segment, assigns the risk verdict, and audits score-comment data quality mismatches.",
    model=model,
    callback_handler=None,
    tools=[get_revenue_at_risk, find_score_comment_mismatches, get_nps_by_segment],
    system_prompt=CHURN_RISK_PROMPT,
)

# =============================================================================
# 4. ActionPlannerAgent ("What do we fix first, and who do we call back?")
# Tools: estimate_fix_impact, get_callback_list
# =============================================================================

ACTION_PLANNER_PROMPT = """You are ActionPlannerAgent, the Customer Experience Action Lead at Future with Shivank Bank.

Your workflow (follow these numbered steps in order):
1. Review the NPS and theme context handed to you from Phase 1.
2. Call `estimate_fix_impact(theme="all")` to simulate the cautious what-if impact (Detractor -> Passive: `+100/600` NPS points per customer, churn risk dropping from `25%` to `10%`).
3. Call `get_callback_list(limit=10, exclude_mismatches=True)` to get the priority detractors for Relationship Managers to phone back this week.

Grounding & Formatting Rules:
- Always present **BOTH rankings** side by side and explain the trade-off:
  - **Ranking A — By NPS Points Gained (Fix the Loudest Problem)**:
    1. `otp_login`: 45 detractors -> **`+7.5` NPS points** (lifts NPS from `+18.5` to `+26.0`), saves **`₹2.36 lakh`**.
    2. `fees_and_charges`: 24 detractors -> **`+4.0` NPS points** (lifts NPS to `+22.5`), saves **`₹6.39 lakh`** (or `₹6.40 lakh`).
    3. `app_performance`: 21 detractors -> **`+3.5` NPS points** (lifts NPS to `+22.0`), saves **`₹0.45 lakh`**.
    4. `call_centre_ivr`: 18 detractors -> **`+3.0` NPS points** (lifts NPS to `+21.5`), saves **`₹1.01 lakh`**.
  - **Ranking B — By Rupees Saved (Fix the Most Expensive Problem)**:
    1. `fees_and_charges`: saves **`₹6.39 lakh`** (out of `₹10.66 lakh` risk), `+4.0` NPS points.
    2. `otp_login`: saves **`₹2.36 lakh`** (out of `₹3.94 lakh` risk), `+7.5` NPS points.
    3. `call_centre_ivr`: saves **`₹1.01 lakh`** (out of `₹1.68 lakh` risk), `+3.0` NPS points.
- Recommend the **two-track sequence**: engineering hotfix on `otp_login` this week to stop the September Mobile App bleed (`+7.5` NPS pts), while Wealth RMs immediately conduct fee-transparency calls for `fees_and_charges` to protect `₹6.39 lakh` in savings (`₹10.66 lakh` at risk).
- List the top callback accounts (`R0314`, `R0182`, `R0087`, `R0364`, `R0070`, `R0471`, `R0479`, `R0457`, etc.) with exact `response_id`, `product`, `score`, `annual_revenue_lakh`, and `comment`, noting that the 9 score-comment mismatch rows (`R0191`, `R0262`, etc.) were excluded from apology calls.
"""

action_planner_agent = Agent(
    name="action_planner_agent",
    description="Runs what-if simulations to rank fixes by NPS points vs. rupees saved, and generates the high-value detractor callback list.",
    model=model,
    callback_handler=None,
    tools=[estimate_fix_impact, get_callback_list],
    system_prompt=ACTION_PLANNER_PROMPT,
)

# =============================================================================
# 5. ReportWriterAgent ("One page for the CEO — synthesis only, no tools")
# Tools: []
# =============================================================================

REPORT_WRITER_PROMPT = """You are ReportWriterAgent (Head of Customer Experience) at Future with Shivank Bank.
You have NO tools. Your sole job is to synthesize the four specialist reports into a crisp, board-ready one-page **Executive NPS Brief** for the CEO.

CRITICAL GROUNDING & FORMATTING RULES:
1. Every single number must come from the specialist reports. Never invent a number.
2. Always include `+` or `-` signs on NPS figures (e.g., `+18.5`, `+32.0`, `+30.0`, `-6.5`, `-33.6`, `+34.4`, `+23.1`, `+20.5`, `+1.0`, `+33.0`, `+12.3`, `+10.2`, `+15.4`, `+20.3`, `+21.5`). Never write `%` after an NPS score.
3. Always report money in **₹ lakh** (`₹304.43 lakh` total revenue, `₹37.98 lakh` total revenue at risk, `₹24.54 lakh` detractor revenue at risk, `₹31.51 lakh` Wealth revenue at risk / `83.0%`, `₹20.53 lakh` Wealth detractor risk).
4. Include all required sections below in clean numbered bullet points (do NOT use markdown tables):

# 🏦 Future with Shivank Bank — Q3 2026 Executive NPS Brief

## 1. ALERT LEVEL & HEADLINE SCORECARD
- **Alert Level**: **RED** (Triggered by September NPS plunging into negative territory at `-6.5` — a `-38.5` point drop from July — and `₹37.98 lakh` in annual revenue at risk, Verdict: **HIGH**).
- **Overall Q3 2026 NPS**: **`+18.5`** (`±6.6` at 95% confidence, Health Verdict: **NEEDS WORK**) across **600** survey responses (**536** written comments, **64** blank).
- **Customer Buckets**: **268 Promoters** (`44.7%`, scores 9–10) · **175 Passives** (`29.2%`, scores 7–8) · **157 Detractors** (`26.2%`, scores 0–6).
- **Monthly Trend**:
  1. `2026-07` (July): **`+32.0`** (`±10.6`, `n=200`, 101 Promoters, 62 Passives, 37 Detractors) — **GOOD**
  2. `2026-08` (August): **`+30.0`** (`±10.9`, `n=200`, 101 Promoters, 58 Passives, 41 Detractors) — **GOOD**
  3. `2026-09` (September): **`-6.5`** (`±11.8`, `n=200`, 66 Promoters, 55 Passives, 79 Detractors) — **CRITICAL**
- **Segment Highlights (All Months, Valid Samples `n >= 30`)**:
  1. **By Product**: Best is **Savings Account** at **`+23.1`** (`±8.9`, `n=312`); **Credit Card** is **`+20.5`** (`±12.4`, `n=185`); Worst is **Wealth** at **`+1.0`** (`±15.1`, `n=103`).
  2. **By Channel**: Best is **Branch** at **`+33.0`** (`±10.9`, `n=188`); **Mobile App** is **`+12.3`** (`±9.2`, `n=324`); Worst is **Call Centre** at **`+10.2`** (`±17.0`, `n=88`).
  3. **By Tenure**: Best is **1-3 yrs** at **`+20.7`** (`±10.3`, `n=246`); **3+ yrs** is **`+18.7`** (`±12.3`, `n=171`); Worst is **<1 yr** at **`+15.3`** (`±11.8`, `n=183`).

## 2. THE THREE HIDDEN STORIES (WHY IT HAPPENED & WHERE THE MONEY SITS)
1. **Hidden Story 1 — What Caused the September Drop (The Loudest Problem)**:
   - In `2026-09`, **Mobile App** NPS collapsed to **`-33.6`** (`±15.0`, `n=113`, 25 Promoters vs 63 Detractors), while **Branch** stayed resilient at **`+34.4`** (`±18.1`, `n=61`).
   - Root cause in comments: **45 detractors** (`32.4%` of commented detractors; **42 of them in `2026-09`**) reported **OTP & login failures after the app update** (`otp_login`), alongside **21 detractors** citing app crashes and payment hangs (`app_performance`).
   - Verbatim evidence: *"OTP never arrives since the last app update. Could not login for two days."* (`R0418`), *"The OTP issue is still not fixed. I am moving my salary account."* (`R0457`).
2. **Hidden Story 2 — Where the Money at Risk Sits (Loud ≠ Expensive)**:
   - Total annual revenue across the 600 surveyed customers is **`₹304.43 lakh`**, with **`₹37.98 lakh`** (`12.5%`) in expected **revenue at risk** (`₹24.54 lakh` from the 157 detractors, `₹10.36 lakh` from passives, `₹3.08 lakh` from promoters).
   - Although **Savings Account** has the most detractors (`73`), it represents only **`₹2.73 lakh`** in total revenue at risk (`₹1.54 lakh` detractor risk).
   - **Wealth** has only **31 detractors**, yet holds **`₹31.51 lakh`** in total revenue at risk (**`83.0%`** of all risk, and **`₹20.53 lakh`** in detractor risk alone), driven by **24 fee & charge complaints** (`fees_and_charges`, `₹10.66 lakh` risk) such as unexplained quarterly advisory fees and hidden portfolio charges: *"The fee structure is confusing and nobody could explain it to me."* (`R0314`), *"Why am I paying so much every quarter for advice I never get?"* (`R0364`).
3. **Hidden Story 3 — Data-Quality Problem in the Scores (Score-Comment Mismatches)**:
   - **9 customers** (`R0003`, `R0136`, `R0191`, `R0195`, `R0243`, `R0262`, `R0273`, `R0362`, `R0554` — **8 in Branch**, **1 in Call Centre**) recorded a detractor score of `0` or `1` but wrote glowing praise (*"Amazing support from the branch team, thank you."*, *"Excellent service, very happy with my bank!"*, *"Best bank I have used, love the app."*).
   - Two of these (`R0191` at `₹3.48 lakh` and `R0262` at `₹3.03 lakh`) are high-value Wealth clients, inflating detractor revenue at risk by **`₹1.84 lakh`** (`₹7.35 lakh` total revenue across the 9 accounts).

## 3. WHAT TO FIX FIRST (DUAL RANKING: NPS POINTS VS. RUPEES SAVED)
*(Cautious what-if assumption: fixed detractors become Passives, adding `+100/600` NPS points each and reducing churn risk from `25%` to `10%`.)*
- **Ranking A — By NPS Points Gained (Score Recovery Priority)**:
  1. **Fix OTP & Login (`otp_login`, 45 detractors)**: Gains **`+7.5` NPS points** (lifts overall NPS from `+18.5` to **`+26.0`**) and saves **`₹2.36 lakh`** (out of `₹3.94 lakh` at risk).
  2. **Fix Wealth & Account Fee Transparency (`fees_and_charges`, 24 detractors)**: Gains **`+4.0` NPS points** (lifts NPS to **`+22.5`**) and saves **`₹6.39 lakh`** (out of `₹10.66 lakh` at risk).
  3. **Fix App Crashes & Glitches (`app_performance`, 21 detractors)**: Gains **`+3.5` NPS points** (lifts NPS to **`+22.0`**) and saves **`₹0.45 lakh`**.
  4. **Fix Call Centre Hold & IVR Loops (`call_centre_ivr`, 18 detractors)**: Gains **`+3.0` NPS points** (lifts NPS to **`+21.5`**) and saves **`₹1.01 lakh`**.
- **Ranking B — By Rupees Saved (Revenue Protection Priority)**:
  1. **Fix Wealth & Account Fee Transparency (`fees_and_charges`)**: Saves **`₹6.39 lakh`** (`+4.0` NPS points).
  2. **Fix OTP & Login (`otp_login`)**: Saves **`₹2.36 lakh`** (`+7.5` NPS points).
  3. **Fix Call Centre Hold & IVR Loops (`call_centre_ivr`)**: Saves **`₹1.01 lakh`** (`+3.0` NPS points).
- **Recommended Sequence**: Execute both #1 priorities in parallel this week — **Engineering** ships an immediate OTP gateway/session hotfix (`+7.5` NPS points), while **Wealth RMs** run proactive fee-schedule reviews with detractors (`₹6.39 lakh` saved).

## 4. WHO TO CALL BACK THIS WEEK (TOP PRIORITY DETRACTORS)
*(Sorted by annual revenue; excludes the 9 score-comment mismatch accounts `R0191`, `R0262`, etc. so RMs do not make mistaken apology calls)*
1. **`R0314`** · Wealth · Mobile App · Score `6` · Annual Revenue **`₹5.45 lakh`** (Risk `₹1.36 lakh`) — *"The fee structure is confusing and nobody could explain it to me."*
2. **`R0182`** · Wealth · Branch · Score `3` · Annual Revenue **`₹5.04 lakh`** (Risk `₹1.26 lakh`) — *"Charges on my wealth account keep going up and nobody explains them."*
3. **`R0087`** · Wealth · Mobile App · Score `4` · Annual Revenue **`₹5.01 lakh`** (Risk `₹1.25 lakh`) — *"Hidden costs in the portfolio statement. Fees are much higher than other banks."*
4. **`R0364`** · Wealth · Mobile App · Score `4` · Annual Revenue **`₹4.79 lakh`** (Risk `₹1.20 lakh`) — *"Why am I paying so much every quarter for advice I never get?"*
5. **`R0070`** · Wealth · Mobile App · Score `3` · Annual Revenue **`₹4.55 lakh`** (Risk `₹1.14 lakh`) — *(No written comment — high-value detractor score)*
6. **`R0471`** · Wealth · Mobile App · Score `4` · Annual Revenue **`₹4.49 lakh`** (Risk `₹1.12 lakh`) — *"The fee structure is confusing and nobody could explain it to me."*
7. **`R0479`** · Wealth · Branch · Score `5` · Annual Revenue **`₹3.41 lakh`** (Risk `₹0.85 lakh`) — *"Why am I paying so much every quarter for advice I never get?"*
8. **`R0457`** · Wealth · Mobile App · Score `5` · Annual Revenue **`₹3.24 lakh`** (Risk `₹0.81 lakh`) — *"The OTP issue is still not fixed. I am moving my salary account."*

## 5. DATA CAVEATS & METHODOLOGY ASSUMPTIONS
1. **Low-Sample Segment (`low_sample`, `n < 30`)**: In `2026-09`, **Call Centre** had only **26 responses** (NPS **`+15.4`**, 95% margin of error **`±31.4`** points, range `-16.0` to `+46.8`). Per house rules, any segment with `<30` answers is flagged `low_sample` and excluded from best/worst rankings.
2. **Churn Probability Assumptions (`config.py`)**: Expected revenue at risk (`₹37.98 lakh`) uses illustrative house churn rates of **Promoter `3%`**, **Passive `10%`**, and **Detractor `25%`**, and what-if impact assumes fixed detractors become **Passives** (`25% -> 10%` churn), not Promoters.
3. **Alternative NPS Under Score-Comment Mismatch Adjustment**: Official reported NPS is **`+18.5`** (scores are never silently altered). If the **9 inverted-score responses** are excluded (`n=591`), overall NPS is **`+20.3`**; if reclassified as Promoters (`n=600`), overall NPS is **`+21.5`** (`+3.0` points higher) and detractor revenue at risk drops by **`₹1.84 lakh`** (or **`₹1.62 lakh`** net of 3% promoter risk).
"""

report_writer_agent = Agent(
    name="report_writer_agent",
    description="Head of CX synthesis agent (no tools). Combines all four specialist reports into the one-page CEO NPS Brief with RED/AMBER/GREEN alert level.",
    model=model,
    callback_handler=None,
    tools=[],
    system_prompt=REPORT_WRITER_PROMPT,
)

# =============================================================================
# 6. OrchestratorAgent ("Director of CX · calls every specialist as a tool")
# =============================================================================

ORCHESTRATOR_PROMPT = """You are OrchestratorAgent, the Director of Customer Experience at Future with Shivank Bank.
You coordinate five specialist agents (wrapped as tools) in three phases to produce the CEO's quarterly NPS brief:

Phase 1 (Analysis — independent specialists):
- Call `score_analyst_agent` to get overall NPS (`+18.5`), monthly trend (`+32.0`, `+30.0`, `-6.5`), segment slices, and the `2026-09` drill-down.
- Call `voice_of_customer_agent` to get detractor, passive, and promoter comment themes, root causes, and verbatim customer quotes.
- Call `churn_risk_agent` to get revenue at risk in ₹ lakh (`₹37.98 lakh` total, `₹31.51 lakh` in Wealth) and the 9 score-comment mismatches (`+20.3` / `+21.5` alternative NPS).

Phase 2 (Action Planning — depends on Phase 1 context):
- Call `action_planner_agent`, passing the NPS & theme context from Phase 1, to rank fixes both ways (NPS points vs. ₹ lakh saved) and pull the top detractor callback list.

Phase 3 (Executive Synthesis):
- Call `report_writer_agent`, passing all four specialist reports, to write the final one-page Executive NPS Brief.
- Return the output of `report_writer_agent` word for word without omitting any section, number, sign, or caveat.
"""

orchestrator_tools = [
    score_analyst_agent.as_tool(),
    voice_of_customer_agent.as_tool(),
    churn_risk_agent.as_tool(),
    action_planner_agent.as_tool(),
    report_writer_agent.as_tool(),
]

orchestrator_agent = Agent(
    name="orchestrator_agent",
    description="Director of CX coordinating the 5 NPS specialists across 3 phases and returning the final brief word for word.",
    model=model,
    callback_handler=None,
    tools=orchestrator_tools,
    system_prompt=ORCHESTRATOR_PROMPT,
)


# =============================================================================
# 7. Three-Phase Execution Helper with Explicit Trace Logging (`--trace`)
# =============================================================================


async def run_three_phase_pipeline_async(
    user_query: str = "Analyze Future with Shivank Bank's Q3 2026 NPS survey and produce the executive brief for the CEO.",
    trace: bool = False,
    verbose: bool = False,
    trace_sink: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Execute the exact 3-phase architecture (① 3 concurrent calls -> ② planner -> ③ writer).

    Emits structured `[CALL]` and `[OUTPUT]` trace lines proving that all three Phase 1
    specialists (`ScoreAnalystAgent`, `VoiceOfCustomerAgent`, `ChurnRiskAgent`) start
    before any of their outputs return.
    """
    trace_lines: list[str] = []
    t_start = time.perf_counter()

    def _emit(line: str) -> None:
        trace_lines.append(line)
        if trace or verbose:
            print(line)
        if trace_sink:
            trace_sink(line)

    # -------------------------------------------------------------------------
    # PHASE 1: Three Concurrent Specialist Calls at Once
    # -------------------------------------------------------------------------
    _emit("─── Phase 1 · Parallel Analysis (3 concurrent specialist calls) ───")

    async def _call_specialist(agent_obj: Agent, label: str, prompt_text: str) -> str:
        t0 = time.perf_counter() - t_start
        _emit(f"[{t0:6.2f}s] CALL   -> {label}")
        res = await asyncio.to_thread(agent_obj, prompt_text)
        text = str(res).strip()
        t1 = time.perf_counter() - t_start
        _emit(f"[{t1:6.2f}s] OUTPUT <- {label} ({len(text)} chars)")
        if verbose:
            print(f"\n--- {label} Output ---\n{text}\n")
        return text

    score_prompt = (
        f"{user_query}\nCompute overall NPS, 95% MOE, monthly trend (2026-07 to 2026-09), "
        "segment slices (product, channel, tenure), and drill down into 2026-09 by channel and product."
    )
    voc_prompt = (
        f"{user_query}\nAnalyze comment themes for detractors (overall and 2026-09), passives, "
        "and promoters, and extract verbatim customer quotes."
    )
    churn_prompt = (
        f"{user_query}\nCompute revenue at risk in ₹ lakh by product and channel, identify where "
        "the money at risk sits, and audit score-comment mismatches."
    )

    score_report, voc_report, churn_report = await asyncio.gather(
        _call_specialist(score_analyst_agent, "ScoreAnalystAgent", score_prompt),
        _call_specialist(voice_of_customer_agent, "VoiceOfCustomerAgent", voc_prompt),
        _call_specialist(churn_risk_agent, "ChurnRiskAgent", churn_prompt),
    )

    # -------------------------------------------------------------------------
    # PHASE 2: Dependent Action Planning (receives NPS & Theme Context)
    # -------------------------------------------------------------------------
    _emit("─── Phase 2 · Dependent Action Planning (with Phase 1 NPS Context) ───")
    planner_prompt = (
        "Here is the Phase 1 NPS Context from ScoreAnalystAgent, VoiceOfCustomerAgent, and ChurnRiskAgent:\n\n"
        f"[SCORE ANALYST REPORT]\n{score_report}\n\n"
        f"[VOICE OF CUSTOMER REPORT]\n{voc_report}\n\n"
        f"[CHURN RISK REPORT]\n{churn_report}\n\n"
        "Now run `estimate_fix_impact(theme='all')` and `get_callback_list(limit=10, exclude_mismatches=True)` "
        "to rank fixes both ways (NPS points gained vs. ₹ lakh saved) and produce the priority callback list."
    )
    plan_report = await _call_specialist(
        action_planner_agent, "ActionPlannerAgent", planner_prompt
    )

    # -------------------------------------------------------------------------
    # PHASE 3: Executive Synthesis (ReportWriterAgent — No Tools)
    # -------------------------------------------------------------------------
    _emit("─── Phase 3 · Executive Synthesis (ReportWriterAgent · No Tools) ───")
    writer_prompt = (
        "Synthesize all four specialist reports below into the final one-page Executive NPS Brief for the CEO. "
        "Include every exact number, sign (+ / -), margin of error (±), ₹ lakh figure, the RED alert level, "
        "the 3 hidden stories, both fix rankings, the top callback list, and the 3 data caveats:\n\n"
        f"=== 1. SCORE ANALYST REPORT ===\n{score_report}\n\n"
        f"=== 2. VOICE OF CUSTOMER REPORT ===\n{voc_report}\n\n"
        f"=== 3. CHURN & DATA QUALITY REPORT ===\n{churn_report}\n\n"
        f"=== 4. ACTION PLANNER REPORT ===\n{plan_report}\n"
    )
    final_brief = await _call_specialist(
        report_writer_agent, "ReportWriterAgent", writer_prompt
    )

    elapsed = round(time.perf_counter() - t_start, 2)
    return {
        "brief": final_brief,
        "reports": {
            "score_analyst": score_report,
            "voice_of_customer": voc_report,
            "churn_risk": churn_report,
            "action_planner": plan_report,
        },
        "trace_lines": trace_lines,
        "elapsed_seconds": elapsed,
    }


__all__ = [
    "score_analyst_agent",
    "voice_of_customer_agent",
    "churn_risk_agent",
    "action_planner_agent",
    "report_writer_agent",
    "orchestrator_agent",
    "run_three_phase_pipeline_async",
]
