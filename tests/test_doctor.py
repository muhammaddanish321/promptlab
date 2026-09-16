"""Unit tests for doctor module."""

import unittest
import sys
from unittest import mock
from promptlab import doctor


class TestPythonVersion(unittest.TestCase):
    """Tests for Python version check."""

    def test_python_310_passes(self):
        """Test that Python 3.10 passes."""
        with mock.patch.object(sys, 'version_info', (3, 10, 0)):
            self.assertTrue(doctor.check_python_version())

    def test_python_311_passes(self):
        """Test that Python 3.11 passes."""
        with mock.patch.object(sys, 'version_info', (3, 11, 0)):
            self.assertTrue(doctor.check_python_version())

    def test_python_39_fails(self):
        """Test that Python 3.9 fails."""
        with mock.patch.object(sys, 'version_info', (3, 9, 0)):
            self.assertFalse(doctor.check_python_version())

    def test_python_38_fails(self):
        """Test that Python 3.8 fails."""
        with mock.patch.object(sys, 'version_info', (3, 8, 0)):
            self.assertFalse(doctor.check_python_version())


class TestModelBinary(unittest.TestCase):
    """Tests for model binary check."""

    @mock.patch('subprocess.run')
    def test_model_binary_success(self, mock_run):
        """Test successful model binary check."""
        mock_run.return_value.returncode = 0
        self.assertTrue(doctor.check_model_binary())

    @mock.patch('subprocess.run')
    def test_model_binary_error_code(self, mock_run):
        """Test model binary with non-zero exit code."""
        mock_run.return_value.returncode = 1
        self.assertFalse(doctor.check_model_binary())

    @mock.patch('subprocess.run')
    def test_model_binary_not_found(self, mock_run):
        """Test model binary not found."""
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(doctor.check_model_binary())

    @mock.patch('subprocess.run')
    def test_model_binary_timeout(self, mock_run):
        """Test model binary timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)
        self.assertFalse(doctor.check_model_binary())

    @mock.patch('subprocess.run')
    def test_model_binary_general_error(self, mock_run):
        """Test model binary general error."""
        mock_run.side_effect = Exception("Some error")
        self.assertFalse(doctor.check_model_binary())


class TestSuitesDirectory(unittest.TestCase):
    """Tests for suites directory check."""

    @mock.patch('os.path.isdir')
    @mock.patch('os.listdir')
    def test_suites_directory_found(self, mock_listdir, mock_isdir):
        """Test suites directory found with files."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["smoke.json", "classify.json", "readme.txt"]

        count = doctor.check_suites_directory()
        self.assertEqual(count, 2)

    @mock.patch('os.path.isdir')
    @mock.patch('os.listdir')
    def test_suites_directory_empty(self, mock_listdir, mock_isdir):
        """Test suites directory with no files."""
        mock_isdir.return_value = True
        mock_listdir.return_value = []

        count = doctor.check_suites_directory()
        self.assertEqual(count, 0)

    @mock.patch('os.path.isdir')
    def test_suites_directory_not_found(self, mock_isdir):
        """Test suites directory not found."""
        mock_isdir.return_value = False

        count = doctor.check_suites_directory()
        self.assertIsNone(count)

    @mock.patch('os.path.isdir')
    @mock.patch('os.listdir')
    def test_suites_directory_error(self, mock_listdir, mock_isdir):
        """Test suites directory with error."""
        mock_isdir.return_value = True
        mock_listdir.side_effect = Exception("Permission denied")

        count = doctor.check_suites_directory()
        self.assertIsNone(count)


class TestAssertionTypes(unittest.TestCase):
    """Tests for assertion types check."""

    def test_assertion_types_present(self):
        """Test all assertion types are present."""
        self.assertTrue(doctor.check_assertion_types())


class TestDoctorIntegration(unittest.TestCase):
    """Integration tests for run_doctor function."""

    @mock.patch('promptlab.doctor.check_python_version', return_value=True)
    @mock.patch('promptlab.doctor.check_model_binary', return_value=True)
    @mock.patch('promptlab.doctor.check_suites_directory', return_value=2)
    @mock.patch('promptlab.doctor.check_assertion_types', return_value=True)
    def test_run_doctor_all_pass(self, mock_assertions, mock_suites, mock_model, mock_python):
        """Test run_doctor when all checks pass."""
        result = doctor.run_doctor()
        self.assertEqual(result, 0)

    @mock.patch('promptlab.doctor.check_python_version', return_value=False)
    @mock.patch('promptlab.doctor.check_model_binary', return_value=True)
    @mock.patch('promptlab.doctor.check_suites_directory', return_value=2)
    @mock.patch('promptlab.doctor.check_assertion_types', return_value=True)
    def test_run_doctor_python_fails(self, mock_assertions, mock_suites, mock_model, mock_python):
        """Test run_doctor when Python version check fails."""
        result = doctor.run_doctor()
        self.assertEqual(result, 1)

    @mock.patch('promptlab.doctor.check_python_version', return_value=True)
    @mock.patch('promptlab.doctor.check_model_binary', return_value=False)
    @mock.patch('promptlab.doctor.check_suites_directory', return_value=2)
    @mock.patch('promptlab.doctor.check_assertion_types', return_value=True)
    def test_run_doctor_model_fails(self, mock_assertions, mock_suites, mock_model, mock_python):
        """Test run_doctor when model binary check fails."""
        result = doctor.run_doctor()
        self.assertEqual(result, 1)

    @mock.patch('promptlab.doctor.check_python_version', return_value=True)
    @mock.patch('promptlab.doctor.check_model_binary', return_value=True)
    @mock.patch('promptlab.doctor.check_suites_directory', return_value=None)
    @mock.patch('promptlab.doctor.check_assertion_types', return_value=True)
    def test_run_doctor_suites_fails(self, mock_assertions, mock_suites, mock_model, mock_python):
        """Test run_doctor when suites directory check fails."""
        result = doctor.run_doctor()
        self.assertEqual(result, 1)

    @mock.patch('promptlab.doctor.check_python_version', return_value=True)
    @mock.patch('promptlab.doctor.check_model_binary', return_value=True)
    @mock.patch('promptlab.doctor.check_suites_directory', return_value=2)
    @mock.patch('promptlab.doctor.check_assertion_types', return_value=False)
    def test_run_doctor_assertions_fails(self, mock_assertions, mock_suites, mock_model, mock_python):
        """Test run_doctor when assertion types check fails."""
        result = doctor.run_doctor()
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
