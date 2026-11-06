# AGENTS.md

## Python

- Follow PEP 8 and the project's formatter and configuration.
- Use descriptive names, type-hint function signatures, and document public APIs. Avoid `Any`
  unless necessary.
- Keep functions focused; use dataclasses for simple data containers when appropriate. Avoid
  mutable defaults, and use `is` for `None`, `True`, and `False`.
- Prefer explicit imports, f-strings, and context managers.
- Avoid wildcard imports and redundant comments.


## Workflow

1. **Inspect** the relevant code, project structure, configuration, dependencies, and existing tests before making changes.
2. **Plan** briefly for nontrivial tasks. Define concrete, verifiable success criteria.
3. **Implement** the smallest complete solution, following existing project conventions.
4. **Verify** changes with relevant tests, formatting, linting, and type checking. Fix issues introduced by the changes.
5. **Report** what changed, which checks passed, and any remaining limitations.

Do not claim that checks passed unless they were actually executed. If verification is impossible, explain why.

## Tests

- Add or update "Tests with Teeth" for behavior changes and important edge/failure cases. Keep tests
  deterministic, mock only when needed, and never weaken tests to pass.
- Run relevant configured checks and report what actually ran; do not claim unrun checks passed.

## Dependencies and Tooling

- Use `uv` for dependency management and virtual environments when available or when initializing a project.
- Declare and manage dependencies in `pyproject.toml`. Avoid unnecessary dependencies and preserve existing project tooling.
- Prefer established project commands and configuration over introducing new tools or conventions.
- Use `ruff` for formatting and linting and `mypy` for static type checking when configured or appropriate.
- Use `pytest` for tests. Add or update tests for new behavior, bug fixes, and meaningful edge cases. Mock external dependencies where appropriate.
- Never introduce tooling or dependencies solely for marginal benefits.

## Project workflows and generated files

- Use existing Makefile targets when relevant; common checks are 

```bash
make fmt
make lint
make test
```

Check the Makefile and project configuration rather than assuming a command exists.
- `make syncdocs` runs `scripts/generate_config_docs.py`, `scripts/update_readme.py`, and
  `.github/update_funding.py`. It regenerates `config.yaml`, `docs/usage/config.md`,
  `docs/usage/cli.md`, `README.md`, and `docs/funding/funding.md`. Do not edit these outputs
  directly: update the relevant `ConfigCategory` definitions used by `ConfigManager` or
  `docs/index.md`, then run `make syncdocs`.


## github

- use github cli to interact with github, see https://cli.github.com/manual/gh
- if requested, use `gh issue list` to view a number of issues (--limit <int>) or filter JSON output using a jq expression (--jq <expression>) to view existing issues
- Create issues via the GitHub web UI or `gh issue create`; templates are located in `.github/ISSUE_TEMPLATE/`.
- to view details of an issue use `gh issue view {<number> | <url>} [flags]`
- to append a comment to an issue use `gh issue comment {<number> | <url>} [flags]`
- Check the status of an Actions pipeline using `gh run list` and `gh run view <run-id>`.
- use this commit message format: (where type may be one of `feat` `fix` `docs` `refactor` `test` `ci` `revert`)
  ```
  <type>[optional scope]: <description>
  
  [optional body]
  
  [optional footer(s), e.g. `#<number>` for a github issue or `Fixes #` if the issue is completed on this commit]
  ```
