"""Section 4 · Notebook 2 — Agent as Tool: Tutoring Assistant (Amazon Bedrock edition)

A teacher agent receives a student's question and delegates to the right specialist tutor
(math, writing, science). The teacher always stays in control.

Requirements:
    pip install -r requirements.txt

Prerequisites:
    AWS credentials configured with access to Amazon Bedrock models.

Run:
    python 02_agent_as_tool.py
"""

import os
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel

load_dotenv(find_dotenv())

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)


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
    print(f"Using {MODEL_ID} in {REGION}")

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

