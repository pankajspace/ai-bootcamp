# LLM System Building Blocks: code

Runnable versions of the worked examples in
[1-Building-Blocks-of-LLM-Systems.html](../llm-system-building-blocks-notes/1-Building-Blocks-of-LLM-Systems.html).

| File | Example from the notes | Needs a key? |
|---|---|---|
| `01_first_llm_call.py` | Your first LLM call | yes |
| `02_rules_vs_learning.py` | Rules vs learning (spam filter) | no |
| `03_embeddings.py` | Getting a real embedding | yes |
| `04_prompt_roles_json.py` | System / user messages with a JSON reply | yes |
| `05_ast_explorer.py` | A real AST with Python's `ast` module | no |
| `06_temperature.py` | Same prompt, two temperatures | yes |
| `07_minimal_rag.py` | A minimal RAG in about 20 lines | yes |
| `data/fine_tuning_example.jsonl` | One fine-tuning training example | — |

```bash
cp .env.example .env        # add your OPENAI_API_KEY
uv venv && uv pip install -r requirements.txt
uv run python 01_first_llm_call.py
```

The notes use the model `gpt-6.1-terra`; set `OPENAI_MODEL` in `.env` to use another one.
