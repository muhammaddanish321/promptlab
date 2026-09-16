---
ID: 002
TITLE: Create major architecture decision records
STAGE: spec
DATE_ISO: 2026-09-16
SURFACE: agent
MODEL: claude-haiku-4-5-20251001
FEATURE: promptlab
BRANCH: master
USER: muhammaddanish321@gmail.com
COMMAND: /sp.adr Flaky classification policy
LABELS: ["adr", "architecture", "decisions"]
LINKS:
  SPEC: specs/master/spec.md
  ADR: history/adr/001-005-*.md
  TICKET: null
  PR: null
---

## Prompt

```
Create ADRs (Architecture Decision Records) for the major decisions documented in the spec.

Focus on decisions that impact implementation, have notable tradeoffs, and will be questioned later:

1. Flaky classification policy (pass, fail, flaky distinction)
2. Fenced JSON handling (extract inner JSON or not)
3. Regression detection (any drop vs threshold)
4. Cost accounting (totals, averages, or both)
5. Assertion evaluation (all vs stop-first)

For each ADR:
- Document the decision clearly
- Explain why this approach was chosen
- List alternatives considered and why they were rejected
- Include consequences and implementation notes
- Reference the brief and spec sections

Create 5 ADRs in history/adr/ directory.
```

## Response

**ADR creation completed successfully.**

**5 ADRs created**:

1. **ADR-001: Flaky Classification Policy**
   - Decision: Status = pass (1.0), fail (0.0), or flaky (0 < rate < 1.0)
   - Rationale: Strict detection aligns with brief intent; catches instability
   - Alternatives: Threshold-based (rejected as arbitrary), run-dependent (rejected as complex)

2. **ADR-002: Fenced JSON Handling**
   - Decision: Accept fenced JSON; extract inner JSON and parse
   - Rationale: Practical; handles real model behavior; consistent between json_valid and json_field_equals
   - Alternatives: Reject fenced JSON (rejected as too strict), inconsistent handling (rejected as confusing)

3. **ADR-003: Regression Detection Strategy**
   - Decision: Any drop in pass_rate counts as regression, regardless of magnitude
   - Rationale: Aligns with brief MUST 15; catches silent degradation
   - Alternatives: Threshold-based (rejected as hiding regressions), run-dependent (rejected as complex)

4. **ADR-004: Cost Accounting Approach**
   - Decision: Report both totals and averages for full transparency
   - Rationale: Totals show impact; averages show efficiency; judges need both views
   - Alternatives: Totals only (incomplete), Averages only (misleading), Differential (over-engineered)

5. **ADR-005: Assertion Evaluation Strategy**
   - Decision: Evaluate all assertions in every run; do not stop at first failure
   - Rationale: Required by MUST 12 (per-assertion counts); provides diagnostic data
   - Alternatives: Stop-first (violates MUST 12), Partial evaluation (inconsistent and incomplete)

**All ADRs include**:
- Clear decision statement
- Rationale section explaining "why"
- 2-3 alternatives with pros/cons
- Consequences (positive and negative)
- Implementation pseudocode or notes
- References to brief and spec sections

---

## Outcome

- ✅ All major architectural decisions documented
- ✅ Alternatives considered and rejected documented
- ✅ Implementation implications clear
- ✅ Judges will understand reasoning and tradeoffs

**Status**: Ready for `/sp.plan` (implementation roadmap)

---

## Changes Made

**Files created**:
- history/adr/001-flaky-classification-policy.md
- history/adr/002-fenced-json-handling.md
- history/adr/003-regression-detection-strategy.md
- history/adr/004-cost-accounting-approach.md
- history/adr/005-assertion-evaluation-strategy.md
- history/prompts/master/002-create-major-adrs.spec.prompt.md (this PHR)

**Tests run**: None (ADRs are documentation)

**Evaluation**:
- All ADRs follow a consistent structure
- Each documents a decision that impacts implementation
- Alternatives are explicit and justified
- References link back to brief and spec
- No contradictions or conflicts detected
