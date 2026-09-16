"""Unit tests for compare module."""

import unittest
import json
from promptlab import compare


class TestCompareReports(unittest.TestCase):
    """Tests for compare_reports function."""

    def setUp(self):
        """Create sample baseline and candidate reports."""
        self.baseline = {
            "suite": "smoke",
            "prompt_file": "prompts/test.txt",
            "prompt_hash": "a19f40cc21b8",
            "runs": 1,
            "model": {"temperature": 0.0, "max_tokens": 256},
            "totals": {
                "cases": 2,
                "passed": 2,
                "failed": 0,
                "flaky": 0,
                "tokens_in": 1000,
                "tokens_out": 200,
                "wall_ms": 5000
            },
            "cases": [
                {
                    "id": "c001",
                    "status": "pass",
                    "pass_rate": 1.0,
                    "tokens_out_avg": 100,
                    "assertions": [],
                    "failures": []
                },
                {
                    "id": "c002",
                    "status": "pass",
                    "pass_rate": 1.0,
                    "tokens_out_avg": 100,
                    "assertions": [],
                    "failures": []
                }
            ]
        }

        self.candidate = {
            "suite": "smoke",
            "prompt_file": "prompts/test.txt",
            "prompt_hash": "b29g51dd32c9",
            "runs": 1,
            "model": {"temperature": 0.0, "max_tokens": 256},
            "totals": {
                "cases": 3,
                "passed": 2,
                "failed": 1,
                "flaky": 0,
                "tokens_in": 1100,
                "tokens_out": 220,
                "wall_ms": 5500
            },
            "cases": [
                {
                    "id": "c001",
                    "status": "pass",
                    "pass_rate": 1.0,
                    "tokens_out_avg": 100,
                    "assertions": [],
                    "failures": []
                },
                {
                    "id": "c002",
                    "status": "fail",
                    "pass_rate": 0.0,
                    "tokens_out_avg": 100,
                    "assertions": [],
                    "failures": []
                },
                {
                    "id": "c003",
                    "status": "pass",
                    "pass_rate": 1.0,
                    "tokens_out_avg": 100,
                    "assertions": [],
                    "failures": []
                }
            ]
        }

    def test_compare_reports_structure(self):
        """Test that compare produces correct diff structure."""
        diff = compare.compare_reports(self.baseline, self.candidate)

        self.assertIn("baseline_suite", diff)
        self.assertIn("candidate_suite", diff)
        self.assertIn("baseline_prompt_hash", diff)
        self.assertIn("candidate_prompt_hash", diff)
        self.assertIn("cases", diff)
        self.assertIn("cost_delta", diff)
        self.assertIn("warnings", diff)

    def test_case_classification_unchanged(self):
        """Test unchanged case classification."""
        diff = compare.compare_reports(self.baseline, self.candidate)

        # c001 should be unchanged (1.0 → 1.0)
        c001 = next(c for c in diff["cases"] if c["id"] == "c001")
        self.assertEqual(c001["status"], "unchanged")
        self.assertEqual(c001["baseline_pass_rate"], 1.0)
        self.assertEqual(c001["candidate_pass_rate"], 1.0)

    def test_case_classification_regressed(self):
        """Test regressed case classification."""
        diff = compare.compare_reports(self.baseline, self.candidate)

        # c002 should be regressed (1.0 → 0.0)
        c002 = next(c for c in diff["cases"] if c["id"] == "c002")
        self.assertEqual(c002["status"], "regressed")
        self.assertEqual(c002["baseline_pass_rate"], 1.0)
        self.assertEqual(c002["candidate_pass_rate"], 0.0)

    def test_case_classification_new(self):
        """Test new case classification."""
        diff = compare.compare_reports(self.baseline, self.candidate)

        # c003 should be new (only in candidate)
        c003 = next(c for c in diff["cases"] if c["id"] == "c003")
        self.assertEqual(c003["status"], "new")
        self.assertNotIn("baseline_pass_rate", c003)
        self.assertEqual(c003["candidate_pass_rate"], 1.0)

    def test_case_classification_removed(self):
        """Test removed case classification."""
        self.candidate["cases"].pop()  # Remove c003
        self.candidate["totals"]["cases"] = 2
        self.candidate["totals"]["passed"] = 1
        self.candidate["totals"]["failed"] = 1

        diff = compare.compare_reports(self.baseline, self.candidate)

        # After removing c003, we still have c001 and c002
        # No removed case since c001 and c002 are in both
        removed = [c for c in diff["cases"] if c["status"] == "removed"]
        self.assertEqual(len(removed), 0)

    def test_cost_delta_calculation(self):
        """Test cost delta calculation."""
        diff = compare.compare_reports(self.baseline, self.candidate)

        cost_delta = diff["cost_delta"]
        self.assertEqual(cost_delta["tokens_in_delta"], 100)  # 1100 - 1000
        self.assertEqual(cost_delta["tokens_out_delta"], 20)   # 220 - 200
        self.assertAlmostEqual(cost_delta["tokens_in_pct"], 10.0, places=1)
        self.assertAlmostEqual(cost_delta["tokens_out_pct"], 10.0, places=1)

    def test_warnings_same_hash(self):
        """Test warning for same prompt hash."""
        self.candidate["prompt_hash"] = self.baseline["prompt_hash"]
        diff = compare.compare_reports(self.baseline, self.candidate)

        self.assertIn("Same prompt_hash; comparing report against itself?", diff["warnings"])

    def test_warnings_different_suites(self):
        """Test warning for different suites."""
        self.candidate["suite"] = "different-suite"
        diff = compare.compare_reports(self.baseline, self.candidate)

        self.assertIn("Different suites; results may not be comparable.", diff["warnings"])

    def test_warnings_different_model_settings(self):
        """Test warning for different model settings."""
        self.candidate["model"]["temperature"] = 0.7
        diff = compare.compare_reports(self.baseline, self.candidate)

        self.assertIn("Different model settings (temperature or max_tokens); results may not be comparable.", diff["warnings"])

    def test_classify_case_regressed(self):
        """Test classify_case for regressions."""
        self.assertEqual(compare.classify_case(1.0, 0.9), "regressed")
        self.assertEqual(compare.classify_case(0.8, 0.7), "regressed")
        self.assertEqual(compare.classify_case(0.5, 0.0), "regressed")

    def test_classify_case_improved(self):
        """Test classify_case for improvements."""
        self.assertEqual(compare.classify_case(0.5, 0.8), "improved")
        self.assertEqual(compare.classify_case(0.0, 0.5), "improved")
        self.assertEqual(compare.classify_case(0.8, 1.0), "improved")

    def test_classify_case_unchanged(self):
        """Test classify_case for unchanged."""
        self.assertEqual(compare.classify_case(1.0, 1.0), "unchanged")
        self.assertEqual(compare.classify_case(0.5, 0.5), "unchanged")
        self.assertEqual(compare.classify_case(0.0, 0.0), "unchanged")

    def test_compute_cost_delta_zero_baseline(self):
        """Test cost delta with zero baseline (avoid division by zero)."""
        baseline_totals = {"tokens_in": 0, "tokens_out": 100}
        candidate_totals = {"tokens_in": 50, "tokens_out": 120}

        delta = compare.compute_cost_delta(baseline_totals, candidate_totals)

        self.assertEqual(delta["tokens_in_delta"], 50)
        self.assertEqual(delta["tokens_in_pct"], 0.0)  # Division by zero handled
        self.assertEqual(delta["tokens_out_delta"], 20)
        self.assertAlmostEqual(delta["tokens_out_pct"], 20.0, places=1)


class TestClassifyCase(unittest.TestCase):
    """Tests for classify_case function."""

    def test_regression_detection(self):
        """Test that any pass rate drop is detected as regression."""
        self.assertEqual(compare.classify_case(1.0, 0.99), "regressed")
        self.assertEqual(compare.classify_case(1.0, 0.9), "regressed")
        self.assertEqual(compare.classify_case(0.9, 0.8), "regressed")

    def test_improvement_detection(self):
        """Test improvement detection."""
        self.assertEqual(compare.classify_case(0.0, 0.1), "improved")
        self.assertEqual(compare.classify_case(0.5, 0.6), "improved")

    def test_no_change(self):
        """Test unchanged classification."""
        self.assertEqual(compare.classify_case(1.0, 1.0), "unchanged")
        self.assertEqual(compare.classify_case(0.5, 0.5), "unchanged")


class TestComputeCostDelta(unittest.TestCase):
    """Tests for compute_cost_delta function."""

    def test_positive_delta(self):
        """Test positive cost increase."""
        baseline = {"tokens_in": 1000, "tokens_out": 200}
        candidate = {"tokens_in": 1200, "tokens_out": 250}

        delta = compare.compute_cost_delta(baseline, candidate)

        self.assertEqual(delta["tokens_in_delta"], 200)
        self.assertAlmostEqual(delta["tokens_in_pct"], 20.0, places=1)
        self.assertEqual(delta["tokens_out_delta"], 50)
        self.assertAlmostEqual(delta["tokens_out_pct"], 25.0, places=1)

    def test_negative_delta(self):
        """Test negative cost decrease."""
        baseline = {"tokens_in": 1000, "tokens_out": 200}
        candidate = {"tokens_in": 900, "tokens_out": 180}

        delta = compare.compute_cost_delta(baseline, candidate)

        self.assertEqual(delta["tokens_in_delta"], -100)
        self.assertAlmostEqual(delta["tokens_in_pct"], -10.0, places=1)
        self.assertEqual(delta["tokens_out_delta"], -20)
        self.assertAlmostEqual(delta["tokens_out_pct"], -10.0, places=1)

    def test_zero_delta(self):
        """Test no cost change."""
        baseline = {"tokens_in": 1000, "tokens_out": 200}
        candidate = {"tokens_in": 1000, "tokens_out": 200}

        delta = compare.compute_cost_delta(baseline, candidate)

        self.assertEqual(delta["tokens_in_delta"], 0)
        self.assertEqual(delta["tokens_in_pct"], 0.0)
        self.assertEqual(delta["tokens_out_delta"], 0)
        self.assertEqual(delta["tokens_out_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
