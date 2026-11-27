"""Shared task, prompt and MOCK data for the four-framework comparison (section 3.3 of the notes).

Same model, same two tools, same prompt, same mock data — only the framework changes.
"""
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-5-mini"

# Mock data, so every framework sees exactly the same numbers
MOCK_STOCKS = {
    "AAPL": {"company": "Apple Inc.", "price": 195.30, "eps": 6.67},
    "JPM":  {"company": "JPMorgan Chase & Co.", "price": 148.70, "eps": 12.61},
}

system_message = (
    "You are a financial analyst. Use the tools to fetch each company's price and EPS, "
    "compute each P/E ratio with the compute_pe_ratio tool (never by yourself), "
    "then write a short comparison memo for an investor."
)

input_message = (
    "Fetch Apple's (AAPL) and JPMorgan's (JPM) price and EPS, compute their P/E ratios, "
    "and write a short comparison memo."
)


def get_stock_data(ticker: str) -> dict:
    """Return the current price and trailing EPS for a stock ticker (mock data)."""
    data = MOCK_STOCKS.get(ticker.upper())
    if data is None:
        return {"error": f"No data for {ticker}"}
    return {"ticker": ticker.upper(), **data}


def compute_pe_ratio(price: float, eps: float) -> dict:
    """Compute the price-to-earnings ratio: price divided by earnings per share."""
    if eps <= 0:
        return {"error": "P/E is not meaningful when EPS is zero or negative"}
    return {"pe_ratio": round(price / eps, 1)}
