# tools/financial_data.py — fetch ONE company's numbers and clean them up
import os
import httpx
from common import CompanyMetrics

BASE_URL = "https://api.financialdatasets.ai"


def _pct(part, whole):
    """part ÷ whole as a percent (1 decimal), or None if we can't work it out."""
    if part is None or not whole:
        return None
    return round(part / whole * 100, 1)


async def get_financial_metrics(ticker: str) -> CompanyMetrics:
    headers = {"X-API-KEY": os.environ["FINANCIAL_DATASETS_API_KEY"]}   # ① password
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers,
                                 timeout=30) as client:                 # ② open line
        income_resp = await client.get(                                 # ③ 2 years
            "/financials/income-statements",
            params={"ticker": ticker, "period": "annual", "limit": 2},
        )
        price_resp = await client.get("/prices/snapshot",               # ④ price
                                      params={"ticker": ticker})
    income_resp.raise_for_status()           # ⑤ 401 / 404 / 429 / 500 → error
    price_resp.raise_for_status()

    statements = income_resp.json()["income_statements"]   # ⑥ newest year first
    latest = statements[0]
    prior = statements[1] if len(statements) > 1 else None
    snapshot = price_resp.json()["snapshot"]
    price = snapshot.get("price") or snapshot.get("close")

    revenue = latest.get("revenue")                          # in plain dollars
    eps = latest.get("earnings_per_share")
    growth = None
    if revenue and prior and prior.get("revenue"):           # ⑦ growth needs 2 years
        growth = round((revenue / prior["revenue"] - 1) * 100, 1)

    return CompanyMetrics(                                   # ⑧ the clean form
        ticker=ticker,
        revenue=round(revenue / 1_000_000, 1) if revenue else None,  # → $ millions
        revenue_growth=growth,
        eps=eps,
        gross_margin=_pct(latest.get("gross_profit"), revenue),
        operating_margin=_pct(latest.get("operating_income"), revenue),
        pe_ratio=round(price / eps, 1) if price and eps and eps > 0 else None,
        market_cap=snapshot.get("market_cap"),
    )
