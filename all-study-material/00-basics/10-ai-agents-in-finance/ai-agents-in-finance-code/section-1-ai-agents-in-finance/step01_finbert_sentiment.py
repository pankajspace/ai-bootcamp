"""Try it: see a classifier in action (FinBERT runs on a laptop CPU, no API key)."""
from transformers import pipeline

# FinBERT is a classifier: sentence in → label out. It cannot write text.
finbert = pipeline("text-classification", model="ProsusAI/finbert")

headlines = [
    "Apple reports record-breaking revenue in Q4 despite market slowdown",
    "Tesla stock falls after earnings miss expectations",
]
for h in headlines:
    print(h, "→", finbert(h)[0])     # e.g. {'label': 'positive', 'score': 0.93}
