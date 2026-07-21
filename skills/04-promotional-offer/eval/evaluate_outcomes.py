#!/usr/bin/env python3
"""Validate frozen synthetic outcomes without reimplementing the skill policy."""
import json
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"
REQUIRED_FIELDS = {"decision", "reason_code", "required_actions"}


def main() -> int:
    cases = json.loads(FIXTURES.read_text())["cases"]
    failures = []
    for case in cases:
        expected = case["expected"]
        outcome = case["candidate_outcome"]
        if not REQUIRED_FIELDS.issubset(expected) or not REQUIRED_FIELDS.issubset(outcome):
            failures.append(f"{case['name']}: missing outcome fields")
        elif outcome != expected:
            failures.append(f"{case['name']}: outcome did not match expected result")

    if failures:
        print("FAIL: held-out outcomes")
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(cases)} held-out outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
