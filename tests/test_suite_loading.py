"""Unit tests for suite loading and validation."""

import unittest
import json
import os
import tempfile
from pathlib import Path
from promptlab import suite


class TestSuiteLoading(unittest.TestCase):
    """Test suite loading functionality."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()

        # Create a valid prompt file
        self.prompt_file = os.path.join(self.test_dir, "prompt.txt")
        with open(self.prompt_file, 'w') as f:
            f.write("Classify the ticket\nTicket: {input}")

        # Create a valid input file
        self.input_file = os.path.join(self.test_dir, "input.txt")
        with open(self.input_file, 'w') as f:
            f.write("I was charged twice")

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _write_suite(self, suite_dict):
        """Write suite dict to file and return path."""
        suite_file = os.path.join(self.test_dir, "suite.json")
        with open(suite_file, 'w') as f:
            json.dump(suite_dict, f)
        return suite_file

    def _valid_suite(self):
        """Return a valid suite dict."""
        return {
            "name": "test-suite",
            "prompt_file": "prompt.txt",
            "model": {"temperature": 0.0, "max_tokens": 256},
            "runs": 1,
            "cases": [
                {
                    "id": "c001",
                    "input": "test input",
                    "assert": [{"type": "contains", "value": "test"}]
                }
            ]
        }

    def test_load_valid_suite(self):
        """Valid suite loads successfully."""
        suite_file = self._write_suite(self._valid_suite())
        loaded = suite.load_suite(suite_file)

        self.assertEqual(loaded["name"], "test-suite")
        self.assertIsNotNone(loaded["cases"])
        self.assertEqual(len(loaded["cases"]), 1)

    def test_missing_required_field(self):
        """Missing required field raises ValueError."""
        invalid_suite = self._valid_suite()
        del invalid_suite["name"]

        suite_file = self._write_suite(invalid_suite)
        with self.assertRaises(ValueError) as ctx:
            suite.load_suite(suite_file)
        self.assertIn("missing field", str(ctx.exception))

    def test_wrong_field_type(self):
        """Wrong field type raises ValueError."""
        invalid_suite = self._valid_suite()
        invalid_suite["runs"] = "one"  # Should be int

        suite_file = self._write_suite(invalid_suite)
        with self.assertRaises(ValueError):
            suite.load_suite(suite_file)

    def test_unknown_assertion_type(self):
        """Unknown assertion type raises ValueError."""
        invalid_suite = self._valid_suite()
        invalid_suite["cases"][0]["assert"] = [{"type": "json_schema"}]

        suite_file = self._write_suite(invalid_suite)
        with self.assertRaises(ValueError) as ctx:
            suite.load_suite(suite_file)
        self.assertIn("unknown type", str(ctx.exception))

    def test_file_not_found(self):
        """Missing suite file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            suite.load_suite("/nonexistent/suite.json")

    def test_invalid_json(self):
        """Invalid JSON raises ValueError."""
        bad_json_file = os.path.join(self.test_dir, "bad.json")
        with open(bad_json_file, 'w') as f:
            f.write("{invalid json")

        with self.assertRaises(ValueError) as ctx:
            suite.load_suite(bad_json_file)
        self.assertIn("JSON parse error", str(ctx.exception))

    def test_missing_prompt_file(self):
        """Missing prompt file raises FileNotFoundError."""
        invalid_suite = self._valid_suite()
        invalid_suite["prompt_file"] = "nonexistent.txt"

        suite_file = self._write_suite(invalid_suite)
        with self.assertRaises(FileNotFoundError) as ctx:
            suite.load_suite(suite_file)
        self.assertIn("prompt file", str(ctx.exception))

    def test_path_resolution(self):
        """Paths are resolved relative to suite file."""
        valid_suite = self._valid_suite()
        suite_file = self._write_suite(valid_suite)

        loaded = suite.load_suite(suite_file)

        # Prompt path should be absolute
        self.assertTrue(os.path.isabs(loaded["prompt_file"]))
        # And should exist
        self.assertTrue(os.path.exists(loaded["prompt_file"]))

    def test_input_file_path_resolution(self):
        """Input file paths are resolved relative to suite file."""
        valid_suite = self._valid_suite()
        valid_suite["cases"][0]["input"] = {"file": "input.txt"}
        suite_file = self._write_suite(valid_suite)

        loaded = suite.load_suite(suite_file)

        # Input path should be absolute and exist
        input_path = loaded["cases"][0]["input"]["file"]
        self.assertTrue(os.path.isabs(input_path))
        self.assertTrue(os.path.exists(input_path))

    def test_invalid_regex(self):
        """Invalid regex in matches assertion raises ValueError."""
        invalid_suite = self._valid_suite()
        invalid_suite["cases"][0]["assert"] = [{"type": "matches", "pattern": "[invalid("}]

        suite_file = self._write_suite(invalid_suite)
        with self.assertRaises(ValueError) as ctx:
            suite.load_suite(suite_file)
        self.assertIn("invalid regex", str(ctx.exception))


class TestSuiteValidation(unittest.TestCase):
    """Test suite validation logic."""

    def test_valid_suite(self):
        """Valid suite passes validation."""
        valid_suite = {
            "name": "test",
            "prompt_file": "prompt.txt",
            "model": {"temperature": 0.0},
            "runs": 1,
            "cases": [{"id": "c1", "input": "test"}]
        }
        is_valid, msg = suite.validate_suite(valid_suite)
        self.assertTrue(is_valid, msg)

    def test_empty_name(self):
        """Empty name fails validation."""
        invalid = {"name": "", "prompt_file": "p.txt", "model": {}, "runs": 1, "cases": []}
        is_valid, msg = suite.validate_suite(invalid)
        self.assertFalse(is_valid)
        self.assertIn("name", msg)

    def test_runs_must_be_positive(self):
        """Runs must be >= 1."""
        invalid = {"name": "test", "prompt_file": "p.txt", "model": {}, "runs": 0, "cases": []}
        is_valid, msg = suite.validate_suite(invalid)
        self.assertFalse(is_valid)
        self.assertIn("runs", msg)


if __name__ == "__main__":
    unittest.main()
