# promptlab

A command-line test runner for prompts. Evaluates assertions on model outputs and reports pass/fail/flaky outcomes.

## Quick Start

### Install

Clone the repo and ensure Python 3.10+ is available.

```bash
python --version  # Must be 3.10+
```

### Run a test suite

```bash
python -m promptlab run --suite suites/smoke.json --report
```

### Compare two prompt versions

```bash
python -m promptlab run --suite suites/smoke.json --out baseline.json
python -m promptlab run --suite suites/classify_v2.json --out candidate.json
python -m promptlab compare --baseline baseline.json --candidate candidate.json
```

### Check environment

```bash
python -m promptlab doctor
```

## CLI Reference

### `run`

Execute a test suite against a prompt.

```bash
python -m promptlab run --suite <file> [--runs N] [--out report.json] [--report]
```

**Options**:
- `--suite <file>` (required): Path to suite JSON file.
- `--runs N`: Number of runs per case. Overrides suite file value.
- `--out <file>`: Write JSON report to file. If omitted, writes to stdout.
- `--report`: Print human-readable summary to stderr.

**Exit codes**:
- 0: All cases passed.
- 1: Bad usage or malformed suite.
- 2: One or more cases failed.
- 3: Model could not be invoked.
- 4: File unreadable.

### `compare`

Compare two reports and classify changes.

```bash
python -m promptlab compare --baseline <report.json> --candidate <report.json> [--out diff.json]
```

**Output**: JSON diff with case classifications (regressed, improved, unchanged, new, removed) and cost delta.

### `doctor`

Diagnostic utility.

```bash
python -m promptlab doctor
```

Checks: Python version, model binary, suites directory, assertion types.

## Suite Format

Suites are JSON files with cases and assertions.

```json
{
  "name": "suite-name",
  "prompt_file": "path/to/prompt.txt",
  "model": {
    "temperature": 0.0,
    "max_tokens": 256
  },
  "runs": 1,
  "cases": [
    {
      "id": "c001",
      "input": "text or {\"file\": \"path\"}",
      "assert": [
        {"type": "json_valid"},
        {"type": "json_field_equals", "field": "category", "value": "billing"}
      ]
    }
  ]
}
```

## Assertion Types

- **contains**: Output contains substring.
- **not_contains**: Output does not contain substring.
- **equals**: Output equals value (optionally normalized).
- **matches**: Regex matches output.
- **json_valid**: Output parses as JSON.
- **json_field_equals**: Dotted path in JSON equals value.
- **max_tokens**: Output tokens at or below threshold.
- **finish_is**: Finish field equals "stop", "length", or "refusal".

## Understanding Results

**Pass**: Case passed all assertions in all runs.

**Fail**: Case failed at least one assertion in all runs.

**Flaky**: Case passed in some runs, failed in others.

A case that passes 7/10 times is flaky, not a pass.

## Development

Run tests:

```bash
python -m unittest discover
```

Build and commit:

```bash
git add .
git commit -m "feat: implement run command"
```
