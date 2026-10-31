# Trip Buddy (DB + RAG + Tools)

Plan a trip with friends using **SQLite** for destination and stay pricing, **ChromaDB + HuggingFace Embeddings** for the travel tips notebook (RAG), **LangChain Tools** for exact cost calculations, and a **Gradio** chat UI.

## Folder Structure

```text
projects/03-trip-buddy/
├── db.py              # SQLite database (places + stays tables & lookups)
├── rag.py             # ChromaDB vector store + sentence-transformers embeddings
├── tools.py           # @tool functions for DB lookup & exact trip arithmetic
├── agent.py           # ChatOpenAI tool-calling loop augmented with RAG context
├── app.py             # Gradio ChatInterface ("Trip Buddy (DB + RAG + Tools)")
├── requirements.txt   # Project dependencies
└── README.md          # Documentation
```

## Setup & Run

1. **Install dependencies:**
   ```bash
   pip install -r projects/03-trip-buddy/requirements.txt
   ```

2. **Configure environment (`.env`):**
   Ensure `OPENAI_API_KEY` (and optional `OPENAI_MODEL`, defaults to `gpt-6-luna`) is set in your `.env` file.

3. **Launch the Gradio app:**
   ```bash
   python projects/03-trip-buddy/app.py
   ```

## Example Prompts

- `list`
- `We are 4 friends with ₹12,000 each. Can we do Goa for 3 nights?`
- `Is Manali a good idea in July?`
- `How much is Hampi for 5 friends, 2 nights?`
- `Which trips fit ₹8,000 each for 3 friends, 2 nights?`

