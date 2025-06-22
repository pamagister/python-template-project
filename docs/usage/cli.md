# Command Line Interface

Command line options for app

```bash
python -m app [OPTIONS] input
```

## Options

| Option                | Type | Description                                       | Default    | Choices       |
|-----------------------|------|---------------------------------------------------|------------|---------------|
| `input`               | str  | Path to input (file or folder)                    | *required* | -             |
| `--output`            | str  | Path to output destination                        | *required* | -             |
| `--min_dist`          | int  | Maximum distance between two waypoints            | 20         | -             |
| `--extract_waypoints` | bool | Extract starting points of each track as waypoint | True       | [True, False] |
| `--elevation`         | bool | Include elevation data in waypoints               | True       | [True, False] |


## Examples


### 1. Basic usage

```bash
python -m app input
```

### 2. With min_dist parameter

```bash
python -m app --min_dist 20 input
```

### 3. With extract_waypoints parameter

```bash
python -m app --extract_waypoints True input
```

### 4. With elevation parameter

```bash
python -m app --elevation True input
```