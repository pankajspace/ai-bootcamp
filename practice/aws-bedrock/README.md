# Roadmap to create project with AWS Bedrock from simple to advanced

## Step 1: Set up AWS environment

#### 1. Configure AWS CLI

Before using AWS Bedrock, ensure that the AWS CLI is installed and configured with your credentials:

```bash
aws configure

AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=your_default_region

aws sts get-caller-identity
```

## Step 2: List Available Models with AWS Bedrock
```python
# boto3 is the AWS SDK for Python
import boto3

# Initialize the Bedrock client
client = boto3.client('bedrock')

# Example: List 10 available models
response = client.list_models(MaxResults=10)

print(response)
```

### Step 3: Ask a simple question to the model

```python
# Replace 'model_id' with the ID of the model you want to use
model_id = 'model_id'

# Example: Ask a simple question to the model
response = client.invoke_model(
    ModelId=model_id,
    Body=b'{"question": "What is the capital of France?"}',
    ContentType='application/json'
)

print(response)
```

