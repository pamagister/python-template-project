---
name: workflow-autopilot
description: Autonomously execute a multi-phase implementation plan in repeated verified work-package loops, with commits, batched pushes, issue tracking and CI gates.
---

# Autopilot Workflow

Use only when the user explicitly authorizes autonomous execution of a larger plan. Load `git-workflow` as well.

## Input plan

The plan may be:
- Markdown pasted directly into the prompt, or
- Any user-specified Markdown file path (for example, `plan.md`).

Do not require a fixed filename or a separate `tasklist.md`. The plan is the single source of truth for scope, decisions, work packages, acceptance criteria and progress.

A useful plan normally contains an objective, constraints/decisions, phases, coherent work packages and verifiable acceptance criteria. If it is too vague to execute safely, clarify only the blocking decisions before starting.

## Preparation

1. Inspect repository status, branch, project instructions and the supplied plan.
2. Preserve all pre-existing user changes; identify them before implementation.
3. Identify phase dependencies, work-package boundaries and completion criteria.
4. For each phase, search open issues and reuse an accurate matching issue. If none exists, create a phase issue autonomously.
5. Never edit metadata or state of a reused issue; comments are allowed. Agent-created phase issues may receive progress updates and may be closed after the phase gate succeeds.
6. Start with the first pending, unblocked work package.

## Repeated work-package loop

For each work package:

1. Set its status to `[-]` when beginning, if the plan is a writable file.
2. Inspect relevant implementation, tests, configuration and documentation.
3. Implement the smallest complete change satisfying the acceptance criteria.
4. Review the diff before testing for scope, correctness and unintended changes.
5. Run relevant tests and non-mutating checks. Use the project's actual commands; do not assume targets exist. Run broader checks at meaningful integration boundaries.
6. Fix failures and repeat affected checks. Do not bypass failing tests.
7. Review the final diff, stage only work-package changes and create one coherent Conventional Commit referencing the phase issue.
8. Mark the work package `[x]` only after implementation is verified and committed.
9. Add a concise progress comment to the phase issue when useful. Never edit a reused issue's fields or state.

A work package may combine closely related small tasks. Avoid both giant commits and artificial micro-commits.

## Status markers

Use these markers directly in phase and work-package headings:

- `[ ]` pending
- `[-]` in progress
- `[x]` completed
- `[~]` deferred or blocked

Mark a work package `[x]` after local verification and commit. Mark a phase `[x]` only after all its work packages are complete, all intended changes are pushed, and relevant CI is green. Use `[~]` with a short explanation for blocked/deferred work; do not mark incomplete work as complete.

If the plan was pasted into the prompt rather than supplied as a writable file, maintain progress in the session and provide an updated plan/status in the final response. Do not create a second tracking file unless explicitly requested.

## Push cadence and CI gate

- Track coherent commits since the last successful push.
- Push after approximately 3–6 commits, or at phase completion if earlier. Do not exceed six commits solely to preserve a batch.
- Push only intended work; never include unrelated user changes.
- After each push, monitor the relevant GitHub Actions workflows until they reach a definitive result.
- If CI fails, inspect logs, fix the cause, run local checks, commit the correction, push and monitor again.
- Do not start dependent work or mark the phase complete until relevant CI is green.
- If two repair cycles fail to produce a clear path, or CI is non-reproducible and requires user input, stop and report the blocker.

## Phase completion

A phase is complete only when:
- Every work package and acceptance criterion is satisfied.
- Relevant local tests and checks pass.
- All phase changes are committed and pushed.
- Relevant GitHub Actions CI is green.

Then mark the phase `[x]`. Close the phase issue only if the agent created it during this run. Never close a reused issue.

## Context handoff and plan report

When context is becoming large, before handing off, or at a phase boundary:

- Ensure the current work package status is accurate.
- Update the supplied plan file with a short `## Progress / Handoff` entry at its end: completed work, current state, next work package, relevant commits/push/CI, blockers and important decisions.
- Keep the report concise and append a new dated entry rather than rewriting useful history.
- If the plan was prompt-only, provide the handoff summary in the conversation; do not invent a file path.

## Final report

Summarize completed phases/work packages, tests and checks, commits, pushes, CI results, issue references, blockers and deferred work. State explicitly if any part remains incomplete.
