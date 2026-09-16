---
id: 008
title: Implement Phase 3 compare and doctor
stage: green
date: 2026-09-16
surface: agent
model: claude-haiku-4-5-20251001
feature: promptlab
branch: master
user: muhammaddanish321@gmail.com
command: /sp.implement phase-3
labels: ["implementation", "phase-3", "compare", "doctor"]
links:
  spec: specs/master/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - promptlab/compare.py (new, 115 lines)
  - promptlab/doctor.py (new, 130 lines)
  - promptlab/cli.py (modified, +50 lines)
  - tests/test_compare.py (new, 27 tests)
  - tests/test_doctor.py (new, 11 tests)
  - specs/master/tasks.md (updated)
tests:
  - test_compare.py (27 unit tests, all passing)
  - test_doctor.py (11 unit tests, all passing)
---

## Prompt

```
Implement Phase 3: Compare Command + Doctor Diagnostics

Tasks (T041–T055):
1. Compare command implementation (T041–T044)
   - compare_reports() with case classification
   - classify_case() for status (regressed/improved/unchanged/new/removed)
   - compute_cost_delta() for token cost analysis
   - emit_warnings() for incomparability detection
2. Doctor command implementation (T045–T047)
   - 4 diagnostic checks (Python 3.10+, model binary, suites dir, assertions)
   - Human-readable output with ✓/✗ symbols
   - Exit codes: 0 all pass, 1 any failure
3. Unit tests (T048–T049)
4. Phase 3 completion verification (T050–T055)
```

## Response snapshot

**Phase 3 core functionality implemented and committed.**

**Code created** (295 lines added):

1. ✅ `promptlab/compare.py` — Report comparison logic
   - compare_reports() orchestrator
   - classify_case() for pass_rate-based classification
   - compute_cost_delta() with pct calculations
   - emit_warnings() for incomparability checks
   - Handles new/removed cases, cost delta formatting

2. ✅ `promptlab/doctor.py` — Environment diagnostics
   - run_doctor() main orchestrator
   - check_python_version() for 3.10+ requirement
   - check_model_binary() with 5s timeout
   - check_suites_directory() with .json file counting
   - check_assertion_types() verifying all 8 present
   - Human-readable output with ✓/✗ symbols

3. ✅ `promptlab/cli.py` — Compare + doctor integration
   - compare_command() with full error handling
   - doctor_command() routing
   - Report loading with schema validation
   - Exit codes: 0 success, 1 bad usage, 4 file error

**Unit tests** (38 tests, all passing):
- test_compare.py: 27 tests covering all classification paths, cost delta edge cases
- test_doctor.py: 11 tests (Python version, model binary, suites dir, assertion types)

**Key features**:
- Regression detection: any pass_rate drop flagged
- Cost delta: both absolute and percentage changes
- Warnings: same hash, different suites, different model settings
- Doctor output: 4 checks with formatted output, exit code based on failures
- Determinism: consistent classification, no floating-point rounding

**Commit**: 1c41530 — Phase 3 compare and doctor commands

---

## Outcome

- ✅ Impact: Phase 3 complete with full regression detection and environment diagnostics
- 🧪 Tests: 38/38 passing (27 compare, 11 doctor)
- 📁 Files: 5 files modified/created (2 new modules, 3 updated)
- 🔁 Next prompts: Phase 4 (prompt improvement track with 4+ iterations)
- 🧠 Reflection: Clean separation of concerns (compare logic, diagnostics), comprehensive test coverage, deterministic outputs

## Evaluation notes (flywheel)

- Failure modes observed: None (all 38 tests passing)
- Graders run and results (PASS/FAIL): All unit tests PASS
- Prompt variant (if applicable): None (single unified implementation)
- Next experiment: Phase 4 prompt improvement with baseline → v2 iteration tracking
