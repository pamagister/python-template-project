---
name: workflow-autopilot
description: Execute a complete plan or selected phases autonomously. Ensures one GitHub issue per phase, loops the feature cycle per work package, pushes in batches, gates on CI, updates the plan handoff block, and starts a fresh session at phase boundaries when context is large. Use even for a single selected phase.
---

# Autopilot Workflow

Use this skill whenever the user asks to implement, execute or continue a plan, or selects one or more phases/work packages. The user does not need to say "Autopilot".

Execute the authorized scope autonomously. Do not ask for permission to continue, create issues or push when this workflow authorizes it.

## Input plan

The plan may be Markdown pasted into the prompt or any user-specified Markdown file path.

- Do not require a fixed filename or separate task list.
- The plan is the single source of truth for scope, decisions, acceptance criteria and progress.
- If the plan is too vague to execute safely, ask only blocking questions via `question`.

## Preparation

1. Load `workflow-core` and `git-workflow`. Load `workflow-feature` only for the per-work-package feature cycle. Load `mission-planning` only if the plan must be repaired or extended.
2. Inspect repository status, current branch, repository instructions and the supplied plan. Preserve pre-existing user changes.
3. Reconcile plan status with the repository: inspect implementation, tests, docs and Git status. Status markers are hints, not proof.
4. Determine authorized scope:
   - If the user names phases or work packages, execute only those.
   - Otherwise execute the full plan, including all pending phases.
   - Plan content is binding; order is flexible. Dependencies and acceptance criteria remain binding.
5. Ensure one GitHub issue per phase exists before implementation:
   - Search open issues and reuse an accurate issue for a phase.
   - Create a missing phase issue autonomously with objective, scope and acceptance criteria.
   - Never edit pre-existing issue metadata or state. Comments are allowed.
   - If `gh` is unavailable or unauthenticated, continue without issue tracking and report the limitation.
   - If the plan has no explicit phases, use one issue for the whole plan.
6. Start with the first pending, unblocked work package.

## Work-package loop

For each work package:

1. Set its status to `[-]` when beginning, if the plan is a writable file.
2. Inspect the relevant implementation, tests, configuration and documentation. Use `explore` for broad discovery; follow `workflow-core` context discipline.
3. Implement the smallest complete change satisfying acceptance criteria.
4. Review the diff before testing.
5. Run relevant local checks. Fix failures and repeat affected checks. Do not bypass or weaken tests.
6. Update the work-package checkbox to `[x]` **before committing**, if the plan is a writable file.
7. Review the combined code-and-plan diff, stage only work-package changes and create one coherent Conventional Commit. Put every related phase issue at the end of the subject line, for example `fix(parser): handle empty input Refs #12, #15`.
8. If the commit cannot be created, restore the work package to `[-]` or `[~]` and explain the blocker.
9. Add a concise progress comment to the relevant phase issue when useful.

A work package may combine closely related small tasks. Avoid giant commits and artificial micro-commits.

## Phase completion

A phase is complete only when:

- Every selected work package and acceptance criterion is satisfied.
- Relevant local tests and checks pass.
- All phase changes, including plan status updates, are committed and pushed.
- Relevant CI is green.

Then mark the phase `[x]` and update the handoff block. Close the phase issue only if this run created it and CI is green. Never close a pre-existing issue.

## Push and CI gate

- Push directly to the repository's default branch.
- If the current branch is not the default branch, do not silently switch or push. Ask the user or follow an explicit repository instruction.
- Track coherent commits since the last successful push. Push after approximately 3–6 commits or at a logical phase boundary. Do not exceed six commits solely to preserve batching.
- Run relevant local checks before every push. Never push known-failing changes.
- After each push, monitor relevant CI until a definitive result. Do not treat pending, missing or timed-out results as success.
- If CI fails, inspect logs, reproduce locally, fix the cause, run checks, commit, push and monitor again.
- Allow at most two repair cycles. If unresolved, stop and report the blocker.
- If the repository has no CI, state that and rely on local checks.

## Context handoff and session boundaries

Update the plan's `## Progress / Handoff` block at each phase boundary and whenever context becomes large.

Start a fresh session when any of these is true:

- Context reaches roughly 60–70% of the model's usable window.
- About 120–150 assistant requests have run in the current session.
- A phase boundary is reached and the next phase is large or independent.
- The handoff block says `needs-fresh-session`.

Fresh-session procedure:

1. Ensure the handoff block contains: completed work, active work, next work, relevant files with line ranges, decisions, blockers, last verification and context status.
2. Start a new session with the current model and build agent, for example:

   ```bash
   opencode run --agent build --session autopilot-<plan-slug>-<phase> \
     "Continue the plan at <path>. Read the Progress / Handoff block first, then resume at <next>."
   ```

3. Do not paste the full prior transcript. The handoff block is the contract.

Use compaction only when the current task thread is important and exact recent details do not fit the handoff block:

```bash
opencode api post /api/session/$OPENCODE_SESSION_ID/compact --data '{}'
```

Compaction is lossy. Prefer a fresh session with a precise handoff over reflex compaction.

## Combining and reordering phases

- Plan content is binding; implementation order is flexible.
- Phases or work packages may be combined or reordered when dependencies and acceptance criteria hold.
- A commit covering multiple phases must reference all relevant phase issues.
- Update all involved work packages and phase statuses when combining.
- If a phase is dropped or deferred, mark it `[~]` with a short explanation. Never mark incomplete work complete.

## Autonomy and interruption

Interrupt the user only when:

- A blocker prevents correct completion.
- A critical decision affects scope, architecture, data safety, irreversibility, acceptance criteria, credentials or permissions.
- A CI failure cannot be resolved within the repair limit.

Routine implementation choices are made independently and reported. Do not ask for permission to continue, create phase issues, commit or push when this workflow authorizes it.

## Plan files outside the repository

Update the plan file in place if writable, even when outside the repository. Include it in a commit only when inside the repository. Otherwise report its path and state that it is not versioned.

## Final report

Summarize completed phases and work packages, tests and checks, issue references, commit hashes, push status and CI results. State explicitly what remains incomplete, deferred or blocked.