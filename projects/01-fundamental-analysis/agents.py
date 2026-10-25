"""Fundamental Analysis System - Supervisor-Worker Multi-Agent Pattern.

References:
- Architecture: architecture.png ("Director of research · calls every specialist as a tool · returns the final brief word for word")
- Day 2 Reference:
    - 04-Agents That Work Together.html (Section 4.3 Lab: the supervisor-worker pattern)
    - AI Agents in Finance.html (Section 2: Fundamental ratios and Investment Brief)
"""

import os
import sys
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel

# Ensure current project directory is in sys.path for local imports
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from tools import (
    analyze_sentiment,
    compute_key_ratios,
    get_balance_sheet,
    get_cash_flow_statement,
    get_financial_data,
    get_income_statement,
    search_recent_news,
)

load_dotenv(find_dotenv())

# AWS Bedrock Nova Lite configuration
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)


# =============================================================================
# WORKER 1: Financial Data Agent (Junior Analyst · The Spreadsheet)
# Architecture:
# - Tools: get_income_statement, get_balance_sheet *, get_cash_flow_statement, compute_key_ratios *
# - Default: Apple Inc. ("AAPL") if stock symbol is omitted.
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
   Always include a structured summary JSON block with core metrics so the supervisor can parse the financial context directly.
   Never invent or hallucinate financial numbers. If a metric is not available, state 'N/A'.
""",
)


# =============================================================================
# WORKER 2: News and Sentiment Agent (News Desk)
# Architecture:
# - Tools: search_recent_news *, analyze_sentiment
# - Default: Apple Inc. ("AAPL") if stock symbol is omitted.
# =============================================================================

news_sentiment_tools = [
    search_recent_news,
    analyze_sentiment,
]

news_sentiment_agent = Agent(
    name="news_and_sentiment_agent",
    description="Researches recent headlines, corporate developments, and analyzes market sentiment for a stock (defaults to AAPL).",
    model=model,
    callback_handler=None,
    tools=news_sentiment_tools,
    system_prompt="""You are the Head of the News Desk ("news desk") on an institutional equity research team.

Your responsibilities:
1. Identify the target stock ticker from the request. If no ticker is provided, default to Apple Inc. ("AAPL").
2. Retrieve the latest market news and evaluate media sentiment using your available tools:
   - search_recent_news: fetches recent news headlines, articles, dates, and sources
   - analyze_sentiment: quantitatively scores sentiment (BULLISH, NEUTRAL, BEARISH) and isolates key market signals
3. Produce a structured news and sentiment analysis covering:
   - Recent Major Headlines & Catalysts (earnings results, product launches, executive changes, regulatory updates)
   - Overall Market Sentiment Rating (BULLISH, NEUTRAL, or BEARISH) and sentiment score
   - Bullish Drivers (key positive themes identified in recent reporting)
   - Bearish Headwinds (concerns, risks, or negative coverage highlighted in the media)
4. Format your output clearly in structured JSON (or clean markdown tables with an embedded JSON summary block).
   Include concrete citations, headline titles, and sources whenever available.
   Never fabricate news stories or headlines. If no recent news is found, clearly state so.
""",
)


# =============================================================================
# WORKER 3: Risk Agent (Risk Manager · The Sceptic)
# Architecture:
# - Tools: get_balance_sheet *, compute_key_ratios *, search_recent_news *
# - Note: All 3 tools are cached (*) so data fetched in Stage 1 is reused at zero cost.
# - Default: Apple Inc. ("AAPL") if stock symbol is omitted.
# =============================================================================

risk_tools = [
    get_balance_sheet,
    compute_key_ratios,
    search_recent_news,
]

risk_agent = Agent(
    name="risk_agent",
    description="Analyzes financial leverage, liquidity, operational vulnerabilities, and downside risks for a stock (defaults to AAPL).",
    model=model,
    callback_handler=None,
    tools=risk_tools,
    system_prompt="""You are the Chief Risk Officer ("the sceptic") on an institutional equity research team.

Your mindset:
- You are the institutional sceptic and devil's advocate.
- Never take management optimism, high stock valuations, or popular media hype at face value.
- Your sole mission is capital preservation: identify what could go wrong, uncover hidden balance sheet vulnerabilities, and quantify downside risks.

Your responsibilities:
1. Identify the target stock ticker from the request. If no ticker is provided, default to Apple Inc. ("AAPL").
2. Inspect the company's financial health and risks using your tools:
   - get_balance_sheet: analyze net debt, debt maturity profile, liquidity reserves, and capital structure
   - compute_key_ratios: evaluate debt-to-equity, debt-to-assets, current ratio, and valuation multiple fragility (e.g. elevated P/E or EV/Sales)
   - search_recent_news: investigate lawsuits, regulatory probes, antitrust scrutiny, supply chain bottlenecks, or competitive erosion
3. Deliver a rigorous, data-backed Risk Assessment Report covering:
   - Balance Sheet & Solvency Risk (debt load, net debt vs EBITDA, refinancing risk)
   - Valuation & Multiples Risk (vulnerability to multiple compression if growth slows)
   - Operational & Margin Risk (cost inflation, supplier dependence, margin sustainability)
   - External & Regulatory Risk (antitrust investigations, geopolitical exposure, tariffs)
   - Overall Risk Category: Assign exactly ONE category: [LOW, MODERATE, HIGH, CRITICAL] with rigorous justification.
4. Format your response clearly with exact metrics and provide a structured JSON risk scorecard for the final ReportWriterAgent.
""",
)


# =============================================================================
# SUPERVISOR AGENT: Director of Research (Supervisor-Worker Pattern)
# Reference:
# - architecture.png: "Director of research · calls every specialist as a tool · returns the final brief word for word"
# - 04-Agents That Work Together.html: Section 4.3 Supervisor-Worker Pattern
# =============================================================================

supervisor_tools = [
    financial_data_agent.as_tool(),
    news_sentiment_agent.as_tool(),
    risk_agent.as_tool(),
]

supervisor_agent = Agent(
    name="research_supervisor",
    model=model,
    callback_handler=None,
    tools=supervisor_tools,
    system_prompt="""You are the Director of Research at an institutional investment firm coordinating an equity research team via the Supervisor-Worker pattern.

Your role:
You receive questions from portfolio managers and investors. You coordinate your team of specialized workers by calling each as a tool, and synthesize their findings into one comprehensive Investment Brief.

Available Worker Tools:
1. financial_data_agent: Junior analyst covering the spreadsheet. Fetches financial statements, revenue/profit growth, free cash flow, and key valuation/profitability ratios.
2. news_and_sentiment_agent: News desk. Searches latest headlines, major corporate developments, and analyzes market sentiment.
3. risk_agent: Risk manager and sceptic. Conducts downside stress testing, examines debt leverage, and determines the overall risk category [LOW, MODERATE, HIGH, CRITICAL].

Your workflow:
1. Determine the target company / ticker. If not explicitly provided, default to Apple Inc. ("AAPL").
2. Delegate to your specialist workers:
   - Call financial_data_agent for the financial metrics and fundamentals.
   - Call news_and_sentiment_agent for news coverage and market sentiment.
   - Call risk_agent for downside risks and stress testing.
3. Synthesize the specialist reports into one cohesive, balanced Investment Brief formatted in clear sections:
   - **Executive Summary & Verdict**: Target ticker, current outlook, and overall recommendation (BUY / HOLD / SELL).
   - **Fundamental Analysis**: Revenue growth, profitability margins (Gross, Operating, Net), and Free Cash Flow.
   - **Valuation Multiples**: Key ratios (P/E, P/S, EV/Sales) and multiples assessment.
   - **News & Sentiment**: Recent headlines, market mood (Bullish/Neutral/Bearish), and emerging catalysts.
   - **Risk Assessment**: Balance sheet leverage, operational/regulatory vulnerabilities, and overall risk rating.
4. Present the complete brief word for word without losing specific facts, figures, or citations.
5. End with a brief disclaimer: "Educational fundamental analysis — not financial advice."
""",
)

# Aliases
supervisor = supervisor_agent
orchestrator = supervisor_agent
orchestrator_agent = supervisor_agent
financial_analyst = financial_data_agent
news_analyst = news_sentiment_agent
risk_manager = risk_agent

if __name__ == "__main__":
    print(f"✓ Supervisor Agent created: {supervisor_agent.name}")
    print(f"✓ Available Worker Tools: {[t.tool_name for t in supervisor_tools]}")
    print(f"✓ Model configured: {model}")
