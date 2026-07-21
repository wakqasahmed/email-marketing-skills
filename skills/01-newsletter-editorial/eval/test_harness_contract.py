#!/usr/bin/env python3
"""Exercise the versioned local runner output interface without Docker or a model."""
import importlib.util
import json
from pathlib import Path


EVAL = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("newsletter_harness", EVAL / "run_harness.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def records(cases: list[dict], trials: int) -> list[dict]:
    return [
        {
            "name": case["name"],
            "condition": condition,
            "trial": trial,
            "outcome": case["expected"],
            "runner_version": "fixture-runner/v1",
            "model": "fixture-model/v1",
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(trials)
    ]


def main() -> int:
    cases = json.loads((EVAL / "fixtures" / "held-out-scenarios.json").read_text())["cases"]
    summary = MODULE.validate(records(cases, 3), cases, 3, "fixture-runner/v1", "fixture-model/v1")
    if summary["enabled_pass_rate"] != 1 or summary["disabled_pass_rate"] != 1:
        raise SystemExit("fixture output interface did not validate")

    invalid = records(cases, 3)
    invalid[0]["model"] = "unversioned-model"
    try:
        MODULE.validate(invalid, cases, 3, "fixture-runner/v1", "fixture-model/v1")
    except ValueError:
        print("PASS: versioned local runner output interface")
        return 0
    raise SystemExit("runner output version mutation was accepted")


if __name__ == "__main__":
    raise SystemExit(main())
