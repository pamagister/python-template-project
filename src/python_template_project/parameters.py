"""Central configuration management for python_template_project project.

This module provides a single source of truth for all configuration parameters.
It can generate config files, CLI modules, and documentation from the parameter definitions.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigParameter:
    """Represents a single configuration parameter with all its metadata."""

    name: str
    default: Any
    type_: type
    choices: list[str | bool] | None = None
    help: str = ""
    cli_arg: str | None = None
    required: bool = False
    is_cli: bool = True

    def __post_init__(self):
        if self.is_cli and self.cli_arg is None:
            self.cli_arg = f"--{self.name}"


"""Central configuration class for python_template_project.

All parameters are defined here as class attributes with their metadata.
This serves as the single source of truth for configuration management.
"""
POSITIONAL_ARGUMENT = "input"
PARAMETERS = [
    ConfigParameter(
        name=POSITIONAL_ARGUMENT,
        default="",
        type_=str,
        help=f"Path to {POSITIONAL_ARGUMENT} (file or folder)",
        required=True,
        cli_arg=None,  # Positional argument
    ),
    ConfigParameter(
        name="output",
        default="",
        type_=str,
        help="Path to output destination",
    ),
    ConfigParameter(
        name="min_dist",
        default=20,
        type_=int,
        help="maximum distance between two waypoints",
    ),
    ConfigParameter(
        name="extract_waypoints",
        default=True,
        type_=bool,
        choices=[True, False],
        help="extract starting points of each track as waypoint",
    ),
    ConfigParameter(
        name="date_format",
        default="%Y-%m-%d",
        type_=str,
        help="Date format to use",
        is_cli=False,
    ),
]
