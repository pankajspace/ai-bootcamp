# Deep Search Agents — Quick Revision & Cheatsheet

> **All 13 Modules (0–12 + Appendix) + 12 Labs + `deepsearch/`** in simple, bite-sized bullets — zero concepts skipped.

---

## 1. Why Deep Search & Architecture (Modules 0–2)

- **Lookup vs Research:** Lookup = 1 fact, 1 step. Research = **multi-source, contradictory, time-changing, high-stakes** (company due diligence).
  - *Normal Search (`2/10`):* SEO-gamed links, ignores dates/conflicts, falls for poisoned pages.
  - *Basic RAG (`5/10`):* Fixed docs, trusts all chunks equally, drops dates, mixes same-name look-alike companies.
  - *Skip Deep Search when:* Simple lookup, static handbook QA (use RAG), `< 1s` chat SLA, or low-stakes task (**uses `~15×` more tokens**!).
- **Anthropic's 5 Workflow Patterns *(all 5 used)*:** **Prompt Chaining** · **Routing** (small vs large LLM) · **Parallelisation** (`asyncio`) · **Orchestrator–Workers** · **Evaluator–Optimiser** (gap loop).
  - *Claude Research Benchmarks:* Opus lead + Sonnet workers = **`+90.2%`** over single Opus; **`80%` of score variance = token budget**; `~4×` tokens (1 agent) / `~15×` (multi-agent); `3–5` parallel workers cut latency up to **`90%`**. *Scale effort:* `1` agent (simple) · `2–4` (comparisons) · `10+` (complex).

```mermaid
flowchart LR
    G["Goal +\nEntityAnchor"] --> P["1. Planner Trio\nCreator → Reviewer → Evaluator"]
    P --> E["2. Parallel Executor\nSearch · Scrape · Tool-less Extract"]
    E --> V["3. Validator & Security\nQuarantine · ID Gate · Shingles · Score"]
    V --> M["4. Merger\nDedupe · Noisy-OR · Conflict Rules"]
    M -- "Gaps & Budget Left" --> P
    M -- "Conf >= 0.6 or Cap Hit" --> S["Synthesiser\nMerged JSON Only (~950 tok)"]
```

---

## 2. Planning, Tools, Schemas & MCP (Modules 3–4)

- **Planner Trio (`planner.py`):**
  1. **Creator:** Writes `5–8` `SubQuestion`s across **5 Lenses**: **Entity** (`EntityAnchor`: domain, country/city, `exclude` look-alikes) · **Claim** · **Time** (`freshness_days`) · **Source Type** · **Decision Criteria** (`high_stakes=True` on licence & security).
  2. **Reviewer *(Code Rubric)*:** Auto-adds missing identity Q, `high_stakes` flags, preferred sources, stop rules & anti-injection rule; flags `< 5`-word vague Qs.
  3. **Evaluator:** **`stop`** if `budget` hit, all high/med Qs reach `conf >= 0.6` (no unresolved conflicts), `max_iterations` hit, or `new_evidence == 0`; else **`continue`** on open gaps with **new query angles** (`queries_used` + `seen_urls` prevent repeats).
- **7-Tool Stack & 4 Pydantic Gates:**
  - *Tools:* Web search (`Tavily / Brave / ddgs` — renamed from `duckduckgo-search`) · Scraper (`trafilatura` / Playwright) · PDF · OCR/VLM · Audio/Video w/ timestamps · Company registries · `think` scratchpad *(largely replaced by native **extended/adaptive thinking** on frontier models; edge tool-callers: Liquid AI `LFM2/2.5`)*. Write tool descriptions as **control logic** (*what, best for, NOT for, I/O*).
  - *Reliability:* Pydantic validation at **Tool In, Tool Out, `Evidence`, `FinalReport`** + `LLM.structured()` **validate-repair retry loop** + timeouts, `429/503` backoff & empty returns (never crash).
- **MCP — Model Context Protocol *(NOT "Capability"!)*:**
  - Turns $M \times N$ custom integrations into **$M + N$**; under Linux Foundation (**Agentic AI Foundation**, Dec 2025).
  - **3 Primitives:** `@tool` (**model-chosen** action) · `@resource` (**app-attached** data) · `@prompt` (**user-chosen** template).
  - **2025–2026 Updates:** Transports = **`stdio`** (never `print()` to stdout!) + **stateless `Streamable HTTP`** (Spec `2026-07-28`; `HTTP+SSE` deprecated). Python SDK v2 renamed `FastMCP` → **`from mcp.server import MCPServer`**. Vet 3rd-party MCP servers for **tool-description injection**.

---

## 3. Validation, Dates & Merging (Modules 5–6)

- **3 Pre-Merge Filters (`validator.py`):**
  1. **Injection Quarantine:** Suspicious instruction text → `accepted = False`.
  2. **Identity Hard Gate (`< 0.5` → rejected!):** Soft weights aren't enough (a real UK regulator page for a same-name UK company still scores `0.82`!).
  3. **Syndicated Copy Collapse:** `5`-word **shingles** + **`Jaccard >= 0.80`** merges wire reprints into **1 `origin_id`** (3 copies of 1 press release = **1 vote**, not 3!).
- **Reliability Score:** $R = 0.45\,\text{Authority} + 0.25\,\text{Freshness} + 0.15\,\text{Identity} + 0.15\,\text{Completeness}$, with $\text{Freshness} = 0.5^{\text{age}/\text{half\_life}}$ (field-tuned authority & half-life, e.g. `regulator=1.0`, `uptime=90d`, `ceo=365d`; undated `= 0.30`).
- **4 Dates & Recency Trap:** Use **`event_date` > `last_updated` > `publication_date`** (+ `retrieval_date`). **Never let recency beat authority** (an attacker's fake page is often the newest!).
- **Merge Pipeline (`merger.py` — ALWAYS Deduplicate BEFORE Resolving Conflicts!):**
  1. **Normalize & Cluster (`0.60`):** Merge `"Series B $40M"` == `"series b 40 million"` (*too loose like `0.15` wrongly merges Series A `$8M` into Series B!*).
  2. **Noisy-OR Confidence Across Independent Origins:** $\text{Conf} = \min\!\big(0.99,\; 1 - \prod_o (1 - r_o)\big)$ — two `0.75` independent sources (`0.938`) beat one `0.85` source.
  3. **High-Stakes Cap (`0.35`):** Licence & security claims without `regulator`/`official` **or** $\ge 2$ independent origins are capped at `0.35` (below `STRONG = 0.60`).
  4. **4 Conflict Outcomes:** **`time_separated`** (newest strong wins `current`, older `>=0.40` kept as `historical`) · **`rejected_weak`** (`<0.40` dropped) · **`accepted_one`** · **`unresolved`** (nothing `>=0.60`, or two strong claims within **`<= 30 days`** → report both!).
- **Safe Synthesis:** Final LLM gets **only merged `FinalReport` JSON (`~950` tok vs `~6,800` raw) — never raw web pages**.

---

## 4. Memory, Security, Budgets, Eval & Law (Modules 7–12)

- **Context & Memory:** Isolate worker contexts; keep raw HTML off the main prompt. **5 Long-Term Memories** (*Entity, Source, Tool, Planning, Failure*) + **6 Guardrails:** revalidate cached facts, fresh evidence wins, keep dates/confidence, avoid personal data, require multi-run proof, and **never save lessons from untrusted web pages** (prevents memory poisoning).
- **Prompt Injection (`OWASP LLM01`) & Security (`security.py`):**
  - Break **Willison's Lethal Trifecta:** *Private Data + Untrusted Content + External Communication* (e.g. markdown image exfiltration).
  - **7 Defence Layers:** **(1)** Strip HTML comments / hidden CSS / zero-width chars → **(2)** Regex quarantine → **(3) Spotlighting** (random `<UNTRUSTED_hex>` tags; cuts attacks `>50% → <2%`) → **(4) Tool-less Dual-LLM / CaMeL extractor** → **(5)** Strict `FieldName` enum → **(6)** `0.35` corroboration cap → **(7)** Audit log. Also block **SSRF** (`localhost`, private IPs, `169.254.169.254`). *(Secure patterns: Plan-Then-Execute, Map-Reduce, Dual-LLM).*
- **Cost & Speed (`budget.py`):** **Extraction = ~68% of tokens** → route extraction/query-gen to **`LLM.small()` (~3× cheaper)**, trim pages (`8k` chars), enforce thread-safe **`Budget`** (`$0.50`, `400k` tok, `300s`, `120` tools; degrade gracefully listing open gaps), cap parallelism with `asyncio.Semaphore`.
- **Evaluation, Law & Domain Adaptation:**
  - **7 Code Metrics:** `field_accuracy`, `history_recall`, `citation_support`, `conflict_recall`, **`forbidden_leaks = 0`** (catches look-alikes & injections; fails when `validation=False`!), `overconfident_errors`, `cost` + **8-dim LLM Judge** (watch verbosity/position/self-bias) + **6 Benchmarks** (`BrowseComp`, `BrowseComp-Plus`, `GAIA`, `FRAMES`, `SimpleQA`, `DeepResearch Bench` RACE/FACT).
  - **Law & Ethics:** Research **companies, not private individuals**. **India DPDP Act 2023** (May 2027 enforcement; fines up to **₹250 crore**; public exemption *only* covers data self-published by that person, **not** 3rd-party posts/scraping!) · **GDPR / EDPB July 2026** scraping rules · obey `robots.txt`.
  - **LangGraph (`lab12`):** Use `StateGraph` when you need **checkpoints, human plan approval, or live UI streaming**. **New Domain = Edit 4 Files:** `schemas.py`, `validator.py`, `planner.py`, `gold_set.json`.

---

## 5. ⚡ Cheatsheet

| Formula / Symptom | Rule / Exact Fix |
|---|---|
| **Reliability & Freshness** | $0.45\,\text{Auth} + 0.25\,\text{Fresh} + 0.15\,\text{ID} + 0.15\,\text{Comp}$ · $\text{Fresh}=0.5^{\text{age}/H}$ · Date: `event > updated > pub` |
| **Noisy-OR & Thresholds** | $\text{Conf} = \min(0.99, 1 - \prod_o(1-r_o))$ · `ID >= 0.5` · Shingle `>= 0.8` · Dedupe `0.6` · Strong `>= 0.6` · High-stakes cap `0.35` · Tie `<= 30d` |
| Look-alike CEO leaks into report | `forbidden_leaks > 0` → enforce **hard gate `identity_match >= 0.5`** + `entity.exclude` |
| Wire copies inflate confidence | Counting URLs instead of origins → run **5-word shingle collapse (`>= 0.8`)** before Noisy-OR |
| Recent fake page beats regulator | Recency trap → quarantine injection + `regulator=1.0` + **`0.35` high-stakes corroboration cap** |

- [ ] **Launch Gate:** Planner Trio + `EntityAnchor` · 4 Pydantic gates + repair loop · 7-layer injection + SSRF defence · Hard ID gate + shingle collapse · Dedupe (`0.6`) before Noisy-OR + `0.35` cap · JSON-only synthesis · `Budget` + `LLM.small()` · Gold-set CI (`forbidden_leaks=0`) + DPDP compliance.

---

## 6. ▶️ Step-by-Step Guide to Run the Code

### Step 1: Offline Setup *(Zero API keys & zero internet needed by default)*
```bash
cd study-material/03-deep-search-agent
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                                 # Defaults to LLM_PROVIDER=mock & SEARCH_PROVIDER=offline
```

### Step 2: Run the Capstone Agent & Verify All 16 Tests
```bash
python run_agent.py                                  # Runs full 2-round due diligence on fictional NimbusPay
python -m pytest -q                                  # Confirms all 16 automated checks pass
```
- **Success check:** Report shows CEO **`Ananya Rao`**, status **`final authorisation`**, funding **`Series B — $40M`**, and **1 quarantined page**.
- **Inspect artifacts:** Open the newest folder inside `runs/` to view `report.md`, `report.json`, `evidence.json`, and step-by-step `trace.jsonl`.

### Step 3: Run All 12 Hands-on Labs *(Always run from `03-deep-search-agent/` root)*
```bash
python labs/lab01_search_vs_rag_vs_deep.py           # Mod 1: Score Search vs Basic RAG vs Deep Search
python labs/lab02_tools_and_schemas.py               # Mod 4: Pydantic schemas + validate-repair loop
python labs/lab03_planner.py                         # Mod 3: Creator → Reviewer → Evaluator + stop rules
python labs/lab04_executor_parallel.py               # Mod 4: Parallel workers & speed-up
python labs/lab05_mcp_client.py                      # Mod 4: Spin up & call an MCP server
python labs/lab06_validation.py                      # Mod 5: Authority, freshness decay, ID gate & copies
python labs/lab07_merge_and_conflicts.py             # Mod 6: Dedupe thresholds, Noisy-OR & conflict rules
python labs/lab08_iteration_memory_context.py        # Mod 7: Round-2 gap loop, compaction & lessons.json
python labs/lab09_prompt_injection.py                # Mod 8: Attack simulation + 7-layer defence
python labs/lab10_cost_latency_budget.py             # Mod 9: Model routing, hard Budget & concurrency
python labs/lab11_evaluation.py                      # Mod 10: Gold-set metrics, ablations & LLM judge
python labs/lab12_langgraph_version.py               # Mod 12: Same agent built as a LangGraph StateGraph
```

### Step 4: Switch On a Live LLM & Real Web Search *(Optional)*
1. Edit `.env` and uncomment **one** LLM provider:
   - *Free Cloud:* `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=...` **or** `LLM_PROVIDER=groq` + `GROQ_API_KEY=...`
   - *Free Local (Ollama):* `ollama pull qwen3:8b` → set `LLM_PROVIDER=ollama` and `LLM_MODEL=qwen3:8b`
   - *Paid Cloud:* `openai`, `anthropic`, or `openrouter` (+ corresponding API key)
2. Set `SEARCH_PROVIDER=ddgs` *(free live web search, no key)* or `SEARCH_PROVIDER=tavily` + `TAVILY_API_KEY=...`.
3. Research a real company *(always pass identity anchors so look-alikes are filtered)*:
   ```bash
   python run_agent.py "Is Razorpay a reliable payment partner today?" \
     --name "Razorpay" --city Bengaluru --country India \
     --industry "payment gateway,payments" --domain razorpay.com --max-usd 0.50
   ```
*(Tip: If you hit `429` rate limits on free tiers, set `DS_MAX_PARALLEL=1` in `.env` or pass `--sequential`; delete `memory/` to reset learned lessons).*
