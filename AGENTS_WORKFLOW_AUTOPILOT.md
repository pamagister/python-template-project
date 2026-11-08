# Autopilot Workflow – Autonomous Plan Implementation

Use this workflow when the user explicitly authorizes independent execution of
a larger plan, typically tracked in `docs/develop/initial-release/plan.md` and
`docs/develop/initial-release/tasklist.md`. Read
`AGENTS_GIT.md` as well. Work continuously within the authorized scope; do not
ask for confirmation at every implementation step.

## Project Invariants

- Make the smallest correct change and preserve the existing architecture,
  conventions, formatting, and style.
- Avoid unrelated refactors.
- Test filesystem operations and safety-critical behavior.
- Never silently overwrite or delete user data; get explicit authorization
  for potentially risky operations.
- JSON is the primary interface; Plain is the human-oriented alternative.
- Allowed Roots default to Home and CWD; other roots require `--allow-root`.
- Output defaults to `auto` (TTY → Plain, pipe → JSON).

## Phase Preparation

!!! CREATE AN ISSUE FOR THE PHASE IF NONE EXISTS. Search open issues first and reuse one only if it accurately represents the phase; otherwise create a phase issue with `gh issue create`. Issue creation for phases is authorized in this mode. 
Do not create separate issues for individual tasks or work packages.

1. Read `AGENTS.md`, this file, `AGENTS_GIT.md`,
   `docs/develop/initial-release/plan.md`, and
   `docs/develop/initial-release/tasklist.md`.
2. Inspect repository status and existing changes; preserve unrelated user work.
3. Identify the current phase, its tasks, acceptance criteria, and manageable
   work packages.
4. Ensure there is one GitHub issue for the phase. Search open issues first
   and reuse one only if it accurately represents the phase; otherwise create
   a phase issue with `gh issue create`. Issue creation for phases is
   authorized in this mode. Do not create separate issues for individual
   tasks or work packages.

## Per-Task Loop

For each open task in the current phase, in tasklist order:

1. Select a manageable task and inspect its relevant code, tests,
   configuration, documentation, and plan sections.
2. Implement the smallest change that satisfies its acceptance criteria.
3. Run `make check` or the narrowest relevant tests and checks; fix failures.
4. Inspect the complete task diff.
5. Update `docs/develop/initial-release/tasklist.md`: mark only completed work,
   record a Work Log entry, and note blockers or deferred work.
6. Stage only files belonging to this task and create one Conventional Commit
   for the validated task. Reference the phase issue with `Refs #N`. Do not
   use a closing keyword in task commits or close the phase issue while other
   phase work or CI remains.

Each commit must represent a coherent, successfully validated change. Never
commit known failing or unvalidated work.

## Push Cadence and CI

- Track successful local commits since the last successful push.
- Push after 3–6 commits, or at phase completion if that comes first.
- Push only intended work; never include unrelated user changes.
- After each push, identify and monitor the relevant GitHub Actions runs with
  `gh` until they reach a definitive result.
- Do not treat timeouts or missing results as success. If CI fails, inspect
  logs, fix the failure, run local checks, commit the correction, push, and
  monitor CI again.
- Do not proceed with dependent phase work until relevant CI is green.

## Phase Gate and Issue Updates

Keep `docs/develop/initial-release/tasklist.md` and the phase issue synchronized
as work progresses. Record meaningful implementation results and related commits
in the issue.

A phase is complete only when:

- All its tasks are complete and its milestone in
  `docs/develop/initial-release/plan.md` is reached.
- Local `make check` and relevant pre-commit checks pass.
- All intended changes are committed and pushed.
- Relevant GitHub Actions CI has completed successfully.

Close the phase issue explicitly with `gh issue close` only after every
phase-gate condition is satisfied.

## Completion

After all planned phases:

1. Run the complete test suite and all configured pre-commit checks.
2. Ensure intended changes are committed and pushed.
3. Verify successful CI and close only fully completed phase issues.
4. Update `docs/develop/initial-release/tasklist.md` and provide a final report
   covering implementation, checks, commits, push and CI status, issue status,
   and outstanding work.

## Stop Conditions and Safety

Stop and ask before proceeding if a decision is destructive or irreversible,
the public interface or CLI contract is unclear, required credentials are
missing, CI repeatedly fails without a locally reproducible cause, or work
would extend outside the authorized repository/scope.

Never bypass failing checks, silently discard user changes, stage unrelated
files, or push incomplete work. Keep task tracking, plan status, and issue
status consistent.

## Context Handoff

At the end of each phase or when context becomes large, update the tasklist
Work Log with a summary, open questions, the next task, and relevant CI notes
so another session can continue safely.
