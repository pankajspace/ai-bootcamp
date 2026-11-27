"""
Section 10 lab — Agentic RAG on a compliance question (LlamaIndex + Claude)
==========================================================================
The question every step tries to answer:

    "Does Acme's Q3 quick ratio satisfy the firm's risk policy?"

To answer it you need TWO facts from TWO different documents:
    • Acme's Q3 quick ratio            → the Q3 earnings-call transcript (1.18)
    • the bank's minimum quick ratio   → the internal risk policy        (1.00)

We answer the same question eight ways and compare:

    naive      one blended index, top-3 chunks, no thinking          (the baseline)
    router     an LLM picks ONE document to search                   (routing)
    subq       an LLM splits the question into per-document parts    (decomposition)
    agent      an agent searches, checks, and searches again         (self-correction)
    hybrid     meaning search + keyword search, fused with RRF       (better recall)
    rerank     fetch 6 chunks, an LLM keeps the best 2               (better precision)
    hybrid_rerank   both together                                    (production default)
    evaluate   grade an answer: faithfulness / relevancy triad       (measurement)

How to run
----------
1. pip install llama-index-core llama-index-llms-anthropic llama-index-embeddings-openai \
               llama-index-retrievers-bm25 python-dotenv
2. Create a .env file next to this script:
       ANTHROPIC_API_KEY=sk-ant-...
       OPENAI_API_KEY=sk-...            (only used for embeddings — fractions of a cent)
3. python step02_agentic_rag_lab.py               # every step, then a side-by-side table
   python step02_agentic_rag_lab.py agent         # just one step (naive, router, subq, agent,
                                           #   hybrid, rerank, hybrid_rerank, evaluate)

The three documents live in ./data and are synthetic. Roughly 40 Claude calls in total.
Learning only — not investment advice.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
SOURCES = {                                  # short key  → file in ./data
    "ten_k": "acme_10k_excerpt.md",
    "earnings_call": "acme_earnings_call_q3.md",
    "risk_policy": "firm_risk_policy.md",
}
COMPARISON_QUESTION = "Does Acme's Q3 quick ratio satisfy the firm's risk policy?"

LLM_MODEL = "claude-sonnet-5-5"              # the reasoning + answer-writing model
EMBED_MODEL = "text-embedding-3-small"       # turns text into vectors for search


def configure_models() -> None:
    """Set the global models once; every index, engine and agent below reuses them."""
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.anthropic import Anthropic

    Settings.llm = Anthropic(model=LLM_MODEL, max_tokens=2048)
    Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL)


# Small chunks (≈150 tokens) so each document becomes several pieces. With one
# giant chunk per file, "top-3" would simply fetch the whole corpus and hide the
# problems naive RAG has on real, long filings.
Settings.chunk_size = 150
Settings.chunk_overlap = 20

COMPARISON: dict[str, str] = {}              # step name → answer to COMPARISON_QUESTION


def _source_of(node) -> str:
    return node.metadata.get("source", "(sub-answer)")   # sub-question answers have no file


def show(title: str, question: str, answer, nodes=None) -> None:
    """Print a question, the answer, and WHICH chunks the answer was built from."""
    nodes = nodes if nodes is not None else getattr(answer, "source_nodes", []) or []
    print(f"\n{'=' * 78}\n{title}\nQ: {question}\n{'-' * 78}")
    print(f"A: {str(answer).strip()}")
    print(f"\n  evidence used ({len(nodes)} chunks):")
    for n in nodes:
        score = f"{n.score:.3f}" if n.score is not None else "  -  "
        snippet = " ".join(n.node.get_content().split())[:70]
        print(f"   [{score}] {_source_of(n):<26} {snippet}…")

def _load(files: list[str]):
    """Read files from ./data and tag every document with its file name as 'source'."""
    return SimpleDirectoryReader(
        input_files=[DATA_DIR / f for f in files],
        file_metadata=lambda path: {"source": Path(path).name},
    ).load_data()


def load_indices() -> dict[str, VectorStoreIndex]:
    """One SEPARATE vector index per document — this is what makes routing possible."""
    return {key: VectorStoreIndex.from_documents(_load([fname]))
            for key, fname in SOURCES.items()}


def load_combined_index() -> VectorStoreIndex:
    """ONE index with all three documents blended together (the naive set-up)."""
    return VectorStoreIndex.from_documents(_load(list(SOURCES.values())))

def step_naive(combined: VectorStoreIndex) -> None:
    engine = combined.as_query_engine(similarity_top_k=3)     # fetch 3 chunks, then answer

    simple = "What was Acme's full-year 2024 total revenue?"  # one fact, one document
    show("NAIVE RAG — single fact", simple, engine.query(simple))

    answer = engine.query(COMPARISON_QUESTION)                # two facts, two documents
    show("NAIVE RAG — cross-document question", COMPARISON_QUESTION, answer)
    COMPARISON["naive"] = str(answer)

from llama_index.core.tools import QueryEngineTool


def build_query_engine_tools(indices: dict[str, VectorStoreIndex]) -> list[QueryEngineTool]:
    """Wrap each document index as a TOOL with a name and a plain-English description.

    The LLM never sees the documents when it chooses — it only reads these
    descriptions. Vague or overlapping descriptions = wrong source picked.
    """
    return [
        QueryEngineTool.from_defaults(
            query_engine=indices["ten_k"].as_query_engine(similarity_top_k=3),
            name="annual_report_10k",
            description=(
                "Acme Robotics' audited FY2024 annual report (Form 10-K). Full-year "
                "revenue, margins, EPS, year-end balance sheet, year-end current and "
                "quick ratios, credit-facility covenants and risk factors."),
        ),
        QueryEngineTool.from_defaults(
            query_engine=indices["earnings_call"].as_query_engine(similarity_top_k=3),
            name="q3_earnings_call",
            description=(
                "Acme Robotics' Q3 FY2025 earnings-call transcript (October 2025). "
                "Most recent quarterly figures: Q3 revenue, Q3 quick and current "
                "ratios, inventory build, raised guidance, analyst Q&A."),
        ),
        QueryEngineTool.from_defaults(
            query_engine=indices["risk_policy"].as_query_engine(similarity_top_k=3),
            name="firm_risk_policy",
            description=(
                "Future with Shivank Bank's internal liquidity and counterparty risk "
                "policy. The REQUIRED thresholds for a new long position: minimum "
                "quick ratio, current-ratio bands, max net debt/EBITDA, which source "
                "is controlling, concentration limits."),
        ),
    ]

from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector


def step_router(indices: dict[str, VectorStoreIndex]) -> None:
    router = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),            # LLM picks exactly ONE tool
        query_engine_tools=build_query_engine_tools(indices),
    )
    tool_names = [t.metadata.name for t in build_query_engine_tools(indices)]

    for q in ["What is the firm's minimum required quick ratio for a new long position?",
              "What was Acme's Q3 quick ratio?",
              "What credit-facility covenants does Acme disclose in its 10-K?",
              COMPARISON_QUESTION]:
        answer = router.query(q)
        pick = answer.metadata["selector_result"].selections[0]   # the routing decision
        show(f"ROUTER → picked '{tool_names[pick.index]}'  (why: {pick.reason[:60]}…)",
             q, answer)
    COMPARISON["router"] = str(answer)                     # answer to the last question

from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.question_gen import LLMQuestionGenerator


def step_subquestion(indices: dict[str, VectorStoreIndex]) -> None:
    engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=build_query_engine_tools(indices),
        # Pass the generator explicitly; the default one is OpenAI-specific.
        question_gen=LLMQuestionGenerator.from_defaults(),
        verbose=True,                       # prints each generated sub-question + tool
    )
    spanning = ("How did Acme's quick ratio change from year-end 2024 to Q3, and does "
                "the Q3 level breach the firm's risk policy?")
    show("SUB-QUESTIONS — trend + policy", spanning, engine.query(spanning))

    answer = engine.query(COMPARISON_QUESTION)
    show("SUB-QUESTIONS — comparison question", COMPARISON_QUESTION, answer)
    COMPARISON["subq"] = str(answer)

from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult

AGENT_SYSTEM_PROMPT = (
    "You are a buy-side compliance analyst. Answer using ONLY the document tools "
    "provided. First work out what evidence the question needs: a compliance check "
    "usually needs BOTH the issuer's figure from its filings AND the matching "
    "threshold from the firm's risk policy. Before concluding, check that you have "
    "every piece; if one tool call did not give you everything, call another tool. "
    "If a required figure cannot be found, say so explicitly instead of estimating. "
    "Cite the source document and reporting period for every figure you use."
)
MAX_AGENT_STEPS = 8          # guardrail: never loop forever, however confused the model is


def run_agent_sync(agent: FunctionAgent, task: str):
    """Run the agent; also record its tool calls (the 'trajectory') and evidence chunks."""
    trajectory: list[str] = []
    evidence: list = []

    async def _run():
        handler = agent.run(task, max_iterations=MAX_AGENT_STEPS,
                            early_stopping_method="generate")
        async for event in handler.stream_events():          # watch it work, live
            if isinstance(event, ToolCallResult):
                trajectory.append(f"{event.tool_name}({event.tool_kwargs.get('input', '')!r})")
                raw = getattr(event.tool_output, "raw_output", None)   # the tool's Response
                evidence.extend(getattr(raw, "source_nodes", None) or [])
        return await handler

    response = asyncio.run(_run())
    return response, trajectory, evidence


def step_agent(indices: dict[str, VectorStoreIndex]) -> None:
    agent = FunctionAgent(
        tools=build_query_engine_tools(indices),
        llm=Settings.llm,
        system_prompt=AGENT_SYSTEM_PROMPT,
    )
    task = ("Can we open a new long position in Acme Robotics under the firm's liquidity "
            "policy? Check the quick-ratio rule against Acme's most recent disclosed "
            "quick ratio.")
    for q, keep in ((task, False), (COMPARISON_QUESTION, True)):
        response, trajectory, evidence = run_agent_sync(agent, q)
        print("\n  agent tool calls, in order:")
        for i, call in enumerate(trajectory, 1):
            print(f"   {i}. {call}")
        show("SELF-CORRECTING AGENT", q, response, evidence)
        if keep:
            COMPARISON["agent"] = str(response)

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever


def build_hybrid_retriever(combined: VectorStoreIndex) -> QueryFusionRetriever:
    """Meaning search + keyword search over the SAME chunks, merged by rank (RRF)."""
    dense = combined.as_retriever(similarity_top_k=5)                  # by meaning
    sparse = BM25Retriever.from_defaults(docstore=combined.docstore,   # by exact words
                                         similarity_top_k=5)
    return QueryFusionRetriever(
        [dense, sparse],
        similarity_top_k=5,          # keep the best 5 after fusion
        num_queries=1,               # 1 = no LLM rewrites of the question (cheap, repeatable)
        mode="reciprocal_rerank",    # Reciprocal Rank Fusion: score = Σ 1/(60 + rank)
        use_async=False,
    )


def step_hybrid(combined: VectorStoreIndex) -> None:
    engine = RetrieverQueryEngine.from_args(build_hybrid_retriever(combined))
    answer = engine.query(COMPARISON_QUESTION)
    show("HYBRID (dense + BM25, fused)", COMPARISON_QUESTION, answer)
    COMPARISON["hybrid"] = str(answer)

from llama_index.core.postprocessor import LLMRerank


def step_rerank(indices: dict[str, VectorStoreIndex]) -> None:
    engine = indices["ten_k"].as_query_engine(
        similarity_top_k=6,                        # cast a wide net…
        node_postprocessors=[LLMRerank(top_n=2)],  # …then the LLM keeps the best 2
    )
    q = "What was Acme's gross margin in fiscal 2024 and why did it expand?"
    show("RERANK (top-6 → best 2)", q, engine.query(q))

def step_hybrid_rerank(combined: VectorStoreIndex) -> None:
    engine = RetrieverQueryEngine.from_args(
        build_hybrid_retriever(combined),                  # recall: wide, fused pool
        node_postprocessors=[LLMRerank(top_n=3)],          # precision: keep the best 3
    )
    answer = engine.query(COMPARISON_QUESTION)
    show("HYBRID + RERANK", COMPARISON_QUESTION, answer)
    COMPARISON["hybrid_rerank"] = str(answer)

from llama_index.core.evaluation import (
    AnswerRelevancyEvaluator,
    ContextRelevancyEvaluator,
    FaithfulnessEvaluator,
)


def step_evaluate(indices: dict[str, VectorStoreIndex]) -> dict:
    engine = indices["ten_k"].as_query_engine(similarity_top_k=3)
    q = "What was Acme's net income per diluted share in fiscal 2024?"
    response = engine.query(q)
    show("EVALUATE — the answer being graded", q, response)

    # The RAG triad. Each uses the LLM as a judge with a fixed grading prompt.
    faithful = FaithfulnessEvaluator().evaluate_response(response=response)
    answer_rel = AnswerRelevancyEvaluator().evaluate_response(query=q, response=response)
    context_rel = ContextRelevancyEvaluator().evaluate_response(query=q, response=response)

    scores = {
        "faithful": faithful.passing,          # True/False: every claim backed by chunks?
        "answer_relevancy": answer_rel.score,  # 0–1: does the answer address the question?
        "context_relevancy": context_rel.score,  # 0–1: were the fetched chunks on topic?
    }
    print("\n  RAG triad:", scores)
    return scores

STEPS = {
    "naive":         lambda ix, comb: step_naive(comb),
    "router":        lambda ix, comb: step_router(ix),
    "subq":          lambda ix, comb: step_subquestion(ix),
    "agent":         lambda ix, comb: step_agent(ix),
    "hybrid":        lambda ix, comb: step_hybrid(comb),
    "rerank":        lambda ix, comb: step_rerank(ix),
    "hybrid_rerank": lambda ix, comb: step_hybrid_rerank(comb),
    "evaluate":      lambda ix, comb: step_evaluate(ix),
}


def main(selected: list[str]) -> None:
    indices, combined = load_indices(), load_combined_index()   # embeds the corpus once
    for name in selected:
        STEPS[name](indices, combined)

    if len(COMPARISON) > 1:                                      # the side-by-side view
        print(f"\n{'#' * 78}\nSAME QUESTION, EVERY PATTERN: {COMPARISON_QUESTION}\n{'#' * 78}")
        for name, answer in COMPARISON.items():
            print(f"\n[{name}]\n  " + " ".join(answer.split())[:400])


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(STEPS)
    unknown = [w for w in wanted if w not in STEPS]
    if unknown:
        sys.exit(f"Unknown step(s) {unknown}. Choose from: {', '.join(STEPS)}")
    configure_models()
    main(wanted)
