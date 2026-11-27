"""Lab 2E · Evaluator-optimizer loop: a news searcher rewrites until a judge approves its links."""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, WebSearchTool
from dotenv import load_dotenv

load_dotenv()

# Step 1 · the date window
today_date   = datetime.now().strftime("%Y-%m-%d")                         # e.g. "2026-10-22"
two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")   # e.g. "2026-10-20"

# Step 2 · the searcher
INSTRUCTIONS_NEWS_SEARCH = (
    "You are a research news assistant specialized in Finance or any news that can have an impact "
    "on the financial health of a given company or a region. "
    "You search the web for a given region to collect the most important and recent news. "
    "Produce a concise summary of the results with citations. The summary must be "
    "2-3 paragraphs and less than 300 words. Capture the main points. Write succinctly. "
    f"Get only the latest news between 2 days ago {two_days_ago} and today {today_date}. "
    "Use only this resource: https://www.reuters.com/. "
    "For each item you are providing, specify the date on which the article was published. "
    "For each item you are providing, specify the complete external link to the article. "
    "This is important. Otherwise, don't give me a summary, if you don't provide a date and an external link. "
    "If you don't give a source link, it means that you are hallucinating. "
)

web_news_searcher = Agent(
    name="web_news_searcher",
    instructions=INSTRUCTIONS_NEWS_SEARCH,
    tools=[WebSearchTool()],          # OpenAI's hosted web search — no code of your own needed
)


# Step 3 · the evaluator and its "form"
@dataclass
class EvaluationFeedback:
    feedback: str                                    # free text: why it passed or failed
    score: Literal["successful", "unsuccessful"]     # exactly one of these two words — nothing else

news_evaluator = Agent(
    name="news_evaluator",
    instructions=(
        "You will be given a financial news summary in a given region (Euro, US, Asia) and you are "
        "asked to evaluate the completeness of external source links. "
        "Check whether the news summary is supported by external article links from https://www.reuters.com/. "
        f"Check whether the news summary was published between 2 days ago {two_days_ago} and today {today_date}. "
        "For each item of news, the date of the news must be explicitly provided. "
        "Check whether the news summary corresponds to the region or regions requested by the user. "
        "If the user requested 'n' news items, each item must be supported by an external source link, "
        "so you need to ensure that there are 'n' source links. "
        "External links are required for the user to verify the accuracy of the news. "
    ),
    output_type=EvaluationFeedback,                  # forces the answer into the form above
)


# Step 4 · the loop
async def main():
    msg = input("User's request:")    # e.g. "Provide the latest 5 news in the Eurozone and specify the source for each one."
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]   # the searcher's running chat
    latest_outline: str | None = None   # will hold the newest news summary
    max_iteration = 4                   # retry limit
    nbr_iterations = 0                  # retries so far

    while True:
        # 1) The searcher writes (or rewrites) the summary, seeing the whole chat so far
        news_searcher_result = await Runner.run(web_news_searcher, input_items)
        input_items = news_searcher_result.to_input_list()                       # old chat + the new reply
        latest_outline = ItemHelpers.text_message_outputs(news_searcher_result.new_items)  # just the new text

        # 2) The evaluator grades ONLY the newest summary
        news_evaluator_result = await Runner.run(news_evaluator, latest_outline)
        result: EvaluationFeedback = news_evaluator_result.final_output         # the filled-in form

        # 3) Passed? Stop.
        if result.score == "successful":
            print("Links check is good ==> stopping the iteration.")
            break

        # 4) Failed: add the summary and the judge's feedback to the chat, then go round again
        input_items.append({"content": f"News Summary: {latest_outline}", "role": "system"})
        input_items.append({"content": f"Feedback: {result.feedback}\n for each item in the news summary, "
                                       "provide an external source link:", "role": "user"})
        nbr_iterations += 1
        if nbr_iterations > max_iteration:
            print("Reached max_iteration ==> stopping the iteration.")
            break

    print(latest_outline)


if __name__ == "__main__":
    asyncio.run(main())
