"""Test Runner for Financial Data Agent & Tools.

References:
- architecture.png: FinancialDataAgent (junior analyst · the spreadsheet)
- AI Agents in Finance.html: Ratio families & JSON format
- 04-Agents That Work Together.html: Multi-agent testing patterns

Usage:
    python test_financial_agent.py          # Runs tests defaulting to Apple (AAPL)
    python test_financial_agent.py MSFT     # Runs tests with explicit ticker
"""

import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from tools import (
    compute_key_ratios,
    get_balance_sheet,
    get_cash_flow_statement,
    get_income_statement,
)
from agents import financial_data_agent


def _fmt_money(val):
    if val is None or not isinstance(val, (int, float)):
        return "N/A"
    return f"${val:,.0f}"


def _fmt_pct(val):
    if val is None or not isinstance(val, (int, float)):
        return "N/A"
    return f"{val:.2%}"


def test_tools(ticker: str | None = None):
    """Test individual FMP financial tools directly."""
    target = ticker if ticker else "default (AAPL)"
    print(f"\n{'='*70}")
    print(f"STEP 1: Testing Financial Tools Directly for {target}")
    print(f"{'='*70}")

    # 1. Income Statement
    print("\n1. Fetching Income Statement...")
    t0 = time.time()
    income_raw = get_income_statement(symbol=ticker) if ticker else get_income_statement()
    income = json.loads(income_raw)
    elapsed = time.time() - t0
    print(f"   ✓ Ticker resolved: {income.get('symbol')}")
    print(f"   ✓ Revenue:        {_fmt_money(income.get('revenue'))}")
    print(f"   ✓ Net Income:     {_fmt_money(income.get('netIncome'))}")
    print(f"   ✓ Operating Margin: {_fmt_pct(income.get('operatingIncomeRatio'))}")
    print(f"   ⏱ Time taken:     {elapsed:.2f}s")

    # 2. Balance Sheet
    print("\n2. Fetching Balance Sheet...")
    t0 = time.time()
    balance_raw = get_balance_sheet(symbol=ticker) if ticker else get_balance_sheet()
    balance = json.loads(balance_raw)
    elapsed = time.time() - t0
    print(f"   ✓ Cash & Equiv:   {_fmt_money(balance.get('cashAndCashEquivalents'))}")
    print(f"   ✓ Total Debt:     {_fmt_money(balance.get('totalDebt'))}")
    print(f"   ✓ Net Debt:       {_fmt_money(balance.get('netDebt'))}")
    print(f"   ⏱ Time taken:     {elapsed:.2f}s")

    # 3. Cash Flow
    print("\n3. Fetching Cash Flow Statement...")
    t0 = time.time()
    cf_raw = get_cash_flow_statement(symbol=ticker) if ticker else get_cash_flow_statement()
    cf = json.loads(cf_raw)
    elapsed = time.time() - t0
    print(f"   ✓ Operating CF:   {_fmt_money(cf.get('operatingCashFlow'))}")
    print(f"   ✓ Free Cash Flow: {_fmt_money(cf.get('freeCashFlow'))}")
    print(f"   ⏱ Time taken:     {elapsed:.2f}s")

    # 4. Key Ratios (TTM)
    print("\n4. Computing Key Ratios (TTM)...")
    t0 = time.time()
    ratios_raw = compute_key_ratios(symbol=ticker) if ticker else compute_key_ratios()
    ratios = json.loads(ratios_raw)
    elapsed = time.time() - t0
    val = ratios.get("valuation", {})
    prof = ratios.get("profitability", {})
    print(f"   ✓ P/E Ratio:      {val.get('peRatioTTM', 'N/A')}")
    print(f"   ✓ P/B Ratio:      {val.get('priceToBookRatioTTM', 'N/A')}")
    print(f"   ✓ Gross Margin:   {_fmt_pct(prof.get('grossProfitMarginTTM'))}")
    print(f"   ✓ Return on Equity:{_fmt_pct(prof.get('returnOnEquityTTM'))}")
    print(f"   ⏱ Time taken:     {elapsed:.2f}s")


def test_agent(ticker: str | None = None):
    """Test FinancialDataAgent using AWS Bedrock Nova Lite."""
    print(f"\n{'='*70}")
    print("STEP 2: Testing FinancialDataAgent via AWS Bedrock (Nova Lite)")
    print(f"{'='*70}")

    if ticker:
        prompt = f"Please retrieve and analyze the financial statements and key ratios for {ticker}."
    else:
        prompt = "Please retrieve and analyze the financial statements and key ratios for our target company."

    print(f"\nSending task to Agent: \"{prompt}\"")
    print("Waiting for Nova Lite response (executing tools)...\n")

    t0 = time.time()
    response = financial_data_agent(prompt)
    elapsed = time.time() - t0

    print("=" * 70)
    print("AGENT RESPONSE:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    print(f"✓ Agent execution completed successfully in {elapsed:.2f}s")


def main():
    # If ticker passed as argument, e.g.: python test_financial_agent.py NVDA
    ticker = sys.argv[1] if len(sys.argv) > 1 else None

    print("\n" + "#" * 70)
    print(" FUNDAMENTAL ANALYSIS - FINANCIAL DATA AGENT VERIFICATION")
    print("#" * 70)
    if not ticker:
        print(">> No ticker provided on CLI: testing default stock (Apple / AAPL).")
    else:
        print(f">> Ticker provided on CLI: {ticker.upper()}")

    # Run direct tool tests
    test_tools(ticker)

    # Run agent tests
    test_agent(ticker)

    print("\n" + "#" * 70)
    print(" ALL TESTS COMPLETED")
    print("#" * 70 + "\n")


if __name__ == "__main__":
    main()
