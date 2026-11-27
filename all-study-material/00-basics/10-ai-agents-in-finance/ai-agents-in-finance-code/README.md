# AI Agents in Finance: code

Code extracted from the seven HTML lessons in [ai-agents-in-finance-notes](../ai-agents-in-finance-notes/).
Each section is its own project with its own `requirements.txt` and `.env.example`.

| Section (notes) | Folder | Keys | Try first (free) |
|---|---|---|---|
| [1 · AI Agents in Finance](../ai-agents-in-finance-notes/ai-agents-finance-section-1.html) | `section-1-ai-agents-in-finance/` | OpenAI, Financial Modeling Prep; optional Google, Hugging Face | `step08_trend_check.py` |
| [2 · Agent Frameworks and Fundamentals](../ai-agents-in-finance-notes/ai-agents-finance-section-2.html) | `section-2-agent-frameworks-and-fundamentals/` | OpenAI | — |
| [3 · Deep Search Agents](../ai-agents-in-finance-notes/ai-agents-finance-section-3.html) | `section-3-deep-search-agents/` | OpenAI, Financial Datasets, Tavily, SEC e-mail | `step01_try_planner.py` |
| [4 · Reasoning Paradigms](../ai-agents-in-finance-notes/ai-agents-finance-section-4.html) | `section-4-reasoning-paradigms/` | Anthropic | — |
| [5 · Teams of Agents](../ai-agents-in-finance-notes/ai-agents-finance-section-5.html) | `section-5-teams-of-agents/` | OpenAI, Anthropic | `step03_superstep_demo.py`, `step07_claims_rules.py`, `step08_test_claims_rules.py` |
| [6 · Agentic RAG in Finance](../ai-agents-in-finance-notes/ai-agents-finance-section-6.html) | `section-6-agentic-rag/` | Anthropic, OpenAI | `step01_rrf_by_hand.py` |
| [7 · Agent Evaluation and Production](../ai-agents-in-finance-notes/ai-agents-finance-section-7.html) | `section-7-evaluation-and-production/` | none (Anthropic optional) | everything |

## Setup (per section)

```bash
cd section-5-teams-of-agents
cp .env.example .env              # fill in your keys
uv venv && uv pip install -r requirements.txt
uv run python section9_insurance_claims/step07_claims_rules.py
```

Each script loads `.env` with `python-dotenv`, which searches upward from the script, so one `.env`
at the section root also serves scripts in its sub-folders.

## Run order

Scripts are numbered `stepNN_` in the order the lesson uses them, continuing across a section's
sub-folders (the `stepNN_` prefix rather than `NN_` keeps them importable, because later steps import
earlier ones). Unnumbered files are helpers that the steps import, not scripts to run.
The lesson pages still use the original names; drop the `stepNN_` prefix to match them.

| Section | Steps |
|---|---|
| 1 | `step01_finbert_sentiment` → `step02_lab_1a_earnings_json` → `step03_lab_1b_knowledge_cutoff` → `step04_lab_1c_price` → `step05_lab_2a_ratio_tool` → `step06_lab_2b_working_memory` → `step07_lab_2c_episodic_memory` → `step08_trend_check` → `step09_lab_2d_react_price` → `step10_self_consistency` → `step11_lab_2e_news_loop` → `step12_lab_2f_buy_hold_sell` |
| 2 | `framework_comparison/step01_openai_agents_version` → `step02_langchain_version` → `step03_autogen_version` → `step04_pydantic_ai_version`, then the full pipeline: `python -m fundamental_analysis_agent.main AAPL` |
| 3 | `step01_try_planner` (free dry run) → `step02_deep_search_agent` |
| 4 | `step01_self_refine` → `step02_self_consistency` → `step03_react_agent` → `step04_critic_sketch` → `step05_reflexion_shape` → `step06_tot_hedge` → `lats/step07_lats_trim` |
| 5 | `section7_health_analyzer/step01_health_analyzer` → `step02_portfolio_parallel` → `section8_trading_committee/step03_superstep_demo` → `step04_investment_committee` → `step05_backtest` → `step06_adversarial_debate` → `section9_insurance_claims/step07_claims_rules` → `step08_test_claims_rules` (run with `python -m pytest step08_test_claims_rules.py -q`) → `step09_claims_pipeline` → `step10_fraud_investigation` → `step11_underwriting_enrichment` |
| 6 | `section10_agentic_rag/step01_rrf_by_hand` → `step02_agentic_rag_lab` |
| 7 | `section11_evaluation/step01_kyc_agent` → `step02_kyc_dataset` → `step03_kyc_eval` → `step04_judge_calibration` → `step05_drift_monitor` → `section12_production/step06_mini_analyst` → `step07_reliability` → `step08_tracing` → `step09_release_manifest` → `step10_guardrails` |

Notes:

- **Section 1:** `step07_lab_2c_episodic_memory.py` first re-runs Lab 2B to get its conversation.
  `step02_lab_1a_earnings_json.py --provider gemini|llama` and `--strict` cover the lab's variations.
  The notes call the Lab 1A transcript "a made-up Apple call" but don't print it;
  `data/apple_earnings_call_sample.txt` is a short fictional stand-in.
- **Section 2:** the four framework scripts run the same mock-data task. The full pipeline runs from the
  section folder: `python -m fundamental_analysis_agent.main AAPL [--stream] [--trace] [--verbose] [--log-dir logs/] [--watchlist MSFT NVDA]`.
- **Section 3:** `python step02_deep_search_agent.py` writes `output/report.json`.

## What was filled in

Sections 4–7 are verbatim copies of the notes' full listings. Sections 1–3 show code step by step, and
some parts are elided ("… full code: …"). Those gaps are filled in and marked `Filled in` in the code:

- Section 2: `get_balance_sheet`, `get_cash_flow_statement`, the DCF inputs, the sector peer lists,
  the peer-comparison result, news relevance filtering and the sentiment report's top headlines, and
  `main.py`'s `--stream / --trace / --verbose / --log-dir / --watchlist` options.
- Section 3: `tools/sec_filings.py` (`get_risk_factors`), which reads the latest 10-K from SEC EDGAR.
