---
name: workflow-feature
description: Implement one self-contained feature or bug fix with a short planning step, GitHub issue tracking, a Conventional Commit, a direct push to the default branch and CI verification. Use for a standalone feature or bug fix. For a bounded change without issue, push or CI, use workflow-task. For a plan or selected phase, use workflow-autopilot.
---

# Feature Workflow

Use this skill for one self-contained feature or bug fix that benefits from a short planning step, issue tracking, a commit, a push and CI verification. Do not use it for a bounded change without those needs (`workflow-task`) or for execution of a plan or phase (`workflow-autopilot`).

## 1. Plan the feature

- Clarify the goal, scope, non-goals, acceptance criteria and verification approach.
- Use the `question` tool only for ambiguity that materially affects correctness, scope, cost, risk or an irreversible decision. Do not ask for permission to create an issue or push when this workflow authorizes it.
- Keep the plan lightweight: state it in the response unless the user asks for a plan file.
- If the feature is large, architectural or naturally multi-phase, stop and recommend `mission-planning` plus `workflow-autopilot` instead of inventing a large plan here.

## 2. Track the issue

1. Load `git-workflow`.
2. Search open issues for an accurate match.
3. If a suitable issue exists, reuse it. Do not edit its title, body, labels, assignees, milestone or state. Comments are allowed when useful.
4. If no suitable issue exists, create one autonomously. Include context, expected outcome, scope and acceptance criteria. Do not ask merely for permission to create it.
5. If `gh` is unavailable or unauthenticated, or the user explicitly forbids issue tracking, continue without an issue and report the limitation.

## 3. Implement and verify

Follow the shared task loop in `workflow-core`:

- Inspect the repository and relevant code.
- Implement the smallest complete change.
- Review the diff before testing.
- Run relevant tests and non-mutating checks.
- Fix task-caused failures and repeat the affected checks.
- Review the final diff.

## 4. Commit

- Stage only task-related files and hunks.
- Create a coherent Conventional Commit. Use `Refs #N` by default.
- Use `Fixes #N` only when the commit itself fully resolves the issue, the issue was created by this run, and closing it at commit time is explicitly authorized. Prefer `Refs #N` plus an explicit close after CI.
- Do not amend, rewrite history or force-push.

## 5. Push and watch CI

- Push directly to the repository's default branch.
- If the current branch is not the default branch, do not silently switch or push. Ask the user or follow an explicit repository instruction.
- Run the relevant local checks before every push. Never push known-failing changes.
- Monitor the relevant CI runs, for example with `gh run list` and `gh run watch`.
- Do not treat pending, missing or timed-out CI as success.
- If CI fails, inspect the logs, reproduce the failure locally where possible, fix the cause, run the relevant checks, commit the correction, push and monitor again.
- Allow at most two repair cycles. If the failure is not clearly resolved, stop and report the blocker.
- If the repository has no CI, state that and rely on local checks.

## 6. Finish

- Consider the feature complete only when local checks and relevant CI are green.
- If this run created the issue, close it explicitly after CI is green, for example `gh issue close <number> --reason completed`.
- Never close an issue that existed before this run.
- Report the issue reference, commit hashes, push status, CI result and checks run.