---
ID: 004
TITLE: Design phase artifacts and contracts
STAGE: plan
DATE_ISO: 2026-09-16
SURFACE: agent
MODEL: claude-haiku-4-5-20251001
FEATURE: promptlab
BRANCH: master
USER: muhammaddanish321@gmail.com
COMMAND: /sp.plan (design artifacts phase)
LABELS: ["plan", "design", "contracts", "data-model"]
LINKS:
  SPEC: specs/master/spec.md
  PLAN: specs/master/plan.md
  ADR: history/adr/001-005-*.md
  TICKET: null
  PR: null
---

## Prompt

```
Based on the implementation plan (plan.md), create design artifacts:

1. research.md - Consolidate all technical decisions and design rationale
2. data-model.md - Document Suite, Report, and Diff JSON schemas with validation rules
3. contracts/cli-*.md - Define CLI contracts for run, compare, doctor commands
4. quickstart.md - Developer quick reference with module responsibilities and patterns

Each artifact should bridge between the high-level plan and the implementation phases.
Make it clear what each module does, what dependencies exist, and how to test.
```

## Response

**Design artifacts completed successfully.**

**Artifacts created**:

1. **research.md** (Decisions Consolidated)
   - Flaky classification: 0 < rate < 1.0
   - Fenced JSON extraction: extract and parse inner JSON
   - Regression detection: any drop counts
   - Cost accounting: totals + averages
   - Assertion evaluation: all assertions evaluate
   - Token counting: ceil(len/4)
   - Error handling: exit codes 0/1/2/3/4
   - Determinism: byte-identical at temp 0.0

2. **data-model.md** (JSON Schemas)
   - Suite schema with validation rules
   - Report schema (totals, cases, per-assertion counts)
   - Diff schema (case classification, cost_delta, warnings)
   - Constraints and determinism requirements

3. **contracts/** (CLI Specifications)
   - cli-run.md: `python -m promptlab run --suite <file> [--runs N] [--out report.json] [--report]`
   - cli-compare.md: `python -m promptlab compare --baseline <file> --candidate <file> [--out diff.json]`
   - cli-doctor.md: `python -m promptlab doctor` (4 checks: Python, Model, Suites, Assertions)
   - Each contract includes: arguments, validation, output format, exit codes, error messages

4. **quickstart.md** (Developer Guide)
   - Project structure (8 core modules)
   - Module responsibilities (cli, suite, model, assertions, runner, report, compare, doctor)
   - Key functions and implementations
   - Testing strategy with unit test structure
   - Common patterns (error handling, path resolution, JSON determinism)
   - Implementation checklist for each phase

---

## Outcome

- ✅ All technical decisions documented with rationale
- ✅ Data schemas fully specified with validation rules
- ✅ CLI contracts precise (arguments, output, exit codes)
- ✅ Developer guide ties design to implementation
- ✅ Clear bridge from plan.md to Phase 1 implementation

**Design is now complete and ready for task breakdown.**

---

## Changes Made

**Files created**:
- specs/master/research.md (8 major decisions)
- specs/master/data-model.md (Suite/Report/Diff schemas)
- specs/master/contracts/cli-run.md
- specs/master/contracts/cli-compare.md
- specs/master/contracts/cli-doctor.md
- specs/master/quickstart.md (developer guide)
- history/prompts/master/004-design-phase-artifacts.plan.prompt.md (this PHR)

**Total design artifacts**: 7 files, ~4000 lines of detailed specification

**Tests run**: None (design/documentation phase)

**Evaluation**:
- Each module responsibility is clear
- Data structures are fully specified
- CLI contracts match the brief exactly
- Developers have concrete implementation guidance
