# CLI Contract: `promptlab compare`

**Command**: `python -m promptlab compare --baseline <report.json> --candidate <report.json> [--out diff.json]`

---

## Arguments

### `--baseline <file>` (required)

**Type**: string (file path)  
**Validation**:
- File must exist and be readable
- File must be valid JSON
- JSON must conform to Report schema

**Behavior**:
- If missing → exit 1, message: "compare: --baseline is required"
- If file not found → exit 4, message: "report: cannot read file"
- If invalid → exit 1, message: "report: JSON parse error..."

---

### `--candidate <file>` (required)

**Type**: string (file path)  
**Validation**: Same as --baseline

---

### `--out <file>` (optional)

**Type**: string (file path)  
**Default**: stdout  
**Behavior**:
- If specified: Write JSON diff to file
- If omitted: Write JSON diff to stdout

---

## Output

### Stdout (if `--out` not specified)
```json
{
  "baseline_suite": "...",
  "candidate_suite": "...",
  "baseline_prompt_hash": "...",
  "candidate_prompt_hash": "...",
  "cases": [...],
  "cost_delta": {...},
  "warnings": [...]
}
```

### File (if `--out` specified)
Same JSON as stdout, written to file.

---

## Exit Codes

| Code | Meaning | Examples |
|------|---------|----------|
| 0 | Diff produced successfully | Reports are comparable |
| 1 | Bad usage or malformed report | Missing arg, invalid JSON, schema violation |
| 4 | File unreadable | Report file missing |

**Note**: Compare always succeeds if reports are valid (even if they show regressions).

---

## Case Classification

For each case in the union of baseline and candidate:

### Unchanged
- Condition: case in both reports, baseline_pass_rate = candidate_pass_rate
- Example: 1.0 → 1.0

### Regressed
- Condition: case in both reports, candidate_pass_rate < baseline_pass_rate
- Examples: 1.0 → 0.9, 0.8 → 0.7
- **Note**: Any drop is a regression (no threshold tolerance)

### Improved
- Condition: case in both reports, candidate_pass_rate > baseline_pass_rate
- Examples: 0.5 → 0.8, 0.0 → 0.5

### New
- Condition: case in candidate but not in baseline
- Example: Case added to suite in candidate version

### Removed
- Condition: case in baseline but not in candidate
- Example: Case deleted from suite in candidate version

---

## Cost Delta

**Calculation** (from totals):
```
tokens_in_delta = candidate_total_in - baseline_total_in
tokens_in_pct = (candidate_total_in - baseline_total_in) / baseline_total_in * 100

tokens_out_delta = candidate_total_out - baseline_total_out
tokens_out_pct = (candidate_total_out - baseline_total_out) / baseline_total_out * 100
```

**Semantics**:
- Positive pct = cost increased
- Negative pct = cost decreased
- Useful for evaluating: "Did accuracy gain justify the token cost?"

---

## Warnings

Emit warnings (non-fatal) when reports are incomparable:

### Same Prompt Hash
**Condition**: baseline_prompt_hash = candidate_prompt_hash  
**Message**: "Same prompt_hash; comparing report against itself?"  
**Significance**: Indicates potential user error (comparing v1 to v1)

### Different Suites
**Condition**: baseline_suite ≠ candidate_suite  
**Message**: "Different suites; results may not be comparable."  
**Significance**: Different test sets; metrics may not align

### Different Model Settings
**Condition**: baseline.model.temperature ≠ candidate.model.temperature OR baseline.model.max_tokens ≠ candidate.model.max_tokens  
**Message**: "Different model settings (temperature or max_tokens); results may not be comparable."  
**Significance**: Different configurations; pass rates may not be comparable

---

## Error Messages (One-Line Only)

Examples:
- `compare: --baseline is required`
- `compare: --candidate is required`
- `report: cannot read file (permission denied)`
- `report: JSON parse error at line 5: ...`
- `report: schema violation: missing field 'totals'`

---

## Determinism

**Guarantee**: Comparing the same two reports always produces the same diff JSON.

**Implementation**:
- Sort case IDs (deterministic order)
- Classification rules are deterministic (any drop = regressed)
- Cost delta calculation is deterministic

---

## Edge Cases

### Self-Comparison
**Input**: --baseline report.json --candidate report.json (same file)  
**Behavior**: Produces diff with all cases "unchanged" and cost_delta = 0  
**Warning**: Emitted ("Same prompt_hash...") to alert user

### Empty Diffs
**Input**: baseline and candidate have no cases in common  
**Behavior**: Produces diff with only "new" and "removed" cases  
**Result**: Likely indicates user error or suite restructure

### Baseline Only / Candidate Only
**Input**: baseline or candidate is missing  
**Behavior**: Exit code 4 (file unreadable) before classification

---

**Next**: CLI Contract for `doctor`
