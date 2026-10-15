#!/usr/bin/env python3
"""THE entrypoint for any 'the checks pass' claim. Order is the point.

A validator's exit code means nothing unless the validator's OWN tests are green.
2026-08-07: an operator allowlist decision silently broke a validator test; the merge
that claimed "validator exit 0" was made while the test guarding that validator was red.
Nobody noticed because nothing ran the tests before the validator.

Order (each gate blocks the next):
  1. unit tests  -> if red, NO validator verdict may be claimed
  2. validate_vocab.py
  3. check_decision_gates.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    ("unit tests (guard the guards)", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-p", "test_*.py"]),
    ("vocab validator", [sys.executable, "scripts/validate_vocab.py"]),
    ("decision-gate bans", [sys.executable, "scripts/check_decision_gates.py"]),
]

def main() -> int:
    for name, cmd in STAGES:
        print(f"\n=== {name} ===", flush=True)
        if "unittest" in cmd:
            # A discover run that collects NOTHING exits 0. "Tests pass" would then be
            # vacuously true. Measured 2026-08-07 in battery-v2: `discover -s . -p test_*.py`
            # -> "Ran 0 tests ... OK" while the real suite (20 tests) lived one dir down.
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            print(r.stdout + r.stderr, end="")
            import re as _re
            m = _re.search(r"Ran (\d+) tests?", r.stderr + r.stdout)
            n = int(m.group(1)) if m else 0
            if n == 0:
                print("\nBLOCKED: test runner collected 0 tests — a green run here is vacuous.")
                return 1
            print(f"[collected {n} tests]")
            rc = r.returncode
        else:
            rc = subprocess.run(cmd, cwd=ROOT).returncode
        if rc != 0:
            print(f"\nBLOCKED at '{name}' (exit {rc}). "
                  f"Later stages NOT run — their verdicts would be unbacked.")
            return rc
    print("\nALL GATES GREEN")
    return 0

if __name__ == "__main__":
    sys.exit(main())
