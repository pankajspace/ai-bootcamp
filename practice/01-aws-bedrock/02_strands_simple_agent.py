import os
from dotenv import load_dotenv

from strands.agent import Agent
from strands.models.bedrock import BedrockModel

# Load environment variables from the .env file
load_dotenv()

# Replace 'model_id' with the ID of the model you want to use
model_id = os.getenv('AWS_BEDROCK_MODEL_ID')

# Initialize the Bedrock model with the specified model ID
model = BedrockModel(model_id=model_id)

# Create an agent with the Bedrock model
agent = Agent(model=model)

# Ask the agent a question
response = agent("What is the capital of France?")

print(response)