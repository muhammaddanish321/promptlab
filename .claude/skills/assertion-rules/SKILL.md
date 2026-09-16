---
name: assertion-rules
description: Rules for promptlab assertion evaluation, run classification, and compare logic. Use this skill whenever writing, changing, reviewing, or testing code for any of the eight assertion types (contains, not_contains, equals, matches, json_valid, json_field_equals, max_tokens, finish_is), for pass/fail/flaky status, pass_rate, per-assertion counts, the failures field, or regression detection in compare — even if the request does not say "assertion".
---

# Assertion rules for promptlab

SPEC.md wins over this file. If they disagree, stop and report it.
Items marked **[decision]** must match what the team wrote in SPEC.md;
replace the default here if the team chose differently.

## The eight types

| Type | Fields | Passes when |
|---|---|---|
| contains | value, ignore_case? | value is in output |
| not_contains | value, ignore_case? | value is not in output |
| equals | value, normalize? | output == value; normalize strips and collapses whitespace on both sides |
| matches | pattern | `re.search(pattern, output)` finds a match |
| json_valid | — | output parses as JSON (see fenced rule) |
| json_field_equals | field, value | dotted path resolves and equals value |
| max_tokens | value | `tokens_out <= value` (use the model's reported tokens_out) |
| finish_is | value | `finish == value`; value must be stop, length, or refusal |

## Consistency rule for JSON
- **[decision]** Fenced JSON (a ```json ... ``` block): valid or not.
- json_valid and json_field_equals MUST call the same helper, e.g.
  `extract_json(output) -> (ok, obj)`. Never parse JSON in two different ways.
- If json_valid fails for an output, json_field_equals fails too.

## Dotted paths
- `a.b.c` walks dict keys. Decide and document whether numeric segments
  index into lists (`items.0.name`). **[decision]**
- A missing key, wrong type, or out-of-range index = assertion failed,
  with a reason like `path 'a.b' not found`. Never raise.
- Compare values by JSON equality: `1` and `"1"` are different.

## Validation happens at load time
- Unknown assertion type, missing required field, or wrong field type →
  malformed suite, exit 1, message naming the case id and assertion index.
- Invalid regex in `matches`: compile it when loading the suite. **[decision]**
  whether this is exit 1 (malformed suite) or a per-case failure; record it in SPEC.md.
  Either way: one-line message, no traceback.

## Evaluation model
- **[decision, default]** All assertions always evaluate. No early stop.
  This keeps per-assertion counts complete, which the report requires.
- A case with zero assertions: decide and document its status. **[decision]**

## Status from multiple runs
- pass_rate = passed_runs / total_runs (a run passes only if all its assertions pass).
- **pass**: pass_rate == 1.0 (or ≥ the SPEC.md threshold). **[decision]**
- **fail**: pass_rate == 0.0.
- **flaky**: everything in between.
- Never collapse flaky into pass. A 7/10 case is NOT passing.
- Exit code 2 if any case is fail or flaky.

## Per-assertion counts
For each assertion in a case: `{"type": ..., "passed": n, "failed": m}`,
where n + m == runs. Keep assertion order as in the suite.

## failures field
Each entry must allow debugging without rerunning:
- run index, assertion type and its parameters, reason
- actual output, truncated (e.g. first 200 chars + `…[+N chars]`)
- finish and tokens_out
Keep ordering deterministic.

## Compare
- Match cases by id: regressed, improved, unchanged, new, removed.
- A pass_rate drop is a regression even when the status label is the same.
- **[decision]** Regression threshold and whether it depends on runs.
- Warn when: prompt_hash equal, suite name differs, model settings differ.
- Cost delta: tokens_in, tokens_out, percent change (guard divide-by-zero).
