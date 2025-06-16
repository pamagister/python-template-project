# Command line interface

Command line options

```bash
python -m python_template_project.cli [OPTIONS] path/to/file
```

---

## ⚙️ CLI-Options

| Option                | Typ  | Description                                       | Default    | Choices       |
|-----------------------|------|---------------------------------------------------|------------|---------------|
| `path/to/file`        | str  | Path to input (file or folder)                    | *required* | -             |
| `--output`            | str  | Path to output destination                        | *required* | -             |
| `--min_dist`          | int  | maximum distance between two waypoints            | 20         | -             |
| `--extract_waypoints` | bool | extract starting points of each track as waypoint | True       | [True, False] |


## 💡 Examples

In the example, the following is assumed: `example.input` in the current directory


### 1. Standard version (only required parameter)

```bash
python -m python_template_project.cli input
```

### 2. Example with 1 Parameter(s)

```bash
python -m python_template_project.cli --min_dist 20 input
```

### 3. Example with 2 Parameter(s)

```bash
python -m python_template_project.cli --min_dist 20 --extract_waypoints True input
```