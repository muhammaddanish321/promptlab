# Data Model

**Date**: 2026-09-16  
**Feature**: promptlab  
**Status**: Complete

---

## Overview

promptlab has three main data structures:

1. **Suite**: Input specification for a test run
2. **Report**: Output from `run` command (results of test execution)
3. **Diff**: Output from `compare` command (comparison of two reports)

All structures are JSON; paths are relative to the file (for suites) or working directory (for reports/diffs).

---

## Suite (Input)

**Location**: `suites/*.json`  
**Purpose**: Specification of test cases and assertions to run against a prompt

```json
{
  "name": "suite-name",
  "prompt_file": "relative/path/to/prompt.txt",
  "model": {
    "temperature": 0.0,
    "max_tokens": 256
  },
  "runs": 1,
  "cases": [
    {
      "id": "c001",
      "input": "text" | {"file": "relative/path"},
      "assert": [
        { "type": "json_valid" },
        { "type": "json_field_equals", "field": "category", "value": "billing" }
      ]
    }
  ]
}
```

### Suite.name
- **Type**: string
- **Required**: yes
- **Validation**: non-empty
- **Use**: Identifies suite in reports (e.g., "classify-smoke")

### Suite.prompt_file
- **Type**: string (path)
- **Required**: yes
- **Validation**: must exist relative to suite file
- **Use**: Path to prompt text file (resolved relative to suite file)
- **Note**: Relative to suite, not working directory (portable)

### Suite.model
- **Type**: object
- **Required**: yes
- **Fields**:
  - `temperature`: float, default 0.0
  - `max_tokens`: int, default 256

### Suite.runs
- **Type**: int
- **Required**: yes
- **Validation**: ≥ 1
- **Note**: Overridden by `--runs` on CLI

### Suite.cases
- **Type**: array of Case objects
- **Required**: yes
- **Validation**: at least 1 case

### Case.id
- **Type**: string
- **Required**: yes
- **Validation**: unique within suite, non-empty
- **Use**: Identifies case in reports (e.g., "c001")

### Case.input
- **Type**: string | {file: string}
- **Required**: yes
- **Validation**:
  - If string: non-empty
  - If object: `file` field must exist relative to suite file
- **Note**: Paths relative to suite file

### Case.assert
- **Type**: array of Assertion objects
- **Required**: no (default: empty array)
- **Validation**:
  - Type must be one of 8 valid types
  - Required fields present for each type
  - Regex must be valid (if type = "matches")

### Assertion Types

| Type | Fields | Validation |
|------|--------|-----------|
| contains | value, ignore_case? | value: non-empty string |
| not_contains | value, ignore_case? | value: non-empty string |
| equals | value, normalize? | value: any type |
| matches | pattern | pattern: valid regex |
| json_valid | — | — |
| json_field_equals | field, value | field: dotted path, value: any type |
| max_tokens | value | value: int ≥ 0 |
| finish_is | value | value: one of ["stop", "length", "refusal"] |

---

## Report (Output)

**Location**: stdout or `--out report.json`  
**Purpose**: Results of running suite against model

```json
{
  "suite": "suite-name",
  "prompt_file": "relative/path.txt",
  "prompt_hash": "a19f40cc21b8",
  "runs": 3,
  "model": {
    "temperature": 0.0,
    "max_tokens": 256
  },
  "totals": {
    "cases": 20,
    "passed": 16,
    "failed": 3,
    "flaky": 1,
    "tokens_in": 4120,
    "tokens_out": 980,
    "wall_ms": 8640
  },
  "cases": [
    {
      "id": "c001",
      "status": "pass",
      "pass_rate": 1.0,
      "tokens_out_avg": 21,
      "assertions": [
        {
          "type": "json_valid",
          "passed": 3,
          "failed": 0
        }
      ],
      "failures": []
    }
  ]
}
```

### Report.suite
- **Type**: string
- **Value**: Suite name

### Report.prompt_file
- **Type**: string
- **Value**: Path to prompt (from suite)

### Report.prompt_hash
- **Type**: string (12 hex chars)
- **Value**: First 12 chars of SHA-256(prompt_bytes)
- **Use**: Identifies prompt; used by `compare` to detect self-comparison

### Report.runs
- **Type**: int
- **Value**: Number of times each case was run

### Report.model
- **Type**: object
- **Value**: Model configuration used

### Report.totals
- **Type**: object
- **Fields**:
  - `cases`: Total number of cases
  - `passed`: Cases with status = "pass"
  - `failed`: Cases with status = "fail"
  - `flaky`: Cases with status = "flaky"
  - `tokens_in`: Sum of tokens_in across all runs
  - `tokens_out`: Sum of tokens_out across all runs
  - `wall_ms`: Wall-clock milliseconds for entire run

### Report.cases[].status
- **Type**: string (enum)
- **Values**:
  - "pass": pass_rate = 1.0
  - "fail": pass_rate = 0.0
  - "flaky": 0 < pass_rate < 1.0

### Report.cases[].pass_rate
- **Type**: float (0.0 to 1.0)
- **Calculation**: passed_count / runs

### Report.cases[].tokens_out_avg
- **Type**: float
- **Calculation**: total_tokens_out / runs

### Report.cases[].assertions
- **Type**: array
- **Item**:
  ```json
  {
    "type": "json_valid",
    "passed": 3,
    "failed": 0
  }
  ```
- **Fields**:
  - `type`: assertion type
  - `passed`: count of runs where assertion passed
  - `failed`: count of runs where assertion failed

### Report.cases[].failures
- **Type**: array
- **Purpose**: Debugging info; what went wrong
- **Item**:
  ```json
  {
    "run": 1,
    "assertion": { "type": "json_field_equals", "field": "category", "value": "billing" },
    "actual": "account",
    "output_truncated": "model output (truncated to 500 chars)"
  }
  ```

---

## Diff (Output)

**Location**: stdout or `--out diff.json`  
**Purpose**: Comparison of two reports

```json
{
  "baseline_suite": "suite-name",
  "candidate_suite": "suite-name",
  "baseline_prompt_hash": "a19f40cc21b8",
  "candidate_prompt_hash": "b29g51dd32c9",
  "cases": [
    {
      "id": "c001",
      "status": "unchanged",
      "baseline_pass_rate": 1.0,
      "candidate_pass_rate": 1.0
    },
    {
      "id": "c002",
      "status": "regressed",
      "baseline_pass_rate": 1.0,
      "candidate_pass_rate": 0.8
    }
  ],
  "cost_delta": {
    "tokens_in_delta": 120,
    "tokens_in_pct": 2.9,
    "tokens_out_delta": -45,
    "tokens_out_pct": -4.6
  },
  "warnings": [
    "Same prompt_hash; comparing report against itself?"
  ]
}
```

### Diff.cases[].status
- **Type**: string (enum)
- **Values**:
  - "unchanged": pass_rate unchanged
  - "regressed": candidate_pass_rate < baseline_pass_rate (any drop)
  - "improved": candidate_pass_rate > baseline_pass_rate
  - "new": case in candidate but not in baseline
  - "removed": case in baseline but not in candidate

### Diff.cost_delta
- **Type**: object
- **Fields**:
  - `tokens_in_delta`: candidate_total - baseline_total
  - `tokens_in_pct`: (candidate - baseline) / baseline * 100
  - `tokens_out_delta`: (same)
  - `tokens_out_pct`: (same)

### Diff.warnings
- **Type**: array of strings
- **Content**: Warnings about comparability
  - Same prompt_hash (self-comparison?)
  - Different suite names (different test sets?)
  - Different model settings (temperature/max_tokens differ?)

---

## Constraints & Validation Rules

### Suite Validation
- ✅ All required fields present
- ✅ Field types correct
- ✅ No unknown assertion types
- ✅ No invalid regexes
- ✅ Paths resolve correctly
- ✅ Case IDs unique within suite

### Report Validation
- ✅ Totals.passed + failed + flaky = totals.cases
- ✅ All cases present in order (deterministic)
- ✅ All assertions reported (even if not in suite — shouldn't happen)
- ✅ pass_rate = passed / runs (consistent)

### Diff Validation
- ✅ Cases keyed by ID (for easy lookup)
- ✅ Status values only from enum
- ✅ Cost delta calculated consistently
- ✅ No duplicates (each case ID once)

---

## Determinism & Ordering

**JSON Key Ordering**:
- Suite: keys in order (name, prompt_file, model, runs, cases)
- Report: keys in order (suite, prompt_file, prompt_hash, runs, model, totals, cases)
- Cases: sorted by case ID (for deterministic order)

**Numeric Formatting**:
- Floats: Fixed precision (3 decimal places for pass_rate, 1 for pct)
- Integers: No padding or special formatting
- Tokens: Integer counts (no decimals)

**Timing Isolation**:
- wall_ms is the only field that varies between runs at temperature 0.0
- All other fields must be byte-identical

---

## Related Specifications

- Suite schema: SPEC.md Section 2
- Report schema: SPEC.md Section 5
- Diff schema: SPEC.md Section 10
- Token rule: `math.ceil(len(text) / 4)` (everywhere)

---

**Status**: ✅ Data model complete. Ready for contracts/ and quickstart.md.
