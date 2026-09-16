# CLI Contract: `promptlab doctor`

**Command**: `python -m promptlab doctor`

---

## Purpose

Diagnostic utility for environment setup. Checks that promptlab can run and all dependencies are available.

**Target Audience**: Users setting up promptlab for the first time, CI/CD systems, judges evaluating the harness.

---

## Checks Performed

### Python Version

**Check**: Python is 3.10 or higher

**Implementation**:
```python
import sys
if sys.version_info < (3, 10):
    print("✗ Python version: {}.{} (need 3.10+)".format(sys.version_info.major, sys.version_info.minor))
else:
    print("✓ Python version: {}.{} OK".format(sys.version_info.major, sys.version_info.minor))
```

**Failure**: Print version; no exit code 1 (doctor continues)

---

### Model Binary

**Check**: Model binary is reachable and responds to `--help`

**Implementation**:
```python
import subprocess
try:
    result = subprocess.run(
        ["python", "stubmodel.py", "--help"],
        capture_output=True,
        timeout=5
    )
    if result.returncode == 0:
        print("✓ Model binary: reachable and responding")
    else:
        print("✗ Model binary: returned exit code {}".format(result.returncode))
except FileNotFoundError:
    print("✗ Model binary: stubmodel.py not found")
except subprocess.TimeoutExpired:
    print("✗ Model binary: timeout (>5s)")
except Exception as e:
    print("✗ Model binary: {}".format(str(e)))
```

**Failure**: Print error; doctor continues

---

### Suites Directory

**Check**: `suites/` directory exists and is readable

**Implementation**:
```python
import os
if os.path.isdir("suites"):
    suite_files = [f for f in os.listdir("suites") if f.endswith(".json")]
    print("✓ Suites directory: found {} suite files".format(len(suite_files)))
else:
    print("✗ Suites directory: not found or not readable")
```

**Failure**: Print error; doctor continues

---

### Assertion Types

**Check**: All 8 assertion types are registered and recognized

**Assertion Types to Check**:
1. contains
2. not_contains
3. equals
4. matches
5. json_valid
6. json_field_equals
7. max_tokens
8. finish_is

**Implementation**:
```python
from promptlab.assertions import ASSERTION_TYPES
expected = {"contains", "not_contains", "equals", "matches", "json_valid", "json_field_equals", "max_tokens", "finish_is"}
found = set(ASSERTION_TYPES.keys())
if expected == found:
    print("✓ Assertion types: all 8 registered")
else:
    missing = expected - found
    extra = found - expected
    if missing:
        print("✗ Assertion types: missing {}".format(", ".join(missing)))
    if extra:
        print("✗ Assertion types: unexpected {}".format(", ".join(extra)))
```

**Failure**: Print error; doctor continues

---

## Output Format

**Example Output**:
```
promptlab Doctor (2026-09-16)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Python version: 3.10 OK
✓ Model binary: reachable and responding
✓ Suites directory: found 2 suite files
  - suites/smoke.json (4 cases)
  - suites/classify.json (63 cases)
✓ Assertion types: all 8 registered

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: Ready to run

Summary:
  - Python 3.10+: ✓
  - Model: ✓
  - Suites: ✓
  - Assertions: ✓

Run 'python -m promptlab run --suite suites/smoke.json' to test.
```

---

## Exit Codes

| Code | Meaning | Condition |
|------|---------|-----------|
| 0 | All checks passed | All 4 checks successful |
| 1 | One or more checks failed | Any check failed |

**Note**: Doctor prints results for all checks, then exits with summary code at end.

---

## Implementation Notes

### Ordering
- Run checks in order: Python, Model, Suites, Assertions
- Continue even if one check fails (show all problems at once)

### Timeouts
- Model check: 5-second timeout on subprocess
- If timeout, print error and continue

### File Discovery
- Suites: Look in `suites/` directory relative to working directory
- Model: Try `python stubmodel.py` (relies on PATH or explicit python binary)

### Edge Cases

**No suites found**: Print warning but don't fail
```
⚠ Suites directory: found 0 suite files (create suites/*.json)
```

**Model check fails**: Suggest next steps
```
✗ Model binary: stubmodel.py not found
  → Try: python stubmodel.py --help
  → Or set PATH to include model location
```

---

## Human-Readable Messaging

All messages must be:
- ✓ Concise (one line per check result)
- ✓ Clear (use ✓/✗ symbols)
- ✓ Actionable (suggest fixes for failures)
- ✓ Helpful (include file counts, paths)

---

**Used by**: Users, CI/CD, judges. Must always succeed or fail clearly.
