"""
Section 12 lab — reliability patterns every production agent needs
==================================================================
Small, framework-free building blocks you wrap around tool calls:

    with_retries               a transient failure? wait a bit longer each time, then retry
    call_with_timeout          never wait forever on one call
    IdempotentExecutor         an order is placed ONCE, even if the request is retried
    CircuitBreaker             stop hammering a service that is down; probe again later
    price_with_fallbacks       primary → backup → recent cache → "insufficient evidence"
    check_ticker               least privilege: only tickers in the approved universe
    RunBudget                  stop on step / token / dollar limits, or when progress stalls
    run_batch_with_checkpoint  an overnight batch that resumes after a crash
    fan_out                    many names concurrently, at most N at a time
    loop_tokens                why long agent loops get expensive

How to run
----------
No installs, no API key:   python step07_reliability.py
The demo at the bottom runs every pattern against a deliberately flaky fake API.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from pathlib import Path

TRANSIENT = (TimeoutError, ConnectionError)       # worth retrying; bad input is NOT


def with_retries(fn, *args, attempts=3, base_delay=0.5, max_delay=8.0,
                 sleep=time.sleep, rng=random.random, on_retry=None, **kwargs):
    """Exponential backoff with full jitter: wait random(0, base × 2^(attempt−1)) seconds."""
    for attempt in range(1, attempts + 1):
        try:
            return fn(*args, **kwargs)
        except TRANSIENT as exc:
            if attempt == attempts:
                raise                              # out of attempts: let the caller decide
            delay = rng() * min(max_delay, base_delay * 2 ** (attempt - 1))
            if on_retry:
                on_retry(attempt, exc, delay)
            sleep(delay)

_POOL = ThreadPoolExecutor(max_workers=8)


def call_with_timeout(fn, seconds: float, *args, **kwargs):
    """Give up waiting after `seconds`. (Prefer a client's own timeout= option when it has one.)"""
    future = _POOL.submit(fn, *args, **kwargs)
    try:
        return future.result(timeout=seconds)
    except FutureTimeout:
        raise TimeoutError(f"{getattr(fn, '__name__', 'call')} took longer than {seconds}s") from None

def order_key(account: str, ticker: str, side: str, qty: int, client_ref: str) -> str:
    """Same order details + same client reference → same key, however many retries happen."""
    raw = json.dumps([account, ticker, side, qty, client_ref])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class IdempotentExecutor:
    """Remembers keys it has executed. In production: a database table with a UNIQUE key."""

    def __init__(self):
        self._done: dict[str, dict] = {}

    def submit(self, key: str, action, *args) -> dict:
        if key in self._done:
            return {**self._done[key], "duplicate": True}     # replay the first result
        result = action(*args)
        self._done[key] = result
        return {**result, "duplicate": False}

class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    """CLOSED (normal) → OPEN after N failures (fail fast) → HALF_OPEN after a pause (one probe)."""

    def __init__(self, failure_threshold: int = 3, reset_after: float = 30.0, clock=time.monotonic):
        self.failure_threshold, self.reset_after, self.clock = failure_threshold, reset_after, clock
        self.state, self.failures, self.opened_at = "CLOSED", 0, 0.0

    def call(self, fn, *args, **kwargs):
        if self.state == "OPEN":
            if self.clock() - self.opened_at < self.reset_after:
                raise CircuitOpenError("circuit open: not calling the service")
            self.state = "HALF_OPEN"                          # let ONE request test the water
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.state == "HALF_OPEN" or self.failures >= self.failure_threshold:
                self.state, self.opened_at = "OPEN", self.clock()
            raise
        self.state, self.failures = "CLOSED", 0
        return result

def price_with_fallbacks(ticker: str, primary, backup, cache: dict, max_age_s: float = 900, clock=time.time) -> dict:
    """Degrade step by step, and always SAY which rung of the ladder answered."""
    for source, fn in (("primary", primary), ("backup", backup)):
        try:
            price = fn(ticker)
            cache[ticker] = (price, clock())
            return {"ticker": ticker, "price": price, "source": source}
        except Exception:
            continue
    if ticker in cache and clock() - cache[ticker][1] <= max_age_s:
        price, at = cache[ticker]
        return {"ticker": ticker, "price": price, "source": f"cache, {clock() - at:.0f}s old"}
    return {"ticker": ticker, "price": None, "source": "none", "status": "INSUFFICIENT_EVIDENCE"}

RESEARCH_UNIVERSE = {"ACME", "BOLT", "CRUX", "DYNA", "EVRO"}
TICKER_RE = re.compile(r"^[A-Z]{1,5}$")


def check_ticker(raw: str) -> str:
    """Validate BEFORE any tool runs. The model's arguments are untrusted input."""
    t = raw.strip().upper()
    if not TICKER_RE.match(t):
        raise ValueError(f"not a ticker: {raw!r}")
    if t not in RESEARCH_UNIVERSE:
        raise PermissionError(f"{t} is outside the approved research universe")
    return t

@dataclass
class RunBudget:
    max_steps: int = 8
    max_tokens: int = 50_000
    max_usd: float = 0.50
    max_repeats: int = 2                   # same tool + same arguments more than this = stuck
    steps: int = 0
    tokens: int = 0
    usd: float = 0.0
    seen: Counter = field(default_factory=Counter)

    def charge(self, tool: str, args: dict, tokens: int, usd: float) -> str | None:
        """Record one step. Returns a stop reason, or None to keep going."""
        self.steps, self.tokens, self.usd = self.steps + 1, self.tokens + tokens, self.usd + usd
        fingerprint = tool + json.dumps(args, sort_keys=True)
        self.seen[fingerprint] += 1
        if self.seen[fingerprint] > self.max_repeats:
            return f"no progress: {tool}{args} called {self.seen[fingerprint]} times"
        if self.steps > self.max_steps:
            return f"step limit ({self.max_steps})"
        if self.tokens > self.max_tokens:
            return f"token budget ({self.max_tokens:,})"
        if self.usd > self.max_usd:
            return f"cost budget (${self.max_usd:.2f})"
        return None

def run_batch_with_checkpoint(items: list[str], work, path: Path) -> dict:
    """Append each finished item to a JSONL file; on restart, skip what's already there."""
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            done[rec["item"]] = rec
    with path.open("a", encoding="utf-8") as f:
        for item in items:
            if item in done:
                continue
            rec = {"item": item, **work(item)}
            f.write(json.dumps(rec) + "\n")
            f.flush()                                          # on disk before moving on
            done[item] = rec
    return done

async def fan_out(items, worker, limit: int = 5):
    """Run worker(item) for every item concurrently, but never more than `limit` at once."""
    gate = asyncio.Semaphore(limit)

    async def one(item):
        async with gate:
            return await worker(item)
    return await asyncio.gather(*(one(i) for i in items), return_exceptions=True)

def loop_tokens(iterations: int, system: int = 600, question: int = 50,
                per_reply: int = 120, per_tool_result: int = 400) -> tuple[int, int]:
    """Input tokens grow EVERY step, because the whole conversation is re-sent each time."""
    context, total_in = system + question, 0
    for _ in range(iterations):
        total_in += context                     # this step re-reads everything so far
        context += per_reply + per_tool_result  # …and adds its own reply + tool result
    return total_in, iterations * per_reply

if __name__ == "__main__":
    rng = random.Random(3)

    def flaky_quote(ticker):
        if rng.random() < 0.5:
            raise ConnectionError("503 from market-data API")
        return 41.20

    print("1) retries with backoff")
    price = with_retries(flaky_quote, "ACME", attempts=4, sleep=lambda s: None, rng=rng.random,
                         on_retry=lambda a, e, d: print(f"   attempt {a} failed ({e}); waiting {d:.2f}s"))
    print(f"   got {price}")

    print("2) timeout")
    try:
        call_with_timeout(time.sleep, 0.2, 1.0)
    except TimeoutError as e:
        print(f"   {e}")

    print("3) idempotent order: the client retries after a network blip")
    ex = IdempotentExecutor()
    key = order_key("FUND-7", "ACME", "BUY", 500, "ref-0091")
    send = lambda: {"order_id": f"ORD-{rng.randint(1000, 9999)}", "status": "FILLED"}
    print("  ", ex.submit(key, send))
    print("  ", ex.submit(key, send), "← no second order")

    print("4) circuit breaker on a dead service")
    now = [0.0]
    cb = CircuitBreaker(failure_threshold=3, reset_after=30, clock=lambda: now[0])

    service_up = [False]

    def market_data(_):
        if not service_up[0]:
            raise ConnectionError("down")
        return 41.20
    for t, up in ((0, False), (1, False), (2, False), (3, False), (40, False), (80, True)):
        now[0], service_up[0] = t, up
        try:
            outcome = f"ok {cb.call(market_data, 'ACME')}"
        except Exception as e:
            outcome = type(e).__name__
        print(f"   t={t:>2}s  service {'up  ' if up else 'down'} → {outcome:<17} state={cb.state}")

    def dead(_):
        raise ConnectionError("down")

    print("5) fallback ladder")
    cache = {"BOLT": (12.70, time.time() - 120)}
    print("  ", price_with_fallbacks("BOLT", dead, dead, cache))
    print("  ", price_with_fallbacks("CRUX", dead, dead, cache))

    print("6) allow-list")
    for t in ("acme", "TSLA", "ACME; DROP TABLE"):
        try:
            print(f"   {t!r} → {check_ticker(t)}")
        except (ValueError, PermissionError) as e:
            print(f"   {t!r} → {type(e).__name__}: {e}")

    print("7) budget + no-progress detector")
    b = RunBudget()
    for step in range(1, 6):
        reason = b.charge("get_news", {"ticker": "ACME"}, tokens=3000, usd=0.02)
        print(f"   step {step}: {reason or 'ok'}")
        if reason:
            break

    print("8) checkpointed batch: crash after 3 names, then resume")
    path = Path(__file__).with_name("batch_checkpoint.jsonl")
    path.unlink(missing_ok=True)
    names, calls = ["ACME", "BOLT", "CRUX", "DYNA", "EVRO"], []

    def work(name):
        calls.append(name)
        if len(calls) == 4 and name == "DYNA":
            raise RuntimeError("worker crashed")
        return {"verdict": "NEUTRAL"}
    try:
        run_batch_with_checkpoint(names, work, path)
    except RuntimeError as e:
        print(f"   first run: {e} after {calls[:3]}")
    done = run_batch_with_checkpoint(names, work, path)
    print(f"   second run processed {calls[4:]}, total done = {len(done)}")
    path.unlink()

    print("9) fan-out with a limit of 5")
    active, peak = [0], [0]

    async def analyse(name):
        active[0] += 1
        peak[0] = max(peak[0], active[0])
        await asyncio.sleep(0.05)
        active[0] -= 1
        return name
    t0 = time.perf_counter()
    out = asyncio.run(fan_out([f"N{i:03d}" for i in range(20)], analyse, limit=5))
    print(f"   {len(out)} names in {time.perf_counter() - t0:.2f}s, never more than {peak[0]} at once")

    print("10) why long loops get expensive (input tokens re-read every step)")
    for n in (2, 4, 6, 8):
        tin, tout = loop_tokens(n)
        print(f"   {n} steps → {tin:>6,} input tokens, {tout:>5,} output tokens")
