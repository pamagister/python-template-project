# Welcome to python-template-project

A feature-rich Python project template designed for robustness and ease of use.

[![Github CI Status](https://github.com/pamagister/python-template-project/actions/workflows/main.yml/badge.svg)](https://github.com/pamagister/python-template-project/actions)
[![GitHub release](https://img.shields.io/github/v/release/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/releases)
[![Read the Docs](https://readthedocs.org/projects/python-template-project/badge/?version=stable)](https://python-template-project.readthedocs.io/en/stable/)
[![License](https://img.shields.io/github/license/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/pamagister/python-template-project)](https://github.com/pamagister/python-template-project/issues)
[![PyPI](https://img.shields.io/pypi/v/python-template-project)](https://pypi.org/project/python-template-project/)


This template provides a solid foundation for your next Python project, incorporating best practices for testing, automation, and distribution. It streamlines the development process with a comprehensive set of pre-configured tools and workflows, allowing you to focus on writing code.


## Feature overview

* **Testing:** Unit testing setup with `pytest`.
* **CI/CD:** GitHub Actions for automated builds (Windows, macOS), unit tests, and code checks.
* **Code Formatting:** Pre-commit hook with the *black* auto-formatter to ensure consistent code style.
* **Automated Builds:** GitHub pipeline for automatically building a Windows executable and a macOS installer.
* **Package Management:** Utilizes *uv*, an extremely fast Python package manager, with dependencies managed in `pyproject.toml`.
* **Parameter-Driven Automation:**
    * Automatic generation of a configuration file from parameter definitions.
    * Automatic generation of a Command-Line Interface (CLI) from the same parameters.
    * Automatic generation of CLI API documentation.
* **Documentation:** Configuration for publishing documentation on Read the Docs.
* **Workflow Automation:** A `Makefile` is included to simplify and automate common development tasks.
* **Minimalist GUI:** Comes with a basic GUI based on [tkinker](https://tkdocs.com/tutorial/index.html) that includes an auto-generated settings menu based on your defined parameters.

## Getting started

1. **Create** a new [github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).
2. **Clone** [github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the into your local file system.
    ```bash
    git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY
    ```
4. **Install** [uv package and project manager](https://docs.astral.sh/uv/getting-started/installation/)
    ```bash
    pip install uv
    ```
5. **Generate** [a sample project](https://docs.astral.sh/uv/guides/projects/#creating-a-new-project) with uv
6. Add and **push** the artifacts to your github repository
    ```bash
    git push
    ```
8. Copy the content of this repository into your repository

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

