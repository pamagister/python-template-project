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
	uv sync --all-groups

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
fmt:              ## Format code using Ruff.
	uv run ruff format src/
	uv run ruff format tests/
	uv run ruff check src/ --fix
	uv run ruff check tests/ --fix
	$(MAKE) syncdocs

.PHONY: lint
lint:             ## Run the Ruff linter and format check.
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

.PHONY: build-linux
build-linux:    ## Build the Linux executable (includes the web UI assets and Pillow).
	## Build the Linux executable.
	uv run pyinstaller --onefile --noconfirm src/main.py \
		--name python-template-project \
		--add-data "config.yaml:." \
		--add-data "src/python_template_project/web/assets:python_template_project/web/assets" \
		--collect-submodules PIL \
		--hidden-import python_template_project.cli.cli \
		--hidden-import python_template_project.web.server

	rm -rf release
	mkdir release
	cp dist/python-template-project release
	cp config.yaml release
	cp README.md release


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
release:          ## Create a new, validated release tag (Linux-only release).
	$(MAKE) precommit
	@echo "WARNING: This operation will create a version tag and push to GitHub"

	# Reject a dirty working tree. HISTORY.md churn from gitchangelog is allowed.
	@if [ -n "$$(git status --porcelain | grep -v '^.. HISTORY.md$$')" ]; then \
		echo "ERROR: working tree is not clean (only HISTORY.md changes are allowed)"; \
		git status --short; \
		exit 1; \
	fi

	# Get the latest Git tag if it exists, otherwise default to 0.0.0 for calculations
	# 'git describe --tags --abbrev=0' gets the most recent tag
	# '|| echo 0.0.0' provides a fallback if no tags exist yet
	@CURRENT_TAG=$$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
	@echo "Current (latest) Git tag: $$CURRENT_TAG"

	# Suggest next patch version based on the current tag
	IFS=. read -r MAJOR MINOR PATCH <<< "$$CURRENT_TAG"
	@NEXT_PATCH_VERSION="$$MAJOR.$$MINOR.$$((PATCH + 1))"

	# Prompt the user for the new tag, suggesting the next patch version by default
	read -e -i "$$NEXT_PATCH_VERSION" -p "Enter the new release tag (e.g., 1.0.0, 1.1.0, 1.1.1): " NEW_TAG

	# Validate the semver format (X.Y.Z)
	@echo "$$NEW_TAG" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$$' || { echo "ERROR: tag '$$NEW_TAG' is not X.Y.Z"; exit 1; }

	# Reject duplicate tags
	@if git rev-parse -q --verify "refs/tags/$${NEW_TAG}" >/dev/null; then \
		echo "ERROR: tag '$${NEW_TAG}' already exists"; \
		exit 1; \
	fi

	# Ensure the new version is greater than the current tag
	@NEW_KEY=$$(echo "$${NEW_TAG}" | awk -F. '{print $$1*1000000+$$2*1000+$$3}')
	@CUR_KEY=$$(echo "$${CURRENT_TAG}" | awk -F. '{print $$1*1000000+$$2*1000+$$3}')
	@if [ "$$NEW_KEY" -le "$$CUR_KEY" ]; then \
		echo "ERROR: new tag '$${NEW_TAG}' is not greater than '$${CURRENT_TAG}'"; \
		exit 1; \
	fi

	# Generate changelog *before* tagging, based on existing history up to the new tag point
	uv run gitchangelog > HISTORY.md
	git add HISTORY.md
	git commit -m "docs: Update HISTORY.md for release $${NEW_TAG}"

	echo "Creating git tag : $${NEW_TAG}"
	git tag "$${NEW_TAG}"
	git push -u origin HEAD --tags

	echo "GitHub Actions will detect the new tag and trigger the release workflow."

.PHONY: syncdocs
syncdocs:         ## Sync the documentation.
	@echo "sync documentation ..."
	@uv run ./scripts/generate_config_docs.py
	@uv run ./scripts/update_readme.py
	@uv run ./.github/update_funding.py

.PHONY: docs
docs:             ## Build and sync the documentation.
	## run syncdocs
	$(MAKE) syncdocs
	@echo "building documentation ..."
	@uv run --group docs mkdocs build
	@uv run --group docs mkdocs serve

.PHONY: tree
tree:            ## Show project tree (excluding ignored folders)
	@uv run ./scripts/show_tree.py --details

.PHONY: pytree
pytree:            ## Show project tree (excluding ignored folders)
	@uv run ./scripts/show_tree.py --show-code

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh

.PHONY: mirror-agents
mirror-skills:    ## Mirror OpenCode skills and AGENTS_GLOBAL.md to the global OpenCode skills directory.
	./scripts/mirror-opencode-skills.sh
	./scripts/mirror-opencode-agents.sh
