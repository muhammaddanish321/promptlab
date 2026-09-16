# Research & Design Decisions

**Date**: 2026-09-16  
**Feature**: promptlab  
**Status**: Complete (all unknowns resolved)

---

## Flaky Classification Policy

**Decision**: Flaky = 0 < pass_rate < 1.0 (any mixed result)

**Rationale**:
- Brief MUST 10: "distinguish three outcomes, not two: pass, fail, flaky"
- Brief: "case that passes 7 times out of 10 is not a passing case"
- Core problem: non-determinism must be made visible, not hidden
- Strict policy catches subtle regressions

**Alternatives Considered**:
- Threshold-based (e.g., ≥ 0.9 is pass): Rejected as arbitrary and hides instability
- Run-dependent threshold (lower for --runs 2, higher for --runs 100): Rejected as over-engineered

**Implementation**: Compare pass_rate to strict boundaries (1.0, 0.0, or in-between)

---

## Fenced JSON Extraction

**Decision**: Accept fenced JSON. Extract inner JSON and parse it.

Example: ` ```json\n{...}\n``` ` → extract and parse inner JSON

**Rationale**:
- Models commonly wrap JSON in markdown code fences
- Practical for real-world usage; penalizes reasonable formatting if rejected
- Both `json_valid` and `json_field_equals` must apply consistently

**Alternatives Considered**:
- Reject fenced JSON entirely: Rejected as too strict; breaks real workflows
- Accept only in `json_valid`, not `json_field_equals`: Rejected as inconsistent and confusing

**Implementation**: Regex pattern `^```(?:\w+)?\s*\n([\s\S]*?)\n```\s*$` to extract; then parse

---

## Regression Detection: Any Drop

**Decision**: Any drop in pass_rate counts as regression, regardless of magnitude.

**Rationale**:
- Brief MUST 15: "1.0 to 0.9 is a regression even if still labelled a pass"
- Core purpose: "catch silent degradation"
- User should judge acceptability; tool should report what changed

**Alternatives Considered**:
- Threshold-based (≥ 0.05 drop): Rejected as hiding real degradation
- Statistical model (depends on --runs and confidence): Rejected as over-engineered

**Implementation**: Classification: regressed if candidate_rate < baseline_rate

---

## Cost Accounting: Totals + Averages

**Decision**: Report both totals (sum across all runs) and averages (per-run/per-case).

**Rationale**:
- Totals show true resource cost (for budgeting)
- Averages normalize across different --runs values (for comparison)
- Both views give judges complete picture; no ambiguity

**Alternatives Considered**:
- Totals only: Rejected as incomplete (doesn't show efficiency)
- Averages only: Rejected as misleading (hides true cost)
- Differential: Rejected as over-granular

**Implementation**:
- In `run` report: `totals.tokens_in/out` and `cases[].tokens_out_avg`
- In `compare`: delta (absolute change) and percentage change

---

## Assertion Evaluation: All Assertions

**Decision**: Evaluate all assertions on every run. Do not stop at first failure.

**Rationale**:
- Brief MUST 12: "per-assertion counts: for each assertion, how many runs it passed and failed"
- Diagnostic detail: know exactly which assertion is flaky
- Required to fulfill spec

**Alternatives Considered**:
- Stop at first failure: Rejected as violating MUST 12 (no per-assertion data)
- Partial evaluation: Rejected as inconsistent and incomplete

**Implementation**: Loop through all assertions, record pass/fail for each, aggregate for case

---

## Token Counting Rule

**Decision**: `tokens = math.ceil(len(text) / 4)` everywhere

**Rationale**:
- Brief: "Token rule everywhere in this project, including inside your own reports"
- Simple, deterministic, works consistently
- Applied to: prompt tokens, input tokens, output tokens, reported totals

**Implementation**: Single function `compute_tokens(text: str) -> int` used everywhere

---

## Error Handling: Exit Codes

**Decision**: Strict exit code mapping (0, 1, 2, 3, 4)

| Code | Meaning | Example |
|------|---------|---------|
| 0 | All cases passed | ✓ All assertions passed all runs |
| 1 | Bad usage or malformed suite | Malformed JSON, unknown assertion type, invalid regex |
| 2 | Cases failed (result, not error) | ✓ One or more cases failed |
| 3 | Model not invokable | Binary absent, subprocess error, response not JSON |
| 4 | File unreadable | Suite file missing, report file missing, input file not found |

**Rationale**:
- Clear exit codes allow CI/CD pipelines to distinguish failures
- Exit code 2 is a "result" not an "error" (judges depend on this distinction)
- One-line messages only; no tracebacks (brief MUST 9)

---

## JSON Schema Decisions

**Suite Input Path Resolution**:
- Paths in `prompt_file` and `input.file` are relative to suite file location, not working directory
- Rationale: Suites are portable; relative paths keep them self-contained

**Dotted Path Resolution** (for `json_field_equals`):
- Support 0-based array indices: `items.0.name` → items[0]["name"]
- Do NOT support negative indices: `items.-1` is invalid
- Strict type equality: 42 ≠ "42" (no type coercion)
- Invalid paths fail the assertion (don't throw exceptions)

---

## Determinism at Temperature 0

**Decision**: At `--temperature 0.0`, running the same suite twice produces byte-identical reports (except timing fields).

**Rationale**:
- Model determinism is a feature we leverage
- Allows diff-based regression testing ("Did this change break anything?")
- Requires consistent JSON key ordering and numeric formatting

**Implementation**:
- Sort JSON keys (or use ordered structure)
- Format numbers consistently (no floating-point rounding)
- Isolate timing field (wall_ms) so it can vary without affecting diffs

---

## Summary Table

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Flaky policy | 0 < rate < 1.0 | Strict but honest |
| Fenced JSON | Extract and parse | More practical, slight complexity |
| Regression | Any drop | Catches all degradation |
| Assertions | Evaluate all | More diagnostic, slightly slower |
| Cost | Totals + averages | Complete picture, more output |
| Exit codes | 0/1/2/3/4 | Clear semantics for CI |
| Token rule | ceil(len/4) | Simple and consistent |
| Determinism | Byte-identical at temp 0 | Enables diff-based testing |

---

**Status**: ✅ All unknowns resolved. Ready for data-model.md and contracts/.
