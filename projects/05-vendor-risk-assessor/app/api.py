"""
app/api.py — the assessor as a web service (FastAPI, Milestone 5).

COURSE MAP
  Production RAG  Module 4 (entry points and validation), Module 12 & Lab 13 (Observability: p50/p95 latency & cost),
                  Module 13 (the production app: api.py / worker queue / persistent database).
  Deep Search     Module 12 & Lab 12 (LangGraph checkpointing & vendor assessment history SEC-12.1).

Run:   uvicorn app.api:app --reload --port 8000     then open http://localhost:8000/docs

Endpoints
  POST /ask                     → policy or vendor fact answer (ACL groups derived from caller identity header)
  POST /assess                  → run or enqueue (`?queued=true`) a full vendor risk assessment
  POST /jobs/assess             → always enqueue a background assessment job and return `job_id` immediately
  GET  /jobs/{job_id}           → poll job progress (`queued` → `running` → `completed`) and fetch report
  POST /approve/{run_id}        → record human decision (`approve` | `reject`); refuses `BLOCKED` with HTTP 409
  GET  /runs/{run_id}           → full persisted run record (report, profile, stage timings, trace)
  GET  /runs/{run_id}/report.md → the Markdown review file
  GET  /vendors/{name}/history  → chronological vendor review history + diffs since last review (SEC-12.1)
  GET  /observability/runs      → last 20 runs with per-stage timings and p50/p95 latency & cost
  GET  /health
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from assessor.config import SETTINGS
from assessor.graph import Pipeline, new_state
from assessor.store import AssessmentStore, JobQueue
from assessor.tracing import Budget, Tracer

app = FastAPI(
    title="Nimbu Mart Vendor Risk Assessor",
    version="0.5.0",
    description="Capstone project by Shivank Agrawal (Future with Shivank). Assessments are inputs to a human decision.",
)

STORE = AssessmentStore()
QUEUE = JobQueue(STORE)

# Server-side Identity Directory (Rule #7: Groups come from identity on the server, NEVER from the request body)
IDENTITY_DIRECTORY: dict[str, list[str]] = {
    "anonymous": ["public", "employees"],
    "employee": ["public", "employees"],
    "alice@nimbumart.example": ["public", "employees"],
    "security": ["public", "employees", "security"],
    "priya.sec@nimbumart.example": ["public", "employees", "security"],
    "procurement": ["public", "employees", "procurement"],
    "rohan.proc@nimbumart.example": ["public", "employees", "procurement"],
    "dpo": ["public", "employees", "security", "procurement"],
    "meera.dpo@nimbumart.example": ["public", "employees", "security", "procurement"],
    "admin": ["public", "employees", "security", "procurement"],
}


def resolve_caller_identity(
    x_user_identity: Optional[str] = Header(default=None, alias="X-User-Identity"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> tuple[str, list[str]]:
    """Derive `(caller_id, user_groups)` strictly from server-side identity headers.
    Never trusts `user_groups` sent in a client JSON payload."""
    ident = (x_user_identity or "").strip()
    if not ident and authorization:
        parts = authorization.strip().split()
        ident = parts[-1] if parts else ""
    if not ident:
        ident = "anonymous"
    groups = IDENTITY_DIRECTORY.get(ident.lower(), ["public", "employees"])
    return ident, list(groups)


class AskBody(BaseModel):
    question: str
    # Retained as optional field in schema so legacy clients do not 422, but IGNORED by server ACL
    user_groups: Optional[list[str]] = Field(default=None, description="Ignored by server; ACL is derived from X-User-Identity.")


class AssessBody(BaseModel):
    question: str
    vendor: str
    official_domain: Optional[str] = None
    tier: str = "T3"
    users: int = 1
    user_groups: Optional[list[str]] = Field(default=None, description="Ignored by server; ACL is derived from X-User-Identity.")
    requested_by: Optional[str] = None


class ApproveBody(BaseModel):
    decision: str  # approve | reject
    approver: str
    comment: str = ""


@app.get("/health")
def health():
    return {
        "ok": True,
        "llm_provider": SETTINGS.llm_provider,
        "search_provider": SETTINGS.search_provider,
        "db_path": str(STORE.db_path),
    }


@app.post("/ask")
def ask(body: AskBody, caller: tuple[str, list[str]] = Depends(resolve_caller_identity)):
    caller_id, server_groups = caller
    pipe = Pipeline(tracer=None, store=STORE)
    s = pipe.run_plain(new_state(body.question, user_groups=server_groups, requested_by=caller_id))
    if s["route"] == "assessment":
        raise HTTPException(400, "This question needs a full assessment: call POST /assess with vendor, tier and users.")
    return {
        "route": s["route"],
        "caller": caller_id,
        "user_groups": server_groups,
        "answer": s["answer"],
        "citations": [c.model_dump() for c in (s["policy_answer"].citations if s.get("policy_answer") else [])],
    }


def _execute_assessment_job(
    job_id: str,
    body: AssessBody,
    caller_id: str,
    server_groups: list[str],
) -> dict[str, Any]:
    tracer = Tracer("api")
    pipe = Pipeline(tracer=tracer, budget=Budget(), store=STORE)
    req_by = body.requested_by or caller_id
    s = new_state(
        body.question,
        user_groups=server_groups,
        tier=body.tier,
        users=body.users,
        vendor=body.vendor,
        domain=body.official_domain,
        requested_by=req_by,
    )

    def _on_step(stage: str, _state: dict, dur_ms: float) -> None:
        STORE.update_job_stage(job_id, stage, {"duration_ms": dur_ms})

    try:
        s = pipe.run(s, on_step=_on_step)
        if s.get("report") is None:
            payload = {
                "job_id": job_id,
                "run_id": tracer.run_id,
                "route": s["route"],
                "caller": caller_id,
                "user_groups": server_groups,
                "answer": s["answer"],
            }
            STORE.complete_job(job_id, tracer.run_id, payload)
            return payload
        rep_json = s["report"].model_dump(mode="json")
        payload = {
            "job_id": job_id,
            "run_id": tracer.run_id,
            "caller": caller_id,
            "user_groups": server_groups,
            "stage_timings_ms": s.get("stage_timings_ms", {}),
            "report": rep_json,
        }
        STORE.complete_job(job_id, tracer.run_id, payload)
        return payload
    except Exception as exc:  # noqa: BLE001
        STORE.fail_job(job_id, str(exc))
        raise
    finally:
        tracer.close()


@app.post("/assess")
def assess(
    body: AssessBody,
    queued: bool = Query(default=False, description="Set true to enqueue and poll /jobs/{job_id}"),
    caller: tuple[str, list[str]] = Depends(resolve_caller_identity),
):
    caller_id, server_groups = caller
    req_by = body.requested_by or caller_id
    if queued:
        job_id = QUEUE.enqueue(
            question=body.question,
            vendor=body.vendor,
            requested_by=req_by,
            worker_fn=lambda jid: _execute_assessment_job(jid, body, caller_id, server_groups),
            run_sync=False,
        )
        return {"job_id": job_id, "status": "queued", "poll_url": f"/jobs/{job_id}"}

    # Default synchronous mode (runs through the same job tracker so every run has both a job_id and run_id)
    result_holder: dict[str, Any] = {}
    job_id = QUEUE.enqueue(
        question=body.question,
        vendor=body.vendor,
        requested_by=req_by,
        worker_fn=lambda jid: result_holder.update(_execute_assessment_job(jid, body, caller_id, server_groups)),
        run_sync=True,
    )
    result_holder.setdefault("job_id", job_id)
    return result_holder


@app.post("/jobs/assess")
def enqueue_assess(body: AssessBody, caller: tuple[str, list[str]] = Depends(resolve_caller_identity)):
    """Explicit queue endpoint: returns a `job_id` immediately for polling via `GET /jobs/{job_id}`."""
    caller_id, server_groups = caller
    req_by = body.requested_by or caller_id
    job_id = QUEUE.enqueue(
        question=body.question,
        vendor=body.vendor,
        requested_by=req_by,
        worker_fn=lambda jid: _execute_assessment_job(jid, body, caller_id, server_groups),
        run_sync=False,
    )
    return {"job_id": job_id, "status": "queued", "poll_url": f"/jobs/{job_id}"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = STORE.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return job


@app.post("/approve/{run_id}")
def approve(run_id: str, body: ApproveBody):
    try:
        return STORE.record_decision(
            run_id=run_id,
            decision=body.decision,
            approver=body.approver,
            comment=body.comment,
        )
    except KeyError as exc:
        raise HTTPException(404, "run not found") from exc
    except PermissionError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    rec = STORE.get_run(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    return rec


@app.get("/runs/{run_id}/report.md", response_class=PlainTextResponse)
def report_md(run_id: str):
    rec = STORE.get_run(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    return rec["report_md"]


@app.get("/vendors/{name}/history")
def vendor_history(name: str):
    """SEC-12.1: Return past assessments for `{name}` and show what changed since the last review."""
    return STORE.vendor_history(name)


@app.get("/observability/runs")
def observability_runs(limit: int = Query(default=20, ge=1, le=100)):
    """Production RAG Lab 13: Last 20 runs with per-stage timings and p50/p95 latency & cost."""
    return STORE.observability_summary(limit=limit)
