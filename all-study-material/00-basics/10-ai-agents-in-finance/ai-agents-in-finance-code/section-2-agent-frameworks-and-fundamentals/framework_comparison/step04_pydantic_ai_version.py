"""PydanticAI: declare the form first (≈2,382 tokens in the notes' run)."""
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from common import MODEL, compute_pe_ratio, get_stock_data, input_message, system_message


class InvestmentMemo(BaseModel):            # the "form" every answer must fill in
    aapl_pe: float = Field(description="Computed P/E for AAPL")
    jpm_pe: float = Field(description="Computed P/E for JPM")
    memo: str = Field(description="Short comparative memo")


agent = Agent(f"openai:{MODEL}", system_prompt=system_message, output_type=InvestmentMemo,
              tools=[get_stock_data, compute_pe_ratio])
result = agent.run_sync(input_message)
print(result.output.model_dump_json(indent=2))   # validated JSON, not prose
