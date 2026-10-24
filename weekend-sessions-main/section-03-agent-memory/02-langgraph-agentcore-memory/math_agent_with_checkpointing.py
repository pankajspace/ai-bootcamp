"""Section 3 · Notebook 2: LangGraph + AgentCore Memory (Amazon Bedrock edition)

Demonstrates session memory for a LangGraph agent using Amazon Bedrock AgentCore
Memory as its checkpointer. Every step of the conversation is saved automatically,
allowing the agent to persist state across turns and isolate different sessions.

Requirements:
    pip install -r requirements.txt

Prerequisites:
    AWS credentials, Bedrock access, and IAM permissions for AgentCore Memory:
    bedrock-agentcore:CreateMemory, CreateEvent, ListEvents, GetMemory, DeleteMemory, etc.

Run:
    python math_agent_with_checkpointing.py
"""

import os
from dotenv import load_dotenv
from bedrock_agentcore.memory import MemoryClient
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph_checkpoint_aws import AgentCoreMemorySaver

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


# Math tools
@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b


def main():
    print(f"Model: {MODEL_ID} | Region: {REGION}")

    # 1. Create (or reuse) the AgentCore Memory resource
    print("\n--- Connecting to AgentCore Memory ---")
    client = MemoryClient(region_name=REGION)
    memory = client.create_or_get_memory(
        name="MathLanggraphAgent",
        description="Short-term memory for the LangGraph math agent",
    )
    memory_id = memory["id"]
    print("Memory ID:", memory_id, "| status:", memory.get("status"))

    try:
        # 2. Configure checkpointer and LLM
        checkpointer = AgentCoreMemorySaver(memory_id, region_name=REGION)
        llm = init_chat_model(MODEL_ID, model_provider="bedrock_converse", region_name=REGION)
        tools = [add, multiply]

        # 3. Build the LangGraph agent
        graph = create_agent(
            model=llm,
            tools=tools,
            system_prompt="You are a helpful assistant. Use the tools for every calculation.",
            checkpointer=checkpointer,
        )

        # 4. Run calculation in session-1
        print("\n" + "=" * 60)
        print("Run 1: First calculation in session-1")
        print("=" * 60)
        config1 = {
            "configurable": {
                "thread_id": "session-1",  # REQUIRED: maps to AgentCore session_id
                "actor_id": "react-agent-1",  # REQUIRED: maps to AgentCore actor_id
            }
        }
        inputs1 = {
            "messages": [
                {
                    "role": "user",
                    "content": "What is 1337 times 515321? Then add 412 and return the value to me.",
                }
            ]
        }
        for chunk in graph.stream(inputs1, stream_mode="updates", config=config1):
            print(chunk)

        # 5. Inspect the saved state
        print("\n" + "=" * 60)
        print("Saved state messages for session-1")
        print("=" * 60)
        for message in graph.get_state(config1).values.get("messages", []):
            print(f"{message.type}: {message.text}")
            print("-" * 40)

        # 6. Checkpoint history
        print("\n" + "=" * 60)
        print("Checkpoint history (most recent first)")
        print("=" * 60)
        for checkpoint in graph.get_state_history(config1):
            print(
                f"Checkpoint {checkpoint.config['configurable']['checkpoint_id']} "
                f"— messages in state: {len(checkpoint.values.get('messages', []))}"
            )

        # 7. Memory persistence — continue session-1
        print("\n" + "=" * 60)
        print("Run 2: Continue session-1 (recalling previous calculation)")
        print("=" * 60)
        inputs2 = {
            "messages": [
                {
                    "role": "user",
                    "content": "What were the first calculations I asked you to do?",
                }
            ]
        }
        for chunk in graph.stream(inputs2, stream_mode="updates", config=config1):
            print(chunk)

        # 8. Session isolation — session-2 starts fresh
        print("\n" + "=" * 60)
        print("Run 3: New session-2 (verifying session isolation)")
        print("=" * 60)
        config2 = {
            "configurable": {
                "thread_id": "session-2",  # new session
                "actor_id": "react-agent-1",  # same actor
            }
        }
        inputs3 = {
            "messages": [
                {
                    "role": "user",
                    "content": "What values did I ask you to multiply and add?",
                }
            ]
        }
        for chunk in graph.stream(inputs3, stream_mode="updates", config=config2):
            print(chunk)

    finally:
        # Clean up the AgentCore Memory resource
        print("\n--- Cleaning up AgentCore Memory resource ---")
        client.delete_memory_and_wait(memory_id=memory_id, max_wait=300, poll_interval=10)
        print("Deleted memory", memory_id)


if __name__ == "__main__":
    main()

