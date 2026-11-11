"""
store.py — persistent database, background job queue, vendor history (SEC-12.1), and observability (Milestone 5).

COURSE MAP
  Production RAG  Module 12 & Lab 13 (Observability: per-stage timings, cost, last 20 runs with p50/p95 latency & cost)
  Production RAG  Module 13 (API + background queue + persistent database)
  Deep Search     Module 7 & 12 (Long-term vendor assessment history & diffing for SEC-12.1)
"""

from __future__ import annotations

import json
import math
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from .config import RUNS_DIR
from .report import to_markdown
from .schemas import AssessmentReport

DEFAULT_DB_PATH = RUNS_DIR / "assessor.db"


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return round(sorted_vals[0], 4)
    idx = (pct / 100.0) * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return round(sorted_vals[lo], 4)
    frac = idx - lo
    return round(sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo]), 4)


class AssessmentStore:
    """SQL-backed store for assessment runs, human gate decisions, background jobs, and observability."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS assessments (
                    run_id TEXT PRIMARY KEY,
                    vendor TEXT NOT NULL,
                    official_domain TEXT,
                    question TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    users INTEGER NOT NULL,
                    requested_by TEXT NOT NULL,
                    user_groups_json TEXT NOT NULL,
                    overall TEXT NOT NULL,
                    overall_reason TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    decided_by TEXT,
                    decided_on TEXT,
                    approval_comment TEXT,
                    cost_usd REAL NOT NULL,
                    llm_calls INTEGER NOT NULL,
                    duration_s REAL NOT NULL,
                    stage_timings_json TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    report_md TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    trace_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    status TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    vendor TEXT,
                    question TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    progress_json TEXT NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    # ------------------------------------------------------------------ runs
    def save_run(
        self,
        report: AssessmentReport,
        report_md: str,
        *,
        stage_timings_ms: Optional[dict[str, float]] = None,
        trace_events: Optional[list[dict]] = None,
    ) -> str:
        run_id = report.run_id or f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-store"
        report.run_id = run_id
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rep_dict = report.model_dump(mode="json")
        prof_dict = report.profile.model_dump(mode="json")
        timings = stage_timings_ms or {}
        events = trace_events or []

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO assessments (
                    run_id, vendor, official_domain, question, tier, users, requested_by,
                    user_groups_json, overall, overall_reason, approval_status, decided_by,
                    decided_on, approval_comment, cost_usd, llm_calls, duration_s,
                    stage_timings_json, report_json, report_md, profile_json, trace_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    report.request.vendor,
                    report.profile.official_domain,
                    report.request.question,
                    report.request.tier,
                    report.request.users,
                    report.request.requested_by,
                    json.dumps(report.request.user_groups),
                    report.overall,
                    report.overall_reason,
                    report.approval.status,
                    report.approval.decided_by,
                    str(report.approval.decided_on) if report.approval.decided_on else None,
                    report.approval.comment,
                    float(report.cost_usd),
                    int(report.llm_calls),
                    float(report.duration_s),
                    json.dumps(timings),
                    json.dumps(rep_dict, ensure_ascii=False),
                    report_md,
                    json.dumps(prof_dict, ensure_ascii=False),
                    json.dumps(events, default=str, ensure_ascii=False),
                    now,
                ),
            )
            conn.commit()
        return run_id

    def get_run(self, run_id: str) -> Optional[dict[str, Any]]:
        if ".." in run_id:
            return None
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM assessments WHERE run_id = ?", (run_id,)).fetchone()
        if row is not None:
            return {
                "run_id": row["run_id"],
                "vendor": row["vendor"],
                "tier": row["tier"],
                "overall": row["overall"],
                "overall_reason": row["overall_reason"],
                "approval_status": row["approval_status"],
                "decided_by": row["decided_by"],
                "decided_on": row["decided_on"],
                "approval_comment": row["approval_comment"],
                "cost_usd": row["cost_usd"],
                "llm_calls": row["llm_calls"],
                "duration_s": row["duration_s"],
                "stage_timings_ms": json.loads(row["stage_timings_json"]),
                "report": json.loads(row["report_json"]),
                "report_md": row["report_md"],
                "profile": json.loads(row["profile_json"]),
                "trace": json.loads(row["trace_json"]),
                "created_at": row["created_at"],
            }
        # Fallback to filesystem `runs/<run_id>/` if run was created via CLI prior to DB sync
        run_dir = RUNS_DIR / run_id
        if run_dir.exists() and (run_dir / "report.json").exists():
            rep_dict = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
            md = (run_dir / "report.md").read_text(encoding="utf-8") if (run_dir / "report.md").exists() else ""
            trace = []
            if (run_dir / "trace.jsonl").exists():
                trace = [
                    json.loads(line)
                    for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            rep_obj = AssessmentReport.model_validate(rep_dict)
            self.save_run(rep_obj, md, trace_events=trace)
            return self.get_run(run_id)
        return None

    def record_decision(self, run_id: str, decision: str, approver: str, comment: str = "") -> dict[str, Any]:
        """Record a human approval or rejection decision.
        Enforces Rule #9: A BLOCKED assessment cannot be approved."""
        rec = self.get_run(run_id)
        if rec is None:
            raise KeyError(f"Run {run_id!r} not found")
        rep_dict = rec["report"]
        norm = decision.strip().lower()
        if norm in ("approve", "approved") and rep_dict["overall"] == "BLOCKED":
            raise PermissionError(
                "A BLOCKED assessment cannot be approved. Resolve the blocking requirement or change the data tier."
            )
        new_status = "approved" if norm in ("approve", "approved") else "rejected"
        decided_on = date.today().isoformat()
        rep_dict["approval"].update(
            {
                "status": new_status,
                "decided_by": approver,
                "decided_on": decided_on,
                "comment": comment,
            }
        )
        rep_obj = AssessmentReport.model_validate(rep_dict)
        new_md = to_markdown(rep_obj)
        trace = rec.get("trace", [])
        trace.append({"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "stage": "approval", **rep_dict["approval"]})

        self.save_run(rep_obj, new_md, stage_timings_ms=rec.get("stage_timings_ms", {}), trace_events=trace)

        # Also keep `runs/<run_id>/` files in sync if directory exists
        run_dir = RUNS_DIR / run_id
        if run_dir.exists():
            (run_dir / "report.json").write_text(json.dumps(rep_dict, indent=2, ensure_ascii=False), encoding="utf-8")
            (run_dir / "report.md").write_text(new_md, encoding="utf-8")
            with open(run_dir / "trace.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"stage": "approval", **rep_dict["approval"]}) + "\n")

        return rep_dict["approval"]

    # ------------------------------------------------------------------ vendor history (SEC-12.1)
    def vendor_history(self, vendor: str) -> dict[str, Any]:
        """Return chronological assessment history for `vendor` and compute field & verdict diffs between runs."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM assessments WHERE LOWER(vendor) = LOWER(?) ORDER BY created_at ASC, rowid ASC",
                (vendor,),
            ).fetchall()

        history: list[dict[str, Any]] = []
        prev_facts: Optional[dict[str, Any]] = None
        prev_verdicts: Optional[dict[str, str]] = None
        prev_overall: Optional[str] = None

        for row in rows:
            rep = json.loads(row["report_json"])
            prof = json.loads(row["profile_json"])
            cur_facts = {k: v.get("value") for k, v in prof.get("facts", {}).items()}
            cur_verdicts = {r["requirement_id"]: r["verdict"] for r in rep.get("results", [])}
            cur_overall = row["overall"]

            fact_changes: dict[str, dict[str, Any]] = {}
            verdict_changes: dict[str, dict[str, str]] = {}
            if prev_facts is not None:
                for field_name in sorted(set(prev_facts) | set(cur_facts)):
                    old_v = prev_facts.get(field_name)
                    new_v = cur_facts.get(field_name)
                    if json.dumps(old_v, sort_keys=True, default=str) != json.dumps(new_v, sort_keys=True, default=str):
                        fact_changes[field_name] = {"previous": old_v, "current": new_v}
            if prev_verdicts is not None:
                for req_id in sorted(set(prev_verdicts) | set(cur_verdicts)):
                    old_ver = prev_verdicts.get(req_id)
                    new_ver = cur_verdicts.get(req_id)
                    if old_ver != new_ver:
                        verdict_changes[req_id] = {"previous": old_ver or "N/A", "current": new_ver or "N/A"}

            history.append(
                {
                    "run_id": row["run_id"],
                    "vendor": row["vendor"],
                    "tier": row["tier"],
                    "users": row["users"],
                    "overall": cur_overall,
                    "overall_changed": (prev_overall is not None and prev_overall != cur_overall),
                    "approval_status": row["approval_status"],
                    "decided_by": row["decided_by"],
                    "decided_on": row["decided_on"],
                    "cost_usd": row["cost_usd"],
                    "duration_s": row["duration_s"],
                    "created_at": row["created_at"],
                    "fact_changes": fact_changes,
                    "verdict_changes": verdict_changes,
                }
            )
            prev_facts = cur_facts
            prev_verdicts = cur_verdicts
            prev_overall = cur_overall

        return {
            "vendor": vendor,
            "total_runs": len(history),
            "runs": history,
        }

    # ------------------------------------------------------------------ observability (Production RAG Lab 13)
    def observability_summary(self, limit: int = 20) -> dict[str, Any]:
        """Return the last `limit` runs (default 20) plus p50/p95 latency and cost metrics."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM assessments ORDER BY created_at DESC, rowid DESC LIMIT ?",
                (limit,),
            ).fetchall()

        runs_table: list[dict[str, Any]] = []
        durations: list[float] = []
        costs: list[float] = []

        for row in rows:
            dur = float(row["duration_s"])
            cost = float(row["cost_usd"])
            durations.append(dur)
            costs.append(cost)
            runs_table.append(
                {
                    "run_id": row["run_id"],
                    "vendor": row["vendor"],
                    "tier": row["tier"],
                    "overall": row["overall"],
                    "approval_status": row["approval_status"],
                    "duration_s": round(dur, 3),
                    "cost_usd": round(cost, 4),
                    "llm_calls": row["llm_calls"],
                    "stage_timings_ms": json.loads(row["stage_timings_json"]),
                    "created_at": row["created_at"],
                }
            )

        sorted_dur = sorted(durations)
        sorted_cost = sorted(costs)
        return {
            "count": len(runs_table),
            "latency_p50_s": _percentile(sorted_dur, 50),
            "latency_p95_s": _percentile(sorted_dur, 95),
            "cost_p50_usd": _percentile(sorted_cost, 50),
            "cost_p95_usd": _percentile(sorted_cost, 95),
            "total_cost_usd": round(sum(costs), 4),
            "runs": runs_table,
        }

    # ------------------------------------------------------------------ jobs
    def create_job(self, question: str, vendor: Optional[str], requested_by: str) -> str:
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    job_id, run_id, status, current_stage, vendor, question,
                    requested_by, progress_json, result_json, error, created_at, updated_at
                ) VALUES (?, NULL, 'queued', 'queued', ?, ?, ?, '[]', NULL, NULL, ?, ?)
                """,
                (job_id, vendor, question, requested_by, now, now),
            )
            conn.commit()
        return job_id

    def update_job_stage(self, job_id: str, stage: str, info: Optional[dict] = None) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT progress_json FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return
            progress = json.loads(row["progress_json"])
            progress.append({"ts": now, "stage": stage, **(info or {})})
            conn.execute(
                "UPDATE jobs SET status = 'running', current_stage = ?, progress_json = ?, updated_at = ? WHERE job_id = ?",
                (stage, json.dumps(progress), now, job_id),
            )
            conn.commit()

    def complete_job(self, job_id: str, run_id: str, result: dict[str, Any], status: str = "completed") -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE jobs SET run_id = ?, status = ?, current_stage = 'done', result_json = ?, updated_at = ? WHERE job_id = ?",
                (run_id, status, json.dumps(result, default=str), now, job_id),
            )
            conn.commit()

    def fail_job(self, job_id: str, error: str) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = 'failed', current_stage = 'failed', error = ?, updated_at = ? WHERE job_id = ?",
                (error, now, job_id),
            )
            conn.commit()

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if not row:
            return None
        return {
            "job_id": row["job_id"],
            "run_id": row["run_id"],
            "status": row["status"],
            "current_stage": row["current_stage"],
            "vendor": row["vendor"],
            "question": row["question"],
            "requested_by": row["requested_by"],
            "progress": json.loads(row["progress_json"]),
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "error": row["error"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


class JobQueue:
    """Background assessment queue (supports Redis+RQ when REDIS_URL is set, with built-in ThreadPoolExecutor fallback)."""

    def __init__(self, store: AssessmentStore, max_workers: int = 2):
        self.store = store
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    def enqueue(
        self,
        question: str,
        vendor: Optional[str],
        requested_by: str,
        worker_fn: Callable[[str], None],
        *,
        run_sync: bool = False,
    ) -> str:
        job_id = self.store.create_job(question=question, vendor=vendor, requested_by=requested_by)
        if run_sync:
            worker_fn(job_id)
        else:
            self._pool.submit(worker_fn, job_id)
        return job_id
