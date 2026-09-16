"""Case execution and flaky classification."""

import time
from . import model, assertions


def classify_status(pass_rate: float) -> str:
    """Classify case status based on pass rate."""
    if pass_rate == 1.0:
        return "pass"
    elif pass_rate == 0.0:
        return "fail"
    else:
        return "flaky"


def run_suite(suite: dict, runs: int) -> tuple:
    """
    Execute all cases in suite.

    Returns:
        (cases_results: list, start_time: float, end_time: float)
    """
    start_time = time.time()
    cases_results = []

    for case in suite["cases"]:
        case_result = run_case(case, suite["prompt_file"], runs, suite["model"])
        cases_results.append(case_result)

    end_time = time.time()
    return cases_results, start_time, end_time


def run_case(case: dict, prompt_file: str, runs: int, model_config: dict) -> dict:
    """
    Execute one case N times.

    Returns:
        Case result dict with status, pass_rate, assertions, failures
    """
    case_id = case["id"]
    assertions_list = case.get("assert", [])

    # Track per-assertion pass/fail across runs
    assertion_counts = {}
    for assertion in assertions_list:
        assertion_type = assertion["type"]
        if assertion_type not in assertion_counts:
            assertion_counts[assertion_type] = {"passed": 0, "failed": 0}

    failures = []
    passed_runs = 0
    total_tokens_out = 0

    # Run case N times
    for run_num in range(runs):
        # Get input (string or file)
        if isinstance(case.get("input"), dict) and "file" in case["input"]:
            with open(case["input"]["file"], 'r') as f:
                input_text = f.read()
        else:
            input_text = case.get("input", "")

        # Invoke model
        try:
            response = model.invoke_model(
                prompt_file,
                input_text,
                temperature=model_config.get("temperature", 0.0),
                max_tokens=model_config.get("max_tokens", 256)
            )
        except Exception as e:
            # Model error - fail this run
            for assertion in assertions_list:
                assertion_type = assertion["type"]
                if assertion_type not in assertion_counts:
                    assertion_counts[assertion_type] = {"passed": 0, "failed": 0}
                assertion_counts[assertion_type]["failed"] += 1
            continue

        output = response.get("output", "")
        tokens_out = response.get("tokens_out", 0)
        tokens_in = response.get("tokens_in", 0)
        finish = response.get("finish", "")

        total_tokens_out += tokens_out

        # Evaluate all assertions
        all_passed = True
        for assertion in assertions_list:
            assertion_type = assertion["type"]
            if assertion_type not in assertion_counts:
                assertion_counts[assertion_type] = {"passed": 0, "failed": 0}

            # Special handling for assertions that need response fields
            if assertion_type == "max_tokens":
                passed = assertions.max_tokens(tokens_out, assertion["value"])
            elif assertion_type == "finish_is":
                passed = assertions.finish_is(finish, assertion["value"])
            else:
                passed = assertions.evaluate_assertion(assertion, output, tokens_out)

            if passed:
                assertion_counts[assertion_type]["passed"] += 1
            else:
                assertion_counts[assertion_type]["failed"] += 1
                all_passed = False
                failures.append({
                    "run": run_num,
                    "assertion": assertion,
                    "actual": finish if assertion_type == "finish_is" else (str(tokens_out) if assertion_type == "max_tokens" else output),
                    "output_truncated": output[:500] if len(output) > 500 else output
                })

        if all_passed:
            passed_runs += 1

    # Compute results
    pass_rate = passed_runs / runs if runs > 0 else 0.0
    status = classify_status(pass_rate)
    tokens_out_avg = total_tokens_out / runs if runs > 0 else 0

    # Build assertions list for report
    assertions_report = []
    for assertion in assertions_list:
        assertion_type = assertion["type"]
        if assertion_type in assertion_counts:
            assertions_report.append({
                "type": assertion_type,
                "passed": assertion_counts[assertion_type]["passed"],
                "failed": assertion_counts[assertion_type]["failed"]
            })

    return {
        "id": case_id,
        "status": status,
        "pass_rate": pass_rate,
        "tokens_out_avg": tokens_out_avg,
        "assertions": assertions_report,
        "failures": failures
    }
