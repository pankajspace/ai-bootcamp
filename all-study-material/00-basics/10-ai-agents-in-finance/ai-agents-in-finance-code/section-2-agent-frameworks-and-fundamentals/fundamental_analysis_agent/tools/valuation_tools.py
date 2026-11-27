"""tools/valuation_tools.py: a 5-year DCF and a peer-multiples comparison.

The notes print run_dcf_model and _peer_verdict as "simplified sketches" and get_peer_multiples
as "key parts"; the pieces they elide are filled in below and marked "Filled in".
"""
import json

import yfinance as yf
from agents import function_tool

from fundamental_analysis_agent.tools.financial_tools import _safe_float


# Filled in: the notes say "the real tool reads these from yfinance: latest FCF, total debt, cash, shares, price"
def _load_dcf_inputs(ticker: str):
    info = yf.Ticker(ticker.upper()).info
    fcf = _safe_float(info.get("freeCashflow"))
    debt = _safe_float(info.get("totalDebt")) or 0.0
    cash = _safe_float(info.get("totalCash")) or 0.0
    shares = _safe_float(info.get("sharesOutstanding"))
    price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    if not fcf or fcf <= 0:
        raise ValueError(f"No positive free cash flow for {ticker}: a DCF is not meaningful")
    if not shares or not price:
        raise ValueError(f"Missing shares outstanding or price for {ticker}")
    return fcf, debt - cash, shares, price


@function_tool
def run_dcf_model(ticker: str, growth_rate: float, discount_rate: float,
                  terminal_growth_rate: float) -> str:
    """Estimate intrinsic value per share with a 5-year DCF and compare it to the current price."""
    try:
        if discount_rate <= terminal_growth_rate:
            raise ValueError("discount_rate must be higher than terminal_growth_rate")
        fcf, net_debt, shares, price = _load_dcf_inputs(ticker)

        # Step 1 · project free cash flow for 5 years
        fcfs = [fcf * (1 + growth_rate) ** t for t in range(1, 6)]
        # Step 2 · bring each year back to today's money
        pv_fcfs = [f / (1 + discount_rate) ** t for t, f in enumerate(fcfs, start=1)]
        # Step 3 · everything after year 5 as one lump (Gordon growth), also brought back
        terminal_value = fcfs[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
        pv_terminal = terminal_value / (1 + discount_rate) ** 5
        # Step 4 · business value → owners' value → per share
        enterprise_value = sum(pv_fcfs) + pv_terminal
        equity_value = enterprise_value - net_debt
        intrinsic_value = equity_value / shares

        upside = (intrinsic_value / price - 1) * 100
        return json.dumps({"intrinsic_value": round(intrinsic_value, 2), "current_price": price,
                           "upside_pct": round(upside, 1), "verdict": _dcf_verdict(upside)})
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


def _dcf_verdict(upside):
    if upside > 30:   return "SIGNIFICANTLY UNDERVALUED"
    if upside > 15:   return "SLIGHTLY UNDERVALUED"
    if upside >= -15: return "FAIRLY VALUED"
    if upside >= -30: return "SLIGHTLY OVERVALUED"
    return "SIGNIFICANTLY OVERVALUED"


# Filled in: the notes elide how `peers` is chosen ("choose the list `peers` for this sector")
SECTOR_PEERS = {
    "Technology":             ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ORCL"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "TMUS"],
    "Consumer Cyclical":      ["AMZN", "TSLA", "HD", "MCD", "NKE"],
    "Consumer Defensive":     ["WMT", "PG", "KO", "PEP", "COST"],
    "Financial Services":     ["JPM", "BAC", "WFC", "GS", "MS"],
    "Healthcare":             ["JNJ", "UNH", "PFE", "MRK", "ABBV"],
    "Energy":                 ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Industrials":            ["CAT", "HON", "GE", "UPS", "DE"],
    "Utilities":              ["NEE", "DUK", "SO", "D", "AEP"],
    "Real Estate":            ["PLD", "AMT", "EQIX", "SPG", "O"],
    "Basic Materials":        ["LIN", "SHW", "APD", "FCX", "NEM"],
}


@function_tool
def get_peer_multiples(ticker: str) -> str:
    """
    Compare a stock's valuation multiples against its sector peers.
    Fetches P/E, P/B, EV/EBITDA, and P/S ratios for the company and
    a set of sector peers. Returns averages, medians, and highlights
    whether the stock trades at a premium or discount to peers.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
    """
    try:
        stock  = yf.Ticker(ticker.upper())
        info   = stock.info
        sector = info.get("sector")
        peers  = [p for p in SECTOR_PEERS.get(sector, SECTOR_PEERS["Technology"]) if p != ticker.upper()][:5]

        def get_multiples(t: str) -> dict:                  # the same 5 multiples for ANY ticker
            try:
                i = yf.Ticker(t).info
                return {
                    "ticker":     t,
                    "pe":         _safe_float(i.get("trailingPE")),
                    "forward_pe": _safe_float(i.get("forwardPE")),
                    "pb":         _safe_float(i.get("priceToBook")),
                    "ps":         _safe_float(i.get("priceToSalesTrailing12Months")),
                    "ev_ebitda":  _safe_float(i.get("enterpriseToEbitda")),
                    "roe_pct":    round(i.get("returnOnEquity", 0) * 100, 2) if i.get("returnOnEquity") else None,
                }
            except Exception:
                return {"ticker": t, "pe": None, "pb": None, "ps": None, "ev_ebitda": None}

        subject   = get_multiples(ticker.upper())               # our company
        peer_data = [get_multiples(p) for p in peers]           # one dict per peer

        def avg(key: str) -> float | None:                      # peer average, skipping missing values
            vals = [p[key] for p in peer_data if p.get(key) is not None]
            return round(sum(vals) / len(vals), 2) if vals else None

        def median(key: str) -> float | None:                   # Filled in: the docstring promises medians
            vals = sorted(p[key] for p in peer_data if p.get(key) is not None)
            if not vals:
                return None
            mid = len(vals) // 2
            return round(vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2, 2)

        peer_avg = {"pe": avg("pe"), "forward_pe": avg("forward_pe"), "pb": avg("pb"),
                    "ps": avg("ps"), "ev_ebitda": avg("ev_ebitda"), "roe_pct": avg("roe_pct")}

        def premium(subject_val, peer_val) -> str | None:      # "+16.2%" style text
            if subject_val is None or peer_val is None or peer_val == 0:
                return None
            pct = round(((subject_val - peer_val) / peer_val) * 100, 1)
            return f"{'+' if pct >= 0 else ''}{pct}%"

        verdict, weighted_avg = _peer_verdict(subject, peer_avg)   # the verdict is computed in code

        # Filled in: "build `result` with subject, peers, averages, premiums, verdict"
        result = {
            "ticker": ticker.upper(),
            "sector": sector,
            "subject": subject,
            "peers": peer_data,
            "peer_average": peer_avg,
            "peer_median": {k: median(k) for k in ("pe", "forward_pe", "pb", "ps", "ev_ebitda", "roe_pct")},
            "premium_vs_peer_average": {k: premium(subject.get(k), peer_avg.get(k))
                                        for k in ("pe", "forward_pe", "pb", "ps", "ev_ebitda")},
            "peer_verdict": {"weighted_avg_premium_pct": weighted_avg, "verdict": verdict},
        }
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


WEIGHTS = {"forward_pe": 0.30, "ev_ebitda": 0.25, "pe": 0.20, "ps": 0.15, "pb": 0.10}


def _peer_verdict(subject, peer_avg):
    total, weight_used = 0.0, 0.0
    for key, w in WEIGHTS.items():
        s, p = subject.get(key), peer_avg.get(key)
        if s is None or not p:                     # missing on either side → skip this multiple
            continue
        total += w * (s / p - 1) * 100             # premium of this multiple, times its weight
        weight_used += w
    if weight_used == 0:
        return "N/A", None
    weighted_avg = round(total / weight_used, 1)   # re-scale so skipped weights don't count
    if weighted_avg > 30:     verdict = "SIGNIFICANTLY OVERVALUED"
    elif weighted_avg > 15:   verdict = "SLIGHTLY OVERVALUED"
    elif weighted_avg >= -15: verdict = "FAIRLY VALUED"
    elif weighted_avg >= -30: verdict = "SLIGHTLY UNDERVALUED"
    else:                     verdict = "SIGNIFICANTLY UNDERVALUED"
    return verdict, weighted_avg
