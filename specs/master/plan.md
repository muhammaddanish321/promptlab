# Implementation Plan: promptlab

**Branch**: `master` | **Date**: 2026-09-16 | **Spec**: `specs/master/spec.md`  
**Input**: Feature specification from `specs/master/spec.md`

## Summary

promptlab is a command-line test runner for prompts. It executes test cases against a prompt, evaluates assertions on model outputs, and reports pass/fail/flaky outcomes to detect prompt regressions and improvements.

**Technical Approach**:
- Python 3.10+ standard library only (no third-party packages)
- Subprocess model invocation (never import stubmodel.py)
- Pass/fail/flaky classification (0 < pass_rate < 1.0 = flaky)
- Fenced JSON extraction and parsing for robust assertion handling
- Per-assertion pass/fail counts for diagnostic detail
- Cost accounting (both totals and averages) for transparency

## Technical Context

**Language/Version**: Python 3.10+ (standard library only)  
**Primary Dependencies**: None (standard library: argparse, subprocess, json, re, hashlib, math, time, pathlib, sys, unittest)  
**Storage**: JSON files (suite format, reports, diffs) — no database  
**Testing**: unittest (standard library; must pass from fresh clone)  
**Target Platform**: Linux/macOS/Windows (cross-platform CLI)  
**Project Type**: Single package (CLI tool)  
**Performance Goals**: <5 minutes for smoke suite end-to-end (per brief)  
**Constraints**: No network, no third-party packages, determinism at temperature 0.0  
**Scale/Scope**: Support suites with 1000+ cases; reports JSON-serializable for CI pipelines  

## Constitution Check

*GATE: Must pass before Phase 1. Re-check after implementation.*

✅ **Language/Version**: Python 3.10+ — confirmed standard library only  
✅ **Dependencies**: None (stdlib only) — compliant  
✅ **No imports of stubmodel.py** — will invoke as subprocess only  
✅ **Non-determinism handling**: Pass/fail/flaky distinction implemented  
✅ **Exit codes**: 0, 1, 2, 3, 4 as specified  
✅ **No tracebacks**: One-line error messages required  
✅ **Tests**: unittest required; all modules tested  
✅ **Explainability**: Simple, readable code; every team member can explain  

**Gate Status**: ✅ PASS — No violations detected

---

## Project Structure

### Documentation

```
specs/master/
├── spec.md              # Feature specification ✅ Done
├── plan.md              # This file ✅ Done
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```
promptlab/                         # Main package
├── __init__.py
├── __main__.py                    # Entry point: python -m promptlab
├── cli.py                         # CLI argument parsing (router for 3 commands)
├── suite.py                       # Suite loading & validation
├── model.py                       # Model subprocess invocation
├── assertions.py                  # All 8 assertion types
├── runner.py                      # Core run logic (cases + assertions)
├── report.py                      # Report generation & schema
├── compare.py                     # Diff generation & cost delta
└── doctor.py                      # Environment diagnostics

tests/
├── __init__.py
├── test_assertions.py             # Unit tests for all 8 assertion types
├── test_suite_loading.py          # Unit tests for suite parsing & validation
├── test_model.py                  # Unit tests for model invocation
├── test_runner.py                 # Unit tests for case execution & flaky classification
├── test_report.py                 # Unit tests for report generation
├── test_compare.py                # Unit tests for comparison logic
├── test_doctor.py                 # Unit tests for doctor command
└── fixtures/
    └── fake_model.py              # Fake model for testing (implements CLI contract)

data/
├── tickets.json                   # 63 labeled tickets ✅ Done

prompts/
├── classify_v1.txt                # Weak prompt ✅ Done
└── classify_v2.txt                # Improved prompt (Phase 3)

suites/
├── smoke.json                     # Smoke test suite ✅ Done
└── classify.json                  # Full classification suite (Phase 3)

history/
├── prompts/master/                # Prompt History Records ✅ Started
└── adr/                           # Architecture Decision Records ✅ 5 ADRs created

docs/
├── USAGE.md                       # Agent-facing documentation (Phase 2)
├── IMPROVEMENT.md                 # Prompt improvement track (Phase 3)
├── PROMPTS.md                     # Five most important prompts (Phase 3)
├── README.md                      # User-facing guide
└── JOURNAL.md                     # Post-hackathon reflection (after Phase 3)
```

**Structure Decision**: Single package (CLI tool) with modular components. No database, no external services, no third-party packages.

---

## Implementation Phases

### Phase 1: CLI Skeleton + Suite Loading + Validation

**Goal**: Parse arguments, load and validate suite JSON, establish error handling.

**Modules**:
- `cli.py`: argparse routes for `run`, `compare`, `doctor`
- `suite.py`: Parse suite JSON, validate schema, resolve paths

**Tasks**:
1. Create `promptlab/__init__.py` and `__main__.py` (entry point)
2. Implement `cli.py` with command routing
3. Implement `suite.py` with JSON schema validation
4. Test suite loading with various malformed inputs
5. Establish error handling with correct exit codes (0, 1, 2, 3, 4)

**Acceptance**:
- ✅ `python -m promptlab run --suite suites/smoke.json` parses args
- ✅ Malformed suite files produce exit code 1 with one-line message
- ✅ `python -m unittest tests.test_suite_loading` passes

---

### Phase 2: Model Invocation + Assertions + Run Command

**Goal**: Call model as subprocess, evaluate all 8 assertion types, generate reports.

**Modules**:
- `model.py`: Subprocess call, JSON response parsing
- `assertions.py`: All 8 assertion types with fenced JSON extraction
- `runner.py`: Case execution loop, flaky classification
- `report.py`: Report JSON generation

**Tasks**:
1. Implement `model.py` subprocess invocation
2. Implement all 8 assertions in `assertions.py`
3. Implement fenced JSON extractor (used by json_valid, json_field_equals)
4. Implement `runner.py` case execution (run each case --runs times)
5. Implement pass/fail/flaky classification (0 < rate < 1.0 = flaky)
6. Implement `report.py` JSON report with totals and averages
7. Test all assertions with unit tests

**Acceptance**:
- ✅ `python -m promptlab run --suite suites/smoke.json` executes end-to-end
- ✅ Report JSON matches schema exactly
- ✅ At temperature 0.0, repeated runs produce byte-identical reports
- ✅ `python -m unittest tests.test_assertions tests.test_runner tests.test_report` pass

---

### Phase 3: Compare + Doctor + Warnings

**Goal**: Implement comparison logic, detect regressions, provide diagnostics.

**Modules**:
- `compare.py`: Case classification, cost delta, warnings
- `doctor.py`: Environment checks

**Tasks**:
1. Implement `compare.py` with case classification (regressed, improved, unchanged, new, removed)
2. Implement any-drop regression detection
3. Implement cost delta (both totals and percentages)
4. Implement warnings (same prompt_hash, different suites, different model settings)
5. Implement `doctor.py` environment checks
6. Test compare logic with various report pairs

**Acceptance**:
- ✅ `python -m promptlab compare --baseline baseline.json --candidate candidate.json` produces diff
- ✅ Regression detection flags 1.0 → 0.9 drops
- ✅ Cost delta computed correctly
- ✅ Warnings issued for incomparable reports
- ✅ `python -m promptlab doctor` runs without error
- ✅ `python -m unittest tests.test_compare tests.test_doctor` pass

---

### Phase 4: Prompt Improvement Track

**Goal**: Evaluate classify_v1.txt, create classify_v2.txt, measure improvement.

**Tasks**:
1. Create `suites/classify.json` from `data/tickets.json`
2. Run `python -m promptlab run --suite suites/classify.json --out baseline.json --runs 10`
3. Create `prompts/classify_v2.txt` (improved prompt)
4. Run candidate report
5. Run `python -m promptlab compare --baseline baseline.json --candidate candidate.json --out diff.json`
6. Document improvement in `IMPROVEMENT.md` (prediction + actual result for 4+ iterations)
7. Include one iteration that doesn't help

**Acceptance**:
- ✅ `IMPROVEMENT.md` includes baseline, candidate, and diff outputs
- ✅ At least 4 iterations with predictions and results
- ✅ One iteration shows no improvement (for honesty)
- ✅ `prompts/classify_v2.txt` measurably outperforms v1

---

### Phase 5: Documentation + Context

**Goal**: Write user-facing docs and context artifacts.

**Tasks**:
1. Write `USAGE.md` (agent-facing: commands, exit codes, when to use)
2. Write `README.md` (quick start, CLI reference)
3. Extract 5 most important prompts and write `PROMPTS.md`
4. Write `JOURNAL.md` (decisions, hardest bug, what Claude got wrong, improvements)

**Acceptance**:
- ✅ `USAGE.md` documents all commands and exit codes
- ✅ `PROMPTS.md` has 5 prompts with what/came-back/changed/why
- ✅ `JOURNAL.md` answers all 5 questions
- ✅ Fresh clone can run `doctor` + smoke suite in <5 min

---

## Critical Dependencies

1. **Phase 1** → Phase 2: Suite loading must work before model invocation
2. **Phase 2** → Phase 3: Run command must produce valid reports before compare
3. **Phase 3** → Phase 4: Compare must work before evaluating prompt improvements
4. **Phase 4** → Phase 5: Need evidence of improvement before writing IMPROVEMENT.md

---

## Definition of Done (Per Phase)

**Phase 1**:
- ✅ Suite validation works with correct exit codes
- ✅ `python -m unittest tests.test_suite_loading` passes
- ✅ Code is simple and readable

**Phase 2**:
- ✅ All 8 assertions implemented and tested
- ✅ Flaky classification (0 < rate < 1.0) working
- ✅ Report JSON matches schema exactly
- ✅ Byte-identical reports at temperature 0.0
- ✅ `python -m unittest` passes all test_*.py files
- ✅ Smoke suite runs end-to-end

**Phase 3**:
- ✅ Compare command works correctly
- ✅ Regression detection flags any drop
- ✅ Cost delta computed and formatted
- ✅ Doctor command runs and checks all items
- ✅ Warnings issued appropriately
- ✅ `python -m unittest` passes all tests

**Phase 4**:
- ✅ classify_v1.txt baseline established
- ✅ classify_v2.txt created and tested
- ✅ 4+ iterations documented with predictions
- ✅ One non-helping iteration included
- ✅ v2 measurably outperforms v1

**Phase 5**:
- ✅ All documentation written
- ✅ JOURNAL.md answers all 5 questions
- ✅ Fresh clone can doctor + smoke suite in <5 min
- ✅ Code review: "Every team member can explain every file"

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Fenced JSON extraction fails | json_valid/json_field_equals broken | Write regex carefully; test extensively |
| Flaky threshold misclassified | Silent regressions missed | Clear test cases (1/10, 2/10, etc.) |
| Regression detection too strict | Noise flagged as regression | Judges understand the philosophy |
| Token calculation errors | Cost delta wrong | Use ceil(len/4) consistently everywhere |
| Model subprocess hangs | Entire suite hangs | Add timeout; document in USAGE.md |

---

**Next**: `/sp.tasks` to break phases into granular, testable tasks.
