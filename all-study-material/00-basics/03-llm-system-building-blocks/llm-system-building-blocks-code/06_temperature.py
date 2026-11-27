"""Worked example: same prompt, two temperatures (0 = repeatable, 1.0 = varied)."""
from _common import MODEL, get_client

client = get_client()

for t in [0, 1.0]:
    for run in range(2):
        r = client.chat.completions.create(model=MODEL, temperature=t,
              messages=[{"role": "user", "content": "Name a monsoon snack in 2 words."}])
        print(t, r.choices[0].message.content)
