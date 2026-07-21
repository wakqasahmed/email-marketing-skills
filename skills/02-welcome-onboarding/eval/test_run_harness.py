#!/usr/bin/env python3
"""Regression tests for the isolated welcome-onboarding harness gate."""
import importlib.util
import unittest
from pathlib import Path


HARNESS = Path(__file__).parent / "run_harness.py"
SPEC = importlib.util.spec_from_file_location("welcome_harness", HARNESS)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


CASES = [
    {"name": "valid-welcome", "expected_outcome": {"decision": "SEND"}},
    {"name": "unverified-signup", "expected_outcome": {"decision": "BLOCK"}},
]


def records(enabled: tuple[str, str], disabled: tuple[str, str]) -> list[dict]:
    return [
        {"name": name, "condition": condition, "trial": trial, "outcome": {"decision": decision}}
        for condition, decisions in (("enabled", enabled), ("disabled", disabled))
        for trial in range(3)
        for name, decision in zip(("valid-welcome", "unverified-signup"), decisions)
    ]


class HarnessValidationTests(unittest.TestCase):
    def test_scores_enabled_condition_and_ablation_delta(self) -> None:
        summary = MODULE.validate(records(("SEND", "BLOCK"), ("HOLD", "BLOCK")), CASES, 3)

        self.assertEqual(summary, {
            "enabled_pass_rate": 1.0,
            "disabled_pass_rate": 0.5,
            "delta": 0.5,
        })

    def test_rejects_duplicate_or_missing_trial_records(self) -> None:
        invalid = records(("SEND", "BLOCK"), ("HOLD", "BLOCK"))[:-1]

        with self.assertRaisesRegex(ValueError, "exactly once"):
            MODULE.validate(invalid, CASES, 3)

    def test_requires_a_digest_pinned_image(self) -> None:
        with self.assertRaisesRegex(ValueError, "digest-pinned"):
            MODULE.require_digest_pinned_image("registry.example/welcome-harness:latest")


if __name__ == "__main__":
    unittest.main()
