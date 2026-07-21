#!/usr/bin/env python3
"""Unit tests for outcome evaluation and harness isolation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


EVAL = Path(__file__).parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, EVAL / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromotionalOfferEvaluationTests(unittest.TestCase):
    def test_harness_workspace_contains_prompts_not_answer_key(self) -> None:
        harness = load_module("run_harness", "run_harness.py")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = workspace / "source-runner"
            runner.write_text("#!/bin/sh\n")
            harness.prepare_workspace(workspace, runner, "disabled")
            cases = json.loads((workspace / "cases.json").read_text())["cases"]

        self.assertTrue(cases)
        self.assertEqual(set(cases[0]), {"name", "prompt"})

    def test_harness_report_retains_model_and_harness_versions(self) -> None:
        harness = load_module("run_harness", "run_harness.py")
        report = harness.build_report(
            trials=3,
            model_version="model-2026-07-21",
            harness_version="runner@abc123",
            summary={"enabled_pass_rate": 1.0, "disabled_pass_rate": 0.0, "delta": 1.0},
            records=[],
        )
        self.assertEqual(report["model_version"], "model-2026-07-21")
        self.assertEqual(report["harness_version"], "runner@abc123")

    def test_outcome_scorer_rejects_incorrect_agent_result(self) -> None:
        outcomes = load_module("evaluate_outcomes", "evaluate_outcomes.py")
        cases = json.loads((EVAL / "fixtures" / "held-out-scenarios.json").read_text())["cases"]
        passes, failures = outcomes.score(
            [{"name": cases[0]["name"], "outcome": {"decision": "BLOCK"}}],
            [cases[0]],
        )
        self.assertEqual(passes, 0)
        self.assertEqual(failures, [f"{cases[0]['name']}: missing outcome fields"])


if __name__ == "__main__":
    unittest.main()
