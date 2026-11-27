"""Lab 1A · Earnings-call summariser that returns JSON.

Usage:
    python step02_lab_1a_earnings_json.py                      # GPT-4.1-mini (needs OPENAI_API_KEY)
    python step02_lab_1a_earnings_json.py --provider gemini    # Gemini 2.5 Flash (needs GOOGLE_API_KEY)
    python step02_lab_1a_earnings_json.py --provider llama     # Llama 3.1 8B (needs a GPU + HF_TOKEN)
    python step02_lab_1a_earnings_json.py --strict             # the stricter output contract
"""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# The notes keep the transcript in a variable; here it is read from a (fictional) sample file.
transcript_apple_earnings_call = (Path(__file__).parent / "data" / "apple_earnings_call_sample.txt").read_text()

# WHO the model is + WHAT SHAPE the answer must have
system_prompt = """You are a finance analyst. Produce a concise, decision-useful summary of an
earnings call for portfolio managers. Return strict JSON with keys:
company, quarter, revenue, eps, guidance, highlights[], risks[], outlook."""

# Finance corner: name every key, its type and its unit, so numbers arrive as numbers
strict_system_prompt = """You are a finance analyst writing for portfolio managers.
Return strict JSON with exactly these keys and types:
  company: string
  quarter: string, like "FY2025 Q3"
  revenue_usd: number in US dollars, no symbols or words (98700000000, not "$98.7B")
  revenue_growth_yoy_pct: number (6 means +6%)
  eps_usd: number
  guidance: string
  highlights: list of strings
  risks: list of strings
  outlook: one of "positive", "neutral", "negative"
"""

# The actual job + the data. The f"..." drops the transcript text into the {...} slot.
user_prompt = f"""Summarize the following earnings call transcript:
{transcript_apple_earnings_call}"""


def run_openai(system_prompt: str) -> None:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model="gpt-4.1-mini",                                    # cheap + fast: fine for summarising
        input=[{"role": "system", "content": system_prompt},
               {"role": "user",   "content": user_prompt}],
        text={"format": {"type": "json_object"}},                # JSON mode: the reply must be valid JSON
    )

    raw_text = response.output[0].content[0].text                # dig the text out of the response box
    summary  = json.loads(raw_text)                              # JSON text  →  Python dictionary
    print(json.dumps(summary, indent=2))                         # dictionary →  pretty, indented text


def run_gemini(system_prompt: str) -> None:
    from google import genai

    gclient = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])   # separate name, so we don't overwrite 'client'
    resp_genai = gclient.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt + "\n\n" + user_prompt,             # here: both prompts glued into one text
        config={"response_mime_type": "application/json"},         # Gemini's version of JSON mode
    )
    print(resp_genai.text)


def run_llama(system_prompt: str) -> None:
    # Open weights · needs a GPU, e.g. Colab T4, and access to the model on Hugging Face
    import torch, transformers

    pipe = transformers.pipeline(
        "text-generation",
        model="meta-llama/Llama-3.1-8B-Instruct",       # downloaded to YOUR machine — nothing leaves it
        model_kwargs={"torch_dtype": torch.float16},     # half-precision numbers → fits on a 16 GB GPU
        device_map="auto",                               # place it on the GPU automatically
    )
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}]
    outputs = pipe(messages, max_new_tokens=1024)
    print(outputs[0]["generated_text"][-1]["content"])  # the last message is the model's reply


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", choices=["openai", "gemini", "llama"], default="openai")
    ap.add_argument("--strict", action="store_true", help="use the stricter output contract")
    args = ap.parse_args()
    prompt = strict_system_prompt if args.strict else system_prompt
    {"openai": run_openai, "gemini": run_gemini, "llama": run_llama}[args.provider](prompt)
