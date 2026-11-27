# step01_try_planner.py — test the wiring for free: no real LLM call
import asyncio
from pydantic_ai.models.test import TestModel
from planner import planner_agent, create_research_plan


async def main():
    with planner_agent.override(model=TestModel()):    # a fake, free "LLM"
        plan = await create_research_plan("Compare NVIDIA with AMD")
    print(plan)            # dummy text, but a perfectly valid ResearchPlan


asyncio.run(main())
