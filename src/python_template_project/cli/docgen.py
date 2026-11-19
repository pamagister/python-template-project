"""Generate CLI documentation by recursing the argparse help tree."""

from __future__ import annotations

import argparse
from pathlib import Path


def _iter_subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    """Return the subparsers of a parser, keyed by subcommand name."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def _format_action(action: argparse.ArgumentParser._ActionsContainer) -> list[str]:
    """Format one argument action as a Markdown table row."""
    if isinstance(action, argparse._HelpAction):
        return []
    flags = ", ".join(action.option_strings) if action.option_strings else action.metavar or ""
    if not flags:
        return []
    type_name = "" if action.type is None else getattr(action.type, "__name__", str(action.type))
    choices = ", ".join(str(choice) for choice in action.choices) if action.choices else "-"
    default = "-" if action.default in (None, argparse.SUPPRESS) else str(action.default)
    help_text = action.help or ""
    return [f"| `{flags}` | {type_name or '-'} | {help_text} | {default} | {choices} |"]


def _format_section(parser: argparse.ArgumentParser, title: str, level: int) -> list[str]:
    """Render usage, description and options for a parser."""
    heading = "#" * level
    lines = [f"{heading} {title}", "", "```", parser.format_usage().strip(), "```", ""]
    if parser.description:
        lines.extend([parser.description, ""])
    rows = [row for action in parser._actions for row in _format_action(action)]
    if rows:
        lines.extend(
            [
                "| Option | Type | Description | Default | Choices |",
                "|--------|------|-------------|---------|---------|",
                *rows,
                "",
            ]
        )
    return lines


def generate_cli_markdown(
    parser: argparse.ArgumentParser,
    output_file: str | Path,
    app_name: str = "python-template-project",
) -> Path:
    """Walk the parser tree and write Markdown documentation."""
    lines: list[str] = [
        "# Command Line Interface",
        "",
        f"Command line options for {app_name}.",
        "",
        "This document is generated from the live argparse parser, so it always",
        "matches the actual CLI.",
        "",
    ]
    lines.extend(_format_section(parser, f"`{app_name}`", 2))

    subparsers = _iter_subparsers(parser)
    for name, subparser in subparsers.items():
        lines.extend(_format_section(subparser, f"`{app_name} {name}`", 2))
        nested = _iter_subparsers(subparser)
        for nested_name, nested_parser in nested.items():
            lines.extend(_format_section(nested_parser, f"`{app_name} {name} {nested_name}`", 3))

    output = Path(output_file)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
