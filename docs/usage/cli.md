# Command Line Interface

Command line options for python_template_project.

This document is generated from the live argparse parser, so it always
matches the actual CLI.

## `python_template_project`

```
usage: python-template-project [-h] [--config CONFIG] [-v | -q] {gui,export,config} ...
```

Local web UI and image export helper.

| Option | Type | Description | Default | Choices |
|--------|------|-------------|---------|---------|
| `--config` | - | Path to a configuration file (defaults to ./config.yaml) | - | - |
| `-v, --verbose` | - | Enable debug logging | False | - |
| `-q, --quiet` | - | Show warnings and errors only | False | - |

## `python_template_project gui`

```
usage: python-template-project gui [-h] [--host HOST] [--port PORT] [--open-browser | --no-open-browser]
```

| Option | Type | Description | Default | Choices |
|--------|------|-------------|---------|---------|
| `--host` | str | Host interface the web UI binds to | 127.0.0.1 | - |
| `--port` | int | Port the web UI listens on | 8765 | - |
| `--open-browser, --no-open-browser` | - | Open the web UI in the default browser on start | True | - |

## `python_template_project export`

```
usage: python-template-project export [-h] [--source SOURCE_DIR] [--output OUTPUT_ROOT] [--format {jpg,png}] [--quality JPG_QUALITY] [--reduce | --no-reduce] [--max-side MAX_LONG_SIDE]
```

| Option | Type | Description | Default | Choices |
|--------|------|-------------|---------|---------|
| `--source` | str | Default directory that contains the source images | /home/paul/Pictures | - |
| `--output` | str | Root directory below which export folders are created | /home/paul/Pictures | - |
| `--format` | str | Export image format | jpg | jpg, png |
| `--quality` | int | JPEG quality (1-100) | 85 | - |
| `--reduce, --no-reduce` | - | Resize images so the longest side matches max_long_side | False | - |
| `--max-side` | int | Longest side in pixels when reducing resolution | 1200 | - |

## `python_template_project config`

```
usage: python-template-project config [-h] [--show] [--set KEY=VALUE] [--path]
```

| Option | Type | Description | Default | Choices |
|--------|------|-------------|---------|---------|
| `--show` | - | Print the effective configuration | False | - |
| `--set` | - | Set a configuration value (repeatable) | [] | - |
| `--path` | - | Print the configuration file path | False | - |
