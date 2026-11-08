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

## Generated documentation

- `docs/index.md` is the source for `README.md`. Never edit `README.md` directly.
- After changing `docs/index.md`, run `make syncdocs` when appropriate.
- Check existing generation scripts before editing generated files.

## Agent workflows

Load the relevant skill only when needed:
- `workflow-standard`: bounded task mode, including small tasks and single-feature implementation.
- `workflow-autopilot`: explicitly authorized multi-work-package plan execution.
- `git-workflow`: Git, GitHub issues, commits, pushes and CI.
- `mission-planning`: turn a mission or external specification into one executable plan.

The standard workflow is the default. Do not load the autopilot workflow unless the user explicitly requests autonomous execution of a larger plan.
