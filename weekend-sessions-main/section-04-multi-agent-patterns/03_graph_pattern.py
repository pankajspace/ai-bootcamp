"""Section 4 · Notebook 3 — Graph Pattern: Order Processing (Amazon Bedrock edition)

Orders follow explicit, auditable paths:

```
                    ┌─ HIGH_VALUE ──→ Manual Review ─┐
Risk Analyzer ──────┼─ SUSPICIOUS ──→ Fraud Check ───┼──→ Inventory ──┬─ IN_STOCK ─────→ Shipping
                    └─ LOW_RISK ─────────────────────┘               └─ OUT_OF_STOCK ─→ Refund
```

Unlike a swarm, the routing lives in code. Every path is visible and can be audited.

Requirements:
    pip install -r requirements.txt

Prerequisites:
    AWS credentials configured with access to Amazon Bedrock models.

Run:
    python 03_graph_pattern.py
"""

import os
import re
from dotenv import find_dotenv, load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent import GraphBuilder

load_dotenv(find_dotenv())

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)


# -----------------------------------------------------------------------------
# Specialised agents
# -----------------------------------------------------------------------------
# The two "decision" agents end their answer with a fixed line
# (RISK_CATEGORY: ..., STOCK_STATUS: ...). The routing functions read only that
# line, so an explanation that merely mentions another category cannot send
# the order down the wrong path.

risk_analyzer = Agent(
    name="risk_analyzer",
    model=model,
    callback_handler=None,
    system_prompt="""Analyze the order's risk level and pick exactly ONE category:
- HIGH_VALUE: orders over $1,000
- SUSPICIOUS: mismatched billing/shipping country, brand-new account with a large order, or known fraud patterns
- LOW_RISK: regular orders from trusted customers
If more than one applies, SUSPICIOUS wins over HIGH_VALUE.
Give a one-paragraph explanation, then finish with a final line in exactly this format:
RISK_CATEGORY: <HIGH_VALUE|SUSPICIOUS|LOW_RISK>""",
)

manual_review_agent = Agent(
    name="manual_review_agent",
    model=model,
    callback_handler=None,
    system_prompt="Review high-value orders. Verify customer identity, check order history, and approve or flag for further review.",
)

fraud_detection_agent = Agent(
    name="fraud_detection_agent",
    model=model,
    callback_handler=None,
    system_prompt="Run fraud detection on suspicious orders: known fraud patterns, velocity checks, and device fingerprinting. Decide whether to proceed.",
)

inventory_agent = Agent(
    name="inventory_agent",
    model=model,
    callback_handler=None,
    system_prompt="""Check inventory for the order items. Assume laptops, books and phones are in stock and
anything described as 'limited edition' or 'pre-order' is out of stock.
Explain briefly, then finish with a final line in exactly this format:
STOCK_STATUS: <IN_STOCK|OUT_OF_STOCK>""",
)

shipping_agent = Agent(
    name="shipping_agent",
    model=model,
    callback_handler=None,
    system_prompt="Generate a shipping label and process the shipment. Confirm a tracking number and estimated delivery date.",
)

refund_agent = Agent(
    name="refund_agent",
    model=model,
    callback_handler=None,
    system_prompt="Process a refund for out-of-stock items. Notify the customer and initiate the payment reversal.",
)


# -----------------------------------------------------------------------------
# Routing conditions
# -----------------------------------------------------------------------------
# Each condition reads the previous node's output and returns True/False.
# The logic is plain Python — not hidden inside model reasoning.

def decision(state, node_id: str, label: str) -> str:
    """Return the value of the final 'LABEL: VALUE' line written by a node."""
    text = str(state.results.get(node_id, ""))
    matches = re.findall(rf"{label}\s*:\s*([A-Z_]+)", text.upper())
    return matches[-1] if matches else ""


def is_high_value(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "HIGH_VALUE"


def is_suspicious(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "SUSPICIOUS"


def is_low_risk(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "LOW_RISK"


def is_in_stock(state):
    return decision(state, "inventory_check", "STOCK_STATUS") == "IN_STOCK"


def is_out_of_stock(state):
    return decision(state, "inventory_check", "STOCK_STATUS") == "OUT_OF_STOCK"


# -----------------------------------------------------------------------------
# Build the graph
# -----------------------------------------------------------------------------

builder = GraphBuilder()

# Nodes
builder.add_node(risk_analyzer, "risk_analysis")
builder.add_node(manual_review_agent, "manual_review")
builder.add_node(fraud_detection_agent, "fraud_check")
builder.add_node(inventory_agent, "inventory_check")
builder.add_node(shipping_agent, "shipping")
builder.add_node(refund_agent, "refund")

# Conditional edges out of risk analysis
builder.add_edge("risk_analysis", "manual_review", condition=is_high_value)
builder.add_edge("risk_analysis", "fraud_check", condition=is_suspicious)
builder.add_edge("risk_analysis", "inventory_check", condition=is_low_risk)

# Review / fraud check → inventory
builder.add_edge("manual_review", "inventory_check")
builder.add_edge("fraud_check", "inventory_check")

# Inventory → ship or refund
builder.add_edge("inventory_check", "shipping", condition=is_in_stock)
builder.add_edge("inventory_check", "refund", condition=is_out_of_stock)

builder.set_entry_point("risk_analysis")
graph = builder.build()


def show_path(result):
    path = " → ".join(node.node_id for node in result.execution_order)
    print(f"Status: {result.status}\nPath:   {path}")
    last = result.execution_order[-1].node_id
    print(f"\nFinal step ({last}):\n{result.results[last].result}")


def main():
    print(f"Using {MODEL_ID} in {REGION}")

    # Process orders — each one takes a different path
    # High value → manual review → inventory → shipping
    print("\n" + "=" * 80)
    print("Order 1: High value order")
    print("=" * 80)
    result1 = graph("Order #12345: $1,500 laptop from an existing customer with 3 previous orders; billing and shipping address match")
    show_path(result1)

    # Low risk → inventory → shipping
    print("\n" + "=" * 80)
    print("Order 2: Low risk order")
    print("=" * 80)
    result2 = graph("Order #67890: $45 book from a returning customer with 50+ previous orders")
    show_path(result2)

    # Suspicious → fraud check → inventory → refund (limited edition is out of stock)
    print("\n" + "=" * 80)
    print("Order 3: Suspicious order with out-of-stock item")
    print("=" * 80)
    result3 = graph(
        "Order #11111: $800 limited edition headphones, account created 5 minutes ago, "
        "shipping to a different country than the billing address"
    )
    show_path(result3)


if __name__ == "__main__":
    main()

