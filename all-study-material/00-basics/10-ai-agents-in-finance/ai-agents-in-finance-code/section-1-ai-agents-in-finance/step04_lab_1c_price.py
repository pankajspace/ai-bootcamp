"""Lab 1C · "What's NVIDIA trading at?" — without and with an agent."""
import os

import yfinance as yf
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Without an agent: a plain LLM call can only guess from its training data
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
response = client.responses.create(model="gpt-4.1", input="What is the last price of NVIDIA.")
print("Plain LLM call:\n", response.output_text, "\n")


# Step 1 · a normal Python function plus one decorator
@function_tool                                    # turns this function into a tool the LLM can call
def get_latest_stock_price(symbol: str) -> dict:
    """Fetch the current stock price for the given symbol."""   # the LLM reads this to decide when to use it
    ticker = yf.Ticker(symbol)                    # a handle for one stock, e.g. "NVDA"
    hist = ticker.history(period="1d")            # a table of the last trading day
    latest_close = hist["Close"].iloc[-1]         # column "Close", last row  → latest price
    latest_date = hist.index[-1]                  # label of that last row    → its date
    return {"price": float(latest_close), "date": str(latest_date.date())}


# Step 2 · the agent, then run it
stock_price_agent = Agent(
    name="Stock Price Agent",                                          # a label, shows up in logs
    instructions="Fetch Historical prices for a given stock symbol",   # its job description
    model="gpt-4.1",                                                   # the brain
    tools=[get_latest_stock_price],                                    # what it may call
)

output = Runner.run_sync(                                              # run_sync: no 'await' needed
    starting_agent=stock_price_agent,
    input="What is today's date, and what is the current stock price of Nvidia?",
)
print("With an agent:\n", output.final_output)
