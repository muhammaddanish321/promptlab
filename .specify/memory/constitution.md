# promptlab Constitution

Project: promptlab, a command-line test runner for prompts. Measures whether prompts pass, fail, or run flaky across assertion types and versions.

## Core Principles

1. **Spec First**: SPEC.md at the repo root is the graded specification. Every design change updates SPEC.md before any code, in a separate commit.
2. **Python Standard Library Only**: Python 3.10+, no third-party packages, no network access.
3. **Model as Subprocess Only**: The model is called only as a subprocess using its CLI contract (stubmodel.py). Never import, copy, reimplement, or predict its output. Judges swap in a different binary with the same contract—our harness must keep working.
4. **Non-Determinism is the Core Problem**: Every case is pass, fail, or flaky, based on pass_rate over N runs. Never collapse flaky into pass. A case that passes 7/10 times is not a passing case.
5. **No User-Visible Tracebacks**: Every error = one-line message + exact exit code: 0 (all pass), 1 (bad usage/malformed suite), 2 (cases failed), 3 (model not invokable), 4 (file unreadable).
6. **Determinism at Temperature 0**: Running the same suite twice at temperature 0.0 produces byte-identical reports apart from timing fields.
7. **Full Test Coverage**: Every harness module has unittest tests; `python -m unittest` passes from a fresh clone.
8. **Explainability**: Every team member must be able to explain every file. Prefer simple, readable code over abstraction.

## Token Accounting

All text counting uses: `tokens = math.ceil(len(text) / 4)`. Applied everywhere: model calls, prompt tokens, input/output token accounting in reports.

## CLI Contract (Mandatory)

Three commands, exact signatures:
- `promptlab run --suite <file> [--runs N] [--out report.json] [--report]`
- `promptlab compare --baseline <report.json> --candidate <report.json> [--out diff.json]`
- `promptlab doctor`

Suite format: fixed JSON. Report schema: fixed JSON. Both are governed by SPEC.md.

## The Eight Assertion Types

All mandatory, all with exact semantics defined in SPEC.md:
1. `contains` — output contains value
2. `not_contains` — output does not contain value
3. `equals` — output equals value (with optional whitespace normalization)
4. `matches` — regex matches
5. `json_valid` — output parses as JSON
6. `json_field_equals` — dotted path resolves to value
7. `max_tokens` — tokens_out at or below threshold
8. `finish_is` — finish equals stop, length, or refusal

## Development Workflow

1. **Spec Phase** (0–2h): Define SPEC.md with all decisions (flaky policy, fenced JSON rule, regression threshold, assertion eval model, cost accounting, failure taxonomy, definition of done). No implementation code.
2. **Clarification** (2–6h): Resolve ambiguities via team consensus. Update SPEC.md with decisions and rejected alternatives.
3. **Implementation**: Phase-by-phase. Each phase: write code, run tests, commit, review with team. Update SPEC.md when design changes.
4. **Incremental Commits**: SPEC changes before code. Feature work in small, testable chunks. Each commit self-contained.
5. **Test-Driven**: Tests written alongside code. Every harness module has unit tests.

## Exit Codes and Error Handling

- **0**: All cases passed.
- **1**: Bad usage or malformed suite (missing fields, wrong types, unknown assertion type, invalid regex).
- **2**: One or more cases failed (a result, not an error—something in CI depends on this distinction).
- **3**: Model could not be invoked (binary absent, not executable, subprocess error).
- **4**: Suite file or report file unreadable.

Error messages are one-line, no tracebacks.

## Governance

- Constitution is binding; all code must comply.
- Amendment requires written justification and team consensus.
- SPEC.md is the ground truth; code and tests follow it.
- Judges review: (1) spec discipline (SPEC.md first, code second), (2) understanding (live viva), (3) functionality, (4) context artifacts (CLAUDE.md, PROMPTS.md, USAGE.md), (5) prompt improvement evidence.

**Version**: 1.0 | **Ratified**: 2026-09-16


