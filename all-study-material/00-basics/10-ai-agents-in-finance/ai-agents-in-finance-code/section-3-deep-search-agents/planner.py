# planner.py — lab version, with PydanticAI
from pydantic_ai import Agent
from common import PLANNING_MODEL, ResearchPlan

PLANNER_SYSTEM_PROMPT = """You are a financial research planner. Given a research
question, decompose it into concrete sub-tasks that can be executed by tools.

Available data sources:
- financial_api: Structured financial metrics (revenue, EPS, margins, P/E, market cap)
- sec_filing: SEC filing content (risk factors, business descriptions, MD&A)
- web_search: Recent news, competitive intelligence, analyst commentary

Rules:
1. Each sub-task must have a clear, measurable outcome.
2. Specify which data_sources each sub-task should use.
3. Mark dependencies — which tasks must complete before others can start.
4. Tasks with no dependencies can run in parallel.
5. Always include a final synthesis task that depends on all data-gathering tasks.
6. For multi-company comparisons, create parallel tasks for each company.

Respond with a JSON object matching the ResearchPlan schema."""

planner_agent = Agent(
    model=PLANNING_MODEL,
    system_prompt=PLANNER_SYSTEM_PROMPT,
    output_type=ResearchPlan,             # the form the answer must fit
    retries=2,                            # wrong shape? sent back, up to 2 times
    model_settings={"temperature": 0},
)


async def create_research_plan(question: str) -> ResearchPlan:
    result = await planner_agent.run(question)
    return result.output                  # already a ResearchPlan object
