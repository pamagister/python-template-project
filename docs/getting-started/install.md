# Installation


## PyPI

### Install the package from PyPI

Download from [PyPI](https://pypi.org/):

```bash
pip install python-template-project
```

### Run the web UI

```bash
python-template-project
```

The command starts a local server (bound to `127.0.0.1` by default) and opens the
browser. Use `python-template-project gui --help` for host, port and browser options.

### Run the CLI

```bash
python-template-project --help
python-template-project export --source ./photos --output ~/Pictures --format jpg
python-template-project config --show
```

## Executable

Download the latest Linux executable from the
[GitHub releases page](https://github.com/pamagister/python-template-project/releases/latest).

The project only ships a Linux binary. On other platforms install from PyPI or
run from source.

## Run from source

### Clone the repository

```bash
git clone https://github.com/pamagister/python-template-project
```

### Navigate to the project directory

```bash
cd python-template-project
```

### Install dependencies

```bash
make install
```

### Run the web UI from source

```bash
python -m python_template_project gui
```

### Run the CLI from source

```bash
python -m python_template_project --help
```