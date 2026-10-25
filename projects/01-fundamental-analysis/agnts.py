import os
from strands import Agent
from strands.multiagent import GraphBuilder
from dotenv import load_dotenv, find_dotenv

os =load_dotenv(find_dotenv())

model = os.getenv("OPENAI_MODEL")

orchestrator = Agent(
    name="orchestrator",
    model=model,
    callback_handler=None,
    system_prompt="""

    """,
)

print("✓ All agents created")