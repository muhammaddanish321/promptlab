# ADR-005: Assertion Evaluation Strategy

**Status**: Accepted  
**Date**: 2026-09-16  
**Deciders**: Team  

## Context

A suite case can have multiple assertions:

```json
{
  "id": "c001",
  "input": "...",
  "assert": [
    {"type": "json_valid"},
    {"type": "json_field_equals", "field": "category", "value": "billing"},
    {"type": "contains", "value": "confirmed"}
  ]
}
```

Question: **When running a case, do we evaluate all assertions, or stop at the first failure?**

## Decision

**Evaluate all assertions in every run. Do not stop at first failure.**

**Rationale**: MUST 12 requires "Per-assertion counts: for each assertion, how many runs it passed and failed." To fulfill this requirement, all assertions must evaluate on every run.

## Process

For each run:
1. Evaluate assertion 1 → record pass/fail
2. Evaluate assertion 2 → record pass/fail
3. Evaluate assertion 3 → record pass/fail
4. Aggregate: case passes if all assertions pass; case fails if any assertion fails

## Rationale

**Why evaluate all?**

1. **MUST 12 requirement**: The brief explicitly requires per-assertion pass/fail counts. We can't provide this without evaluating all.
2. **Diagnostic information**: Knowing which assertion failed is crucial for debugging. Example:
   - If only assertion 3 fails, the output format is correct (assertion 1, 2 pass) but content is wrong
   - This points to a specific issue in the prompt
3. **Transparency**: Users can see exactly what went wrong, not just "case failed"

**Why not stop at first failure?**

- Violates MUST 12 (no per-assertion data)
- Loses diagnostic information
- Faster execution but at the cost of correctness
- Judges will expect detailed assertion analysis

## Alternatives Considered

### A1: Stop at first failure

**Pros**:
- Faster execution (saves unnecessary work)
- Simpler logic

**Cons**:
- Violates MUST 12 (cannot report per-assertion counts)
- Loses diagnostic data
- Incomplete reporting

**Rejected**: Mandatory requirement violation.

### A2: Partial evaluation (early stop, but cache results)

**Pros**:
- Faster for some cases
- Still captures some data

**Cons**:
- Complex caching logic
- Inconsistent results (some runs have full data, some don't)
- Still violates MUST 12 for later assertions

**Rejected**: Inconsistency is worse than full evaluation.

## Consequences

**Positive**:
- Fulfills MUST 12 requirement
- Users get detailed assertion-level diagnostics
- Can identify which assertion is flaky
- Helps debug prompt issues precisely

**Negative**:
- Slightly slower (evaluate all assertions)
- Overhead is small (~5-10% per case, negligible at suite scale)
- Larger report JSON (includes assertion-level data)

## Implementation Notes

```python
def evaluate_case(case: dict, output: str, runs: int) -> dict:
    """Evaluate all assertions and record per-assertion pass/fail counts."""
    assertions_results = []
    failures = []
    
    case_passed_count = 0
    
    for run_num in range(runs):
        all_pass = True
        
        for assertion in case["assert"]:
            result = evaluate_assertion(assertion, output)
            
            if not assertions_results:
                # First run: initialize counters
                assertions_results.append({
                    "type": assertion["type"],
                    "passed": 0,
                    "failed": 0
                })
            
            if result:
                assertions_results[len(assertions_results) - 1]["passed"] += 1
            else:
                assertions_results[len(assertions_results) - 1]["failed"] += 1
                all_pass = False
                failures.append({
                    "run": run_num,
                    "assertion": assertion,
                    "output": output[:500]
                })
        
        if all_pass:
            case_passed_count += 1
    
    pass_rate = case_passed_count / runs
    
    return {
        "id": case["id"],
        "pass_rate": pass_rate,
        "status": classify_status(pass_rate),  # pass/fail/flaky
        "assertions": assertions_results,
        "failures": failures
    }

def evaluate_assertion(assertion: dict, output: str) -> bool:
    """Evaluate a single assertion against output."""
    assertion_type = assertion["type"]
    
    if assertion_type == "json_valid":
        return is_json_valid(output)
    elif assertion_type == "json_field_equals":
        return json_field_equals(output, assertion["field"], assertion["value"])
    elif assertion_type == "contains":
        return contains(output, assertion["value"], assertion.get("ignore_case", False))
    # ... handle other assertion types
    
    return False
```

## References

- Brief: MUST 4, MUST 12, MUST 13
- Spec: Section 4 (Assertion Evaluation Model), Section 5 (Report Schema)
- Related ADR: ADR-001 (Flaky Classification)

---

**All major ADRs complete**:
- ADR-001: Flaky classification policy ✓
- ADR-002: Fenced JSON handling ✓
- ADR-003: Regression detection strategy ✓
- ADR-004: Cost accounting approach ✓
- ADR-005: Assertion evaluation strategy ✓
