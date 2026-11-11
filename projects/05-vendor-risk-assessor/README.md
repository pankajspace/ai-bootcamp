# AI Vendor Risk Assessor — capstone starter kit

**Capstone project by Shivank Agrawal · Future with Shivank**

> *"Can our support team use LedgerLens AI with customer tickets?"*
> The assessor reads our policies, researches the vendor on the web, checks every requirement
> deterministically, drafts the questions we still need to ask the vendor, and hands a review file to a
> human approver. It never approves anything itself.

This repo is the **starter kit**. It runs end to end **offline** (no API key, no internet) against a
fictional company (Nimbu Mart) and three fictional vendors, so you can see the finished shape on day one.
Then you replace the simplified parts with the real components you built in the three courses:

| Course | What you bring into this project |
|---|---|
| **Production RAG from Scratch** | the policy library: ingestion, chunking by clause, hybrid search + reranking, grounded answers with citations, access control, evaluation, the FastAPI service |
| **Agentic RAG** | the Router (policy / vendor / assessment), the Answer Grader and the Hallucination Grader |
| **Deep Search Agents** | vendor research: planner, parallel executor, identity gate, freshness + authority scoring, merging with provenance, prompt-injection quarantine, budgets, LangGraph |

Open **`Capstone-AI-Vendor-Risk-Assessor-Shivank-Agrawal.html`** in your browser for the full brief:
milestones, the module-by-module course map, the rubric and the demo checklist.

---

## 1. Setup (10 minutes)

Python 3.10 or newer.

```bash
cd projects/05-vendor-risk-assessor
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                 # Windows: copy .env.example .env
python scripts/check_setup.py
```

## 2. Run it

```bash
python run_assessor.py                                                          # LedgerLens AI, T3, 35 users → BLOCKED
python run_assessor.py "Can we use Parakeet Translate for support chats?" --tier T3 --users 60   # → CONDITIONAL
python run_assessor.py "Can the product team use Parakeet Translate for roadmap docs?" --tier T2 --users 8   # → READY FOR APPROVAL
python run_assessor.py "Can marketing use QuillDesk for customer replies?" --tier T3 --users 12   # → BLOCKED (2 blockers)
python run_assessor.py "Where must customer personal data be stored?"            # policy question
python run_assessor.py "Does QuillDesk have SOC 2?"                               # vendor facts only
python run_assessor.py --groups public,employees                                  # outside Security: the Approved Vendor List is hidden
python run_assessor.py --interactive --approver "A. Sharma"                       # record a human decision
```

Each assessment writes `runs/<timestamp>-assess/`:

| File | What it is |
|---|---|
| `report.md` | the review file (PROC-2.1): verdict table with source URL + date, facts, open questions, approval block |
| `report.json` | the same, structured |
| `profile.json` | everything established about the vendor, with scores and conflicts |
| `trace.jsonl` | every step: searches, rejections, quarantines, LLM calls, verdicts. **Read this to debug.** |
| `vendor_questions.txt` | the email to send the vendor |

Tests and evaluation:

```bash
python -m pytest -q              # 70 tests
python eval/run_eval.py          # scorecard against data/gold_set.json → reports/eval_report.md
python eval/run_eval.py --strict # exit 1 on a failed threshold (use in CI)
```

## 3. Switch on a real LLM and real search (after the offline run is green)

Edit `.env`: pick one `LLM_PROVIDER` block (Gemini and Groq have free tiers; Ollama is local) and set
`SEARCH_PROVIDER=ddgs` (no key) or `tavily`. Install the extras: `pip install openai ddgs trafilatura httpx`.
Then assess a **real** vendor:

```bash
python run_assessor.py "Can our support team use <Tool> for ticket summaries?" --vendor "<Tool>" --domain <vendor.com> --tier T3 --users 35 --max-usd 0.30
```

Live mode is a *baseline*: sequential, unplanned, one model. Making it good is the project (Milestone 2).

## 4. The code, in reading order

```
assessor/
  schemas.py          every contract between stages (Pydantic)                 ← read first
  matcher.py          requirement × fact → verdict. Deterministic. Tested.      ← the heart
  policy_rag.py       policy library: clause chunks, BM25, ACL, versions, extractive answers
  vendor_research.py  deep search retarget: plan → gather → identity → quarantine → extract → score → merge
  router.py           policy / vendor / assessment / refuse
  graders.py          relevance + groundedness checks on policy answers
  guardrails.py       input redaction, intent check, output policy
  questionnaire.py    UNKNOWN / NEEDS_REVIEW → questions from template NM-SEC-Q
  report.py           Markdown + JSON review file
  graph.py            the orchestrator: plain Python AND LangGraph, same nodes
  llm.py / tracing.py / config.py   provider wrapper, trace + budget, settings
data/
  policies/           8 Nimbu Mart documents + _metadata.json (access, status, trust)
  requirements.yaml   11 machine-checkable rules, each tied to a clause
  vendor_web/corpus.json   the fictional web: 23 pages, deliberately messy
  gold_set.json       hand-checked expected verdicts (5 cases) + policy questions
  gold_set_template.json   fill this for REAL vendors
eval/run_eval.py      the scorecard
tests/                70 tests
app/api.py, app/ui.py FastAPI + Streamlit skeletons (Milestone 5)
```

Every file starts with a **COURSE MAP** comment and a **LEARNER TODO** block that names the milestone and
the course module/lab to use.

## 5. Rules of the project (read before you write any code)

1. **The LLM never decides a verdict.** It reads pages and drafts text. `matcher.py` decides.
2. **UNKNOWN beats a guess.** A PASS without a URL is a bug; the output guardrail downgrades it.
3. **A claim is not evidence.** "We are SOC 2 compliant" is `claimed`; a report, certificate or registry entry is `documented`.
4. **Identity is a gate.** A page about a same-name company is rejected before anything is read from it.
5. **Untrusted content never reaches the verdict.** Pages that talk to the AI are quarantined; forum rumours are dropped and logged.
6. **Access control lives in retrieval.** The Approved Vendor List is invisible to people outside Security/Procurement, and the assistant says so instead of leaking it.
7. **Humans approve.** The report ends in an approval block that only a named person can fill.

All companies, people, domains and documents in `data/` are fictional and were written for this course.

---

## 6. Milestones (M0 – M6) — What Each Includes & How to Run

### ✅ Milestone 0 (M0): Run and Read the Starter Kit
**Goal:** Understand the end-to-end architecture, contracts, deterministic rule engine, offline web corpus traps, and baseline evaluation before changing components.

#### What M0 Includes
- **Contracts (`assessor/schemas.py`):** Pydantic schemas for the 9 vendor fields (`VENDOR_FIELDS`), `Claim`, `Evidence`, `VendorFact`, `VendorProfile`, `PolicyHit`, `PolicyAnswer`, `Requirement`, `RequirementResult`, `RouteDecision`, `AssessmentRequest`, and `AssessmentReport`.
- **Deterministic Matcher (`assessor/matcher.py` + `data/requirements.yaml`):** 8 rule functions (`certification_valid`, `region_includes`, `value_known`, `enum_verdict`, `list_disclosed`, `retention_within`, `no_unresolved_incident`, `approved_for_tier`) evaluating 11 policy requirements across tiers `T1`, `T2`, `T3`. Includes support for `allow_planned` in `rule_region_includes`.
- **Orchestrator (`assessor/graph.py`):** Unified node pipeline running in both plain Python (`run_plain`) and LangGraph (`build_langgraph`).
- **Offline Corpus (`data/vendor_web/corpus.json`):** 23 fictional pages across **LedgerLens AI**, **QuillDesk**, and **Parakeet Translate**, including a stale 2024 security page (`L08`), a look-alike UK accounting firm (`L09`), a forum rumour (`L07`), a syndicated directory copy (`Q06`), and a prompt-injection blog post (`L10`).
- **Baseline Evaluation (`eval/run_eval.py` + `data/gold_set.json`):** 5 assessment gold cases + 6 policy QA checks (with `pq-who-approves` marked as the baseline keyword-search failure to fix in M1).

#### How to Run M0
Assuming you are in the `projects/05-vendor-risk-assessor` directory:

```bash
# 1. Verify environment, policies, and corpus
python scripts/check_setup.py

# 2. Run the 4 core demo assessments
# Case 1: LedgerLens AI (T3, 35 users) -> BLOCKED (fails DP-3.1 India residency)
python run_assessor.py

# Case 2: Parakeet Translate (T3, 60 users) -> CONDITIONAL (passes tech rules, approved for T2 only on AVL)
python run_assessor.py "Can we use Parakeet Translate for support chats?" --tier T3 --users 60

# Case 3: Parakeet Translate (T2, 8 users) -> READY_FOR_APPROVAL (all T2 rules pass)
python run_assessor.py "Can the product team use Parakeet Translate for roadmap docs?" --tier T2 --users 8

# Case 4: QuillDesk (T3, 12 users) -> BLOCKED (fails DP-3.1 US-only & SEC-9.3 incident without post-mortem)
python run_assessor.py "Can marketing use QuillDesk for customer replies?" --tier T3 --users 12

# 3. Run policy-only, vendor-facts-only, and ACL-restricted queries
python run_assessor.py "Where must customer personal data be stored?"
python run_assessor.py "Does QuillDesk have SOC 2?"
python run_assessor.py --groups public,employees

# 4. Run unit test suite
python -m pytest -q

# 5. Run the evaluation harness & strict CI check
python eval/run_eval.py --strict
```

---

### ✅ Milestone 1 (M1): The Policy Library, Production Grade
**Goal:** Replace pure keyword search with the `rag_core/` hybrid retrieval + reranking pipeline and grounded answer generation while preserving every security property (ACL, archived, draft, untrusted, and injection filtering).

#### What M1 Includes
- **`rag_core/` Integration (`rag_core/`):**
  - `rag_core/documents.py`: `Chunk` and deterministic `stable_chunk_id` indexing all policy clauses with full metadata (`doc`, `title`, `doc_id`, `clause_id`, `heading`, `section`, `version`, `status`, `trust`, `access`, `effective_date`, `injected`).
  - `rag_core/embeddings.py`: Embedder abstraction (`FastEmbed`, `OpenAI`, `WordLlama`, and offline stem/synonym/bigram/n-gram `HashingEmbedder`).
  - `rag_core/hybrid.py` & `rag_core/vectorstore.py`: Pre-filtered exact vector + BM25 hybrid search fused with **Reciprocal Rank Fusion (RRF)**.
  - `rag_core/rerank.py`: Cross-encoder reranker (`CrossEncoderReranker`) with heading/intent-aware fallback (`KeywordOverlapReranker`).
  - `rag_core/security.py`: Pre-ranking `acl_filter`, prompt-injection detection (`detect_injection`) at ingestion, and `redact_pii`.
- **Upgraded `PolicyLibrary` (`assessor/policy_rag.py`):**
  - Pre-ranking filters enforce `access` (ACL), `status` (`active` only by default, excluding `archived` and `draft` unless requested), `trust == "trusted"`, and `injected == False`.
  - Grounded LLM generation (`GROUNDED_POLICY_SYSTEM`) with clause & version citations, verified by `grade_grounded()`, plus extractive fallback for offline runs.
  - Fixes the baseline failure `pq-who-approves` (`"Who approves a tool that handles customer data?"` now ranks `AI-5.1` #1 and cites `DPO`, raising `policy_qa_soft` from **81.25%** to **100.00%**).
- **3 New Policy Documents (`data/policies/` + `data/policies/_metadata.json`):**
  1. `incident_response_runbook.md` (`NM-SEC-IR`, `v2026.1`, `status: active`): 4h internal ticket, 24h DPO brief, 72h CERT-In & DPDP Board breach notification (`IR-1.1`), 4h token revocation (`IR-2.1`), post-mortem re-enablement gate (`IR-3.1`).
  2. `ai_governance_policy_2027_draft.md` (`NM-AI-POL-2027`, `v2027.0-draft`, `status: draft`): Proposed 2027 EU adequacy corridor (`DP-3.1-DRAFT`), filtered out from active policy answers by default.
  3. `cryptography_and_key_management_standard.md` (`NM-SEC-CRYPTO`, `v2026.1`, `status: active`): TLS 1.3 / AES-256-GCM (`CRY-1.1`), BYOK for >100k T3 records (`CRY-2.1`), 90-day API key & token rotation (`CRY-3.1`).
- **3 New Gold Policy Questions (`data/gold_set.json`):**
  - `pq-incident-notification` (`IR-1.1`, `72 hours`)
  - `pq-draft-not-active` (`DP-3.1`, `must_not_cite_doc: "ai_governance_policy_2027_draft.md"`)
  - `pq-crypto-key-rotation` (`CRY-3.1`, `90 days`)

#### How to Run M1
Assuming you are in the `projects/05-vendor-risk-assessor` directory:

```bash
# 1. Verify 11 policy files (68 clause chunks) are indexed through rag_core
python scripts/check_setup.py

# 2. Run the M1 policy RAG unit tests (ACL, archived, draft, untrusted, hybrid + rerank)
python -m pytest tests/test_policy_rag.py -v

# 3. Ask the previously failing baseline question & the new M1 policy questions
python run_assessor.py "Who approves a tool that handles customer data?"
python run_assessor.py "How quickly must we notify CERT-In and the Data Protection Board after a confirmed vendor breach of customer data?"
python run_assessor.py "How often must vendor API keys and service account tokens be rotated?"
python run_assessor.py "Which vendors are on the approved vendor list?" --groups public,employees

# 4. Run the full evaluation harness (verifying 100% policy_qa_hard and 100% policy_qa_soft across all 9 policy questions)
python eval/run_eval.py --strict
```

### ⏳ Milestone 2 (M2): Vendor Research on the Real Web *(Planned)*
- **What it will include:** Justified authority/freshness tables, `Plan Creator -> Plan Reviewer` query planner with stop rules, parallel fetch + extraction workers with shared `Budget` and small-model routing, LLM identity gate, 3 real AI/SaaS vendors in the gold set with cached snapshots, and assessment memory for re-reviews.

### ⏳ Milestone 3 (M3): Router and Graders as Agents *(Planned)*
- **What it will include:** Structured LLM Router (`policy`, `vendor`, `assessment`, `refuse`), LLM Relevance & Groundedness/Hallucination Graders with retry loop (query rewrite / search widening and strict regeneration), and a 30-question routing benchmark.

### ⏳ Milestone 4 (M4): Security — Attack It, Then Defend in Layers *(Planned)*
- **What it will include:** 15 red-team attacks in `tests/test_red_team.py` asserting exact catch points, a second-layer small-model injection classifier, identity-gate ablation study, and DPDP privacy compliance checks.

### ⏳ Milestone 5 (M5): Make It a Product — Graph, API, UI, Human Gate *(Planned)*
- **What it will include:** LangGraph checkpointer + `interrupt()` at `human_gate`, FastAPI background queue & vendor history (`/vendors/{name}/history`) with server-derived ACL groups, Streamlit UI with live progress & trace tree viewer, and per-stage latency/cost observability.

### ⏳ Milestone 6 (M6): Evaluate, Ablations, Write-Up & Demo *(Planned)*
- **What it will include:** Expanded real-vendor gold set, calibrated LLM-as-judge for verdict reasons, component ablation table (no reranker, no identity gate, no freshness decay, no planner), CI workflow, and final demo rehearsal.
