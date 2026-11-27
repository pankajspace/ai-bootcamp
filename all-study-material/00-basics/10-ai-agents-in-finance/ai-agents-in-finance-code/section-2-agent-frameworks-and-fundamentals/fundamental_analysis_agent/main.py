"""Command-line entry point: run the full fundamental analysis pipeline.

Run from the folder ABOVE fundamental_analysis_agent/:
    python -m fundamental_analysis_agent.main AAPL                        # one stock
    python -m fundamental_analysis_agent.main MSFT --stream               # watch it type
    python -m fundamental_analysis_agent.main AAPL --trace --verbose --log-dir logs/   # see everything
    python -m fundamental_analysis_agent.main AAPL --watchlist GOOGL TSLA NVDA MSFT    # several stocks

The notes print analyze_ticker's "key parts"; the streaming / tracing / logging options they
elide are filled in here with the Agents SDK's streamed run events.
"""
import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # OPENAI_API_KEY from .env, before the SDK creates its client

from agents import Runner  # noqa: E402
from openai.types.responses import ResponseTextDeltaEvent  # noqa: E402

from fundamental_analysis_agent.agents.orchestrator import orchestrator  # noqa: E402


async def analyze_ticker(
    ticker: str,
    stream: bool = False,          # print tokens as they arrive
    verbose: bool = False,         # print each sub-agent's output afterwards
    trace: bool = False,           # print the CALL / OUTPUT sequence
    log_dir: Path | None = None,   # save each sub-agent's output to its own .txt file
) -> str:
    """Run the full fundamental analysis pipeline for a single ticker."""
    ticker = ticker.upper().strip()                      # " aapl " → "AAPL"
    prompt = (
        f"Perform a complete fundamental analysis for the stock ticker: {ticker}\n"
        f"Follow the full workflow: gather financial data, news sentiment, and risk "
        f"assessment, then run valuation, and finally produce the investment brief."
    )

    result = Runner.run_streamed(orchestrator, input=prompt)
    call_names: dict[str, str] = {}                      # call_id → sub-agent tool name
    sub_outputs: list[tuple[str, str]] = []              # (tool name, its output), in order

    async for event in result.stream_events():
        if stream and event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
        elif event.type == "run_item_stream_event":
            item = event.item
            if item.type == "tool_call_item":
                raw = item.raw_item
                call_id, name = getattr(raw, "call_id", None), getattr(raw, "name", "tool")
                call_names[call_id] = name
                if trace:
                    print(f"\n[CALL]   {name}({getattr(raw, 'arguments', '')})")
            elif item.type == "tool_call_output_item":
                raw = item.raw_item
                call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None)
                name = call_names.get(call_id, "tool")
                sub_outputs.append((name, str(item.output)))
                if trace:
                    print(f"[OUTPUT] {name}: {len(str(item.output))} characters")
    if stream:
        print()

    if verbose:
        for name, text in sub_outputs:
            print(f"\n{'=' * 30} {name} {'=' * 30}\n{text}")
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        for i, (name, text) in enumerate(sub_outputs, 1):
            (log_dir / f"{ticker}_{i:02d}_{name}.txt").write_text(text)
        (log_dir / f"{ticker}_final_report.txt").write_text(str(result.final_output))

    return result.final_output


def main() -> None:
    ap = argparse.ArgumentParser(description="Fundamental analysis of one or more stocks.")
    ap.add_argument("ticker", help="stock ticker, e.g. AAPL")
    ap.add_argument("--stream", action="store_true", help="print the output word by word")
    ap.add_argument("--verbose", action="store_true", help="print each specialist's full report")
    ap.add_argument("--trace", action="store_true", help="print every CALL and OUTPUT in order")
    ap.add_argument("--log-dir", type=Path, help="save one .txt file per agent here")
    ap.add_argument("--watchlist", nargs="*", default=[], help="extra tickers to analyse in one go")
    args = ap.parse_args()

    for ticker in [args.ticker, *args.watchlist]:
        report = asyncio.run(analyze_ticker(ticker, args.stream, args.verbose, args.trace, args.log_dir))
        if not args.stream:
            print(report)
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()
