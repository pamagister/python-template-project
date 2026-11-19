<!-- This README.md is auto-generated from docs/index.md -->

# Welcome to python-template-project

A slim, local-first Python project template with a browser-based image exporter.

[![Github CI Status](https://github.com/pamagister/python-template-project/actions/workflows/main.yml/badge.svg)](https://github.com/pamagister/python-template-project/actions)
[![GitHub release](https://img.shields.io/github/v/release/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/releases)
[![Read the Docs](https://readthedocs.org/projects/python-template-project/badge/?version=stable)](https://python-template-project.readthedocs.io/en/stable/)
[![License](https://img.shields.io/github/license/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/issues)
[![PyPI](https://img.shields.io/pypi/v/python-template-project)](https://pypi.org/project/python-template-project/)
[![Downloads](https://pepy.tech/badge/python-template-project)](https://pepy.tech/project/python-template-project/)

This template provides a solid foundation for your next Python project. It keeps a
battle-tested tooling setup (uv, Ruff, pytest, mkdocs, PyInstaller, tag-based
releases) while staying small: the only runtime dependencies are **PyYAML** and
**Pillow**.

---

## How to use this template

Getting started on developing your own project based on this template.

> **DO NOT FORK**
> This project is meant to be used from the **[Use this template](https://github.com/pamagister/python-template-project/generate)** feature.

---

1. **Create a new repository using GitHub template**
   Click on **[Use this template](https://github.com/pamagister/python-template-project/generate)**.

2. **Give a name to your project**
   For example: `my-python-project`
   *(Hyphens may be used as project name; they are converted during renaming internally to underscores for packages.)*

3. **Set write permissions**
   Go to: `Repository -> Settings -> Actions -> General -> Workflow permissions`
   Select: `Read and write permissions`, then click **Save**.

4. **Trigger rename workflow**
   Navigate to the `Actions` tab, select **Rename Action** and run the workflow on the `main` branch.

5. **Wait for the workflow to finish**

6. **Clone the repository**
   ```bash
   git clone [your-github-url]
   ```

7. **Open the project in your IDE**

8. **Install dependencies and create virtual environment**
   ```bash
   make install
   ```

9. **Configure your IDE**
   Set `.venv` as the local Python virtual environment.

10. **Adjust project metadata**
    Modify `pyproject.toml` (e.g., project description, authors, license, etc.)

11. **Clean up template scripts**
    Delete the files:
    * `rename_project.yml`
    * `rename_project.sh`

12. **Format your codebase**
    ```bash
    make fmt
    ```

13. **Enable pre-commit hooks**
    ```bash
    uv run pre-commit install
    ```

14. **Add repository to Read the Docs**
    Visit: [https://app.readthedocs.org/dashboard/import/](https://app.readthedocs.org/dashboard/import/)

15. **Configure PyPI publishing**
    * Generate a **PyPI API token** from your PyPI account.
    * Go to **GitHub -> Settings -> Secrets and variables -> Actions**.
    * Add the secret as `PYPI_API_TOKEN`.

16. **Release your first version**
    ```bash
    make release
    ```

---

## Feature overview

* **Package Management:** Uses [uv](https://docs.astral.sh/uv/getting-started/), an extremely fast Python package manager, with dependencies managed in `pyproject.toml`.
* **Code Formatting and Linting:** Ruff auto-formatter and linter for consistent code style.
* **Testing:** Unit testing framework with [pytest](https://docs.pytest.org/en/latest/).
* **Code coverage reports** using [coverage.py](https://coverage.readthedocs.io/).
* **CI/CD:** [GitHub Actions](https://github.com/features/actions) Linux checks on every push and pull request.
* **Automated Builds:** GitHub pipeline for a single-file Linux executable with PyInstaller.
* **Parameter-Driven Automation:**
  * A self-contained configuration layer (no external config framework).
  * A stdlib `argparse` CLI with `gui`, `export` and `config` subcommands.
  * CLI and configuration documentation generated from the live parser and config definitions.
  * Automatic change log using **gitchangelog** to keep a `HISTORY.md` file up to date.
* **Documentation:** Publishing on [Read the Docs](https://about.readthedocs.com/) using [mkdocs](https://www.mkdocs.org/).
* **Local Web UI:** A lightweight, local-first browser UI served by the standard library `http.server`, using Pillow for thumbnails and export. No native desktop GUI and no client framework.
* **Workflow Automation:** A `Makefile` simplifies and automates common development tasks.
* **Agentic Workflows:** Context-sparing OpenCode workflows (task, feature, autopilot, mission planning) — see [docs/workflows.md](workflows.md).
* **Release pipeline:** `make release` validates the tag, creates it and pushes it. The `release` workflow then creates a GitHub release and publishes to [PyPI](https://pypi.org).
  * **[setuptools](https://pypi.org/project/setuptools/)** is used to package the project and manage dependencies.
  * **[setuptools-scm](https://pypi.org/project/setuptools-scm/)** automatically generates `_version.py` from the Git tag.

---

## Installation

Get an impression of how your own project could be installed and used.

Download from [PyPI](https://pypi.org/).

For more installation options see [install](docs/getting-started/install.md).

```bash
pip install python-template-project
```

Open the web UI (also the default when the installed command is run without arguments):

```bash
python-template-project
```

Run the CLI directly:

```bash
python-template-project export --source ./photos --output ~/Pictures --format jpg
python-template-project config --show
```

From a source checkout the module equivalents are:

```bash
python -m python_template_project --help
python -m python_template_project export --source ./photos
```

---

## Troubleshooting

### Problems with release pipeline

If you get this error below:
```bash
/home/runner/work/_temp/xxxx_xxx.sh: line 1: .github/release_message.sh: Permission denied
```

You have to run these commands in your IDE Terminal or the git bash and then push the changes.
```bash
git update-index --chmod=+x ./.github/release_message.sh
```