"""Comparison logic for two reports."""

import json


def compare_reports(baseline: dict, candidate: dict) -> dict:
    """
    Compare two reports and produce a diff.

    Args:
        baseline: Report dict from baseline run
        candidate: Report dict from candidate run

    Returns:
        Diff dict matching spec schema
    """
    # Collect all case IDs
    baseline_cases = {c["id"]: c for c in baseline["cases"]}
    candidate_cases = {c["id"]: c for c in candidate["cases"]}
    all_case_ids = sorted(set(baseline_cases.keys()) | set(candidate_cases.keys()))

    # Classify each case
    cases = []
    for case_id in all_case_ids:
        baseline_case = baseline_cases.get(case_id)
        candidate_case = candidate_cases.get(case_id)

        if baseline_case is None:
            # New case
            case_diff = {
                "id": case_id,
                "status": "new",
                "candidate_pass_rate": candidate_case["pass_rate"]
            }
        elif candidate_case is None:
            # Removed case
            case_diff = {
                "id": case_id,
                "status": "removed",
                "baseline_pass_rate": baseline_case["pass_rate"]
            }
        else:
            # Case in both reports
            baseline_rate = baseline_case["pass_rate"]
            candidate_rate = candidate_case["pass_rate"]
            status = classify_case(baseline_rate, candidate_rate)
            case_diff = {
                "id": case_id,
                "status": status,
                "baseline_pass_rate": baseline_rate,
                "candidate_pass_rate": candidate_rate
            }

        cases.append(case_diff)

    # Compute cost delta
    cost_delta = compute_cost_delta(baseline["totals"], candidate["totals"])

    # Emit warnings
    warnings = emit_warnings(baseline, candidate)

    # Build diff
    diff = {
        "baseline_suite": baseline["suite"],
        "candidate_suite": candidate["suite"],
        "baseline_prompt_hash": baseline["prompt_hash"],
        "candidate_prompt_hash": candidate["prompt_hash"],
        "cases": cases,
        "cost_delta": cost_delta,
        "warnings": warnings
    }

    return diff


def classify_case(baseline_rate: float, candidate_rate: float) -> str:
    """Classify case status based on pass rate change."""
    if candidate_rate < baseline_rate:
        return "regressed"
    elif candidate_rate > baseline_rate:
        return "improved"
    else:
        return "unchanged"


def compute_cost_delta(baseline_totals: dict, candidate_totals: dict) -> dict:
    """Compute cost delta between two reports."""
    baseline_in = baseline_totals["tokens_in"]
    baseline_out = baseline_totals["tokens_out"]
    candidate_in = candidate_totals["tokens_in"]
    candidate_out = candidate_totals["tokens_out"]

    tokens_in_delta = candidate_in - baseline_in
    tokens_out_delta = candidate_out - baseline_out

    # Compute percentages (avoid division by zero)
    tokens_in_pct = (tokens_in_delta / baseline_in * 100) if baseline_in > 0 else 0.0
    tokens_out_pct = (tokens_out_delta / baseline_out * 100) if baseline_out > 0 else 0.0

    return {
        "tokens_in_delta": tokens_in_delta,
        "tokens_in_pct": round(tokens_in_pct, 1),
        "tokens_out_delta": tokens_out_delta,
        "tokens_out_pct": round(tokens_out_pct, 1)
    }


def emit_warnings(baseline: dict, candidate: dict) -> list:
    """Emit warnings about report comparability."""
    warnings = []

    # Check for same prompt hash
    if baseline["prompt_hash"] == candidate["prompt_hash"]:
        warnings.append("Same prompt_hash; comparing report against itself?")

    # Check for different suites
    if baseline["suite"] != candidate["suite"]:
        warnings.append("Different suites; results may not be comparable.")

    # Check for different model settings
    if (baseline["model"]["temperature"] != candidate["model"]["temperature"] or
        baseline["model"]["max_tokens"] != candidate["model"]["max_tokens"]):
        warnings.append("Different model settings (temperature or max_tokens); results may not be comparable.")

    return warnings
