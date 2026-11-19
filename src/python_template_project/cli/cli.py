"""argparse-based command line interface for python-template-project.

The parser is derived from the configuration metadata so that ``config.yaml``,
the CLI flags and the generated documentation share a single source of truth.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from python_template_project.config.config import ConfigManager, build_default_config

_TYPES: dict[str, Any] = {"str": str, "int": int, "float": float}


def _add_parameter(parser: argparse.ArgumentParser, parameter: Any) -> None:
    """Add a single CLI parameter to an (sub)parser."""
    flag = f"--{parameter.flag}"
    if parameter.type == "bool":
        parser.add_argument(
            flag,
            dest=parameter.name,
            default=parameter.value,
            action=argparse.BooleanOptionalAction,
            help=parameter.help,
        )
        return
    parser.add_argument(
        flag,
        dest=parameter.name,
        type=_TYPES.get(parameter.type, str),
        default=parameter.value,
        choices=parameter.choices,
        help=parameter.help,
    )


def build_parser(config: ConfigManager) -> argparse.ArgumentParser:
    """Build the full argument parser from configuration metadata."""
    parser = argparse.ArgumentParser(
        prog="python-template-project",
        description="Local web UI and image export helper.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a configuration file (defaults to ./config.yaml)",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Show warnings and errors only",
    )

    subparsers = parser.add_subparsers(dest="command")

    gui_parser = subparsers.add_parser("gui", help="Launch the local web UI")
    for parameter in config.get_cli_parameters("gui"):
        _add_parameter(gui_parser, parameter)

    export_parser = subparsers.add_parser("export", help="Export selected images")
    for parameter in config.get_cli_parameters("export"):
        _add_parameter(export_parser, parameter)

    config_parser = subparsers.add_parser("config", help="Inspect or edit configuration")
    config_parser.add_argument(
        "--show", action="store_true", help="Print the effective configuration"
    )
    config_parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set a configuration value (repeatable)",
    )
    config_parser.add_argument(
        "--path", action="store_true", help="Print the configuration file path"
    )

    return parser


def _load_config(config_path: str | None) -> ConfigManager:
    """Load the configuration, honoring an explicit path.

    A missing file is not an error: the built-in defaults are used and any
    later save (for example via ``config --set``) creates the file.
    """
    config = build_default_config()
    if config_path:
        config.config_file = Path(config_path)
    config.load(config.config_file)
    return config


def _apply_namespace(config: ConfigManager, args: argparse.Namespace, group: str) -> None:
    """Copy CLI overrides for a group back into the configuration."""
    for parameter in config.get_cli_parameters(group):
        value = getattr(args, parameter.name, parameter.value)
        parameter.value = value


def _run_gui(args: argparse.Namespace, config: ConfigManager) -> int:
    """Start the web UI."""
    _apply_namespace(config, args, "gui")
    from python_template_project.core.logging import initialize_logging
    from python_template_project.web.server import run_server

    initialize_logging(config)
    return run_server(config)


def _run_export(args: argparse.Namespace, config: ConfigManager) -> int:
    """Export images from the configured source directory."""
    from python_template_project.core.images import export_images, list_images
    from python_template_project.core.logging import initialize_logging
    from python_template_project.core.paths import resolve_output_root

    _apply_namespace(config, args, "export")
    initialize_logging(config)
    export = config.category("export")
    paths = config.category("paths")

    source = Path(paths.get("source_dir").value)
    output_root = resolve_output_root(paths.get("output_root").value)
    images = list_images(source)
    if not images:
        print(f"No images found in {source}")
        return 1

    output_dir, written = export_images(
        images,
        output_root,
        fmt=export.get("format").value,
        quality=export.get("jpg_quality").value,
        reduce=export.get("reduce_resolution").value,
        max_side=export.get("max_long_side").value,
    )
    print(f"Exported {len(written)} image(s) to {output_dir}")
    return 0


def _run_config(args: argparse.Namespace, config: ConfigManager) -> int:
    """Inspect or modify the configuration."""
    if args.path:
        print(config.config_file)
    if args.show or (not args.set and not args.path):
        data = {name: category.as_dict() for name, category in config.categories.items()}
        print(json.dumps(data, indent=2, default=str))
    for item in args.set:
        if "=" not in item:
            raise SystemExit(f"Invalid --set value (expected KEY=VALUE): {item}")
        key, value = item.split("=", 1)
        try:
            config.set(key.strip(), value.strip())
        except KeyError as error:
            raise SystemExit(str(error)) from error
        print(f"{key}={value}")
    if args.set:
        config.save()
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    argv = list(sys.argv[1:] if argv is None else argv)

    # Pre-parse --config so defaults come from the requested file.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default=None)
    known, _ = pre.parse_known_args(argv)
    config = _load_config(known.config)

    parser = build_parser(config)
    args = parser.parse_args(argv)

    if args.command == "gui":
        return _run_gui(args, config)
    if args.command == "export":
        return _run_export(args, config)
    if args.command == "config":
        return _run_config(args, config)

    parser.print_help()
    return 0


def gui_main(argv: list[str] | None = None) -> int:
    """Entry point that always launches the web UI (used by the GUI alias)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    config = _load_config(_extract_config(argv))
    parser = build_parser(config)
    args = parser.parse_args(["gui", *argv])
    return _run_gui(args, config)


def _extract_config(argv: list[str]) -> str | None:
    """Return the value of --config from an argument list, if present."""
    if "--config" in argv:
        index = argv.index("--config")
        if index + 1 < len(argv):
            return argv[index + 1]
    for item in argv:
        if item.startswith("--config="):
            return item.split("=", 1)[1]
    return None


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
