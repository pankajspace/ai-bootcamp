"""Lab 2B · Working memory: two turns on the same notepad (an SQLite session)."""
import asyncio

from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv

load_dotenv()

# Step 1 · the agent
portfolio_agent = Agent(
    name="Portfolio Rebalancing Agent",
    model="gpt-4o-mini",
    instructions="""You are a Portfolio Rebalancing Agent for a professional investor.
Your goal is to propose clear, explainable rebalancing actions that keep the
portfolio aligned with the target risk/return profile and constraints.
Your role
- Analyze the current portfolio (weights, asset classes, sectors, factors, cash).
- Incorporate market regime information (volatility, trends, macro environment).
- Compare current allocation to:
  - Target allocation or risk budget (if provided),
  - Or to a reasonably diversified allocation based on the information you have.
- Propose specific rebalancing trades with approximate percentage changes and short rationales.
- Prioritize diversification, risk control, and alignment with the investor's objectives.
- Keep answers concise and structured, and state assumptions when information is missing.
- Treat the allocation provided in the user's prompt as the portfolio's current allocation.
Always explain your reasoning.""",
)


async def run_working_memory() -> list[tuple[str, str]]:
    """Run the two-turn conversation and return it as clean (role, text) pairs."""
    # Step 2 · create the notepad (the session)
    session_ptf_rebal = SQLiteSession("conversation_ptf")    # a fresh notepad named "conversation_ptf"
    # Same, but saved in a file so it survives a restart:
    # session_ptf_rebal = SQLiteSession("conversation_ptf", "portfolio_sessions.db")

    # Step 3 · two turns, same notepad
    input_user_1 = """Current Market Situation:
- Volatility Regime: high
- Market Trend: declining
Current Portfolio State:
- Portfolio: {"stocks": 0.70, "bonds": 0.20, "cash": 0.10}
What rebalancing action should I take?"""

    output_1 = await Runner.run(
        starting_agent=portfolio_agent,
        input=input_user_1,
        session=session_ptf_rebal,      # read what's on the notepad, then write this turn onto it
    )
    print(output_1.final_output)        # suggests ~50% stocks / 40% bonds / 10% cash (defensive)

    input_user_2 = "In this case, I'm reducing equity to 50%, increasing bonds to 35% and cash to 15%."
    output_2 = await Runner.run(
        starting_agent=portfolio_agent,
        input=input_user_2,
        session=session_ptf_rebal,      # SAME notepad → the agent still knows the 70/20/10 starting point
    )
    print(output_2.final_output)

    # Step 4 · read the notepad back (simplified, same result)
    all_items = await session_ptf_rebal.get_items()    # everything on the notepad, oldest first
    conversation_history = []                           # we'll fill this with (role, text) pairs

    for i, msg in enumerate(all_items, 1):              # i counts 1, 2, 3 … (only for printing)
        role = msg.get("role", "unknown")               # "user" or "assistant"; tool-call items have no role
        content = msg.get("content", "")

        if role == "user":
            text = content                              # a letter: already a string
        elif role == "assistant":
            text = content[0]["text"]                   # an envelope: open it, take page 0's text
        else:
            continue                                    # skip tool calls and other item types

        print(f"{i}. {role}: {text}")
        print("--" * 50)
        conversation_history.append((role, text))       # save a clean (role, text) pair

    return conversation_history


if __name__ == "__main__":
    asyncio.run(run_working_memory())
