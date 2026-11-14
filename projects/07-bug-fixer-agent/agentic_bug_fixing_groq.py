"""
Agentic Bug Fixing - Groq version
=============================================
Author: Shivank Agarwal

WHAT THIS PROGRAM DOES (one line)
    It runs a Python function. If the function crashes, an AI agent rewrites the
    function so it handles the error, then runs it again — in a loop — until it works.

HOW IT WORKS (the "agent loop")

       START
         |
         v
   +-----------------------+   no error /
   | code execution node   |-----------------> END
   +-----------------------+   max retries
         |            ^
         | error      |
         v            |
   +-----------------------+
   |   bug fixing node     |
   +-----------------------+

RUN IT
    python projects/07-bug-fixer-agent/agentic_bug_fixing_groq.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from agentic_bug_fixing_openai import (
    SAMPLE_BUGS,
    BugFixState,
    code_execution_node,
    extract_code_and_diagnosis,
    should_continue,
)

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def bug_fixing_node_groq(state: BugFixState) -> dict:
    """Diagnose the traceback and rewrite the Python code using Groq."""
    iteration = state.get("iteration", 0) + 1
    code = state["code"]
    error = state["error"]
    trace = list(state.get("trace", []))

    print(f"\n[Iteration {iteration}] Running bug_fixing_node (Groq: {DEFAULT_GROQ_MODEL})...")

    system_prompt = (
        "You are an expert Python debugging agent.\n"
        "Given a Python script (containing a function and its verification assertions) "
        "and the exact exception traceback it raised:\n"
        "1. Diagnose the root cause of the bug (and any other latent bugs visible in the function).\n"
        "2. Rewrite the function so all verification assertions pass.\n"
        "3. NEVER delete, weaken, or modify the `assert` statements at the bottom — only fix the implementation!\n\n"
        "Respond in this exact format:\n"
        "DIAGNOSIS: <one or two sentences explaining the root cause and fix>\n"
        "```python\n"
        "<complete runnable Python script including the original assertions>\n"
        "```"
    )
    user_prompt = (
        f"### Current Python Code\n```python\n{code}\n```\n\n"
        f"### Exception Traceback\n```text\n{error}\n```\n\n"
        "Please diagnose the bug and provide the complete fixed Python code."
    )

    llm = ChatGroq(model=DEFAULT_GROQ_MODEL, temperature=0)
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    content = response.text if hasattr(response, "text") else str(response.content)
    diagnosis, fixed_code = extract_code_and_diagnosis(content)

    print(f"  → Diagnosis: {diagnosis}")
    trace.append(
        {
            "iteration": iteration,
            "node": "bug_fixing_node",
            "diagnosis": diagnosis,
            "fixed_code": fixed_code,
        }
    )
    return {
        "code": fixed_code,
        "iteration": iteration,
        "diagnosis": diagnosis,
        "trace": trace,
    }


def build_bug_fixing_graph_groq():
    """Compile the LangGraph StateGraph for the Groq bug-fixing loop."""
    graph = StateGraph(BugFixState)
    graph.add_node("code_execution_node", code_execution_node)
    graph.add_node("bug_fixing_node", bug_fixing_node_groq)

    graph.add_edge(START, "code_execution_node")
    graph.add_conditional_edges(
        "code_execution_node",
        should_continue,
        {
            "fix_bug": "bug_fixing_node",
            "end": END,
        },
    )
    graph.add_edge("bug_fixing_node", "code_execution_node")
    return graph.compile()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic Bug Fixing — Groq + LangGraph")
    parser.add_argument(
        "--sample",
        choices=list(SAMPLE_BUGS.keys()),
        default="division_and_types",
        help="Built-in buggy sample to run (default: division_and_types)",
    )
    parser.add_argument("--max-retries", type=int, default=3, help="Max repair iterations (default: 3)")
    args = parser.parse_args()

    sample = SAMPLE_BUGS[args.sample]
    initial_code = sample["code"]
    desc = sample["description"]

    print("=" * 72)
    print("  AGENTIC BUG FIXING (Groq + LangGraph)")
    print(f"  Model : {DEFAULT_GROQ_MODEL}")
    print(f"  Target: {desc}")
    print("=" * 72)

    app = build_bug_fixing_graph_groq()
    final_state = app.invoke(
        {
            "code": initial_code,
            "function_name": desc,
            "error": None,
            "output": "",
            "iteration": 0,
            "max_retries": args.max_retries,
            "diagnosis": "",
            "trace": [],
        }
    )

    print("\n" + "=" * 72)
    if final_state.get("error") is None:
        print(f"  STATUS : FIXED in {final_state.get('iteration', 0)} iteration(s)")
        print(f"  SUMMARY: {final_state.get('diagnosis', '')}")
        print("=" * 72)
        print("\n--- Final Fixed Code ---")
        print(final_state["code"])
    else:
        print(f"  STATUS : FAILED after {final_state.get('iteration', 0)} iteration(s)")
        print("=" * 72)
        print(final_state["error"])


if __name__ == "__main__":
    main()
