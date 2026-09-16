---
ID: 005
TITLE: Generate comprehensive task list
STAGE: tasks
DATE_ISO: 2026-09-16
SURFACE: agent
MODEL: claude-haiku-4-5-20251001
FEATURE: promptlab
BRANCH: master
USER: muhammaddanish321@gmail.com
COMMAND: /sp.tasks
LABELS: ["tasks", "implementation", "phases"]
LINKS:
  SPEC: specs/master/spec.md
  PLAN: specs/master/plan.md
  ADR: history/adr/001-005-*.md
  TICKET: null
  PR: null
---

## Prompt

```
Generate a detailed task list from the implementation plan and specification.

Tasks should:
1. Follow strict checklist format: "- [ ] [TaskID] [P] [Story] Description with file path"
2. Be organized by implementation phase (5 phases from plan.md)
3. Include acceptance criteria per phase
4. Mark parallelizable tasks with [P]
5. Include exact file paths for each task
6. Total ~80 tasks covering all implementation work
7. Be independently testable per phase
8. Include unit test tasks
9. Document prompt improvement track (4+ iterations)
10. Include documentation tasks (USAGE, PROMPTS, JOURNAL)

Each phase must have clear acceptance criteria and be completable independently.
```

## Response

**Task list generated successfully.**

**Structure** (5 phases, 80 tasks):

1. **Phase 1: CLI + Suite Loading** (16 tasks)
   - Project structure: 4 tasks
   - CLI argument parsing: 5 tasks
   - Suite loading & validation: 3 tasks
   - Unit tests: 1 task
   - Completion checks: 3 tasks

2. **Phase 2: Run Command** (24 tasks)
   - Model invocation: 3 tasks
   - All 8 assertions: 4 tasks
   - Fenced JSON extraction: 1 task
   - Dotted path resolution: 1 task
   - Case execution & flaky classification: 4 tasks
   - Report generation: 4 tasks
   - Unit tests: 4 tasks
   - Completion checks: 3 tasks

3. **Phase 3: Compare + Doctor** (15 tasks)
   - Comparison logic: 4 tasks
   - Doctor command: 3 tasks
   - Unit tests: 2 tasks
   - Completion checks: 6 tasks

4. **Phase 4: Prompt Improvement** (17 tasks)
   - Baseline evaluation: 3 tasks
   - 4+ iterations with compare: 12 tasks
   - Final verification: 2 tasks

5. **Phase 5: Documentation** (8 tasks)
   - USAGE.md, PROMPTS.md, README.md, JOURNAL.md: 4 tasks
   - Updates: 1 task
   - Reflection & verification: 3 tasks

**Format Compliance**:
- ✅ All tasks follow checklist format (- [ ] [ID])
- ✅ Task IDs sequential (T001–T080)
- ✅ Parallelizable tasks marked [P]
- ✅ Exact file paths included for each task
- ✅ Acceptance criteria per phase

**Parallel Opportunities**:
- Phase 1: Project structure (T002–T004), validation (T011–T012)
- Phase 2: Assertion implementations (T020a–T020h), support functions (T022–T030)
- Phase 3: Comparison (T042–T044), doctor output (T046–T047)
- Phase 4: 4 independent iterations
- Phase 5: Documentation tasks (T075–T076)

**MVP Scope**: Phases 1–3 (core harness) = ~55 tasks. All 5 phases = ~80 tasks.

---

## Outcome

- ✅ 80 granular, testable tasks covering all implementation work
- ✅ Organized by phase with clear dependencies
- ✅ Parallelization opportunities identified
- ✅ Acceptance criteria per phase
- ✅ Ready for `/sp.implement` to begin coding

**Status**: Task list complete. Ready for Phase 1 implementation.

---

## Changes Made

**Files created**:
- specs/master/tasks.md (80 tasks, 5 phases)
- history/prompts/master/005-generate-task-list.tasks.prompt.md (this PHR)

**Task Summary**:
- Total: 80 tasks
- Phase 1: 16 tasks (CLI + Suite Loading)
- Phase 2: 24 tasks (Run Command)
- Phase 3: 15 tasks (Compare + Doctor)
- Phase 4: 17 tasks (Prompt Improvement)
- Phase 5: 8 tasks (Documentation)

**Parallel opportunities**: ~30 tasks marked [P] for parallel execution within phases
