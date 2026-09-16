# ADR-004: Cost Accounting Approach

**Status**: Accepted  
**Date**: 2026-09-16  
**Deciders**: Team  

## Context

Language models incur token costs. When running a suite with `--runs N`, the total cost scales with N:

- 1 run at 100 tokens → 100 tokens total
- 10 runs at 100 tokens → 1000 tokens total

The `compare` command reports cost delta (how token usage changed between baseline and candidate). The question: **How should we account for costs in reports?**

Options:
1. **Totals**: Sum token counts across all runs
2. **Averages**: Compute per-run or per-case averages
3. **Both**: Report both for transparency

## Decision

**Report both totals and averages.**

**In `run` report**:
- `totals.tokens_in`: Sum of all tokens_in across all runs and cases
- `totals.tokens_out`: Sum of all tokens_out across all runs and cases
- `cases[].tokens_out_avg`: Average output tokens per run for this case

**In `compare` report**:
- `cost_delta.tokens_in_delta`: baseline total - candidate total
- `cost_delta.tokens_in_pct`: (candidate - baseline) / baseline * 100
- `cost_delta.tokens_out_delta`: (same for output)
- `cost_delta.tokens_out_pct`: (same for output)

**Example**:
```json
{
  "baseline": {
    "totals": {
      "tokens_in": 1000,
      "tokens_out": 500
    }
  },
  "candidate": {
    "totals": {
      "tokens_in": 1100,
      "tokens_out": 520
    }
  },
  "cost_delta": {
    "tokens_in_delta": -100,
    "tokens_in_pct": 10.0,
    "tokens_out_delta": -20,
    "tokens_out_pct": 4.0
  }
}
```

## Rationale

**Why totals?**

- Reflects true resource usage and cost
- Allows budgeting (e.g., "this change costs 10% more tokens")
- More comparable across suites (not affected by --runs variance)

**Why averages?**

- Normalized comparison (allows comparison across different --runs values)
- Useful for efficiency metrics (e.g., "cost per case")
- Helps identify which cases are expensive

**Why both?**

- Judges need complete transparency
- Totals show impact; averages show efficiency
- No ambiguity (users can pick the view that matters)
- Small overhead (just include both numbers)

## Alternatives Considered

### A1: Totals only

**Pros**:
- Simpler reporting
- Reflects true cost
- Directly comparable to budget

**Cons**:
- Hard to compare across different --runs values
- Doesn't show efficiency per run
- Loses per-case granularity

**Rejected**: Incomplete picture for judges.

### A2: Averages only

**Pros**:
- Normalized comparison
- Shows efficiency per run
- Not affected by --runs variance

**Cons**:
- Doesn't reflect true cost
- Misleading (e.g., 2 runs at 500 tokens avg looks cheaper than 1 run at 1000 tokens total, but it's the same)
- Loses information about total cost impact

**Rejected**: Hides true resource usage.

### A3: Differential accounting (per-run delta)

**Pros**:
- Shows exactly what changed per run

**Cons**:
- Too granular
- Doesn't answer "how much did cost change overall?"
- Complex to compute and report

**Rejected**: Over-engineered.

## Consequences

**Positive**:
- Judges have full picture of cost impact
- Users can understand both total cost and efficiency
- No ambiguity or missing information
- Scales well to different --runs values

**Negative**:
- Slightly more output (but negligible)
- Users might misinterpret (e.g., confuse totals with averages)
- Mitigation: Clear labels and documentation

## Implementation Notes

```python
import math

def compute_tokens(text: str) -> int:
    """Token rule: ceil(len(text) / 4)."""
    return math.ceil(len(text) / 4)

def build_report(cases_results: list, runs: int) -> dict:
    """Build report with both totals and averages."""
    total_tokens_in = 0
    total_tokens_out = 0
    
    for case in cases_results:
        # Sum tokens from all runs
        total_tokens_in += case["total_tokens_in"]
        total_tokens_out += case["total_tokens_out"]
        
        # Compute averages
        case["tokens_out_avg"] = case["total_tokens_out"] // runs
    
    return {
        "totals": {
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out
        },
        "cases": cases_results
    }

def compare_cost(baseline: dict, candidate: dict) -> dict:
    """Compute cost delta."""
    baseline_in = baseline["totals"]["tokens_in"]
    candidate_in = candidate["totals"]["tokens_in"]
    baseline_out = baseline["totals"]["tokens_out"]
    candidate_out = candidate["totals"]["tokens_out"]
    
    return {
        "tokens_in_delta": candidate_in - baseline_in,
        "tokens_in_pct": (candidate_in - baseline_in) / baseline_in * 100 if baseline_in > 0 else 0,
        "tokens_out_delta": candidate_out - baseline_out,
        "tokens_out_pct": (candidate_out - baseline_out) / baseline_out * 100 if baseline_out > 0 else 0
    }
```

## References

- Brief: MUST 5, MUST 16
- Spec: Section 5 (Report Schema), Section 9 (Cost Accounting)
- Token rule: `math.ceil(len(text) / 4)` everywhere

---

**Next ADRs to consider**:
- ADR-005: Assertion evaluation order
