"""
step05_reflexion_shape.py — Thursday afternoon: the SHAPE of a reflexion loop.
Stand-in functions so it runs offline:  python step05_reflexion_shape.py
"""
MAX_TRIALS = 3
memory: list[str] = []                        # long-term memory: lessons, not logs


def actor(task: str, lessons: list[str]) -> dict:
    """Does the screening. Real life: a ReAct agent with the lessons in its prompt."""
    knows = any("negative working capital" in l for l in lessons)
    return {"task": task, "flagged_wc": not knows}


def evaluator(trajectory: dict) -> bool:
    """Reward: did we get it right? (rubric, labelled examples or another model)"""
    return not trajectory["flagged_wc"]


def reflector(trajectory: dict, memory: list[str]) -> str:
    """Writes a short, human-readable lesson about the failure."""
    return ("I treated negative working capital as a red flag. For retailers and "
            "platforms with strong supplier terms it is often a strength; "
            "check the industry first.")


for trial in range(1, MAX_TRIALS + 1):
    trajectory = actor("Screen ShopCo for the buy list", lessons=memory)   # act
    passed = evaluator(trajectory)                                         # score
    print(f"Trial {trial}: {'PASS' if passed else 'FAIL'}  (lessons in memory: {len(memory)})")
    if passed:
        break
    memory.append(reflector(trajectory, memory))                          # learn
