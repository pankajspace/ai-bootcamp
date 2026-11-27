"""Worked example: system vs user messages, with the reply forced into a JSON shape."""
from _common import MODEL, get_client

client = get_client()

reply = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content":
            "You are a friendly personal-finance teacher. "          # persona
            "The user just got their first salary; suggest only safe options. "  # context
            "Reply ONLY as JSON: {\"summary\": str, \"tips\": [3 strings]}"},  # format
        {"role": "user", "content":
            "Explain compound interest with a ₹5,000 monthly SIP example."},  # instruction
    ],
)
print(reply.choices[0].message.content)
