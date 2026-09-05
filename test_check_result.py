"""Regression checks against false claims from verifier output parsing."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

DIAGNOSTIC = "Undefined Behavior: Reading from an uninitialized pointer of type u8"


def check(number, status, message):
    return f'Check {number}: property.{number}\n - Status: {status}\n - Description: "{message}"\n'


def negative_log(checks, summary=""):
    return ("Checking harness negative_control_uninitialized_read...\n" + checks
            + "SUMMARY:\n" + summary
            + "\nComplete - 0 successfully verified harnesses, 1 failures, 1 total.\n")


class ResultGateTests(unittest.TestCase):
    def accepted(self, mode, log):
        with tempfile.TemporaryDirectory(prefix="smallsort-log-test-") as temp:
            path = Path(temp) / "result.log"
            path.write_text(log)
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("check_result.py")), mode, str(path)],
                capture_output=True, text=True,
            )
            return result.returncode == 0

    def test_summary_cannot_disguise_unrelated_final_failure(self):
        log = negative_log(check(1, "FAILURE", DIAGNOSTIC)
                           + check(2, "FAILURE", "unwinding assertion"),
                           "Failed Checks: " + DIAGNOSTIC + "; unwinding assertion")
        self.assertFalse(self.accepted("negative_uninit", log))

    def test_multiple_actual_initialization_failures_are_valid_control(self):
        log = negative_log(check(1, "FAILURE", DIAGNOSTIC) + check(2, "FAILURE", DIAGNOSTIC))
        self.assertTrue(self.accepted("negative_uninit", log))

    def test_summary_alone_does_not_establish_detector_failure(self):
        log = negative_log(check(1, "SUCCESS", "ordinary check"), "Failed Checks: " + DIAGNOSTIC)
        self.assertFalse(self.accepted("negative_uninit", log))

    def test_both_positive_sizes_require_reachable_named_checks_and_instrumentation(self):
        for size, mode in ((4, "positive_init"), (8, "positive8_init")):
            with self.subTest(size=size):
                log = (f"Checking harness sort{size}_preserves_values_and_sorts_i32...\n"
                       + check(1, "SUCCESS", f"SORT{size}_SORTEDNESS")
                       + check(2, "SUCCESS", f"SORT{size}_MULTISET")
                       + check(3, "SUCCESS", DIAGNOSTIC)
                       + "SUMMARY:\nComplete - 1 successfully verified harnesses, 0 failures, 1 total.\n")
                self.assertTrue(self.accepted(mode, log))
                self.assertFalse(self.accepted(mode, log.replace(DIAGNOSTIC, "ordinary check")))
                self.assertFalse(self.accepted(mode, log.replace("Status: SUCCESS", "Status: UNREACHABLE", 1)))

    def test_empty_or_compile_error_is_not_a_result(self):
        for mode in ("positive_init", "positive8_init", "negative", "negative_uninit"):
            self.assertFalse(self.accepted(mode, ""))
            self.assertFalse(self.accepted(mode, "compilation failed"))


if __name__ == "__main__":
    unittest.main()
