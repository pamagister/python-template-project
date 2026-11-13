---
name: workflow-task
description: Execute a bounded, well-specified change such as a typo fix, small refactor, review fix or small documentation adjustment. Stage only task files, do not commit or push, and suggest a Conventional Commit message. For a standalone feature with issue, push and CI, use workflow-feature. For plan or phase execution, use workflow-autopilot.
---

# Task Workflow

Use this skill for a bounded change whose acceptance criteria are already clear. Do not use it for a standalone feature that needs design, issue tracking, push or CI, or for execution of a plan or phase. Those requests use `workflow-feature` or `workflow-autopilot`.

## Procedure

1. Load `workflow-core` and `git-workflow`.
2. Inspect repository status, the current branch, repository instructions and the relevant implementation, tests, configuration and documentation. Preserve pre-existing user changes.
3. Implement the smallest complete change.
4. Review the diff before testing.
5. Run the relevant tests and non-mutating checks using the project's actual commands.
6. Fix failures caused by the task and repeat the affected checks.
7. Review the final diff again.
8. Stage only files or hunks that belong to this task. Leave pre-existing user changes unstaged. If safe partial staging is not practical, leave the file unstaged and explain why.
9. Do not commit, push, create GitHub issues or wait for CI.

## Escalation

If the scope grows materially during implementation, stop and ask whether to switch to `workflow-feature` or `workflow-autopilot`. Do not silently turn a bounded task into an issue-tracked, pushed feature.

## Final report

Report the changed files, the checks run and their results, and any remaining limitations. When a commit would be appropriate, suggest one concise Conventional Commit message inline, for example:

```text
fix(cli): handle empty input without traceback
```

Do not create the commit unless the user asks.