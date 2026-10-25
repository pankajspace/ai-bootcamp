# AI Projects

## 1. 🚀 Environment Setup

### 1. Create and Activate Virtual Environment (`venv`)

Create a virtual environment:
```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Command Prompt / PowerShell)**:
  ```bash
  .venv\Scripts\activate
  ```

*(To exit the virtual environment later, simply run `deactivate`)*

---

## 2. 📦 Installing Requirements

Once your virtual environment is active, install the dependencies:

### Option A: Install everything across all sections (Recommended)
```bash
pip install -r requirements.txt
```

### Option B: Install section-by-section
- **Day 1 · Section 1 (Foundations & Chains):**
  ```bash
  pip install -r day1/section1/requirements.txt
  ```
- **Day 1 · Section 2 (Agents, Tools & Structured Output):**
  ```bash
  pip install -r day1/section2/requirements.txt
  ```

---

## 3. ⚙️ Configuration (`.env`)

Before running API-based scripts, ensure you have your `.env` configured in the project root:

```bash
cp .env.example .env
```

Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=section-01-langchain-foundations
# If using APAC region for LangSmith, uncomment:
# LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com
```

---

## 4. ▶️ Running Python Scripts

### Method 1: With Activated `venv` (Standard)
```bash
source .venv/bin/activate
python day1/section1/01_hello_world_env_setup.py
python day1/section1/02_summary_chain_openai.py
```

### Method 2: Direct Execution (Without Activating)
You can directly invoke Python using the virtual environment's binary:
```bash
.venv/bin/python day1/section1/01_hello_world_env_setup.py
.venv/bin/python day1/section1/02_summary_chain_openai.py
```

---

## 5. 🦙 Running Local Models (Ollama)

For scripts that use local models (e.g. `day1/section1/03_summary_chain_ollama.py`):

1. **Install and start Ollama**:
   ```bash
   ollama serve
   ```
2. **Download the model**:
   ```bash
   ollama pull gemma3:270m
   ```
3. **Run the script**:
   ```bash
   python day1/section1/03_summary_chain_ollama.py
   ```

---

# 📚 Reference Material
1. [AI Reusable Snippets](snippets/ai-reusable-snippets.md)

# Notes
1. Alphavantage API key may be required for certain financial data scripts.
2. https://site.financialmodelingprep.com/