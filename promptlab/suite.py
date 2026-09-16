"""Suite loading and validation."""

import json
import os
from pathlib import Path


# All 8 valid assertion types
VALID_ASSERTION_TYPES = {
    "contains",
    "not_contains",
    "equals",
    "matches",
    "json_valid",
    "json_field_equals",
    "max_tokens",
    "finish_is"
}


def load_suite(file_path: str) -> dict:
    """
    Load and validate a suite JSON file.

    Args:
        file_path: Path to suite JSON file

    Returns:
        Validated suite dict

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If suite is invalid
    """
    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"suite file not found: {file_path}")

    # Read and parse JSON
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error at line {e.lineno}: {e.msg}")
    except Exception as e:
        raise FileNotFoundError(f"cannot read file: {str(e)}")

    # Validate suite schema
    is_valid, error_msg = validate_suite(data)
    if not is_valid:
        raise ValueError(error_msg)

    # Resolve paths relative to suite file location
    suite_dir = os.path.dirname(os.path.abspath(file_path))
    data = resolve_paths(data, suite_dir)

    return data


def validate_suite(data: dict) -> tuple:
    """
    Validate suite JSON schema.

    Args:
        data: Suite dict to validate

    Returns:
        (is_valid: bool, error_message: str)
    """
    # Check top-level required fields
    required_fields = {"name", "prompt_file", "model", "runs", "cases"}
    for field in required_fields:
        if field not in data:
            return False, f"missing field '{field}' at root"

    # Check field types
    if not isinstance(data["name"], str) or not data["name"]:
        return False, "field 'name' must be non-empty string"

    if not isinstance(data["prompt_file"], str) or not data["prompt_file"]:
        return False, "field 'prompt_file' must be non-empty string"

    if not isinstance(data["model"], dict):
        return False, "field 'model' must be object"

    if not isinstance(data["runs"], int) or data["runs"] < 1:
        return False, "field 'runs' must be int >= 1"

    if not isinstance(data["cases"], list) or not data["cases"]:
        return False, "field 'cases' must be non-empty array"

    # Validate model config
    if "temperature" in data["model"]:
        if not isinstance(data["model"]["temperature"], (int, float)):
            return False, "model.temperature must be number"

    if "max_tokens" in data["model"]:
        if not isinstance(data["model"]["max_tokens"], int):
            return False, "model.max_tokens must be int"

    # Validate cases
    for i, case in enumerate(data["cases"]):
        if not isinstance(case, dict):
            return False, f"cases[{i}] must be object"

        if "id" not in case or not isinstance(case["id"], str):
            return False, f"cases[{i}] missing or invalid 'id' field"

        if "input" not in case:
            return False, f"cases[{i}] missing 'input' field"

        # Input can be string or {file: ...}
        if isinstance(case["input"], str):
            if not case["input"]:
                return False, f"cases[{i}].input string must be non-empty"
        elif isinstance(case["input"], dict):
            if "file" not in case["input"]:
                return False, f"cases[{i}].input object must have 'file' field"
            if not isinstance(case["input"]["file"], str):
                return False, f"cases[{i}].input.file must be string"
        else:
            return False, f"cases[{i}].input must be string or object with 'file'"

        # Validate assertions
        if "assert" in case:
            if not isinstance(case["assert"], list):
                return False, f"cases[{i}].assert must be array"

            for j, assertion in enumerate(case["assert"]):
                if not isinstance(assertion, dict):
                    return False, f"cases[{i}].assert[{j}] must be object"

                if "type" not in assertion:
                    return False, f"cases[{i}].assert[{j}] missing 'type' field"

                assertion_type = assertion["type"]
                if assertion_type not in VALID_ASSERTION_TYPES:
                    return False, f"cases[{i}].assert[{j}] unknown type '{assertion_type}'"

                # Validate regex for matches type
                if assertion_type == "matches":
                    if "pattern" not in assertion:
                        return False, f"cases[{i}].assert[{j}] 'matches' requires 'pattern' field"
                    try:
                        import re
                        re.compile(assertion["pattern"])
                    except re.error as e:
                        return False, f"cases[{i}].assert[{j}] invalid regex: {str(e)}"

    return True, ""


def resolve_paths(suite: dict, suite_dir: str) -> dict:
    """
    Resolve relative paths in suite to absolute paths (relative to suite file location).

    Args:
        suite: Suite dict
        suite_dir: Directory containing suite file

    Returns:
        Suite with resolved absolute paths
    """
    # Resolve prompt_file
    prompt_file = suite["prompt_file"]
    if not os.path.isabs(prompt_file):
        suite["prompt_file"] = os.path.join(suite_dir, prompt_file)

    # Verify prompt file exists
    if not os.path.exists(suite["prompt_file"]):
        raise FileNotFoundError(f"prompt file '{prompt_file}' not found (relative to suite)")

    # Resolve input file paths in cases
    for case in suite.get("cases", []):
        if isinstance(case.get("input"), dict) and "file" in case["input"]:
            input_file = case["input"]["file"]
            if not os.path.isabs(input_file):
                case["input"]["file"] = os.path.join(suite_dir, input_file)

            # Verify input file exists
            if not os.path.exists(case["input"]["file"]):
                raise FileNotFoundError(f"input file '{input_file}' not found (relative to suite)")

    return suite
