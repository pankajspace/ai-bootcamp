"""tools/financial_tools.py: financial statements and key ratios from yfinance (millions USD)."""
import json, math
import yfinance as yf
from agents import function_tool

class _SimpleCache:
    """Remembers tool results for this run, keyed by (tool name, ticker)."""
    def __init__(self):
        self._store = {}
    def get(self, key):
        return self._store.get(key)          # None = never seen this key
    def store(self, key, value):
        self._store[key] = value

_cache = _SimpleCache()

def _safe_float(v):
    """Anything → float, or None if it isn't a usable number."""
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

def _millions(v):
    """Raw dollars → millions: 383285000000 → 383285.0"""
    f = _safe_float(v)
    return round(f / 1_000_000, 1) if f is not None else None

def _extract_row(df, *names, col):
    """Value of the first row name that exists in the table (in millions)."""
    for name in names:                       # e.g. try "Operating Income", then "EBIT"
        if name in df.index:
            return _millions(df.loc[name, col])
    return None


@function_tool
def get_income_statement(ticker: str) -> str:
    """
    Fetch the annual income statement for a given stock ticker.
    Returns revenue, gross profit, operating income, EBITDA, net income,
    and EPS for the last 4 fiscal years. All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_income_statement", ticker.upper())          # ① cache key
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit                                            #    already fetched this run
    try:
        stock = yf.Ticker(ticker.upper())
        fin = stock.financials                                 # ② rows = line items, columns = fiscal years
        if fin is None or fin.empty:
            return json.dumps({"error": f"No income statement data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "company_name": stock.info.get("longName", ticker.upper()),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},                                 # ③ filled year by year
        }
        for col in fin.columns[:4]:                            #    the newest 4 fiscal years
            year = str(col.year)                               #    Timestamp('2025-09-30') → "2025"
            result["annual_data"][year] = {
                "revenue":          _extract_row(fin, "Total Revenue", col=col),
                "gross_profit":     _extract_row(fin, "Gross Profit", col=col),
                "operating_income": _extract_row(fin, "Operating Income", "EBIT", col=col),
                "ebitda":           _extract_row(fin, "EBITDA", col=col),
                "net_income":       _extract_row(fin, "Net Income", col=col),
                "r_and_d":          _extract_row(fin, "Research And Development", col=col),
            }

        info = stock.info                                      # ④ today's headline numbers
        result["eps_ttm"]       = _safe_float(info.get("trailingEps"))
        result["eps_forward"]   = _safe_float(info.get("forwardEps"))
        result["revenue_ttm_M"] = _millions(info.get("totalRevenue"))
        result["gross_margin_pct"] = _safe_float(info.get("grossMargins", 0)) and round(info.get("grossMargins", 0) * 100, 2)
        result["operating_margin_pct"] = round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else None
        result["net_margin_pct"] = round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None

        output = json.dumps(result, indent=2, default=str)     # ⑤ dict → JSON text
        _cache.store(_key, output)                             #    remember it
        return output
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker}) # ⑥ never crash the pipeline

# Filled in: the notes list get_balance_sheet and get_cash_flow_statement but don't print them.
# They follow the same pattern as get_income_statement: cache → yfinance table → 4 years → JSON.
@function_tool
def get_balance_sheet(ticker: str) -> str:
    """
    Fetch the annual balance sheet for a given stock ticker.
    Returns total assets, liabilities, equity, total debt, cash, current assets,
    current liabilities and working capital for the last 4 fiscal years.
    All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_balance_sheet", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        bs = stock.balance_sheet
        if bs is None or bs.empty:
            return json.dumps({"error": f"No balance sheet data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "company_name": stock.info.get("longName", ticker.upper()),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},
        }
        for col in bs.columns[:4]:
            year = str(col.year)
            current_assets = _extract_row(bs, "Current Assets", col=col)
            current_liabilities = _extract_row(bs, "Current Liabilities", col=col)
            result["annual_data"][year] = {
                "total_assets":        _extract_row(bs, "Total Assets", col=col),
                "total_liabilities":   _extract_row(bs, "Total Liabilities Net Minority Interest", col=col),
                "shareholders_equity": _extract_row(bs, "Stockholders Equity", "Common Stock Equity", col=col),
                "total_debt":          _extract_row(bs, "Total Debt", col=col),
                "cash_and_equivalents": _extract_row(bs, "Cash And Cash Equivalents",
                                                     "Cash Cash Equivalents And Short Term Investments", col=col),
                "current_assets":      current_assets,
                "current_liabilities": current_liabilities,
                "working_capital":     _extract_row(bs, "Working Capital", col=col)
                                       if "Working Capital" in bs.index
                                       else (round(current_assets - current_liabilities, 1)
                                             if current_assets is not None and current_liabilities is not None else None),
            }

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def get_cash_flow_statement(ticker: str) -> str:
    """
    Fetch the annual cash flow statement for a given stock ticker.
    Returns operating cash flow, capital expenditure, free cash flow, investing and
    financing cash flows, buybacks and dividends for the last 4 fiscal years, plus the
    3-year free-cash-flow CAGR. All monetary values are in millions USD.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("get_cash_flow_statement", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        cf = stock.cashflow
        if cf is None or cf.empty:
            return json.dumps({"error": f"No cash flow data found for {ticker}"})

        currency = stock.info.get("financialCurrency", "USD")
        result: dict = {
            "ticker": ticker.upper(),
            "company_name": stock.info.get("longName", ticker.upper()),
            "currency": currency,
            "unit": f"millions {currency}",
            "annual_data": {},
        }
        fcf_by_year = []
        for col in cf.columns[:4]:
            year = str(col.year)
            fcf = _extract_row(cf, "Free Cash Flow", col=col)
            fcf_by_year.append(fcf)
            result["annual_data"][year] = {
                "operating_cash_flow": _extract_row(cf, "Operating Cash Flow", col=col),
                "capital_expenditure": _extract_row(cf, "Capital Expenditure", col=col),
                "free_cash_flow":      fcf,
                "investing_cash_flow": _extract_row(cf, "Investing Cash Flow", col=col),
                "financing_cash_flow": _extract_row(cf, "Financing Cash Flow", col=col),
                "share_buybacks":      _extract_row(cf, "Repurchase Of Capital Stock", col=col),
                "dividends_paid":      _extract_row(cf, "Cash Dividends Paid", col=col),
            }

        # 3-year CAGR needs the newest year and the year three columns back, both positive
        newest, oldest = (fcf_by_year[0], fcf_by_year[3]) if len(fcf_by_year) >= 4 else (None, None)
        result["fcf_cagr_3y_pct"] = (round(((newest / oldest) ** (1 / 3) - 1) * 100, 2)
                                     if newest and oldest and newest > 0 and oldest > 0 else None)

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def compute_key_ratios(ticker: str) -> str:
    """
    Compute key fundamental ratios for a given stock ticker.
    Calculates valuation ratios (P/E, P/B, P/S, EV/EBITDA), profitability
    ratios (ROE, ROA, net margin), leverage ratios (Debt/Equity, current ratio,
    quick ratio), and growth metrics (revenue YoY, EPS YoY).

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    _key = ("compute_key_ratios", ticker.upper())
    _hit = _cache.get(_key)
    if _hit is not None:
        return _hit
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info                                    # one big dict of ready-made fields

        def pct(v):                                          # 0.4691 → 46.91
            return round(v * 100, 2) if v is not None else None

        # --- Valuation ---
        pe_trailing = _safe_float(info.get("trailingPE"))
        pe_forward  = _safe_float(info.get("forwardPE"))
        pb_ratio    = _safe_float(info.get("priceToBook"))
        ps_ratio    = _safe_float(info.get("priceToSalesTrailing12Months"))
        ev_ebitda   = _safe_float(info.get("enterpriseToEbitda"))
        ev_revenue  = _safe_float(info.get("enterpriseToRevenue"))

        # --- Profitability ---
        roe          = pct(info.get("returnOnEquity"))
        roa          = pct(info.get("returnOnAssets"))
        net_margin   = pct(info.get("profitMargins"))
        gross_margin = pct(info.get("grossMargins"))
        op_margin    = pct(info.get("operatingMargins"))

        # --- Liquidity & leverage ---
        current_ratio = _safe_float(info.get("currentRatio"))
        quick_ratio   = _safe_float(info.get("quickRatio"))
        debt_to_eq    = _safe_float(info.get("debtToEquity"))   # already in %

        # --- Growth: worked out by hand from the income statement ---
        fin = stock.financials
        revenue_growth = None
        if fin is not None and not fin.empty and len(fin.columns) >= 2:
            rev_rows = [r for r in ["Total Revenue"] if r in fin.index]
            if rev_rows:
                rev_now  = fin.loc[rev_rows[0], fin.columns[0]]   # column 0 = newest year
                rev_prev = fin.loc[rev_rows[0], fin.columns[1]]   # column 1 = the year before
                if rev_prev and float(rev_prev) != 0:
                    revenue_growth = round(((float(rev_now) - float(rev_prev)) / abs(float(rev_prev))) * 100, 2)

        # --- Free-cash-flow yield ---
        market_cap = info.get("marketCap")
        fcf        = info.get("freeCashflow")
        fcf_yield  = None
        if market_cap and fcf and float(market_cap) > 0:
            fcf_yield = round((float(fcf) / float(market_cap)) * 100, 2)

        # --- Dividend ---
        div_yield  = pct(info.get("dividendYield"))
        payout_rat = pct(info.get("payoutRatio"))

        result = {
            "ticker":        ticker.upper(),
            "company_name":  info.get("longName", ticker.upper()),
            "current_price": _safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
            "market_cap_M":  _millions(info.get("marketCap")),
            "52_week_high":  _safe_float(info.get("fiftyTwoWeekHigh")),
            "52_week_low":   _safe_float(info.get("fiftyTwoWeekLow")),
            "valuation": {
                "pe_trailing": pe_trailing, "pe_forward": pe_forward, "pb_ratio": pb_ratio,
                "ps_ratio": ps_ratio, "ev_ebitda": ev_ebitda, "ev_revenue": ev_revenue,
            },
            "profitability": {
                "roe_pct": roe, "roa_pct": roa, "net_margin_pct": net_margin,
                "gross_margin_pct": gross_margin, "op_margin_pct": op_margin,
            },
            "leverage": {
                "current_ratio": current_ratio, "quick_ratio": quick_ratio, "debt_to_equity": debt_to_eq,
            },
            "growth": {
                "revenue_yoy_pct":     revenue_growth,
                "revenue_growth_3y":   pct(info.get("revenueGrowth")),
                "earnings_growth_yoy": pct(info.get("earningsGrowth")),
                "earnings_quarterly":  pct(info.get("earningsQuarterlyGrowth")),
            },
            "cash_flow": {
                "fcf_yield_pct":    fcf_yield,
                "free_cash_flow_M": _millions(info.get("freeCashflow")),
                "operating_cf_M":   _millions(info.get("operatingCashflow")),
            },
            "dividend": {
                "yield_pct": div_yield, "payout_ratio": payout_rat,
                "annual_div": _safe_float(info.get("dividendRate")),
            },
        }
        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})
