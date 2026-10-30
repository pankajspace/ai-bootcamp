"""Milestone M3, M4 & Stretch Goal 2 · Main CLI Entrypoint (`main.py`).

Supports all flags specified in the project brief:
- `--trace`      : Prints `[CALL]` and `[OUTPUT]` timestamps showing Phase 1 parallel execution
- `--verbose`    : Prints intermediate specialist reports before the final brief
- `--stream`     : Streams the final brief output token-by-token / line-by-line
- `--log-dir`    : Saves the generated brief, specialist reports, trace, and fact-check JSON to disk
- `--survey`     : Path to a custom survey CSV file (defaults to `data/nps_survey.csv`)
- `--guardrail`  : Stretch Goal 2 — if `fact_check` fails, sends failed checks back to `ReportWriterAgent` (up to 2 retries)

Run:
    python projects/02-nps-analyst/nps_insights_agent/main.py --trace
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

# Ensure project root is on sys.path
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nps_insights_agent.agents import (
    report_writer_agent,
    run_three_phase_pipeline_async,
)
from nps_insights_agent.config import DEFAULT_SURVEY_PATH, get_model_description
from nps_insights_agent.fact_check import fact_check_brief, format_fact_check_report
from nps_insights_agent.tools.survey_tools import (
    _compute_nps_by_segment_cached,
    load_survey_df,
)


def run_with_guardrail(
    user_query: str,
    trace: bool = False,
    verbose: bool = False,
    stream: bool = False,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Run the 3-phase multi-agent pipeline and enforce the `fact_check.py` guardrail (max 2 retries)."""
    pipeline_out = asyncio.run(
        run_three_phase_pipeline_async(
            user_query=user_query,
            trace=trace,
            verbose=verbose,
        )
    )
    brief = pipeline_out["brief"]
    audit = fact_check_brief(brief, label_aware=True)
    retries_used = 0

    while not audit["passed"] and retries_used < max_retries:
        retries_used += 1
        failed_summary = "\n".join(
            f"- {chk['name']}: {chk['detail']}" for chk in audit["failed_checks"]
        )
        if trace or verbose:
            print(
                f"\n[GUARDRAIL RETRY {retries_used}/{max_retries}] Fact check failed on "
                f"{len(audit['failed_checks'])} check(s). Sending feedback to ReportWriterAgent..."
            )
        correction_prompt = (
            "Your previous Executive NPS Brief failed the automated Python fact check on the following items:\n"
            f"{failed_summary}\n\n"
            "Rewrite the complete Executive NPS Brief fixing every failed check above while preserving all other "
            "grounded numbers, signs (+ / -), ₹ lakh figures, the RED alert level, the 3 hidden stories, "
            "both fix rankings, the callback list, and the 3 data caveats.\n\n"
            f"Previous Brief:\n{brief}"
        )
        brief = str(report_writer_agent(correction_prompt)).strip()
        audit = fact_check_brief(brief, label_aware=True)

    if stream:
        print("\n" + "=" * 75)
        print("STREAMING EXECUTIVE NPS BRIEF:")
        print("=" * 75)
        for line in brief.splitlines():
            print(line, flush=True)
            time.sleep(0.015)

    return {
        "brief": brief,
        "reports": pipeline_out["reports"],
        "trace_lines": pipeline_out["trace_lines"],
        "elapsed_seconds": pipeline_out["elapsed_seconds"],
        "fact_check": audit,
        "guardrail_retries_used": retries_used,
    }


def _save_run_logs(log_dir: Path, result: dict[str, Any]) -> Path:
    """Persist the brief, trace, specialist reports, and fact-check audit to `log_dir`."""
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    brief_path = log_dir / f"nps_brief_{stamp}.md"
    trace_path = log_dir / f"trace_{stamp}.log"
    audit_path = log_dir / f"fact_check_{stamp}.json"

    brief_path.write_text(result["brief"] + "\n", encoding="utf-8")
    trace_path.write_text("\n".join(result["trace_lines"]) + "\n", encoding="utf-8")
    audit_path.write_text(
        json.dumps(
            {
                "elapsed_seconds": result["elapsed_seconds"],
                "guardrail_retries_used": result["guardrail_retries_used"],
                "fact_check": result["fact_check"],
                "specialist_reports": result["reports"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return brief_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Future with Shivank Bank — NPS Analyst in a Box (5 Specialists + Orchestrator + Auditor)"
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print timestamped [CALL] and [OUTPUT] trace showing Phase 1 parallel execution.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print intermediate specialist reports from Phase 1 and Phase 2.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the final Executive NPS Brief output line by line.",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="",
        help="Directory to save the generated brief (.md), trace (.log), and fact-check (.json).",
    )
    parser.add_argument(
        "--survey",
        type=str,
        default="",
        help="Path to a survey CSV file (defaults to data/nps_survey.csv).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Maximum guardrail retries if fact_check fails (default: 2).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.survey:
        survey_path = Path(args.survey).resolve()
        if not survey_path.exists():
            print(f"Error: Survey CSV not found at {survey_path}", file=sys.stderr)
            return 1
        os.environ["NPS_SURVEY_PATH"] = str(survey_path)
        load_survey_df.cache_clear()
        _compute_nps_by_segment_cached.cache_clear()
    else:
        survey_path = DEFAULT_SURVEY_PATH

    print("=" * 75)
    print("🏦 FUTURE WITH SHIVANK BANK · NPS ANALYST IN A BOX")
    print(f"✓ Model      : {get_model_description()}")
    print(f"✓ Survey CSV : {survey_path}")
    print("✓ Pipeline   : Phase 1 (3 Parallel Analysts) -> Phase 2 (Action Planner) -> Phase 3 (Report Writer) -> Auditor")
    print("=" * 75)

    result = run_with_guardrail(
        user_query="Analyze Future with Shivank Bank's Q3 2026 NPS survey and produce the executive brief for the CEO.",
        trace=args.trace,
        verbose=args.verbose,
        stream=args.stream,
        max_retries=args.max_retries,
    )

    if not args.stream:
        print("\n" + "=" * 75)
        print("FINAL CEO EXECUTIVE NPS BRIEF:")
        print("=" * 75)
        print(result["brief"])

    print("\n" + format_fact_check_report(result["fact_check"]))
    print(
        f"⏱ Total pipeline wall time: {result['elapsed_seconds']:.2f}s | "
        f"Guardrail retries used: {result['guardrail_retries_used']}"
    )

    if args.log_dir:
        saved_brief = _save_run_logs(Path(args.log_dir), result)
        print(f"📁 Saved brief, trace, and audit logs to: {saved_brief.parent}")

    return 0 if result["fact_check"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

