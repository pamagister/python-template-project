# Standard Workflow – One-Shot Tasks

Use this workflow for bounded tasks such as an individual feature, bug fix,
refactor, or documentation change. It is the default mode unless the user
explicitly asks for autonomous execution of a larger plan.

## Workflow

1. Inspect the relevant code, tests, configuration, documentation, and working
   tree. Read any task-specific instructions.
2. Implement the smallest complete change within the requested scope.
3. Run relevant tests and checks. Prefer `make check` or the narrowest
   appropriate project command.
4. Run `make precommit` if available; otherwise run
   `pre-commit run --all-files` when pre-commit is configured.
5. Fix relevant failures and inspect the final diff.
6. Stage only newly created files belonging to this task. Leave existing
   modified files unstaged unless staging was explicitly requested. Never
   stage unrelated user changes.
7. Do not create a commit or push automatically. If new files were created,
   suggest a suitable Conventional Commit message.
8. Report the changes, checks actually run, and any remaining failures or
   limitations.

## GitHub Issues

Do not create or update GitHub issues in standard mode unless the user
explicitly requests it. Follow `AGENTS_GIT.md` for any authorized GitHub
interaction.

## Safety

- Never silently discard or overwrite user changes.
- Do not commit unless explicitly requested.
- Do not claim checks passed unless they were run.
