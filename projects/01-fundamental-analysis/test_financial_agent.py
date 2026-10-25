"""Unified Test Runner for Fundamental Analysis Agents & Tools.

References:
- architecture.png: Multi-agent equity research workflow
- AI Agents in Finance.html: Financial ratio families & JSON relay baton
- 04-Agents That Work Together.html: AWS Strands agents & testing patterns

Usage:
    python test_financial_agent.py              # Runs all tests defaulting to Apple (AAPL)
    python test_financial_agent.py NVDA         # Runs all tests for NVDA
    python test_financial_agent.py AAPL --tools # Tests only the tools
    python test_financial_agent.py AAPL --agent financial  # Tests only FinancialDataAgent
    python test_financial_agent.py AAPL --agent news       # Tests only NewsAndSentimentAgent
    python test_financial_agent.py AAPL --agent risk       # Tests only RiskAgent
"""

import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from agents import financial_data_agent, news_sentiment_agent, risk_agent
from tools import (
    _fetch_cached_news,
    _fetch_fmp,
    analyze_sentiment,
    compute_key_ratios,
    get_balance_sheet,
    get_cash_flow_statement,
    get_income_statement,
    search_recent_news,
)


def _fmt_money(val):
    if val is None or not isinstance(val, (int, float)):
        return "N/A"
    return f"${val:,.0f}"


def _fmt_pct(val):
    if val is None or not isinstance(val, (int, float)):
        return "N/A"
    return f"{val:.2%}"


def test_tools(ticker: str | None = None):
    """Test all tools directly (Financial statements, ratios, news, sentiment)."""
    target = ticker if ticker else "default (AAPL)"
    print(f"\n{'='*75}")
    print(f"STEP 1: Testing Direct Tool Suite for {target}")
    print(f"{'='*75}")

    # 1. Income Statement
    print("\n1. [Tool] get_income_statement...")
    t0 = time.time()
    income = json.loads(get_income_statement(symbol=ticker) if ticker else get_income_statement())
    print(f"   ✓ Ticker resolved:   {income.get('symbol')}")
    print(f"   ✓ Revenue:           {_fmt_money(income.get('revenue'))}")
    print(f"   ✓ Net Income:        {_fmt_money(income.get('netIncome'))}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 2. Balance Sheet
    print("\n2. [Tool] get_balance_sheet (* shared & cached)...")
    t0 = time.time()
    balance = json.loads(get_balance_sheet(symbol=ticker) if ticker else get_balance_sheet())
    print(f"   ✓ Cash & Equiv:      {_fmt_money(balance.get('cashAndCashEquivalents'))}")
    print(f"   ✓ Total Debt:        {_fmt_money(balance.get('totalDebt'))}")
    print(f"   ✓ Net Debt:          {_fmt_money(balance.get('netDebt'))}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 3. Cash Flow
    print("\n3. [Tool] get_cash_flow_statement...")
    t0 = time.time()
    cf = json.loads(get_cash_flow_statement(symbol=ticker) if ticker else get_cash_flow_statement())
    print(f"   ✓ Operating CF:      {_fmt_money(cf.get('operatingCashFlow'))}")
    print(f"   ✓ Free Cash Flow:    {_fmt_money(cf.get('freeCashFlow'))}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 4. Key Ratios (TTM)
    print("\n4. [Tool] compute_key_ratios (* shared & cached)...")
    t0 = time.time()
    ratios = json.loads(compute_key_ratios(symbol=ticker) if ticker else compute_key_ratios())
    val = ratios.get("valuation", {})
    prof = ratios.get("profitability", {})
    print(f"   ✓ P/E Ratio (TTM):   {val.get('peRatioTTM', 'N/A')}")
    print(f"   ✓ Gross Margin:      {_fmt_pct(prof.get('grossProfitMarginTTM'))}")
    print(f"   ✓ Return on Equity:  {_fmt_pct(prof.get('returnOnEquityTTM'))}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 5. Search Recent News
    print("\n5. [Tool] search_recent_news (* shared & cached)...")
    t0 = time.time()
    news = json.loads(search_recent_news(symbol=ticker) if ticker else search_recent_news())
    print(f"   ✓ Articles found:    {news.get('count', len(news.get('articles', [])))}")
    if news.get("articles"):
        print(f"   ✓ Sample Headline:   {news['articles'][0].get('title')[:60]}...")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 6. Analyze Sentiment
    print("\n6. [Tool] analyze_sentiment...")
    t0 = time.time()
    sentiment = json.loads(analyze_sentiment(symbol=ticker) if ticker else analyze_sentiment())
    print(f"   ✓ Sentiment:         {sentiment.get('sentiment')}")
    print(f"   ✓ Score:             {sentiment.get('sentiment_score', 0):+.2f}")
    print(f"   ✓ Bullish Signals:   {sentiment.get('bullish_signals', [])[:3]}")
    print(f"   ✓ Bearish Signals:   {sentiment.get('bearish_signals', [])[:3]}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")


def test_financial_agent(ticker: str | None = None):
    """Test FinancialDataAgent ('junior analyst · the spreadsheet')."""
    print(f"\n{'='*75}")
    print("STEP 2: Testing FinancialDataAgent (Junior Analyst)")
    print(f"{'='*75}")

    prompt = (
        f"Please retrieve and analyze the financial statements and key ratios for {ticker}."
        if ticker
        else "Please retrieve and analyze the financial statements and key ratios for our target company."
    )
    print(f"Prompt: \"{prompt}\"")
    t0 = time.time()
    response = financial_data_agent(prompt)
    elapsed = time.time() - t0

    print("\nAGENT RESPONSE:")
    print("-" * 75)
    print(response)
    print("-" * 75)
    print(f"✓ FinancialDataAgent completed in {elapsed:.2f}s")


def test_news_agent(ticker: str | None = None):
    """Test NewsAndSentimentAgent ('news desk')."""
    print(f"\n{'='*75}")
    print("STEP 3: Testing NewsAndSentimentAgent (News Desk)")
    print(f"{'='*75}")

    prompt = (
        f"Research recent market news and evaluate investor sentiment for {ticker}."
        if ticker
        else "Research recent market news and evaluate investor sentiment for our target company."
    )
    print(f"Prompt: \"{prompt}\"")
    t0 = time.time()
    response = news_sentiment_agent(prompt)
    elapsed = time.time() - t0

    print("\nAGENT RESPONSE:")
    print("-" * 75)
    print(response)
    print("-" * 75)
    print(f"✓ NewsAndSentimentAgent completed in {elapsed:.2f}s")


def test_risk_agent_test(ticker: str | None = None):
    """Test RiskAgent ('risk manager · the sceptic')."""
    print(f"\n{'='*75}")
    print("STEP 4: Testing RiskAgent (Risk Manager · The Sceptic)")
    print(f"{'='*75}")

    prompt = (
        f"Conduct a rigorous downside risk assessment and stress test for {ticker}."
        if ticker
        else "Conduct a rigorous downside risk assessment and stress test for our target company."
    )
    print(f"Prompt: \"{prompt}\"")
    t0 = time.time()
    response = risk_agent(prompt)
    elapsed = time.time() - t0

    print("\nAGENT RESPONSE:")
    print("-" * 75)
    print(response)
    print("-" * 75)
    print(f"✓ RiskAgent completed in {elapsed:.2f}s")


def test_cache_stats():
    """Verify shared tool caching stats."""
    print(f"\n{'='*75}")
    print("STEP 5: Shared Tool Cache Verification (* in architecture.png)")
    print(f"{'='*75}")
    fmp_info = _fetch_fmp.cache_info()
    news_info = _fetch_cached_news.cache_info()
    print(f"FMP API Cache:   hits={fmp_info.hits}, misses={fmp_info.misses}, entries={fmp_info.currsize}")
    print(f"News API Cache:  hits={news_info.hits}, misses={news_info.misses}, entries={news_info.currsize}")
    if fmp_info.hits > 0 or news_info.hits > 0:
        print("✓ SUCCESS: Cached shared tools avoided redundant API calls across agents!")


def main():
    args = sys.argv[1:]
    ticker = None
    mode = "all"

    # Simple CLI argument parser
    for arg in args:
        if arg.startswith("--"):
            mode = arg.lower()
        elif not ticker:
            ticker = arg.upper()

    print("\n" + "#" * 75)
    print(" FUNDAMENTAL ANALYSIS - UNIFIED TEST SUITE")
    print("#" * 75)
    target_str = ticker if ticker else "default (Apple / AAPL)"
    print(f">> Target Stock: {target_str} | Mode: {mode}")

    if mode in ["all", "--tools"]:
        test_tools(ticker)

    if mode in ["all", "--agent", "--financial"]:
        test_financial_agent(ticker)

    if mode in ["all", "--agent", "--news"]:
        test_news_agent(ticker)

    if mode in ["all", "--agent", "--risk"]:
        test_risk_agent_test(ticker)

    test_cache_stats()

    print("\n" + "#" * 75)
    print(" ALL REQUESTED TESTS COMPLETED SUCCESSFULLY")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()
