"""All 8 assertion types."""

import re
import json
from typing import Any


def extract_fenced_json(output: str) -> str:
    """Extract JSON from fenced code block if present."""
    match = re.match(r'^```(?:\w+)?\s*\n([\s\S]*?)\n```\s*$', output.strip())
    return match.group(1) if match else output


def resolve_dotted_path(obj: Any, path: str) -> Any:
    """
    Resolve dotted path in JSON object.

    Example: "foo.bar.0.baz" resolves obj["foo"]["bar"][0]["baz"]
    """
    parts = path.split('.')
    current = obj

    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Path not found: {part}")
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                if idx < 0:
                    raise IndexError("Negative indices not supported")
                current = current[idx]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid array index: {part}")
        else:
            raise TypeError(f"Cannot resolve path '{path}' on non-object/array")

    return current


def contains(output: str, value: str, ignore_case: bool = False) -> bool:
    """Check if output contains substring."""
    if ignore_case:
        return value.lower() in output.lower()
    return value in output


def not_contains(output: str, value: str, ignore_case: bool = False) -> bool:
    """Check if output does not contain substring."""
    return not contains(output, value, ignore_case)


def equals(output: str, value: str, normalize: bool = False) -> bool:
    """Check if output equals value."""
    if normalize:
        output = ' '.join(output.split())
        value = ' '.join(value.split())
    return output == value


def matches(output: str, pattern: str) -> bool:
    """Check if regex pattern matches output."""
    try:
        return bool(re.search(pattern, output))
    except re.error:
        raise ValueError(f"Invalid regex pattern: {pattern}")


def json_valid(output: str) -> bool:
    """Check if output is valid JSON."""
    try:
        json.loads(extract_fenced_json(output))
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def json_field_equals(output: str, field: str, value: Any) -> bool:
    """Check if JSON field (dotted path) equals value."""
    try:
        data = json.loads(extract_fenced_json(output))
        resolved = resolve_dotted_path(data, field)
        return resolved == value
    except (json.JSONDecodeError, KeyError, TypeError, IndexError):
        return False


def max_tokens(tokens_out: int, threshold: int) -> bool:
    """Check if output tokens is at or below threshold."""
    return tokens_out <= threshold


def finish_is(finish: str, expected: str) -> bool:
    """Check if finish equals expected value."""
    return finish == expected


def evaluate_assertion(assertion: dict, output: str, tokens_out: int = None) -> bool:
    """
    Evaluate a single assertion against output.

    Args:
        assertion: Assertion dict with type and parameters
        output: Model output text
        tokens_out: Output token count (for max_tokens assertion)

    Returns:
        True if assertion passes, False otherwise
    """
    assertion_type = assertion.get("type")

    try:
        if assertion_type == "contains":
            return contains(output, assertion["value"], assertion.get("ignore_case", False))
        elif assertion_type == "not_contains":
            return not_contains(output, assertion["value"], assertion.get("ignore_case", False))
        elif assertion_type == "equals":
            return equals(output, assertion["value"], assertion.get("normalize", False))
        elif assertion_type == "matches":
            return matches(output, assertion["pattern"])
        elif assertion_type == "json_valid":
            return json_valid(output)
        elif assertion_type == "json_field_equals":
            return json_field_equals(output, assertion["field"], assertion["value"])
        elif assertion_type == "max_tokens":
            return max_tokens(tokens_out, assertion["value"])
        elif assertion_type == "finish_is":
            # Need to pass finish value from model response
            return finish_is(assertion.get("_finish", ""), assertion["value"])
        else:
            return False

    except Exception:
        return False
