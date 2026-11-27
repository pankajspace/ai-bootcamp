"""
Section 7 lab — extension: analyse a whole portfolio IN PARALLEL
================================================================
Style: PARALLELIZATION wrapped around the SEQUENTIAL PIPELINE from step01_health_analyzer.py.
Five independent copies of the 4-agent pipeline run at the same time, one per company.

How to run (same .env as step01_health_analyzer.py):
    python step02_portfolio_parallel.py
    python step02_portfolio_parallel.py AAPL MSFT KO

Cost: about 5 × one single-company run.
"""

import asyncio
import sys
import time

from step01_health_analyzer import run_analysis

TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA", "JPM"]   # JPM kept on purpose: a bank!


async def analyze_company(ticker: str) -> dict:
    """Run the full 4-agent pipeline for one company and time it."""
    start = time.perf_counter()
    result = await run_analysis(ticker, verbose=False)
    result["seconds"] = time.perf_counter() - start
    return result


async def analyze_portfolio(tickers: list[str]) -> list:
    # gather() starts every pipeline at once and waits for all of them.
    # return_exceptions=True: one company failing becomes ONE bad row,
    # instead of crashing the whole portfolio run.
    return await asyncio.gather(
        *[analyze_company(t) for t in tickers],
        return_exceptions=True,
    )

def print_table(tickers: list[str], results: list, wall: float) -> None:
    print(f"\n{'Ticker':7} {'ROA':>8} {'Current':>8}  {'Profitability band':20} {'Liquidity band':26} {'secs':>5}")
    print("-" * 80)
    total = 0.0
    for ticker, r in zip(tickers, results):
        if isinstance(r, Exception):                       # the degraded row
            print(f"{ticker:7} FAILED → {type(r).__name__}: {r}")
            continue
        total += r["seconds"]
        p, l = r["state"]["profitability"], r["state"]["liquidity"]
        roa, cur = p["roa"]["value_pct"], l["current_ratio"]["value"]
        print(f"{ticker:7} {str(roa) + '%' if roa is not None else 'n/a':>8} "
              f"{cur if cur is not None else 'n/a':>8}  {p['roa']['band']:20} "
              f"{l['current_ratio']['band'][:26]:26} {r['seconds']:5.1f}"
              + ("   ⚠ bank: wrong rubric" if r["state"].get("rubric_warning") else ""))
    print("-" * 80)
    print(f"Wall-clock: {wall:.1f}s   vs   sum of the runs one-by-one: {total:.1f}s")


if __name__ == "__main__":
    tickers = sys.argv[1:] or TICKERS
    t0 = time.perf_counter()
    results = asyncio.run(analyze_portfolio(tickers))
    print_table(tickers, results, time.perf_counter() - t0)
    for ticker, r in zip(tickers, results):
        if not isinstance(r, Exception):
            print(f"\n{'#' * 70}\n{ticker} — final report\n{'#' * 70}\n{r['report']}")
