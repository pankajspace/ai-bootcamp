"""Unit and end-to-end tests for the LangGraph Bug Fixer Agent."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bug_fixer.executor import compute_unified_diff, extract_suspect_files, run_target  # noqa: E402
from bug_fixer.graph import BugFixerAgent  # noqa: E402
from bug_fixer.schemas import BugDiagnosis, ExecutionResult  # noqa: E402
from run_bug_fixer import BUGGY_BILLING_TEMPLATE  # noqa: E402


class TestBugFixerAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="bug_fixer_test_"))
        self.billing_path = self.temp_dir / "billing.py"
        self.test_path = self.temp_dir / "test_billing.py"

        self.billing_path.write_text(BUGGY_BILLING_TEMPLATE, encoding="utf-8")
        orig_test = (PROJECT_ROOT / "sample_buggy_app" / "test_billing.py").read_text(encoding="utf-8")
        self.test_path.write_text(orig_test, encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_buggy_workspace_fails_tests(self) -> None:
        res = run_target(self.temp_dir)
        self.assertFalse(res.passed)
        self.assertIn("billing.py", res.suspect_files)

    def test_langgraph_agent_diagnoses_and_fixes_bugs_end_to_end(self) -> None:
        agent = BugFixerAgent(provider="mock", verbose=False)
        final_state = agent.run(self.temp_dir, max_retries=3)

        self.assertEqual(final_state["status"], "fixed")
        self.assertEqual(final_state["iteration"], 1)
        self.assertEqual(len(final_state["patches"]), 1)
        self.assertTrue(final_state["last_execution"].passed)

        patch = final_state["patches"][0]
        self.assertEqual(patch.target_file, "billing.py")
        self.assertIn("-    taxable_amount = subtotal + discount_amount", patch.diff)
        self.assertIn("+    taxable_amount = max(0.0, subtotal - discount_amount)", patch.diff)

    def test_dry_run_diagnoses_without_writing_to_disk(self) -> None:
        original_code = self.billing_path.read_text(encoding="utf-8")
        agent = BugFixerAgent(provider="mock", verbose=False)
        final_state = agent.run(self.temp_dir, max_retries=2, dry_run=True)

        self.assertEqual(final_state["status"], "dry_run_diagnosed")
        self.assertEqual(len(final_state["patches"]), 1)
        # File on disk must remain untouched
        self.assertEqual(self.billing_path.read_text(encoding="utf-8"), original_code)

    def test_multi_step_retry_loop_stops_at_max_retries_when_unfixed(self) -> None:
        def noop_diagnoser(files: dict[str, str], exec_res: ExecutionResult) -> BugDiagnosis:
            return BugDiagnosis(
                error_type="BugStillPresent",
                target_file="billing.py",
                buggy_function="calculate_invoice_total",
                root_cause="Intentional no-op patch to test max_retries loop bound",
                fix_explanation="No-op",
                patched_code=files["billing.py"],
            )

        agent = BugFixerAgent(provider="mock", verbose=False, mock_diagnoser=noop_diagnoser)
        final_state = agent.run(self.temp_dir, max_retries=2)

        self.assertEqual(final_state["status"], "failed")
        self.assertEqual(final_state["iteration"], 2)
        self.assertEqual(len(final_state["patches"]), 2)

    def test_diff_and_suspect_file_extraction(self) -> None:
        diff = compute_unified_diff("x = 1\n", "x = 2\n", "app.py")
        self.assertIn("-x = 1", diff)
        self.assertIn("+x = 2", diff)

        tb = f'  File "{self.billing_path}", line 18, in calculate_invoice_total\nKeyError: \'qty\''
        suspects = extract_suspect_files(tb, self.temp_dir)
        self.assertEqual(suspects[0], "billing.py")


if __name__ == "__main__":
    unittest.main()
