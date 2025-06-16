# Command line interface

Command line options

```bash
python -m python_template_project.cli [OPTIONS] path/to/file.mbox
```

---

## ⚙️ CLI-Options

| Option              | Typ  | Description                                           | Default    | Choices        |
|---------------------|------|-------------------------------------------------------|------------|----------------|
| `--sent_from`       | bool | Include 'From' field                                  | True       | [True, False]  |
| `--to`              | bool | Include 'To' field                                    | True       | [True, False]  |
| `--date`            | bool | Include 'Date' field                                  | True       | [True, False]  |
| `--subject`         | bool | Include 'Subject' field                               | True       | [True, False]  |
| `--format`          | str  | Output format: txt or csv                             | 'txt'      | ['txt', 'csv'] |
| `--max_days`        | int  | Max number of days per output file (-1 for unlimited) | -1         | -              |
| `path/to/file.mbox` | str  | Path to mbox file                                     | *required* | -              |


## 💡 Examples

In the example, the following is assumed: `example.mbox` in the current directory


### 1. Standard version (only required parameter)

```bash
python -m python_template_project.cli mbox_file
```

### 2. Example with 1 Parameter(s)

```bash
python -m python_template_project.cli --sent_from True mbox_file
```

### 3. Example with 2 Parameter(s)

```bash
python -m python_template_project.cli --sent_from True --to True mbox_file
```

### 4. Example with 3 Parameter(s)

```bash
python -m python_template_project.cli --sent_from True --to True --date True mbox_file
```

### 5. Example with 4 Parameter(s)

```bash
python -m python_template_project.cli --sent_from True --to True --date True --subject True mbox_file
```