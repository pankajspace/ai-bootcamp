"""
Agentic Bug Fixing - OpenAI version
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
    python projects/07-bug-fixer-agent/agentic_bug_fixing_openai.py
"""

from __future__ import annotations

import argparse
import io
import os
import re
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

# Load environment variables from project or workspace root
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# =============================================================================
# 1. Shared Graph State
# =============================================================================
class BugFixState(TypedDict, total=False):
    """State passed between nodes in the LangGraph bug-fixing loop."""

    code: str               # Current Python code (function + test calls)
    function_name: str      # Entry function or test snippet description
    error: str | None       # Traceback / error message from the last run (None if passed)
    output: str             # Captured stdout from executing the code
    iteration: int          # Number of fix attempts so far
    max_retries: int        # Maximum repair iterations allowed
    diagnosis: str          # Short root-cause explanation from the agent
    trace: list[dict[str, Any]]  # Execution history across iterations


# =============================================================================
# 2. Sample Buggy Functions for Demonstration
# =============================================================================
SAMPLE_BUGS: dict[str, dict[str, str]] = {
    "division_and_types": {
        "description": "Calculate average order value from mixed/dirty transaction records",
        "code": '''def calculate_average_order(orders):
    """Return the average amount across valid orders, rounded to 2 decimals."""
    total = 0
    for order in orders:
        # Bug 1: amount might be a string like "$45.50" or None
        # Bug 2: key might be missing
        total += order["amount"]
    # Bug 3: ZeroDivisionError when orders is empty or has no valid items
    return round(total / len(orders), 2)


# --- Verification checks ---
assert calculate_average_order([{"amount": 100}, {"amount": 50}]) == 75.0
assert calculate_average_order([{"amount": "$30.00"}, {"amount": None}, {"note": "free"}, {"amount": 10}]) == 20.0
assert calculate_average_order([]) == 0.0
print("All order average assertions passed!")
''',
    },
    "off_by_one_and_key": {
        "description": "Find top N scoring students and compute their grade summary",
        "code": '''def summarize_top_students(students, top_n=3):
    """Return a list of formatted strings for the top_n students by score."""
    # Bug 1: sorting fails if 'score' is missing or None
    ranked = sorted(students, key=lambda s: s["score"], reverse=True)
    results = []
    # Bug 2: IndexError when len(ranked) < top_n
    for i in range(top_n):
        student = ranked[i]
        # Bug 3: KeyError if 'department' is missing (should default to 'General')
        results.append(f"{i + 1}. {student['name']} ({student['department']}): {student['score']}")
    return results


# --- Verification checks ---
sample = [
    {"name": "Asha", "score": 92, "department": "AI"},
    {"name": "Rohan", "score": None},
    {"name": "Meera", "score": 88},
]
out = summarize_top_students(sample, top_n=5)
assert out == [
    "1. Asha (AI): 92",
    "2. Meera (General): 88",
    "3. Rohan (General): 0",
], f"Unexpected output: {out}"
print("Top student summary assertions passed!")
''',
    },
}


# =============================================================================
# 3. Helper: Build LLM & Strip Markdown Code Fences
# =============================================================================
def build_llm(model: str = DEFAULT_MODEL) -> ChatOpenAI:
    if model.startswith(("gpt-6", "gpt-5", "o1", "o3", "o4")):
        return ChatOpenAI(model=model, reasoning_effort="none")
    return ChatOpenAI(model=model, temperature=0)


def extract_code_and_diagnosis(raw_response: str) -> tuple[str, str]:
    """Extract DIAGNOSIS text and Python code block from LLM response."""
    diagnosis = ""
    diag_match = re.search(r"DIAGNOSIS:\s*(.+?)(?:\n```|\n\n|$)", raw_response, re.S)
    if diag_match:
        diagnosis = diag_match.group(1).strip()

    fence = re.search(r"```(?:python)?\s*\n(.*?)```", raw_response, re.S)
    if fence:
        code = fence.group(1).strip()
    else:
        code = raw_response.strip()
    return diagnosis or "Diagnosed exception from traceback and patched function.", code


# =============================================================================
# 4. Graph Nodes
# =============================================================================
def code_execution_node(state: BugFixState) -> dict[str, Any]:
    """Execute the current Python code in an isolated namespace and capture errors."""
    code = state["code"]
    iteration = state.get("iteration", 0)
    trace = list(state.get("trace", []))

    stdout_buf = io.StringIO()
    namespace: dict[str, Any] = {"__builtins__": __builtins__}

    print(f"\n[Iteration {iteration}] Running code_execution_node...")
    try:
        with redirect_stdout(stdout_buf):
            exec(compile(code, "<agent_code>", "exec"), namespace)
        output = stdout_buf.getvalue().strip()
        print(f"  ✓ Execution succeeded! Output: {output}")
        trace.append({"iteration": iteration, "node": "code_execution_node", "status": "success", "output": output})
        return {"error": None, "output": output, "trace": trace}
    except Exception as exc:
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        # Filter out outer runner frame for cleaner tracebacks
        clean_tb = "".join(line for line in tb_lines if "agentic_bug_fixing" not in line)
        output = stdout_buf.getvalue().strip()
        print(f"  ✗ Execution failed with {type(exc).__name__}: {exc}")
        trace.append(
            {
                "iteration": iteration,
                "node": "code_execution_node",
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": clean_tb.strip(),
            }
        )
        return {"error": clean_tb.strip(), "output": output, "trace": trace}


def bug_fixing_node(state: BugFixState) -> dict[str, Any]:
    """Diagnose the traceback and rewrite the Python code to fix the bug."""
    iteration = state.get("iteration", 0) + 1
    code = state["code"]
    error = state["error"]
    trace = list(state.get("trace", []))

    print(f"\n[Iteration {iteration}] Running bug_fixing_node (diagnosing & patching)...")

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

    llm = build_llm()
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


# =============================================================================
# 5. Conditional Edge (Router) & Graph Builder
# =============================================================================
def should_continue(state: BugFixState) -> str:
    """Decide whether to stop (no error or max retries reached) or loop to bug_fixing_node."""
    if not state.get("error"):
        return "end"
    if state.get("iteration", 0) >= state.get("max_retries", 3):
        print(f"\n  ! Reached max_retries ({state.get('max_retries', 3)}). Stopping loop.")
        return "end"
    return "fix_bug"


def build_bug_fixing_graph():
    """Compile the LangGraph StateGraph for the agentic bug-fixing loop."""
    graph = StateGraph(BugFixState)

    graph.add_node("code_execution_node", code_execution_node)
    graph.add_node("bug_fixing_node", bug_fixing_node)

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


# =============================================================================
# 6. CLI Entrypoint
# =============================================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic Bug Fixing — OpenAI + LangGraph")
    parser.add_argument(
        "--sample",
        choices=list(SAMPLE_BUGS.keys()),
        default="division_and_types",
        help="Built-in buggy sample to run (default: division_and_types)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Optional path to a local Python file to diagnose and fix in-place",
    )
    parser.add_argument("--max-retries", type=int, default=3, help="Max repair iterations (default: 3)")
    args = parser.parse_args()

    if args.file:
        target_path = Path(args.file).resolve()
        initial_code = target_path.read_text(encoding="utf-8")
        desc = f"Local file: {target_path.name}"
    else:
        target_path = None
        sample = SAMPLE_BUGS[args.sample]
        initial_code = sample["code"]
        desc = sample["description"]

    print("=" * 72)
    print("  AGENTIC BUG FIXING (OpenAI + LangGraph)")
    print(f"  Model : {DEFAULT_MODEL}")
    print(f"  Target: {desc}")
    print("=" * 72)
    print("\n--- Initial Buggy Code ---")
    print(initial_code.strip())

    app = build_bug_fixing_graph()
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
        if final_state.get("diagnosis"):
            print(f"  SUMMARY: {final_state['diagnosis']}")
        print("=" * 72)
        print("\n--- Final Fixed Code ---")
        print(final_state["code"])
        if target_path:
            target_path.write_text(final_state["code"] + "\n", encoding="utf-8")
            print(f"\n[Saved fixed code to {target_path}]")
    else:
        print(f"  STATUS : FAILED after {final_state.get('iteration', 0)} iteration(s)")
        print("=" * 72)
        print(final_state["error"])


if __name__ == "__main__":
    main()
