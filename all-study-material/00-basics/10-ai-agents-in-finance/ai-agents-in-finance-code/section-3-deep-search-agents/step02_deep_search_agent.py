# step02_deep_search_agent.py — the manager that runs the whole loop
import asyncio
from pathlib import Path
from common import ResearchReport
from planner import create_research_plan
from researcher import execute_plan
from validator import validate_research
from synthesizer import synthesize_report

MAX_REPLAN_ATTEMPTS = 2


async def deep_search(question: str, tickers: list[str]) -> ResearchReport:
    for attempt in range(MAX_REPLAN_ATTEMPTS + 1):              # attempt = 0, 1, 2
        plan = await create_research_plan(question)             # Phase 1: plan
        results = await execute_plan(plan)                      # Phase 2: execute
        validation = validate_research(plan, results, tickers)  # Phase 3: check
        if validation.is_valid:
            break                                               # all good → leave
        elif attempt < MAX_REPLAN_ATTEMPTS:                     # tries left → re-plan
            problems = validation.gaps + validation.errors
            question += "\nAddress these gaps:\n" + "\n".join(problems)
    return await synthesize_report(question, results, validation)   # Phase 4


if __name__ == "__main__":
    QUESTION = (
        "Analyze NVIDIA's financial performance and competitive position in "
        "the AI chip market. Compare with AMD and Intel on revenue growth, "
        "profitability, and key risk factors. Produce a structured "
        "investment research memo."
    )
    report = asyncio.run(deep_search(QUESTION, ["NVDA", "AMD", "INTC"]))
    Path("output").mkdir(exist_ok=True)
    Path("output/report.json").write_text(report.model_dump_json(indent=2))
    print(report.title)
    print(report.executive_summary)
    print(f"Confidence: {report.confidence_score:.0%}")
