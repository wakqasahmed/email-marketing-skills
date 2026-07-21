#!/usr/bin/env python3
"""Small deterministic tests for launch outcome scoring and workspace isolation."""
import json
import tempfile
import unittest
from pathlib import Path

from evaluate_outcomes import load_cases, validate_records
from run_harness import prepare_workspace


class EvaluationTests(unittest.TestCase):
    def test_outcome_validator_scores_complete_ablation_records(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        records = [
            {"name": case["name"], "condition": condition, "trial": 0, "outcome": case["expected"]}
            for case in cases
            for condition in ("enabled", "disabled")
        ]

        failures, summary = validate_records(records, cases, 1)

        self.assertEqual(failures, [])
        self.assertEqual(summary["enabled_pass_rate"], 1)
        self.assertEqual(summary["disabled_pass_rate"], 1)
        self.assertEqual(summary["delta"], 0)

    def test_workspace_exposes_only_prompts_and_enabled_skill(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        runner = Path(__file__)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            prepare_workspace(workspace, runner, "enabled", cases)
            public_cases = json.loads((workspace / "cases.json").read_text())
            self.assertNotIn("expected", public_cases["cases"][0])
            self.assertTrue((workspace / "SKILL.md").is_file())

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            prepare_workspace(workspace, runner, "disabled", cases)
            self.assertFalse((workspace / "SKILL.md").exists())

    def test_outcome_validator_scores_a_disabled_miss_as_a_positive_delta(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        records = [
            {"name": case["name"], "condition": condition, "trial": 0, "outcome": case["expected"]}
            for case in cases
            for condition in ("enabled", "disabled")
        ]
        incorrect_index = 5
        records[incorrect_index]["outcome"] = {"decision": "SEND", "reason_code": "ALL_APPLICABLE_GATES_PASSED", "required_actions": ["send"]}

        failures, summary = validate_records(records, cases, 1)

        self.assertEqual(failures, [])
        self.assertEqual(summary["enabled_pass_rate"], 1)
        self.assertEqual(summary["disabled_pass_rate"], 11 / 12)
        self.assertAlmostEqual(summary["delta"], 1 / 12)


if __name__ == "__main__":
    unittest.main()
