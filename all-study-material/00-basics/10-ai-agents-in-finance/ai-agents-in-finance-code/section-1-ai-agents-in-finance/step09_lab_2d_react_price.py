"""Lab 2D · A ReAct agent (LlamaIndex): stream the Thought → Action → Observation loop."""
import asyncio
import os

import yfinance as yf
from dotenv import load_dotenv
from llama_index.core.agent.workflow import AgentStream, ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


# Step 1 · the tool and the agent
def get_latest_price(ticker_symbol: str):
    """Fetch the latest price for the given ticker symbol."""
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1d", interval="1m")         # today, one row per MINUTE
    if not data.empty:                                         # did any rows come back?
        latest_row = data.iloc[-1]                             # the most recent minute
        return {
            "ticker": ticker_symbol,
            "datetime": latest_row.name.strftime("%Y-%m-%d %H:%M"),   # .name = this row's label = its timestamp
            "price": float(latest_row["Close"]),
        }
    else:
        return {"error": f"No data found for ticker: {ticker_symbol}"}  # the agent can read this and react

tools = [FunctionTool.from_defaults(get_latest_price)]       # LlamaIndex's way to wrap a function as a tool

agent_prices = ReActAgent(
    llm=OpenAI(model="gpt-4o", api_key=OPENAI_API_KEY),
    tools=tools,
    timeout=120,              # give up after 120 s instead of hanging forever
    verbose=False,
)


# Step 2 · run it and stream the thinking
async def main():
    handler = agent_prices.run("What is the last price of Apple?")   # start the job, get a tracking handle

    async for ev in handler.stream_events():       # live updates while the agent works
        if isinstance(ev, AgentStream):            # only the "text chunk" events
            print(ev.delta, end="", flush=True)    # print each new chunk on the same line, immediately

    response = await handler                       # wait for the final, complete answer
    print("\n\nFinal answer:", response)


if __name__ == "__main__":
    asyncio.run(main())
