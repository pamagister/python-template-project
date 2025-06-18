.ONESHELL:
SHELL := /bin/bash
PYTHONIOENCODING := utf-8

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	uv venv info

.PHONY: install
install:          ## Install the project in dev mode.
	$(MAKE) lock
	$(MAKE) virtualenv
	uv pip install -e .[dev,docs]

.PHONY: lock
lock:           ## builds the uv.make lock file and syncs the packages
	uv lock

.PHONY: precommit
# install automatic pre-commit run locally:
# uv pip install pre-commit # --> is usually configured in pyproject.toml
# uv run pre-commit install # --> will setup .git\hooks\pre-commit if a .pre-commit-config.yaml exists
precommit: ## Format, test and check dependencies.
	$(MAKE) fmt
	$(MAKE) test
	$(MAKE) deptry

.PHONY: fmt
fmt:              ## Format code using black & isort.
	uv run ruff format src/
	uv run ruff format tests/
	uv run ruff check src/ --fix
	uv run ruff check tests/ --fix

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	uv run ruff check src/
	uv run ruff check tests/
	uv run ruff format --check src/
	uv run ruff format --check tests/
#	uv run mypy --ignore-missing-imports src/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	uv run pytest -v --cov-config .coveragerc --cov=src -l --tb=short --maxfail=1 tests/
	uv run coverage xml
	uv run coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr uv run pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf site
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: deptry
deptry:            ## Check for unused dependencies.
	uv pip install deptry
	uv run deptry src

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	uv venv

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create a version tag and push to GitHub"

	@CURRENT_VERSION=$$(cat src/VERSION)
	IFS=. read -r MAJOR MINOR PATCH <<< "$$CURRENT_VERSION"
	@NEXT_VERSION="$$MAJOR.$$MINOR.$$((PATCH + 1))"
	echo "Current version: $$CURRENT_VERSION"
	read -e -i "$$NEXT_VERSION" -p "Version? (provide the next x.y.z semver) : " TAG
	echo "$${TAG}" > src/VERSION
	uv run gitchangelog > HISTORY.md
	git add src/VERSION HISTORY.md
	git commit -m "release: version $${TAG} 🚀"
	echo "creating git tag : $${TAG}"
	git tag $${TAG}
	git push -u origin HEAD --tags
	echo "GitHub Actions will detect the new tag and release the new version."
	echo "Add modified files to commit and push them to main"

.PHONY: docs
docs:             ## Build and sync the documentation.
	@echo "sync documentation ..."
	@uv run ./scripts/update_readme.py
	@echo "building documentation ..."
	@uv run mkdocs build
	@uv run mkdocs serve

.PHONY: list
list:            ## Show project file list (excluding ignored folders)
	@powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/show-filelist.ps1

.PHONY: tree
tree:            ## Show project tree (excluding ignored folders)
	@powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/show-tree.ps1

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh
