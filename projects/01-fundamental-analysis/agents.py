"""Fundamental Analysis System - Agents Definition.

Reference:
- Architecture: architecture.png
- Day 2 Reference: 04-Agents That Work Together.html, AI Agents in Finance.html
"""

import os
import sys
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent import GraphBuilder

# Ensure current project directory is in sys.path for local imports
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from tools import (
    compute_key_ratios,
    get_balance_sheet,
    get_cash_flow_statement,
    get_financial_data,
    get_income_statement,
)

load_dotenv(find_dotenv())

# AWS Bedrock Nova Lite configuration
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)

# =============================================================================
# 1. Orchestrator Agent (Director of Research)
# =============================================================================
# Architecture Role:
# Director of Research · Coordinates specialists · Returns the final brief word for word.
# Workflow Stages:
#   ① Stage 1 (Parallel): FinancialDataAgent, NewsAndSentimentAgent, RiskAgent
#   ② Stage 2: ValuationAgent (ingests financial context)
#   ③ Stage 3: ReportWriterAgent (synthesizes rating, value, risk, sentiment into investment brief)
# =============================================================================

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model=model,
    callback_handler=None,
    system_prompt="""You are the Director of Research at an institutional investment firm orchestrating fundamental equity analysis.

Your role:
- Supervise the entire fundamental analysis pipeline for any target stock ticker.
- Coordinate the specialist team across 3 systematic phases:
    1. Phase 1 (Concurrent specialists):
       - FinancialDataAgent (junior analyst · financial statements & key ratios)
       - NewsAndSentimentAgent (news desk · recent headlines & market sentiment)
       - RiskAgent (risk manager · financial health, debt leverage & downside risks)
    2. Phase 2 (Valuation specialist):
       - ValuationAgent (DCF model & peer multiples, informed by financial context from Phase 1)
    3. Phase 3 (Synthesis & Delivery):
       - ReportWriterAgent (Managing Director synthesizing all 4 specialist reports into a final Investment Brief)

Guiding principles:
- Ground all findings strictly in quantitative metrics and verified data (e.g. Financial Modeling Prep / Yahoo Finance).
- Demand objective, balanced evaluation: upside potential must be paired with clear downside risks.
- Return the final Investment Brief word-for-word without truncation, editorializing, or omitting crucial disclosures.
""",
)

# =============================================================================
# 2. Financial Data Agent (Junior Analyst)
# =============================================================================
# Architecture Role:
# Junior analyst · the spreadsheet
# Tools: get_income_statement, get_balance_sheet *, get_cash_flow_statement, compute_key_ratios *
# Default: Apple Inc. ("AAPL") if stock symbol is omitted or unspecified.
# =============================================================================

financial_tools = [
    get_income_statement,
    get_balance_sheet,
    get_cash_flow_statement,
    compute_key_ratios,
    get_financial_data,
]

financial_data_agent = Agent(
    name="financial_data_agent",
    description="Fetches and analyzes corporate financial statements and key ratios for a given stock (defaults to AAPL).",
    model=model,
    callback_handler=None,
    tools=financial_tools,
    system_prompt="""You are the Junior Financial Analyst ("the spreadsheet") on an institutional equity research team.

Your responsibilities:
1. Identify the target stock ticker from the request. If no ticker is provided, default to Apple Inc. ("AAPL").
2. Retrieve the financial statements and ratios using your available tools:
   - get_income_statement: revenue, margins, operating income, net income, EPS
   - get_balance_sheet: cash, total assets, liabilities, net debt, stockholders' equity
   - get_cash_flow_statement: operating cash flow, capex, free cash flow
   - compute_key_ratios: valuation multiples (P/E, P/S, P/B, EV/Sales), profitability (margins, ROE, ROA, ROIC), and leverage/liquidity metrics
3. Produce a structured, data-grounded report covering:
   - Revenue & Earnings Growth
   - Profitability & Margins (Gross, Operating, Net)
   - Balance Sheet Health & Liquidity (Cash reserves vs. Debt obligations)
   - Free Cash Flow Generation
   - Key Valuation & Operating Ratios (TTM)
4. Format your output clearly in clean, structured JSON format (or accompanied by concise summary tables) with exact figures.
   Always include a structured summary JSON block with core metrics so downstream agents (such as ValuationAgent) can parse the financial context directly.
   Never invent or hallucinate financial numbers. If a metric is not available, state 'N/A'.
""",
)

# Aliases
orchestrator = orchestrator_agent
financial_analyst = financial_data_agent

if __name__ == "__main__":
    print(f"✓ Orchestrator Agent created: {orchestrator_agent.name}")
    print(f"✓ Financial Data Agent created: {financial_data_agent.name}")
    print(f"✓ Available financial tools: {[t.__name__ for t in financial_tools]}")
    print(f"✓ Model configured: {model}")
