# synthesizer.py — lab version: only the LLM call changes
from pydantic_ai import Agent
from common import SYNTHESIS_MODEL, ResearchReport, ValidationResult

SYNTH_PROMPT = """You are a senior equity research analyst.
Write an investment research memo using ONLY the findings provided.
- Quote numbers exactly as given. Never invent a number.
- If data is missing, say so plainly.
- Mention every validation warning where it is relevant.
- confidence_score (0 to 1) must reflect how complete and clean the data is."""

synth_agent = Agent(
    model=SYNTHESIS_MODEL,
    system_prompt=SYNTH_PROMPT,           # same prompt as before
    output_type=ResearchReport,
    retries=2,
    model_settings={"temperature": 0},
)


async def synthesize_report(question: str, results: dict[int, str],
                            validation: ValidationResult) -> ResearchReport:
    findings = "\n\n".join(f"[Task {tid}]\n{text}"           # ① the research folder
                           for tid, text in sorted(results.items()))
    notes = "\n".join(                                        # ② the checker's notes
        [f"WARNING: {w}" for w in validation.warnings]
        + [f"GAP: {g}" for g in validation.gaps]
        + [f"ERROR: {e}" for e in validation.errors]
    ) or "No issues found."
    result = await synth_agent.run(
        f"QUESTION:\n{question}\n\nFINDINGS:\n{findings}"
        f"\n\nVALIDATION NOTES:\n{notes}"
    )
    return result.output
