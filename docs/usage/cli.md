# Command Line Interface

Command line options for python_template_project

```bash
python-template-project [OPTIONS] <input>
```

For development from a source checkout, the equivalent module invocation is:

```bash
python -m python_template_project [OPTIONS] <input>
```

## Options

| Option                | Type | Description                                       | Default    | Choices       |
|-----------------------|------|---------------------------------------------------|------------|---------------|
| --config              | str  | Path to configuration file                        | -          | -             |
| -v, --verbose         | bool | Enable debug logging                              | False      | [True, False] |
| -q, --quiet           | bool | Show warnings and errors only                     | False      | [True, False] |
| `input`               | str  | Path to input (file or folder)                    | *required* | -             |
| `--output`            | str  | Path to output destination                        | *required* | -             |
| `--min_dist`          | int  | Maximum distance between two waypoints            | 25         | -             |
| `--extract_waypoints` | bool | Extract starting points of each track as waypoint | True       | [True, False] |
| `--elevation`         | bool | Include elevation data in waypoints               | True       | [True, False] |


## Examples


### 1. Basic usage

```bash
python-template-project input
```

### 2. With verbose logging

```bash
python-template-project -v input
python-template-project --verbose input
```

### 3. With quiet mode

```bash
python-template-project -q input
python-template-project --quiet input
```

### 4. With output parameter

```bash
python-template-project --output  input
```

### 5. With min_dist parameter

```bash
python-template-project --min_dist 25 input
```

### 6. With extract_waypoints parameter

```bash
python-template-project --extract_waypoints True input
```

### Developer usage

```bash
python -m python_template_project --help
python -m python_template_project input
```