# Repository Instructions

These rules apply to this Python project. Keep changes focused and follow the existing architecture.

## Python conventions

- Target Python 3.11 as declared in `pyproject.toml`.
- Follow PEP 8 and the repository's Ruff configuration: 4-space indentation, double quotes, 100-character line length.
- Use `snake_case` for packages, modules, functions and variables; `PascalCase` for classes; and `UPPER_SNAKE_CASE` for constants.
- Use `snake_case` for importable Python names. Use `kebab-case` for distribution/repository names, CLI commands and documentation paths.
- Prefer descriptive names, type hints on public function signatures, explicit imports, context managers and focused functions.
- Add or update deterministic pytest tests for behavior changes, bug fixes and important edge cases.

## Project tooling

- Use `uv` for dependency and environment management. Declare dependencies in `pyproject.toml`.
- Use Ruff for linting and formatting, and pytest for tests. Follow the existing configuration rather than introducing alternative tools.
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

Load the shared and supporting skills as needed:
- `workflow-core`: shared task loop, safety, verification, reporting and authorization rules.
- `workflow-task`: bounded implementation without commit, push or issue tracking.
- `workflow-feature`: standalone feature implementation with issue, commit, push and CI.
- `workflow-autopilot`: full-plan or selected-phase execution.
- `git-workflow`: Git, GitHub issues, `gh` CLI, commits, pushes and CI.
- `mission-planning`: turn a mission or external specification into one executable plan.
