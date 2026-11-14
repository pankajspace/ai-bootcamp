"""
LangGraph state machine for diagnosing and fixing bugs in a local Python codebase.

Graph topology:
    START ──► execute_tests_node ──┬── (passed or max_retries) ──► END
                                   └── (failed) ──► diagnose_bug_node ──► apply_patch_node ──► execute_tests_node
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from .executor import collect_workspace_files, compute_unified_diff, run_target
from .schemas import BugDiagnosis, ExecutionResult, PatchRecord

# Load environment variables from project or workspace root
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class CodebaseFixState(TypedDict, total=False):
    """Shared state across the LangGraph bug diagnosis and repair loop."""

    workspace_dir: str
    command: list[str] | None
    iteration: int
    max_retries: int
    dry_run: bool
    last_execution: ExecutionResult | None
    last_diagnosis: BugDiagnosis | None
    patches: list[PatchRecord]
    status: str  # "running" | "fixed" | "failed" | "dry_run_diagnosed"


SYSTEM_PROMPT = """You are an autonomous Principal Python Debugging & Bug-Fixing Agent.

Your job is to inspect a failing test execution (stdout/stderr traceback) and the local Python codebase,
diagnose the exact root cause of the bug(s), and return a complete, syntactically valid replacement for the
buggy implementation file.

Rules:
1. NEVER modify or weaken `test_*.py` files unless explicitly told the test itself is the target. Fix the application/library code.
2. Inspect ALL failing tests and potential edge cases in the target file so your patch resolves all bugs in that file in a single pass when possible.
3. Preserve all existing function/class signatures, docstrings, and imports required by callers and tests.
4. `patched_code` MUST contain the ENTIRE updated contents of `target_file` (not a partial snippet or diff).
"""


def _build_structured_llm(provider: str = "openai", model: str | None = None):
    """Instantiate a LangChain chat model bound to the `BugDiagnosis` Pydantic schema."""
    provider = provider.lower()
    if provider == "groq":
        from langchain_groq import ChatGroq

        model_name = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        llm = ChatGroq(model=model_name, temperature=0)
        return llm.with_structured_output(BugDiagnosis)

    from langchain_openai import ChatOpenAI

    model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if model_name.startswith(("gpt-6", "gpt-5", "o1", "o3", "o4")):
        llm = ChatOpenAI(model=model_name, reasoning_effort="none")
    else:
        llm = ChatOpenAI(model=model_name, temperature=0)
    return llm.with_structured_output(BugDiagnosis)


class BugFixerAgent:
    """Orchestrates the LangGraph bug-fixing state machine over a local directory."""

    def __init__(
        self,
        provider: str = "openai",
        model: str | None = None,
        verbose: bool = True,
        mock_diagnoser: Callable[[dict[str, str], ExecutionResult], BugDiagnosis] | None = None,
    ) -> None:
        self.provider = provider.lower()
        if self.provider == "mock" or mock_diagnoser is not None:
            os.environ["LANGSMITH_TRACING"] = "false"
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
        self.model = model
        self.verbose = verbose
        self.mock_diagnoser = mock_diagnoser
        self.graph = self._compile_graph()

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    # ------------------------------------------------------------------
    # Node 1: Execute tests / target script
    # ------------------------------------------------------------------
    def execute_tests_node(self, state: CodebaseFixState) -> dict[str, Any]:
        workspace = Path(state["workspace_dir"]).resolve()
        iteration = state.get("iteration", 0)
        self._log(f"\n[Step 1 · Execute] Iteration {iteration} — running test suite in `{workspace.name}`...")

        result = run_target(workspace, command=state.get("command"))
        if result.passed:
            self._log("  ✓ All checks passed!")
            return {"last_execution": result, "status": "fixed"}

        self._log(f"  ✗ Execution failed (exit code {result.return_code}): {result.error_summary}")
        if result.suspect_files:
            self._log(f"  → Suspect files from traceback: {', '.join(result.suspect_files)}")
        return {"last_execution": result}

    # ------------------------------------------------------------------
    # Node 2: Diagnose bug with LLM (or deterministic mock)
    # ------------------------------------------------------------------
    def diagnose_bug_node(self, state: CodebaseFixState) -> dict[str, Any]:
        workspace = Path(state["workspace_dir"]).resolve()
        iteration = state.get("iteration", 0) + 1
        exec_res: ExecutionResult = state["last_execution"]  # type: ignore[assignment]
        files = collect_workspace_files(workspace)

        self._log(f"\n[Step 2 · Diagnose] Iteration {iteration} — analyzing traceback & source files...")

        if self.provider == "mock" or self.mock_diagnoser is not None:
            diagnoser = self.mock_diagnoser or default_mock_diagnoser
            diagnosis = diagnoser(files, exec_res)
        else:
            file_blocks = []
            for rel_path, content in files.items():
                numbered = "\n".join(f"{idx + 1:4d} | {line}" for idx, line in enumerate(content.splitlines()))
                file_blocks.append(f"### File: `{rel_path}`\n```python\n{numbered}\n```")

            user_prompt = (
                f"## Failing Execution Output\n"
                f"Return code: {exec_res.return_code}\n"
                f"Suspect files: {', '.join(exec_res.suspect_files)}\n\n"
                f"### STDOUT\n```text\n{exec_res.stdout}\n```\n\n"
                f"### STDERR / Traceback\n```text\n{exec_res.stderr}\n```\n\n"
                f"## Workspace Source Files\n" + "\n\n".join(file_blocks)
            )
            structured_llm = _build_structured_llm(self.provider, self.model)
            diagnosis = structured_llm.invoke(
                [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_prompt)]
            )

        self._log(f"  → Target file   : {diagnosis.target_file} ({diagnosis.buggy_function})")
        self._log(f"  → Error type    : {diagnosis.error_type}")
        self._log(f"  → Root cause    : {diagnosis.root_cause}")
        self._log(f"  → Proposed fix  : {diagnosis.fix_explanation}")

        return {"iteration": iteration, "last_diagnosis": diagnosis}

    # ------------------------------------------------------------------
    # Node 3: Apply patch & compute unified diff
    # ------------------------------------------------------------------
    def apply_patch_node(self, state: CodebaseFixState) -> dict[str, Any]:
        workspace = Path(state["workspace_dir"]).resolve()
        iteration = state.get("iteration", 1)
        diagnosis: BugDiagnosis = state["last_diagnosis"]  # type: ignore[assignment]
        patches = list(state.get("patches", []))

        target_path = (workspace / diagnosis.target_file).resolve()
        old_code = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        new_code = diagnosis.patched_code.rstrip() + "\n"

        # Validate Python syntax before writing
        compile(new_code, str(target_path), "exec")

        diff = compute_unified_diff(old_code, new_code, diagnosis.target_file)
        record = PatchRecord(
            iteration=iteration,
            target_file=diagnosis.target_file,
            error_type=diagnosis.error_type,
            root_cause=diagnosis.root_cause,
            fix_explanation=diagnosis.fix_explanation,
            diff=diff,
        )
        patches.append(record)

        if state.get("dry_run", False):
            self._log(f"\n[Step 3 · Patch (DRY RUN)] Would patch `{diagnosis.target_file}`:\n{diff}")
            return {"patches": patches, "status": "dry_run_diagnosed"}

        target_path.write_text(new_code, encoding="utf-8")
        self._log(f"\n[Step 3 · Patch] Applied fix to `{diagnosis.target_file}`:\n{diff}")
        return {"patches": patches}

    # ------------------------------------------------------------------
    # Conditional Edge Router
    # ------------------------------------------------------------------
    def _route_after_execution(self, state: CodebaseFixState) -> str:
        exec_res = state.get("last_execution")
        if exec_res and exec_res.passed:
            return "end"
        if state.get("status") == "dry_run_diagnosed":
            return "end"
        if state.get("iteration", 0) >= state.get("max_retries", 3):
            self._log(f"\n  ! Reached max_retries ({state.get('max_retries', 3)}) without passing all checks.")
            return "end"
        return "diagnose"

    def _route_after_patch(self, state: CodebaseFixState) -> str:
        if state.get("dry_run", False):
            return "end"
        return "retest"

    def _compile_graph(self):
        graph = StateGraph(CodebaseFixState)
        graph.add_node("execute_tests_node", self.execute_tests_node)
        graph.add_node("diagnose_bug_node", self.diagnose_bug_node)
        graph.add_node("apply_patch_node", self.apply_patch_node)

        graph.add_edge(START, "execute_tests_node")
        graph.add_conditional_edges(
            "execute_tests_node",
            self._route_after_execution,
            {
                "diagnose": "diagnose_bug_node",
                "end": END,
            },
        )
        graph.add_edge("diagnose_bug_node", "apply_patch_node")
        graph.add_conditional_edges(
            "apply_patch_node",
            self._route_after_patch,
            {
                "retest": "execute_tests_node",
                "end": END,
            },
        )
        return graph.compile()

    def run(
        self,
        workspace_dir: str | Path,
        command: list[str] | None = None,
        max_retries: int = 3,
        dry_run: bool = False,
    ) -> CodebaseFixState:
        """Execute the full diagnose -> patch -> verify state graph on `workspace_dir`."""
        initial_state: CodebaseFixState = {
            "workspace_dir": str(Path(workspace_dir).resolve()),
            "command": command,
            "iteration": 0,
            "max_retries": max_retries,
            "dry_run": dry_run,
            "last_execution": None,
            "last_diagnosis": None,
            "patches": [],
            "status": "running",
        }
        final_state: CodebaseFixState = self.graph.invoke(initial_state)
        if final_state.get("status") == "running":
            last_exec = final_state.get("last_execution")
            final_state["status"] = "fixed" if (last_exec and last_exec.passed) else "failed"
        return final_state


def build_codebase_fixer_graph(provider: str = "openai", model: str | None = None, verbose: bool = True):
    """Convenience builder returning a compiled LangGraph state machine."""
    return BugFixerAgent(provider=provider, model=model, verbose=verbose).graph


def default_mock_diagnoser(files: dict[str, str], exec_res: ExecutionResult) -> BugDiagnosis:
    """Deterministic offline mock diagnoser for the sample_buggy_app and unit tests."""
    if "billing.py" in files:
        fixed_billing = '''"""Invoice & billing calculation utilities."""

from __future__ import annotations


def calculate_invoice_total(
    items: list[dict],
    discount_pct: float = 0.0,
    tax_rate: float = 0.18,
) -> dict[str, float]:
    """Calculate subtotal, discount, tax, and final total for an invoice."""
    if not 0.0 <= discount_pct <= 100.0:
        raise ValueError("discount_pct must be between 0 and 100")

    subtotal = 0.0
    for item in items:
        price = float(item.get("price", 0.0) or 0.0)
        qty = int(item.get("qty", 1) if item.get("qty") is not None else 1)
        subtotal += price * qty

    discount_amount = subtotal * (discount_pct / 100.0)
    taxable_amount = max(0.0, subtotal - discount_amount)
    tax_amount = taxable_amount * tax_rate
    grand_total = taxable_amount + tax_amount

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_amount, 2),
        "tax": round(tax_amount, 2),
        "total": round(grand_total, 2),
    }


def split_bill_equally(total_amount: float, num_people: int) -> float:
    """Return per-person share of `total_amount`. Returns 0.0 if `num_people <= 0`."""
    if num_people <= 0:
        return 0.0
    return round(total_amount / num_people, 2)
'''
        return BugDiagnosis(
            error_type="ZeroDivisionError / KeyError / LogicBug",
            target_file="billing.py",
            buggy_function="calculate_invoice_total, split_bill_equally",
            root_cause=(
                "1) `calculate_invoice_total` added `price` without multiplying by `qty` (and crashed on missing `qty`), "
                "added discount instead of subtracting it, and taxed the pre-discount subtotal. "
                "2) `split_bill_equally` raised `ZeroDivisionError` when `num_people <= 0`."
            ),
            fix_explanation=(
                "Multiply item `price` by `qty` (defaulting missing `qty` to 1), subtract `discount_amount` from `subtotal` "
                "before computing tax, and guard `split_bill_equally` against `num_people <= 0`."
            ),
            patched_code=fixed_billing,
        )

    # Generic fallback for single-file unit test workspaces
    suspect = exec_res.suspect_files[0] if exec_res.suspect_files else next(iter(files.keys()))
    return BugDiagnosis(
        error_type="RuntimeError",
        target_file=suspect,
        buggy_function="unknown",
        root_cause=exec_res.error_summary,
        fix_explanation="Mock patch applied",
        patched_code=files[suspect],
    )
