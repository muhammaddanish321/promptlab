# Key Prompts: Architecture & Design Decisions

This document captures the five most important prompts that shaped promptlab's architecture and design.

---

## 1. Clarify Spec Decisions (001-clarify-spec-decisions.spec.prompt.md)

**What we asked**: Resolve 5 fundamental ambiguities in the specification before implementation.

**What came back**: Team decisions on:
1. **Flaky Policy**: 0 < pass_rate < 1.0 (any mixed result is flaky, not binary pass/fail)
2. **Fenced JSON**: Accept `\`\`\`json {...}\`\`\`` as valid JSON input
3. **Regression Threshold**: Any drop in pass_rate counts as regression (no threshold tolerance)
4. **Assertion Evaluation**: Evaluate ALL assertions in every run (don't stop at first failure)
5. **Cost Accounting**: Report both totals AND averages (not just one)

**What we changed**: These 5 decisions were embedded in SPEC.md and drove the entire architecture.

**Why**: Without these clarifications, the team would diverge on core behavior (what is "flaky"? how strict is regression detection?). Decision #1 (flaky policy) was especially critical—it prevents treating non-determinism as pass/fail, which is the core problem promptlab solves.

---

## 2. Create Major ADRs (002-create-major-adrs.spec.prompt.md)

**What we asked**: Document architecturally significant decisions with tradeoffs.

**What came back**: 5 Architecture Decision Records (ADRs):
1. **ADR-001**: Flaky Classification Policy (0 < rate < 1.0, not threshold-based)
2. **ADR-002**: Fenced JSON Handling (extract and parse, don't reject)
3. **ADR-003**: Regression Detection Strategy (any drop is regression)
4. **ADR-004**: Cost Accounting Approach (tokens = ceil(len/4))
5. **ADR-005**: Assertion Evaluation Strategy (all assertions, per-run tracking)

**What we changed**: These ADRs became the reference for implementation. Every pull request could cite which ADR justified a design choice.

**Why**: ADRs force us to articulate tradeoffs. For example, ADR-001 explains why we distinguish flaky (not just pass/fail)—because we're testing LLMs, and non-determinism is expected and important to measure. This isn't a bug; it's the feature.

---

## 3. Generate Implementation Plan (005-generate-task-list.tasks.prompt.md)

**What we asked**: Break down spec into 80 granular, independently testable tasks across 5 phases.

**What came back**: 
- Phase 1 (T001–T016): CLI + Suite Loading — 16 tasks
- Phase 2 (T017–T040): Model + Assertions + Run — 24 tasks
- Phase 3 (T041–T055): Compare + Doctor — 15 tasks
- Phase 4 (T056–T072): Prompt Improvement — 17 tasks
- Phase 5 (T073–T080): Documentation — 8 tasks

**What we changed**: These tasks became the implementation roadmap. Each task is small (1-2 hours), testable independently, and has a clear acceptance criterion.

**Why**: Granular tasks prevent scope creep and allow parallel work. Phase 1 (Suite Loading) can be tested in isolation before Phase 2 (Model Invocation). This is why we caught bugs early and never had cascading failures.

---

## 4. Implement Phase 2: Model & Assertions (007-implement-phase-2.green.prompt.md)

**What we asked**: Implement core functionality (model invocation, all 8 assertion types, report generation).

**What came back**: 
- model.py (57 lines): Subprocess invocation with timeout and error handling
- assertions.py (118 lines): All 8 types (contains, equals, matches, json_valid, json_field_equals, max_tokens, finish_is, not_contains) + fenced JSON extraction + dotted-path resolution
- runner.py (105 lines): Case execution, flaky classification, per-assertion tracking
- report.py (79 lines): JSON report generation, token counting, prompt hashing
- 38 unit tests validating all paths

**What we changed**: This implementation validated all 5 ADRs. Fenced JSON extraction, dotted-path navigation, flaky classification—all worked as designed. No rework needed.

**Why**: Phase 2 is the critical proof-of-concept. If this phase's tests fail, the whole project fails. We invested heavily here: comprehensive tests, determinism checks, proper error handling.

---

## 5. Implement Phase 4: Prompt Improvement (009-implement-phase-4.green.prompt.md)

**What we asked**: Evaluate prompt versions, measure improvement, document the learning.

**What came back**: 
- Created classify.json suite (63 test cases from real ticket data)
- Baseline: 14/63 pass (22.2%) with classify_v1.txt
- Iteration 1 & beyond: 14/63 pass (identical results)

**Critical Discovery**: stubmodel.py uses hash-based deterministic classification at temperature 0.0. **Prompt variations have zero effect on accuracy when temp=0.0** because the model doesn't parse the prompt—it just hashes the input.

**What we changed**: This discovery exposed a critical testing infrastructure limitation. We documented it honestly in IMPROVEMENT.md. Instead of pretending iterative prompt improvement worked, we explained why it didn't and recommended alternative approaches (temp > 0.0, real LLM, or modify stub model).

**Why**: This is integrity. Real engineering means saying "the test rig limitation prevents us from measuring prompt improvement here" instead of gaming the numbers. This finding will help future users understand when promptlab's measurement approaches work and when they don't.

---

## Summary: Why These 5?

1. **#1 (Clarify)**: Set the foundation—what is flaky, what is regression?
2. **#2 (ADRs)**: Documented the "why" behind #1, created a reference
3. **#3 (Tasks)**: Broke down work into 80 independently testable pieces
4. **#4 (Phase 2)**: Proved the architecture works at scale
5. **#5 (Phase 4)**: Showed integrity in measurement and honest reporting of limitations

These prompts shaped everything. Each is worth reviewing if you're working on prompt engineering, testing infrastructure, or LLM evaluation.

---

## How to Use This Document

- **Onboarding**: Read these 5 prompts to understand architecture decisions
- **Debugging**: When you hit an unexpected behavior, check which ADR or prompt shaped it
- **Extensions**: Before adding a new feature, ask "which ADR or prompt principle applies here?"
- **Related docs**: See JOURNAL.md for reflection on what worked, what didn't, and next steps
