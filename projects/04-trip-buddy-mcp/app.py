"""
app.py
──────
Gradio chat interface for Trip Buddy (DB + RAG + Tools + MCP).
The chatbot delegates every user message to `mcp_client.run_agent`.

How to run:
    uv run app.py
    # or
    python app.py
"""

import gradio as gr
from db import list_places
from mcp_client import MODEL, run_agent
from rag import get_tip_count


def chat_handler(message, _history):
    """Gradio calls this for every chat message and routes it through the MCP client."""
    try:
        return run_agent(message)
    except Exception as e:
        return (
            f"Something went wrong: {e}\n\n"
            'Try: *"We are 4 friends with ₹12,000 each. Can we do Goa for 3 nights?"*  \n'
            "Or: **list** to see all destinations."
        )


demo = gr.ChatInterface(
    fn=chat_handler,
    title="Trip Buddy (DB + RAG + Tools + MCP)",
    description=(
        "Plan a trip with friends. The chatbot talks to an **MCP Client**, which calls the "
        "**MCP Server** (`stdio`) to fetch prices from the 3-table SQLite DB, do exact maths "
        "with tools, run multi-chain evaluations, and retrieve tips from the ChromaDB travel notebook.  \n"
        "Type **list** to see all destinations."
    ),
    examples=[
        "list",
        "We are 4 friends with ₹12,000 each. Can we do Goa for 3 nights?",
        "Is Manali a good idea in July?",
        "How much is Hampi for 5 friends, 2 nights?",
        "Which trips fit ₹8,000 each for 3 friends, 2 nights?",
    ],
)

if __name__ == "__main__":
    print("Starting Trip Buddy (MCP Edition)...")
    print(f"  model: {MODEL}")
    print(f"  {len(list_places())} destinations in 3-table SQLite DB")
    print(f"  {get_tip_count()} tips in ChromaDB travel notebook")
    demo.launch(debug=True)

