"""
Section 8 lab — A minimal walk-forward backtest for the committee
================================================================
Every Friday: run the committee on each stock → open the position it asks for →
hold it until next Friday → record the profit or loss → move one week forward.

How to run
----------
    python step05_backtest.py --dry-run     # FREE: a random stand-in committee tests the plumbing
    python step05_backtest.py               # REAL: ~36 committee runs ≈ 200 LLM calls, a few dollars

⚠ Big caveat (read before trusting any number): the real committee fetches TODAY's
fundamentals and news even when it is "deciding" on a past Friday. That is look-ahead bias.
A research-grade backtest needs point-in-time data (every fetcher takes an as_of_date)
and a window that starts AFTER the training cutoff of every model you use.
"""

from __future__ import annotations

import argparse
import random
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

UNIVERSE = ["TSLA", "MSFT", "NVDA"]
START, END = "2026-07-01", "2026-10-01"   # pick a window after your models' training cutoff


@dataclass
class Trade:
    decision_date: pd.Timestamp
    ticker: str
    action: str            # "BUY" or "SELL"
    size_pct: float        # PM-proposed size, % of NAV
    confidence: int
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float

    @property
    def pnl_pct(self) -> float:                  # the stock's move, signed by direction
        sign = 1 if self.action == "BUY" else -1
        return sign * (self.exit_price / self.entry_price - 1)

    @property
    def weighted_pnl(self) -> float:             # what it did to the WHOLE portfolio
        return (self.size_pct / 100.0) * self.pnl_pct

_ACTION_RE = re.compile(r"ACTION\s*=\s*(BUY|HOLD|SELL)", re.I)
_CONF_RE = re.compile(r"CONFIDENCE\s*=\s*(\d+)", re.I)
_SIZE_RE = re.compile(r"SIZE_PCT\s*=\s*([\d.]+)", re.I)


def parse_decision(committee_result: dict) -> tuple[str, int, float]:
    thesis = committee_result["pm_thesis"]
    a, c, s = _ACTION_RE.findall(thesis), _CONF_RE.findall(thesis), _SIZE_RE.findall(thesis)
    action = a[-1].upper() if a else "HOLD"
    confidence = int(c[-1]) if c else 0
    size_pct = float(s[-1]) if s else 0.0
    final = committee_result["final_decision"].lower()
    if "(risk veto)" in final or "(risk rejected)" in final:
        return "HOLD", confidence, 0.0           # the risk officer ALWAYS wins
    return action, confidence, size_pct

def _price_on_or_before(series: pd.Series, when: pd.Timestamp) -> float | None:
    """Last close on or before a date (Fridays can be holidays)."""
    s = series[series.index <= when]
    return float(s.iloc[-1]) if len(s) else None


def walk_forward(committee_fn, universe, start, end, rebalance_freq="W-FRI"):
    """committee_fn(ticker, as_of) -> committee result dict."""
    rebalance_dates = pd.date_range(start, end, freq=rebalance_freq)
    prices = {}
    for t in universe:
        close = yf.Ticker(t).history(start=start, end=end)["Close"]
        close.index = close.index.tz_localize(None)        # compare dates without time zones
        prices[t] = close

    trades = []
    for i, decision_date in enumerate(rebalance_dates[:-1]):
        exit_date = rebalance_dates[i + 1]                  # hold for exactly one period
        for ticker in universe:
            result = committee_fn(ticker, decision_date)
            action, confidence, size_pct = parse_decision(result)
            if action == "HOLD" or size_pct == 0.0:
                continue                                    # no position, no trade
            entry = _price_on_or_before(prices[ticker], decision_date)
            exit_ = _price_on_or_before(prices[ticker], exit_date)
            if entry is None or exit_ is None:
                continue
            trades.append(Trade(decision_date, ticker, action, size_pct, confidence,
                                entry, exit_date, exit_))
    return trades, rebalance_dates

def equity_curve(trades, rebalance_dates, start_nav=1_000_000.0) -> pd.Series:
    """Portfolio value after each period. Weeks with no trades count as 0% weeks."""
    weekly = pd.Series(0.0, index=rebalance_dates[1:])      # every exit date, default 0%
    for t in trades:
        weekly[t.exit_date] += t.weighted_pnl               # add up all positions that week
    curve = (1 + weekly).cumprod() * start_nav
    return pd.concat([pd.Series([start_nav], index=[rebalance_dates[0]]), curve])


def metrics(curve: pd.Series, trades, periods_per_year: float = 52.0) -> dict:
    rets = curve.pct_change().dropna()
    sharpe = (rets.mean() / rets.std()) * np.sqrt(periods_per_year) if rets.std() > 0 else 0.0
    max_dd = (curve / curve.cummax() - 1).min()             # worst fall from a previous peak
    wins = sum(1 for t in trades if t.pnl_pct > 0)
    return {
        "trades": len(trades),
        "hit_rate": wins / len(trades) if trades else 0.0,
        "cumulative_return": float(curve.iloc[-1] / curve.iloc[0] - 1),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
    }

def live_committee(ticker: str, as_of: pd.Timestamp) -> dict:
    """The real committee. It IGNORES as_of: its fetchers return today's data (look-ahead!)."""
    from step04_investment_committee import run_committee        # imported only when needed
    return run_committee(ticker)


def random_committee(ticker: str, as_of: pd.Timestamp) -> dict:
    """Free stand-in that mimics the committee's output format, to test the harness."""
    rnd = random.Random(f"{ticker}{as_of.date()}")         # same inputs → same 'decision'
    action = rnd.choice(["BUY", "BUY", "HOLD"])
    conf, size = (rnd.randint(50, 80), rnd.choice([1.0, 1.5, 2.0])) if action == "BUY" else (55, 0.0)
    final = "HOLD (risk veto)" if rnd.random() < 0.1 else action
    return {"pm_thesis": f"...\nACTION={action}; CONFIDENCE={conf}; SIZE_PCT={size}",
            "final_decision": final}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="use the free random committee")
    args = ap.parse_args()
    fn = random_committee if args.dry_run else live_committee

    trades, dates = walk_forward(fn, UNIVERSE, START, END)
    curve = equity_curve(trades, dates)
    m = metrics(curve, trades)
    print("=" * 64)
    print(f"Universe        : {', '.join(UNIVERSE)}   ({'DRY RUN' if args.dry_run else 'live committee'})")
    print(f"Window          : {START} to {END}  (weekly, W-FRI)")
    print(f"Trades executed : {m['trades']}")
    print(f"Hit rate        : {m['hit_rate']:.1%}")
    print(f"Cumulative ret. : {m['cumulative_return']:.1%}")
    print(f"Sharpe (annl.)  : {m['sharpe']:.2f}")
    print(f"Max drawdown    : {m['max_drawdown']:.1%}")
    print("=" * 64)
