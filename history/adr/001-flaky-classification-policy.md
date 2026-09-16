# ADR-001: Flaky Classification Policy

**Status**: Accepted  
**Date**: 2026-09-16  
**Deciders**: Team  

## Context

promptlab runs test cases multiple times (via `--runs N`) to measure non-determinism in prompt behavior. At temperature > 0, the same case does not always produce the same result.

Traditional test runners classify results as only pass or fail. But prompt testing requires distinguishing three outcomes:
- **Pass**: Passed all runs
- **Fail**: Failed all runs  
- **Flaky**: Passed some runs, failed others

The question: What pass_rate threshold determines which outcome a case should report?

## Decision

**A case's outcome is determined by its pass_rate:**

- **pass**: pass_rate = 1.0 (all runs passed)
- **fail**: pass_rate = 0.0 (all runs failed)
- **flaky**: 0 < pass_rate < 1.0 (mixed: some passed, some failed)

**No threshold tolerance.** Any mixed result is flaky, regardless of --runs.

Examples:
- 10 runs, 10 passes → **pass**
- 10 runs, 0 passes → **fail**
- 10 runs, 7 passes, 3 fails → **flaky**
- 2 runs, 1 pass, 1 fail → **flaky**

## Rationale

**Why this policy?**

From the brief: "A case that passes 7 times out of 10 is not a passing case, and reporting it as one is the most common way a prompt harness lies to its owner."

The core insight is that non-determinism is the problem we're trying to solve. Hiding flakiness defeats the purpose of the tool.

**Why not a threshold?**

- Thresholds create false precision (e.g., "0.8 is pass but 0.7 is flaky") and hide instability.
- Users running --runs 2 vs --runs 100 would get different classifications, making results incomparable.
- Judges (the brief's evaluators) will run suites with various --runs values; we must be consistent.

## Alternatives Considered

### A1: Threshold-based (e.g., pass_rate ≥ 0.9)

**Pros**:
- Tolerates minor randomness and noise
- Reduces "false positives" (cases flipped by luck)

**Cons**:
- Arbitrary threshold (why 0.9 and not 0.8?)
- Hides real instability (7/10 would be pass)
- Violates the brief's intent
- Judges could swap thresholds, making results invalid

**Rejected**: Defeats the tool's core purpose.

### A2: Threshold depends on --runs

**Pros**:
- Statistically principled (higher runs → stricter threshold)

**Cons**:
- Complexity (requires confidence intervals or statistical model)
- Implementation overhead
- Two runs at different --runs values are now incomparable
- Not required by the brief

**Rejected**: Over-engineered for the problem.

## Consequences

**Positive**:
- Strict detection catches subtle instability early
- Simple, rule-based classification (no ambiguity)
- Aligns with the brief's intent and philosophy
- Forces users to run sufficient --runs for stability
- Judges can trust that "pass" truly means stable

**Negative**:
- High-temperature suites may need many runs to achieve pass status
- A case that's "mostly stable" (e.g., 19/20) is still flaky
- Users might feel penalized for honest reporting

**Risk**: Users may misunderstand why a "mostly passing" case is flaky. Mitigation: Clear documentation in USAGE.md and --report summaries.

## Implementation Notes

- Report `pass_rate` per case for transparency
- Compute pass_rate as `passed_count / runs`
- In `--report` output, show counts (e.g., "7/10 passed, status: flaky")
- In compare output, flag any pass_rate change (even 1.0 → 0.9) as regression

## References

- Brief: MUST 10, MUST 11, MUST 15
- Spec: Section 6 (Flaky Policy and Threshold)
- Constitution: Core Principles #4

---

**Next ADRs to consider**:
- ADR-002: Fenced JSON handling
- ADR-003: Regression detection strategy
