"""
step07_lats_trim.py — Friday afternoon: cut tech exposure from 40% toward 30% with
Language Agent Tree Search (LATS) on the Claude Agent SDK.

Folder layout (the two skills live next to this script):
    step07_lats_trim.py
    .claude/skills/trade-evaluator/SKILL.md
    .claude/skills/trade-reflector/SKILL.md

Run it:
    pip install claude-agent-sdk anyio python-dotenv
    python step07_lats_trim.py          # 3 iterations, 2 children per expansion, depth ≤ 3
"""
import copy
import json
import math
import re
from pathlib import Path

import anyio
from dotenv import load_dotenv
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

load_dotenv()
MODEL = "claude-sonnet-4-6"
PROJECT_DIR = Path(__file__).resolve().parent   # where .claude/skills/ lives
MAX_LESSONS = 5                                 # keep the lesson list short


# ---------- Pure environment (mock) ----------
# In practice you would read real exposures and constraints from your own systems.
INITIAL_MARKET = {
    "tech_exposure_pct": 40.0,
    "target_pct": 30.0,
    "slippage_bps": [],
}


def apply_trim(state, positions, pct):
    """Apply a trim and return (new_state, observation_text). Never mutates `state`."""
    new = copy.deepcopy(state)                               # a private copy per branch
    impact = 5 + len(positions) * 2 + pct * 1.5              # toy slippage model, in bps
    new["slippage_bps"].append(impact)
    new["tech_exposure_pct"] -= pct * len(positions) * 0.4   # toy exposure model
    obs = (
        f"Trimmed {positions} by {pct}% each. Slippage {impact:.1f} bps. "
        f"New tech exposure: {new['tech_exposure_pct']:.1f}%."
    )
    return new, obs


def reached_target(state):
    return state["tech_exposure_pct"] <= state["target_pct"]


# ---------- LATS tree ----------
class Node:
    """One node = the portfolio AFTER this node's trade (the root = before any trade)."""

    def __init__(self, action_hint, state, parent=None):
        self.action_hint = action_hint
        self.state = state
        self.parent = parent
        self.children = []
        self.depth = 0 if parent is None else parent.depth + 1
        self.visits = 0          # N(s): how many scores have flowed through here
        self.value = 0.0         # V(s): running average of those scores, 0..1
        self.is_terminal = False
        self.proposal = None     # the trade that created this node (not for root)
        self.observation = None  # what the environment said about that trade

    def update(self, score):
        # V_new(s) = (V_old(s) * (N(s) - 1) + r) / N(s)   — a running average
        self.visits += 1
        self.value = ((self.value * (self.visits - 1)) + score) / self.visits


def uct(child, parent_visits, w=1.41):
    """UCT = how good it has looked so far + a bonus for being rarely tried."""
    if child.visits == 0:
        return float("inf")                    # never tried → try it first
    n_p = max(parent_visits, 1)
    return child.value + w * math.sqrt(math.log(n_p) / child.visits)


# ---------- 1. Selection ----------
def select(root, k_expand, max_depth):
    """Walk root → leaf via max-UCT until a node is not fully expanded or terminal."""
    node = root
    while (
        not node.is_terminal
        and node.depth < max_depth
        and len(node.children) >= k_expand
    ):
        node = max(node.children, key=lambda c: uct(c, node.visits))
    return node


# ---------- Talking to Claude through the Agent SDK ----------
async def _run_query(prompt, system_prompt, max_turns, skill=None):
    """Send one prompt; return all the text Claude wrote. `skill` loads one skill."""
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=system_prompt,
        max_turns=max_turns,
        cwd=str(PROJECT_DIR),                    # so .claude/skills/ is found
        skills=[skill] if skill else [],         # [] = no skills for this call
    )
    parts = []
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "\n".join(parts)


def parse_proposals(text):
    """Pull the JSON array out of the ```json block (or the first [...] found)."""
    m = (re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.S)
         or re.search(r"(\[.*\])", text, re.S))
    if not m:
        return []
    try:
        items = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []
    return [p for p in items
            if p.get("positions") and isinstance(p.get("percent_each"), (int, float))]


def parse_score(text):
    """'... SCORE: 7' → 7 (clamped to 1..10; 1 if missing)."""
    found = re.findall(r"SCORE:\s*(\d+)", text)
    return max(1, min(10, int(found[-1]))) if found else 1


def parse_lesson(text):
    """'LESSON: When X, do Y.' → 'When X, do Y.'"""
    found = re.findall(r"LESSON:\s*(When .+)", text)
    return found[-1].strip() if found else None


# ---------- 2. Expansion: K distinct trims in ONE call ----------
PROPOSE_SYSTEM_PROMPT = """You are a trade-construction agent reducing tech exposure.
You will be asked to propose K distinct candidate trims from a given market state.
The K candidates MUST differ materially from one another -- different ticker
selection, different slice size, or different concentration profile. Mode
collapse to identical or near-identical trims is a failure.
Output exactly one fenced JSON code block and no other text. The block must
contain a JSON array of K objects, each with these fields:
- positions: list of ticker symbols (strings, non-empty)
- percent_each: number, the % to trim from each named position
- rationale: short string explaining the candidate's distinct angle
Example:
```json
[
  {"positions": ["NVDA", "AMD"], "percent_each": 5.0,
   "rationale": "concentrated semis trim"},
  {"positions": ["AAPL", "MSFT", "GOOGL", "META"], "percent_each": 2.5,
   "rationale": "diversified mega-cap shave"}
]
```
"""


async def propose_k_trims(state, k_expand, lessons):
    lessons_block = ""
    if lessons:                                              # reflexion-style memory
        lessons_block = "\n\nLessons from prior attempts:\n- " + "\n- ".join(lessons)
    prompt = (
        f"Current tech exposure: {state['tech_exposure_pct']:.1f}%. "
        f"Target: {state['target_pct']}%. "
        f"K = {k_expand}. Propose {k_expand} materially distinct trim candidates."
        f"{lessons_block}"
    )
    text = await _run_query(prompt, system_prompt=PROPOSE_SYSTEM_PROMPT, max_turns=2)
    return parse_proposals(text)


# ---------- 3. Evaluation: a skill scores each new child ----------
def _trajectory_block(parent_state, proposal, child_state, observation):
    return (
        f"Trajectory:\n"
        f"- Starting tech exposure: {parent_state['tech_exposure_pct']:.1f}%\n"
        f"- Action: trim {proposal['positions']} by {proposal['percent_each']}% each\n"
        f"- Rationale: {proposal.get('rationale', '')}\n"
        f"- Observation: {observation}\n"
        f"- Resulting tech exposure: {child_state['tech_exposure_pct']:.1f}%\n"
        f"- Target: {child_state['target_pct']}%"
    )


EVAL_SYSTEM_PROMPT = """You are evaluating a single tech-trim trajectory.
Use the Skill tool to invoke `trade-evaluator` on the trajectory described.
End your response with a line of the exact form: SCORE: <integer 1-10>
"""


async def evaluate_proposal(parent_state, proposal, child_state, observation):
    prompt = _trajectory_block(parent_state, proposal, child_state, observation)
    return await _run_query(prompt + "\n\nEvaluate this trajectory.",
                            system_prompt=EVAL_SYSTEM_PROMPT, max_turns=4,
                            skill="trade-evaluator")


async def expand(node, k_expand, lessons):
    """Grow `node` by up to k children; return [(child, score 0..1), ...]."""
    new = []
    for p in (await propose_k_trims(node.state, k_expand, lessons))[:k_expand]:
        child_state, obs = apply_trim(node.state, p["positions"], p["percent_each"])
        child = Node(action_hint=p.get("rationale"), state=child_state, parent=node)
        child.proposal, child.observation = p, obs
        child.is_terminal = reached_target(child_state)
        verdict = await evaluate_proposal(node.state, p, child_state, obs)
        node.children.append(child)
        new.append((child, parse_score(verdict) / 10))     # 1..10 → 0.1..1.0
    return new


# ---------- 5. Backpropagation ----------
def backprop(leaf, score):
    """Walk leaf → root, updating value/visits at every ancestor (incl. root)."""
    node = leaf
    while node is not None:
        node.update(score)
        node = node.parent


# ---------- 6. Reflection ----------
REFLECT_SYSTEM_PROMPT = """You are reflecting on a failed tech-trim trajectory.
Use the Skill tool to invoke `trade-reflector` on the trajectory described, then
end your response with a line of the exact form:
LESSON: When <situation>, do <action>.
"""


async def reflect_on_failure(parent_state, proposal, child_state, observation):
    prompt = _trajectory_block(parent_state, proposal, child_state, observation)
    return await _run_query(
        prompt + "\n\nThe target was not reached. Reflect on this trajectory.",
        system_prompt=REFLECT_SYSTEM_PROMPT, max_turns=4, skill="trade-reflector")


# ---------- Printing helpers ----------
def name_of(node):
    if node.parent is None:
        return "root"
    return f"{name_of(node.parent)}/c{node.parent.children.index(node) + 1}"


def all_nodes(node):
    yield node
    for c in node.children:
        yield from all_nodes(c)


def print_tree(root):
    print("\n=== Final tree ===")
    for n in all_nodes(root):
        print(f"{'  ' * n.depth}{name_of(n)}: N={n.visits} V={n.value:.2f} "
              f"exposure={n.state['tech_exposure_pct']:.1f}%")


# ---------- The LATS loop ----------
async def lats_search(n_iterations=3, k_expand=2, max_depth=3):
    root = Node(action_hint=None, state=copy.deepcopy(INITIAL_MARKET))
    lessons = []                                             # long-term memory

    for it in range(1, n_iterations + 1):
        print(f"\n=== Iteration {it} ===")
        node = select(root, k_expand, max_depth)                          # 1 SELECT
        print(f"Selected: {name_of(node)} (depth={node.depth}, "
              f"N={node.visits}, V={node.value:.2f})")
        if node.depth >= max_depth:
            print("Reached max depth on this branch; skipping.")
            node.is_terminal = True
            continue

        new = await expand(node, k_expand, lessons)                       # 2 EXPAND + 3 EVALUATE
        for child, score in new:
            p = child.proposal
            print(f"[add ] {name_of(child)}: positions={p['positions']} "
                  f"pct={p['percent_each']}  score={score * 10:.1f}/10  "
                  f"exposure={child.state['tech_exposure_pct']:.1f}%")
        if not new:
            print("No valid proposals this round.")
            continue

        winners = [c for c, _ in new if c.is_terminal]                    # 4 SIMULATE (1 step)
        if winners:
            print(f"Target reached by {name_of(winners[0])}!")
            return winners[0]

        for child, score in new:                                          # 5 BACKPROPAGATE
            backprop(child, score)

        best_child, _ = max(new, key=lambda cs: cs[1])                    # 6 REFLECT
        verdict = await reflect_on_failure(node.state, best_child.proposal,
                                           best_child.state, best_child.observation)
        lesson = parse_lesson(verdict)
        if lesson and lesson not in lessons:                              # dedupe
            lessons.append(lesson)
            lessons = lessons[-MAX_LESSONS:]                              # cap at 5
            print(f"[lesson] {lesson}")

    print_tree(root)
    leaves = [n for n in all_nodes(root) if n.parent and not n.children]
    best = max(leaves, key=lambda n: (n.value, -n.state["tech_exposure_pct"]))
    print(f"Best leaf: {name_of(best)}  V={best.value:.2f}  "
          f"exposure={best.state['tech_exposure_pct']:.1f}%")
    return best


if __name__ == "__main__":
    anyio.run(lats_search, 3, 2, 3)          # n_iterations, k_expand, max_depth
