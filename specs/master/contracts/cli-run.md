# CLI Contract: `promptlab run`

**Command**: `python -m promptlab run --suite <file> [--runs N] [--out report.json] [--report]`

---

## Arguments

### `--suite <file>` (required)

**Type**: string (file path)  
**Validation**:
- File must exist and be readable
- File must be valid JSON
- JSON must conform to Suite schema

**Behavior**:
- If missing → exit 1, message: "run: --suite is required"
- If file not found → exit 4, message: "suite: cannot read file"
- If JSON invalid → exit 1, message: "suite: JSON parse error at line N: ..."
- If schema violation → exit 1, message: "suite: missing field 'cases' at root"

---

### `--runs N` (optional)

**Type**: integer ≥ 1  
**Default**: Value from suite file (or 1 if not specified in suite)  
**CLI Override**: `--runs` overrides suite file value

**Behavior**:
- If N ≤ 0 → exit 1, message: "run: --runs must be ≥ 1"
- Actual behavior: Run each case N times; compute pass_rate = passed_count / N

---

### `--out <file>` (optional)

**Type**: string (file path)  
**Default**: stdout  
**Behavior**:
- If specified: Write JSON report to file (create or overwrite)
- If omitted: Write JSON report to stdout, human summary to stderr

---

### `--report` (optional)

**Type**: flag (boolean)  
**Default**: false  
**Behavior**:
- If specified: Print human-readable summary after JSON report
- Format: "X passed, Y failed, Z flaky. Tokens: in=... out=... Wall: ...ms"
- Output destination: stderr

---

## Output

### Stdout (if `--out` not specified)
```
{
  "suite": "...",
  "prompt_file": "...",
  ...report JSON...
}
```

### Stderr (if `--report` specified or `--out` specified)
```
Smoke Test Suite Results:
  Cases: 20 | Passed: 16 | Failed: 3 | Flaky: 1
  Tokens: in=4120 out=980 avg_out=49
  Wall time: 8640ms
```

### File (if `--out` specified)
Same JSON as stdout, written to file.

---

## Exit Codes

| Code | Meaning | Examples |
|------|---------|----------|
| 0 | All cases passed | All cases status = "pass" |
| 1 | Bad usage or malformed suite | Missing --suite, invalid JSON, unknown assertion type |
| 2 | One or more cases failed | Any case status = "fail" or "flaky" |
| 3 | Model not invokable | Binary absent, subprocess error, response not JSON |
| 4 | File unreadable | Suite file missing, prompt file missing, input file missing |

**Note**: Exit code 2 is a **result**, not an error. CI/CD pipelines depend on this distinction.

---

## Model Invocation

**CLI**: `python stubmodel.py --prompt <file> --input <text|@file> [--temperature T] [--seed N] [--max-tokens M] [--call-index N]`

**Requirements**:
- Must be executable (or runnable via python)
- Must respond to `--help` (for doctor checks)
- Must output valid JSON to stdout
- Exit code 0 = OK; 2 = bad args; 3 = file error

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

---

## Error Messages (One-Line Only)

**No tracebacks. No multi-line output for errors.**

Examples:
- `suite: JSON parse error at line 5: ...`
- `prompt file 'prompts/bad.txt' not found (relative to suite)`
- `assertion c001: unknown type 'json_schema'`
- `model: stubmodel.py not found or not executable`

---

## Determinism at Temperature 0.0

**Guarantee**: Running the same suite twice with the same `--runs` produces byte-identical JSON reports (except `wall_ms`).

**Implementation**:
- Sort JSON keys (or use ordered dict)
- Format floats consistently
- All random seeds set from input
- Only wall_ms varies

---

## Timeout Handling

**Recommendation**: Consider implementing timeout for model subprocess (e.g., 30s per call).

**Behavior**: If model hangs or exceeds timeout:
- Exit code 3 (model not invokable)
- Message: "model: subprocess timeout or no response"

---

## Temperature & Seed

**Temperature 0.0** (deterministic):
- Same input → same output, always
- No seed needed (or seed is ignored)

**Temperature > 0.0** (non-deterministic):
- Same input → different output (unless --seed specified)
- With --seed: Reproducible across runs
- Multiple runs with same seed → same output per run, but seed varies between runs (non-deterministic across runs)

---

**Next**: CLI Contract for `compare` and `doctor`
