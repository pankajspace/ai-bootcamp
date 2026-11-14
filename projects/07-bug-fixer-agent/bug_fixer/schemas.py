"""Pydantic schemas for structured bug diagnosis, execution results, and patch records."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BugDiagnosis(BaseModel):
    """Structured output returned by the LLM bug diagnosis node."""

    error_type: str = Field(description="Exception class or test failure type (e.g. ZeroDivisionError, KeyError, AssertionError)")
    target_file: str = Field(description="Relative path to the source file containing the root-cause bug")
    buggy_function: str = Field(description="Name of the function or method where the bug occurs")
    root_cause: str = Field(description="Clear explanation of why the bug happens based on the traceback and code")
    fix_explanation: str = Field(description="Summary of the code changes made to fix the bug")
    patched_code: str = Field(description="Complete, valid Python source code for target_file with the fix applied")


class ExecutionResult(BaseModel):
    """Outcome of running a Python script or test suite."""

    passed: bool
    return_code: int
    stdout: str
    stderr: str
    error_summary: str = ""
    suspect_files: list[str] = Field(default_factory=list)


class PatchRecord(BaseModel):
    """Record of one diagnose-and-patch iteration."""

    iteration: int
    target_file: str
    error_type: str
    root_cause: str
    fix_explanation: str
    diff: str
