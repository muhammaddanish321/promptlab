---
description: Run unit tests and the smoke suite before committing (report only)
allowed-tools: Bash(python:*), Bash(git status:*)
---
Run these checks in order and report the results. Do not fix anything.

1. `python -m unittest` — report the number of tests, failures, and errors.
   For each failure, give the test name and a one-line reason.
2. `python -m promptlab doctor` — report each diagnostic line and whether it passed.
3. `python -m promptlab run --suite suites/smoke.json --report` —
   report the exit code and what it means:
   0 = all passed, 1 = bad usage/malformed suite, 2 = cases failed or flaky,
   3 = model not invokable, 4 = file unreadable.
4. Run the smoke suite a second time at temperature 0 with `--out` to two
   files and diff them. Report any difference outside timing fields
   (that would break determinism).
5. `git status` — list uncommitted files.

Finish with one line: READY TO COMMIT or NOT READY, with the reason.
