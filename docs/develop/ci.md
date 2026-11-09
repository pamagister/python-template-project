# CI/CD Pipelines

This page explains how the GitHub Actions workflows work and how to run the
Windows and macOS jobs on demand. The short version:

| Goal                          | Command / action                                  |
| ----------------------------- | ------------------------------------------------- |
| Normal CI (Linux only)        | Push to `main` or open a pull request             |
| CI on Linux, Windows + macOS  | Put `--all` in the commit subject or PR title     |
| Manual full CI run            | `gh workflow run main.yml --ref main -f all=true` |
| Linux-only release            | `make release`                                    |
| Release for all platforms     | `make release ALL=1`                              |
| Re-run release for a tag      | `gh workflow run release.yml --ref <tag> -f all=true` |

Linux is the default because it gives the fastest feedback and uses the
cheapest runner minutes. Windows and macOS are opt-in: macOS minutes are
billed at a much higher rate, and most changes do not need a full
cross-platform run.

## How `--all` is detected

Both workflows contain a small `flags` job. It sets the job output
`build_all` to `true` when any of these is true:

* the checked-out commit **subject** contains the literal text `--all`;
* the pull request title contains `--all` (CI workflow only);
* the manual `all` input was enabled (`workflow_dispatch`).

Only the subject line is scanned. A commit body that merely describes the
flag therefore does not start an expensive full run.

The optional jobs use `if: needs.flags.outputs.build_all == 'true'`. A job
output is necessary because variables written to `$GITHUB_ENV` are only
visible inside the job that writes them.

For a release, the flag must be in the **tagged commit**. `make release
ALL=1` takes care of that by appending `--all` to the subject of the
`HISTORY.md` commit before creating the tag. Adding `--all` only to the tag
name is not enough.

## Testing on all platforms

### From a push or pull request

Add `--all` to the commit subject:

```bash
git commit -m "test: verify cross-platform paths --all"
git push
```

For a pull request, you can instead add `--all` to the PR title. This keeps
the commit history clean and works well for a one-off cross-platform check.

The run then contains:

* `tests` on Ubuntu (`make test`, i.e. Ruff plus pytest);
* `tests-windows` on Windows (pytest directly);
* `tests-macos` on macOS (`make test`).

The platform jobs start only after the Ubuntu job has passed, so a clearly
broken change does not consume Windows or macOS minutes.

### Manually from the Actions tab or CLI

Open **Actions → CI → Run workflow** and enable **Also test Windows and
macOS**, or use the CLI:

```bash
gh workflow run main.yml --ref main -f all=true
```

Without the input, the same workflow runs the normal Linux-only check.

## Releasing on all platforms

`make release` remains the release trigger. It runs the local pre-commit
checks, generates `HISTORY.md`, commits it, creates the version tag and
pushes the commit and tag.

```bash
# Linux + PyPI + GitHub release
make release

# Additionally build the Windows EXE and the macOS app bundle
make release ALL=1
```

With `ALL=1`, the generated release commit ends with `--all`, for example:

```text
docs: Update HISTORY.md for release 0.2.8 --all
```

The release workflow reads that commit subject, so the optional jobs run.
The resulting GitHub release contains:

| Artifacts           | Platform | Job             |
| ------------------- | -------- | --------------- |
| `package-linux.zip` | Linux    | `build-linux`   |
| `installer-win.zip` | Windows  | `build-windows` |
| `package-macOS.zip` | macOS    | `build-macos`   |

Every release always runs the `quality` gate first (lint + tests), then
creates the GitHub release, publishes to PyPI and builds Linux. The
Windows/macOS builds only run when `--all` was present.

### Re-running an existing tag

To add the optional artifacts to an existing tag without creating a new
version, dispatch the release workflow on that tag:

```bash
gh workflow run release.yml --ref 0.2.7 -f all=true
```

The `--ref` must be a tag, because the release and upload steps only operate
on `refs/tags/*`. Dispatching on a branch is not a release trigger.

> **Note:** A release can only be published to PyPI once per version. If the
> original release already uploaded that version, the `deploy` job fails with
> "File already exists". The build jobs still run because they depend on the
> `release` job, not on `deploy`; only the overall run is marked as failed.

## Troubleshooting

* **No Windows/macOS jobs appeared.** Check that `--all` is in the commit
  subject or PR title, or trigger the workflow manually with the input.
  The match is a plain substring, so `--all-platforms` also counts.
* **The release has no Windows/macOS archives.** The tagged commit did not
  contain `--all`. Create a new tag with `make release ALL=1`, or re-run the
  existing tag manually as shown above.
* **A platform job was cancelled by capacity.** macOS runners occasionally
  queue for a long time. Re-run the failed job; the workflow itself is fine.
* **Coverage upload is missing.** The Codecov step is intentionally disabled
  until the token issue is resolved (see issue #59). Run `make test` locally
  and open `htmlcov/index.html` for the coverage report.
* **You want to remove a platform.** Delete its job from the workflow and the
  corresponding `build-*` target from the `Makefile`. The `flags` job and the
  remaining jobs keep working unchanged.

## Reusing this setup in another repository

The pattern is deliberately small and portable. The files involved are:

| File                                             | Purpose                                              |
| ------------------------------------------------ | ---------------------------------------------------- |
| `.github/workflows/main.yml`                     | Push/PR CI with the `flags` job and optional jobs    |
| `.github/workflows/release.yml`                  | Tag-triggered release DAG with the same flag logic   |
| `.github/actions/setup-environment/action.yml`   | Shared uv setup used by every job                    |
| `Makefile`                                       | `release` target with `ALL=1`                        |
| `docs/develop/ci.md`                             | This page                                            |

When porting to a similar Python repository:

1. Keep the `flags` job unchanged and adapt only the platform job names and
   commands.
2. Keep the optional jobs behind `needs: [flags, tests]` and
   `if: needs.flags.outputs.build_all == 'true'`.
3. Keep `make test` as the single Linux entry point if it already runs lint
   plus tests; otherwise call the two commands explicitly.
4. Reuse the existing build targets (`build-win`, `build-macos`,
   `build-linux`) so the workflows stay thin.
5. Keep the release DAG in one workflow file so all archives are attached to
   the same GitHub release.
6. Update the artifact names and the documentation table to match the
   repository's actual outputs.

See [Releasing Your Python Project to PyPI](pypi_release.md) for the PyPI
token and packaging setup.
