---
name: git-workflow
description: Repository Git and GitHub conventions for GitHub CLI (`gh`), issue lookup and creation, safe staging, Conventional Commits, direct default-branch pushes, CI monitoring and reporting.
---

# Git and GitHub Workflow

Use this skill whenever a task involves GitHub issues, staging, commits, branches, pushes or CI.
Write issues in English.

## Safety

- Inspect `git status` and the current branch before changing Git state.
- Preserve unrelated and pre-existing user changes. Never use indiscriminate staging.
- Stage only changes belonging to the authorized task or work package.
- Never amend existing commits, rewrite history, force-push or delete branches unless explicitly authorized.
- Never commit secrets, credentials, tokens or temporary/generated artifacts unrelated to the task.

## GitHub CLI (`gh`)

`gh` is the preferred interface for GitHub issues, pull requests, runs and repository operations.

- Check `gh --help` and the relevant subcommand help before using unfamiliar options. Do not guess flags.
- Use `gh issue list`, `gh issue view`, `gh issue create`, `gh issue comment` and `gh issue close` for issue work.
- Use `gh run list` and `gh run watch` to find and monitor CI runs for a pushed commit.
- If `gh` is unavailable or unauthenticated, continue with work that does not depend on GitHub, and report the limitation. Do not fabricate issue numbers, CI results or repository state.

## Issues

- Search open issues in the target repository before creating one. Reuse an issue only when it accurately represents the requested feature or Autopilot phase.
- If no suitable issue exists in Feature mode, create one autonomously; do not interrupt the user just to ask permission.
- In Autopilot, ensure one issue per phase exists before implementation. Reuse an accurate open issue or create a missing phase issue autonomously. If the plan has no explicit phases, use one issue for the whole plan.
- Keep new issue titles concise and bodies actionable: context, expected outcome, scope and acceptance criteria.
- Apply existing repository labels only when they clearly fit. Do not invent a new label taxonomy.
- **Never edit an issue that already existed before this task**: do not change its title, body, labels, assignees, milestone or state. Adding comments is allowed.
- For an issue created by the agent during this task, comments and appropriate progress updates are allowed.
- Close an agent-created issue only after its work is verified and relevant CI is green. Prefer an explicit `gh issue close <number> --reason completed` after CI, because commit keywords may close an issue at a different time or not at all depending on the push/merge model.
- Never close a reused issue. A commit alone is not grounds to close an issue.
- If an issue is deferred or its phase is dropped, leave it open or close it as not planned with an explanatory comment; do not close it as completed.

## Commits

Use Conventional Commits:

```text
<type>(<scope>): <imperative description>

<optional body>

Refs #<issue-number>
```

Use `Fixes #N` only when the commit itself fully resolves the issue, the issue was created by this run and closing it at commit time is explicitly authorized. Otherwise use `Refs #N`.

When a commit covers multiple phases or issues, reference all of them, for example `Refs #12, #15`.

Common types:

- `feat`: functionality
- `fix`: bug fix
- `refactor`: restructuring without behavior change
- `test`: tests
- `docs`: documentation
- `build`: build system or dependencies
- `ci`: CI configuration
- `chore`: maintenance

Keep each commit coherent, verified and focused. Do not bundle unrelated work.

## Push and CI

- Push only when the selected workflow authorizes it.
- Feature and Autopilot push directly to the repository's default branch. If the current branch is not the default branch, do not silently switch or push; ask the user or follow an explicit repository instruction.
- In Autopilot, batch approximately 3–6 coherent commits; push earlier at a logical phase boundary, and never exceed six commits just to preserve batching.
- Run the relevant local checks before every push. Never push known-failing changes.
- After each push, identify the relevant CI runs for the pushed commit and wait for a definitive result. Do not treat pending, missing or timed-out results as success.
- If CI fails, inspect logs, reproduce locally where possible, fix the cause, run the relevant checks, commit the correction, push and verify CI again.
- Allow at most two repair cycles. If the failure is not clearly resolved, stop and report the blocker rather than looping indefinitely.
- Do not continue with dependent work until relevant CI is green.
- If the repository has no CI, state that and rely on local checks.

## Reporting

Report issue numbers, commit hashes, push status and actual CI results. Clearly distinguish local checks from remote CI. Mention when no CI is configured.