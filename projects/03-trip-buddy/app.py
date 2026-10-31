"""
app.py
──────
Gradio web interface for Trip Buddy (DB + RAG + Tools).

How to run:
    uv run app.py
    # or
    python app.py
"""

import gradio as gr
from agent import run_agent


def chat_fn(message: str, history: list) -> str:
    return run_agent(message, history)


demo = gr.ChatInterface(
    fn=chat_fn,
    title="Trip Buddy (DB + RAG + Tools)",
    description=(
        "Plan a trip with friends. The agent fetches prices from the DB, "
        "does exact maths with tools, and uses the travel notebook for tips.\n\n"
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
    demo.launch()

