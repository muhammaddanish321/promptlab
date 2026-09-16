# ADR-002: Fenced JSON Handling in Assertions

**Status**: Accepted  
**Date**: 2026-09-16  
**Deciders**: Team  

## Context

Language models sometimes wrap JSON output in markdown code fences:

```
```json
{"category": "billing", "confidence": 0.95}
```
```

The tool has two assertions that parse JSON:
1. `json_valid` — Checks if output is valid JSON
2. `json_field_equals` — Parses JSON and resolves a dotted path

Question: Should fenced JSON count as valid JSON?

## Decision

**Accept fenced JSON.** Extract the inner JSON and parse it.

**Parsing logic**:
1. Check if output matches pattern: ` ```(language)?\n<content>\n``` `
2. If matched, extract `<content>`
3. Parse extracted (or original) content as JSON
4. If parsing succeeds, assertion passes; if it fails, assertion fails

**Consistency requirement**: Both `json_valid` and `json_field_equals` must apply this rule identically.

## Rationale

**Why accept fenced JSON?**

1. **Real-world necessity**: Models trained to output JSON in markdown often wrap output in fences. Rejecting this penalizes reasonable formatting.
2. **Pragmatism over purity**: The tool's job is to evaluate prompts, not nitpick JSON formatting. A prompt that says "output JSON in a code block" should succeed.
3. **Extracting inner JSON is standard**: Many JSON processors handle code-fenced JSON; this is a known pattern.
4. **Judges will understand**: Evaluators will expect a reasonable harness to handle real model behavior.

**Why keep the rule consistent?**

If `json_valid` accepts fenced JSON but `json_field_equals` rejects it, assertions would be inconsistent. A case with fenced JSON might pass `json_valid` but fail `json_field_equals`, which is confusing and wrong.

## Alternatives Considered

### A1: Reject fenced JSON entirely

**Pros**:
- Simpler logic (no extraction needed)
- Forces model to output clean JSON
- No risk of mis-extraction

**Cons**:
- Breaks on common model behavior (code fences are standard)
- Penalizes reasonable prompt instructions ("output JSON in a code block")
- Judges will see this as brittle

**Rejected**: Too strict; impractical for real prompts.

### A2: Accept fenced JSON only in json_valid, not json_field_equals

**Pros**:
- Gradual adoption (start permissive, tighten later)

**Cons**:
- Inconsistent behavior creates bugs and confusion
- Violates the principle of least surprise
- Harder to debug (same output, different results in different assertions)

**Rejected**: Inconsistency is worse than strictness.

## Consequences

**Positive**:
- Handles real model output gracefully
- Reduces false negatives (cases that should pass but don't)
- Aligns with how users actually use language models
- Judges will see it as practical

**Negative**:
- Extraction logic adds complexity (regex or state machine)
- Risk of malformed fences (e.g., ` ```\n{incomplete json\n``` `) — will fail gracefully
- Slightly slower (extraction before parsing)

**Edge cases handled**:
- Nested code fences: Extract outermost only
- Malformed fences: Fall through to raw parsing (will likely fail)
- No fence: Parse as-is
- Multiple fences: Extract first and parse; if it fails, fail the assertion

## Implementation Notes

```python
def extract_json(output: str) -> str:
    """Extract JSON from fenced code block if present, else return output."""
    import re
    # Match: ```(language)?\nCONTENT\n```
    match = re.match(r'^```(?:\w+)?\s*\n([\s\S]*?)\n```\s*$', output.strip())
    if match:
        return match.group(1)
    return output

def json_valid(output: str) -> bool:
    """Check if output (possibly fenced) is valid JSON."""
    import json
    try:
        json.loads(extract_json(output))
        return True
    except json.JSONDecodeError:
        return False

def json_field_equals(output: str, field: str, value: Any) -> bool:
    """Resolve dotted path in output JSON and compare to value."""
    import json
    try:
        data = json.loads(extract_json(output))
        resolved = resolve_dotted_path(data, field)
        return resolved == value
    except (json.JSONDecodeError, KeyError, IndexError):
        return False
```

## References

- Brief: MUST 4, MUST 6
- Spec: Section 3.5 (json_valid), Section 3.6 (json_field_equals)
- Related ADR: ADR-003 (Regression detection)

---

**Next ADRs to consider**:
- ADR-003: Regression detection strategy
- ADR-004: Cost accounting approach
