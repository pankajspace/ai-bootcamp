import os
import threading
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
# CLASS-BASED TOOLS PATTERN:
# Why use classes for tools?
#   1. Shared State: Keep state (DB connection, cache, inventory) in `self`
#      rather than using global variables.
#   2. Clean Organization: Group related tool methods together in one place.
#   3. Thread Safety: Agents can run tools concurrently across threads;
#      an instance lock (`threading.Lock`) prevents race conditions.
# ==============================================================================
class InventoryManager:
    """Manages an inventory store with shared state and thread-safe operations."""

    def __init__(self):
        # Shared state across tool methods
        self.lock = threading.Lock()
        self.inventory = {
            "PROD-101": {"name": "Laptop", "stock": 10, "price": 999.99},
            "PROD-102": {"name": "Wireless Mouse", "stock": 25, "price": 29.99},
            "PROD-103": {"name": "Mechanical Keyboard", "stock": 5, "price": 89.99},
        }

    @tool
    def check_stock(self, product_id: str) -> str:
        """
        Check the current available stock and price for a product.

        Args:
            product_id: The ID of the product (e.g., 'PROD-101', 'PROD-102', 'PROD-103').
        Returns:
            str: Product details and stock count, or not-found message.
        """
        with self.lock:
            product = self.inventory.get(product_id)
            if product:
                return (
                    f"{product['name']} ({product_id}): "
                    f"{product['stock']} units available at ${product['price']:.2f} each."
                )
            return f"Product '{product_id}' was not found in inventory."

    @tool
    def update_stock(self, product_id: str, quantity_to_add: int) -> str:
        """
        Add or remove stock for an existing product.

        Args:
            product_id: The ID of the product to update.
            quantity_to_add: The number of units to add (positive) or deduct (negative).
        Returns:
            str: Confirmation message with the new stock count.
        """
        with self.lock:
            product = self.inventory.get(product_id)
            if not product:
                return f"Product '{product_id}' was not found in inventory."

            new_stock = product["stock"] + quantity_to_add
            if new_stock < 0:
                return f"Cannot deduct {-quantity_to_add} units. Only {product['stock']} left in stock."

            product["stock"] = new_stock
            return f"Updated {product['name']} ({product_id}). New stock: {new_stock} units."


# 1. Instantiate the class to initialize the shared resource/state
inventory_manager = InventoryManager()

# 2. Pass bound instance methods to the Agent's tools list
agent = Agent(
    model=model,
    tools=[
        inventory_manager.check_stock,
        inventory_manager.update_stock,
    ],
    callback_handler=None,
)

# ------------------------------------------------------------------------------
# Test 1: Check existing stock
# ------------------------------------------------------------------------------
print("=== 1. Checking Stock ===")
response = agent("What is the current stock of PROD-101 and PROD-103?")
print(response)

# ------------------------------------------------------------------------------
# Test 2: Modify stock via tool and verify state update
# ------------------------------------------------------------------------------
print("\n=== 2. Updating Stock ===")
response = agent("We just received a shipment of 15 more units of PROD-103. Please update the stock.")
print(response)

# ------------------------------------------------------------------------------
# Test 3: Verify that subsequent calls reflect updated state
# ------------------------------------------------------------------------------
print("\n=== 3. Verifying Updated Stock ===")
response = agent("How many units of PROD-103 do we have now?")
print(response)

