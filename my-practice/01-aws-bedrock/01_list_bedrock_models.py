# boto3 is the AWS SDK for Python
import boto3

# Initialize the Bedrock client
client = boto3.client('bedrock')

# List available foundation models
response = client.list_foundation_models()

# Print the first 20 models
models = response.get('modelSummaries', [])
print(f"Total foundation models found: {len(models)}\n")
for model in models[:20]:
    print(f"- {model['modelName']} ({model['modelId']}) by {model['providerName']}")
