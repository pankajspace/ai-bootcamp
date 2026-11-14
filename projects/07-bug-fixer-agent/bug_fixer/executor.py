"""Codebase execution, traceback parsing, file inspection, and unified diff utilities."""

from __future__ import annotations

import difflib
import re
import subprocess
import sys
from pathlib import Path

from .schemas import ExecutionResult


def run_target(
    workspace_dir: Path,
    command: list[str] | None = None,
    timeout_sec: int = 20,
) -> ExecutionResult:
    """Run a test suite or Python script inside `workspace_dir` and parse any failure traceback."""
    workspace_dir = workspace_dir.resolve()
    if command is None:
        command = [sys.executable, "-m", "unittest", "discover", "-v"]

    try:
        proc = subprocess.run(
            command,
            cwd=str(workspace_dir),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        passed = proc.returncode == 0
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
    except subprocess.TimeoutExpired as exc:
        passed = False
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = f"TimeoutExpired: Command timed out after {timeout_sec}s"
        proc_returncode = 124
    else:
        proc_returncode = proc.returncode

    combined = f"{stdout}\n{stderr}".strip()
    suspect_files = extract_suspect_files(combined, workspace_dir)
    error_summary = extract_error_summary(combined) if not passed else ""

    return ExecutionResult(
        passed=passed,
        return_code=proc_returncode,
        stdout=stdout,
        stderr=stderr,
        error_summary=error_summary,
        suspect_files=suspect_files,
    )


def extract_suspect_files(traceback_text: str, workspace_dir: Path) -> list[str]:
    """Find workspace-local Python files referenced in a traceback, prioritizing non-test source files."""
    workspace_dir = workspace_dir.resolve()
    matches = re.findall(r'File "([^"]+\.py)", line (\d+)', traceback_text)
    source_files: list[str] = []
    test_files: list[str] = []

    for raw_path, _line in matches:
        p = Path(raw_path)
        if not p.is_absolute():
            p = (workspace_dir / p).resolve()
        else:
            p = p.resolve()

        try:
            rel = str(p.relative_to(workspace_dir))
        except ValueError:
            continue

        if not p.exists():
            continue

        if p.name.startswith("test_") or p.name.endswith("_test.py"):
            if rel not in test_files:
                test_files.append(rel)
        else:
            if rel not in source_files:
                source_files.append(rel)

    # If traceback didn't explicitly name non-test files, scan workspace for non-test .py files
    if not source_files:
        for py_file in sorted(workspace_dir.rglob("*.py")):
            if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                continue
            rel = str(py_file.relative_to(workspace_dir))
            if rel not in source_files:
                source_files.append(rel)

    return source_files + test_files


def extract_error_summary(output_text: str) -> str:
    """Extract the most informative error/assertion line from test output."""
    lines = [line.strip() for line in output_text.splitlines() if line.strip()]
    error_patterns = (
        "Error:",
        "Exception:",
        "AssertionError",
        "ZeroDivisionError",
        "KeyError",
        "TypeError",
        "ValueError",
        "IndexError",
        "AttributeError",
    )
    for line in reversed(lines):
        if any(pat in line for pat in error_patterns):
            return line
    return lines[-1] if lines else "Unknown execution failure"


def collect_workspace_files(workspace_dir: Path) -> dict[str, str]:
    """Read all Python files in `workspace_dir` (relative path -> content)."""
    workspace_dir = workspace_dir.resolve()
    files: dict[str, str] = {}
    for py_file in sorted(workspace_dir.rglob("*.py")):
        if "__pycache__" in py_file.parts or ".venv" in py_file.parts:
            continue
        rel = str(py_file.relative_to(workspace_dir))
        files[rel] = py_file.read_text(encoding="utf-8")
    return files


def compute_unified_diff(old_code: str, new_code: str, filename: str) -> str:
    """Return a clean unified diff between `old_code` and `new_code`."""
    diff_lines = difflib.unified_diff(
        old_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3,
    )
    return "".join(diff_lines).strip()
