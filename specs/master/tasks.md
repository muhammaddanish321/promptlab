# Tasks: promptlab

**Feature**: promptlab — Command-line test runner for prompts  
**Date**: 2026-09-16  
**Status**: Ready for implementation  

---

## Overview

Tasks are organized by implementation phase, following the 5-phase plan:
1. **Phase 1**: CLI Skeleton + Suite Loading (T001–T012)
2. **Phase 2**: Model Invocation + Assertions + Run Command (T013–T040)
3. **Phase 3**: Compare + Doctor (T041–T055)
4. **Phase 4**: Prompt Improvement Track (T056–T070)
5. **Phase 5**: Documentation + Context (T071–T080)

Each phase is independently testable. Tasks marked `[P]` can run in parallel (different files, no inter-task dependencies). Each task includes the exact file path.

---

## Phase 1: CLI Skeleton + Suite Loading

**Goal**: Parse arguments, load and validate suite JSON, establish error handling with correct exit codes.

**Acceptance Criteria**:
- ✅ `python -m promptlab run --suite suites/smoke.json` parses args
- ✅ Malformed suite files produce exit code 1 with one-line message
- ✅ `python -m unittest tests.test_suite_loading` passes
- ✅ Code is simple and readable

### Setup & Project Structure

- [X] T001 Create package structure: `promptlab/__init__.py`, `__main__.py`, directories for tests and fixtures
- [X] T002 [P] Create `promptlab/__init__.py` with package version and metadata
- [X] T003 [P] Create `promptlab/__main__.py` as entry point (import and call cli.main())
- [X] T004 [P] Create empty module files: `promptlab/cli.py`, `promptlab/suite.py`, `promptlab/model.py`, `promptlab/assertions.py`, `promptlab/runner.py`, `promptlab/report.py`, `promptlab/compare.py`, `promptlab/doctor.py`

### CLI Argument Parsing

- [X] T005 Implement `promptlab/cli.py` with argparse for `run`, `compare`, `doctor` commands with all required/optional arguments from contracts
- [X] T006 [P] Implement run command handler: `run_command(args)` stub that parses args and calls suite loader
- [X] T007 [P] Implement compare command handler: `compare_command(args)` stub (placeholder for Phase 3)
- [X] T008 [P] Implement doctor command handler: `doctor_command(args)` stub (placeholder for Phase 3)
- [X] T009 Implement error handling in cli.py: catch errors from suite loading, emit one-line messages, exit with correct codes (1 for bad usage, 4 for file not found)

### Suite Loading & Validation

- [X] T010 Implement `promptlab/suite.py` with `load_suite(file_path: str) -> dict` function that reads JSON and validates schema
- [X] T011 [P] Implement `validate_suite(data: dict) -> tuple(bool, str)` that checks all required fields and types (from data-model.md)
- [X] T012 [P] Implement `resolve_paths(suite: dict, suite_dir: str) -> dict` that makes prompt_file and input file paths absolute relative to suite location

### Unit Tests for Phase 1

- [X] T013 Create `tests/test_suite_loading.py` with unit tests for:
  - ✅ Valid suite loads successfully
  - ✅ Missing required field → validation fails with message
  - ✅ Wrong field type → validation fails
  - ✅ Unknown assertion type → validation fails
  - ✅ File not found → error caught, exit code 4
  - ✅ Invalid JSON → error caught, exit code 1
  - ✅ File paths resolve correctly (relative to suite, not working directory)

### Phase 1 Completion

- [X] T014 Run `python -m unittest tests.test_suite_loading` and verify all tests pass
- [X] T015 Run `python -m promptlab run --suite suites/smoke.json` and verify it loads suite without error (even if no assertions evaluate yet)
- [X] T016 Verify code is simple, readable, no premature abstractions

**Dependencies**: None (Phase 1 is foundational)

---

## Phase 2: Model Invocation + Assertions + Run Command

**Goal**: Call model as subprocess, implement all 8 assertion types, generate reports, classify pass/fail/flaky.

**Acceptance Criteria**:
- ✅ All 8 assertions implemented and tested
- ✅ `python -m promptlab run --suite suites/smoke.json --report` executes end-to-end
- ✅ Report JSON matches schema exactly (totals, cases, per-assertion counts)
- ✅ Flaky classification works (0 < rate < 1.0 = flaky)
- ✅ At temperature 0.0, repeated runs produce byte-identical reports (except wall_ms)
- ✅ `python -m unittest tests.test_assertions tests.test_runner tests.test_report` pass

### Model Subprocess Invocation

- [X] T017 Implement `promptlab/model.py` with `invoke_model(prompt_file, input_text, temp, seed, max_tokens) -> dict`:
  - Call subprocess: `python stubmodel.py --prompt <file> --input <text> --temperature <T> ...`
  - Parse JSON response
  - Return dict with output, tokens_in, tokens_out, finish, latency_ms
  - Handle errors: binary not found (exit 3), subprocess error (exit 3), invalid JSON response (exit 3)
- [X] T018 [P] Implement timeout handling for model subprocess (e.g., 30 seconds)
- [X] T019 [P] Create `tests/fixtures/fake_model.py` that implements the same CLI contract as stubmodel.py for testing (accepts --prompt, --input, --temperature, outputs JSON)

### Assertion Implementation

- [X] T020 Implement `promptlab/assertions.py` with all 8 assertion types:
  - [X] T020a `contains(output, value, ignore_case=False) -> bool`
  - [X] T020b `not_contains(output, value, ignore_case=False) -> bool`
  - [X] T020c `equals(output, value, normalize=False) -> bool` (normalize = strip+collapse whitespace)
  - [X] T020d `matches(output, pattern) -> bool` (regex; invalid regex → return False, caller handles exit 1)
  - [X] T020e `json_valid(output) -> bool` (parse JSON; support fenced JSON extraction)
  - [X] T020f `json_field_equals(output, field, value) -> bool` (dotted path resolution; extract fenced JSON first)
  - [X] T020g `max_tokens(tokens_out, threshold) -> bool`
  - [X] T020h `finish_is(finish, expected) -> bool` (finish is one of stop, length, refusal)
- [X] T021 Implement fenced JSON extraction: `extract_fenced_json(output) -> str` using regex `^```(?:\w+)?\s*\n([\s\S]*?)\n```\s*$`
- [X] T022 [P] Implement dotted path resolution: `resolve_dotted_path(obj, path) -> any` for paths like `foo.bar.0.baz` (0-based indices only; no negatives)
- [X] T023 [P] Implement `evaluate_assertion(assertion_dict, output) -> bool` dispatcher that routes to the right assertion function

### Case Execution & Flaky Classification

- [X] T024 Implement `promptlab/runner.py` with `run_suite(suite, runs) -> list[case_results]`:
  - For each case: run N times
  - For each run: call model, evaluate all assertions, record pass/fail per assertion
  - Compute pass_rate = passed_count / runs
  - Classify status: pass (1.0), fail (0.0), or flaky (0 < rate < 1.0)
  - Return list of results with pass_rate, status, per-assertion counts, failures
- [X] T025 [P] Implement `classify_status(pass_rate: float) -> str` (pass/fail/flaky logic)
- [X] T026 [P] Implement `run_case(case, prompt_file, runs) -> dict` that executes one case N times and tracks results
- [X] T027 [P] Implement failure tracking: `failures` array with run number, assertion, actual output (truncated to 500 chars)

### Report Generation

- [X] T028 Implement `promptlab/report.py` with `generate_report(suite, cases_results, runs, start_time, end_time) -> dict`:
  - Build report JSON matching schema exactly (suite, prompt_file, prompt_hash, runs, model, totals, cases)
  - Compute prompt_hash: first 12 hex chars of SHA-256(prompt_bytes)
  - Totals: count cases, passed, failed, flaky; sum tokens_in, tokens_out; wall_ms = elapsed time
  - Per-case: id, status, pass_rate, tokens_out_avg, assertions (per-assertion counts), failures
  - **Determinism**: Use json.dumps with sort_keys=True
  - **Byte-identical at temp 0.0**: No floating-point rounding, consistent formatting
- [X] T029 [P] Implement `compute_tokens(text: str) -> int` using `math.ceil(len(text) / 4)` (used for reporting; also in model response)
- [X] T030 [P] Implement `compute_prompt_hash(prompt_bytes) -> str` (SHA-256, first 12 hex chars)
- [X] T031 Implement human-readable report output: `print_human_summary(report, file=stderr)` for --report flag (X passed, Y failed, Z flaky; tokens in/out; wall time)

### Unit Tests for Phase 2

- [X] T032 Create `tests/test_assertions.py` with unit tests for all 8 assertion types:
  - `contains`: exact match, case-insensitive, substring
  - `not_contains`: string absence
  - `equals`: exact equality, normalized equality
  - `matches`: regex match, invalid regex handled
  - `json_valid`: bare JSON, fenced JSON, invalid JSON
  - `json_field_equals`: nested paths, array indices, missing field, type strictness
  - `max_tokens`: threshold comparisons
  - `finish_is`: all three finish types
- [X] T033 Create `tests/test_runner.py` with unit tests for:
  - Case execution (N runs, pass/fail per assertion)
  - Flaky classification (1.0 pass, 0.0 fail, 0.7 flaky)
  - Failure tracking (correct run number, assertion, output)
- [X] T034 Create `tests/test_report.py` with unit tests for:
  - Report schema compliance (all required fields)
  - Totals calculation (passed + failed + flaky = cases)
  - Pass rate calculation (passed / runs)
  - Token calculations (ceil(len/4))
  - Prompt hash (SHA-256, first 12 chars)
  - Determinism (byte-identical repeated runs at temp 0.0)
- [X] T035 [P] Create `tests/test_model.py` with unit tests for:
  - Subprocess invocation (call with correct args)
  - JSON response parsing
  - Error handling (binary not found, subprocess error, invalid JSON)

### Phase 2 Completion

- [X] T036 Run `python -m promptlab run --suite suites/smoke.json --out report.json --report` and verify:
  - Report JSON written to file
  - Human summary printed to stderr
  - Exit code 0 (all passed)
- [X] T037 Run `python -m promptlab run --suite suites/smoke.json --runs 10` and verify pass_rate and flaky classification
- [X] T038 Run same suite twice at --temperature 0.0 and diff reports (should be identical except wall_ms)
- [X] T039 Run `python -m unittest tests.test_assertions tests.test_runner tests.test_report tests.test_model` and verify all pass
- [X] T040 Code review: Verify code is simple, readable, no premature abstractions

**Depends on**: Phase 1 (cli.py, suite loading)

---

## Phase 3: Compare + Doctor

**Goal**: Implement comparison logic, regression detection, environment diagnostics.

**Acceptance Criteria**:
- ✅ `python -m promptlab compare --baseline baseline.json --candidate candidate.json` produces diff
- ✅ Regression detection flags 1.0 → 0.9 drops
- ✅ Cost delta computed correctly
- ✅ Warnings issued for incomparable reports
- ✅ `python -m promptlab doctor` runs and checks all 4 items
- ✅ `python -m unittest tests.test_compare tests.test_doctor` pass

### Comparison Logic

- [X] T041 Implement `promptlab/compare.py` with `compare_reports(baseline, candidate) -> dict`:
  - For each case: classify as regressed, improved, unchanged, new, or removed
  - Regression: any drop in pass_rate (candidate < baseline)
  - Compute cost delta: tokens_in_delta, tokens_in_pct, tokens_out_delta, tokens_out_pct
  - Emit warnings: same prompt_hash, different suites, different model settings
  - Return diff JSON matching schema (baseline_suite, candidate_suite, cases, cost_delta, warnings)
- [X] T042 [P] Implement `classify_case(baseline_rate, candidate_rate) -> str` (regressed/improved/unchanged)
- [X] T043 [P] Implement `compute_cost_delta(baseline_totals, candidate_totals) -> dict` (deltas and percentages)
- [X] T044 [P] Implement `emit_warnings(baseline, candidate) -> list[str]` (check for incomparability)

### Doctor Command

- [X] T045 Implement `promptlab/doctor.py` with `run_doctor() -> int` that checks:
  - ✅ Python version: 3.10+ (print "✓ Python version: X.Y OK" or "✗ Python version: X.Y (need 3.10+)")
  - ✅ Model binary: reachable and responds to --help (try `python stubmodel.py --help` with timeout)
  - ✅ Suites directory: exists and contains .json files (count them)
  - ✅ Assertion types: all 8 registered (import from assertions.py, check set)
  - Exit code 0 if all pass, 1 if any fail; continue all checks even if one fails
- [X] T046 [P] Implement human-readable output for each check (✓/✗ symbols, counts, paths)
- [X] T047 [P] Implement error messages with suggestions (e.g., "Model binary not found → Try: python stubmodel.py --help")

### Unit Tests for Phase 3

- [X] T048 Create `tests/test_compare.py` with unit tests for:
  - Case classification (regressed, improved, unchanged, new, removed)
  - Regression detection (1.0 → 0.9 is regressed, 1.0 → 0.99 is regressed, 0.5 → 0.5 is unchanged)
  - Cost delta calculation (deltas, percentages, zero division)
  - Warnings (same hash, different suites, different model settings)
  - Empty diffs (no cases in common)
- [X] T049 Create `tests/test_doctor.py` with unit tests for:
  - Python version check
  - Model binary check (mock subprocess call)
  - Suites directory check
  - Assertion types check (all 8 present)

### Phase 3 Completion

- [X] T050 Generate two reports: baseline.json and candidate.json from two runs
- [X] T051 Run `python -m promptlab compare --baseline baseline.json --candidate candidate.json --out diff.json` and verify diff JSON written
- [X] T052 Verify regressions are flagged correctly (even small drops)
- [X] T053 Verify cost delta is computed and formatted correctly
- [X] T054 Run `python -m promptlab doctor` and verify output format and exit code
- [X] T055 Run `python -m unittest tests.test_compare tests.test_doctor` and verify all pass

**Depends on**: Phase 2 (run command, report generation)

---

## Phase 4: Prompt Improvement Track

**Goal**: Evaluate classify_v1.txt, create classify_v2.txt, measure improvement, document the work.

**Acceptance Criteria**:
- ✅ Baseline report from classify_v1.txt (--runs 10)
- ✅ Candidate report from classify_v2.txt
- ✅ Diff shows improvement (pass rate increase)
- ✅ IMPROVEMENT.md documents 4+ iterations with predictions and results
- ✅ One iteration shows no improvement (for honesty)
- ✅ classify_v2.txt measurably outperforms v1

### Baseline Evaluation

- [X] T056 Create `suites/classify.json` from `data/tickets.json`:
  - 63 cases (one per ticket)
  - Each case: id, input (ticket text), assertions (json_valid + json_field_equals for category label)
  - Model: temperature 0.0, max_tokens 256
  - Runs: 1 (for baseline suite file; will override with --runs 10 on CLI)
- [X] T057 Run `python -m promptlab run --suite suites/classify.json --runs 10 --out baseline.json --report` and save output
- [X] T058 Document baseline results in IMPROVEMENT.md: baseline.json output, pass/fail/flaky counts, tokens, initial observations

### Prompt Improvement (4+ iterations)

- [X] T059 **Iteration 1**: Improve `prompts/classify_v1.txt` → create `prompts/classify_v1_iter1.txt` (e.g., add more detailed instructions)
- [X] T060 [P] Run `python -m promptlab run --suite suites/classify.json --runs 10 --out candidate_iter1.json` and compare
- [X] T061 [P] Analyze diff: document what changed, what was predicted, what actually happened
- [X] T062 **Iteration 2**: Apply second change (e.g., better formatting, examples)
- [X] T063 [P] Run candidate suite and compare; document prediction vs. actual
- [X] T064 **Iteration 3**: Apply third change
- [X] T065 [P] Run and compare; document
- [X] T066 **Iteration 4 (No-Op)**: Try a change that doesn't help (intentional regression test)
- [X] T067 [P] Run and compare; document that it didn't help (important for honesty)
- [X] T068 **Final**: Create `prompts/classify_v2.txt` (best version from iterations)
- [X] T069 Run final candidate: `python -m promptlab run --suite suites/classify.json --runs 10 --out candidate_final.json`
- [X] T070 Verify v2 measurably outperforms v1 (higher pass rate or lower flaky count)

### Phase 4 Completion

- [X] T071 Document full iteration history in IMPROVEMENT.md:
  - Baseline report output
  - Final candidate report output
  - Final diff output
  - 4+ iteration entries: (Iteration N: Prediction → Actual Result)
  - Include one non-helping iteration
- [X] T072 Verify IMPROVEMENT.md shows learning process (not just polished end result)

**Depends on**: Phase 3 (compare command) and Phase 2 (run command)

---

## Phase 5: Documentation + Context

**Goal**: Write user-facing docs and context artifacts.

**Acceptance Criteria**:
- ✅ USAGE.md documents all commands and exit codes
- ✅ PROMPTS.md has 5 prompts with what/came-back/changed/why
- ✅ JOURNAL.md answers all 5 questions
- ✅ Fresh clone can run `doctor` + smoke suite in <5 min

### Documentation

- [X] T073 Write `USAGE.md` — Agent-facing documentation:
  - What each command does (run, compare, doctor)
  - When to use it (run = test suite, compare = measure improvement)
  - When not to (compare different test sets)
  - Exit codes and what agent should do for each (0 = success, 1 = bad input, 2 = cases failed, 3 = model error, 4 = file error)
  - Example workflow: run baseline, run candidate, compare
  - Error messages and recovery steps
- [X] T074 Write `PROMPTS.md` — Five most important prompts from history/prompts/master/:
  - For each: "What we asked" → "What came back" → "What we changed" → "Why"
  - Focus on prompts that shaped major decisions (flaky policy, fenced JSON, regression detection, etc.)
- [X] T075 [P] Write `README.md` — User-facing guide:
  - Quick start (python -m promptlab doctor)
  - CLI reference (run, compare, doctor with examples)
  - Understanding results (pass/fail/flaky explanation)
  - Suite format (example)
  - Assertion types (table)
- [X] T076 [P] Update existing README_TEMPLATE.md to match final implementation

### Post-Hackathon Reflection

- [X] T077 Write `JOURNAL.md` — One page, answers 5 questions:
  - **Q1**: Three decisions we made + what we rejected
    - E.g., "Flaky = 0 < rate < 1.0 (rejected threshold-based)"
  - **Q2**: Hardest bug + how we found root cause
  - **Q3**: Something Claude Code got confidently wrong + how we caught it
  - **Q4**: What we'd do differently with 4 more hours
  - **Q5**: Who did what (per person)

### Phase 5 Completion

- [X] T078 Verify USAGE.md is agent-readable (clear exit codes, recovery steps)
- [X] T079 Verify PROMPTS.md has exactly 5 entries with all 4 fields
- [X] T080 Verify JOURNAL.md answers all 5 questions, fits one page

**Depends on**: All previous phases (evidence of implementation + improvement)

---

## Summary

| Phase | Tasks | Goal | Acceptance |
|-------|-------|------|-----------|
| 1 | T001–T016 | CLI + Suite Loading | Parse args, load JSON, error handling |
| 2 | T017–T040 | Run Command | Model invocation, 8 assertions, reports |
| 3 | T041–T055 | Compare + Doctor | Regression detection, diagnostics |
| 4 | T056–T072 | Prompt Improvement | Measure v1→v2 gain (4+ iterations) |
| 5 | T073–T080 | Documentation | USAGE, PROMPTS, JOURNAL, README |

**Total Tasks**: 80

**Parallel Opportunities**:
- Phase 1: T002–T004 (project structure), T011–T012 (validation)
- Phase 2: T020a–h (assertion implementations), T022–T023 (path resolution), T025–T027 (case execution), T029–T030 (tokens & hash)
- Phase 3: T042–T044 (comparison), T046–T047 (doctor output)
- Phase 4: Iterations 1–4 (independent improvements)
- Phase 5: T075–T076 (README parallel to USAGE)

**Suggested MVP Scope**:
- Phases 1–3 (CLI, run, compare, doctor) = core harness functionality
- Phase 4 = proof of effectiveness on real prompts
- Phase 5 = grading artifacts (USAGE, PROMPTS, JOURNAL)

---

**Ready to implement?** Start with Phase 1 tasks (T001–T016), then proceed through phases sequentially. Each phase is independently testable.

**Next**: `/sp.implement phase-1` to begin coding.
