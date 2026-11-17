# Repository Instructions

## Core Principles

- **Think before coding.** Identify the goal, assumptions, constraints, and success criteria before implementation. If ambiguity materially affects the solution, ask before proceeding. Point out simpler alternatives and relevant trade-offs.
- **Simplicity first.** Implement the simplest solution that fully meets the requirements. Avoid speculative features, unnecessary abstractions, premature optimization, and unrequested configurability.
- **Surgical changes.** Modify only what the task requires. Preserve existing conventions and avoid unrelated refactoring. Remove only dead code made obsolete by your changes; report unrelated issues without fixing them.
- **Correctness over cleverness.** Prioritize clarity, maintainability, reliability, and measurable performance. Optimize algorithms, memory usage, and runtime where justified by actual requirements. Use vectorization or parallelization when beneficial.

## Workflow

1. **Inspect** the relevant code, project structure, configuration, dependencies, and existing tests before making changes.
2. **Plan** briefly for nontrivial tasks. Define concrete, verifiable success criteria.
3. **Implement** the smallest complete solution, following existing project conventions.
4. **Verify** changes with relevant tests, formatting, linting, and type checking. Fix issues introduced by the changes.
5. **Report** what changed, which checks passed, and any remaining limitations.

Do not claim that checks passed unless they were actually executed. If verification is impossible, explain why.

## Python Code Quality

- Follow PEP 8 and the existing project style. Use 4 spaces for indentation and keep lines within 100 characters where practical.
- Use descriptive names, `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_CASE` for constants.
- Add type hints to all function signatures. Avoid `Any` unless genuinely necessary.
- Write docstrings for public functions, classes, and methods. Document parameters, return values, and raised exceptions where relevant.
- Prefer small, focused functions and classes with clear responsibilities. Limit function parameters to five where practical; use early returns to reduce nesting.
- Never use mutable default arguments. Use `is` for comparisons with `None`, `True`, and `False`.
- Prefer f-strings, context managers, and explicit imports. Avoid wildcard imports and redundant comments.
- Handle errors explicitly. Catch specific exceptions, provide meaningful context, and never silently suppress unexpected failures.
- Use dataclasses for simple data containers and composition over inheritance where appropriate.
- Never use emoji or emoji-like Unicode characters in code, comments, or documentation unless explicitly required for tests or functionality.

## Dependencies and Tooling

- Use `uv` for dependency management and virtual environments when available or when initializing a project.
- Declare and manage dependencies in `pyproject.toml`. Avoid unnecessary dependencies and preserve existing project tooling.
- Prefer established project commands and configuration over introducing new tools or conventions.
- Use `ruff` for formatting and linting and `mypy` for static type checking when configured or appropriate.
- Use `pytest` for tests. Add or update tests for new behavior, bug fixes, and meaningful edge cases. Mock external dependencies where appropriate.
- Never introduce tooling or dependencies solely for marginal benefits.

## Project tooling

- Inspect the Makefile before using a target. Relevant targets:
  - `make lint`: Ruff lint and format checks.
  - `make test`: lint plus the test suite and coverage reports.
  - `make fmt`: mutating formatting/fix operations and documentation synchronization.
  - `make precommit`: runs formatting, tests and dependency checks; it is mutating and may install a tool.
- Do not run mutating convenience targets merely as a substitute for understanding what they do.

## GitHub CLI

GitHub CLI (`gh`) is available for repository management and GitHub operations.

Useful commands:

```bash
gh --help
gh issue list
gh issue create --label bug
```

Prefer `gh` for GitHub issues, pull requests, and repository operations when appropriate. Check command help before using unfamiliar options. For workflow conventions around issues, commits, pushes and CI, load `git-workflow`.

## Generated documentation

- `docs/index.md` is the source for `README.md`. Never edit `README.md` directly.
- After changing `docs/index.md`, run `make syncdocs` when appropriate.
- Check existing generation scripts before editing generated files.

## Agent workflow routing

Choose the workflow from the user's requested scope, not from whether they know or use the internal mode name.

- **Task mode:** A bounded change such as a review, typo fix, small refactor or small documentation adjustment. Load `workflow-task`.
- **Feature mode:** One self-contained feature or bug fix that needs a short design step, issue tracking, a commit, a push and CI verification. Load `workflow-feature`.
- **Autopilot:** Whenever the user asks to implement, execute or continue a plan, or names one or more phases/work packages from a plan. This includes a single selected phase. Phrases such as "implement the first phase", "execute phase 2", "continue plan.md" or "implement autonomously" are sufficient; the user does not need to say "Autopilot". Load `workflow-autopilot`. By default it executes the full plan; if the user names phases or work packages, it executes only those.

A plan or phase request always takes precedence over the single-feature workflow, even when the selected phase is the only requested scope.

Load only the skills needed for the current phase:
- `workflow-core`: shared task loop, context discipline, safety, verification, reporting and authorization rules.
- `workflow-task`: bounded implementation without commit, push or issue tracking.
- `workflow-feature`: standalone feature implementation with issue, commit, push and CI.
- `workflow-autopilot`: full-plan or selected-phase execution, including fresh-session handoff.
- `git-workflow`: Git, GitHub issues, `gh` CLI, commits, pushes and CI.
- `mission-planning`: turn a mission or external specification into one executable plan with a durable handoff block.
