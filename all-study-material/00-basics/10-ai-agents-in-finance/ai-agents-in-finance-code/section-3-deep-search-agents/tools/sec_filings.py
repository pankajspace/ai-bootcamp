# tools/sec_filings.py — "Item 1A. Risk Factors" from a company's latest 10-K
# Filled in: the notes use get_risk_factors(ticker) but don't print it. This version uses
# SEC EDGAR's free API, which only asks for a contact e-mail in the User-Agent header.
import os
import re
from html import unescape

import httpx

MAX_CHARS = 6000   # keep the LLM context small: the start of the section is the summary


def _headers() -> dict:
    email = os.environ.get("SEC_EDGAR_EMAIL", "learner@example.com")
    return {"User-Agent": f"ai-agents-in-finance-course {email}"}


def _html_to_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    # Inline tags join without a space (filings split small-caps words across <span>s);
    # block tags become a space.
    text = re.sub(r"(?is)</?(span|font|b|i|u|em|strong|a|sup|sub|small)\b[^>]*>", "", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _risk_section(text: str) -> str:
    """The body of 'Item 1A. Risk Factors', up to the next item.

    The phrase also appears in the table of contents and in cross-references ("see Item 1A.
    Risk Factors"). The real heading is the one followed straight away by an intro sentence
    ("Risk Factors The following ...", "RISK FACTORS The risks and uncertainties ...").
    """
    next_item = re.compile(r"(?i)item\s*1b\.?|item\s*1c\.?|item\s*2\.?\s*[-–—:]?\s*properties")
    heading = re.search(
        r"(?i)(item\s*1a\.?\s*[-–—:]?\s*)?risk\s+factors\s*[.:–—-]?\s*"
        r"(?=the following|the risks|the risk factors|investing in|an investment in|you should|"
        r"our business|we are subject|in addition to|before (you )?(invest|deciding))",
        text,
    )
    if heading:
        end = next_item.search(text, heading.end())
        return text[heading.start(): end.start() if end else len(text)]

    # Fallback: the longest stretch from an "Item 1A. Risk Factors" mention to the next item heading
    best = ""
    for start in re.finditer(r"(?i)item\s*1a\.?\s*[-–—:]?\s*risk\s+factors", text):
        end = next_item.search(text, start.end())
        if end and end.start() - start.start() > len(best):
            best = text[start.start(): end.start()]
    return best


async def get_risk_factors(ticker: str) -> str:
    async with httpx.AsyncClient(headers=_headers(), timeout=30, follow_redirects=True) as client:
        tickers = (await client.get("https://www.sec.gov/files/company_tickers.json")).json()
        cik = next((row["cik_str"] for row in tickers.values() if row["ticker"] == ticker.upper()), None)
        if cik is None:
            return f"{ticker}: not found in SEC EDGAR"

        subs = (await client.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")).json()
        recent = subs["filings"]["recent"]
        idx = next((i for i, form in enumerate(recent["form"]) if form == "10-K"), None)
        if idx is None:
            return f"{ticker}: no recent 10-K filing found"

        accession = recent["accessionNumber"][idx].replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{recent['primaryDocument'][idx]}"
        doc = await client.get(url)
        doc.raise_for_status()

    section = _risk_section(_html_to_text(doc.text))
    if not section:
        return f"{ticker} 10-K ({recent['filingDate'][idx]}): risk factors section not found ({url})"
    return f"{ticker} 10-K filed {recent['filingDate'][idx]} ({url}) — risk factors:\n{section[:MAX_CHARS]}"
