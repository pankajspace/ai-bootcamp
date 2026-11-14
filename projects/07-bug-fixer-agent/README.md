# Project 07 · Autonomous Bug Diagnosis & Repair Agent (LangGraph CLI)

An autonomous AI coding agent built with **LangGraph** and **LangChain** that executes Python code or a local test suite, captures runtime exceptions and test failures, diagnoses the root cause using structured LLM output (`BugDiagnosis`), patches the source file with a unified diff, and re-runs verification in a closed loop until all checks pass.

---

## 🏗️ Architecture (The Agent Loop)

```text
       START
         │
         ▼
┌─────────────────────────┐   no error /
│  execute_tests_node     │─────────────────► END
└─────────────────────────┘   max retries
         │            ▲
         │ error      │
         ▼            │
┌─────────────────────────┐
│   diagnose_bug_node     │
│  (Structured Diagnosis) │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│    apply_patch_node     │
│ (Syntax Check + Diff)   │
└─────────────────────────┘
```

---

## 📂 Project Structure

```text
projects/07-bug-fixer-agent/
├── agentic_bug_fixing_openai.py   # Standalone single-file LangGraph bug-fixing lesson (OpenAI)
├── run_bug_fixer.py               # Multi-file local codebase CLI agent (--workspace, --dry-run, --reset)
├── bug_fixer/
│   ├── __init__.py
│   ├── schemas.py                 # Pydantic schemas: BugDiagnosis, ExecutionResult, PatchRecord
│   ├── executor.py                # Subprocess test runner, traceback parser & unified diff generator
│   └── graph.py                   # LangGraph StateGraph (execute -> diagnose -> patch -> verify)
├── sample_buggy_app/
│   ├── billing.py                 # Sample module with 3 intentional bugs (KeyError, math bug, ZeroDivisionError)
│   └── test_billing.py            # Unittest suite verifying invoice & bill-splitting logic
├── tests/
│   └── test_bug_fixer.py          # Automated unit & end-to-end tests for the agent
└── requirements.txt
```

---

## 🚀 Quick Start (CLI)

### 1. Run the Standalone Function Bug-Fixing Script (`agentic_bug_fixing_openai.py`)
```bash
# Run built-in sample 1 (Order average with mixed types, missing keys & ZeroDivisionError)
.venv/bin/python projects/07-bug-fixer-agent/agentic_bug_fixing_openai.py

# Run built-in sample 2 (Student ranking with None scores, IndexError & missing keys)
.venv/bin/python projects/07-bug-fixer-agent/agentic_bug_fixing_openai.py --sample off_by_one_and_key
```

### 2. Run the Local Codebase Bug Fixer CLI (`run_bug_fixer.py`)
```bash
# Diagnose & fix sample_buggy_app using OpenAI (resets billing.py to buggy state first)
.venv/bin/python projects/07-bug-fixer-agent/run_bug_fixer.py --reset

# Run with Groq instead of OpenAI
.venv/bin/python projects/07-bug-fixer-agent/run_bug_fixer.py --reset --provider groq

# Run offline deterministic mode (no API key required)
.venv/bin/python projects/07-bug-fixer-agent/run_bug_fixer.py --reset --provider mock

# Preview diagnosis and unified diff without modifying files on disk
.venv/bin/python projects/07-bug-fixer-agent/run_bug_fixer.py --reset --dry-run

# Run on any local directory with a custom test command
.venv/bin/python projects/07-bug-fixer-agent/run_bug_fixer.py \
  --workspace /path/to/your/python/project \
  --cmd "python -m unittest discover -v"
```

### 3. Run the Agent's Unit Test Suite
```bash
.venv/bin/python -m unittest discover -s projects/07-bug-fixer-agent/tests -v
```
