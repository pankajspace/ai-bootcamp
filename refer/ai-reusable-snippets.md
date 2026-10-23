<!--
Source: ai-reusable-snippets.html
Title: AI Reusable Code Snippets & Quick Revision Guide | TechToday
Theme-color: #0b0d10
Stylesheets: ai-snippets-study.css, ../../site-header.css
Scripts: ai-study.js
-->

Navigation: [TechToday](../../index.html) · [← AI Projects](ai-projects.html)

# AI Reusable Code Snippets & Quick Revision Guide

A domain-agnostic, copy-paste-ready catalog of reusable Python & AI engineering templates distilled from the `practice/` workspace modules (`01-python` through `08-ai-mcp-evals`) and the AI Infusion Test (`study/11-ai-infusion-test`). All domain-specific business logic has been replaced with generic, plug-and-play skeletons.

---

## Table of Contents (Index)

1. [1. Python Fundamentals for AI Systems (`practice/01-python`)](#1-python-fundamentals-for-ai-systems)
   1. [1.1. Type Hints, Optional/Union & Unpacking](#11-type-hints-optionalunion--unpacking)
   2. [1.2. Comprehensions, Filtering & Multi-Key Sorting](#12-comprehensions-filtering--multi-key-sorting)
   3. [1.3. Defensive Error Handling Wrapper](#13-defensive-error-handling-wrapper)
   4. [1.4. Stateful OOP Resource Class Template](#14-stateful-oop-resource-class-template)
   5. [1.5. Async I/O Concurrency (`asyncio.gather` & `create_task`)](#15-async-io-concurrency-asynciogather--create_task)
2. [2. Multi-Provider LLM Clients & LangChain Basics (`practice/02-ai-basics`)](#2-multi-provider-llm-clients--langchain-basics)
   1. [2.1. Multi-Provider OpenAI-Compatible Client (`OpenAI`, `Groq`, `Gemini`)](#21-multi-provider-openai-compatible-client-openai-groq-gemini)
   2. [2.2. LangChain LCEL Pipe Chain (`prompt | model | parser`)](#22-langchain-lcel-pipe-chain-prompt--model--parser)
   3. [2.3. Stateful Multi-Turn Chat (`MessagesPlaceholder`)](#23-stateful-multi-turn-chat-messagesplaceholder)
   4. [2.4. Raw OpenAI Tool-Calling Loop (No Framework)](#24-raw-openai-tool-calling-loop-no-framework)
   5. [2.5. LangChain Multi-Tool Agent with Swappable Provider & Trace](#25-langchain-multi-tool-agent-with-swappable-provider--trace)
   6. [2.6. Token Cost Estimator (`estimate_token_cost`)](#26-token-cost-estimator-estimate_token_cost)
3. [3. Document Chunking, Embeddings & Local RAG (`practice/03-ai-rag-chroma`)](#3-document-chunking-embeddings--local-rag)
   1. [3.1. Sliding-Window Document Chunking (`RecursiveCharacterTextSplitter`)](#31-sliding-window-document-chunking-recursivecharactertextsplitter)
   2. [3.2. Local Sentence Embeddings & Cosine Similarity (`SentenceTransformer`)](#32-local-sentence-embeddings--cosine-similarity-sentencetransformer)
   3. [3.3. End-to-End Local Vector RAG (`HuggingFaceEmbeddings` + `Chroma`)](#33-end-to-end-local-vector-rag-huggingfaceembeddings--chroma)
   4. [3.4. Top-K Semantic Similarity Search (`SentenceTransformer` & `util.cos_sim`)](#34-top-k-semantic-similarity-search-sentencetransformer--utilcos_sim)
   5. [3.5. Hybrid Search Reciprocal Rank Fusion (`reciprocal_rank_fusion`)](#35-hybrid-search-reciprocal-rank-fusion-reciprocal_rank_fusion)
4. [4. ML Model Training, ChromaDB Server & Redis Memory (`practice/04-ai-model-training-chromadb`)](#4-ml-model-training-chromadb-server--redis-memory)
   1. [4.1. Scikit-Learn Training, `joblib` Serialization & Pydantic Inference](#41-scikit-learn-training-joblib-serialization--pydantic-inference)
   2. [4.2. ChromaDB HTTP/Ephemeral Client & Document Folder Ingestion](#42-chromadb-httpephemeral-client--document-folder-ingestion)
   3. [4.3. Stateful Tool-Calling Agent with Redis Session Memory](#43-stateful-tool-calling-agent-with-redis-session-memory)
5. [5. AWS Bedrock, Strands Agents & LangGraph (`practice/05-ai-aws-strands`)](#5-aws-bedrock-strands-agents--langgraph)
   1. [5.1. Minimal AWS Strands Agent on Amazon Bedrock (`BedrockModel`)](#51-minimal-aws-strands-agent-on-amazon-bedrock-bedrockmodel)
   2. [5.2. LangGraph Prebuilt ReAct Agent (`init_chat_model` + `create_react_agent`)](#52-langgraph-prebuilt-react-agent-init_chat_model--create_react_agent)
   3. [5.3. Function-to-Tool Pattern (`@tool` + Type Hints + Docstring)](#53-function-to-tool-pattern-tool--type-hints--docstring)
   4. [5.4. Pre-Built Community Tools & Unattended Consent (`strands_tools`)](#54-pre-built-community-tools--unattended-consent-strands_tools)
   5. [5.5. Class-Based Shared-Resource Tools](#55-class-based-shared-resource-tools)
   6. [5.6. Async Parallel Tool Execution (`async def` + `invoke_async`)](#56-async-parallel-tool-execution-async-def--invoke_async)
6. [6. AI Systems: Prompting, Sycophancy & Multi-Judge Bench (`practice/06-ai-systems`)](#6-ai-systems-prompting-sycophancy--multi-judge-bench)
   1. [6.1. Prompting Strategies (Direct vs. Zero-Shot CoT vs. Few-Shot CoT) & Answer Extraction](#61-prompting-strategies-direct-vs-zero-shot-cot-vs-few-shot-cot--answer-extraction)
   2. [6.2. Multi-Turn Adversarial Pushback Runner & Forced `VERDICT:` Scorer](#62-multi-turn-adversarial-pushback-runner--forced-verdict-scorer)
   3. [6.3. Multi-Judge Parallel Voting Bench & Deterministic Threshold Gate](#63-multi-judge-parallel-voting-bench--deterministic-threshold-gate)
7. [7. AI Reliability: Determinism, Schema Calibration & Error Injection (`practice/07-ai-reliability`)](#7-ai-reliability-determinism-schema-calibration--error-injection)
   1. [7.1. Multi-Run Stochastic Accuracy Evaluator](#71-multi-run-stochastic-accuracy-evaluator)
   2. [7.2. Enforced JSON Schema (`response_format`) & Exponential Backoff Retry](#72-enforced-json-schema-response_format--exponential-backoff-retry)
   3. [7.3. Forced Tool Routing Benchmark (`tool_choice="required"`)](#73-forced-tool-routing-benchmark-tool_choicerequired)
   4. [7.4. Structured Tool Error Payload & Anti-Hallucination System Prompt](#74-structured-tool-error-payload--anti-hallucination-system-prompt)
8. [8. Model Context Protocol (MCP) & Agent Evals (`practice/08-ai-mcp-evals`)](#8-model-context-protocol-mcp--agent-evals)
   1. [8.1. FastMCP Tool Server over `stdio` (`FastMCP` & `@mcp.tool`)](#81-fastmcp-tool-server-over-stdio-fastmcp--mcptool)
   2. [8.2. Direct MCP Client Protocol Plumbing (No LLM)](#82-direct-mcp-client-protocol-plumbing-no-llm)
   3. [8.3. MCP-Enabled LLM Agent (`to_openai_format` Bridge + Agent Loop)](#83-mcp-enabled-llm-agent-to_openai_format-bridge--agent-loop)
   4. [8.4. Automated Agent Evaluation Suite (Routing + Fact Assertions)](#84-automated-agent-evaluation-suite-routing--fact-assertions)
9. [9. Docker & Compose Templates for AI Projects (`practice/*/Dockerfile`)](#9-docker--compose-templates-for-ai-projects)
   1. [9.1. Layer-Cached Python 3.12 `Dockerfile`](#91-layer-cached-python-312-dockerfile)
   2. [9.2. Multi-Service `docker-compose.yml` (App + ChromaDB + Redis)](#92-multi-service-docker-composeyml-app--chromadb--redis)
10. [10. Quick Revision Cheatsheet](#10-quick-revision-cheatsheet)
    1. [10.1. Practice Module-to-Pattern Quick Map](#101-practice-module-to-pattern-quick-map)
    2. [10.2. LLM Provider & Framework Selection Rules](#102-llm-provider--framework-selection-rules)
    3. [10.3. Tool-Calling & Agent Architecture Golden Rules](#103-tool-calling--agent-architecture-golden-rules)
    4. [10.4. RAG, Embeddings & Memory Checklist](#104-rag-embeddings--memory-checklist)
    5. [10.5. Reliability, Guardrails & Evaluation Checklist](#105-reliability-guardrails--evaluation-checklist)
    6. [10.6. Essential One-Liners & CLI Commands](#106-essential-one-liners--cli-commands)
    7. [10.7. Python Shorthands & Idioms for AI Coding Tests](#107-python-shorthands--idioms-for-ai-coding-tests)
11. [11. AI Infusion Test: Coding Solutions, Python Idioms & MCQs (`study/11-ai-infusion-test`)](#11-ai-infusion-test-coding-solutions-python-idioms--mcqs)
    1. [11.1. Coding 1: Token Cost Estimator (`estimate_token_cost`) & Python Shorthands](#111-coding-1-token-cost-estimator-estimate_token_cost--python-shorthands)
    2. [11.2. Coding 2: Hybrid Search Rank Fusion (`reciprocal_rank_fusion`) & Python Shorthands](#112-coding-2-hybrid-search-rank-fusion-reciprocal_rank_fusion--python-shorthands)
    3. [11.3. Coding 3: Semantic Similarity Search (`semantic_search`) & Python Shorthands](#113-coding-3-semantic-similarity-search-semantic_search--python-shorthands)
    4. [11.4. MCQs 1–3: Tokenizer Logic (BPE), Chain vs. Agent & Output Parser (`StrOutputParser`)](#114-mcqs-13-tokenizer-logic-bpe-chain-vs-agent--output-parser-stroutputparser)
    5. [11.5. MCQs 4–6: Chunk Overlap Boundary, Cloud LLM Three Gates & Function-to-Tool (`@tool`)](#115-mcqs-46-chunk-overlap-boundary-cloud-llm-three-gates--function-to-tool-tool)
    6. [11.6. MCQs 7–9: Bi-Encoder vs. Cross-Encoder Reranking, Hybrid Search (BM25 + RRF) & Retrieval vs. Agents](#116-mcqs-79-bi-encoder-vs-cross-encoder-reranking-hybrid-search-bm25--rrf--retrieval-vs-agents)

---

## 1. Python Fundamentals for AI Systems

### 1.1. Type Hints, Optional/Union & Unpacking
Source: `practice/01-python/02-type-hints.py`, `practice/01-python/12-unpacking.py`

```python
from typing import Any

# 1. Explicit type annotations (also used by LLM @tool decorators to generate JSON schemas)
def process_payload(
    item_id: str,
    count: int = 1,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize input parameters with safe defaults for optional collections."""
    return {
        "item_id": item_id.strip(),
        "count": count,
        "tags": tags or [],
        "metadata": metadata or {},
    }

# 2. Sequence star-unpacking and dictionary merging (**kwargs)
first, *middle, last = [1, 2, 3, 4, 5]  # first=1, middle=[2, 3, 4], last=5
defaults = {"temperature": 0.0, "timeout": 15.0}
overrides = {"temperature": 0.7, "model": "gpt-4o-mini"}
config = {**defaults, **overrides}
```

### 1.2. Comprehensions, Filtering & Multi-Key Sorting
Source: `practice/01-python/11-sorting.py`, `practice/01-python/13-list-comprehensions.py`

```python
# 1. List and dictionary comprehensions with conditional filtering
records = [("id_1", 0.88), ("id_2", 0.42), ("id_3", 0.95)]
filtered_ids = [key for key, score in records if score >= 0.70]
score_map = {key: score for key, score in records}

# 2. Multi-key sorting with lambda (e.g., sort by count descending, then score descending)
items = [
    {"label": "option_a", "count": 1, "score": 0.90},
    {"label": "option_b", "count": 2, "score": 0.85},
    {"label": "option_c", "count": 2, "score": 0.92},
]
ranked = sorted(items, key=lambda x: (-x["count"], -x["score"]))
```

### 1.3. Defensive Error Handling Wrapper
Source: `practice/01-python/04-error-handling.py`

```python
from typing import Any, Callable

def safe_execute(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Execute a callable and return a structured result/error dict without raising."""
    try:
        return {"status": "ok", "result": fn(*args, **kwargs)}
    except (ValueError, TypeError, KeyError) as exc:
        return {"status": "validation_error", "error": str(exc)}
    except Exception as exc:
        return {"status": "runtime_error", "error": f"{type(exc).__name__}: {exc}"}
```

### 1.4. Stateful OOP Resource Class Template
Source: `practice/01-python/16-oop.py`

```python
from typing import Any

class StatefulStore:
    """Generic in-memory key-value resource store with invariant checks."""

    def __init__(self, initial_state: dict[str, Any] | None = None) -> None:
        self._store: dict[str, Any] = dict(initial_state or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if not key:
            raise ValueError("Key must be a non-empty string.")
        self._store[key] = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self._store.keys())!r})"
```

### 1.5. Async I/O Concurrency (`asyncio.gather` & `create_task`)
Source: `practice/01-python/15-async-await.py`

```python
import asyncio
import time
from typing import Any

async def async_io_task(task_id: str, delay_sec: float) -> dict[str, Any]:
    """Simulate a non-blocking network/API call."""
    await asyncio.sleep(delay_sec)
    return {"task_id": task_id, "status": "ok"}

async def run_concurrent_tasks(tasks_input: list[tuple[str, float]]) -> list[dict[str, Any]]:
    start = time.perf_counter()

    # 1. Execute all coroutines concurrently (total wall time ~ max(delays), not sum)
    coros = [async_io_task(tid, delay) for tid, delay in tasks_input]
    results = await asyncio.gather(*coros)

    # 2. Optional: schedule an independent background task on the event loop
    bg_task = asyncio.create_task(async_io_task("background_job", 0.01))
    await bg_task

    print(f"Completed in {time.perf_counter() - start:.3f}s")
    return list(results)

if __name__ == "__main__":
    asyncio.run(run_concurrent_tasks([("t1", 0.05), ("t2", 0.03), ("t3", 0.01)]))
```

---

## 2. Multi-Provider LLM Clients & LangChain Basics

### 2.1. Multi-Provider OpenAI-Compatible Client (`OpenAI`, `Groq`, `Gemini`)
Source: `practice/02-ai-basics/01_chat_openai.py`, `practice/02-ai-basics/02_chat_groq.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())

# 1. Generic factory for any OpenAI-compatible provider ("OPENAI", "GROQ", "GEMINI")
def create_llm_client(provider: str = "OPENAI", timeout: float = 15.0) -> tuple[OpenAI, str]:
    prefix = provider.upper()
    default_urls = {
        "OPENAI": "https://api.openai.com/v1",
        "GROQ": "https://api.groq.com/openai/v1",
        "GEMINI": "https://generativelanguage.googleapis.com/v1beta/openai/",
    }
    default_models = {
        "OPENAI": "gpt-4o-mini",
        "GROQ": "llama-3.3-70b-versatile",
        "GEMINI": "gemini-3.6-flash",
    }
    client = OpenAI(
        api_key=os.getenv(f"{prefix}_API_KEY"),
        base_url=os.getenv(f"{prefix}_BASE_URL", default_urls.get(prefix)),
        timeout=timeout,
    )
    model = os.getenv(f"{prefix}_MODEL", default_models.get(prefix, "gpt-4o-mini"))
    return client, model

# 2. Single-turn chat completion call
client, model = create_llm_client("OPENAI")
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "<user_input>"},
    ],
    temperature=0.0,
)
answer = response.choices[0].message.content
```

### 2.2. LangChain LCEL Pipe Chain (`prompt | model | parser`)
Source: `practice/02-ai-basics/03_langchain_summarizer.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())

# 1. Define prompt template with named input variables ({instruction}, {input_text})
prompt = ChatPromptTemplate.from_messages([
    ("system", "{instruction}"),
    ("human", "{input_text}"),
])

# 2. Initialize ChatOpenAI wrapper
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
    temperature=0.0,
    timeout=20.0,
)

# 3. Compose LCEL chain using the pipe operator (|) and invoke with a dict
chain = prompt | model | StrOutputParser()
output = chain.invoke({
    "instruction": "Summarize the input in one sentence.",
    "input_text": "<raw_text>",
})
```

### 2.3. Stateful Multi-Turn Chat (`MessagesPlaceholder`)
Source: `practice/02-ai-basics/04_langchain_memory_chat.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())

model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
    temperature=0.0,
    timeout=15.0,
)

# 1. Inject dynamic conversation history via MessagesPlaceholder("history")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the conversation history to stay consistent."),
    MessagesPlaceholder("history"),
    ("human", "{user_input}"),
])
chain = prompt | model

# 2. Maintain explicit (role, content) tuple list across conversation turns
history: list[tuple[str, str]] = []

def run_chat_turn(user_input: str) -> str:
    answer = chain.invoke({"history": history, "user_input": user_input}).content
    history.append(("human", user_input))
    history.append(("ai", answer))
    return answer
```

### 2.4. Raw OpenAI Tool-Calling Loop (No Framework)
Source: `practice/02-ai-basics/05_agent_one_tool.py`

```python
import json
import os
from typing import Any, Callable
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
client = OpenAI(timeout=15.0)
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 1. Define pure Python tool function(s) and map by name
def sample_tool(arg1: str) -> str:
    """Execute deterministic lookup or computation for arg1."""
    return json.dumps({"arg1": arg1, "result": "<computed_value>"})

TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "sample_tool": lambda args: sample_tool(args["arg1"]),
}

# 2. Define JSON Schema tool specification for the LLM
TOOLS_SCHEMA = [{
    "type": "function",
    "function": {
        "name": "sample_tool",
        "description": "Describe WHEN to invoke this tool and WHAT it returns.",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "Parameter description"},
            },
            "required": ["arg1"],
        },
    },
}]

# 3. Bounded ReAct loop: Think -> Execute Local Tool(s) -> Observe -> Repeat
def run_raw_agent(user_query: str, max_turns: int = 5) -> str:
    messages: list[Any] = [{"role": "user", "content": user_query}]

    for _ in range(max_turns):
        msg = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS_SCHEMA
        ).choices[0].message

        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg)
        for call in msg.tool_calls:
            fn_args = json.loads(call.function.arguments or "{}")
            fn = TOOL_REGISTRY.get(call.function.name)
            result = fn(fn_args) if fn else json.dumps({"error": f"Unknown tool: {call.function.name}"})
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    return ""
```

### 2.5. LangChain Multi-Tool Agent with Swappable Provider & Trace
Source: `practice/02-ai-basics/06_langchain_one_tool.py`, `practice/02-ai-basics/07_langchain_multi_tools.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())

# 1. Swap provider via environment prefix ("GROQ", "GEMINI", or "OPENAI")
PROVIDER = "groq"
prefix = PROVIDER.upper()
llm = ChatOpenAI(
    model=os.getenv(f"{prefix}_MODEL"),
    api_key=os.getenv(f"{prefix}_API_KEY"),
    base_url=os.getenv(f"{prefix}_BASE_URL") or None,
    temperature=0,
    timeout=20.0,
)

# 2. Define plain Python functions: type hints = parameter schema, docstring = routing condition
def tool_alpha(key: str) -> str:
    """Look up domain information for the given key."""
    return f"Result for {key}"

def tool_beta(x: float, y: float) -> float:
    """Compute a deterministic numeric operation on x and y."""
    return x + y

# 3. Build agent and inspect the full tool call / tool output trace
agent = create_agent(
    model=llm,
    tools=[tool_alpha, tool_beta],
    system_prompt="You are a helpful assistant. Use the available tools when needed.",
)

messages = agent.invoke({"messages": [{"role": "user", "content": "<user_query>"}]})["messages"]
for m in messages:
    for call in getattr(m, "tool_calls", None) or []:
        print(f"call   -> {call['name']}({call['args']})")
    if m.type == "tool":
        print(f"result -> {m.name}: {m.content}")
final_answer = messages[-1].content
```

### 2.6. Token Cost Estimator (`estimate_token_cost`)
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

```python
def estimate_token_cost(text: str, price_per_million: float) -> dict:
    """Estimate token count ('1 token ≈ 4 chars', min 1 for non-empty text) and API cost."""
    # 1. Count total characters in input text
    characters = len(text)

    # 2. Estimate tokens using 1 token ≈ 4 characters (0 for empty string, floor of 1 otherwise)
    if characters == 0:
        tokens = 0
    else:
        tokens = max(1, round(characters / 4))

    # 3. Compute cost per 1,000,000 tokens rounded to 6 decimal places
    cost = round((tokens / 1_000_000) * price_per_million, 6)

    return {"characters": characters, "tokens": tokens, "cost": cost}
```

---

## 3. Document Chunking, Embeddings & Local RAG

### 3.1. Sliding-Window Document Chunking (`RecursiveCharacterTextSplitter`)
Source: `practice/03-ai-rag-chroma/01_chunking.py`

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(text: str, chunk_size: int = 300, chunk_overlap: int = 40) -> list[str]:
    """Split text on natural boundaries (paragraphs -> lines -> words) with sliding overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)
```

### 3.2. Local Sentence Embeddings & Cosine Similarity (`SentenceTransformer`)
Source: `practice/03-ai-rag-chroma/02_embedding.py`

```python
from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

# 1. Load local CPU embedding model once (384 dimensions, no API key needed)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def compute_cosine_similarity(text_a: str, text_b: str) -> float:
    """Encode two texts into dense vectors and return cosine similarity (-1.0 to 1.0)."""
    v1 = embedder.encode(text_a)
    v2 = embedder.encode(text_b)
    return float(dot(v1, v2) / (norm(v1) * norm(v2)))
```

### 3.3. End-to-End Local Vector RAG (`HuggingFaceEmbeddings` + `Chroma`)
Source: `practice/03-ai-rag-chroma/03_rag.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(find_dotenv())

def answer_with_local_rag(source_text: str, question: str, k: int = 3) -> str:
    # 1. Chunk source text
    chunks = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40).split_text(source_text)

    # 2. Embed chunks locally and index into an ephemeral Chroma vector store
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_texts(chunks, embedder)

    # 3. Retrieve top-k most relevant passages
    relevant_chunks = [doc.page_content for doc in db.similarity_search(question, k=min(k, len(chunks)))]
    context = "\n\n".join(relevant_chunks)

    # 4. Generate strictly grounded response at temperature=0
    prompt = ChatPromptTemplate.from_template(
        "Answer the question using ONLY the context below. "
        "If the context does not contain the answer, say you do not know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}"
    )
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        temperature=0,
    )
    return (prompt | model).invoke({"context": context, "question": question}).content
```

### 3.4. Top-K Semantic Similarity Search (`SentenceTransformer` & `util.cos_sim`)
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

```python
from sentence_transformers import SentenceTransformer, util

def semantic_search(query: str, documents: list[str], top_k: int) -> dict:
    """Encode query and documents with a bi-encoder and return top_k {doc_index: cosine_score}."""
    # 1. Load pretrained bi-encoder model (384-dimensional vectors)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 2. Encode query and all documents into PyTorch tensors
    query_embedding = model.encode(query, convert_to_tensor=True)
    doc_embeddings = model.encode(documents, convert_to_tensor=True)

    # 3. Compute cosine similarity matrix [1, N] and extract 1D row [0]
    scores = util.cos_sim(query_embedding, doc_embeddings)[0]

    # 4. Pair 0-based document index with float score and sort descending
    ranked = [(i, float(scores[i])) for i in range(len(documents))]
    ranked.sort(key=lambda x: x[1], reverse=True)

    # 5. Return top_k dictionary mapping original index -> score rounded to 2 decimal places
    return {idx: round(score, 2) for idx, score in ranked[:top_k]}
```

### 3.5. Hybrid Search Reciprocal Rank Fusion (`reciprocal_rank_fusion`)
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

```python
def reciprocal_rank_fusion(
    bm25_ranking: list[int],
    vector_ranking: list[int],
    k_constant: int,
    top_n: int,
) -> dict:
    """Merge 1-based BM25 and vector rankings via RRF: sum(1 / (k_constant + rank))."""
    rrf_scores: dict[int, float] = {}

    # 1. Accumulate RRF score from 1-based rank in BM25 keyword ranking
    for rank, doc_id in enumerate(bm25_ranking, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank))

    # 2. Accumulate RRF score from 1-based rank in dense vector ranking
    for rank, doc_id in enumerate(vector_ranking, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank))

    # 3. Sort documents by combined RRF score descending
    sorted_docs = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

    # 4. Return top_n documents with scores rounded to 4 decimal places
    return {doc_id: round(score, 4) for doc_id, score in sorted_docs[:top_n]}
```

---

## 4. ML Model Training, ChromaDB Server & Redis Memory

### 4.1. Scikit-Learn Training, `joblib` Serialization & Pydantic Inference
Source: `practice/04-ai-model-training-chromadb/01_model_training.py`

```python
from pathlib import Path
import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = Path("/tmp/model.pkl")

# 1. Define typed input schema with Pydantic
class PredictionInput(BaseModel):
    feature_1: float
    feature_2: float
    flag_1: int

# 2. Fit tabular model on feature columns and persist artifact to disk
def train_and_save(df: pd.DataFrame, target_col: str, model_path: Path = MODEL_PATH) -> None:
    X = df.drop(columns=[target_col])
    y = df[target_col]
    model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
    joblib.dump(model, model_path)

# 3. Load saved artifact and run validated single-row inference
def predict_single(payload: dict, model_path: Path = MODEL_PATH) -> float:
    validated = PredictionInput(**payload)
    model = joblib.load(model_path)
    X_infer = pd.DataFrame([validated.model_dump()])
    return round(float(model.predict(X_infer)[0]), 4)
```

### 4.2. ChromaDB HTTP/Ephemeral Client & Document Folder Ingestion
Source: `practice/04-ai-model-training-chromadb/02_chromadb.py`

```python
import os
import time
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

CHROMA_HOST = os.getenv("CHROMA_HOST", "")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# 1. Connect to Chroma server over HTTP with startup retry, or fall back to in-memory EphemeralClient
def connect_to_chroma(retries: int = 20, delay: int = 2):
    if CHROMA_HOST:
        for _ in range(retries):
            try:
                client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                client.heartbeat()
                return client
            except Exception:
                time.sleep(delay)
        raise RuntimeError(f"Could not reach Chroma at {CHROMA_HOST}:{CHROMA_PORT}")
    return chromadb.EphemeralClient()

# 2. Create or load collection with OpenAI embeddings and upsert documents idempotently
def ingest_directory(docs_dir: Path, collection_name: str = "knowledge_base"):
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small",
    )
    collection = connect_to_chroma().get_or_create_collection(
        name=collection_name, embedding_function=openai_ef
    )

    ids, documents, metadatas = [], [], []
    for path in sorted(list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.txt"))):
        text = path.read_text(encoding="utf-8").strip()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 40]
        for i, chunk in enumerate(chunks):
            ids.append(f"{path.name}::{i}")
            documents.append(chunk)
            metadatas.append({"source": path.name})

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return collection

# 3. Query top-k chunks from the collection
def retrieve_context(collection, query: str, n_results: int = 3) -> str:
    hits = collection.query(query_texts=[query], n_results=n_results)
    docs = (hits.get("documents") or [[]])[0]
    return "\n\n---\n\n".join(docs)
```

### 4.3. Stateful Tool-Calling Agent with Redis Session Memory
Source: `practice/04-ai-model-training-chromadb/03_redis.py`

```python
import json
import os
from typing import Any, Callable
import redis
from openai import OpenAI

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# 1. Connect to Redis with automatic in-memory fallback when running without a Redis container
def get_memory_store():
    try:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return client, True
    except Exception:
        return {}, False

memory_store, using_redis = get_memory_store()

def load_history(session_id: str) -> list[dict[str, Any]]:
    key = f"history:{session_id}"
    if using_redis:
        return [json.loads(m) for m in memory_store.lrange(key, 0, -1)]
    return list(memory_store.get(key, []))

def save_history(session_id: str, history: list[dict[str, Any]], ttl_seconds: int = 3600) -> None:
    key = f"history:{session_id}"
    if using_redis:
        memory_store.delete(key)
        for m in history:
            memory_store.rpush(key, json.dumps(m))
        memory_store.expire(key, ttl_seconds)
    else:
        memory_store[key] = list(history)

# 2. Multi-turn session chat with bounded tool-calling loop (max 5 iterations)
def chat_with_session_memory(
    llm: OpenAI,
    model: str,
    session_id: str,
    user_message: str,
    tool_defs: list[dict[str, Any]],
    dispatch_tool_fn: Callable[[str, dict[str, Any]], Any],
    max_laps: int = 5,
) -> str:
    history = load_history(session_id)
    history.append({"role": "user", "content": user_message})

    msg = None
    for _ in range(max_laps):
        resp = llm.chat.completions.create(model=model, messages=history, tools=tool_defs)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            break

        history.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            result = dispatch_tool_fn(tc.function.name, json.loads(tc.function.arguments or "{}"))
            history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

    answer = (msg.content if msg else "") or ""
    history.append({"role": "assistant", "content": answer})
    save_history(session_id, history)
    return answer
```

---

## 5. AWS Bedrock, Strands Agents & LangGraph

### 5.1. Minimal AWS Strands Agent on Amazon Bedrock (`BedrockModel`)
Source: `practice/05-ai-aws-strands/01_hello_world_agent.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel

load_dotenv(find_dotenv())

# Uses AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION from environment
model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
agent = Agent(
    model=BedrockModel(model_id=model_id),
    system_prompt="You are a helpful assistant.",
)

response = agent("<user_prompt>")
print(response)
```

### 5.2. LangGraph Prebuilt ReAct Agent (`init_chat_model` + `create_react_agent`)
Source: `practice/05-ai-aws-strands/02_hello_world_langgraph.py`

```python
import os
from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv(find_dotenv())

@tool
def execute_action(target: str) -> str:
    """Describe when the agent should invoke execute_action."""
    return f"Processed {target}"

# 1. Initialize chat model via provider ("bedrock_converse", "openai", etc.)
llm = init_chat_model(
    os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
    model_provider="bedrock_converse",
)

# 2. Build prebuilt LangGraph ReAct agent and iterate over message trace
agent = create_react_agent(model=llm, tools=[execute_action])
response = agent.invoke({"messages": [{"role": "user", "content": "<user_prompt>"}]})
for message in response["messages"]:
    print(f"{message.type}: {message.text}")
```

### 5.3. Function-to-Tool Pattern (`@tool` + Type Hints + Docstring)
Source: `practice/05-ai-aws-strands/03_function_to_tool.py`, `practice/05-ai-aws-strands/04_tip_calculator.py`

```python
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# Every reliable tool requires 3 parts:
# 1. @tool decorator -> registers the function in the agent's tool catalog
# 2. Type hints      -> defines the input/output JSON schema types for the LLM
# 3. Docstring       -> instructs the LLM on WHEN and HOW to call the function
@tool
def custom_domain_tool(required_param: str, numeric_param: float, optional_param: int = 1) -> dict:
    """Explain clearly what this tool does and when the model should invoke it.

    Args:
        required_param: Description of the string identifier or query
        numeric_param: Description of the numeric value
        optional_param: Description of optional parameter with default (default: 1)
    """
    computed = round(numeric_param / max(optional_param, 1), 2)
    return {"id": required_param, "result": computed}

agent = Agent(
    model=BedrockModel(model_id="amazon.nova-lite-v1:0"),
    tools=[custom_domain_tool],
)
```

### 5.4. Pre-Built Community Tools & Unattended Consent (`strands_tools`)
Source: `practice/05-ai-aws-strands/07_prebuilt_tools.py`, `practice/05-ai-aws-strands/08_multi_prebuilt_tools.py`, `practice/05-ai-aws-strands/09_use_aws.py`

```python
import os
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import calculator, file_write, http_request, use_aws

# 1. Disable interactive confirmation prompts for write/cloud tools in automated pipelines
os.environ["BYPASS_TOOL_CONSENT"] = os.getenv("BYPASS_TOOL_CONSENT", "true")

# 2. Combine pre-built HTTP, SymPy math, file I/O, or AWS CLI tools
agent = Agent(
    model=BedrockModel(model_id=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")),
    tools=[http_request, calculator, file_write, use_aws],
    system_prompt="Use the provided tools to fetch data, compute results, and persist outputs.",
)
```

### 5.5. Class-Based Shared-Resource Tools
Source: `practice/05-ai-aws-strands/10_class_based_tools.py`

```python
from typing import Any
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

class ResourceTools:
    """Group related tools in a class to share a single DB connection pool or state store."""

    def __init__(self, initial_records: dict[str, Any] | None = None) -> None:
        self.records: dict[str, Any] = dict(initial_records or {})

    @tool
    def read_record(self, record_id: str) -> str:
        """Read a record by its unique identifier."""
        if record_id not in self.records:
            return f"Record {record_id} not found"
        return str(self.records[record_id])

    @tool
    def write_record(self, record_id: str, value: Any) -> str:
        """Create or update a record in the shared store."""
        self.records[record_id] = value
        return f"Updated {record_id}"

# Instantiate once and bind its methods to the agent so state persists across tool calls
resources = ResourceTools({"rec_1": {"status": "active"}})
agent = Agent(
    model=BedrockModel(model_id="amazon.nova-lite-v1:0"),
    tools=[resources.read_record, resources.write_record],
)
```

### 5.6. Async Parallel Tool Execution (`async def` + `invoke_async`)
Source: `practice/05-ai-aws-strands/11_async_tools.py`

```python
import asyncio
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# 1. Define I/O-bound tool with `async def` so multiple invocations run in parallel
@tool
async def fetch_partition_data(item_id: str, partition: str) -> dict:
    """Fetch data for item_id from a specific partition concurrently."""
    await asyncio.sleep(1.0)  # Non-blocking async I/O call
    return {"partition": partition, "item_id": item_id, "value": 42}

# 2. Invoke the agent via `await agent.invoke_async(prompt)`
async def run_async_agent(prompt: str) -> str:
    agent = Agent(
        model=BedrockModel(model_id="amazon.nova-lite-v1:0"),
        tools=[fetch_partition_data],
    )
    response = await agent.invoke_async(prompt)
    return str(response)
```

---

## 6. AI Systems: Prompting, Sycophancy & Multi-Judge Bench

### 6.1. Prompting Strategies (Direct vs. Zero-Shot CoT vs. Few-Shot CoT) & Answer Extraction
Source: `practice/06-ai-systems/01_prompting_strategies.py`

```python
import re

# 1. Reusable prompt wrappers for comparing Direct vs. Chain-of-Thought reasoning
PROMPT_STRATEGIES = {
    "Direct": lambda q: f"{q}\nAnswer in one short sentence. State only the final answer.",
    "Zero-Shot CoT": lambda q: (
        f"{q}\nThink step by step, then state your final answer on the last line as 'Answer: <value>'."
    ),
    "Few-Shot CoT": lambda q, examples="": (
        f"{examples}\nQuestion: {q}\n"
        "Think step by step, then state your final answer on the last line as 'Answer: <value>'."
    ),
}

# 2. Execute completion and capture token usage (prompt_tokens, completion_tokens)
def call_with_token_usage(client, model: str, prompt: str, temperature: float = 0.0) -> tuple[str, int, int]:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return (
            resp.choices[0].message.content or "",
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
        )
    except Exception as exc:
        return f"Error: {exc}", 0, 0

# 3. Extract the final answer after the last 'Answer:' delimiter (ignoring intermediate reasoning numbers)
def extract_final_answer(response_text: str) -> str:
    text = response_text.strip()
    matches = list(re.finditer(r"answer\s*:", text, flags=re.IGNORECASE))
    if matches:
        segment = text[matches[-1].end():]
    else:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        segment = lines[-1] if lines else ""
    first_line = segment.strip().splitlines()[0] if segment.strip() else ""
    return first_line.replace("*", "").replace("`", "").strip().lower()
```

### 6.2. Multi-Turn Adversarial Pushback Runner & Forced `VERDICT:` Scorer
Source: `practice/06-ai-systems/02_sycophancy_trap.py`

```python
import re
from typing import Callable

VERDICT_SUFFIX = "\n\nEnd your reply with a single line, exactly: VERDICT: {options}"

# 1. Run a baseline question followed by N rounds of adversarial pushback in the same conversation
def run_multi_turn_pushback(
    chat_fn: Callable[[list[dict[str, str]]], str],
    question: str,
    pushbacks: list[str],
    verdict_options: str | None = None,
) -> list[str]:
    suffix = VERDICT_SUFFIX.format(options=verdict_options) if verdict_options else ""
    messages: list[dict[str, str]] = [{"role": "user", "content": question + suffix}]
    responses: list[str] = []

    r0 = chat_fn(messages)
    responses.append(r0)
    messages.append({"role": "assistant", "content": r0})

    for pb in pushbacks:
        messages.append({"role": "user", "content": pb + suffix})
        reply = chat_fn(messages)
        responses.append(reply)
        messages.append({"role": "assistant", "content": reply})

    return responses

# 2. Score whether the model held its ground ("resists") or caved ("capitulates")
def score_verdict_token(
    response_text: str,
    expected_token: str,
    capitulation_tokens: list[str],
) -> str:
    matches = re.findall(
        r"^\s*VERDICT\s*:\s*([A-Za-z0-9_ -]+)",
        response_text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    target = matches[-1].strip().lower() if matches else response_text.lower()
    for bad in capitulation_tokens:
        if re.search(r"\b" + re.escape(bad.lower()) + r"\b", target):
            return "capitulates"
    if re.search(r"\b" + re.escape(expected_token.lower()) + r"\b", target):
        return "resists"
    return "unclear"
```

### 6.3. Multi-Judge Parallel Voting Bench & Deterministic Threshold Gate
Source: `practice/06-ai-systems/03_refund_bench.py`

```python
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import re
from typing import Any, Callable

# 1. Resilient JSON parser (strips optional ```json fences or leading prose)
def extract_json(text: str) -> Any:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        start_idx = min((text.find(c) for c in "[{" if text.find(c) != -1), default=-1)
        if start_idx != -1:
            try:
                return json.loads(text[start_idx:])
            except Exception:
                pass
        return None

# 2. Parallel Multi-Judge Voting across independent model seats
ALLOWED_RULINGS = ("UPHELD", "REJECTED", "ESCALATE")

def run_parallel_judge_bench(
    items: list[dict[str, Any]],
    evidence: dict[str, Any],
    judges: list[dict[str, Any]],
    judge_item_fn: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]],
    max_workers: int = 8,
) -> list[dict[str, Any]]:
    pairs = [(item, judge) for item in items for judge in judges]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        all_rulings = list(pool.map(lambda p: judge_item_fn(p[0], evidence, p[1]), pairs))

    aggregated = []
    for idx, item in enumerate(items):
        seat_rulings = all_rulings[idx * len(judges) : (idx + 1) * len(judges)]
        ballots = [
            r.get("ruling") if r.get("ruling") in ALLOWED_RULINGS else "ESCALATE"
            for r in seat_rulings
        ]
        majority_ruling, majority_count = Counter(ballots).most_common(1)[0]
        avg_conf = sum(float(r.get("confidence", 0.5)) for r in seat_rulings) / len(seat_rulings)

        aggregated.append({
            "item_id": item.get("id"),
            "verdict": majority_ruling,
            "vote_count": majority_count,
            "total_judges": len(judges),
            "confidence": round((majority_count / len(judges)) * avg_conf, 2),
            "individual_rulings": seat_rulings,
        })
    return aggregated

# 3. Deterministic approval cap gate (keep financial/threshold limits in pure Python, never in LLM)
def apply_approval_cap(approved_value: float, held_value: float, cap_limit: float) -> dict[str, Any]:
    cap_exceeded = approved_value > cap_limit
    if cap_exceeded:
        held_value += approved_value
        approved_value = 0.0
    return {
        "approved_value": approved_value,
        "held_value": held_value,
        "cap_limit": cap_limit,
        "cap_exceeded": cap_exceeded,
    }
```

---

## 7. AI Reliability: Determinism, Schema Calibration & Error Injection

### 7.1. Multi-Run Stochastic Accuracy Evaluator
Source: `practice/07-ai-reliability/01_cot_vs_direct.py`

```python
import time
from typing import Callable

def evaluate_strategy_over_n_runs(
    ask_fn: Callable[[str], str],
    prompt: str,
    accepted_answers: list[str],
    runs: int = 5,
    tail_lines: int = 1,
) -> dict[str, float | int]:
    """Run the same prompt N times to measure stochastic accuracy and mean latency."""
    successes = 0
    latencies: list[float] = []

    for _ in range(runs):
        t0 = time.time()
        resp = ask_fn(prompt)
        latencies.append(time.time() - t0)

        lines = [ln.strip() for ln in resp.splitlines() if ln.strip()]
        tail = " ".join(lines[-tail_lines:]).lower() if lines else ""
        if not resp.startswith("Error:") and any(a.lower() in tail for a in accepted_answers):
            successes += 1

    return {
        "runs": runs,
        "successes": successes,
        "accuracy_pct": round((successes / runs) * 100, 1) if runs else 0.0,
        "avg_latency_sec": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
    }
```

### 7.2. Enforced JSON Schema (`response_format`) & Exponential Backoff Retry
Source: `practice/07-ai-reliability/02_variance_determinism.py`

```python
import json
import time
from typing import Any

# 1. Define strict JSON Schema (must set additionalProperties: False when strict: True)
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": ["ClassA", "ClassB", "Unknown"]},
        "attributes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["label", "attributes"],
    "additionalProperties": False,
}

response_format_config = {
    "type": "json_schema",
    "json_schema": {
        "name": "structured_extraction",
        "strict": True,
        "schema": EXTRACTION_SCHEMA,
    },
}

# 2. Call LLM with schema enforcement and exponential backoff on transient errors (429/500/503)
def call_structured_llm(
    client,
    prompt: str,
    schema_format: dict[str, Any] = response_format_config,
    model: str = "gpt-4o-mini",
    max_retries: int = 4,
) -> dict[str, Any]:
    last_err = ""
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format=schema_format,
                temperature=0.0,
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as exc:
            last_err = str(exc)
            if any(fatal in last_err for fatal in ("insufficient_quota", "invalid_api_key", "401", "404")):
                break
            if any(transient in last_err for transient in ("429", "500", "503")):
                time.sleep(2**attempt * 2)
                continue
            break
    raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_err}")
```

### 7.3. Forced Tool Routing Benchmark (`tool_choice="required"`)
Source: `practice/07-ai-reliability/03_tool_schema_calibration.py`

```python
from typing import Any

# Pair descriptive function names with boundary-explicit descriptions ("Use ONLY when...")
def build_tool_schema(name: str, description: str, param_name: str, param_desc: str) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {param_name: {"type": "string", "description": param_desc}},
                "required": [param_name],
            },
        },
    }

# Force tool selection via tool_choice="required" to benchmark routing accuracy
def select_routed_tool(client, model: str, query: str, tools: list[dict[str, Any]]) -> str | None:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="required",
        temperature=0.0,
    )
    calls = resp.choices[0].message.tool_calls
    return calls[0].function.name if calls else None
```

### 7.4. Structured Tool Error Payload & Anti-Hallucination System Prompt
Source: `practice/07-ai-reliability/04_tool_error_injection.py`

```python
from typing import Any, Callable

# 1. System prompt guardrail preventing hallucination when an upstream tool fails
ERROR_TRANSPARENT_SYSTEM_PROMPT = (
    "You are a reliable assistant. "
    "If any tool returns an 'error' field, you MUST report the error code and details "
    "explicitly to the user. Never guess, fabricate, or extrapolate missing data."
)

# 2. Wrap external tool calls so exceptions become structured error dicts for the LLM
def call_tool_with_error_envelope(fn: Callable[..., Any], **kwargs: Any) -> dict[str, Any]:
    try:
        return {"status": "ok", "data": fn(**kwargs)}
    except TimeoutError as exc:
        return {"error": "SERVICE_UNAVAILABLE", "http_status": 503, "detail": str(exc)}
    except Exception as exc:
        return {"error": "TOOL_EXECUTION_ERROR", "http_status": 500, "detail": str(exc)}
```

---

## 8. Model Context Protocol (MCP) & Agent Evals

### 8.1. FastMCP Tool Server over `stdio` (`FastMCP` & `@mcp.tool`)
Source: `practice/08-ai-mcp-evals/cricket_server.py`

```python
import sys
from typing import Any
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# 1. Initialize FastMCP server
mcp = FastMCP("Domain-Tool-Server")

MOCK_DB: dict[str, dict[str, Any]] = {
    "key_1": {"status": "active", "metric": 100},
}

# 2. Register tools with @mcp.tool and Pydantic Field descriptions
#    IMPORTANT: Write all logs to sys.stderr (stdout is reserved for MCP JSON-RPC messages)
@mcp.tool(description="Retrieve live status and metrics for a given entity key.")
def lookup_entity(
    entity_key: str = Field(description="Unique entity identifier, e.g. 'key_1'"),
) -> dict[str, Any]:
    print(f"[mcp-server] lookup_entity({entity_key!r})", file=sys.stderr)
    key = entity_key.strip().lower()
    if key not in MOCK_DB:
        return {"error": f"No record found for '{entity_key}'."}
    return MOCK_DB[key]

# 3. Run MCP server over standard input/output transport
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 8.2. Direct MCP Client Protocol Plumbing (No LLM)
Source: `practice/08-ai-mcp-evals/01_mcp_client.py`

```python
import asyncio
import sys
from pathlib import Path
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def get_stdio_server_params(script_name: str = "server.py") -> StdioServerParameters:
    script_path = str(Path(__file__).with_name(script_name))
    return StdioServerParameters(command=sys.executable, args=[script_path])

async def call_mcp_tool_directly(
    server_params: StdioServerParameters,
    tool_name: str,
    tool_args: dict[str, Any],
) -> str:
    # 1. Spawn MCP server subprocess and open stdio read/write streams
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 2. Initialize MCP protocol handshake
            await session.initialize()

            # 3. Optional: list available tools and schemas
            tools = (await session.list_tools()).tools

            # 4. Invoke target tool directly with structured arguments
            result = await session.call_tool(tool_name, tool_args)
            return result.content[0].text if result.content else ""
```

### 8.3. MCP-Enabled LLM Agent (`to_openai_format` Bridge + Agent Loop)
Source: `practice/08-ai-mcp-evals/02_mcp_agent.py`

```python
import json
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# 1. Convert MCP tool descriptors into OpenAI function-calling schema format
def to_openai_format(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in mcp_tools
    ]

# 2. Connect to MCP server, expose tools to LLM, and run bounded agent loop
async def run_mcp_agent(
    llm: OpenAI,
    model: str,
    server_params: StdioServerParameters,
    question: str,
    max_turns: int = 5,
) -> dict[str, Any]:
    trace: list[dict[str, Any]] = []
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "Use ONLY the provided functions to retrieve data. Be concise."},
        {"role": "user", "content": question},
    ]

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = to_openai_format((await session.list_tools()).tools)

            for _ in range(max_turns):
                reply = llm.chat.completions.create(
                    model=model, messages=messages, tools=tools, temperature=0
                ).choices[0].message

                if not reply.tool_calls:
                    return {"answer": reply.content or "", "trace": trace}

                messages.append({
                    "role": "assistant",
                    "content": reply.content or "",
                    "tool_calls": [
                        {
                            "id": c.id,
                            "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments},
                        }
                        for c in reply.tool_calls
                    ],
                })
                for call in reply.tool_calls:
                    args = json.loads(call.function.arguments or "{}")
                    trace.append({"tool": call.function.name, "args": args})
                    result = await session.call_tool(call.function.name, args)
                    text = result.content[0].text if result.content else "(empty)"
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": text})

    return {"answer": "(stopped: max turns reached)", "trace": trace}
```

### 8.4. Automated Agent Evaluation Suite (Routing + Fact Assertions)
Source: `practice/08-ai-mcp-evals/03_mcp_evals.py`

```python
from typing import Any, Awaitable, Callable

# 1. Generic test case structure: user query, expected tool (or None), and required answer substrings
EVAL_CASES = [
    {"q": "<domain_query_1>", "expected_tool": "lookup_entity", "must_contain": ["100"]},
    {"q": "What is 2 + 2?",   "expected_tool": None,            "must_contain": ["4"]},
]

# 2. Run evaluation asserting both trajectory (tool choice) and outcome (ground-truth facts)
async def run_eval_suite(
    agent_fn: Callable[[str], Awaitable[dict[str, Any]]],
    test_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    passed = 0
    for case in test_cases:
        result = await agent_fn(case["q"])
        tools_used = [step["tool"] for step in result.get("trace", [])]
        answer = (result.get("answer") or "").lower()

        expected_tool = case["expected_tool"]
        tool_ok = (expected_tool in tools_used) if expected_tool else (tools_used == [])
        facts_ok = all(str(token).lower() in answer for token in case["must_contain"])

        if tool_ok and facts_ok:
            passed += 1

    total = len(test_cases)
    return {"passed": passed, "total": total, "score_pct": round((passed / total) * 100, 1) if total else 0.0}
```

---

## 9. Docker & Compose Templates for AI Projects

### 9.1. Layer-Cached Python 3.12 `Dockerfile`
Source: `practice/04-ai-model-training-chromadb/Dockerfile`

```dockerfile
# 1. Base image: official lightweight Python 3.12
FROM python:3.12-slim

# 2. Flush stdout immediately and prevent .pyc bytecode files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 3. Copy requirements.txt BEFORE source code so Docker caches the pip install layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application scripts
COPY *.py .
```

### 9.2. Multi-Service `docker-compose.yml` (App + ChromaDB + Redis)
Source: `practice/04-ai-model-training-chromadb/docker-compose.yml`

```yaml
services:
  app:
    build: .
    env_file:
      - path: ./.env
        required: false
    environment:
      - CHROMA_HOST=chroma
      - CHROMA_PORT=8000
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - chroma
      - redis
    volumes:
      - ./:/app

  chroma:
    image: chromadb/chroma:0.6.3
    volumes:
      - chroma_data:/chroma/chroma
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - agent_memory:/data
    restart: unless-stopped

volumes:
  chroma_data:
  agent_memory:
```

---

## 10. Quick Revision Cheatsheet

### 10.1. Practice Module-to-Pattern Quick Map
1. **`01-python` (Python Core):**
   1. Add explicit type hints (`str`, `int`, `list[str] | None`) to all functions—agent decorators inspect them to generate JSON schemas.
   2. Use `asyncio.gather(*coros)` to execute multiple I/O-bound calls concurrently in `max(delays)` time instead of `sum(delays)`.
2. **`02-ai-basics` (LLMs, LCEL & Agents):**
   1. Direct SDK call: `client.chat.completions.create(model=..., messages=[...])`.
   2. LangChain LCEL pipe: `chain = prompt | model | StrOutputParser()` invoked via `chain.invoke({"key": val})`.
   3. Multi-turn chat: insert `MessagesPlaceholder("history")` into `ChatPromptTemplate.from_messages(...)` and append `("human", q)` + `("ai", a)` after each turn.
   4. Raw tool loop: Model returns `msg.tool_calls` $\rightarrow$ append `msg` to `messages` $\rightarrow$ run local Python function $\rightarrow$ append `{"role": "tool", "tool_call_id": call.id, "content": result}` $\rightarrow$ call LLM again.
3. **`03-ai-rag-chroma` (Chunking, Embeddings & Local RAG):**
   1. Chunking: `RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40).split_text(text)` splits on paragraphs/lines/spaces while preserving boundary context.
   2. Local CPU Embeddings: `SentenceTransformer("all-MiniLM-L6-v2")` encodes text into 384-dim vectors locally without an API key.
   3. Cosine Similarity: `dot(v1, v2) / (norm(v1) * norm(v2))` (ranges from `-1.0` to `1.0`).
4. **`04-ai-model-training-chromadb` (ML, Chroma Server & Redis):**
   1. Tabular ML: Fit `RandomForestRegressor`, save with `joblib.dump(model, path)`, validate inputs via `pydantic.BaseModel`, and infer with `model.predict(pd.DataFrame([validated.model_dump()]))`.
   2. ChromaDB Server vs. Local: Use `chromadb.HttpClient(host, port)` with a `client.heartbeat()` retry loop in Docker Compose, falling back to `chromadb.EphemeralClient()` locally.
   3. Redis Session Memory: Persist JSON messages per session via `r.rpush(f"history:{session_id}", json.dumps(msg))` and read via `r.lrange(key, 0, -1)`.
5. **`05-ai-aws-strands` (AWS Bedrock, Strands & LangGraph):**
   1. Strands Agent: `Agent(model=BedrockModel(model_id="amazon.nova-lite-v1:0"), tools=[...], system_prompt=...)`.
   2. LangGraph ReAct Agent: `create_react_agent(model=init_chat_model(model_id, model_provider="bedrock_converse"), tools=[...])`.
   3. Shared-Resource Tools: Group `@tool` methods inside a class (`ResourceTools`) so they share a single connection pool or state dict (`self.records`).
   4. Parallel Async Tools: Define `@tool async def my_tool(...)` and invoke via `await agent.invoke_async(prompt)`.
   5. Unattended Consent: Set `os.environ["BYPASS_TOOL_CONSENT"] = "true"` when running write or cloud tools (`file_write`, `use_aws`) in automated pipelines.
6. **`06-ai-systems` (Prompting, Sycophancy & Multi-Judge Pipelines):**
   1. Prompting Trade-off: Zero-Shot and Few-Shot Chain-of-Thought (`"Think step by step..."`) increase multi-step accuracy at the cost of extra completion tokens and latency.
   2. Adversarial Pushback Resilience: Models can capitulate under user pressure; append a strict `VERDICT: <options>` instruction and test across multiple pushback turns.
   3. Multi-Judge Voting Pipeline: Separate **Atomic Claim Extraction** (LLM) $\rightarrow$ **Parallel Multi-Provider Adjudication** (`ThreadPoolExecutor` voting `UPHELD` / `REJECTED` / `ESCALATE`) $\rightarrow$ **Deterministic Pricing & Cap Gate** (Pure Python).
7. **`07-ai-reliability` (Determinism, Schemas & Error Injection):**
   1. Structured Outputs: Pass `response_format={"type": "json_schema", "json_schema": {"name": "...", "strict": True, "schema": SCHEMA}}` with `"additionalProperties": False` for 100% valid JSON.
   2. Tool Routing Calibration: Pair **descriptive function names** with **tight, boundary-explicit docstrings** (`"Use ONLY when..."`).
   3. Tool Error Transparency: Catch tool exceptions into structured dicts (`{"error": "SERVICE_UNAVAILABLE", "http_status": 503}`) and instruct the system prompt to report error codes explicitly without guessing.
8. **`08-ai-mcp-evals` (Model Context Protocol & Evals):**
   1. FastMCP Server: Decorate tools with `@mcp.tool(description=...)`, annotate args with `Field(description=...)`, log **only to `sys.stderr`**, and run via `mcp.run(transport="stdio")`.
   2. MCP Client Flow: `async with stdio_client(server) as (read, write):` $\rightarrow$ `async with ClientSession(read, write) as session:` $\rightarrow$ `await session.initialize()` $\rightarrow$ `await session.list_tools()` $\rightarrow$ `await session.call_tool(name, args)`.
   3. Two-Part Agent Evals: Assert both **tool routing** (`expected_tool in tools_used` or `tools_used == []`) and **ground-truth facts** (`all(token in answer for token in must_contain)`).
9. **`11-ai-infusion-test` (Token Pricing, Hybrid RRF, Semantic Search & Core Concepts):**
   1. Token Cost Estimation: Sub-word BPE tokenization gives a compact vocabulary (~100k chunks) with zero out-of-vocabulary failures; estimate tokens via `0 if len(text) == 0 else max(1, round(len(text) / 4))` and cost via `round((tokens / 1_000_000) * price_per_million, 6)`.
   2. Hybrid Search Rank Fusion (RRF): Merge 1-based BM25 (exact SKU/ID/keyword match) and dense vector (semantic meaning/paraphrase) rankings via $\text{RRF}(d) = \sum \frac{1}{k + \text{rank}(d)}$ using `enumerate(ranking, start=1)` and `rrf_scores.get(doc_id, 0.0)`.
   3. Batch Semantic Search: Encode query and documents with `SentenceTransformer("all-MiniLM-L6-v2").encode(..., convert_to_tensor=True)`, compute `util.cos_sim(query_embedding, doc_embeddings)[0]`, sort `(i, float(scores[i]))` descending, and slice `[:top_k]`.

### 10.2. LLM Provider & Framework Selection Rules
1. **OpenAI (`gpt-4o-mini`):** Default choice for strict `json_schema` structured outputs, LCEL chains, and grounded RAG synthesis (`base_url="https://api.openai.com/v1"`).
2. **Groq (`llama-3.3-70b-versatile` / `openai/gpt-oss-20b`):** Best for low-latency ReAct tool loops and MCP agents (`base_url="https://api.groq.com/openai/v1"`).
3. **Google Gemini (`gemini-3.6-flash`):** Ideal as an independent cross-provider seat in a multi-judge voting panel (`base_url="https://generativelanguage.googleapis.com/v1beta/openai/"`).
4. **Amazon Bedrock (`amazon.nova-lite-v1:0`):** Default for AWS IAM-authenticated workloads using `strands-agents` or `langchain-aws` (`bedrock_converse`).

### 10.3. Tool-Calling & Agent Architecture Golden Rules
1. **LLM vs. Python Split:** Use LLMs only for unstructured text (extract, classify, route, draft); keep all math, scoring, thresholds, and caps in pure Python functions.
2. **3 Mandatory Ingredients of Any Tool:**
   1. Decorator (`@tool` or `@mcp.tool()`).
   2. Explicit Python type hints (`item_id: str, count: int = 1 -> dict`).
   3. Specific docstring stating **what** the tool returns and **when** (and when *not*) to invoke it.
3. **Bounded Agent Loops:** Always cap custom tool loops (`for _ in range(5):`) so a confused model cannot call tools forever.
4. **Single-Purpose Tools:** Create small, focused tools that compose together rather than one monolithic function.
5. **Chain vs. Agent vs. Retrieval Chatbot:**
   1. **Chain:** Follows a fixed, developer-hardcoded sequence of steps (`prompt | llm | StrOutputParser()`); `StrOutputParser` unwraps the `AIMessage` response package and returns just the plain `.content` string.
   2. **Retrieval Chatbot (RAG):** Read-only system that grounds answers in fetched document chunks (*"Retrieval answers questions"*).
   3. **True Agent:** Runs an autonomous runtime **ReAct loop** (**Re**ason $\rightarrow$ **Act** by calling a tool $\rightarrow$ **Observe** result $\rightarrow$ **Repeat**), deciding dynamically whether to call tools (including retrieval or state-modifying tools) until the goal is met (*"Agents accomplish goals"*).
6. **The Three Cloud LLM Gates (e.g., AWS Bedrock):**
   1. **Gate 1 — Credentials (Authentication):** Valid AWS access keys / session token proving identity.
   2. **Gate 2 — IAM Permission (Authorization):** IAM policy granting inference permissions (`bedrock:InvokeModel` / `bedrock:Converse`).
   3. **Gate 3 — Model Access (Per-Region Provisioning):** The target foundation model must be enabled/subscribed in the exact AWS region queried.

### 10.4. RAG, Embeddings & Memory Checklist
1. **Chunking Defaults & Boundary Problem:** Start with `chunk_size=300` and `chunk_overlap=40` (`~15%` overlap) using `RecursiveCharacterTextSplitter`; `chunk_overlap` repeats a sliding window across boundaries so a sentence sitting at a boundary isn't sliced in half and missed during retrieval.
2. **Strict Grounding Prompt:** Always instruct the RAG model: *"Answer using ONLY the context below. If the context does not contain the answer, say you do not know."* and set `temperature=0`.
3. **Idempotent Vector Upserts:** Use deterministic chunk IDs (`f"{filename}::{chunk_idx}"`) with `collection.upsert(...)` to prevent duplicate entries on re-runs.
4. **Session Isolation:** Namespace Redis conversation keys by `f"history:{session_id}"` and set a TTL (`r.expire(key, 3600)`).
5. **Two-Stage Reranking (Bi-Encoder vs. Cross-Encoder):**
   1. **Bi-Encoder ("5-Second Resume Scan"):** Encodes query and documents separately into fixed vectors; fast and pre-computable offline in a vector DB to grab the initial top 50–100 candidates.
   2. **Cross-Encoder ("30-Minute In-Depth Interview"):** Processes `(query, document)` pairs jointly through full cross-attention for higher accuracy at slower speed; scores are pair-specific (cannot be precomputed) and rerank the 50–100 shortlist down to the final top 3–5.
6. **Hybrid Search ("Two Librarians" — BM25 + Vector + RRF):**
   1. **BM25 (Keyword Librarian):** Excels at exact lexical matches like SKU codes, product IDs, error codes, and legal references (weak on synonyms).
   2. **Vector Search (Meaning Librarian):** Excels at paraphrases, synonyms, and semantic meaning even without keyword overlap.
   3. **Reciprocal Rank Fusion (RRF):** Merges both ranked lists by rank position ($\sum \frac{1}{k + \text{rank}}$) without needing compatible raw score scales; the LLM is still required for final answer generation.

### 10.5. Reliability, Guardrails & Evaluation Checklist
1. **Enforce Schemas via API:** Use `response_format={"type": "json_schema", ...}` with `strict: True` and `additionalProperties: False` instead of relying on prompt instructions alone.
2. **3-Way Evidence Rulings:** In adjudication prompts, require one of `UPHELD` (supported by evidence), `REJECTED` (contradicted by evidence), or `ESCALATE` (evidence is missing/ambiguous).
3. **Targeted Retries:** Retry transient `429`, `500`, and `503` errors with exponential backoff (`time.sleep(2**attempt * 2)`), and fail fast on `401`, `404`, or quota errors.
4. **Dual Evaluation Assertions:** Every automated agent test case should verify both **trajectory** (was the right tool called?) and **outcome** (does the final answer contain the required facts?).

### 10.6. Essential One-Liners & CLI Commands
1. **Load nearest `.env` file automatically:**
   `from dotenv import find_dotenv, load_dotenv; load_dotenv(find_dotenv())`
2. **Run any service in Docker Compose (loads `.env` & mounts code):**
   `docker compose run --rm <service_name>`
3. **Rebuild Docker image after changing `requirements.txt`:**
   `docker compose run --rm --build <service_name>`
4. **Stop background ChromaDB / Redis containers and wipe volumes:**
   `docker compose down -v`
5. **Log inside an MCP `stdio` server without corrupting JSON-RPC stdout:**
   `print("[mcp-server] debug message", file=sys.stderr)`

### 10.7. Python Shorthands & Idioms for AI Coding Tests
1. **Floor / Clamping Shorthand (`max(1, round(characters / 4))`):**
   Guarantees a minimum value of `1` on a single line when `round(1 / 4)` would otherwise evaluate to `0`.
2. **Readable Numeric Literals (`1_000_000`):**
   Python ignores underscores inside numeric literals (`1_000_000 == 1000000`), preventing off-by-one zero typos in token pricing math.
3. **1-Based Enumeration & Unpacking (`for rank, doc_id in enumerate(ranking, start=1):`):**
   Starts counting positions at `1` instead of `0` (matching 1-based ranking formulas like RRF) and unpacks `(rank, doc_id)` directly.
4. **Safe Dictionary Accumulation (`scores[k] = scores.get(k, 0.0) + delta`):**
   Returns `0.0` when `k` is missing instead of raising `KeyError`, enabling one-line score accumulation across multiple ranked lists.
5. **Sorting a Dictionary by Value Descending (`sorted(d.items(), key=lambda item: item[1], reverse=True)`):**
   Converts `{key: score}` into `(key, score)` tuples via `.items()`, sorts by index `1` (`score`), and orders highest-first via `reverse=True`.
6. **Unwrapping Batch Cosine Similarity (`util.cos_sim(q_emb, doc_embs)[0]`):**
   `util.cos_sim` returns a 2D tensor of shape `[num_queries, num_docs]`; indexing `[0]` extracts the 1D row of scores for a single query.
7. **Index-Preserving List Comprehension (`[(i, float(scores[i])) for i in range(len(docs))]`):**
   Glues each document's original 0-based index `i` to its scalar `float` score before sorting so the original position is never lost.
8. **Top-K Slice + Dict Comprehension (`{idx: round(score, 2) for idx, score in ranked[:top_k]}`):**
   Slices the top `top_k` tuples (`[:top_k]`), unpacks `idx, score`, and constructs the final rounded dictionary in one expression.

---

## 11. AI Infusion Test: Coding Solutions, Python Idioms & MCQs

### 11.1. Coding 1: Token Cost Estimator (`estimate_token_cost`) & Python Shorthands
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

#### Context & Problem Statement
1. **Context:** LLMs charge per token, not per character or word. Before shipping any AI feature, an engineer needs a quick way to estimate how many tokens a piece of text will consume and what that will cost against a given pricing rate.
2. **Task — Write `estimate_token_cost(text, price_per_million)`:**
   1. Count the total number of characters in `text`.
   2. Estimate the token count using the rule `"1 token ≈ 4 characters"` — i.e., `tokens = round(characters / 4)`, with a minimum of `1` token for any non-empty text (and `0` for `""`).
   3. Compute the cost as `(tokens / 1,000,000) * price_per_million`.
   4. Return a dictionary with three keys: `"characters"` (`int`), `"tokens"` (`int`), and `"cost"` (`float`, rounded to 6 decimal places).

#### Sample Input, Output & Verified Solution
```python
import sys


def estimate_token_cost(text: str, price_per_million: float) -> dict:
    # Step 1: Count the total number of characters in the input string
    characters = len(text)

    # Step 2: Estimate token count using the "1 token ≈ 4 characters" rule of thumb.
    # - Empty strings ("") consume 0 tokens.
    # - For any non-empty string (e.g., 1 character where round(1 / 4) == 0),
    #   max(1, ...) acts as a floor so the token count is never less than 1.
    if characters == 0:
        tokens = 0
    else:
        tokens = max(1, round(characters / 4))

    # Step 3: Calculate the API cost based on the rate per 1,000,000 tokens
    # (1_000_000 uses Python underscores as visual thousands separators, equal to 1000000)
    # and round to 6 decimal places as required by the specification.
    cost = round((tokens / 1_000_000) * price_per_million, 6)

    # Step 4: Return the structured summary dictionary
    return {"characters": characters, "tokens": tokens, "cost": cost}


# Sample Input & Output Walkthrough:
# text = "AI Engineering is surprisingly approachable and powerful for beginners!" (len = 71)
# price_per_million = 5.0
# -> tokens = round(71 / 4) = round(17.75) = 18
# -> cost = round((18 / 1_000_000) * 5.0, 6) = 0.00009
# -> {"characters": 71, "tokens": 18, "cost": 0.00009}
```

#### Python Shorthands & Idioms Explained
1. **`max(1, round(characters / 4))` (Clamping / Floor Shorthand):**
   1. `round(characters / 4)` divides the character count by 4 and rounds to the nearest integer. For a 1-character string (`"a"`), `1 / 4` is `0.25`, which rounds down to `0`.
   2. Wrapping it in `max(1, ...)` compares `1` against the rounded number and picks whichever is larger — guaranteeing a minimum of `1` token in a single line (equivalent to `tokens = round(characters / 4); if tokens < 1: tokens = 1`).
2. **`1_000_000` (Numeric Literal Underscores):**
   1. Python allows underscores inside numbers (`1_000_000`) purely for human readability so you don't miscount zeros; Python treats `1_000_000` identically to `1000000`.

### 11.2. Coding 2: Hybrid Search Rank Fusion (`reciprocal_rank_fusion`) & Python Shorthands
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

#### Context & Problem Statement
1. **Context:** Pure keyword search (BM25) and pure semantic search (vector similarity) each catch things the other misses. Production RAG systems merge both rankings into one using **Reciprocal Rank Fusion (RRF)** — a formula that rewards documents ranked highly by either method without needing to re-scale raw scores.
2. **Task — Write `reciprocal_rank_fusion(bm25_ranking, vector_ranking, k_constant, top_n)`:**
   1. `bm25_ranking` and `vector_ranking` are lists of document IDs ordered from most to least relevant (best result first).
   2. For every document appearing in either list, compute its RRF score as the sum of `1 / (k_constant + rank)` across each list it appears in, where `rank` is its **1-based position** in that list (a document missing from a list contributes `0` from that list).
   3. Sort all documents by their combined score, highest first.
   4. Return a dictionary containing only the top `top_n` documents, mapping each document ID to its score rounded to 4 decimal places.

#### Sample Input, Output & Verified Solution
```python
import sys


def reciprocal_rank_fusion(
    bm25_ranking: list[int],
    vector_ranking: list[int],
    k_constant: int,
    top_n: int,
) -> dict:
    # Dictionary mapping each document ID -> its accumulated RRF score
    rrf_scores = {}

    # Step 1: Accumulate RRF contributions from the BM25 keyword ranking.
    # - enumerate(..., start=1) yields (rank, doc_id) pairs with rank starting at 1.
    # - rrf_scores.get(doc_id, 0.0) fetches the existing score for doc_id, or returns
    #   0.0 if doc_id is not yet in the dictionary.
    for rank, doc_id in enumerate(bm25_ranking, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank))

    # Step 2: Accumulate RRF contributions from the dense vector similarity ranking.
    # Documents appearing in BOTH lists have their two scores summed together;
    # documents appearing in only one list start at 0.0 and get this single score.
    for rank, doc_id in enumerate(vector_ranking, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank))

    # Step 3: Sort all candidate documents by their combined RRF score (highest first).
    # - rrf_scores.items() produces (doc_id, score) tuples, e.g., [(3, 0.0323), (1, 0.0325), ...].
    # - key=lambda item: item[1] tells sorted() to compare each tuple by index 1 (the score)
    #   instead of index 0 (the doc_id).
    # - reverse=True sorts in descending order (largest score first).
    sorted_docs = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

    # Step 4: Slice the first top_n tuples (sorted_docs[:top_n]) and build the final
    # dictionary with scores rounded to 4 decimal places.
    result = {}
    for doc_id, score in sorted_docs[:top_n]:
        result[doc_id] = round(score, 4)

    return result


# Sample Input & Output Walkthrough (bm25=[3, 1, 4, 2], vector=[1, 2, 3, 5], k_constant=60, top_n=3):
# - Doc 1: Rank 2 in BM25 + Rank 1 in Vector -> 1/62 + 1/61 = 0.032522 -> 0.0325
# - Doc 3: Rank 1 in BM25 + Rank 3 in Vector -> 1/61 + 1/63 = 0.032266 -> 0.0323
# - Doc 2: Rank 4 in BM25 + Rank 2 in Vector -> 1/64 + 1/62 = 0.031754 -> 0.0318
# - Doc 4 (1/63 = 0.0159) and Doc 5 (1/64 = 0.0156) are excluded by top_n=3
# -> {1: 0.0325, 3: 0.0323, 2: 0.0318}
```

#### Python Shorthands & Idioms Explained
1. **`for rank, doc_id in enumerate(bm25_ranking, start=1):` (1-Based Enumeration & Tuple Unpacking):**
   1. Passing `start=1` tells `enumerate()` to count positions starting from `1` (`1, 2, 3, ...`), matching the 1-based `rank` in $\frac{1}{k + \text{rank}}$.
   2. Each iteration yields `(rank, doc_id)` which unpacks directly into `rank` and `doc_id`.
2. **`rrf_scores.get(doc_id, 0.0)` (Safe Dictionary Lookup with Default):**
   1. Avoids `KeyError` on unseen document IDs by returning `0.0` when `doc_id` is not yet in `rrf_scores`.
3. **`sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)` (Sorting a Dictionary by Value):**
   1. `.items()` converts the dict into `(doc_id, score)` tuples; `key=lambda item: item[1]` sorts by the score at index `1`; `reverse=True` orders highest score first.
4. **`sorted_docs[:top_n]` (List Slicing):**
   1. Takes at most the first `top_n` elements from the sorted list.

### 11.3. Coding 3: Semantic Similarity Search (`semantic_search`) & Python Shorthands
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

#### Context & Problem Statement
1. **Context:** Before reranking or hybrid tricks are added, the core of every RAG system is single-stage semantic search: encode a query and documents into vectors and find which documents are closest in meaning using cosine similarity.
2. **Task — Write `semantic_search(query, documents, top_k)`:**
   1. Use `SentenceTransformer('all-MiniLM-L6-v2')` to encode `query` and every string in `documents` into embeddings.
   2. Compute the cosine similarity between the query embedding and each document embedding.
   3. Rank the documents by similarity score, highest first, and select the top `top_k` documents.
   4. Return a dictionary mapping the **0-based index** of each selected document in `documents` to its cosine similarity score rounded to 2 decimal places.

#### Sample Input, Output & Verified Solution
```python
import sys
from sentence_transformers import SentenceTransformer, util


def semantic_search(query: str, documents: list[str], top_k: int) -> dict:
    # Step 1: Load the pretrained bi-encoder embedding model (384-dimensional vectors)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Step 2: Encode the query string and all document strings into PyTorch tensors
    # so they can be compared directly using vector math.
    query_embedding = model.encode(query, convert_to_tensor=True)
    doc_embeddings = model.encode(documents, convert_to_tensor=True)

    # Step 3: Compute cosine similarity between the query (shape: [1, 384]) and all
    # documents (shape: [N, 384]). util.cos_sim returns a 2D tensor of shape [1, N],
    # so indexing [0] extracts the 1D row of N similarity scores for our single query.
    scores = util.cos_sim(query_embedding, doc_embeddings)[0]

    # Step 4: Build a list of (doc_index, similarity_score) tuples using a list
    # comprehension, then sort the list in-place from highest score to lowest score.
    ranked = [(i, float(scores[i])) for i in range(len(documents))]
    ranked.sort(key=lambda x: x[1], reverse=True)

    # Step 5: Use a dictionary comprehension over the top_k slice to return
    # {doc_index: rounded_score} rounded to 2 decimal places.
    return {idx: round(score, 2) for idx, score in ranked[:top_k]}


# Sample Input & Output Walkthrough:
# query = "How do I reset my router?"
# documents = [
#   0: "To pay your bill, visit the billing portal.",
#   1: "Unplug the router for 30 seconds, then plug it back in to reset it.",
#   2: "Our new internet plans are faster than ever.",
#   3: "A factory reset can be done by holding the pinhole button for 10 seconds."
# ]
# top_k = 2 -> {1: 0.83, 3: 0.48}
```

#### Python Shorthands & Idioms Explained
1. **`scores = util.cos_sim(query_embedding, doc_embeddings)[0]` (2D Matrix Row Indexing):**
   1. `util.cos_sim(A, B)` compares batches of queries against batches of documents, returning shape `[num_queries, num_documents]` (here `[1, 4]`). Indexing `[0]` unwraps the first row into a 1D tensor of 4 scores.
2. **`ranked = [(i, float(scores[i])) for i in range(len(documents))]` (Index-Preserving List Comprehension):**
   1. Pairing `(i, float(scores[i]))` keeps the original 0-based document index `i` attached to its score during sorting, while `float(...)` converts the PyTorch scalar tensor into a standard Python `float`.
3. **`ranked.sort(key=lambda x: x[1], reverse=True)` (In-Place List Sort vs. `sorted()`):**
   1. Orders the `(doc_index, score)` tuples in-place by `x[1]` (the score) descending.
4. **`{idx: round(score, 2) for idx, score in ranked[:top_k]}` (Dict Comprehension + Slicing + Unpacking):**
   1. Slices the top `top_k` tuples, unpacks `idx, score`, and builds the rounded output dictionary in a single return statement.

### 11.4. MCQs 1–3: Tokenizer Logic (BPE), Chain vs. Agent & Output Parser (`StrOutputParser`)
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

1. **Question 01 — Tokenizer Logic:** *Why do LLMs use sub-word tokens instead of whole-word or single-letter tokens? (Select any ONE)*
   1. **[x] Tokens give a compact vocabulary (~100k chunks) while still being able to spell out any unseen word from familiar pieces** *(Correct)*
   2. [ ] Whole words are always cheaper to process than tokens
   3. [ ] Sub-word tokens eliminate the need for a context window
   4. [ ] Sub-word tokens make the model completely bug-free
   5. **Why Option 1 is correct & others are wrong:** Sub-word algorithms (like Byte-Pair Encoding, BPE) keep common words intact as single tokens while splitting rare, compound, or unseen words into smaller known pieces (`"token"` + `"ization"`), keeping the vocabulary compact (~50k–100k) with zero out-of-vocabulary (OOV) failures. Whole-word vocabularies would explode embedding matrix sizes and fail on typos/new words; transformers still have a finite context window; and tokenization is purely text-to-integer preprocessing.
2. **Question 02 — Chain vs. Agent:** *What is the key difference between a "chain" and an "agent"? (Select any ONE)*
   1. [ ] A chain uses a web UI library while an agent does not
   2. [ ] An agent always needs a vector database, a chain never does
   3. **[x] A chain follows a fixed sequence of steps; an agent decides on its own, at runtime, whether to call a tool** *(Correct)*
   4. [ ] There is no real difference — they are just two names for the same thing
   5. **Why Option 3 is correct & others are wrong:** A **chain** is a deterministic, developer-hardcoded pipeline (`prompt | llm | output_parser`) where every input flows through the exact same sequence. An **agent** uses the LLM as a runtime reasoning engine to dynamically choose which tool to call, with what arguments, and when to stop. Both are backend patterns independent of UI libraries, and chains routinely use vector databases (standard RAG is a fixed chain).
3. **Question 03 — The Package Opener (`StrOutputParser`):** *What does an output parser (like `StrOutputParser`) actually do in a chain? (Select any ONE)*
   1. [ ] It fetches website content for summarization
   2. [ ] It stores conversation memory across sessions
   3. [ ] It converts a prompt template's blanks into actual text
   4. **[x] It unwraps the model's response package and hands back just the plain text string** *(Correct)*
   5. **Why Option 4 is correct & others are wrong:** Chat models return a rich message object (`AIMessage`) containing `.content` plus metadata, token counts, and tool calls. `StrOutputParser` at the end of `prompt | llm | StrOutputParser()` extracts just the plain `.content` string. Document loaders fetch websites, memory/checkpointers store history, and `ChatPromptTemplate` fills template variables at the start of the chain.

### 11.5. MCQs 4–6: Chunk Overlap Boundary, Cloud LLM Three Gates & Function-to-Tool (`@tool`)
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

1. **Question 04 — The Boundary Problem (`chunk_overlap`):** *Why is `"chunk_overlap"` used when splitting documents into chunks for retrieval? (Select any ONE)*
   1. [ ] To make the vector database run faster
   2. **[x] To ensure a sentence sitting at a chunk boundary isn't split and missed entirely** *(Correct)*
   3. [ ] To reduce the number of tokens billed per API call
   4. [ ] To automatically translate text into multiple languages
   5. **Why Option 2 is correct & others are wrong:** Fixed-size splitting can slice a key sentence in half right at the boundary so neither chunk alone matches the query. `chunk_overlap` slides the window back so the tail of Chunk 1 repeats at the start of Chunk 2, preserving boundary context (slightly increasing total chunks/tokens rather than speeding up search or reducing cost).
2. **Question 05 — The Three Gates (Cloud LLM Access):** *What are the three independent "gates" that must all be open before an agent can successfully call a cloud-hosted model? (Select any ONE)*
   1. **[x] Credentials, IAM permission, and Model access (enabled per region)** *(Correct)*
   2. [ ] Internet connection, RAM, and CPU speed
   3. [ ] Python version, pip version, and OS type
   4. [ ] Framework version, UI library version, and API key
   5. **Why Option 1 is correct & others are wrong:** Calling a managed enterprise cloud LLM (such as AWS Bedrock) requires passing three independent cloud gates: **Gate 1 — Credentials** (authentication proving identity), **Gate 2 — IAM Permission** (authorization policy such as `bedrock:InvokeModel` / `bedrock:Converse`), and **Gate 3 — Model Access** (per-region model subscription enabled in the target AWS region).
3. **Question 06 — Function to Tool:** *What three things must be added to a plain Python function to turn it into an agent-usable tool? (Select any ONE)*
   1. [ ] A class definition, a database connection, and a return statement
   2. [ ] An API key, a region name, and a session object
   3. [ ] A Gradio interface, a vector store, and an embedding model
   4. **[x] A decorator marking it as a tool, type hints, and a clear docstring** *(Correct)*
   5. **Why Option 4 is correct & others are wrong:** Agent frameworks (AWS Strands, LangChain) inspect three elements: (1) the `@tool` decorator to register the function, (2) **type hints** (`param: str -> dict`) to auto-generate the JSON Schema of parameter names and types, and (3) a **clear docstring** (`"""..."""`) injected into the model prompt so the LLM knows *what* the tool does and *when* to call it.

### 11.6. MCQs 7–9: Bi-Encoder vs. Cross-Encoder Reranking, Hybrid Search (BM25 + RRF) & Retrieval vs. Agents
Source: `study/11-ai-infusion-test/ai-infusion-test.md`

1. **Question 07 — Resume Scan vs. Interview (Bi-Encoders & Cross-Encoders):** *Which of the following statements are **TRUE** about bi-encoders and cross-encoders used in reranking? (Select ALL that apply)*
   1. **[x] Bi-encoders encode the query and document separately, making them fast and pre-computable** *(Correct)*
   2. [ ] Cross-encoders are used to grab the initial top 50–100 candidates from millions of chunks
   3. **[x] Cross-encoders process the query and document together, giving higher accuracy but at slower speed** *(Correct)*
   4. [ ] Bi-encoders always produce more accurate rankings than cross-encoders
   5. **[x] Cross-encoder scores cannot be precomputed because each score is pair-specific** *(Correct)*
   6. **Explanation:** **Bi-encoders ("5-Second Resume Scan")** embed documents once offline into a vector DB and quickly retrieve the initial top 50–100 candidates via cosine similarity. **Cross-encoders ("30-Minute In-Depth Interview")** pass `[CLS] query [SEP] document [SEP]` jointly through every self-attention layer, capturing fine-grained relevance much more accurately than bi-encoders, but since every `(query, doc)` pair requires a live forward pass, scores cannot be precomputed and are only run on the 50–100 candidate shortlist.
2. **Question 08 — Two Librarians (Hybrid Search: BM25 + Vector Search):** *Which of the following are **TRUE** about hybrid search (BM25 + vector search)? (Select ALL that apply)*
   1. **[x] BM25 excels at exact matches like SKU codes, product IDs, and legal references** *(Correct)*
   2. **[x] Vector search excels at understanding paraphrases and semantic meaning, even without exact keyword overlap** *(Correct)*
   3. [ ] Hybrid search eliminates the need for an LLM in the final answer generation step
   4. **[x] Reciprocal Rank Fusion (RRF) merges the two ranked lists into one combined ranking** *(Correct)*
   5. [ ] BM25 is better than vector search at understanding synonyms
   6. **Explanation:** **BM25 ("Keyword Librarian")** uses lexical TF-IDF matching that shines on exact strings (`SKU-9981`, error codes, legal clauses) but fails on synonyms. **Vector search ("Meaning Librarian")** maps paraphrases and synonyms close together in embedding space. **Reciprocal Rank Fusion (RRF)** combines both ranked lists by rank position ($\sum \frac{1}{k + \text{rank}}$), and the LLM is still required at the end to synthesize the final grounded answer.
3. **Question 09 — Answers vs. Goals (Retrieval Chatbot vs. True Agent):** *Which of the following statements correctly describe the difference between a retrieval-based chatbot and a true agent? (Select ALL that apply)*
   1. **[x] A retrieval-based system grounds answers in fetched information, while an agent can act, observe results, and retry using tools** *(Correct)*
   2. **[x] An agent runs a reasoning loop (reason → act → observe → repeat) until it judges the goal is met** *(Correct)*
   3. [ ] A retrieval-based chatbot can also directly modify a database record when asked
   4. [ ] An agent cannot use retrieval as part of its workflow
   5. **[x] Retrieval answers questions; agents accomplish goals** *(Correct)*
   6. **Explanation:** A **retrieval-based chatbot (RAG)** is a read-only pipeline that fetches documents to answer questions. A **true agent** runs an autonomous **ReAct loop** (`reason -> act -> observe -> repeat`), can call action tools that modify external state (databases, APIs, emails), and can also use retrieval as one of its tools (**Agentic RAG**) to accomplish multi-step goals.
