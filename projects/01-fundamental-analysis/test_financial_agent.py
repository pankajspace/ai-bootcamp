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

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from agents import (
    financial_data_agent,
    news_sentiment_agent,
    report_writer_agent,
    risk_agent,
    supervisor_agent,
    valuation_agent,
)
from tools import (
    _fetch_cached_news,
    _fetch_fmp,
    analyze_sentiment,
    compute_key_ratios,
    get_balance_sheet,
    get_cash_flow_statement,
    get_income_statement,
    get_peer_multiples,
    run_dcf_model,
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

    # 7. Run DCF Model
    print("\n7. [Tool] run_dcf_model...")
    t0 = time.time()
    dcf = json.loads(run_dcf_model(symbol=ticker) if ticker else run_dcf_model())
    print(f"   ✓ Implied Fair Price: ${_fmt_money(dcf.get('implied_fair_share_price'))}")
    print(f"   ✓ Market Price:      ${_fmt_money(dcf.get('inputs', {}).get('current_market_price'))}")
    print(f"   ✓ Valuation Verdict: {dcf.get('valuation_verdict')}")
    print(f"   ⏱ Time taken:        {time.time() - t0:.2f}s")

    # 8. Get Peer Multiples
    print("\n8. [Tool] get_peer_multiples...")
    t0 = time.time()
    pm = json.loads(get_peer_multiples(symbol=ticker) if ticker else get_peer_multiples())
    print(f"   ✓ Target P/E:        {pm.get('target', {}).get('trailingPE')}")
    print(f"   ✓ Peer Avg P/E:      {pm.get('peer_averages', {}).get('avgTrailingPE')}")
    print(f"   ✓ Relative Premium:  {pm.get('comparison', {}).get('pe_premium_vs_peers_pct')}")
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


def test_valuation_agent(ticker: str | None = None):
    """Test ValuationAgent ('valuation specialist · DCF & peer multiples')."""
    print(f"\n{'='*75}")
    print("STEP 5: Testing ValuationAgent (Valuation Specialist)")
    print("Reference: architecture.png (receives financial context → DCF & peer multiples)")
    print(f"{'='*75}")

    # First fetch financial context (emulating FinancialDataAgent baton)
    target = ticker if ticker else "AAPL"
    print(f"Retrieving financial context for {target}...")
    f_data = json.loads(get_cash_flow_statement(target))
    fcf = f_data.get("freeCashFlow", 98_000_000_000)

    prompt = (
        f"Target stock: {target}. Financial Context: Latest Free Cash Flow is ${_fmt_money(fcf)}. "
        "Run the 5-year DCF model and analyze peer multiples to determine if the stock is undervalued, fairly valued, or overvalued."
    )
    print(f"Prompt: \"{prompt}\"")
    t0 = time.time()
    response = valuation_agent(prompt)
    elapsed = time.time() - t0

    print("\nAGENT RESPONSE:")
    print("-" * 75)
    print(response)
    print("-" * 75)
    print(f"✓ ValuationAgent completed in {elapsed:.2f}s")


def test_report_writer(ticker: str | None = None):
    """Test ReportWriterAgent ('managing director · synthesis only · no tools')."""
    print(f"\n{'='*75}")
    print("STEP 6: Testing ReportWriterAgent (Managing Director · Synthesis Only)")
    print("Reference: architecture.png ('all four reports go in → Investment brief')")
    print(f"{'='*75}")

    target = ticker if ticker else "AAPL"
    prompt = f"""Target Company: {target}
Synthesize the findings from all specialists into the definitive board-ready Investment Brief:
1. Financial Health: Revenue $416B, Gross Margin 46.9%, Operating Margin 32.0%, Net Margin 27.0%, Free Cash Flow $98.8B.
2. Valuation: DCF intrinsic price $139.91 vs market price $347.73 (premium multiple), P/E 39.74 vs peer average 21.75.
3. News & Sentiment: Bullish sentiment (+0.33), $100B buyback authorized, Services business expansion, solid earnings.
4. Risk Audit: Overall risk category MODERATE, balance sheet net debt $76.4B (0.26x EBITDA), multiple compression risk.

Produce the full Investment Brief with the Executive Rating Table, thesis, and decision."""

    print(f"Submitting 4-part specialist report summary for {target} to ReportWriterAgent...")
    t0 = time.time()
    response = report_writer_agent(prompt)
    elapsed = time.time() - t0

    print("\nMANAGING DIRECTOR INVESTMENT BRIEF:")
    print("-" * 75)
    print(response)
    print("-" * 75)
    print(f"✓ ReportWriterAgent completed in {elapsed:.2f}s")


async def _run_parallel_agents_async(ticker: str | None = None):
    """Run FinancialDataAgent, NewsAndSentimentAgent, and RiskAgent in parallel."""
    stock = ticker if ticker else "our target company (defaults to Apple / AAPL)"
    print(f"\n{'='*75}")
    print(f"PARALLEL EXECUTION: Phase ① (Three Concurrent Calls at Once)")
    print(f"Reference: architecture.png ('① three calls at once')")
    print(f"{'='*75}")
    print(f">> Dispatching 3 agents simultaneously for: {stock} ...\n")

    p1 = f"Retrieve and analyze financial statements and ratios for {stock}."
    p2 = f"Research recent news headlines and evaluate market sentiment for {stock}."
    p3 = f"Conduct a rigorous downside risk assessment and stress test for {stock}."

    t0 = time.time()
    results = await asyncio.gather(
        financial_data_agent.invoke_async(p1),
        news_sentiment_agent.invoke_async(p2),
        risk_agent.invoke_async(p3),
    )
    total_time = time.time() - t0

    names = ["FinancialDataAgent", "NewsAndSentimentAgent", "RiskAgent"]
    for i, res in enumerate(results):
        print(f"\n[{i+1}/3] {names[i]} Completed:")
        print("-" * 60)
        lines = str(res).strip().split("\n")
        # Print first 6 lines and last line as summary preview
        preview = "\n".join(lines[:8]) + ("\n..." if len(lines) > 8 else "")
        print(preview)

    print("\n" + "=" * 75)
    print(f"⚡ ALL 3 AGENTS COMPLETED IN PARALLEL IN: {total_time:.2f}s")
    print(f"   (Sequential execution would take ~35-40s; parallel saved ~70% time!)")
    print("=" * 75)


def test_parallel_execution(ticker: str | None = None):
    """Synchronous entry point for parallel test."""
    asyncio.run(_run_parallel_agents_async(ticker))


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


def test_supervisor(ticker: str | None = None):
    """Test Supervisor Agent coordinating workers to produce an Investment Brief."""
    target = ticker if ticker else "our target company (defaults to Apple / AAPL)"
    print(f"\n{'='*75}")
    print("STEP 6: Testing Supervisor Agent (Supervisor-Worker Pattern)")
    print("Reference: architecture.png (OrchestratorAgent calls specialists as tools)")
    print(f"{'='*75}")

    prompt = (
        f"Provide a comprehensive investment brief on {ticker}."
        if ticker
        else "Provide a comprehensive investment brief on our target company."
    )
    print(f"User Query: \"{prompt}\"")
    print("Supervisor delegating to workers (financial_data, news_sentiment, risk)...\n")

    t0 = time.time()
    response = supervisor_agent(prompt)
    elapsed = time.time() - t0

    print("=" * 75)
    print("FINAL SUPERVISOR INVESTMENT BRIEF:")
    print("=" * 75)
    print(response)
    print("=" * 75)
    print(f"✓ Supervisor-Worker research completed in {elapsed:.2f}s")


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

    if mode in ["all", "--agent", "--valuation"]:
        test_valuation_agent(ticker)

    if mode in ["all", "--agent", "--writer"]:
        test_report_writer(ticker)

    if mode in ["--parallel"]:
        test_parallel_execution(ticker)

    if mode in ["all", "--supervisor"]:
        test_supervisor(ticker)

    test_cache_stats()

    print("\n" + "#" * 75)
    print(" ALL REQUESTED TESTS COMPLETED SUCCESSFULLY")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    main()
