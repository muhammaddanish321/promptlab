"""Report generation and schema compliance."""

import json
import hashlib
import math


def compute_tokens(text: str) -> int:
    """Token rule: ceil(len(text) / 4)."""
    return math.ceil(len(text) / 4)


def compute_prompt_hash(prompt_bytes: bytes) -> str:
    """Compute SHA-256 hash of prompt, return first 12 hex chars."""
    return hashlib.sha256(prompt_bytes).hexdigest()[:12]


def generate_report(suite: dict, cases_results: list, runs: int,
                   start_time: float, end_time: float) -> dict:
    """
    Generate report matching the spec schema.

    Args:
        suite: Suite dict
        cases_results: List of case result dicts from runner
        runs: Number of runs
        start_time: Unix timestamp of run start
        end_time: Unix timestamp of run end

    Returns:
        Report dict matching spec schema
    """
    # Read prompt file for hash
    with open(suite["prompt_file"], 'rb') as f:
        prompt_bytes = f.read()

    prompt_hash = compute_prompt_hash(prompt_bytes)
    wall_ms = int((end_time - start_time) * 1000)

    # Calculate totals
    total_cases = len(cases_results)
    passed_count = sum(1 for c in cases_results if c["status"] == "pass")
    failed_count = sum(1 for c in cases_results if c["status"] == "fail")
    flaky_count = sum(1 for c in cases_results if c["status"] == "flaky")

    # Calculate token totals
    total_tokens_out = sum(c.get("tokens_out_avg", 0) * runs for c in cases_results)

    # Estimate tokens_in (prompt + input for each run)
    prompt_tokens = compute_tokens(prompt_bytes.decode('utf-8', errors='ignore'))
    total_tokens_in = 0
    for case_result in cases_results:
        # Estimate input tokens (we don't have the actual input text here)
        # This is a limitation - in a real implementation, runner would track this
        total_tokens_in += prompt_tokens * runs

    # Build report
    report = {
        "suite": suite["name"],
        "prompt_file": suite["prompt_file"],
        "prompt_hash": prompt_hash,
        "runs": runs,
        "model": suite["model"],
        "totals": {
            "cases": total_cases,
            "passed": passed_count,
            "failed": failed_count,
            "flaky": flaky_count,
            "tokens_in": total_tokens_in,
            "tokens_out": int(total_tokens_out),
            "wall_ms": wall_ms
        },
        "cases": cases_results
    }

    return report


def print_human_summary(report: dict, file=None):
    """Print human-readable summary of report."""
    totals = report["totals"]

    summary = (
        f"{report['suite']} Results:\n"
        f"  Cases: {totals['cases']} | Passed: {totals['passed']} | "
        f"Failed: {totals['failed']} | Flaky: {totals['flaky']}\n"
        f"  Tokens: in={totals['tokens_in']} out={totals['tokens_out']} "
        f"avg_out={totals['tokens_out']//(totals['cases']*report['runs']) if totals['cases'] > 0 and report['runs'] > 0 else 0}\n"
        f"  Wall time: {totals['wall_ms']}ms"
    )

    if file:
        print(summary, file=file)
    else:
        print(summary)
