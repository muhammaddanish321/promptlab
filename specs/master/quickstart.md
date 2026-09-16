# quickstart.md — Developer Quick Reference

**Date**: 2026-09-16  
**For**: Developers implementing promptlab phases  
**Status**: Complete

---

## Project Setup

### Clone & Check Environment

```bash
git clone <repo>
cd aicode/promptlab
python doctor  # Should show all checks passed
```

### Directory Structure

```
promptlab/               # Main package
├── __main__.py         # Entry point
├── cli.py              # Command routing
├── suite.py            # Suite loading
├── model.py            # Model invocation
├── assertions.py       # Assertion evaluation
├── runner.py           # Case execution
├── report.py           # Report generation
├── compare.py          # Diff logic
└── doctor.py           # Diagnostics

tests/
├── test_assertions.py
├── test_suite_loading.py
├── test_runner.py
└── fixtures/fake_model.py
```

---

## Key Modules & Responsibilities

### `cli.py` — Command Routing

**Purpose**: Parse CLI arguments, route to correct handler

**Key Functions**:
- `main()` — Entry point, parse args via argparse
- `run_command(args)` — Handler for `run` command
- `compare_command(args)` — Handler for `compare` command
- `doctor_command(args)` — Handler for `doctor` command

**Dependencies**: argparse, sys

---

### `suite.py` — Suite Loading & Validation

**Purpose**: Load suite JSON, validate schema, resolve paths

**Key Functions**:
- `load_suite(file_path: str) -> dict` — Load and validate suite
- `validate_suite(data: dict) -> tuple(bool, str)` — Validate schema
- `resolve_paths(suite: dict, suite_dir: str) -> dict` — Resolve relative paths

**Path Resolution**:
```python
prompt_path = os.path.join(os.path.dirname(suite_file), suite["prompt_file"])
```

**Dependencies**: json, os, pathlib

---

### `model.py` — Model Subprocess Invocation

**Purpose**: Call stubmodel.py, parse response, handle errors

**Key Functions**:
- `invoke_model(prompt_file: str, input_text: str, temp: float, seed: int, max_tokens: int) -> dict` — Call model, return response

**Response Format**:
```json
{
  "output": "...",
  "tokens_in": 92,
  "tokens_out": 24,
  "finish": "stop",
  "latency_ms": 340
}
```

**Error Handling**:
- Model not found → exit 3
- Subprocess error → exit 3
- Response not JSON → exit 3
- JSON parse error → exit 3

**Dependencies**: subprocess, json, sys

---

### `assertions.py` — All 8 Assertion Types

**Purpose**: Evaluate assertions against model output

**Key Functions**:
- `evaluate_assertion(assertion: dict, output: str) -> bool` — Evaluate one assertion
- `extract_fenced_json(output: str) -> str` — Extract JSON from fenced code block
- `resolve_dotted_path(obj: dict, path: str) -> any` — Resolve foo.bar.0.baz paths

**Assertion Evaluators**:
```python
def contains(output: str, value: str, ignore_case: bool = False) -> bool: ...
def not_contains(output: str, value: str, ignore_case: bool = False) -> bool: ...
def equals(output: str, value: str, normalize: bool = False) -> bool: ...
def matches(output: str, pattern: str) -> bool: ...
def json_valid(output: str) -> bool: ...
def json_field_equals(output: str, field: str, value: any) -> bool: ...
def max_tokens(output: str, tokens_out: int, threshold: int) -> bool: ...
def finish_is(output: str, finish: str, expected: str) -> bool: ...
```

**Fenced JSON**:
```python
def extract_fenced_json(output: str) -> str:
    import re
    match = re.match(r'^```(?:\w+)?\s*\n([\s\S]*?)\n```\s*$', output.strip())
    return match.group(1) if match else output
```

**Dependencies**: re, json, math

---

### `runner.py` — Case Execution Loop

**Purpose**: Run each case N times, track pass/fail per assertion, classify flaky

**Key Functions**:
- `run_suite(suite: dict, runs: int) -> list` — Execute all cases
- `run_case(case: dict, prompt_file: str, runs: int) -> dict` — Execute one case N times
- `classify_status(pass_rate: float) -> str` — Classify as pass/fail/flaky

**Flaky Classification**:
```python
def classify_status(pass_rate: float) -> str:
    if pass_rate == 1.0:
        return "pass"
    elif pass_rate == 0.0:
        return "fail"
    else:
        return "flaky"  # 0 < pass_rate < 1.0
```

**Per-Assertion Tracking**:
```python
assertions_results = [
    {"type": "json_valid", "passed": 3, "failed": 0},
    {"type": "json_field_equals", "passed": 2, "failed": 1}
]
```

**Dependencies**: model.py, assertions.py

---

### `report.py` — Report Generation

**Purpose**: Build report JSON matching schema

**Key Functions**:
- `generate_report(suite: dict, cases_results: list, runs: int, model_config: dict) -> dict` — Build report

**Report Structure**:
```python
{
    "suite": suite["name"],
    "prompt_file": suite["prompt_file"],
    "prompt_hash": compute_hash(prompt_bytes)[:12],
    "runs": runs,
    "model": model_config,
    "totals": {
        "cases": len(cases),
        "passed": count_status("pass"),
        "failed": count_status("fail"),
        "flaky": count_status("flaky"),
        "tokens_in": sum(...),
        "tokens_out": sum(...),
        "wall_ms": elapsed_ms
    },
    "cases": cases_results
}
```

**Token Counting**:
```python
def compute_tokens(text: str) -> int:
    import math
    return math.ceil(len(text) / 4)
```

**Determinism**: Use json.dumps with sort_keys=True for consistent key ordering

**Dependencies**: json, hashlib, math, time

---

### `compare.py` — Report Comparison

**Purpose**: Classify cases (regressed/improved/unchanged/new/removed), compute cost delta

**Key Functions**:
- `compare_reports(baseline: dict, candidate: dict) -> dict` — Generate diff
- `classify_case(baseline_rate: float, candidate_rate: float) -> str` — Classify change

**Classification Logic**:
```python
def classify_case(baseline_rate: float, candidate_rate: float) -> str:
    if candidate_rate < baseline_rate:
        return "regressed"  # ANY drop is regression
    elif candidate_rate > baseline_rate:
        return "improved"
    else:
        return "unchanged"
```

**Cost Delta**:
```python
cost_delta = {
    "tokens_in_delta": candidate_in - baseline_in,
    "tokens_in_pct": (candidate_in - baseline_in) / baseline_in * 100,
    "tokens_out_delta": candidate_out - baseline_out,
    "tokens_out_pct": (candidate_out - baseline_out) / baseline_out * 100
}
```

**Warnings**:
- Same prompt_hash → self-comparison?
- Different suites → incomparable?
- Different model settings → incomparable?

**Dependencies**: json

---

### `doctor.py` — Environment Diagnostics

**Purpose**: Check Python version, model binary, suites, assertions

**Key Functions**:
- `run_doctor() -> int` — Run all checks, return exit code

**Checks**:
1. Python 3.10+
2. Model binary reachable (`python stubmodel.py --help`)
3. Suites directory exists with .json files
4. All 8 assertion types registered

**Dependencies**: sys, subprocess, os, assertions.py

---

## Testing Strategy

### Unit Tests (Phase 2 & 3)

**Test Structure**:
```
tests/
├── test_assertions.py       # Test all 8 assertion types
├── test_suite_loading.py    # Test suite parsing & validation
├── test_model.py            # Test model invocation
├── test_runner.py           # Test case execution & flaky logic
├── test_report.py           # Test report generation
├── test_compare.py          # Test comparison & regression detection
├── test_doctor.py           # Test doctor checks
└── fixtures/
    └── fake_model.py        # Fake model for testing
```

**Running Tests**:
```bash
python -m unittest discover tests/
```

### Test Fixtures

**fake_model.py** (implements model CLI contract):
```python
# python fake_model.py --prompt <file> --input <text|@file>
# Outputs: {"output": "...", "tokens_in": ..., "tokens_out": ..., "finish": "stop", "latency_ms": ...}
```

### Key Test Cases

**Assertions**:
- `contains`: "hello" in "hello world" → pass
- `contains`: "hello" not in "goodbye" → fail
- `json_valid`: Bare JSON → pass
- `json_valid`: Fenced JSON → pass
- `json_field_equals`: Resolve foo.bar.0.baz → extract and compare
- `matches`: Valid regex → pass; invalid regex → exit 1

**Suite Loading**:
- Valid suite → load successfully
- Missing fields → exit 1
- Invalid JSON → exit 1
- File not found → exit 4

**Flaky Classification**:
- 3 runs, 3 passes → status = "pass", pass_rate = 1.0
- 3 runs, 0 passes → status = "fail", pass_rate = 0.0
- 3 runs, 2 passes, 1 fail → status = "flaky", pass_rate = 0.667

**Regression Detection**:
- 1.0 → 0.9 → regressed
- 0.8 → 0.7 → regressed
- 0.5 → 0.5 → unchanged
- 0.5 → 0.8 → improved

---

## Common Patterns

### Error Handling

**Exit Codes**:
```python
if error_condition:
    print("error message", file=sys.stderr)
    sys.exit(exit_code)
```

**One-Line Messages Only**: No tracebacks

---

### Path Resolution

```python
import os
suite_dir = os.path.dirname(suite_file)
prompt_path = os.path.join(suite_dir, suite["prompt_file"])
```

---

### JSON Determinism

```python
import json
output = json.dumps(data, sort_keys=True, separators=(',', ':'))
```

---

### Token Counting

```python
import math
def tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
```

---

## Key Decisions Summary

| Decision | Value | Reference |
|----------|-------|-----------|
| Flaky | 0 < rate < 1.0 | ADR-001 |
| Fenced JSON | Extract & parse | ADR-002 |
| Regression | Any drop | ADR-003 |
| Cost | Totals + averages | ADR-004 |
| Assertions | All evaluate | ADR-005 |
| Tokens | ceil(len/4) | SPEC.md |
| Exit Codes | 0/1/2/3/4 | SPEC.md |

---

## Implementation Checklist

**Phase 1** (CLI + Suite):
- [ ] cli.py with argparse routing
- [ ] suite.py with validation
- [ ] Error handling with correct exit codes
- [ ] Tests passing

**Phase 2** (Run + Assertions):
- [ ] model.py subprocess call
- [ ] assertions.py with all 8 types
- [ ] runner.py with flaky classification
- [ ] report.py with schema compliance
- [ ] Byte-identical reports at temp 0.0
- [ ] Tests passing

**Phase 3** (Compare + Doctor):
- [ ] compare.py with regression detection
- [ ] doctor.py with 4 checks
- [ ] Warnings for incomparable reports
- [ ] Tests passing

---

**Next**: `/sp.tasks` to break phases into granular, testable tasks.
