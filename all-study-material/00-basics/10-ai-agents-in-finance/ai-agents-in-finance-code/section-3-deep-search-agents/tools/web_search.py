# tools/web_search.py — recent news, from trusted publishers only
import os
from tavily import AsyncTavilyClient

TRUSTED = ["reuters.com", "bloomberg.com", "wsj.com",
           "cnbc.com", "seekingalpha.com", "ft.com"]


async def search_financial_news(query: str) -> str:
    client = AsyncTavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = await client.search(
        query,
        topic="news",                # news search, not the whole web
        include_domains=TRUSTED,     # only these publishers
        max_results=5,
    )
    # a list of hits → one readable block of text for the LLM
    return "\n\n".join(
        f"{hit['title']} ({hit['url']})\n{hit['content']}"
        for hit in response["results"]
    )
