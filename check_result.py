"""Reject empty, skipped, timeout and compilation-error logs as proof results."""
from pathlib import Path
import re
import sys

mode, name = sys.argv[1:]
log = Path(name).read_text()
if mode == "positive":
    if not re.search(r"Complete\s*-\s*1 successfully verified harnesses?,\s*0 failures?,\s*1 total", log):
        raise SystemExit("Missing exact one-harness success summary")
    if "sort4_preserves_values_and_sorts_i32" not in log:
        raise SystemExit("Expected positive harness not observed")
elif mode == "negative":
    if not re.search(r"Complete\s*-\s*0 successfully verified harnesses?,\s*1 failures?,\s*1 total", log):
        raise SystemExit("Missing exact one-harness failure summary")
    if "negative_control_preservation" not in log:
        raise SystemExit("Expected negative control not observed")
    blocks = re.split(r"(?m)^\s*Check \d+:", log)[1:]
    failures = [block for block in blocks if re.search(r"Status:\s*FAILURE", block)]
    if len(failures) != 1 or "INTENTIONAL_MULTISET_LOSS_CONTROL" not in failures[0]:
        raise SystemExit("Failure was not uniquely the deliberate multiset assertion")
else:
    raise SystemExit("Unknown result mode")
print(f"Validated {mode} result summary; inspect detailed checks in this log.")
