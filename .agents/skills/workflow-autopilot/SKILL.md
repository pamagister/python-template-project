---
name: workflow-autopilot
description: Execute a complete plan or selected phases autonomously. Ensures one GitHub issue per phase upfront, loops the feature cycle per work package, updates plan status, pushes directly to the default branch, gates on CI and interrupts only for blockers or critical decisions. Use even for a single selected phase.
---

# Autopilot Workflow

Use this skill whenever the user asks to implement, execute or continue a plan, or selects one or more phases/work packages from a plan. This applies even when only one phase is selected. The user does not need to say "Autopilot".

Execute the authorized scope autonomously. Do not ask for permission to continue, create issues or push when this workflow authorizes it.

## Input plan

The plan may be:

- Markdown pasted directly into the prompt, or
- Any user-specified Markdown file path.

Do not require a fixed filename or a separate task list. The plan is the single source of truth for scope, decisions, acceptance criteria and progress.

A useful plan contains an objective, scope and non-goals, decisions, phases, coherent work packages, stable identifiers, acceptance criteria, dependencies and risks. If the plan is too vague to execute safely, ask only the blocking questions via the `question` tool.

If the plan was pasted into the prompt rather than supplied as a writable file, maintain progress in the session and provide an updated plan/status in the final response. Do not create a second tracking file unless explicitly requested.

## Preparation

1. Load `workflow-core`, `workflow-feature` and `git-workflow`. Load `mission-planning` only if the plan itself must be repaired or extended.
2. Inspect repository status, the current branch, repository instructions and the supplied plan. Preserve all pre-existing user changes.
3. Reconcile plan status with the actual repository: inspect implementation, tests, documentation and Git status. Status markers are progress hints, not proof that work is implemented or committed. Do not redo verified work; do not trust unchecked boxes blindly.
4. Determine the authorized scope:
   - If the user names phases or work packages, execute only those.
   - Otherwise execute the full plan, including all pending phases.
   - The plan content is binding; the order is not rigid. Dependencies and acceptance criteria remain binding.
5. Ensure one GitHub issue per phase exists before implementation:
   - Search open issues and reuse an accurate issue for a phase.
   - Create a missing phase issue autonomously. Include the phase objective, scope, acceptance criteria and plan reference.
   - Never edit the metadata or state of an issue that existed before this run. Comments are allowed.
   - Record the issue references in the plan or progress report.
   - If `gh` is unavailable or unauthenticated, continue without issue tracking and report the limitation.
   - If the plan has no explicit phases, use one issue for the whole plan.
6. Start with the first pending, unblocked work package.

## Work-package loop

For each work package:

1. Set its status to `[-]` when beginning, if the plan is a writable file.
2. Inspect the relevant implementation, tests, configuration and documentation.
3. Implement the smallest complete change satisfying the acceptance criteria.
4. Review the diff before testing for scope, correctness and unintended changes.
5. Run the relevant local checks using the project's actual commands. Fix failures and repeat the affected checks. Do not bypass or weaken failing tests.
6. Once the work package is implemented and locally verified, update its plan checkbox to `[x]` **before committing**. Include the plan update in the same commit when the plan is inside the repository.
7. Review the combined code-and-plan diff, stage only work-package changes and create one coherent Conventional Commit. Reference every phase issue the commit relates to, for example `Refs #12, #15`.
8. If the commit cannot be created, do not leave the work package marked complete: restore its status to `[-]` or `[~]` and explain the blocker.
9. Add a concise progress comment to the relevant phase issue when useful.

A work package may combine closely related small tasks. Avoid both giant commits and artificial micro-commits.

## Combining and reordering phases

- The plan content is binding, but the implementation order is not rigid.
- Phases or work packages may be combined or reordered when dependencies and acceptance criteria still hold and the change improves implementation.
- A commit that covers multiple phases must reference all relevant phase issues.
- When phases are combined, update all involved work packages and phase statuses. Mark a phase `[x]` only when its acceptance criteria are satisfied and its relevant CI is green.
- If a phase is dropped or deferred, mark it `[~]` with a short explanation. Do not mark it complete.

## Push and CI gate

- Push directly to the repository's default branch.
- If the current branch is not the default branch, do not silently switch or push. Ask the user or follow an explicit repository instruction.
- Track coherent commits since the last successful push. Push after approximately 3–6 commits, or at a logical phase boundary if earlier. Do not exceed six commits solely to preserve batching.
- Run the relevant local checks before every push. Never push known-failing changes.
- After each push, monitor the relevant CI runs until they reach a definitive result. Do not treat pending, missing or timed-out results as success.
- If CI fails, inspect the logs, reproduce the failure locally where possible, fix the cause, run the relevant checks, commit the correction, push and monitor again.
- Allow at most two repair cycles. If the failure is not clearly resolved, or CI is non-reproducible and requires user input, stop and report the blocker.
- If the repository has no CI, state that and rely on local checks.

## Status markers

Use these markers directly in phase and work-package headings:

- `[ ]` pending
- `[-]` in progress
- `[x]` completed
- `[~]` deferred or blocked

A work package may be marked `[x]` after its acceptance criteria pass local verification; commit the code and plan update together. A phase must remain `[-]` until all its selected work packages are complete, its changes are pushed and relevant CI is green. Only then mark the phase `[x]`. Use `[~]` with a short explanation for blocked or deferred work; never mark incomplete work complete.

Phase gates in the plan are verification checkpoints, not authorization stops. If a gate fails, fix the cause. Stop only if resolving it requires a critical decision.

## Autonomy and interruption

The agent is fully autonomous for the authorized plan. Interrupt the user only when:

- A blocker prevents correct completion.
- A critical decision affects scope, architecture, data safety, irreversibility, acceptance criteria, credentials or permissions.
- A CI failure cannot be resolved within the repair limit.

Routine implementation choices are made independently and reported. Do not ask for permission to continue, create phase issues, commit or push when this workflow authorizes it.

## Plan files outside the repository

Update the plan file in place if it is writable, even when it is outside the repository. Include it in a commit only when it is inside the repository. Otherwise report its path and state that it is not versioned.

## Context handoff and progress

When context is becoming large, before handing off, or at a phase boundary:

- Ensure the current work-package status is accurate.
- Append a short dated `## Progress / Handoff` entry to the plan file when it is writable. Include completed work, current state, next work package, relevant issue/commit/push/CI references, blockers and important decisions.
- Append a new entry rather than rewriting useful history.
- If the plan is prompt-only, provide the handoff summary in the conversation.

## Phase completion and issue closing

A selected phase is complete only when:

- Every selected work package and acceptance criterion is satisfied.
- Relevant local tests and checks pass.
- All phase changes, including plan status updates, are committed and pushed.
- Relevant CI is green.

Then mark the phase `[x]` and commit/push the final status update if it was not already included. Close the phase issue only when this run created it, its work is verified and relevant CI is green. Never close an issue that existed before this run.

## Final report

Summarize completed phases and work packages, tests and checks, issue references, commit hashes, push status and CI results. State explicitly what remains incomplete, deferred or blocked.