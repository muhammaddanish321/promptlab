# promptlab Usage Guide

**promptlab** is a command-line test runner for evaluating LLM prompts. It executes test cases, detects flaky behavior (non-determinism), measures token costs, and compares prompt versions.

---

## Quick Start

```bash
# Verify environment setup
python -m promptlab doctor

# Run a test suite
python -m promptlab run --suite suites/smoke.json --report

# Compare two prompt versions
python -m promptlab compare --baseline baseline.json --candidate candidate.json

# See exit code
echo $?  # 0=all pass, 2=failures, 3=model error, 4=file error
```

---

## Commands

### `run` — Execute a test suite

**Purpose**: Run test cases against a prompt, detect flaky behavior, generate report.

**Usage**:
```bash
python -m promptlab run --suite <file.json> [--runs N] [--out report.json] [--report]
```

**Arguments**:
- `--suite <file>` (required): Path to suite JSON file
- `--runs N` (optional): Number of runs per case (default: from suite)
- `--out <file>` (optional): Write report JSON to file (default: stdout)
- `--report` (optional): Print human-readable summary to stderr

**Output**: JSON report with results, token counts, and pass/fail/flaky classification.

**Exit Codes**:
- `0`: All cases passed
- `1`: Bad arguments or malformed suite JSON
- `2`: One or more cases failed or flaky
- `3`: Model binary not found or subprocess error
- `4`: Suite file unreadable

**Example Workflow**:
```bash
# Run once to test
python -m promptlab run --suite suites/classify.json --runs 1 --report

# Run 10 times for flaky detection
python -m promptlab run --suite suites/classify.json --runs 10 --out baseline.json

# Check results
cat baseline.json | jq '.totals'
```

---

### `compare` — Compare two reports

**Purpose**: Detect regressions, measure cost changes, identify incomparable reports.

**Usage**:
```bash
python -m promptlab compare --baseline <report.json> --candidate <report.json> [--out diff.json]
```

**Arguments**:
- `--baseline <file>` (required): Baseline report JSON
- `--candidate <file>` (required): Candidate report JSON
- `--out <file>` (optional): Write diff JSON to file (default: stdout)

**Output**: JSON diff with case classifications and cost delta.

**Case Classifications**:
- `unchanged`: Same pass rate as baseline
- `improved`: Higher pass rate than baseline
- `regressed`: Lower pass rate than baseline (any drop is flagged)
- `new`: Case in candidate but not baseline
- `removed`: Case in baseline but not candidate

**Warnings** (non-fatal):
- Same prompt_hash → "comparing report against itself?"
- Different suites → "results may not be comparable"
- Different model settings → "temperature or max_tokens differ"

**Exit Codes**:
- `0`: Comparison successful (even if regressions detected)
- `1`: Bad arguments or malformed report JSON
- `4`: Report file unreadable

**Example Workflow**:
```bash
# Baseline: classify_v1.txt with 10 runs
python -m promptlab run --suite suites/classify.json --runs 10 --out v1.json

# Candidate: classify_v2.txt with 10 runs
# (create new suite with different prompt_file, run same)
python -m promptlab run --suite suites/classify_v2.json --runs 10 --out v2.json

# Compare
python -m promptlab compare --baseline v1.json --candidate v2.json

# Check for regressions
cat diff.json | jq '.cases[] | select(.status=="regressed")'

# Check cost delta
cat diff.json | jq '.cost_delta'
```

---

### `doctor` — Diagnostic utility

**Purpose**: Verify environment is ready to run promptlab.

**Usage**:
```bash
python -m promptlab doctor
```

**Checks Performed**:
1. **Python version**: 3.10+ required
2. **Model binary**: `python stubmodel.py --help` reachable and responds
3. **Suites directory**: `suites/` exists with .json files
4. **Assertion types**: All 8 types registered (contains, not_contains, equals, matches, json_valid, json_field_equals, max_tokens, finish_is)

**Output**: Human-readable report with ✓/✗ symbols.

**Exit Codes**:
- `0`: All checks passed
- `1`: One or more checks failed

**Example**:
```bash
$ python -m promptlab doctor
promptlab Doctor (2026-09-16)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Python version: 3.11 OK
✓ Model binary: reachable and responding
✓ Suites directory: found 2 suite files
✓ Assertion types: all 8 registered
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: Ready to run
```

---

## Suite Format

Suites define test cases. Each case specifies input text and assertions.

**Example** (`suites/classify.json`):
```json
{
  "name": "classify",
  "prompt_file": "../prompts/classify_v1.txt",
  "model": {
    "temperature": 0.0,
    "max_tokens": 256
  },
  "runs": 1,
  "cases": [
    {
      "id": "c001",
      "input": "I was charged twice. Please refund.",
      "assert": [
        {"type": "json_valid"},
        {"type": "json_field_equals", "field": "category", "value": "billing"}
      ]
    }
  ]
}
```

**Fields**:
- `name`: Suite identifier (appears in reports)
- `prompt_file`: Path to prompt (relative to suite file, not working directory)
- `model`: Temperature and max_tokens for model invocation
- `runs`: Default number of runs per case (overridden by CLI `--runs`)
- `cases`: Array of test case objects
  - `id`: Case identifier (unique within suite)
  - `input`: Input text (string or `{"file": "path"}` to read from file)
  - `assert`: Array of assertions (checked after model generates output)

---

## Assertion Types

All 8 assertion types work with JSON output from the model.

### 1. `json_valid`
Check if output is valid JSON (including fenced JSON blocks).
```json
{"type": "json_valid"}
```

### 2. `json_field_equals`
Check if a JSON field matches expected value (supports dotted paths like `foo.bar.0.baz`).
```json
{"type": "json_field_equals", "field": "category", "value": "billing"}
```

### 3. `contains`
Check if output contains substring.
```json
{"type": "contains", "value": "success", "ignore_case": false}
```

### 4. `not_contains`
Check if output does NOT contain substring.
```json
{"type": "not_contains", "value": "error"}
```

### 5. `equals`
Check if output exactly equals value (with optional whitespace normalization).
```json
{"type": "equals", "value": "OK", "normalize": false}
```

### 6. `matches`
Check if regex pattern matches output.
```json
{"type": "matches", "pattern": "^status: (success|ok)$"}
```

### 7. `max_tokens`
Check if output tokens are at or below threshold.
```json
{"type": "max_tokens", "value": 100}
```

### 8. `finish_is`
Check if model's finish reason matches (one of: `stop`, `length`, `refusal`).
```json
{"type": "finish_is", "value": "stop"}
```

---

## Report Schema

Reports are JSON files with test results.

**Structure**:
```json
{
  "suite": "classify",
  "prompt_file": "prompts/classify_v1.txt",
  "prompt_hash": "a19f40cc21b8",
  "runs": 10,
  "model": {"temperature": 0.0, "max_tokens": 256},
  "totals": {
    "cases": 63,
    "passed": 14,
    "failed": 49,
    "flaky": 0,
    "tokens_in": 44100,
    "tokens_out": 7100,
    "wall_ms": 109804
  },
  "cases": [
    {
      "id": "c001",
      "status": "pass",
      "pass_rate": 1.0,
      "tokens_out_avg": 11,
      "assertions": [
        {"type": "json_valid", "passed": 10, "failed": 0}
      ],
      "failures": []
    }
  ]
}
```

**Key Fields**:
- `status`: "pass" (1.0), "fail" (0.0), or "flaky" (0 < rate < 1.0)
- `pass_rate`: Fraction of runs where all assertions passed
- `prompt_hash`: First 12 chars of SHA-256(prompt bytes) — identifies prompt version
- `tokens_in`, `tokens_out`: Token counts using rule `ceil(len(text) / 4)`

---

## Determinism & Flaky Behavior

A **flaky** case is one that passes sometimes and fails other times (when running at temperature > 0.0 or with non-deterministic models).

**Why it matters**: Flaky tests indicate the model's non-determinism, which affects real-world reliability.

**Fixing flaky tests**:
1. Lower temperature toward 0.0 (more deterministic)
2. Improve prompt clarity (reduce ambiguity)
3. Adjust assertions to be more robust (less strict matching)

**Example**: If a case passes 7/10 times with pass_rate=0.7, it's flaky.

---

## Error Messages & Recovery

| Message | Exit Code | Recovery |
|---------|-----------|----------|
| `suite: cannot read file` | 4 | Check suite path, verify file exists and is readable |
| `suite: JSON parse error` | 1 | Validate JSON with `jq suites/file.json` |
| `suite: schema violation` | 1 | Check required fields (name, prompt_file, model, runs, cases) |
| `report: cannot read file` | 4 | Check report path, verify file exists |
| `compare: --baseline is required` | 1 | Provide `--baseline` argument |
| `✗ Model binary: stubmodel.py not found` | 1 | Run `python stubmodel.py --help` to verify model availability |

---

## Token Accounting

Token count uses the rule: **tokens = ceil(len(text) / 4)**

Applied everywhere:
- Prompt text
- Input text
- Model output
- Report totals

**Why**: Approximates actual LLM token usage without tokenizer dependency.

---

## Cost Analysis

Use `compare` to measure cost delta between versions.

**Example**:
```bash
python -m promptlab compare --baseline v1.json --candidate v2.json | jq '.cost_delta'
```

Output:
```json
{
  "tokens_in_delta": 500,
  "tokens_in_pct": 5.2,
  "tokens_out_delta": -200,
  "tokens_out_pct": -4.1
}
```

**Interpretation**:
- Candidate uses 5.2% more input tokens
- Candidate produces 4.1% fewer output tokens
- Overall cost impact: slight increase
- Is the accuracy gain worth the extra cost?

---

## Next Steps

1. Run `python -m promptlab doctor` to verify setup
2. Create a suite: `suites/my-suite.json`
3. Run baseline: `python -m promptlab run --suite suites/my-suite.json --runs 10 --out baseline.json`
4. Iterate on prompt to improve accuracy
5. Compare versions: `python -m promptlab compare --baseline baseline.json --candidate candidate.json`
6. Check IMPROVEMENT.md for iteration history

**Questions?** See PROMPTS.md for key decisions, or JOURNAL.md for learnings.
