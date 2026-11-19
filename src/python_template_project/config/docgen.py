"""Generate the default config file and configuration Markdown docs."""

from __future__ import annotations

from pathlib import Path

from python_template_project.config.config import ConfigManager, ConfigParameter


def _format_comment(parameter: ConfigParameter) -> str:
    """Build the inline comment that documents a parameter."""
    parts = [f"type={parameter.type}"]
    if parameter.choices is not None:
        parts.append(f"choices={parameter.choices}")
    if parameter.is_cli:
        parts.append("CLI")
    return "# " + parameter.help + " | " + " | ".join(parts)


def _format_value(value: object) -> str:
    """Render a value as a YAML scalar literal."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return repr(value) if value == "" else f"'{value}'"
    return str(value)


def generate_default_config_file(config: ConfigManager, output_file: str | Path) -> Path:
    """Write a commented ``config.yaml`` for the given configuration."""
    lines: list[str] = []
    for name, category in config.categories.items():
        if lines:
            lines.append("")
        lines.append(f"{name}:")
        for parameter in category.parameters:
            lines.append(f"  {_format_comment(parameter)}")
            lines.append(f"  {parameter.name}: {_format_value(parameter.value)}")
    output = Path(output_file)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def _format_default(parameter: ConfigParameter) -> str:
    """Render a parameter default for the Markdown table."""
    if parameter.required:
        return "*required*"
    if isinstance(parameter.value, str):
        return f"'{parameter.value}'"
    return str(parameter.value)


def _format_choices(parameter: ConfigParameter) -> str:
    """Render a parameter's choices, or a dash when unconstrained."""
    return str(parameter.choices) if parameter.choices is not None else "-"


def generate_config_markdown(config: ConfigManager, output_file: str | Path) -> Path:
    """Write a Markdown reference for every category and parameter."""
    lines: list[str] = [
        "# Configuration Parameters",
        "",
        "These parameters configure the behavior of python-template-project. "
        "Parameters marked as CLI options can also be set on the command line.",
        "",
        "The configuration is stored in `config.yaml` in the project root. You can:",
        "",
        "- Edit the file directly with a text editor.",
        "- Point to a different file with `--config`.",
        "- Change values from the web UI settings panel or the `config` subcommand.",
        "",
    ]
    for name, category in config.categories.items():
        lines.append(f'## Category "{name}" {{#{name}}}')
        lines.append("")
        lines.append("| Name | Type | Description | Default | Choices |")
        lines.append("|------|------|-------------|---------|---------|")
        for parameter in category.parameters:
            columns = [
                parameter.name,
                parameter.type,
                parameter.help,
                _format_default(parameter),
                _format_choices(parameter),
            ]
            lines.append("| " + " | ".join(columns) + " |")
        lines.append("")
    output = Path(output_file)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
