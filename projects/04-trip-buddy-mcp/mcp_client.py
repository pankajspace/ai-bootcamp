"""
mcp_client.py
─────────────
MCP Client that spawns `mcp_server.py` over stdio, discovers tools dynamically,
fetches RAG travel tips via MCP, and runs the ReAct agent loop (based on trip_08_full_agent.py).
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")
MAX_STEPS = 10

SYSTEM = """You are Trip Buddy, a cheerful trip planner for groups of friends travelling from Bengaluru.

When the user asks about a trip:
1. Use db_lookup to fetch the place's prices
2. Use compute_trip_cost for exact arithmetic (never do the maths yourself)
3. Give a clear answer: can they afford it, cost per person, and 1-2 useful tips
If the number of friends or nights is missing, ask for it before calculating.

When the user asks to list places, call list_destinations.

Travel notebook (use this for tips and warnings):
{rag_context}"""

# Tools exposed to the LLM for the ReAct loop
AGENT_TOOL_NAMES = {"db_lookup", "list_destinations", "compute_trip_cost", "evaluate_trip_plan"}


def get_server_params() -> StdioServerParameters:
    """Build stdio server parameters pointing to mcp_server.py."""
    server_script = str(Path(__file__).with_name("mcp_server.py"))
    return StdioServerParameters(command=sys.executable, args=[server_script])


def to_openai_tools(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    """Convert MCP tool schemas into OpenAI function-calling format for ChatOpenAI.bind_tools()."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in mcp_tools
        if t.name in AGENT_TOOL_NAMES
    ]


def _build_llm(openai_tools: list[dict[str, Any]]):
    """Initialize ChatOpenAI and bind the MCP-discovered tool schemas."""
    if MODEL.startswith(("gpt-6", "gpt-5", "o1", "o3", "o4")):
        base = ChatOpenAI(model=MODEL, reasoning_effort="none")
    else:
        base = ChatOpenAI(model=MODEL, temperature=0)
    return base.bind_tools(openai_tools)


def _extract_tool_text(call_result: Any) -> str:
    """Extract text payload from an MCP CallToolResult."""
    if not call_result or not getattr(call_result, "content", None):
        return "{}"
    parts = [getattr(block, "text", str(block)) for block in call_result.content]
    return "\n".join(parts)


async def call_mcp_tool(tool_name: str, tool_args: dict[str, Any]) -> Any:
    """Directly call a single tool on the MCP server over stdio."""
    server_params = get_server_params()
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            text = _extract_tool_text(result)
            try:
                return json.loads(text)
            except Exception:
                return text


async def run_agent_async(user_message: str) -> str:
    """Connect to the MCP server, retrieve RAG tips, and run the ReAct tool-calling loop over MCP."""
    server_params = get_server_params()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Retrieve RAG context from ChromaDB via the MCP server
            rag_res = await session.call_tool(
                "retrieve_travel_tips",
                {"query": user_message, "n": 3},
            )
            rag_context = _extract_tool_text(rag_res)

            # 2. Discover available tools from the MCP server
            mcp_tools = (await session.list_tools()).tools
            openai_tools = to_openai_tools(mcp_tools)
            llm = _build_llm(openai_tools)

            messages = [
                SystemMessage(content=SYSTEM.format(rag_context=rag_context)),
                HumanMessage(content=user_message),
            ]

            # 3. ReAct loop: Reason -> Act (via MCP session.call_tool) -> Observe
            for _ in range(MAX_STEPS):
                response = await llm.ainvoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    return response.text if hasattr(response, "text") else str(response.content)

                for tc in response.tool_calls:
                    print(f"  [mcp-client -> tool] {tc['name']}({tc['args']})")
                    mcp_result = await session.call_tool(tc["name"], tc["args"])
                    tool_output = _extract_tool_text(mcp_result)
                    messages.append(
                        ToolMessage(
                            content=tool_output,
                            tool_call_id=tc["id"],
                        )
                    )

    return "I had to stop after too many steps. Try asking about one place at a time."


def run_agent(user_message: str) -> str:
    """Synchronous entry point for the Gradio chatbot and CLI scripts."""
    return asyncio.run(run_agent_async(user_message))


if __name__ == "__main__":
    print("=== Testing Direct MCP Tool Call (db_lookup) ===")
    goa = asyncio.run(call_mcp_tool("db_lookup", {"place": "Goa"}))
    print(goa)

    print("\n=== Testing Direct MCP Tool Call (compute_trip_cost) ===")
    cost = asyncio.run(
        call_mcp_tool(
            "compute_trip_cost",
            {
                "travel_cost_per_person": 2800,
                "room_price_per_night": 3000,
                "daily_spend_per_person": 1500,
                "people": 4,
                "nights": 3,
                "budget_per_person": 12000,
            },
        )
    )
    print(cost)

