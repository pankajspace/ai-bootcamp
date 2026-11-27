"""Lab 1B · Knowledge cutoff: ask a model with a known training cutoff for "the latest" news."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-4.1",
    input="Give me the latest news about NVIDIA.",
)
print(response.output_text)
