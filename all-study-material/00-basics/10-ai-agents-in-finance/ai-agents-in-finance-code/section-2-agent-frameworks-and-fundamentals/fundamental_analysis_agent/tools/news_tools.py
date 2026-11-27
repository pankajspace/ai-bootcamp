"""tools/news_tools.py: recent headlines from yfinance and a keyword sentiment score.

The notes print these tools as "key parts" with illustrative keyword lists; the elided pieces
are filled in below and marked "Filled in".
"""
import json
import re
from datetime import datetime

import yfinance as yf
from agents import function_tool

from fundamental_analysis_agent.tools.financial_tools import _cache

BULLISH_SIGNALS = ["beat", "beats", "record", "surge", "upgrade", "growth", "strong",
                   "raises", "buyback", "outperform", "jumps", "rally", "gains", "boosts"]
BEARISH_SIGNALS = ["miss", "misses", "fall", "falls", "drop", "decline", "cut", "downgrade",
                   "lawsuit", "probe", "investigation", "antitrust", "recall", "fine", "weak", "loss"]


def _score_headline(text: str):
    words = re.findall(r"[a-z]+", text.lower())          # "Apple beats estimates!" → ["apple", "beats", "estimates"]
    bull = sum(w in BULLISH_SIGNALS for w in words)       # True counts as 1
    bear = sum(w in BEARISH_SIGNALS for w in words)
    if bull + bear == 0:
        return "neutral", 0.0                             # no signal words at all
    net = (bull - bear) / (bull + bear)                   # always between -1 and +1
    if net > 0.15:  return "bullish", round(net, 2)
    if net < -0.15: return "bearish", round(net, 2)
    return "neutral", round(net, 2)


def _format_timestamp(value) -> str:
    """Filled in: ISO text ('2025-10-28T14:05:00Z') or Unix seconds → 'YYYY-MM-DD HH:MM'."""
    if not value:
        return "unknown"
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(value)


def _first_sentence(text: str | None) -> str | None:
    """Filled in: the first sentence of an article summary."""
    if not text:
        return None
    return re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]


def _is_relevant(item: dict, ticker: str, short_name: str) -> bool:
    """Filled in: keep articles whose title or summary mentions the ticker or the company name."""
    content = item.get("content") or {}
    text = f"{content.get('title', '')} {content.get('summary', '')}".lower()
    name_word = short_name.split()[0].lower().strip(",.") if short_name else ""
    return ticker.lower() in text or (bool(name_word) and name_word in text)


@function_tool
def search_recent_news(ticker: str, max_results: int) -> str:
    """
    Fetch recent news articles and headlines for a given stock ticker.
    Uses yfinance to retrieve the latest news. Returns titles, publishers,
    publication dates, and article links. This data feeds into sentiment
    analysis and helps identify current market narratives around the stock.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
        max_results: Maximum number of news articles to retrieve (1-20).
    """
    try:
        max_results = max(1, min(int(max_results), 20))           # ① clamp to 1..20
        _key = ("search_recent_news", ticker.upper(), max_results)
        _hit = _cache.get(_key)
        if _hit is not None:
            return _hit

        stock      = yf.Ticker(ticker.upper())
        short_name = stock.info.get("shortName", "")
        raw_news   = stock.news or []                              # ② list of news items, or []
        relevant   = [n for n in raw_news if _is_relevant(n, ticker, short_name)]
        raw_news   = relevant or raw_news                          #    nothing matched → keep everything

        articles = []
        for item in raw_news:
            if len(articles) >= max_results:
                break
            content   = item.get("content") or {}                 # ③ safe digging into nested dicts
            title     = content.get("title") or "No title"
            publisher = (content.get("provider") or {}).get("displayName") or "Unknown"
            pub_time  = _format_timestamp(content.get("pubDate"))
            link      = (content.get("clickThroughUrl") or {}).get("url") or ""
            first_sentence = _first_sentence(content.get("summary"))
            scoring_text = f"{title}. {first_sentence or ''}"
            label, score = _score_headline(scoring_text)          # ④ quick keyword score
            articles.append({
                "title": title, "publisher": publisher, "published_at": pub_time,
                "sentiment": label, "sentiment_score": score,
                "url": link, "first_sentence": first_sentence,
            })

        # Filled in: count labels, wrap in a dict, json.dumps, cache, return
        summary = {lab: sum(a["sentiment"] == lab for a in articles) for lab in ("bullish", "neutral", "bearish")}
        output = json.dumps({"ticker": ticker.upper(), "company_name": short_name,
                             "article_count": len(articles), "sentiment_summary": summary,
                             "articles": articles}, indent=2, default=str)
        _cache.store(_key, output)
        return output
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


@function_tool
def analyze_sentiment(news_json: str) -> str:
    """
    Perform a structured sentiment analysis on a set of news articles.
    Takes the JSON output from search_recent_news and produces a detailed
    sentiment report: an aggregate sentiment score, key bullish and bearish
    themes extracted from headlines, and an overall market narrative summary.

    Args:
        news_json: JSON string output from search_recent_news containing
                   a list of articles with titles and sentiment scores.
    """
    ticker = "UNKNOWN"
    try:
        data = json.loads(news_json)                          # tool 1's text → dict again
        articles = data.get("articles", [])
        ticker = data.get("ticker", "UNKNOWN")

        scores = [a.get("sentiment_score", 0.0) for a in articles]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        all_titles = " ".join(a.get("title", "") for a in articles).lower()
        bullish_themes = [w for w in BULLISH_SIGNALS if w in all_titles][:5]
        bearish_themes = [w for w in BEARISH_SIGNALS if w in all_titles][:5]
        # Filled in: top_bullish / top_bearish = the most extreme headlines
        by_score = sorted(articles, key=lambda a: a.get("sentiment_score", 0.0))
        top_bullish = [a for a in reversed(by_score) if a.get("sentiment_score", 0.0) > 0][:3]
        top_bearish = [a for a in by_score if a.get("sentiment_score", 0.0) < 0][:3]

        if avg_score > 0.40:
            overall = "strongly bullish"
        elif avg_score > 0.15:
            overall = "bullish"
        elif avg_score < -0.40:
            overall = "strongly bearish"
        elif avg_score < -0.15:
            overall = "bearish"
        else:
            overall = "neutral"

        high_risk_keywords = ["fraud", "investigation", "antitrust", "lawsuit",
                              "recall", "scandal", "penalty", "fine"]
        risk_flags = [
            a["title"] for a in articles
            if any(kw in a.get("title", "").lower() for kw in high_risk_keywords)
        ]

        result = {
            "ticker": ticker,
            "overall_sentiment": overall,
            "aggregate_score": avg_score,
            "interpretation": f"Score of {avg_score:.3f} on a scale of -1 (very bearish) to +1 (very bullish)",
            "article_count": len(articles),
            "sentiment_breakdown": data.get("sentiment_summary", {}),
            "key_bullish_themes": bullish_themes,
            "key_bearish_themes": bearish_themes,
            "top_bullish_headlines": [h["title"] for h in top_bullish],
            "top_bearish_headlines": [h["title"] for h in top_bearish],
            "risk_flags": risk_flags,
            "risk_flag_count": len(risk_flags),
            "all_articles": [
                {"title": a["title"], "publisher": a["publisher"], "published_at": a["published_at"],
                 "sentiment": a["sentiment"], "url": a["url"], "first_sentence": a.get("first_sentence")}
                for a in articles
            ],
        }
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})
