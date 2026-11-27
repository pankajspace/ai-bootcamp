# researcher.py — run the whole plan, wave by wave (execute_plan) and run ONE task with the right tool (run_task)
import asyncio
from openai import AsyncOpenAI
from common import ResearchPlan, SubTask, TaskStatus
from tools.financial_data import get_financial_metrics
from tools.sec_filings import get_risk_factors
from tools.web_search import search_financial_news

NAMES = {"NVDA": "NVIDIA", "AMD": "AMD", "INTC": "INTEL"}


def extract_tickers(text: str) -> list[str]:
    """'Fetch Intel metrics' → ['INTC']"""
    up = text.upper()
    return [tk for tk, name in NAMES.items() if tk in up or name in up]


async def analyze_with_llm(instruction: str, context: str) -> str:
    """For 'thinking' tasks (6 and 7): reason over earlier results."""
    response = await AsyncOpenAI().chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a financial analyst. "
             "Use ONLY the data given. Quote numbers exactly."},
            {"role": "user", "content": f"{instruction}\n\nDATA:\n{context}"},
        ],
    )
    return response.choices[0].message.content


async def run_task(task: SubTask, results: dict[int, str]) -> tuple[int, str]:
    task.status = TaskStatus.RUNNING
    try:
        if task.dependencies:                                # ① a thinking task
            context = "\n\n".join(f"[Task {d}] {results[d]}"
                                  for d in task.dependencies)
            output = await analyze_with_llm(task.description, context)
        elif "financial_api" in task.data_sources:           # ② numbers
            ticker = extract_tickers(task.description)[0]
            metrics = await get_financial_metrics(ticker)
            output = metrics.model_dump_json()
        elif "sec_filing" in task.data_sources:              # ③ filings
            tickers = extract_tickers(task.description)
            output = "\n\n".join([await get_risk_factors(t) for t in tickers])
        else:                                                # ④ news
            output = await search_financial_news(task.description)
        task.status = TaskStatus.COMPLETED
    except Exception as e:                                   # ⑤ never crash
        task.status = TaskStatus.FAILED
        output = f"ERROR: {e}"
    return task.id, output


async def execute_plan(plan: ResearchPlan) -> dict[int, str]:
    results: dict[int, str] = {}                      # ① the shared notebook
    tasks_by_id = {t.id: t for t in plan.sub_tasks}   # ② id → task lookup

    while any(t.status == TaskStatus.PENDING for t in plan.sub_tasks):   # ③
        ready = [                                     # ④ who can start now?
            t for t in plan.sub_tasks
            if t.status == TaskStatus.PENDING
            and all(tasks_by_id[d].status == TaskStatus.COMPLETED
                    for d in t.dependencies)
        ]
        if not ready:                                 # ⑤ stuck → stop the loop
            break
        completed = await asyncio.gather(             # ⑥ run the wave together
            *[run_task(t, results) for t in ready]
        )
        for task_id, result in completed:             # ⑦ write it all down
            results[task_id] = result

    return results
