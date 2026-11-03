import asyncio
import os
import time
from dotenv import load_dotenv

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# Load environment variables from the .env file
load_dotenv()

# Replace 'model_id' with the ID of the model you want to use
model_id = os.getenv('AWS_BEDROCK_MODEL_ID')

# Initialize the Bedrock model with the specified model ID
model = BedrockModel(model_id=model_id)

# ==============================================================================
# ASYNC TOOL DEFINITION:
# 1. Use `@tool` decorator.
# 2. Define the function with `async def`.
# 3. Use non-blocking operations like `await asyncio.sleep(...)` or `httpx.AsyncClient`.
#
# Benefit: If the agent needs to check multiple sources (e.g. 3 warehouses),
# Strands executes the async tool calls concurrently instead of sequentially!
# ==============================================================================
@tool
async def check_warehouse_inventory(warehouse_name: str, item_name: str) -> dict:
    """
    Check item stock level in a specific warehouse.
    Simulates a network API call taking 1.5 seconds.

    Args:
        warehouse_name: Name of the warehouse (e.g., 'New York', 'London', 'Tokyo').
        item_name: The product to check (e.g., 'laptop').
    Returns:
        dict: Warehouse stock information.
    """
    print(f"  [Tool] Fetching stock for '{item_name}' in warehouse '{warehouse_name}'...")
    # Simulate network latency (1.5 seconds)
    await asyncio.sleep(1.5)

    stock_database = {
        "New York": {"laptop": 15, "phone": 40},
        "London": {"laptop": 25, "phone": 10},
        "Tokyo": {"laptop": 30, "phone": 50},
    }

    count = stock_database.get(warehouse_name, {}).get(item_name.lower(), 0)
    return {"warehouse": warehouse_name, "item": item_name, "available_stock": count}


# Create the agent with our async tool
agent = Agent(
    model=model,
    tools=[check_warehouse_inventory],
    callback_handler=None
)


async def main():
    print("=== Asking Agent to Check All 3 Warehouses Concurrently ===\n")
    start_time = time.time()

    # When using async tools, use `await agent.invoke_async(...)`
    prompt = (
        "Check how many laptops we have in stock across all three warehouses: "
        "New York, London, and Tokyo. What is the total?"
    )
    
    response = await agent.invoke_async(prompt)
    elapsed_time = time.time() - start_time

    print("\n=== Agent Response ===")
    print(response)

    print(f"\nCompleted in: {elapsed_time:.2f} seconds")
    print(
        "(Notice: If executed sequentially, 3 calls x 1.5s = ~4.5s. "
        "With async tools, calls run concurrently in ~1.5s + LLM inference time!)"
    )


if __name__ == "__main__":
    asyncio.run(main())

