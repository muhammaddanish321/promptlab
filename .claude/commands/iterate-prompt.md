---
description: Measure a classify prompt version against the v1 baseline
argument-hint: <candidate prompt file, e.g. prompts/classify_v2.txt>
allowed-tools: Bash(python:*), Read
---
Candidate prompt: $ARGUMENTS

1. Make sure `reports/baseline_v1.json` exists. If not, create it with:
   `python -m promptlab run --suite suites/classify_v1.json --runs 5 --out reports/baseline_v1.json`
2. Run the candidate with the same suite settings (same cases, temperature,
   max_tokens, runs), pointing at $ARGUMENTS, and write
   `reports/candidate.json`.
3. Run:
   `python -m promptlab compare --baseline reports/baseline_v1.json --candidate reports/candidate.json --out reports/diff.json`
4. Report:
   - passed / failed / flaky for baseline and candidate
   - counts of regressed, improved, unchanged, new, removed
   - token cost change (in, out, percent)
   - every compare warning, word for word
   - the three worst regressed cases with their failing assertion
5. Draft an IMPROVEMENT.md entry using this template and show it to me.
   Do NOT write it to the file; I fill in the prediction and verdict myself.

```
### Iteration N — <change>
- What I changed:
- Technique used:
- Prediction (written before running):
- Result: passed X→Y, flaky X→Y, regressed N, improved N, tokens +/-P%
- Was the prediction right?
- Keep or revert:
```

Never edit the prompt file or the suite. Measurement only.
