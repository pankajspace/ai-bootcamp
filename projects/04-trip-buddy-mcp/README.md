# Trip Buddy (DB + RAG + Tools + Multi-Chain + MCP)

Extends Trip Buddy with the features from `trip_07_multi_chain.py` and `trip_08_full_agent.py` over the **Model Context Protocol (MCP)**:
- **3-table SQLite database** (`places`, `stays`, `costs`) with 10 destinations from Bengaluru (`db.py`)
- **13-tip ChromaDB RAG travel notebook** (`rag.py`)
- **Multi-chain pipeline** (`chains.py`): `DB → trip_cost_tool → Chain 1 (cost breakdown) → Chain 2 (GO / NOT YET decision)`
- **MCP Server over `stdio`** (`mcp_server.py`): Exposes `db_lookup`, `list_destinations`, `compute_trip_cost`, `retrieve_travel_tips`, and `evaluate_trip_plan`
- **MCP Client + ReAct Agent** (`mcp_client.py`): Spawns `mcp_server.py` over `stdio`, discovers tools via MCP `session.list_tools()`, retrieves RAG context, and executes tool calls via `session.call_tool()`
- **Gradio Chatbot** (`app.py`): Calls `mcp_client.run_agent()` for every user message

## Folder Structure

```text
projects/04-trip-buddy-mcp/
├── db.py              # 3-table SQLite database (places, stays, costs)
├── rag.py             # 13-tip ChromaDB travel notebook & embeddings
├── chains.py          # Multi-chain pipeline (Chain 1 breakdown -> Chain 2 GO/NOT YET)
├── mcp_server.py      # MCP Server over stdio exposing DB, RAG, cost, & multi-chain tools
├── mcp_client.py      # MCP Client + ReAct loop calling mcp_server.py over stdio
├── app.py             # Gradio ChatInterface calling mcp_client.run_agent()
├── requirements.txt   # Project dependencies
└── README.md          # Documentation
```

## How to Run

1. **Install dependencies:**
   ```bash
   pip install -r projects/04-trip-buddy-mcp/requirements.txt
   ```

2. **Test the MCP Client & Server handshake directly:**
   ```bash
   python projects/04-trip-buddy-mcp/mcp_client.py
   ```

3. **Run the Multi-Chain Pipeline (`trip_07` style):**
   ```bash
   python projects/04-trip-buddy-mcp/chains.py
   ```

4. **Launch the Gradio Chatbot (calls the MCP Client):**
   ```bash
   python projects/04-trip-buddy-mcp/app.py
   ```

