# AGENTS_WORKFLOW.md

## Purpose

Define how implementation agents execute tasks, validate changes and interact with Git.

Two operating modes are supported.

---

## 1. Standard Mode – One-Shot Implementation

Use this mode for individual implementation tasks, bug fixes, refactoring and documentation changes.

### Workflow

1. Understand the task and inspect the relevant code.
2. Implement the requested changes.
3. Run relevant tests.
4. Run the project's pre-commit checks.
5. Run `make precommit` if available, otherwise `pre-commit run --all-files`
6. Fix all relevant failures.
7. Inspect the final diff.
8. Stage newly created files using explicit `git add <file>` commands.
9. Do not create a commit automatically.
10. If new files were created, propose a suitable Conventional Commit message.

### Important Rules

- Do not stage unrelated user changes or temporary files.
- Do not stage all modified files indiscriminately.
- Do not commit unless explicitly requested.
- Existing modified files remain unstaged unless staging is explicitly requested.
- Report tests and checks performed.
- Clearly identify any remaining failures.

### Expected Result

A completed implementation with passing checks, relevant new files staged and a suggested commit message where applicable.

No automatic commit or push.

---

## 2. AUTO Mode – Autonomous Plan Implementation

Use this mode when the agent is explicitly instructed to implement a larger plan independently, typically based on `plan.md` and `tasklist.md`.

The agent is responsible for implementation progress, validation, commits, GitHub synchronization and github issue updates where applicable.

### Phase A – Preparation

1. Read `AGENTS.md`.
2. Read `AGENTS_WORKFLOW.md` and `AGENTS_GIT.md`.
3. Inspect repository status and existing changes.
4. Read `plan.md` and `tasklist.md`.
5. Identify implementation phases and manageable work packages.
6. Check existing GitHub issues.
7. Create a GitHub issue only if requested by the user and no suitable open issue exists.
8. Create or identify one github issue ticket per implementation phase/work package if required.

### Phase B – Implementation

For each work package:

1. Select a manageable implementation task.
2. Implement the changes.
3. Run relevant tests.
4. Run pre-commit checks.
5. Run `make precommit` or the configured dry-run equivalent.
6. Inspect the complete diff.
7. Update `tasklist.md`.
8. Stage only relevant files.
9. Create a Conventional Commit.
10. Reference the relevant GitHub issue in the commit message where applicable.

Each commit must represent a coherent, successfully validated change.

Never commit known failing or unvalidated changes merely to reach the push threshold.

### Phase C – Push Cadence

Maintain a counter of successful local commits since the last successful push.

- Push after approximately four successful commits.
- The normal target is four commits; a range of three to five is acceptable when work-package boundaries justify it.
- Do not push incomplete or failing work.
- Do not push unrelated user changes.
- Reset the counter after a successful push.

Do not wait unnecessarily for an exact commit count if a meaningful implementation boundary or operational requirement justifies an earlier push.

### Phase D – GitHub Actions Monitoring

After each push:

1. Identify the relevant GitHub Actions workflow runs.
2. Monitor CI until the relevant workflows finish.
3. Require a successful result before proceeding with dependent work.
4. If CI fails, inspect logs, fix the issue, run local checks and commit the correction.
5. Push the correction according to the established workflow.

#### Polling and Timeout

- Default polling interval: 60 seconds.
- Adjust polling dynamically according to observed workflow duration and progress.
- Prefer waiting for actual workflow completion over repeatedly issuing short status checks.
- Increase the waiting interval for long-running workflows.
- Reduce it when a workflow is expected to finish soon.
- Do not interpret a timeout or missing result as success.
- Continue monitoring until a definitive result is available.

### Phase E – github issue Updates

For each implementation phase:

1. Update the corresponding github issue ticket as work progresses.
2. Record relevant implementation results.
3. Reference associated commits or GitHub issues where appropriate.
4. Close the github issue ticket only when:
   - All tasks belonging to the phase are implemented.
   - Relevant tests and pre-commit checks pass.
   - Changes have been pushed.
   - Relevant GitHub Actions CI has completed successfully.

Never close a ticket prematurely.

### Phase F – Progress Tracking

After completing work packages:

- Update `tasklist.md`.
- Mark only genuinely completed tasks.
- Record deferred tasks and blockers.
- Keep the plan and implementation status consistent.
- Maintain a clear relationship between tasks, commits, github issues.

### Phase G – Completion

After all planned implementation work:

1. Run the complete test suite.
2. Run all pre-commit checks.
3. Ensure all intended changes are committed.
4. Push outstanding commits.
5. Verify successful GitHub Actions CI.
6. Close completed github issue phase tickets.
7. Update `tasklist.md`.
8. Provide a final implementation report.

The report must include:

- Implemented functionality.
- Tests and checks performed.
- Commit references.
- Push and CI status.
- GitHub issue references, if applicable.
- github issue status, if applicable.
- Outstanding tasks and known limitations.

---

## General AUTO Mode Rules

- Work independently within the explicitly authorized scope.
- Do not ask for confirmation for every individual implementation step.
- Ask before performing actions outside the authorized scope.
- Never bypass failing tests or CI to make progress appear successful.
- Never silently discard user changes.
- Prefer small, coherent commits.
- Keep documentation and task tracking synchronized.

**Guiding principle: Implement continuously, validate locally, commit coherently, push in batches and verify remotely.**