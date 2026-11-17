---
name: git-workflow
description: Repository Git and GitHub conventions for GitHub CLI (`gh`), issue lookup and creation, safe staging, Conventional Commits, direct default-branch pushes, CI monitoring and reporting.
---

# Git and GitHub Workflow

Use this skill whenever a task involves GitHub issues, staging, commits, branches, pushes or CI. Write issues in English.

## Safety

- Inspect `git status` and the current branch before changing Git state.
- Preserve unrelated and pre-existing user changes. Never use indiscriminate staging.
- Stage only changes belonging to the authorized task or work package.
- Never amend commits, rewrite history, force-push or delete branches unless explicitly authorized.
- Never commit secrets, credentials, tokens or temporary/generated artifacts unrelated to the task.

## GitHub CLI (`gh`)

`gh` is the preferred interface for GitHub issues, pull requests, runs and repository operations.

- Check `gh --help` and subcommand help before using unfamiliar options.
- Use `gh issue list`, `gh issue view`, `gh issue create`, `gh issue comment` and `gh issue close` for issue work.
- Use `gh run list` and `gh run watch` to find and monitor CI runs for a pushed commit.
- If `gh` is unavailable or unauthenticated, continue without GitHub operations and report the limitation. Never fabricate issue numbers, CI results or repository state.

## Issues

- Search open issues before creating one. Reuse an issue only when it accurately represents the requested feature or Autopilot phase.
- If no suitable issue exists in Feature mode, create one autonomously.
- In Autopilot, ensure one issue per phase exists before implementation. Reuse an accurate open issue or create a missing phase issue autonomously.
- Keep issue titles concise and bodies actionable: context, expected outcome, scope and acceptance criteria.
- Apply existing labels only when they clearly fit. Do not invent a new taxonomy.
- Never edit an issue that existed before this task. Comments are allowed.
- Close an agent-created issue only after its work is verified and relevant CI is green. Prefer `gh issue close <number> --reason completed`.
- Never close a reused issue. If an issue is deferred, leave it open or close it as not planned with a comment.

## Commits

Use Conventional Commits with the issue reference at the end of the subject line:

```text
<type>(<scope>): <imperative description> Refs #<issue-number>

<optional body>
```

Example: `fix(parser): handle empty input Refs #42`

Use `Fixes #N` only when the commit itself fully resolves an issue created by this run and closing at commit time is explicitly authorized. Otherwise use `Refs #N`.

When a commit covers multiple phases or issues, list all references at the end of the subject line: `<type>(<scope>): <description> Refs #12, #15`.

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`.

Keep each commit coherent, verified and focused. Do not bundle unrelated work.

## Push and CI

- Push only when the selected workflow authorizes it.
- Feature and Autopilot push directly to the repository's default branch. If the current branch is not the default branch, do not silently switch or push; ask the user or follow an explicit repository instruction.
- In Autopilot, batch approximately 3–6 coherent commits; push earlier at a logical phase boundary, and never exceed six commits solely to preserve batching.
- Run relevant local checks before every push. Never push known-failing changes.
- After each push, identify the relevant CI runs for the pushed commit and wait for a definitive result. Do not treat pending, missing or timed-out results as success.
- If CI fails, inspect logs, reproduce locally, fix the cause, commit the correction, push and verify CI again.
- Allow at most two repair cycles. If the failure is not clearly resolved, stop and report the blocker.
- Do not continue dependent work until relevant CI is green.
- If the repository has no CI, state that and rely on local checks.

## Reporting

Report issue numbers, commit hashes, push status and actual CI results. Clearly distinguish local checks from remote CI. Mention when no CI is configured.