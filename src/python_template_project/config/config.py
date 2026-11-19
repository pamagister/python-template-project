"""In-repo configuration layer.

A single source of truth for application parameters. Parameters are grouped
into categories and can be persisted to a commented YAML file. Parameters
flagged with ``is_cli`` are turned into argparse arguments and documented by
the CLI and config doc generators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

APP_NAME = "python_template_project"


def _default_pictures_dir() -> str:
    """Return the OS-specific default pictures directory."""
    return str(Path.home() / "Pictures")


@dataclass
class ConfigParameter:
    """A single configuration parameter."""

    name: str
    value: Any
    help: str = ""
    type: str = "str"
    choices: list[Any] | None = None
    required: bool = False
    is_cli: bool = False
    cli_group: str | None = None
    cli_flag: str | None = None

    @property
    def flag(self) -> str:
        """Return the CLI flag (without leading dashes)."""
        return self.cli_flag or self.name

    def coerce(self, raw: Any) -> Any:
        """Coerce a raw (usually string) value into the parameter type."""
        if self.choices is not None:
            for choice in self.choices:
                if isinstance(choice, bool):
                    if isinstance(raw, str) and raw.strip().lower() in {
                        "true",
                        "1",
                        "yes",
                        "on",
                    }:
                        return True
                    if isinstance(raw, str) and raw.strip().lower() in {
                        "false",
                        "0",
                        "no",
                        "off",
                    }:
                        return False
                if str(choice) == str(raw):
                    return choice
        if self.type == "bool":
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, str):
                return raw.strip().lower() in {"true", "1", "yes", "on"}
            return bool(raw)
        if self.type == "int":
            return int(raw)
        if self.type == "float":
            return float(raw)
        return str(raw)


@dataclass
class ConfigCategory:
    """An ordered group of configuration parameters."""

    name: str
    parameters: list[ConfigParameter] = field(default_factory=list)

    def add(self, parameter: ConfigParameter) -> ConfigParameter:
        """Append a parameter and return it."""
        self.parameters.append(parameter)
        return parameter

    def get(self, name: str) -> ConfigParameter:
        """Return a parameter by name."""
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter
        raise KeyError(f"Unknown config parameter: {self.name}.{name}")

    def has(self, name: str) -> bool:
        """Return whether a parameter with this name exists."""
        return any(parameter.name == name for parameter in self.parameters)

    def as_dict(self) -> dict[str, Any]:
        """Return the parameter values as a plain dictionary."""
        return {parameter.name: parameter.value for parameter in self.parameters}


class ConfigManager:
    """Holds categories of parameters and handles YAML persistence."""

    def __init__(self, categories: list[ConfigCategory], config_file: str | Path | None = None):
        self.categories: dict[str, ConfigCategory] = {
            category.name: category for category in categories
        }
        self.config_file = Path(config_file) if config_file else Path("config.yaml")
        if self.config_file.exists():
            self.load(self.config_file)

    def category(self, name: str) -> ConfigCategory:
        """Return a category by name."""
        return self.categories[name]

    def get(self, category: str, name: str) -> ConfigParameter:
        """Return a single parameter."""
        return self.category(category).get(name)

    def set(self, key: str, value: Any) -> None:
        """Set a parameter value using a ``category.name`` or ``name`` key."""
        if "." in key:
            category_name, name = key.split(".", 1)
            self.get(category_name, name).value = self.get(category_name, name).coerce(value)
            return
        for category in self.categories.values():
            if category.has(key):
                parameter = category.get(key)
                parameter.value = parameter.coerce(value)
                return
        raise KeyError(f"Unknown config key: {key}")

    def get_cli_parameters(self, group: str | None = None) -> list[ConfigParameter]:
        """Return CLI parameters, optionally filtered by subcommand group."""
        result: list[ConfigParameter] = []
        for category in self.categories.values():
            for parameter in category.parameters:
                if parameter.is_cli and parameter.cli_group == group:
                    result.append(parameter)
        return result

    @staticmethod
    def get_app_name() -> str:
        """Return the application name."""
        return APP_NAME

    def load(self, path: str | Path | None = None) -> None:
        """Load values from a YAML file, ignoring unknown keys."""
        path = Path(path) if path else self.config_file
        if not path.exists():
            return
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for category_name, values in data.items():
            category = self.categories.get(category_name)
            if category is None or not isinstance(values, dict):
                continue
            for name, raw in values.items():
                if category.has(name):
                    category.get(name).value = category.get(name).coerce(raw)

    def save(self, path: str | Path | None = None) -> None:
        """Persist the current values using a plain YAML document."""
        path = Path(path) if path else self.config_file
        data = {name: category.as_dict() for name, category in self.categories.items()}
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )


def build_default_config() -> ConfigManager:
    """Create the default configuration for this template."""
    app = ConfigCategory("app")
    app.add(
        ConfigParameter(
            name="log_level",
            value="INFO",
            help="Logging level for the application",
            type="str",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
    )
    app.add(
        ConfigParameter(
            name="enable_file_logging",
            value=True,
            help="Enable logging to a file",
            type="bool",
        )
    )
    app.add(
        ConfigParameter(
            name="enable_console_logging",
            value=True,
            help="Enable logging to the console",
            type="bool",
        )
    )

    paths = ConfigCategory("paths")
    paths.add(
        ConfigParameter(
            name="source_dir",
            value=_default_pictures_dir(),
            help="Default directory that contains the source images",
            type="str",
            is_cli=True,
            cli_group="export",
            cli_flag="source",
        )
    )
    paths.add(
        ConfigParameter(
            name="output_root",
            value=_default_pictures_dir(),
            help="Root directory below which export folders are created",
            type="str",
            is_cli=True,
            cli_group="export",
            cli_flag="output",
        )
    )

    export = ConfigCategory("export")
    export.add(
        ConfigParameter(
            name="format",
            value="jpg",
            help="Export image format",
            type="str",
            choices=["jpg", "png"],
            is_cli=True,
            cli_group="export",
        )
    )
    export.add(
        ConfigParameter(
            name="jpg_quality",
            value=85,
            help="JPEG quality (1-100)",
            type="int",
            is_cli=True,
            cli_group="export",
            cli_flag="quality",
        )
    )
    export.add(
        ConfigParameter(
            name="reduce_resolution",
            value=False,
            help="Resize images so the longest side matches max_long_side",
            type="bool",
            is_cli=True,
            cli_group="export",
            cli_flag="reduce",
        )
    )
    export.add(
        ConfigParameter(
            name="max_long_side",
            value=1200,
            help="Longest side in pixels when reducing resolution",
            type="int",
            is_cli=True,
            cli_group="export",
            cli_flag="max-side",
        )
    )

    server = ConfigCategory("server")
    server.add(
        ConfigParameter(
            name="host",
            value="127.0.0.1",
            help="Host interface the web UI binds to",
            type="str",
            is_cli=True,
            cli_group="gui",
        )
    )
    server.add(
        ConfigParameter(
            name="port",
            value=8765,
            help="Port the web UI listens on",
            type="int",
            is_cli=True,
            cli_group="gui",
        )
    )
    server.add(
        ConfigParameter(
            name="open_browser",
            value=True,
            help="Open the web UI in the default browser on start",
            type="bool",
            is_cli=True,
            cli_group="gui",
            cli_flag="open-browser",
        )
    )

    return ConfigManager([app, paths, export, server])
