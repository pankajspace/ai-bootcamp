"""Section 4 · Notebook 2 — Agent as Tool: Tutoring Assistant (Groq edition)

A teacher agent receives a student's question and delegates to the right specialist tutor
(math, writing, science). The teacher always stays in control.

Requirements:
    pip install -r requirements-groq.txt

Prerequisites:
    GROQ_API_KEY in environment or .env file (free at console.groq.com/keys).

Run:
    python 02_agent_as_tool_groq.py
"""

import os
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

load_dotenv(find_dotenv())

MODEL_ID = os.getenv("GROQ_MODEL_ID", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = OpenAIModel(
    client_args={
        "api_key": GROQ_API_KEY,
        "base_url": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        "max_retries": 5,
    },
    model_id=MODEL_ID,
    # Groq reasoning models stream their thinking by default; hide it so only the answer prints.
    params={"extra_body": {"include_reasoning": False}},
)


# -----------------------------------------------------------------------------
# Specialist agents
# -----------------------------------------------------------------------------
# Each specialist gets a `name` and a `description`. When an agent is used as a tool,
# the name becomes the tool name and the description tells the teacher when to call it.

math_tutor = Agent(
    name="math_tutor",
    description="Solves mathematical equations and explains math concepts step by step",
    model=model,
    system_prompt="You are a math tutor. Solve math problems and explain your solutions clearly, step by step.",
    callback_handler=None,
)

writing_coach = Agent(
    name="writing_coach",
    description="Helps with writing, grammar, and essay structure",
    model=model,
    system_prompt="You are a writing coach. Help with writing, grammar, and essay structure. Provide constructive feedback.",
    callback_handler=None,
)

science_helper = Agent(
    name="science_helper",
    description="Explains scientific concepts and principles in simple terms",
    model=model,
    system_prompt="You are a science tutor. Explain scientific concepts clearly using simple language and real-world examples.",
    callback_handler=None,
)


# -----------------------------------------------------------------------------
# The teacher (orchestrator)
# -----------------------------------------------------------------------------
# Pass the specialist agents straight into `tools=[...]` — Strands wraps each one as a callable tool.

teacher = Agent(
    model=model,
    system_prompt="""You are a teacher who helps students by delegating to specialist tutors.
Never solve problems yourself. Always delegate to the appropriate specialist:
- math_tutor: for math problems and equations
- writing_coach: for writing, grammar, and essays
- science_helper: for science questions

After receiving the specialist's response, present it to the student in a friendly way.""",
    tools=[math_tutor, writing_coach, science_helper],
)


def main():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set. Please set it in your environment or in a .env file.")

    print(f"Using {MODEL_ID} on Groq")

    # Test with different questions
    # Math → math_tutor
    print("\n--- Question 1: Math ---")
    question_1 = "Can you help me solve this quadratic equation: x^2 + 5x + 6 = 0?"
    print(f"Student: {question_1}\n")
    response = teacher(question_1)
    print(response)

    # Writing → writing_coach
    print("\n--- Question 2: Writing ---")
    question_2 = "How do I write a strong thesis statement for my essay about climate change?"
    print(f"Student: {question_2}\n")
    response = teacher(question_2)
    print(response)

    # Science → science_helper
    print("\n--- Question 3: Science ---")
    question_3 = "Why does ice float on water?"
    print(f"Student: {question_3}\n")
    response = teacher(question_3)
    print(response)


if __name__ == "__main__":
    main()

