# ADR-003: Regression Detection Strategy

**Status**: Accepted  
**Date**: 2026-09-16  
**Deciders**: Team  

## Context

The `compare` command analyzes two reports and classifies each case as: regressed, improved, unchanged, new, or removed.

The key question for regression: **When comparing pass_rate values, what change counts as a regression?**

Example scenarios:
- Baseline 1.0 → Candidate 0.9: Regression?
- Baseline 1.0 → Candidate 0.99: Regression?
- Baseline 0.8 → Candidate 0.7: Regression?

## Decision

**Any drop in pass_rate is a regression, regardless of magnitude or absolute level.**

Classification rules:
- **regressed**: candidate_pass_rate < baseline_pass_rate
- **improved**: candidate_pass_rate > baseline_pass_rate  
- **unchanged**: candidate_pass_rate = baseline_pass_rate
- **new**: case in candidate but not in baseline
- **removed**: case in baseline but not in candidate

Examples:
- 1.0 → 0.9: regressed ✓
- 1.0 → 0.5: regressed ✓
- 0.8 → 0.7: regressed ✓
- 0.6 → 0.6: unchanged
- 0.5 → 0.8: improved ✓

## Rationale

**Why detect any drop?**

From the brief (MUST 15): *"A pass rate moving from 1.0 to 0.9 is a regression even if the case is still labelled a pass under your policy. Silent degradation is exactly what this tool exists to catch."*

The tool's core purpose is to **catch silent performance degradation**. A prompt that worked perfectly (1.0) but now works almost perfectly (0.9) has regressed. The diff should flag this so the user can decide if 0.1 loss is acceptable.

**Why not use a threshold (e.g., 0.05 drop)?**

- Thresholds hide real regressions. A 0.04 drop might be noise, but cumulatively over many cases it's significant.
- Users should judge "acceptability", not the tool. The tool's job is to report what changed.
- Judges will expect sensitive detection; a harness that misses regressions is worse than one that reports them.

## Alternatives Considered

### A1: Threshold-based (e.g., drops ≥ 0.05 are regression)

**Pros**:
- Reduces noise (ignores tiny variations)
- More forgiving for flaky cases

**Cons**:
- Arbitrary threshold (why 0.05 and not 0.02?)
- Hides real degradation (0.04 drop is not reported)
- Violates the brief's intent ("even 1.0 to 0.9")
- Judges can change expectations, invalidating results

**Rejected**: Defeats the tool's purpose.

### A2: Threshold depends on --runs

**Pros**:
- Statistically principled (more runs → lower threshold)

**Cons**:
- Complexity (requires statistical model)
- Results incomparable across different --runs values
- Not required by the brief

**Rejected**: Over-engineered.

### A3: Categorical comparison (pass/fail/flaky status only, ignore pass_rate)

**Pros**:
- Simpler (fewer state transitions)

**Cons**:
- Loses fine-grained information
- Misses the regression case: flaky → flaky but lower pass_rate
- Violates MUST 15

**Rejected**: Insufficient precision.

## Consequences

**Positive**:
- Catches all degradation (no false negatives)
- Aligns with the brief's philosophy
- Forces users to consider whether regressions are acceptable
- Judges can trust regression reports

**Negative**:
- May report "regressions" that are within noise (0.95 → 0.94 on 20 runs)
- Users might feel penalized for minor variations
- "Regressed" status might not always mean "bad" (depends on context)

**Mitigation**:
- In reports, show the actual pass_rate drop (e.g., "1.0 → 0.9, -10%") so users can judge severity
- Document in USAGE.md that regression ≠ failure; it's a signal for investigation

## Implementation Notes

```python
def classify_case(baseline_pass_rate: float, candidate_pass_rate: float) -> str:
    """Classify a case by comparing pass rates."""
    if baseline_pass_rate > candidate_pass_rate:
        return "regressed"
    elif baseline_pass_rate < candidate_pass_rate:
        return "improved"
    else:
        return "unchanged"

def compare_reports(baseline: dict, candidate: dict) -> dict:
    """Generate diff with case classifications."""
    diff = {
        "baseline_suite": baseline["suite"],
        "candidate_suite": candidate["suite"],
        "cases": []
    }
    
    baseline_cases = {c["id"]: c for c in baseline["cases"]}
    candidate_cases = {c["id"]: c for c in candidate["cases"]}
    
    all_ids = set(baseline_cases.keys()) | set(candidate_cases.keys())
    
    for case_id in sorted(all_ids):
        if case_id in baseline_cases and case_id in candidate_cases:
            status = classify_case(
                baseline_cases[case_id]["pass_rate"],
                candidate_cases[case_id]["pass_rate"]
            )
        elif case_id in candidate_cases:
            status = "new"
        else:
            status = "removed"
        
        diff["cases"].append({
            "id": case_id,
            "status": status,
            "baseline_pass_rate": baseline_cases.get(case_id, {}).get("pass_rate"),
            "candidate_pass_rate": candidate_cases.get(case_id, {}).get("pass_rate")
        })
    
    return diff
```

## References

- Brief: MUST 14, MUST 15
- Spec: Section 8 (Regression Definition), Section 10 (Compare Output Schema)
- Related ADR: ADR-001 (Flaky Classification)

---

**Next ADRs to consider**:
- ADR-004: Cost accounting approach
- ADR-005: Assertion evaluation order
