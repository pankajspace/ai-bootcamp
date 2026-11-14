#!/usr/bin/env python3
"""
run_bug_fixer.py — CLI entry point for the LangGraph Local Codebase Bug Fixer Agent.

Examples:
    # 1. Diagnose & fix the sample buggy app using OpenAI (default)
    python projects/07-bug-fixer-agent/run_bug_fixer.py --reset

    # 2. Run in deterministic offline mock mode (no API calls needed)
    python projects/07-bug-fixer-agent/run_bug_fixer.py --reset --provider mock

    # 3. Preview diagnosis & unified diff without modifying files
    python projects/07-bug-fixer-agent/run_bug_fixer.py --reset --dry-run

    # 4. Run on any custom local directory
    python projects/07-bug-fixer-agent/run_bug_fixer.py --workspace /path/to/project
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bug_fixer.graph import BugFixerAgent  # noqa: E402

BUGGY_BILLING_TEMPLATE = '''"""Invoice & billing calculation utilities (intentionally contains bugs for the agent to diagnose and fix)."""

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
        # BUG 1: crashes with KeyError if 'qty' is omitted (should default to 1),
        # and forgets to multiply price * qty!
        subtotal += item["price"] + item["qty"] * 0

    discount_amount = subtotal * (discount_pct / 100.0)
    # BUG 2: adds discount_amount instead of subtracting it, and computes tax on pre-discount subtotal!
    taxable_amount = subtotal + discount_amount
    tax_amount = subtotal * tax_rate
    grand_total = taxable_amount + tax_amount

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_amount, 2),
        "tax": round(tax_amount, 2),
        "total": round(grand_total, 2),
    }


def split_bill_equally(total_amount: float, num_people: int) -> float:
    """Return per-person share of `total_amount`. Returns 0.0 if `num_people <= 0`."""
    # BUG 3: ZeroDivisionError when num_people == 0 (or negative)
    return round(total_amount / num_people, 2)
'''


def reset_sample_app() -> Path:
    """Restore `sample_buggy_app/billing.py` to its original buggy state."""
    billing_path = PROJECT_ROOT / "sample_buggy_app" / "billing.py"
    billing_path.write_text(BUGGY_BILLING_TEMPLATE, encoding="utf-8")
    return billing_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous Bug Diagnosis & Repair Agent (LangGraph + LangChain)"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=str(PROJECT_ROOT / "sample_buggy_app"),
        help="Path to the target Python directory (default: sample_buggy_app)",
    )
    parser.add_argument(
        "--cmd",
        type=str,
        default=None,
        help="Custom test/execution command (default: `<python> -m unittest discover -v`)",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "groq", "mock"],
        default="openai",
        help="LLM provider to use for structured diagnosis & patching (default: openai)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model name (defaults to OPENAI_MODEL or GROQ_MODEL in .env)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum diagnose-and-fix iterations (default: 3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Diagnose the bug and print the unified diff without modifying files on disk",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset sample_buggy_app/billing.py to its buggy state before running",
    )
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="Print the Mermaid graph definition of the LangGraph workflow",
    )
    args = parser.parse_args()

    if args.reset:
        restored = reset_sample_app()
        print(f"[Reset] Restored buggy sample at {restored}")

    workspace_dir = Path(args.workspace).resolve()
    command = shlex.split(args.cmd) if args.cmd else None

    print("=" * 76)
    print("  AUTONOMOUS BUG FIXER AGENT (LangGraph State Machine)")
    print(f"  Workspace   : {workspace_dir}")
    print(f"  Provider    : {args.provider}" + (f" ({args.model})" if args.model else ""))
    print(f"  Max Retries : {args.max_retries}")
    print(f"  Mode        : {'DRY RUN (no disk writes)' if args.dry_run else 'LIVE PATCH & VERIFY'}")
    print("=" * 76)

    agent = BugFixerAgent(provider=args.provider, model=args.model, verbose=True)

    if args.show_graph:
        print("\n--- LangGraph Mermaid Diagram ---")
        print(agent.graph.get_graph().draw_mermaid())

    final_state = agent.run(
        workspace_dir=workspace_dir,
        command=command,
        max_retries=args.max_retries,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 76)
    print(f"  FINAL STATUS : {final_state['status'].upper()}")
    print(f"  ITERATIONS   : {final_state['iteration']}")
    print(f"  PATCHES      : {len(final_state['patches'])}")
    print("=" * 76)

    return 0 if final_state["status"] in ("fixed", "dry_run_diagnosed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
