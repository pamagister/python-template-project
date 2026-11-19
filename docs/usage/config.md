# Configuration Parameters

These parameters configure the behavior of python-template-project. Parameters marked as CLI options can also be set on the command line.

The configuration is stored in [`config.yaml`](../../config.yaml). You can:

- Edit the file directly with a text editor.
- Point to a different file with `--config`.
- Change values from the web UI settings panel or the `config` subcommand.

## Category "app" {#app}

| Name | Type | Description | Default | Choices |
|------|------|-------------|---------|---------|
| log_level | str | Logging level for the application | 'INFO' | ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] |
| enable_file_logging | bool | Enable logging to a file | True | - |
| enable_console_logging | bool | Enable logging to the console | True | - |

## Category "paths" {#paths}

| Name | Type | Description | Default | Choices |
|------|------|-------------|---------|---------|
| source_dir | str | Default directory that contains the source images | '/home/paul/Pictures' | - |
| output_root | str | Root directory below which export folders are created | '/home/paul/Pictures' | - |

## Category "export" {#export}

| Name | Type | Description | Default | Choices |
|------|------|-------------|---------|---------|
| format | str | Export image format | 'jpg' | ['jpg', 'png'] |
| jpg_quality | int | JPEG quality (1-100) | 85 | - |
| reduce_resolution | bool | Resize images so the longest side matches max_long_side | False | - |
| max_long_side | int | Longest side in pixels when reducing resolution | 1200 | - |

## Category "server" {#server}

| Name | Type | Description | Default | Choices |
|------|------|-------------|---------|---------|
| host | str | Host interface the web UI binds to | '127.0.0.1' | - |
| port | int | Port the web UI listens on | 8765 | - |
| open_browser | bool | Open the web UI in the default browser on start | True | - |
