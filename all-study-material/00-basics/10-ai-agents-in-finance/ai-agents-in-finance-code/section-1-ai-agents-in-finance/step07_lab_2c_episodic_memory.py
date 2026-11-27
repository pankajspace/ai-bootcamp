"""Lab 2C · Episodic memory: turn Lab 2B's conversation into a "journal page", file it in
Chroma, and use it days later in a fresh session."""
import asyncio
import json
import os

import chromadb
from agents import Runner, SQLiteSession
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI

from step06_lab_2b_working_memory import portfolio_agent, run_working_memory

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

episodic_memory_prompt_template = """
You will read a conversation between a user and a portfolio-rebalancing agent.
Extract an episodic memory that will help the agent in future sessions.

OUTPUT FORMAT:
Return only valid JSON in this exact schema:
{{
  "conversation_summary": string,            // 3–5 sentences: market conditions, portfolio situation, actions taken
  "portfolio_allocation_trajectory": string, // how allocations changed, with the market situation each time
  "what_worked": string,                     // alignment with goals, risk management, clear decisions
  "what_didnt_work": string,                 // unclear strategy, over/under-reaction, concentration risk, data issues
  "key_points": ["string"]                   // the most important insights to keep for future sessions
}}

(… a few examples of GOOD and POOR summaries go here — few-shot …)

Here is the conversation between the user and the principal portfolio-rebalancing agent:
{conversation}
"""


async def main():
    # Step 1 · the conversation from Lab 2B
    conversation_history = await run_working_memory()

    # Step 2 · list of (role, text) pairs → one string
    conversation_history_string = "\n\n".join(
        [f'{role}: """{text}"""' for role, text in conversation_history]
    )

    # Step 3 · the prompt
    user_prompt = episodic_memory_prompt_template.format(conversation=conversation_history_string)

    # Step 4 · ask the LLM to write the journal page
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": user_prompt}],
        text={"format": {"type": "json_object"}},              # JSON mode, as in Lab 1A
    )
    episodic_memory = json.loads(response.output[0].content[0].text)   # JSON text → Python dict
    print(json.dumps(episodic_memory, indent=2))

    # Step 5 · prepare two versions of the same page
    # Version A: one readable text — this is what gets embedded and searched by meaning
    document_text = f"""
Conversation Summary: {episodic_memory['conversation_summary']}
Portfolio Allocation Trajectory: {episodic_memory['portfolio_allocation_trajectory']}
What Worked: {episodic_memory['what_worked']}
What Didn't Work: {episodic_memory['what_didnt_work']}
Key Points: {', '.join(episodic_memory['key_points'])}
"""
    # Version B: the same facts as separate fields — the labels on the folder
    metadata_clean = {
        "conversation_summary": episodic_memory["conversation_summary"],
        "portfolio_allocation_trajectory": episodic_memory["portfolio_allocation_trajectory"],
        "what_worked": episodic_memory["what_worked"],
        "what_didnt_work": episodic_memory["what_didnt_work"],
        "key_points": " | ".join(episodic_memory["key_points"]),   # list → one string
    }

    # Step 6 · open the filing cabinet
    # The translator: turns any text into a list of 1,536 numbers (a vector) that captures its meaning
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small",
    )
    collection_name = "episodic_memory_ptf_rebal"                         # the drawer's name
    persistent_client = chromadb.PersistentClient(path="./chroma_ptf_rebal")  # the cabinet, saved in a folder
    collection = persistent_client.get_or_create_collection(               # open the drawer (create it if new)
        collection_name, embedding_function=embedding_function
    )

    # Step 7 · file the page (upsert, so re-running doesn't fail on the existing id)
    collection.upsert(
        ids=["memory_1"],               # a unique name for this page
        documents=[document_text],      # the text → Chroma embeds it automatically with our translator
        metadatas=[metadata_clean],     # the folder labels
    )

    # Step 8 · days later: a new question searches the cabinet
    input_user_init = """Current Market Situation:
- Volatility Regime: low
- Market Trend: bullish
What rebalancing action should I take?"""

    episodic_memory_recap = collection.query(
        query_texts=[input_user_init],   # a LIST: you could ask several questions at once
        n_results=3,                     # up to 3 closest pages per question
    )

    # Step 9 · paste the lesson into the new question and run with a fresh notepad
    session_ptf_rebal_2 = SQLiteSession("conversation_ptf_2")      # a brand-new, EMPTY notepad

    input_user_with_memory = input_user_init + f"""
Here are relevant insights from past rebalancing episodes. Use them as guidance, not strict rules:
{episodic_memory_recap['documents'][0][0]}
Argue your proposition using past rebalancing episodes if needed.
"""

    output_using_memory = await Runner.run(
        starting_agent=portfolio_agent,
        input=input_user_with_memory,
        session=session_ptf_rebal_2,
    )
    print(output_using_memory.final_output)


if __name__ == "__main__":
    asyncio.run(main())
