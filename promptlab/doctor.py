"""Diagnostics utility for checking environment setup."""

import sys
import subprocess
import os
from datetime import datetime


def run_doctor() -> int:
    """
    Run diagnostics on environment setup.

    Returns:
        0 if all checks pass, 1 if any check fails
    """
    print(f"promptlab Doctor ({datetime.now().strftime('%Y-%m-%d')})")
    print("━" * 40)
    print()

    all_pass = True

    # Check Python version
    if check_python_version():
        print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor} OK")
    else:
        print(f"✗ Python version: {sys.version_info.major}.{sys.version_info.minor} (need 3.10+)")
        all_pass = False

    # Check model binary
    if check_model_binary():
        print("✓ Model binary: reachable and responding")
    else:
        print("✗ Model binary: stubmodel.py not found or not responding")
        print("  → Try: python stubmodel.py --help")
        all_pass = False

    # Check suites directory
    suite_count = check_suites_directory()
    if suite_count is not None:
        print(f"✓ Suites directory: found {suite_count} suite files")
    else:
        print("✗ Suites directory: not found or not readable")
        all_pass = False

    # Check assertion types
    if check_assertion_types():
        print("✓ Assertion types: all 8 registered")
    else:
        print("✗ Assertion types: mismatch or import error")
        all_pass = False

    print()
    print("━" * 40)

    if all_pass:
        print("Status: Ready to run")
        print()
        print("Run 'python -m promptlab run --suite suites/smoke.json' to test.")
        return 0
    else:
        print("Status: One or more checks failed")
        return 1


def check_python_version() -> bool:
    """Check if Python version is 3.10 or higher."""
    return sys.version_info >= (3, 10)


def check_model_binary() -> bool:
    """Check if model binary is reachable and responds to --help."""
    try:
        result = subprocess.run(
            ["python", "stubmodel.py", "--help"],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False


def check_suites_directory() -> int | None:
    """
    Check if suites directory exists and count .json files.

    Returns:
        Number of suite files found, or None if directory doesn't exist
    """
    if os.path.isdir("suites"):
        try:
            suite_files = [f for f in os.listdir("suites") if f.endswith(".json")]
            return len(suite_files)
        except Exception:
            return None
    return None


def check_assertion_types() -> bool:
    """Check if all 8 assertion types are registered."""
    try:
        from . import assertions

        # Check if evaluate_assertion can handle all types
        expected_types = {
            "contains", "not_contains", "equals", "matches",
            "json_valid", "json_field_equals", "max_tokens", "finish_is"
        }

        # Verify by checking if functions exist
        for assertion_type in expected_types:
            if assertion_type == "contains":
                if not hasattr(assertions, "contains"):
                    return False
            elif assertion_type == "not_contains":
                if not hasattr(assertions, "not_contains"):
                    return False
            elif assertion_type == "equals":
                if not hasattr(assertions, "equals"):
                    return False
            elif assertion_type == "matches":
                if not hasattr(assertions, "matches"):
                    return False
            elif assertion_type == "json_valid":
                if not hasattr(assertions, "json_valid"):
                    return False
            elif assertion_type == "json_field_equals":
                if not hasattr(assertions, "json_field_equals"):
                    return False
            elif assertion_type == "max_tokens":
                if not hasattr(assertions, "max_tokens"):
                    return False
            elif assertion_type == "finish_is":
                if not hasattr(assertions, "finish_is"):
                    return False

        return True
    except Exception:
        return False
