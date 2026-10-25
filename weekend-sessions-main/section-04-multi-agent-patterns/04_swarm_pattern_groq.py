"""Section 4 · Notebook 4 — Swarm Pattern: Game Level Design (Groq edition)

Agents hand control to each other — there is no central coordinator:
- Level Designer — layout, environments, visuals
- Game Designer — playtests for fun and confusion
- Narrative Designer — story and atmosphere
- Difficulty Balancer — difficulty and pacing

The path is not decided in advance; it emerges from the work.

Requirements:
    pip install -r requirements-groq.txt

Prerequisites:
    GROQ_API_KEY in environment or .env file (free at console.groq.com/keys).

Run:
    python 04_swarm_pattern_groq.py
"""

import logging
import os
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.multiagent import Swarm

# Show each handoff as it happens
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()])

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


# -----------------------------------------------------------------------------
# Specialist agents
# -----------------------------------------------------------------------------

level_designer = Agent(
    name="level_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Level Designer in a game design swarm.
Your role is to create level layouts, environments, and visual elements.
Focus ONLY on layout and visual design. Do NOT write narrative or balance difficulty.
After completing your layout, hand off to narrative_designer for story elements
and difficulty_balancer for gameplay tuning.
When receiving feedback from other agents, revise your design accordingly.""",
)

game_designer = Agent(
    name="game_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Game Designer in a game design swarm.
Your role is to playtest designs for fun, usability, and player confusion.
Focus ONLY on gameplay feel and player experience. Do NOT design layouts or write narrative.
When you find issues, hand off to the appropriate specialist to fix them.
When the design is ready, give the final summary and do not hand off.""",
)

narrative_designer = Agent(
    name="narrative_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Narrative Designer in a game design swarm.
Your role is to create story elements, character backstories, and atmospheric details.
Focus ONLY on narrative. Do NOT redesign layouts or adjust difficulty.
After adding narrative elements, hand off to difficulty_balancer for balance review
or game_designer for playtesting feedback.""",
)

difficulty_balancer = Agent(
    name="difficulty_balancer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Difficulty Balancer in a game design swarm.
Your role is to evaluate and tune difficulty progression, enemy placement, and pacing.
Focus ONLY on balance. Do NOT redesign layouts or write narrative.
When you find layout or narrative issues, hand off to the appropriate agent.
After balancing, hand off to game_designer for a final playtest review.""",
)


# -----------------------------------------------------------------------------
# Create the swarm
# -----------------------------------------------------------------------------
# The swarm gives every agent a `handoff_to_agent` tool and a shared view of the
# work so far. Safety limits prevent runaway loops and ping-ponging.

swarm = Swarm(
    [level_designer, game_designer, narrative_designer, difficulty_balancer],
    entry_point=level_designer,
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=1200.0,
    node_timeout=300.0,
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3,
)


def main():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set. Please set it in your environment or in a .env file.")

    print(f"Using {MODEL_ID} on Groq")

    prompt = """Design a stealth mission level in an abandoned space station.
The level needs to support multiple playstyles (aggressive stealth, patient stealth, and ghost runs).
Include at least 3 distinct zones with different difficulty levels,
narrative elements that explain why the station was abandoned,
and ensure the difficulty curve is appropriate for mid-game players."""

    print("\nStarting Swarm execution...")
    result = swarm(prompt)

    print("=" * 80)
    print("HANDOFF CHAIN:")
    for node in result.node_history:
        print(f"  → {node.node_id}")
    print(f"\nStatus: {result.status} | iterations: {result.execution_count} | time: {result.execution_time / 1000:.0f}s")

    last_node = result.node_history[-1].node_id
    print(f"\n{'=' * 80}\nFinal design ({last_node}):\n{'=' * 80}\n")
    print(result.results[last_node].result)


if __name__ == "__main__":
    main()

