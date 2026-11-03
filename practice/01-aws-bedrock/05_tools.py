import os
import logging
import warnings
from dotenv import load_dotenv

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# Suppress deprecation logs and warnings for clean output
warnings.filterwarnings("ignore")
logging.getLogger("strands_tools").setLevel(logging.ERROR)

# Load environment variables from the .env file
load_dotenv()

model_id = os.getenv('AWS_BEDROCK_MODEL_ID')
model = BedrockModel(model_id=model_id)

# ==============================================================================
# 1. CUSTOM TOOL:
# Custom tools REQUIRE the `@tool` decorator, type hints, and docstrings.
# Without `@tool`, Strands cannot register the function as an agent tool.
# ==============================================================================
@tool
def greet(name: str) -> str:
    """
    Greet a person by their name.
    Args:
        name: The name of the person to greet.
    Returns:
        A personalized greeting message.
    """
    return f"Hello, {name}! Welcome to Strands Agents."


# ==============================================================================
# 2. INBUILT / PREBUILT TOOLS:
# Strands provides prebuilt tools for common capabilities:
#
# A) From `strands_tools` (strands-agents-tools package):
#    - calculator: exact math computations via SymPy (powers, roots, algebra)
#
# B) From `strands.vended_tools` (built directly into strands-agents):
#    - http_request: call external APIs
#    - write: write files to the file system
#    - read: read files from the file system
# ==============================================================================
from strands_tools import calculator

# Create agent with both custom and inbuilt tools
agent = Agent(
    model=model,
    tools=[greet, calculator],
    callback_handler=None
)

# ------------------------------------------------------------------------------
# Test 1: Agent invokes our Custom Tool (`greet`)
# ------------------------------------------------------------------------------
print("=== 1. Custom Tool Execution (greet) ===")
response = agent("Say hi to Pankaj.")
print(response)

# ------------------------------------------------------------------------------
# Test 2: Agent invokes the Inbuilt Tool (`calculator`)
# ------------------------------------------------------------------------------
print("\n=== 2. Inbuilt Tool Execution (calculator) ===")
response = agent("What is 42 raised to the power of 5?")
print(response)
