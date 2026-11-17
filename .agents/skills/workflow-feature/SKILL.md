---
name: workflow-feature
description: Implement one self-contained feature or bug fix with a short planning step, GitHub issue tracking, a Conventional Commit, a direct push to the default branch and CI verification. Use for a standalone feature or bug fix. For a bounded change without issue, push or CI, use workflow-task. For a plan or selected phase, use workflow-autopilot.
---

# Feature Workflow

Use this skill for one self-contained feature or bug fix that benefits from a short planning step, issue tracking, a commit, a push and CI verification.

## 1. Plan the feature

- Clarify goal, scope, non-goals, acceptance criteria and verification approach.
- Use `question` only for ambiguity that materially affects correctness, scope, cost, risk or an irreversible decision.
- Keep the plan lightweight: state it in the response unless the user asks for a plan file.
- If the feature is large, architectural or multi-phase, recommend `mission-planning` plus `workflow-autopilot` instead.

## 2. Track the issue

1. Load `git-workflow`.
2. Search open issues for an accurate match.
3. Reuse a suitable issue without editing its metadata or state. Comments are allowed.
4. If none exists, create one autonomously with context, expected outcome, scope and acceptance criteria.
5. If `gh` is unavailable or unauthenticated, continue without issue tracking and report the limitation.

## 3. Implement and verify

Follow `workflow-core`:

- Inspect repository and relevant code.
- Implement the smallest complete change.
- Review the diff before testing.
- Run relevant tests and non-mutating checks.
- Fix task-caused failures and repeat affected checks.
- Review the final diff.

## 4. Commit

- Stage only task-related files and hunks.
- Create a coherent Conventional Commit with the issue reference at the end of the subject line: `fix(parser): handle empty input Refs #42`.
- Use `Refs #N` by default. Use `Fixes #N` only when the commit fully resolves an issue created by this run and closing at commit time is explicitly authorized.
- Do not amend, rewrite history or force-push.

## 5. Push and watch CI

- Push directly to the repository's default branch.
- If the current branch is not the default branch, do not silently switch or push. Ask the user or follow an explicit repository instruction.
- Run relevant local checks before every push. Never push known-failing changes.
- Monitor relevant CI runs with `gh run list` and `gh run watch`.
- Do not treat pending, missing or timed-out CI as success.
- If CI fails, inspect logs, reproduce locally, fix the cause, commit, push and monitor again.
- Allow at most two repair cycles. Then stop and report the blocker.
- If the repository has no CI, state that and rely on local checks.

## 6. Finish

- Consider the feature complete only when local checks and relevant CI are green.
- If this run created the issue, close it after CI is green: `gh issue close <number> --reason completed`.
- Never close a reused issue.
- Report issue reference, commit hashes, push status, CI result and checks run.