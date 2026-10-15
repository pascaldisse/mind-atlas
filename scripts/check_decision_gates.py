#!/usr/bin/env python3
"""Enforce gates/forbidden-decision-gates.json across the repo. Exit 1 on violation.

Prose in a knowledge file has no force over a lane. This does.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = json.loads((ROOT / "gates" / "forbidden-decision-gates.json").read_text())

def main() -> int:
    violations = []
    for ban in GATES["bans"]:
        if ban.get("match") == "comment-only":
            continue
        rx = re.compile(ban["pattern"])
        allow = set(ban.get("allowlist_paths", []))
        for py in ROOT.rglob("*.py"):
            rel = py.relative_to(ROOT).as_posix()
            if rel in allow or "/.git/" in rel or rel.startswith("scripts/check_decision_gates"):
                continue
            for n, line in enumerate(py.read_text(errors="replace").splitlines(), 1):
                if rx.search(line):
                    violations.append((ban["id"], rel, n, line.strip()[:100]))
    for bid, rel, n, line in violations:
        print(f"VIOLATION [{bid}] {rel}:{n}\n    {line}")
    if violations:
        print(f"\n{len(violations)} decision-gate violation(s). See gates/forbidden-decision-gates.json.")
        return 1
    print(f"OK: no forbidden decision gates (checked {len(GATES['bans'])} bans)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
