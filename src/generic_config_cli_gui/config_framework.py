# config_framework/core.py
"""Generic configuration framework for Python applications."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any

import yaml
from pydantic import BaseModel


@dataclass
class ConfigParameter:
    """Represents a single configuration parameter with all its metadata."""

    name: str
    default: Any
    type_: type
    choices: list[str | bool] = None
    help: str = ""
    cli_arg: str = None
    required: bool = False
    category: str = "general"

    def __post_init__(self):
        if self.cli_arg is None and not self.required:
            self.cli_arg = f"--{self.name}"
        if self.type_ is bool and self.choices is None:
            self.choices = [True, False]


class BaseConfigCategory(BaseModel, ABC):
    """Base class for configuration categories."""

    @abstractmethod
    def get_category_name(self) -> str:
        """Return the category name for this configuration group."""
        pass

    def get_parameters(self) -> list[ConfigParameter]:
        """Get all ConfigParameter objects from this category."""
        parameters = []
        for field_name in self.model_fields:
            param = getattr(self, field_name)
            if isinstance(param, ConfigParameter):
                param.category = self.get_category_name()
                parameters.append(param)
        return parameters


class CliConfigCategory(BaseConfigCategory):
    """Base class for CLI-specific configuration parameters."""

    def get_category_name(self) -> str:
        return "cli"


class ConfigManager:
    """Generic configuration manager that can handle multiple configuration categories."""

    def __init__(self, config_file: str = None, **kwargs):
        """Initialize configuration manager.

        Args:
            config_file: Path to configuration file (JSON or YAML)
            **kwargs: Override parameters in format category__parameter
        """
        self._categories: dict[str, BaseConfigCategory] = {}
        self._cli_category_name: str = None

        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)

        # Override with provided kwargs
        self._apply_kwargs(kwargs)

    def add_category(self, name: str, category: BaseConfigCategory):
        """Add a configuration category.

        Args:
            name: Name of the category (e.g., 'cli', 'app', 'gui')
            category: Configuration category instance
        """
        self._categories[name] = category
        if isinstance(category, CliConfigCategory):
            self._cli_category_name = name

    def get_category(self, name: str) -> BaseConfigCategory:
        """Get a configuration category by name."""
        return self._categories.get(name)

    def get_cli_category(self) -> BaseConfigCategory | None:
        """Get the CLI configuration category."""
        if self._cli_category_name:
            return self._categories[self._cli_category_name]
        return None

    def _apply_kwargs(self, kwargs: dict[str, Any]):
        """Apply keyword arguments to override configuration values."""
        for key, value in kwargs.items():
            if "__" in key:
                category_name, param_name = key.split("__", 1)
                if category_name in self._categories:
                    category = self._categories[category_name]
                    if hasattr(category, param_name):
                        param = getattr(category, param_name)
                        if isinstance(param, ConfigParameter):
                            param.default = value

    def load_from_file(self, config_file: str):
        """Load configuration from JSON or YAML file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yml", ".yaml"]:
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)

        # Apply loaded configuration
        for category_name, category_data in config_data.items():
            if category_name in self._categories:
                category = self._categories[category_name]
                for param_name, param_value in category_data.items():
                    if hasattr(category, param_name):
                        param = getattr(category, param_name)
                        if isinstance(param, ConfigParameter):
                            param.default = param_value

    def save_to_file(self, config_file: str, format_: str = "auto"):
        """Save current configuration to file."""
        config_path = Path(config_file)
        config_data = self.to_dict()

        # Determine format
        if format_ == "auto":
            format_ = "yaml" if config_path.suffix.lower() in [".yml", ".yaml"] else "json"

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            if format_ == "yaml":
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_data, f, indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for category_name, category in self._categories.items():
            category_dict = {}
            for param in category.get_parameters():
                category_dict[param.name] = param.default
            result[category_name] = category_dict
        return result

    def get_all_parameters(self) -> list[ConfigParameter]:
        """Get all parameters from all categories."""
        parameters = []
        for category in self._categories.values():
            parameters.extend(category.get_parameters())
        return parameters

    def get_cli_parameters(self) -> list[ConfigParameter]:
        """Get only CLI parameters."""
        cli_category = self.get_cli_category()
        if cli_category:
            return cli_category.get_parameters()
        return []


class DocumentationGenerator:
    """Generates documentation and configuration files from ConfigManager."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def generate_config_markdown_doc(self, output_file: str):
        """Generate Markdown documentation for all configuration parameters."""

        def pad(s, width):
            return s + " " * (width - len(s))

        markdown_content = dedent("""
            # Configuration Parameters

            These parameters are available to configure the behavior of your application.
            The parameters in the cli category can be accessed via the command line interface.

            """).lstrip()

        for category_name, category in self.config_manager._categories.items():
            markdown_content += f'## Category "{category_name}"\n\n'

            # Collect all parameters for this category
            rows = []
            header = ["Name", "Type", "Description", "Default", "Choices"]

            for param in category.get_parameters():
                name = param.name
                typ = param.type_.__name__
                desc = param.help
                default = repr(param.default)
                choices = str(param.choices) if param.choices else "-"

                rows.append((name, typ, desc, default, choices))

            if not rows:
                continue

            # Calculate column widths
            all_rows = [header] + rows
            widths = [max(len(str(col)) for col in column) for column in zip(*all_rows)]

            # Create Markdown table
            table = (
                "| "
                + " | ".join(pad(h, w) for h, w in zip(header, widths))
                + " |\n"
                + "|-"
                + "-|-".join("-" * w for w in widths)
                + "-|\n"
            )
            for row in rows:
                table += "| " + " | ".join(pad(str(col), w) for col, w in zip(row, widths)) + " |\n"

            markdown_content += table + "\n"

        # Write to file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

    def generate_default_config_file(self, output_file: str):
        """Generate a default configuration file with all parameters and descriptions."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Configuration File\n")
            f.write("# This file was auto-generated. Modify as needed.\n\n")

            for category_name, category in self.config_manager._categories.items():
                f.write(f"# {category_name.upper()} Configuration\n")
                f.write(f"{category_name}:\n")

                for param in category.get_parameters():
                    f.write(f"  # {param.help}\n")
                    if param.choices:
                        f.write(f"  # Choices: {param.choices}\n")
                    f.write(f"  # Type: {param.type_.__name__}\n")
                    f.write(f"  {param.name}: {repr(param.default)}\n\n")

                f.write("\n")

    def generate_cli_markdown_doc(self, output_file: str, app_name: str = "app"):
        """Generate Markdown CLI documentation."""
        cli_params = self.config_manager.get_cli_parameters()

        if not cli_params:
            return

        rows = []
        required_params = []
        optional_params = []

        for param in cli_params:
            cli_arg = f"`--{param.name}`" if not param.required else f"`{param.name}`"
            typ = param.type_.__name__
            desc = param.help
            default = (
                "*required*"
                if param.required or param.default in (None, "")
                else repr(param.default)
            )
            choices = str(param.choices) if param.choices else "-"

            rows.append((cli_arg, typ, desc, default, choices))
            if default == "*required*":
                required_params.append(param)
            else:
                optional_params.append(param)

        # Generate table
        def pad(s, width):
            return s + " " * (width - len(s))

        widths = [max(len(str(col)) for col in column) for column in zip(*rows)]
        header = ["Option", "Type", "Description", "Default", "Choices"]

        table = (
            "| "
            + " | ".join(pad(h, w) for h, w in zip(header, widths))
            + " |\n"
            + "|-"
            + "-|-".join("-" * w for w in widths)
            + "-|\n"
        )
        for row in rows:
            table += "| " + " | ".join(pad(str(col), w) for col, w in zip(row, widths)) + " |\n"

        # Generate examples
        examples = []
        required_arg = required_params[0].name if required_params else "example.input"

        examples.append(
            dedent(
                f"""
            ### 1. Basic usage

            ```bash
            python -m {app_name} {required_arg}
            ```
            """
            )
        )

        # Add more examples with optional parameters
        for i, param in enumerate(optional_params[:3], 2):
            if param.name in ["verbose", "quiet"]:
                continue
            example_value = param.choices[0] if param.choices else param.default
            examples.append(
                dedent(f"""
                ### {i}. With {param.name} parameter

                ```bash
                python -m {app_name} --{param.name} {example_value} {required_arg}
                ```
                """)
            )

        markdown = dedent(
            f"""
            # Command Line Interface

Command line options for {app_name}

```bash
python -m {app_name} [OPTIONS] {required_arg if required_params else ""}
```

## Options

{table}

## Examples

            {"".join(examples)}
            """
        ).strip()

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown)
