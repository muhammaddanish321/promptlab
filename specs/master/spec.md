# promptlab Specification

**Status**: Active (team decisions recorded 2026-09-16)
**Version**: 1.0
**Last Updated**: 2026-09-16

## Project Overview

promptlab is a command-line test runner for prompts. It evaluates assertions on model outputs, tracks pass/fail/flaky outcomes across multiple runs, and compares prompt versions to detect regressions and improvements.

**Key insight**: Non-determinism is the core problem. At temperature > 0, the same case does not always produce the same result. This tool distinguishes three outcomes, not two: pass, fail, and flaky.

---

## Clarifications

### Session 2026-09-16

- Q: Flaky policy — what pass rate counts as pass? → A: Flaky = 0 < pass_rate < 1.0. Any mixed result (some passes, some failures) is flaky, not a pass.
- Q: Fenced JSON handling — valid or not? → A: Accept fenced JSON. Extract inner JSON from markdown code blocks and parse it. Apply consistently to both json_valid and json_field_equals.
- Q: Regression threshold — any drop or only significant? → A: Any drop in pass_rate counts as regression. Catches silent degradation (1.0 → 0.9 is a regression).
- Q: Assertion evaluation — all or stop-first? → A: Evaluate all assertions in every run. Required by MUST 12 (per-assertion pass/fail counts).
- Q: Cost accounting — totals or averages? → A: Report both. Include totals across all runs AND average per run for transparency.

---

## 1. CLI Contract (Mandatory, Exactly As Specified)

### Command: `run`

```bash
promptlab run --suite <file> [--runs N] [--out report.json] [--report]
```

**Arguments**:
- `--suite <file>`: Path to suite JSON file (required).
- `--runs N`: Number of times to run each case. Overrides runs in suite file. (optional, default: value in suite)
- `--out <report.json>`: Path to write JSON report. If omitted, report goes to stdout; human-readable output goes to stderr.
- `--report`: Print human-readable summary to stderr (pass, fail, flaky counts; total tokens; wall time; worst offenders).

**Output**:
- Stdout: JSON report (if `--out` not specified) or human summary (if `--report` flag, to stderr).
- Stderr: Human-readable output (if `--out` specified and `--report` flag).

**Exit Codes**:
- 0: All cases passed.
- 1: Bad usage or malformed suite.
- 2: One or more cases failed.
- 3: Model could not be invoked.
- 4: Suite or report file unreadable.

---

### Command: `compare`

```bash
promptlab compare --baseline <report.json> --candidate <report.json> [--out diff.json]
```

**Arguments**:
- `--baseline <report.json>`: Path to baseline report.
- `--candidate <report.json>`: Path to candidate report.
- `--out <diff.json>`: Path to write diff. If omitted, diff goes to stdout.

**Output**:
- Stdout: JSON diff (if `--out` not specified).
- JSON diff structure (see section 5).

**Exit Codes**:
- 0: Reports are comparable and diff is produced.
- 1: Bad usage or malformed report.
- 4: Report file unreadable.

---

### Command: `doctor`

```bash
promptlab doctor
```

**Purpose**: Diagnostic utility for environment setup.

**Checks**:
- Python version (3.10+).
- Model binary reachable and responding (call with `--help`).
- Suites discoverable (look for `suites/` directory).
- Assertion types registered (list all 8).

**Output**: Human-readable diagnostic report to stdout.

**Exit Codes**:
- 0: All checks pass.
- 1: One or more checks fail.

---

## 2. Suite Format (Fixed, You Consume It)

Suite files are JSON. Required structure:

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
      "input": "text string" | {"file": "relative/path.txt"},
      "assert": [
        { "type": "json_valid" },
        { "type": "json_field_equals", "field": "category", "value": "billing" },
        { "type": "not_contains", "value": "Sure" },
        { "type": "max_tokens", "value": 40 },
        { "type": "finish_is", "value": "stop" }
      ]
    }
  ]
}
```

**Key Rules**:
- `prompt_file`: Path relative to the suite file, not the working directory.
- `input`: Either a string or `{"file": "path"}`. If file, path is relative to suite file.
- `--runs` on command line overrides `runs` in the file.
- All fields required except `--out` on CLI.

---

## 3. The Eight Assertion Types (All Mandatory)

### 3.1 `contains`

**Fields**: `value` (required), `ignore_case` (optional bool, default false).

**Passes when**: The output contains the substring `value`.

**Behavior**: Case-sensitive unless `ignore_case: true`.

---

### 3.2 `not_contains`

**Fields**: `value` (required), `ignore_case` (optional bool, default false).

**Passes when**: The output does not contain the substring `value`.

**Behavior**: Case-sensitive unless `ignore_case: true`.

---

### 3.3 `equals`

**Fields**: `value` (required), `normalize` (optional bool, default false).

**Passes when**: The output equals `value` exactly, or after normalization if `normalize: true`.

**Normalization**: Strip leading/trailing whitespace, collapse interior whitespace to single spaces.

---

### 3.4 `matches`

**Fields**: `pattern` (required, regex).

**Passes when**: The regex finds a match anywhere in the output.

**Behavior**: Case-sensitive. Invalid regex → exit code 1 (bad usage).

---

### 3.5 `json_valid`

**Fields**: None.

**Passes when**: The output parses as valid JSON, including fenced JSON code blocks.

**Fenced JSON handling** (DECIDED): The model sometimes wraps JSON in a fenced code block:
```
```json
{...}
```
```

Fenced JSON is accepted as valid. Extract the inner JSON and parse it. This applies consistently to both `json_valid` and `json_field_equals`.

**Parsing rule**: If output matches the pattern ` ```(language)?\n<json>\n``` `, extract the inner JSON. Otherwise, parse the output as-is.

---

### 3.6 `json_field_equals`

**Fields**: `field` (required, dotted path), `value` (required).

**Passes when**: The output parses as JSON, and resolving the dotted path equals `value`.

**Dotted-path resolution**: `foo.bar.0.baz` resolves as:
1. Parse output as JSON → object
2. Get key "foo" → object
3. Get key "bar" → array
4. Get index 0 → object
5. Get key "baz" → value
6. Compare to `value`.

**Array indexing** (DECIDED): Numeric indices are supported (0-based). Negative indices are NOT supported.
- `items.0.name` resolves to items[0]["name"].
- `items.-1.name` is invalid and causes assertion failure.

**Type coercion** (DECIDED): Strict equality. No type coercion.
- If path resolves to integer `42` and we compare to string `"42"`, they do NOT match.
- JSON types must match exactly: object, array, string, number, boolean, null.

---

### 3.7 `max_tokens`

**Fields**: `value` (required, int, threshold).

**Passes when**: The response field `tokens_out` is at or below `value`.

**Source of truth**: The `tokens_out` field from the model's JSON response.

---

### 3.8 `finish_is`

**Fields**: `value` (required, one of: "stop", "length", "refusal").

**Passes when**: The response field `finish` equals the specified value.

**Source of truth**: The `finish` field from the model's JSON response.

---

## 4. Assertion Evaluation Model

**DECIDED**: Evaluate all assertions in every run. Do not stop at first failure.

**Rationale**: MUST 12 requires "per-assertion counts: for each assertion, how many runs it passed and failed." To fulfill this, all assertions must evaluate on every run.

**Consequence**: Report includes per-assertion pass/fail counts, allowing pinpoint debugging. Example:
```json
{
  "type": "json_valid",
  "passed": 3,
  "failed": 0
},
{
  "type": "json_field_equals",
  "passed": 2,
  "failed": 1
}
```

This shows that 2 out of 3 runs succeeded at extracting the field, even if the case as a whole is flaky.

---

## 5. Report Schema (Fixed, Judges Diff It)

### 5.1 Top-Level Structure

```json
{
  "suite": "suite-name",
  "prompt_file": "relative/path.txt",
  "prompt_hash": "a19f40cc21b8",
  "runs": 3,
  "model": {
    "temperature": 0.4,
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

### 5.2 Field Definitions

**Top-level**:
- `suite` (string): Suite name from suite file.
- `prompt_file` (string): Path to prompt, relative to suite file.
- `prompt_hash` (string): First 12 hex characters of SHA-256(prompt_bytes). Used by `compare` to detect self-comparison.
- `runs` (int): Number of runs executed.
- `model` (object): Model configuration {temperature, max_tokens}.

**totals**:
- `cases` (int): Total number of cases in suite.
- `passed` (int): Cases with status "pass".
- `failed` (int): Cases with status "fail".
- `flaky` (int): Cases with status "flaky".
- `tokens_in` (int): Total tokens input across all runs and cases.
- `tokens_out` (int): Total tokens output across all runs and cases.
- `wall_ms` (int): Wall-clock time in milliseconds.

**cases[].assertions[].passed/failed**: Count of runs where each assertion passed/failed.

**cases[].failures**: Array of failure details for debugging (see section 5.3).

### 5.3 Failure Details

For each run where assertions failed, capture:

```json
{
  "run": 1,
  "assertion": { "type": "json_field_equals", "field": "category", "value": "billing" },
  "actual": "account_issue",
  "output_truncated": "actual output (truncated to 500 chars for large responses)"
}
```

---

## 6. Flaky Policy and Threshold

**DECIDED**: Flaky = 0 < pass_rate < 1.0 (any mixed result).

A case is classified as:
- **pass**: pass_rate = 1.0 (passed all runs)
- **fail**: pass_rate = 0.0 (failed all runs)
- **flaky**: 0 < pass_rate < 1.0 (passed some, failed others)

Examples:
- 10 runs, 10 passes → status = "pass"
- 10 runs, 0 passes → status = "fail"
- 10 runs, 7 passes, 3 fails → status = "flaky"
- 2 runs, 1 pass, 1 fail → status = "flaky"

**Rationale**: Strict detection of instability. Aligns with the brief's core message: "A case that passes 7 times out of 10 is not a passing case, and reporting it as one is the most common way a prompt harness lies to its owner."

**Consequence**: High-temperature suites require sufficient --runs to achieve stability. A case that flickers is not hidden or reported as passing.

---

## 7. Fenced JSON Decision

**DECIDED**: Accept fenced JSON. Extract and parse the inner JSON.

The model's output may include markdown code fences:
```
```json
{"category": "billing"}
```
```

**Parsing logic**:
1. If output matches pattern ` ```(lang)?\n<content>\n``` `, extract <content>.
2. Parse the extracted (or original) text as JSON.
3. If parsing succeeds, the assertion passes. If it fails, the assertion fails.

**Consistency**: This rule applies to both `json_valid` and `json_field_equals`. Both must accept fenced JSON.

**Rationale**: Real-world models often wrap JSON in fences. This is a pragmatic choice that reduces friction. Judges will understand this reasoning.

---

## 8. Regression Definition

**DECIDED**: A regression is any drop in pass_rate, regardless of magnitude.

From MUST 15: "A pass rate moving from 1.0 to 0.9 is a regression even if the case is still labelled a pass under your policy. Silent degradation is exactly what this tool exists to catch."

**Examples**:
- 1.0 → 0.9: regression ✓
- 1.0 → 0.5: regression ✓
- 0.8 → 0.7: regression ✓
- 0.6 → 0.6: unchanged (no change)
- 0.5 → 0.8: improved ✓

**Rationale**: Strict detection. The purpose of this tool is to catch subtle performance degradation. The judge of what is "acceptable noise" should be the user, not the tool.

---

## 9. Cost Accounting

**DECIDED**: Report both totals and averages for full transparency.

**Totals** (in `totals` section):
- `tokens_in`: Sum of all tokens_in across all runs and cases.
- `tokens_out`: Sum of all tokens_out across all runs and cases.
- Reflects true resource usage and cost.

**Averages** (in `cases[].tokens_out_avg`):
- Per-case average output tokens: `tokens_out / runs`.
- Per-run average: can be computed as `totals.tokens_out / totals.cases / runs`.
- Allows comparison across different --runs values.

**In compare output** (cost_delta):
- Report totals delta: `baseline_total - candidate_total`.
- Report percentage delta: `(candidate_total - baseline_total) / baseline_total * 100%`.
- Example: baseline 1000 tokens → candidate 1100 tokens = +10% cost delta.

**Rationale**: Judges need both views. Totals show resource impact; averages show efficiency.

---

## 10. Compare Output Schema

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
    },
    {
      "id": "c003",
      "status": "improved",
      "baseline_pass_rate": 0.6,
      "candidate_pass_rate": 1.0
    },
    {
      "id": "c004",
      "status": "new",
      "candidate_pass_rate": 1.0
    },
    {
      "id": "c005",
      "status": "removed"
    }
  ],
  "cost_delta": {
    "tokens_in_delta": 120,
    "tokens_in_pct": 2.9,
    "tokens_out_delta": -45,
    "tokens_out_pct": -4.6
  },
  "warnings": [
    "Same prompt_hash; comparing report against itself?",
    "Different suites; results may not be comparable.",
    "Different model settings; temperature differs."
  ]
}
```

**Case statuses**:
- `unchanged`: Pass rate unchanged.
- `regressed`: Pass rate dropped.
- `improved`: Pass rate improved.
- `new`: Case in candidate but not in baseline.
- `removed`: Case in baseline but not in candidate.

**Warnings** (from MUST 17):
- Same prompt_hash → likely self-comparison.
- Different suite names → different test sets.
- Different model settings (temperature, max_tokens) → results not directly comparable.

---

## 11. Failure Taxonomy (One-Line Messages + Exit Codes)

### 11.1 Exit Code 1 (Bad Usage or Malformed Suite)

| Error | Message | Example |
|-------|---------|---------|
| Missing required argument | `run: --suite is required` | — |
| Unknown argument | `run: unknown argument --foo` | — |
| Suite file parse error | `suite: JSON parse error at line 5: ...` | — |
| Missing required field | `suite: missing field 'cases' at root` | — |
| Wrong field type | `suite: field 'runs' must be int, got string` | — |
| Unknown assertion type | `assertion c001: unknown type 'json_schema'` | — |
| Invalid regex in `matches` | `assertion c001: regex compile error: ...` | — |
| Missing prompt file | `prompt file 'prompts/bad.txt' not found (relative to suite)` | — |

### 11.2 Exit Code 3 (Model Not Invokable)

| Error | Message |
|-------|---------|
| Model binary not found | `model: stubmodel.py not found or not executable` |
| Model subprocess error | `model: subprocess error: ... (exit code 2)` |
| Model response parse error | `model: response is not valid JSON` |

### 11.3 Exit Code 4 (File Unreadable)

| Error | Message |
|-------|---------|
| Suite file not readable | `suite: cannot read file (permission denied)` |
| Report file not readable | `report: cannot read file (permission denied)` |
| Input file referenced in suite | `input: cannot read file 'relative/path' (file not found)` |

### 11.4 Exit Code 2 (Cases Failed)

Not an error; a result. Exit code 2 indicates that one or more cases failed during execution.

---

## 12. Model Invocation

**CLI Contract**:

```bash
python stubmodel.py \
  --prompt <prompt-file-path> \
  --input <text|@file-path> \
  [--temperature 0.0] \
  [--seed N] \
  [--max-tokens 256] \
  [--call-index N]
```

**Constraints**:
- Never import or reimplement stubmodel.py. Call as subprocess only.
- Judges swap in a different binary; our harness must not assume anything about the model's behavior beyond what the CLI contract guarantees.

**Token Counting**:
- Everywhere in this project: `tokens = math.ceil(len(text) / 4)`.
- This applies to: prompt tokens, input tokens, output tokens, and any reported token counts in our tool.

**Determinism**:
- At `--temperature 0.0`, the model is byte-for-byte deterministic. Same prompt, same input → same output, always.
- Above 0.0, output is non-deterministic without `--seed`.

---

## 13. Path Resolution Rules

**Suite file paths are relative to the suite file location, not the working directory.**

Examples:
- Suite at `suites/smoke.json` specifies `"prompt_file": "prompts/classify_v1.txt"`.
- Resolved path: `suites/prompts/classify_v1.txt` (relative to suite directory).

**Input file paths follow the same rule**:
- Suite at `suites/smoke.json` specifies `"input": {"file": "data/tickets.json"}`.
- Resolved path: `suites/data/tickets.json`.

---

## 14. Determinism and Report Consistency

**At temperature 0**:
- Running the same suite twice with the same `--runs` N produces byte-identical JSON reports.
- Exception: Timing fields (`wall_ms`) may differ slightly.
- **Isolation strategy**: Separate timing fields from deterministic fields so a diff of two runs shows only timing changes.

**Key implications**:
- JSON key ordering must be deterministic (use sorted keys or explicit ordering).
- All numeric values must be stable (no floating-point rounding drift).
- Randomness in assertion evaluation must not affect the report (or must be seeded).

---

## 15. Definition of Done

A implementation phase is complete when:

- [ ] All assertions for the phase pass their test cases.
- [ ] `python -m unittest` passes (all harness tests pass).
- [ ] `promptlab run --suite suites/smoke.json --report` executes end-to-end without error.
- [ ] JSON output conforms to the report schema (validated against a schema checker or manual inspection).
- [ ] Error handling produces one-line messages with correct exit codes.
- [ ] At temperature 0, repeated runs of the same suite produce byte-identical reports (apart from wall_ms).
- [ ] Code is simple and readable; every team member can explain it.

---

## 16. Hidden-Suite Categories (From Brief)

At judging, the harness is tested against suites in these categories:

1. **Empty and minimal suites**
   - Empty suite (no cases).
   - Suite with one case and zero assertions.

2. **Malformed suites**
   - Missing required fields (e.g., no "cases").
   - Wrong field types (e.g., "runs": "three" instead of 3).
   - Unknown assertion type.

3. **File not found**
   - Suite points to prompt file that does not exist.
   - Suite points to input file that does not exist.

4. **High-temperature flaky classification**
   - Suite with temperature > 0.0 and --runs 10.
   - Must correctly classify pass/fail/flaky per case.

5. **All cases fail**
   - Suite where every case fails.
   - Must exit code 2 (cases failed).

6. **Complex JSON and regex**
   - Invalid regex in `matches` assertion → exit 1.
   - Deeply nested JSON paths in `json_field_equals` (e.g., `level1.level2.level3.level4`).
   - JSON truncated mid-field by `--max-tokens`.

7. **Model refusal**
   - Case where model outputs `{"finish": "refusal", ...}`.
   - Assertions must handle this gracefully.

8. **Determinism verification**
   - Same suite run twice at temperature 0.
   - Diff must show only timing changes (wall_ms).

9. **Cross-prompt comparison**
   - Two reports from genuinely different suites.
   - Compare must flag as incomparable.

10. **Different model binary**
    - A different binary with the same CLI contract but different behavior.
    - Harness must not assume model output format beyond the contract.

---

## 17. Team Decisions Summary

| Decision | Choice | Rationale | Status |
|----------|--------|-----------|--------|
| Flaky Policy | 0 < pass_rate < 1.0 | Strict detection; matches brief intent | ✅ DECIDED |
| Fenced JSON | Accept and extract | Practical; handles real-world models | ✅ DECIDED |
| Regression Threshold | Any drop counts | Catches silent degradation | ✅ DECIDED |
| Assertion Evaluation | Evaluate all | Required by MUST 12 | ✅ DECIDED |
| Cost Accounting | Both totals and averages | Full transparency for judges | ✅ DECIDED |
| Array Indexing | 0-based, no negatives | Standard JSON path semantics | ✅ DECIDED |
| Type Coercion | Strict equality | JSON types must match exactly | ✅ DECIDED |

---

## 18. References

- **Brief**: `PROMPTLAB_Student_Brief.pdf`
- **Constitution**: `.specify/memory/constitution.md`
- **Claude Rules**: `CLAUDE.md`

---

**Next**: Team review and clarification of all [NEEDS CLARIFICATION] sections. Then commit SPEC.md alone before any implementation.
