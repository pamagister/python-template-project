Changelog
=========


(unreleased)
------------

Fix
~~~
- UnicodeEncodeError in show_tree.py unter Windows (cp1252) [Paul
  Magister]

  sys.stdout auf UTF-8 umstellen, damit Unicode-Symbole (Emojis,
  Baum-Zeichen) auch unter Windows mit cp1252-Konsole ausgegeben
  werden können.

  Closes #48
- Use Unix path separator in build-linux (closes #43) [Paul Magister]

  config.yaml verwendet in build-linux das Windows-Pfadtrennzeichen ';',
  unter Linux/macOS erwartet PyInstaller den Doppelpunkt ':'. Damit wird
  config.yaml korrekt in den Linux-Build bündelt.

Other
~~~~~
- Move globally useful guidelines to a AGENTS_GLOBAL.md that has to be
  renamed and kept in the global folder for AGENTS.md files. [Paul
  Magister]
- Merge pull request #49 from
  pamagister/dependabot/github_actions/actions/checkout-7. [Paul
  Magister]

  Bump actions/checkout from 4 to 7
- Merge branch 'main' into dependabot/github_actions/actions/checkout-7.
  [Paul Magister]
- Merge pull request #50 from
  pamagister/dependabot/github_actions/actions/setup-python-7. [Paul
  Magister]

  Bump actions/setup-python from 5 to 7
- Bump actions/setup-python from 5 to 7. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 7.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v7)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #51 from
  pamagister/dependabot/github_actions/codecov/codecov-action-7. [Paul
  Magister]

  Bump codecov/codecov-action from 5 to 7
- Bump codecov/codecov-action from 5 to 7. [dependabot[bot]]

  Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 5 to 7.
  - [Release notes](https://github.com/codecov/codecov-action/releases)
  - [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/codecov/codecov-action/compare/v5...v7)

  ---
  updated-dependencies:
  - dependency-name: codecov/codecov-action
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Bump actions/checkout from 4 to 7. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 7.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v7)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '7'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge pull request #39 from
  pamagister/dependabot/github_actions/actions/setup-python-6. [Paul
  Magister]

  Bump actions/setup-python from 4 to 6
- Merge branch 'main' into dependabot/github_actions/actions/setup-
  python-6. [Paul Magister]
- Merge pull request #40 from
  pamagister/dependabot/github_actions/actions/checkout-6. [Paul
  Magister]

  Bump actions/checkout from 3 to 6
- Merge branch 'main' into dependabot/github_actions/actions/checkout-6.
  [Paul Magister]
- Bump actions/checkout from 3 to 6. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 3 to 6.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v3...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Merge branch 'main' into dependabot/github_actions/actions/setup-
  python-6 resolve merge conflict manually. [Paul Magister]
- Test: show_tree-Ausgabe unter Windows als UTF-8 dekodieren. [Paul
  Magister]

  subprocess.run(text=True) dekodiert unter Windows (cp1252) die
  Kindprozess-Ausgabe; da show_tree.py UTF-8 ausgibt, muss der Test
  encoding="utf-8" verwenden, damit Emoji- und Baum-Zeichen korrekt
  erfasst werden.

  Closes #48
- #48: add github usage details. [Paul Magister]
- Docs: Add SECURITY.md for vulnerability reporting (closes #45) [Paul
  Magister]
- Docs: Add SECURITY.md for vulnerability reporting (closes #45) [Paul
  Magister]

  Dokumentiert den Meldungsweg für Sicherheitslücken über die private
  Schwachstellenmeldung von GitHub (Security -> Report a vulnerability),
  da es keinen öffentlichen Kanal gab.
- Ci: concurrency-Gruppen in allen Workflows (closes #42) [Paul
  Magister]

  Verhindert überlappende Läufe desselben Workflows (Gruppe nach
  github.workflow und github.ref). Läufe bei Pull-Requests werden beim
  erneuten Push abgebrochen; Tag-Releases und main-Pushes laufen weiter.
- Ci: release_message.sh auch bei erstem Tag gültig (closes #46) [Paul
  Magister]

  Bei nur einem Tag lieferte 'git tag ... | sed -n 2p' keinen Vorgänger,
  weshalb 'git shortlog ".."' fehlschlug oder einen leeren
  Changelog erzeugte. Nun wird bei fehlendem Vorgänger-Tag die Historie
  aller Commits einbezogen.
- Ci: Checkout with fetch-depth 0 in deploy job (closes #44) [Paul
  Magister]

  setuptools_scm benötigt die Git-Tags, um die Version zu erzeugen.
  Im deploy-Job von release.yml fehlte fetch-depth: 0 (shallow clone),
  wodurch der PyPI-Upload fehlschlagen oder eine falsche Version
  veröffentlichen konnte.
- Squeeze AGENTS.md. [Paul Magister]
- Feat(show_tree): use nice symbols. [Paul Magister]
- Feat(show_tree): align folder details and add global summary. [Paul
  Magister]

  Show folder summaries whenever --details is used, restrict --folder output to directories without file names, and always print a recursive overall summary at the end.

  Refs #41
- Feat(show_tree): add per-folder summaries. [Paul Magister]

  Add --folder to show direct subfolder/file counts, total size, and the top three file extensions per directory. File metadata is suppressed in this mode.

  Refs #41
- Feat(show_tree): add optional metadata details. [Paul Magister]

  Add a --details flag that appends file size, timestamps, owner, directory entry counts, and best-effort document metadata from ODF, OOXML, and PDF files. The default tree output remains unchanged.

  Closes #41
- Add AGENTS.md and harmonize doc generation. [Paul Magister]
- Bump actions/setup-python from 4 to 6. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 4 to 6.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v4...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...


0.2.5 (2026-10-07)
------------------
- Docs: Update HISTORY.md for release 0.2.5. [Paul Magister]
- Ich habe .readthedocs.yaml auf Read the Docs’ uv-Integration mit der
  Gruppe docs umgestellt. Hinweis: uv sync wählt standardmäßig auch die
  dev-Gruppe aus. [Paul Magister]
- Updated pyproject.toml to remove Deptry’s deprecated setting, which
  pointed at optional-dependency groups that this project doesn’t use.
  Added a targeted exception for lxml, an intentional dependency that
  Deptry otherwise flags as unused. [Paul Magister]
- Bump version of config-cli-gui to latest version. [Paul Magister]
- Improve makefile. [Paul Magister]


0.2.4 (2025-11-30)
------------------
- Docs: Update HISTORY.md for release 0.2.4. [Paul Magister]
- Add linux build workflow. [Paul Magister]
- Avoid warning by adding lxml package. [Paul Magister]
- Fix format. [Paul Magister]
- Only use on py file to show tree with or without python classes. [Paul
  Magister]
- Switch to python scripts that print the project structure. [Paul
  Magister]
- Switch to pytest. [Paul Magister]
- Update README.md from docs/index.md. [github-actions]
- Typo with with. [Paul Magister]


0.2.3 (2025-11-14)
------------------
- Docs: Update HISTORY.md for release 0.2.3. [Paul Magister]
- Run precommit before building release for proper formatting. [Paul
  Magister]
- Valid app_name for cli configuration. [Paul Magister]
- Proper run configurations. [Paul Magister]


0.2.2 (2025-11-14)
------------------
- Docs: Update HISTORY.md for release 0.2.2. [Paul Magister]
- Improved cli example, fix elevation cli param problem. [Paul Magister]
- Update to new config: cli fixes. [Paul Magister]


0.2.1 (2025-11-14)
------------------
- Docs: Update HISTORY.md for release 0.2.1. [Paul Magister]
- Update to new config: use .value to be type save. [Paul Magister]
- Contributing.md: troubleshooting make release issue. [Paul Magister]
- Linux setup details. [paul]
- Feat #34: generate cli and config.md on make docs. [Paul Magister]
- Update README.md from docs/index.md. [github-actions]
- Feat #34: update to config-cli-gui 0.1.1. [Paul Magister]
- Feat #31: delete rename_project.yml. [Paul Magister]
- Feat #34: use config-cli-gui library. [Paul Magister]
- Feat #35: funding page centralized #35. [Paul Magister]


0.2.0 (2025-06-22)
------------------
- Feat #34: prepare config and gui to be used as library: massive
  refactoring. [Paul Magister]
- Feat #34: prepare config and gui to be used as library #34. [Paul
  Magister]
- Feat #20: Makefile: python tree: all class attributes in one line.
  [Paul Magister]
- Update README.md from docs/index.md. [github-actions]
- Feat #31: update docs: usage guide for this template. [Paul Magister]
- Feat #31: update docs: remove unneeded part of get_logging_config.
  [Paul Magister]
- Feat #31: update docs: move installation description below. Describe
  features first. [Paul Magister]
- Feat #20: Makefile: Generate file tree including python internals.
  [Paul Magister]
- Feat #31: move Prepare ZIP file for release into build-macos.yml.
  [Paul Magister]
- Feat #33: Support kml files for input and display output files as
  clickable links #33. [Paul Magister]


0.1.21 (2025-06-21)
-------------------
- Feat #33: Support kml files for input and display output files as
  clickable links #33. [Paul Magister]
- Feat #31: move project specific namings into makefile so that it can
  be renamed. [Paul Magister]


0.1.20 (2025-06-20)
-------------------
- Feat #31: move project specific namings into makefile so that it can
  be renamed. [Paul Magister]
- Feat #31: move project specific namings into makefile so that it can
  be renamed. [Paul Magister]


0.1.19 (2025-06-20)
-------------------
- Feat #31: move project specific namings into makefile so that it can
  be renamed. [Paul Magister]
- Feat #31: try this renaming automation. [Paul Magister]
- Feat #31: improve renaming automation: has to be triggered manually,
  keep kebab-case if project is named like this. [Paul Magister]
- Feat #31: improve renaming automation: has to be triggered manually,
  keep kebab-case if project is named like this. [Paul Magister]
- Feat #31: improve renaming automation: has to be triggered manually,
  keep kebab-case if project is named like this. [Paul Magister]
- Feat #31: consistent naming. [Paul Magister]
- Feat #31: fix rename_project.yml: use correct git auto commit. [Paul
  Magister]
- Feat #31: fix rename_project.yml: use correct git auto commit. [Paul
  Magister]
- Feat #30: fix link issue by modifying link in README.md. [Paul
  Magister]


0.1.18 (2025-06-20)
-------------------
- Feat #30: do not track _version.py. [Paul Magister]
- Feat #30: fix version. [Paul Magister]


0.1.17 (2025-06-20)
-------------------
- Feat #30: fix link issue by modifying link in README.md. [Paul
  Magister]


0.1.16 (2025-06-20)
-------------------
- Fix #29: more rubust usage of srtm in case of connection issues. [Paul
  Magister]
- Feat #30: exclude _version.py from check. [Paul Magister]
- Feat #31: doc on how to generate. [Paul Magister]
- Feat #30: exclude _version.py from check. [Paul Magister]
- Feat #31: enable project to be copied #31. [Paul Magister]
- Feat #27: move build logic into make file #27. [Paul Magister]
- Feat #30: improve README.md, fix utf8-issues on copying. [Paul
  Magister]
- Feat #30: correct doc how to install and use this project. [Paul
  Magister]
- Feat #30: add _version.py instead of VERSION. [Paul Magister]
- Update README.md from docs/index.md. [github-actions]


0.1.15 (2025-06-20)
-------------------
- Feat #30: switch build system to setuptools_scm. [Paul Magister]
- Feat #30: add some links to the doc. [Paul Magister]


0.1.14 (2025-06-20)
-------------------
- Feat #30: release project on pypi: deploy section in release.yml.
  [Paul Magister]
- Feat #30: release project on pypi: rename contributing section, add
  pypi_release.md doc. [Paul Magister]


0.1.13 (2025-06-19)
-------------------
- Feat #16: fix installer link and name. [Paul Magister]
- Feat #16: release. [Paul Magister]


0.1.12 (2025-06-19)
-------------------
- Feat #16: remove old mbox strings and adjust names. [Paul Magister]
- Feat #16: release. [Paul Magister]
- Update README.md from docs/index.md. [github-actions]


0.1.11 (2025-06-19)
-------------------
- Feat #29: Generate elevation of points optionally, bugfix loop in main
  gui, [Paul Magister]
- Feat #28: Multiple file list conversion and merging #28. [Paul
  Magister]
- Feat #14: GUI: add buttons and run menu for each functionality. [Paul
  Magister]
- Feat #14: GUI: do NOT display required param in settings dialog. it
  has to be set every time via gui. [Paul Magister]
- Feat #23: little refactorings on gpx. [Paul Magister]
- Feat #14: GUI: mention tkinker in docs. [Paul Magister]
- Feat #18: Logging enabled in converter logic. [Paul Magister]
- Merge pull request #15 from
  pamagister/dependabot/github_actions/softprops/action-gh-release-2.
  [Paul Magister]

  Bump softprops/action-gh-release from 1 to 2
- Bump softprops/action-gh-release from 1 to 2. [dependabot[bot]]

  Bumps [softprops/action-gh-release](https://github.com/softprops/action-gh-release) from 1 to 2.
  - [Release notes](https://github.com/softprops/action-gh-release/releases)
  - [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/softprops/action-gh-release/compare/v1...v2)

  ---
  updated-dependencies:
  - dependency-name: softprops/action-gh-release
    dependency-version: '2'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...
- Feat #26: unit-tests gpx functionality #26. [Paul Magister]
- Feat #23: Implement gpx functionality: adjust interface. [Paul
  Magister]
- Feat #16: generate relative paths and improve filtering and visuals.
  [Paul Magister]
- Feat #25: add example gpx data #25. [Paul Magister]
- Feat #23: Implement gpx functionality #23. [Paul Magister]
- Feat #22: Auto-generate parameters md doc #22. [Paul Magister]


0.1.10 (2025-06-17)
-------------------
- Feat #21: Build unified executable (gui and cli) for mac os. [Paul
  Magister]


0.1.9 (2025-06-17)
------------------
- Feat #21: Build unified executable (gui and cli) #21. [Paul Magister]
- Feat #20: Makefile: Generate file tree #20. [Paul Magister]
- Feat #16: make release. [Paul Magister]
- Feat #16: fix doc: add git init commands. [Paul Magister]


0.1.8 (2025-06-17)
------------------
- Feat #16: fix doc: command line prompts. [Paul Magister]
- Fix #19: Workaround for deptree issue 295 #19. [Paul Magister]
- Feat #16: new release. [Paul Magister]


0.1.7 (2025-06-17)
------------------
- Feat #8: CI: build macos: more echo. [Paul Magister]
- Feat #7: CI: build windows: more echo. [Paul Magister]
- Feat #7: CI: Create workflow for building Windows executable: fix
  script: remove unneccessary ** [Paul Magister]
- Feat #7: CI: Create workflow for building Windows executable: english.
  [Paul Magister]
- Feat #7: CI: Create workflow for building Windows executable. [Paul
  Magister]
- Feat #7: CI: Create workflow for building Windows executable. [Paul
  Magister]
- Feat #8: CI: Create workflow for building macOS installer/app bundle.
  [Paul Magister]
- Feat #7: CI: Create workflow for building Windows executable. [Paul
  Magister]
- Feat #17: cleanup doc. [Paul Magister]
- Feat #16: adjust doc. [Paul Magister]
- Feat #18: fix deprecation warning. [Paul Magister]
- Feat #18: fix tests. [Paul Magister]
- Feat #18: add logging for gui. [Paul Magister]
- Feat #18: fix. [Paul Magister]
- Feat #18: Logging framework. [Paul Magister]


0.1.6 (2025-06-17)
------------------
- Feat #18: Logging framework. [Paul Magister]
- Feat #14: add run configurations. [Paul Magister]
- Feat #14: Implement minimalist GUI with an auto-generated settings
  menu. [Paul Magister]
- Feat #10: massive refactoring on parameter and config handling: fix
  tests. [Paul Magister]
- Feat #10: massive refactoring on parameter and config handling: remove
  parameters.py. [Paul Magister]
- Feat #10: massive refactoring on parameter and config handling. [Paul
  Magister]
- Feat #17: genberal refactoring. [Paul Magister]
- Feat #13: rename image. [Paul Magister]
- Feat #11: adjust posituonal parameter to be more general. [Paul
  Magister]
- Feat #17: structural refactorings, fix import issues. [Paul Magister]
- Feat #17: structural refactorings. [Paul Magister]
- Feat #11: suitable cli parameters for this example workspace. [Paul
  Magister]
- Feat #5: Makefile better debugable. [Paul Magister]
- Feat #12: add cli nav. [Paul Magister]
- Feat #16: release. [Paul Magister]


0.1.5 (2025-06-16)
------------------
- Feat #12: add cli nav. [Paul Magister]
- Feat #12: cli documentation. [Paul Magister]
- Feat #16: make the sh files runnable using: ```git update-index
  --chmod=+x ./.github/release_message.sh``` [Paul Magister]
- Feat #16: release. [Paul Magister]


0.1.3 (2025-06-16)
------------------
- Feat #16: release: remove redundand VERSION and HISTORY push. [Paul
  Magister]
- Feat #16: release. [Paul Magister]


0.1.2 (2025-06-16)
------------------
- Feat #16: Make release_message.sh executable. [Paul Magister]
- Feat #16: release. [Paul Magister]


0.1.1 (2025-06-15)
------------------
- Feat #2: Configure pre-commit hook with black for code formatting.
  [Paul Magister]
- Feat #13: auto-copy readme. [Paul Magister]
- Feat #13: auto-copy readme. [Paul Magister]
- Feat #13: add correct image. [Paul Magister]
- Feat #10: adjust automatic generation of config files from parameters.
  [Paul Magister]
- Feat #2: auto-format code, adjust Makefile #6: make github actions
  running finally. [Paul Magister]
- Feat #2: auto-format code, adjust Makefile. [Paul Magister]
- Feat #2: auto-format code. [Paul Magister]
- Feat #1: Setup unit testing with pytest. [Paul Magister]
- Feat #6: Implement GitHub Actions for test, and checks. [Paul
  Magister]
- Feat #10: Implement automatic generation of config files from
  parameters. [Paul Magister]
- Feat #11: Implement automatic generation of a CLI from parameters.
  [Paul Magister]
- Feat #4: adjust project names. [Paul Magister]
- Feat #4: Manage dependencies via pyproject.toml. [Paul Magister]
- Feat #5: Makefile for automating common development tasks. [Paul
  Magister]
- Merge remote-tracking branch 'origin/main' [Paul Magister]
- Feat #13: add readthedocs config. [Paul Magister]
- Feat #13: add readthedocs config. [Paul Magister]
- Feat #13: initial README.md. [Paul Magister]
- Initial commit. [Paul Magister]


