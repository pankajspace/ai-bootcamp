import os
from dotenv import load_dotenv

from strands.agent import Agent
from strands.models.bedrock import BedrockModel

# Load environment variables from the .env file
load_dotenv()

# Initialize the Bedrock model
model_id = os.getenv('AWS_BEDROCK_MODEL_ID')
model = BedrockModel(model_id=model_id)

# Create an agent (callback_handler=None prevents duplicate prints)
agent = Agent(model=model, callback_handler=None)

print("Chat with the agent (type 'exit' to quit):\n")

# Interactive loop: agent automatically remembers previous questions and answers
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = agent(user_input)
    print(f"Assistant: {response}\n")
