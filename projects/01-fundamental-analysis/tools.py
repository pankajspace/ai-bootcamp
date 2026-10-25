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
import yfinance as yf
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


# =============================================================================
# News and Sentiment Tools (Shared & Cached: *)
# Reference: architecture.png (* = shared tool, cached across agents)
# =============================================================================

@lru_cache(maxsize=32)
def _fetch_cached_news(ticker: str) -> list[Dict[str, Any]]:
    """Internal cached news fetcher using Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set.")

    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)
    query = f"{ticker} stock company news financial performance earnings"
    response = client.search(query=query, max_results=6, topic="news")
    results = response.get("results", [])

    articles = []
    for item in results:
        articles.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0.0),
        })
    return articles


@tool
def search_recent_news(symbol: str = "AAPL") -> str:
    """Fetch recent news articles and market developments for a given stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string containing recent news articles, headlines, sources, and summaries.
    """
    ticker = _clean_symbol(symbol)
    try:
        articles = _fetch_cached_news(ticker)
        if not articles:
            return json.dumps({
                "symbol": ticker,
                "message": f"No recent news articles found for {ticker}",
                "articles": [],
            })

        return json.dumps({
            "symbol": ticker,
            "count": len(articles),
            "articles": articles,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch news for {ticker}: {str(e)}"})


@tool
def analyze_sentiment(symbol: str = "AAPL") -> str:
    """Analyze recent market and investor sentiment for a given stock based on recent news headlines.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string with sentiment classification (BULLISH, NEUTRAL, or BEARISH), sentiment score (-1.0 to 1.0), and key sentiment drivers.
    """
    ticker = _clean_symbol(symbol)
    try:
        articles = _fetch_cached_news(ticker)
        if not articles:
            return json.dumps({
                "symbol": ticker,
                "sentiment": "NEUTRAL",
                "sentiment_score": 0.0,
                "confidence": 0.5,
                "summary": f"Insufficient recent news coverage to compute reliable sentiment for {ticker}.",
                "bullish_signals": [],
                "bearish_signals": [],
            }, indent=2)

        # Quantitative sentiment lexicon scoring
        positive_keywords = {
            "growth", "surge", "beat", "rally", "record", "profit", "gain", "buy",
            "upgrade", "bullish", "innovative", "expansion", "dividend", "revenue",
            "outperform", "strong", "raised", "positive", "high", "success", "lead"
        }
        negative_keywords = {
            "drop", "fall", "decline", "miss", "loss", "slump", "bearish", "downgrade",
            "investigation", "lawsuit", "antitrust", "sell", "probe", "plunge", "risk",
            "warning", "headwind", "cut", "weak", "penalty", "debt", "tariff", "fine"
        }

        pos_matches = []
        neg_matches = []
        total_text = ""

        for a in articles:
            text = f"{a.get('title', '')} {a.get('content', '')}".lower()
            total_text += " " + text
            for kw in positive_keywords:
                if kw in text and kw not in pos_matches:
                    pos_matches.append(kw)
            for kw in negative_keywords:
                if kw in text and kw not in neg_matches:
                    neg_matches.append(kw)

        pos_count = len(pos_matches)
        neg_count = len(neg_matches)
        total = pos_count + neg_count

        if total == 0:
            score = 0.0
            sentiment = "NEUTRAL"
        else:
            score = round((pos_count - neg_count) / total, 2)
            if score > 0.15:
                sentiment = "BULLISH"
            elif score < -0.15:
                sentiment = "BEARISH"
            else:
                sentiment = "NEUTRAL"

        result = {
            "symbol": ticker,
            "sentiment": sentiment,
            "sentiment_score": score,
            "articles_analyzed": len(articles),
            "bullish_signals": pos_matches[:5],
            "bearish_signals": neg_matches[:5],
            "summary": f"Market sentiment for {ticker} is {sentiment} with a net score of {score:+.2f} across {len(articles)} analyzed news articles.",
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze sentiment for {ticker}: {str(e)}"})


# =============================================================================
# Valuation Tools
# Reference: architecture.png (ValuationAgent · run_dcf_model, get_peer_multiples)
# =============================================================================

@tool
def run_dcf_model(
    symbol: str = "AAPL",
    discount_rate: float = 0.09,
    terminal_growth_rate: float = 0.03,
    growth_rate: float = 0.08,
) -> str:
    """Run a 5-year Discounted Cash Flow (DCF) model to estimate the intrinsic share price.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT'). Defaults to 'AAPL'.
        discount_rate: Cost of capital / WACC (e.g. 0.09 for 9%). Defaults to 0.09.
        terminal_growth_rate: Perpetual terminal growth rate (e.g. 0.03 for 3%). Defaults to 0.03.
        growth_rate: Projected annual FCF growth rate for the next 5 years. Defaults to 0.08 (8%).

    Returns:
        JSON string containing projected cash flows, terminal value, enterprise value, implied share price, and margin of safety.
    """
    ticker = _clean_symbol(symbol)
    try:
        cf_data = json.loads(get_cash_flow_statement(ticker))
        bs_data = json.loads(get_balance_sheet(ticker))

        fcf_base = cf_data.get("freeCashFlow")
        if not fcf_base or fcf_base <= 0:
            # Fallback to operating cash flow - capex or default
            fcf_base = (cf_data.get("operatingCashFlow") or 0) + (cf_data.get("capitalExpenditure") or 0)
        if not fcf_base or fcf_base <= 0:
            fcf_base = 50_000_000_000  # Conservative institutional default

        cash = bs_data.get("totalCashAndInvestments") or bs_data.get("cashAndCashEquivalents") or 0
        debt = bs_data.get("totalDebt") or 0

        # Retrieve market share price and shares outstanding
        info = yf.Ticker(ticker).info
        shares = info.get("sharesOutstanding") or 15_000_000_000
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 250.0

        # 5-Year Cash Flow Projections
        projected_fcf = []
        pv_fcf_sum = 0.0
        cur_fcf = float(fcf_base)

        for year in range(1, 6):
            cur_fcf *= (1.0 + growth_rate)
            discount_factor = (1.0 + discount_rate) ** year
            pv = cur_fcf / discount_factor
            pv_fcf_sum += pv
            projected_fcf.append({
                "year": year,
                "projected_fcf": round(cur_fcf, 0),
                "present_value": round(pv, 0),
            })

        # Terminal Value Calculation
        terminal_value = (cur_fcf * (1.0 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1.0 + discount_rate) ** 5)

        # Enterprise Value & Equity Value
        enterprise_value = pv_fcf_sum + pv_terminal_value
        equity_value = enterprise_value + cash - debt
        implied_share_price = equity_value / shares

        upside_pct = ((implied_share_price - current_price) / current_price) * 100.0
        valuation_verdict = "UNDERVALUED" if upside_pct > 10 else ("OVERVALUED" if upside_pct < -10 else "FAIRLY_VALUED")

        dcf_summary = {
            "symbol": ticker,
            "inputs": {
                "base_fcf": fcf_base,
                "projected_growth_rate": f"{growth_rate:.1%}",
                "discount_rate_wacc": f"{discount_rate:.1%}",
                "terminal_growth_rate": f"{terminal_growth_rate:.1%}",
                "cash_and_investments": cash,
                "total_debt": debt,
                "shares_outstanding": shares,
                "current_market_price": round(current_price, 2),
            },
            "projected_cash_flows": projected_fcf,
            "pv_of_5yr_cash_flows": round(pv_fcf_sum, 0),
            "terminal_value": round(terminal_value, 0),
            "pv_of_terminal_value": round(pv_terminal_value, 0),
            "enterprise_value": round(enterprise_value, 0),
            "implied_equity_value": round(equity_value, 0),
            "implied_fair_share_price": round(implied_share_price, 2),
            "upside_potential_pct": f"{upside_pct:+.2f}%",
            "valuation_verdict": valuation_verdict,
        }
        return json.dumps(dcf_summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to run DCF model for {ticker}: {str(e)}"})


@tool
def get_peer_multiples(symbol: str = "AAPL") -> str:
    """Compare valuation multiples of the target stock against top industry peers.

    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'NVDA'). Defaults to 'AAPL'.

    Returns:
        JSON string comparing P/E, P/S, EV/EBITDA, and P/B multiples against peers.
    """
    ticker = _clean_symbol(symbol)
    peer_map = {
        "AAPL": ["MSFT", "GOOGL", "AMZN"],
        "MSFT": ["AAPL", "GOOGL", "AMZN"],
        "GOOGL": ["META", "MSFT", "AMZN"],
        "NVDA": ["AMD", "INTC", "TSM"],
        "TSLA": ["F", "GM", "RIVN"],
    }
    peers = peer_map.get(ticker, ["MSFT", "GOOGL", "AMZN"])

    try:
        def fetch_multiples(sym):
            try:
                info = yf.Ticker(sym).info
                return {
                    "symbol": sym,
                    "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "trailingPE": round(info.get("trailingPE"), 2) if info.get("trailingPE") else None,
                    "forwardPE": round(info.get("forwardPE"), 2) if info.get("forwardPE") else None,
                    "evToEbitda": round(info.get("enterpriseToEbitda"), 2) if info.get("enterpriseToEbitda") else None,
                    "priceToSales": round(info.get("priceToSalesTrailing12Months"), 2) if info.get("priceToSalesTrailing12Months") else None,
                    "priceToBook": round(info.get("priceToBook"), 2) if info.get("priceToBook") else None,
                }
            except Exception:
                return {"symbol": sym}

        target_metrics = fetch_multiples(ticker)
        peer_metrics = [fetch_multiples(p) for p in peers]

        # Calculate averages for peer group
        pe_list = [p["trailingPE"] for p in peer_metrics if p.get("trailingPE")]
        ev_ebitda_list = [p["evToEbitda"] for p in peer_metrics if p.get("evToEbitda")]
        ps_list = [p["priceToSales"] for p in peer_metrics if p.get("priceToSales")]

        avg_pe = round(sum(pe_list) / len(pe_list), 2) if pe_list else None
        avg_ev_ebitda = round(sum(ev_ebitda_list) / len(ev_ebitda_list), 2) if ev_ebitda_list else None
        avg_ps = round(sum(ps_list) / len(ps_list), 2) if ps_list else None

        target_pe = target_metrics.get("trailingPE")
        pe_premium = round(((target_pe - avg_pe) / avg_pe) * 100, 1) if target_pe and avg_pe else None

        result = {
            "target": target_metrics,
            "peers": peer_metrics,
            "peer_averages": {
                "avgTrailingPE": avg_pe,
                "avgEVtoEBITDA": avg_ev_ebitda,
                "avgPriceToSales": avg_ps,
            },
            "comparison": {
                "pe_premium_vs_peers_pct": f"{pe_premium:+.1f}%" if pe_premium is not None else "N/A",
                "relative_valuation": "PREMIUM" if (pe_premium and pe_premium > 10) else ("DISCOUNT" if (pe_premium and pe_premium < -10) else "IN_LINE"),
            },
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to compute peer multiples for {ticker}: {str(e)}"})


