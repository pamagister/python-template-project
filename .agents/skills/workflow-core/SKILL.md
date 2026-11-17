---
name: workflow-core
description: Shared execution loop, context discipline, safety, verification, reporting and authorization rules for the task, feature and autopilot workflows. Load before implementation work.
---

# Workflow Core

This skill defines the rules shared by `workflow-task`, `workflow-feature` and `workflow-autopilot`. Mode-specific behavior lives in the mode skill; this file defines how work is executed, verified, staged, reported and escalated.

## Mode selection

The repository's `AGENTS.md` is the primary routing source. If no routing is present, use this fallback:

- **Task:** a bounded, well-specified change with clear acceptance criteria and no commit, push or issue tracking. Use `workflow-task`.
- **Feature:** one self-contained feature or bug fix that needs a short design step, GitHub issue, commit, push and CI verification. Use `workflow-feature`.
- **Autopilot:** execution of a complete plan or selected phases. Use `workflow-autopilot`.

A plan or phase request takes precedence over a single-feature request. If scope is ambiguous, choose the smaller mode and escalate when it grows. Ask only when ambiguity materially affects correctness, scope, cost, risk or an irreversible decision.

## Shared task loop

1. Inspect repository status, current branch, repository instructions, relevant implementation, tests, configuration and documentation. Preserve pre-existing user changes.
2. Understand acceptance criteria. Use the `question` tool only for material choices.
3. Implement the smallest complete change.
4. Review the diff before testing: scope, correctness, unintended changes, consistency.
5. Run relevant local checks using the project's actual commands. Inspect the project configuration instead of assuming generic targets.
6. Fix task-caused failures and repeat affected checks. Never hide, weaken or disable failing tests.
7. Review the final diff and report exactly which checks ran and their results.

## Context discipline

Context is the main cost driver. Follow these rules by default:

- Prefer `grep`, `glob` and `read` with `offset`/`limit` over full-file reads.
- For broad discovery across many files, launch the built-in `explore` subagent. Ask for a concise map: file, symbol, line range, relevance. Do not paste large file contents into the main context.
- Do not re-read a file already in context unless it changed. After an edit, read only the changed hunk.
- Bound tool output: use `pytest -q --tb=short`, `tail -n 100`, `gh run view --log-failed` instead of full logs.
- Prefer opening files by symbol or line range; avoid reading whole generated or lock files.
- Load only the skills needed for the current phase. Do not load all workflow skills at once.

## Safety

- Inspect `git status` and the current branch before changing Git state.
- Preserve unrelated and pre-existing user changes. Never use `git add .` or `git add -A`.
- Stage only files or hunks belonging to the authorized task.
- Never commit secrets, credentials, tokens or generated artifacts unrelated to the task.
- Never amend commits, rewrite history, force-push or delete branches unless explicitly authorized.
- Never commit known failing or unverified changes.
- If a blocker prevents correct completion, stop at that boundary and explain what is needed.

## Verification

- Use the project's actual commands. Inspect `Makefile`, `pyproject.toml`, `package.json`, CI configuration or equivalent files before choosing a command.
- Run relevant checks for the changed area. Run broader checks at meaningful integration boundaries.
- Distinguish local checks from remote CI. Do not claim remote CI passed when only local checks ran.
- If the project has no tests or CI, state that explicitly and do not invent verification.

## Authorization matrix

| Mode | Stage | Commit | Push | GitHub issue | Close issue |
|---|---|---|---|---|---|
| Task | Task files/hunks only | No; suggest a Conventional Commit message | No | No | No |
| Feature | Task files/hunks only | Yes; Conventional Commit with `Refs #N` | Yes; direct to default branch after local checks | Reuse accurate open issue or create one | Agent-created issue only, after CI is green |
| Autopilot | Work-package files/hunks only | Yes; Conventional Commit with all relevant phase issues | Yes; batch 3–6 commits or push at a phase boundary | One issue per phase upfront; reuse or create | Agent-created phase issue only, after CI is green |

## Reporting

Every final report should state:

- Selected mode and scope.
- Files changed and why.
- Checks run, exact commands where useful, and results.
- Issue references, commit hashes, push status and CI results when applicable.
- Blockers, assumptions and remaining work.

Use `git-workflow` for GitHub-specific commands and conventions.