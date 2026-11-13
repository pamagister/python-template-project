---
name: workflow-core
description: Shared execution loop, safety rules, verification expectations, reporting format and authorization matrix for the task, feature and autopilot workflow skills. Load this before any implementation work.
---

# Workflow Core

This skill contains the rules shared by `workflow-task`, `workflow-feature` and `workflow-autopilot`. Load it before any implementation work. Mode-specific behavior is defined in the mode skill; this file defines how work is executed, verified, staged, reported and escalated.

## Mode selection

The repository's `AGENTS.md` is the primary routing source. If no repository routing is present, use this fallback:

- **Task mode:** a bounded, well-specified change with clear acceptance criteria and no request for issue tracking, commit, push or CI gating. Use `workflow-task`.
- **Feature mode:** one self-contained feature or bug fix that needs a short design and acceptance-criteria step, GitHub issue tracking, a commit, a push and CI verification. Use `workflow-feature`.
- **Autopilot mode:** execution of a complete plan or selected phases, including work that is already described by a plan. Use `workflow-autopilot`.

A plan or phase request takes precedence over a single-feature request. If the scope is ambiguous, choose the smaller mode and escalate when the scope grows. Ask only when the ambiguity materially affects correctness, scope, cost, risk or an irreversible decision.

## Shared task loop

1. Inspect repository status, the current branch, repository instructions, relevant implementation, tests, configuration and documentation. Preserve pre-existing user changes.
2. Understand the acceptance criteria. Ask only when a consequential ambiguity cannot be resolved safely. Use the `question` tool for material choices.
3. Implement the smallest complete change that satisfies the request.
4. Review the diff before testing. Check scope, correctness, unintended changes and consistency with existing conventions.
5. Run the relevant tests and non-mutating checks using the project's actual configured commands. Inspect the project configuration instead of assuming a generic `make check` target exists.
6. Fix failures caused by the task and repeat the affected checks. Do not hide, weaken or disable failing tests.
7. Review the final diff and report exactly which checks were run and what their results were.

## Safety

- Inspect `git status` and the current branch before changing Git state.
- Preserve unrelated and pre-existing user changes. Never discard, overwrite or silently include them.
- Never use indiscriminate staging such as `git add .` or `git add -A`. Stage only files or hunks that belong to the authorized task.
- If a file already contains unrelated changes and safe partial staging is not practical, leave it unstaged and explain why.
- Never commit secrets, credentials, tokens or generated artifacts unrelated to the task.
- Never amend existing commits, rewrite history, force-push or delete branches unless explicitly authorized.
- Never commit known failing or unverified changes.
- If required credentials or permissions are unavailable, continue with work that does not depend on them and report the limitation.
- If a blocker makes correct completion impossible, stop at that boundary and explain what is needed.

## Verification

- Use the project's actual commands. Inspect `Makefile`, `pyproject.toml`, `package.json`, CI configuration or equivalent files before choosing a command.
- Run relevant tests and checks for the changed area. Run broader checks at meaningful integration boundaries.
- Distinguish local checks from remote CI. Do not claim that remote CI passed when only local checks ran.
- If the project has no tests or no CI, state that limitation explicitly and do not invent verification.

## Authorization matrix

| Mode | Stage | Commit | Push | GitHub issue | Close issue |
|---|---|---|---|---|---|
| Task | Only task files/hunks | No; suggest a Conventional Commit message | No | No | No |
| Feature | Only task files/hunks | Yes; Conventional Commit, `Refs #N` by default | Yes; direct to the default branch after local checks | Search and reuse an accurate open issue; otherwise create one | Agent-created issue only, after relevant CI is green; never a reused issue |
| Autopilot | Only work-package files/hunks | Yes; Conventional Commit, reference all relevant phase issues | Yes; batch approximately 3–6 commits or push at a logical boundary | Ensure one issue per phase upfront; reuse or create | Agent-created phase issue only, after its work is verified and relevant CI is green; never a reused issue |

Mode-specific details and exceptions are defined in the mode skill. This matrix is the default; a mode may add constraints but must not weaken the safety rules.

## Reporting

Every final report should state:

- The selected mode and scope.
- Files changed and the reason for each material change.
- Checks run, including the exact commands where useful, and their results.
- Issue references, commit hashes, push status and CI results when applicable.
- Blockers, assumptions and remaining work.

Use `git-workflow` for GitHub-specific commands and conventions.