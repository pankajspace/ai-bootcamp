"""Financial Tools for Fundamental Analysis.

Uses Financial Modeling Prep (FMP) API with caching and error handling.
Reference: architecture.png (* = shared tool, cached across agents)
"""

import json
import os
from functools import lru_cache
from typing import Any, Dict
from dotenv import find_dotenv, load_dotenv
import requests
from strands import tool

load_dotenv(find_dotenv())

FMP_BASE_URL = "https://financialmodelingprep.com/stable"


def _get_api_key() -> str:
    key = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")
    if not key:
        raise ValueError("FINANCIAL_MODELING_PREP_API_KEY environment variable is not set.")
    return key


def _clean_symbol(symbol: str | None) -> str:
    if not symbol or not symbol.strip():
        return "AAPL"
    return symbol.strip().upper()


@lru_cache(maxsize=64)
def _fetch_fmp(endpoint: str, symbol: str) -> list[Dict[str, Any]]:
    """Cached internal fetcher for FMP endpoints."""
    api_key = _get_api_key()
    url = f"{FMP_BASE_URL}/{endpoint}"
    params = {"symbol": symbol, "apikey": api_key}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "Error Message" in data:
        raise RuntimeError(data["Error Message"])
    if not isinstance(data, list):
        return [data]
    return data


@tool
def get_income_statement(symbol: str = "AAPL") -> str:
    """Fetch the latest annual income statement for a company from Financial Modeling Prep.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing the latest annual income statement metrics.
    """
    ticker = _clean_symbol(symbol)
    try:
        data = _fetch_fmp("income-statement", ticker)
        if not data:
            return json.dumps({"error": f"No income statement data found for {ticker}"})

        latest = data[0]
        summary = {
            "symbol": ticker,
            "period": latest.get("period", "FY"),
            "fiscalYear": latest.get("fiscalYear") or latest.get("calendarYear"),
            "date": latest.get("date"),
            "revenue": latest.get("revenue"),
            "costOfRevenue": latest.get("costOfRevenue"),
            "grossProfit": latest.get("grossProfit"),
            "grossProfitRatio": latest.get("grossProfitRatio"),
            "researchAndDevelopmentExpenses": latest.get("researchAndDevelopmentExpenses"),
            "operatingExpenses": latest.get("operatingExpenses"),
            "operatingIncome": latest.get("operatingIncome"),
            "operatingIncomeRatio": latest.get("operatingIncomeRatio"),
            "netIncome": latest.get("netIncome"),
            "netIncomeRatio": latest.get("netIncomeRatio"),
            "eps": latest.get("eps"),
            "epsDiluted": latest.get("epsdiluted"),
            "ebitda": latest.get("ebitda"),
            "ebitdaratio": latest.get("ebitdaratio"),
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve income statement for {ticker}: {str(e)}"})


@tool
def get_balance_sheet(symbol: str = "AAPL") -> str:
    """Fetch the latest annual balance sheet for a company from Financial Modeling Prep.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing the latest annual balance sheet metrics.
    """
    ticker = _clean_symbol(symbol)
    try:
        data = _fetch_fmp("balance-sheet-statement", ticker)
        if not data:
            return json.dumps({"error": f"No balance sheet data found for {ticker}"})

        latest = data[0]
        summary = {
            "symbol": ticker,
            "period": latest.get("period", "FY"),
            "fiscalYear": latest.get("fiscalYear") or latest.get("calendarYear"),
            "date": latest.get("date"),
            "cashAndCashEquivalents": latest.get("cashAndCashEquivalents"),
            "shortTermInvestments": latest.get("shortTermInvestments"),
            "totalCashAndInvestments": (latest.get("cashAndCashEquivalents") or 0)
            + (latest.get("shortTermInvestments") or 0),
            "totalCurrentAssets": latest.get("totalCurrentAssets"),
            "totalNonCurrentAssets": latest.get("totalNonCurrentAssets"),
            "totalAssets": latest.get("totalAssets"),
            "totalCurrentLiabilities": latest.get("totalCurrentLiabilities"),
            "totalNonCurrentLiabilities": latest.get("totalNonCurrentLiabilities"),
            "totalLiabilities": latest.get("totalLiabilities"),
            "totalDebt": latest.get("totalDebt"),
            "netDebt": latest.get("netDebt"),
            "totalStockholdersEquity": latest.get("totalStockholdersEquity"),
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve balance sheet for {ticker}: {str(e)}"})


@tool
def get_cash_flow_statement(symbol: str = "AAPL") -> str:
    """Fetch the latest annual cash flow statement for a company from Financial Modeling Prep.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing the latest annual cash flow metrics.
    """
    ticker = _clean_symbol(symbol)
    try:
        data = _fetch_fmp("cash-flow-statement", ticker)
        if not data:
            return json.dumps({"error": f"No cash flow data found for {ticker}"})

        latest = data[0]
        summary = {
            "symbol": ticker,
            "period": latest.get("period", "FY"),
            "fiscalYear": latest.get("fiscalYear") or latest.get("calendarYear"),
            "date": latest.get("date"),
            "operatingCashFlow": latest.get("operatingCashFlow"),
            "capitalExpenditure": latest.get("capitalExpenditure"),
            "freeCashFlow": latest.get("freeCashFlow"),
            "netCashUsedForInvestingActivites": latest.get("netCashUsedForInvestingActivites"),
            "debtRepayment": latest.get("debtRepayment"),
            "commonStockRepurchased": latest.get("commonStockRepurchased"),
            "dividendsPaid": latest.get("dividendsPaid"),
            "netCashUsedProvidedByFinancingActivities": latest.get(
                "netCashUsedProvidedByFinancingActivities"
            ),
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve cash flow statement for {ticker}: {str(e)}"})


@tool
def compute_key_ratios(symbol: str = "AAPL") -> str:
    """Fetch and compute key valuation and financial health ratios (TTM) for a company.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing valuation, profitability, liquidity, and leverage ratios.
    """
    ticker = _clean_symbol(symbol)
    try:
        ratios_data = _fetch_fmp("ratios-ttm", ticker)
        metrics_data = _fetch_fmp("key-metrics-ttm", ticker)

        ratios = ratios_data[0] if ratios_data else {}
        metrics = metrics_data[0] if metrics_data else {}

        summary = {
            "symbol": ticker,
            "valuation": {
                "peRatioTTM": ratios.get("priceToEarningsRatioTTM")
                or ratios.get("priceToEarningsDilutedRatioTTM"),
                "priceToBookRatioTTM": ratios.get("priceToBookRatioTTM"),
                "priceToSalesRatioTTM": ratios.get("priceToSalesRatioTTM"),
                "priceToFreeCashFlowRatioTTM": ratios.get("priceToFreeCashFlowRatioTTM"),
                "marketCap": metrics.get("marketCap"),
                "enterpriseValue": metrics.get("enterpriseValueTTM"),
                "evToSalesTTM": metrics.get("evToSalesTTM"),
            },
            "profitability": {
                "grossProfitMarginTTM": ratios.get("grossProfitMarginTTM"),
                "operatingProfitMarginTTM": ratios.get("operatingProfitMarginTTM"),
                "netProfitMarginTTM": ratios.get("netProfitMarginTTM"),
                "returnOnEquityTTM": metrics.get("returnOnEquityTTM"),
                "returnOnAssetsTTM": metrics.get("returnOnAssetsTTM"),
                "returnOnInvestedCapitalTTM": metrics.get("returnOnInvestedCapitalTTM"),
            },
            "liquidity_and_leverage": {
                "currentRatioTTM": ratios.get("currentRatioTTM")
                or metrics.get("currentRatioTTM"),
                "debtToEquityRatioTTM": ratios.get("debtToEquityRatioTTM"),
                "debtToAssetsRatioTTM": ratios.get("debtToAssetsRatioTTM"),
                "netDebtToEBITDATTM": metrics.get("netDebtToEBITDATTM"),
            },
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to compute key ratios for {ticker}: {str(e)}"})


@tool
def get_financial_data(symbol: str = "AAPL") -> str:
    """Fetch complete financial statements and key ratios in one aggregated JSON payload.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing income statement, balance sheet, cash flows, and key ratios.
    """
    ticker = _clean_symbol(symbol)
    try:
        income = json.loads(get_income_statement(ticker))
        balance = json.loads(get_balance_sheet(ticker))
        cashflow = json.loads(get_cash_flow_statement(ticker))
        ratios = json.loads(compute_key_ratios(ticker))

        overview = {
            "symbol": ticker,
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cashflow,
            "key_ratios": ratios,
        }
        return json.dumps(overview, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get full financial data for {ticker}: {str(e)}"})
