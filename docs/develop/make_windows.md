# Build a Linux Executable

This project ships a single-file Linux executable built with PyInstaller.

## Prerequisites

* Linux
* [uv](https://docs.astral.sh/uv/) and the project dependencies (`make install`)

## Build

```bash
make build-linux
```

This produces `dist/python-template-project` and assembles a `release/` directory
containing the binary, `config.yaml` and `README.md`.

The PyInstaller invocation bundles the web UI assets
(`src/python_template_project/web/assets`) and Pillow, so the resulting binary
can serve the browser UI without a source checkout.

## Run the binary

```bash
./dist/python-template-project            # opens the web UI
./dist/python-template-project --help     # shows the CLI
```

> **Note:** Only a Linux build is produced. Windows and macOS build jobs were
> removed from CI; use PyPI or a source checkout on those platforms.