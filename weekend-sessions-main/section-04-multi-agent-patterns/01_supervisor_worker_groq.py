"""Section 4 · Notebook 1 — Supervisor–Worker Pattern (Groq edition)

A market-research assistant:
- News Agent — recent news and developments (Tavily web search)
- Financial Agent — prices, history and fundamentals (Yahoo Finance via yfinance)
- Sentiment Agent — what investors are saying (Tavily web search)
- Supervisor — splits the question, delegates to the workers, and writes one recommendation

```
                    ┌──────────────┐
   question ──────► │  Supervisor  │ ──────► one combined answer
                    └──────┬───────┘
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     News Agent     Financial Agent   Sentiment Agent
```

Requirements:
    pip install -r requirements-groq.txt

Prerequisites:
    GROQ_API_KEY in environment or .env file (free at console.groq.com/keys).
    TAVILY_API_KEY in environment or .env file (free key at tavily.com).
    ALPHA_VANTAGE_API_KEY is optional.

Run:
    python 01_supervisor_worker_groq.py
"""

import os
from dotenv import find_dotenv, load_dotenv
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from strands import Agent, ToolContext, tool
from strands.models.openai import OpenAIModel
from strands_tools.tavily import tavily_search

load_dotenv(find_dotenv())

MODEL_ID = os.getenv("GROQ_MODEL_ID", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = OpenAIModel(
    client_args={
        "api_key": GROQ_API_KEY,
        "base_url": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        "max_retries": 5,
    },
    model_id=MODEL_ID,
    # Groq reasoning models stream their thinking by default; hide it so only the answer prints.
    params={"extra_body": {"include_reasoning": False}},
)


# Groq's free tier rejects any single request over 8,000 tokens ("Request too large").
# A default Tavily search returns ~3,700 tokens, so a worker that searches twice overflows.
# The workers use this wrapper instead: the same Tavily search, top 3 results (~1,100 tokens),
# at most twice per task, because every result is resent with the worker's next request.
@tool(context=True)
async def web_search(query: str, tool_context: ToolContext, time_range: str = "month") -> dict | str:
    """Search the web with Tavily and return the top 3 results.

    Args:
        query: What to search for
        time_range: How recent the results should be: day, week, month or year
    """
    searches = tool_context.agent.state.get("searches") or 0  # as_tool() resets state for each task
    if searches >= 2:
        return "Search limit reached: answer with the results you already have."
    tool_context.agent.state.set("searches", searches + 1)
    return await tavily_search(query=query, max_results=3, time_range=time_range)


# -----------------------------------------------------------------------------
# Custom financial tools (Yahoo Finance)
# -----------------------------------------------------------------------------

def _num(value, money=False, pct=False):
    """Format numbers safely — Yahoo sometimes leaves fields empty."""
    if not isinstance(value, (int, float)):
        return "N/A"
    if pct:
        return f"{value * 100:.2f}%"
    return f"${value:,.2f}" if money else f"{value:,.2f}"


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price and key metrics using Yahoo Finance.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'MSFT')
    """
    try:
        info = yf.Ticker(symbol).info
        return (
            f"Stock: {symbol}\n"
            f"Current Price: {_num(info.get('currentPrice') or info.get('regularMarketPrice'), money=True)}\n"
            f"Market Cap: {_num(info.get('marketCap'), money=True)}\n"
            f"P/E Ratio: {_num(info.get('trailingPE'))}\n"
            f"52 Week High: {_num(info.get('fiftyTwoWeekHigh'), money=True)}\n"
            f"52 Week Low: {_num(info.get('fiftyTwoWeekLow'), money=True)}\n"
            f"Average Volume: {_num(info.get('averageVolume'))}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}"
        )
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {e}"


@tool
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """Get historical stock price data.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        period: One of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        hist = yf.Ticker(symbol).history(period=period)
        if hist.empty:
            return f"No historical data available for {symbol}"
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        change_pct = (end_price - start_price) / start_price * 100
        return (
            f"Historical Data for {symbol} ({period}):\n"
            f"Starting Price: ${start_price:.2f}\n"
            f"Ending Price: ${end_price:.2f}\n"
            f"Change: {change_pct:+.2f}%\n"
            f"Highest: ${hist['High'].max():.2f}\n"
            f"Lowest: ${hist['Low'].min():.2f}\n"
            f"Average Volume: {hist['Volume'].mean():,.0f}\n\n"
            f"Recent 5-day trend:\n{hist[['Close', 'Volume']].tail().to_string()}"
        )
    except Exception as e:
        return f"Error fetching historical data for {symbol}: {e}"


@tool
def get_company_financials(symbol: str) -> str:
    """Get company financial metrics: revenue, margins, growth and leverage.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    """
    try:
        info = yf.Ticker(symbol).info
        return (
            f"Financial Metrics for {symbol}:\n"
            f"Revenue: {_num(info.get('totalRevenue'), money=True)}\n"
            f"Revenue Growth: {_num(info.get('revenueGrowth'), pct=True)}\n"
            f"Gross Profit: {_num(info.get('grossProfits'), money=True)}\n"
            f"Profit Margin: {_num(info.get('profitMargins'), pct=True)}\n"
            f"Operating Margin: {_num(info.get('operatingMargins'), pct=True)}\n"
            f"EBITDA: {_num(info.get('ebitda'), money=True)}\n"
            f"Earnings Growth: {_num(info.get('earningsGrowth'), pct=True)}\n"
            f"Return on Equity: {_num(info.get('returnOnEquity'), pct=True)}\n"
            f"Debt to Equity: {_num(info.get('debtToEquity'))}\n"
            f"Free Cash Flow: {_num(info.get('freeCashflow'), money=True)}"
        )
    except Exception as e:
        return f"Error fetching financial data for {symbol}: {e}"


# -----------------------------------------------------------------------------
# Optional: Alpha Vantage tool
# -----------------------------------------------------------------------------

@tool
def get_alpha_vantage_quote(symbol: str) -> str:
    """Get the latest stock quote from the Alpha Vantage API.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    """
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not key:
        return "ALPHA_VANTAGE_API_KEY is not set."
    ts = TimeSeries(key=key, output_format="pandas")
    data, _ = ts.get_quote_endpoint(symbol=symbol)
    return data.to_string()


financial_tools = [get_stock_price, get_stock_history, get_company_financials, web_search]
if os.getenv("ALPHA_VANTAGE_API_KEY"):
    financial_tools.append(get_alpha_vantage_quote)


# -----------------------------------------------------------------------------
# Worker agents
# -----------------------------------------------------------------------------

news_agent = Agent(
    name="news_agent",
    description="Researches recent news and developments about companies and industries.",
    model=model,
    system_prompt="""You are a news research specialist. Search for recent news and developments about companies and industries.

When searching:
- Focus on recent news (use time_range='week' or 'month')
- Prefer reliable sources such as major news outlets
- Summarize key developments and trends
- Include specific facts, dates, and figures when available
- Make at most two web_search calls: Groq's free tier caps each request at 8,000 tokens""",
    tools=[web_search],
    callback_handler=None,
)

financial_agent = Agent(
    name="financial_agent",
    description="Analyzes stock prices, price history, and company financial metrics.",
    model=model,
    system_prompt="""You are a financial analysis specialist. Analyze financial metrics, stock performance, and company valuations.

When analyzing:
- Use get_stock_price for current prices and key metrics
- Use get_stock_history for price trends
- Use get_company_financials for revenue, earnings, and growth
- Compare companies within the same sector and give specific numbers
- Look at no more than three companies, and use web_search at most once""",
    tools=financial_tools,
    callback_handler=None,
)

sentiment_agent = Agent(
    name="sentiment_agent",
    description="Analyzes market and investor sentiment from forums, social media, and commentary.",
    model=model,
    system_prompt="""You are a market sentiment analyst. Analyze market sentiment from social media, forums, and investor discussions.

When analyzing sentiment:
- Look for both bullish and bearish opinions
- Identify common concerns and excitement points
- Distinguish retail from institutional sentiment
- Summarize the overall market mood
- Make at most two web_search calls: Groq's free tier caps each request at 8,000 tokens""",
    tools=[web_search],
    callback_handler=None,
)


# -----------------------------------------------------------------------------
# Supervisor agent
# -----------------------------------------------------------------------------

supervisor = Agent(
    name="research_supervisor",
    model=model,
    system_prompt="""You are a market research coordinator. When asked about investment opportunities:

1. Work out what information is needed
2. Delegate to the specialist agents:
   - news_agent: recent developments and industry news
   - financial_agent: financial metrics and performance data
   - sentiment_agent: market sentiment and investor opinions
3. Synthesize their responses into one balanced recommendation

This is educational analysis, not financial advice — say so briefly at the end.
Do not ask the user clarifying questions: pick sensible defaults (for example, the sector's leading companies) and delegate straight away.""",
    tools=[news_agent.as_tool(), financial_agent.as_tool(), sentiment_agent.as_tool()],
)


def main():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set. Please set it in your environment or in a .env file.")

    print(f"Using {MODEL_ID} on Groq")

    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  TAVILY_API_KEY not set — the news and sentiment agents cannot search the web.")
    else:
        print("✓ TAVILY_API_KEY is configured")

    if not os.getenv("ALPHA_VANTAGE_API_KEY"):
        print("ℹ️  ALPHA_VANTAGE_API_KEY not set — financial data comes from yfinance (free, no key).")
    else:
        print("✓ ALPHA_VANTAGE_API_KEY is configured")

    print("\n--- Testing get_stock_price tool directly ---")
    print(get_stock_price(symbol="AAPL"))

    # Run the multi-agent system
    question = "Should I invest in electric vehicle companies?"
    print(f"\nQuestion: {question}\n")
    response = supervisor(question)
    print(response)

    # Try different questions
    questions = [
        "What's the outlook for renewable energy stocks?",
        # "Is the semiconductor industry a good investment right now?",  # see the Groq note in the notebook
    ]

    for q in questions:
        print(f"\n{'=' * 80}\nQuestion: {q}\n{'=' * 80}")
        supervisor.messages = []  # start each question fresh to stay within token limits
        resp = supervisor(q)
        print(resp)


if __name__ == "__main__":
    main()

