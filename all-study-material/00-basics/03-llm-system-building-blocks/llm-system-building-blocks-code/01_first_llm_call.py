"""Worked example: your first LLM call. Send one prompt and print the answer."""
from _common import MODEL, get_client

client = get_client()

reply = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Write a 5-word tagline for a chai shop."}],
)
print(reply.choices[0].message.content)
