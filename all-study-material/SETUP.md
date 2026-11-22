# ⚡ Using `uv` for a Project Folder

Run all commands from inside the project folder; `uv` creates a `.venv` there.

```bash
# Install uv (one time)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux (or: brew install uv)

# Change to the project folder (from all-study-material/)
cd 00-basics/01-langchain-foundation

# If the folder has pyproject.toml, install dependencies
uv sync

# Else if the folder has only requirements.txt
## Create the virtual environment
uv venv
## Install dependencies from requirements.txt
uv pip install -r requirements.txt

# Run scripts (no activation needed; picks up the local .venv)
uv run python 01_hello_world_env_setup.py   # or: uv run 01_hello_world_env_setup.py

# Manage packages (pyproject.toml folders)
uv add <package>
uv remove <package>

# Manage packages (requirements.txt-only folders)
uv pip install <package>
uv pip uninstall <package>
```
