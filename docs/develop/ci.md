# CI/CD Pipelines

This page explains how the GitHub Actions workflows work. The project is
Linux-only: there are no Windows or macOS jobs.

| Goal                    | Command / action                          |
| ----------------------- | ----------------------------------------- |
| CI (Linux)              | Push to `main` or open a pull request     |
| Manual CI run           | `gh workflow run main.yml --ref main`     |
| Create a release        | `make release`                            |
| Re-run a release        | `gh workflow run release.yml --ref <tag>` |

## Continuous integration

`.github/workflows/main.yml` runs on every push to `main` (and `ci/**`
branches) and on every pull request targeting `main`. It performs a single
Linux job:

* `make test` runs the Ruff lint, a pytest run with coverage enabled, and writes
both `coverage.xml` and an HTML report to `htmlcov/index.html`. Open the HTML
report in a browser (for example with `xdg-open htmlcov/index.html`) or run
`uv run coverage report` for a terminal summary.

`HISTORY.md`-only changes are ignored so changelog commits do not trigger a run.

## Release pipeline

`.github/workflows/release.yml` is triggered by a tag push (normally created by
`make release`). It runs:

1. `quality` — the same `make test` gate.
2. `release` — creates the GitHub release with a generated changelog.
3. `deploy` — builds the distributions and uploads them to PyPI.
4. `build-linux` — builds the single-file executable with PyInstaller and
   attaches `package-linux.zip` to the GitHub release.

### Re-running a release

To re-run the pipeline for an existing tag (for example to rebuild the Linux
archive), dispatch the workflow on that tag:

```bash
gh workflow run release.yml --ref 0.2.7
```

The `--ref` must be a tag, because the release and upload steps only operate on
`refs/tags/*`.

> **Note:** A version can only be uploaded to PyPI once. If the original
> release already uploaded that version, the `deploy` job fails with
> "File already exists". The build jobs still run because they depend on the
> `release` job, not on `deploy`; only the overall run is marked as failed.

## Troubleshooting

* **Coverage report is empty or stale.** Run `make test` locally and open
  `htmlcov/index.html` for the coverage report.
* **The release has no Linux archive.** Confirm the workflow ran on a tag, not a
  branch, and inspect the `build-linux` job logs.

## Reusing this setup in another repository

| File                                           | Purpose                                       |
| ---------------------------------------------- | --------------------------------------------- |
| `.github/workflows/main.yml`                   | Push/PR CI                                    |
| `.github/workflows/release.yml`                | Tag-triggered release and Linux build         |
| `.github/actions/setup-environment/action.yml` | Shared uv setup used by every job             |
| `Makefile`                                     | `release` and `build-linux` targets           |
| `docs/develop/ci.md`                           | This page                                     |

See [Releasing Your Python Project to PyPI](pypi_release.md) for the PyPI token
and packaging setup.