# AI with AWS Bedrock

## 0: Setup

#### 0.1. Configure AWS CLI

Before using AWS Bedrock, ensure that the AWS CLI is installed and configured with your credentials:

```bash
aws configure

AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=your_default_region

aws sts get-caller-identity
```

#### 0.2. Python Environment Setup

Ensure you have Python installed. It's recommended to use a virtual environment:

```bash
cd practice/01-aws-bedrock
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### 0.3. Install Required Python Packages

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Demo 1: List Bedrock Models
requirements.txt
```
boto3
```

```bash
python3 practice/01-aws-bedrock/01_list_bedrock_models.py
```

## Demo 2: Simple Agent
requirements.txt
```
python-dotenv
strands-agents
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/02_simple_agent.py
```

## Demo 3: Agent with roles
requirements.txt
```
python-dotenv
strands-agents
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/03_agent_roles.py
```

## Demo 4: Agent with conversation history
requirements.txt
```
python-dotenv
strands-agents
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/04_agent_conversation_history.py
```

## Demo 5: Agent with tools
requirements.txt
```
python-dotenv
strands-agents
strands-agents-tools
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/05_tools.py
```

## Demo 6: Agent with asynchronous tools
requirements.txt
```
python-dotenv
strands-agents
strands-agents-tools
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/06_async_tools.py
```

## Demo 7: Agent with class-based tools
requirements.txt
```
python-dotenv
strands-agents
strands-agents-tools
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/07_class_based_tools.py
```

## Demo 7: Agent with class-based tools
requirements.txt
```
python-dotenv
strands-agents
strands-agents-tools
```

.env
```
AWS_BEDROCK_MODEL_ID=your_model_id
```

```bash
python3 practice/01-aws-bedrock/07_class_based_tools.py
```
