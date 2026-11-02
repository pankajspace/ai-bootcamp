# Setup Guide: Run Section 1 on Your Computer

No coding experience needed. Follow the steps in order and don't skip any. It takes about 20 minutes.

Commands are shown for **Windows** first, with **Mac** next to them when they differ.

---

## Step 1: Install VS Code

1. Go to https://code.visualstudio.com and click **Download**.
2. Run the installer and click Next through everything. Keep the default options.
3. Open VS Code once to confirm it starts.

---

## Step 2: Install Python

1. Go to https://www.python.org/downloads and download **Python 3.12 or 3.13**. (3.11 is the minimum this course needs.)
2. Run the installer.
   - **Windows:** on the very first screen, tick **"Add python.exe to PATH"** *before* clicking Install. This is the step people miss.
   - **Mac:** just click through.
3. Check it worked. Open VS Code's terminal (Step 5) and type:

| Windows | Mac |
| :--- | :--- |
| `python --version` | `python3 --version` |

4. You should see something like `Python 3.13.x`. If Windows says "Python was not found", close VS Code, reopen it and try again. Still no luck? Re-run the installer, choose **Modify**, and make sure the PATH option is on.

---

## Step 3: Unzip the course folder

1. Save the zip file somewhere easy, like **Documents**.
2. Right-click it and choose **Extract All** (Mac: double-click it).
3. You now have a folder called `section1`.

> Don't open files from inside the zip. Always extract first.

---

## Step 4: Open the folder in VS Code

1. In VS Code: **File → Open Folder…**
2. Pick the `section1` folder (the one that contains `README.md`).
3. If VS Code asks *"Do you trust the authors?"*, click **Yes, I trust the authors**.

You should now see the files on the left: `01_hello_world_env_setup.py`, `02_...`, and so on.

---

## Step 5: Install the Python extension and open the terminal

1. Press `Ctrl + Shift + X` (Mac: `Cmd + Shift + X`).
2. Search **Python**, pick the one by **Microsoft**, and click **Install**.
3. Open the terminal: `` `Ctrl + ` ` `` (the key under Esc), or menu **Terminal → New Terminal**.

A panel opens at the bottom. Every command below is typed there, followed by **Enter**. The path shown in the terminal should end with `section1`.

---

## Step 6: Install uv (the tool that sets everything up)

`uv` creates a private Python environment for this project and installs the right libraries, so nothing clashes with other projects.

| Windows | Mac |
| :--- | :--- |
| `python -m pip install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

Check it:

```bash
uv --version
```

If it says "not found", close the terminal panel, open a new one and try again.

---

## Step 7: Install the project libraries

```bash
uv sync
```

Wait a minute or two. It creates a hidden `.venv` folder and downloads everything. When the prompt comes back, you're done.

---

## Step 8: Tell VS Code to use that environment

1. Press `Ctrl + Shift + P` (Mac: `Cmd + Shift + P`).
2. Type **Python: Select Interpreter** and press Enter.
3. Choose the one that has **`.venv`** in its path.

*(This only stops VS Code from underlining imports in yellow. The scripts run fine without it.)*

---

## Step 9: Add your API key

The scripts need a key to talk to an AI model. You keep it in a file called `.env`, so it never sits inside the code.

### 1. Make your `.env` file. In the terminal:

| Windows | Mac |
| :--- | :--- |
| `copy sample.env.example .env` | `cp sample.env.example .env` |

You'll see a new file named `.env` appear on the left. Click it to open it. (Create it in VS Code, not Notepad. Notepad likes to rename it `.env.txt`.)

### 2. Get a key. Pick one:

* **OpenAI** (paid, needs a card): https://platform.openai.com/api-keys → *Create new secret key*. Paste it after `OPENAI_API_KEY=`.
* **Groq** (free tier, no OpenAI account needed): https://console.groq.com/keys → *Create API Key*. Then in `.env`:
  1. Put a `#` at the start of the Option A `OPENAI_API_KEY=` line.
  2. Remove the `#` from the three Option B lines.
  3. Paste your Groq key (it starts with `gsk_`) in place of the placeholder.

### 3. Save with `Ctrl + S` (Mac: `Cmd + S`).

Rules for the `.env` file: no spaces around `=`, no quote marks, and never share this file with anyone.

---

## Step 10: Run the scripts

Run them one at a time, in order:

```bash
uv run python 01_hello_world_env_setup.py
```

You should see:

```text
Hello from Future with Shivank — AI Harness!
OPENAI_API_KEY loaded ✅  (starts with 'sk-proj-', ... characters)
```

(With Groq it says `starts with 'gsk_...'`. That's correct. The script uses the same variable name for both.)

If you see ✅, move on:

```bash
uv run python 02_summary_chain_openai.py
uv run python 04_inspect_the_response_object.py
```

Script 02 prints a headline, a 3-bullet summary and an interview question. The wording is different every time. That's normal.

> You don't need to "activate" anything. `uv run` handles the environment for you.

---

## Step 11 (optional): Run a model on your own computer

Only needed for script 03 and `04 --local`. It needs no key, but it's a bigger download.

1. Install Ollama: https://ollama.com/download and open it.
2. In the terminal: `ollama pull gemma3:270m` (about 300 MB).
3. Run:

```bash
uv run python 03_summary_chain_ollama.py
```

---

## When something goes wrong

| What you see | What to do |
| :--- | :--- |
| `python` / `uv` "not found" | Close the terminal, open a new one. On Windows, check the PATH box from Step 2. |
| OPENAI_API_KEY is missing ❌ | `.env` doesn't exist yet, or it's in the wrong folder. It must sit next to the `.py` files. Redo Step 9. |
| `AuthenticationError` or `401` | The key is wrong, has a stray space, or was revoked. Make a fresh one and paste it again. |
| `model ... does not exist` | Set `OPENAI_MODEL=` in `.env` to a model your account can use. For Groq, use `llama-3.3-70b-versatile`. |
| `insufficient_quota` / `429` | Your OpenAI account has no credit. Switch to Groq (Step 9). |
| You edited `.env` but nothing changed | Save the file (`Ctrl + S`), then run the script again. |
| `Failed to connect to Ollama` | Open the Ollama app, then retry. |
| `No module named ...` | You skipped `uv sync`, or you ran `python` instead of `uv run python`. |

Stuck? Copy the **full** red error text from the terminal and send it to your instructor. Never send your API key along with it.
