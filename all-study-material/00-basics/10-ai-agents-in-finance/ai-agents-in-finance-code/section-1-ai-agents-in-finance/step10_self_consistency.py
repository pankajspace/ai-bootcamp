"""Try it yourself: self-consistency. Sample 5 reasoning paths and take the majority vote."""
from collections import Counter

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

cot_prompt = """You are a financial analysis agent.
Classify the earnings result as: Positive surprise, Neutral surprise or Negative surprise.
Reason step by step before producing the final classification.

Input:
EPS: 1.25 vs consensus 1.20
Revenue: +4% YoY
Margins: Declining
Guidance: Raised
Management: CEO departure announced

End with exactly one line: FINAL: Positive surprise | Neutral surprise | Negative surprise"""

answers = []
for _ in range(5):                                            # 5 independent reasoning paths
    r = client.responses.create(model="gpt-4.1-mini", input=cot_prompt, temperature=1.0)
    last_line = r.output_text.strip().splitlines()[-1]        # e.g. "FINAL: Positive surprise"
    answers.append(last_line.replace("FINAL:", "").strip())

votes = Counter(answers)                                      # counts each distinct answer
print(votes)                                                  # e.g. Counter({'Positive surprise': 3, 'Neutral surprise': 2})
print("Majority:", votes.most_common(1)[0][0])
