"""Reject empty, skipped, timeout and compilation-error logs as proof results."""
from pathlib import Path
import re
import sys

mode, name = sys.argv[1:]
log = Path(name).read_text()
uninit_diagnostic = "Undefined Behavior: Reading from an uninitialized pointer of type"
if mode in ("positive", "positive8", "positive_init", "positive8_init"):
    size = 8 if mode.startswith("positive8") else 4
    if not re.search(r"Complete\s*-\s*1 successfully verified harnesses?,\s*0 failures?,\s*1 total", log):
        raise SystemExit("Missing exact one-harness success summary")
    if f"sort{size}_preserves_values_and_sorts_i32" not in log:
        raise SystemExit("Expected positive harness not observed")
    blocks = re.split(r"(?m)^\s*Check \d+:", log)[1:]
    for message in (f"SORT{size}_SORTEDNESS", f"SORT{size}_MULTISET"):
        matches = [block for block in blocks if message in block]
        if len(matches) != 1 or not re.search(r"Status:\s*SUCCESS", matches[0]):
            raise SystemExit(f"Expected reachable successful assertion: {message}")
    if mode.endswith("_init") and not any(
        uninit_diagnostic in block and re.search(r"Status:\s*SUCCESS", block)
        for block in blocks
    ):
        raise SystemExit("No reachable successful uninitialized-read check observed")
elif mode == "negative":
    if not re.search(r"Complete\s*-\s*0 successfully verified harnesses?,\s*1 failures?,\s*1 total", log):
        raise SystemExit("Missing exact one-harness failure summary")
    if "negative_control_preservation" not in log:
        raise SystemExit("Expected negative control not observed")
    blocks = re.split(r"(?m)^\s*Check \d+:", log)[1:]
    failures = [block for block in blocks if re.search(r"Status:\s*FAILURE", block)]
    if len(failures) != 1 or "INTENTIONAL_MULTISET_LOSS_CONTROL" not in failures[0]:
        raise SystemExit("Failure was not uniquely the deliberate multiset assertion")
elif mode == "negative_uninit":
    if not re.search(r"Complete\s*-\s*0 successfully verified harnesses?,\s*1 failures?,\s*1 total", log):
        raise SystemExit("Missing exact one-harness failure summary")
    if "negative_control_uninitialized_read" not in log:
        raise SystemExit("Expected uninitialized-read control not observed")
    blocks = re.split(r"(?m)^\s*Check \d+:", log)[1:]
    failures = [block for block in blocks if re.search(r"Status:\s*FAILURE", block)]
    if not failures or any(uninit_diagnostic not in block for block in failures):
        raise SystemExit("Control failures were not exclusively uninitialized-read diagnostics")
else:
    raise SystemExit("Unknown result mode")
print(f"Validated {mode} result summary; inspect detailed checks in this log.")
