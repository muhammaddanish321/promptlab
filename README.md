# promptlab

**promptlab** is a command-line test runner for LLM prompts. Test your prompts like you test code.

> Detect non-determinism, measure prompt improvement, and compare versions with confidence.

---

## Features

✅ **Run test suites** against prompts and measure accuracy  
✅ **Detect flaky behavior** — distinguish pass/fail/flaky (non-determinism)  
✅ **Compare versions** — measure improvement and regressions  
✅ **Cost analysis** — track token usage across iterations  
✅ **Deterministic at temp 0.0** — reproducible results for CI/CD  
✅ **Standard library only** — no dependencies, runs anywhere Python 3.10+ is available  

---

## Quick Start

**Verify environment**:
```bash
python -m promptlab doctor
```

**Run a test suite** (10 iterations):
```bash
python -m promptlab run --suite suites/classify.json --runs 10 --report
```

**Compare two prompt versions**:
```bash
python -m promptlab compare --baseline v1.json --candidate v2.json
```

See **USAGE.md** for detailed command reference.

---

## Suite Format

Create a JSON file defining your test cases:

```json
{
  "name": "classify",
  "prompt_file": "prompts/classify_v1.txt",
  "model": {"temperature": 0.0, "max_tokens": 256},
  "runs": 1,
  "cases": [
    {
      "id": "c001",
      "input": "I was charged twice. Please refund.",
      "assert": [
        {"type": "json_valid"},
        {"type": "json_field_equals", "field": "category", "value": "billing"}
      ]
    }
  ]
}
```

**Key points**:
- `prompt_file` is relative to the suite file location (not working directory)
- `input` can be a string or `{"file": "path"}`
- `assert` can combine multiple checks (all must pass)

---

## Assertion Types

| Type | Purpose | Example |
|------|---------|---------|
| `json_valid` | Output is valid JSON (including fenced) | `{"type": "json_valid"}` |
| `json_field_equals` | JSON field matches value (dotted paths: `foo.bar.0.baz`) | `{"type": "json_field_equals", "field": "category", "value": "billing"}` |
| `contains` | Output contains substring | `{"type": "contains", "value": "success"}` |
| `not_contains` | Output does NOT contain substring | `{"type": "not_contains", "value": "error"}` |
| `equals` | Output exactly equals value | `{"type": "equals", "value": "OK"}` |
| `matches` | Regex pattern matches output | `{"type": "matches", "pattern": "^OK$"}` |
| `max_tokens` | Output is ≤ token threshold | `{"type": "max_tokens", "value": 100}` |
| `finish_is` | Model's finish reason matches | `{"type": "finish_is", "value": "stop"}` |

---

## Flaky Behavior

A **flaky** case passes sometimes and fails other times (when temperature > 0.0 or with non-deterministic models).

```
Pass Rate Classification:
- 1.0 → PASS (all runs pass)
- 0.0 → FAIL (all runs fail)
- 0 < rate < 1.0 → FLAKY (inconsistent)
```

**Why detect flakiness?** Because real LLMs are non-deterministic. Understanding flakiness is critical for:
- Identifying prompts that need refinement
- Measuring prompt robustness across variations
- Detecting when model behavior is unstable

---

## Regression Detection

Any drop in pass rate is flagged as regression:
- 1.0 → 0.9 = **regressed**
- 0.8 → 0.7 = **regressed**
- 0.5 → 0.5 = **unchanged**

No threshold tolerance. Even small drops matter.

---

## Exit Codes

| Code | Meaning | What to do |
|------|---------|-----------|
| 0 | All cases passed | ✓ Success, no action needed |
| 1 | Bad input or malformed JSON | Fix suite JSON or check arguments |
| 2 | Cases failed or flaky | Investigate failures, improve prompt |
| 3 | Model error (binary not found) | Run `python -m promptlab doctor` to diagnose |
| 4 | File unreadable | Check file permissions and paths |

---

## Token Accounting

Tokens are counted using the rule: **ceil(len(text) / 4)**

Applies to:
- Prompt text
- Input text
- Model output
- Report totals

This approximates actual LLM token usage without requiring a tokenizer.

---

## Workflow Example

### 1. Set up your prompt and suite

Create `prompts/my_prompt.txt`:
```
Classify this support ticket:

Ticket: {input}

Respond with JSON: {"category": "billing|account|technical"}
```

Create `suites/my_suite.json`:
```json
{
  "name": "my_test",
  "prompt_file": "../prompts/my_prompt.txt",
  "model": {"temperature": 0.0, "max_tokens": 256},
  "runs": 1,
  "cases": [
    {"id": "1", "input": "I was charged twice", 
     "assert": [{"type": "json_field_equals", "field": "category", "value": "billing"}]}
  ]
}
```

### 2. Run baseline

```bash
python -m promptlab run --suite suites/my_suite.json --runs 10 --out baseline.json --report
```

Check results:
```bash
cat baseline.json | jq '.totals'
# {cases: 1, passed: 1, failed: 0, flaky: 0, ...}
```

### 3. Improve prompt

Edit `prompts/my_prompt.txt` to add examples, clarify instructions, etc.

### 4. Run candidate

```bash
# Create candidate suite with new prompt
python -m promptlab run --suite suites/my_suite_v2.json --runs 10 --out candidate.json
```

### 5. Compare

```bash
python -m promptlab compare --baseline baseline.json --candidate candidate.json | jq '.cost_delta'
```

Did accuracy improve? Did tokens increase? Make an informed decision.

---

## Understanding Reports

Reports are JSON with structure:

```json
{
  "suite": "my_test",
  "prompt_hash": "a1b2c3d4e5f6",  // First 12 hex of SHA-256(prompt)
  "runs": 10,
  "totals": {
    "cases": 1,
    "passed": 1,
    "failed": 0,
    "flaky": 0,
    "tokens_in": 250,
    "tokens_out": 50,
    "wall_ms": 2500
  },
  "cases": [
    {
      "id": "1",
      "status": "pass",           // "pass" | "fail" | "flaky"
      "pass_rate": 1.0,           // Fraction of runs that passed
      "tokens_out_avg": 5,        // Average tokens per run
      "assertions": [
        {"type": "json_field_equals", "passed": 10, "failed": 0}
      ],
      "failures": []              // Details of failed assertions
    }
  ]
}
```

---

## Determinism

At temperature 0.0, reports are byte-identical (except `wall_ms`) across runs.

This enables:
- Reproducible CI/CD testing
- Baseline comparison (same prompt twice = same results)
- Regression detection (only code/prompt changes cause diff)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `doctor` shows ✗ for model binary | Run `python stubmodel.py --help` directly to debug |
| All cases fail | Check JSON output format; assertions may expect different field names |
| Flaky results at temp 0.0 | This shouldn't happen; report as bug or check model binary |
| Tokens seem too high/low | Use rule: ceil(len(text) / 4); not actual LLM tokenization |
| Paths not resolving | Remember: paths in suite are relative to suite file, not working directory |

---

## Documentation

- **USAGE.md** — Complete command reference and error recovery
- **PROMPTS.md** — Key architectural decisions that shaped the design
- **IMPROVEMENT.md** — Example of iterative prompt improvement (with findings)
- **JOURNAL.md** — Reflection on what worked, what didn't, next steps

---

## Requirements

- Python 3.10+
- Standard library only (no pip dependencies)
- `stubmodel.py` in PATH for testing (included in repo)

---

## Examples

See the included suites and prompts:
- `suites/smoke.json` — Quick sanity check
- `suites/classify.json` — 63 real support ticket classifications
- `prompts/classify_v1.txt` — Initial prompt
- `prompts/classify_v2.txt` — Refined version

---

## License & Attribution

promptlab is a Spec-Driven Development (SDD) implementation example.

Created with [Claude Code](https://claude.com/claude-code) and documented in `PROMPTS.md` and `JOURNAL.md`.

---

**Questions?** Start with `python -m promptlab doctor` then review USAGE.md.

**Feedback?** See JOURNAL.md for known limitations and next steps.
