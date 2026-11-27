"""Shared setup for the chapter's examples: load .env and pick the model."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# The chapter uses gpt-6.1-terra; set OPENAI_MODEL in .env to use another chat model.
MODEL = os.getenv("OPENAI_MODEL", "gpt-6.1-terra")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def get_client() -> OpenAI:
    return OpenAI()  # reads OPENAI_API_KEY from the environment
