"""Central configuration management for python_template_project project.

This module provides a single source of truth for all configuration parameters.
It can generate config files, CLI modules, and documentation from the parameter definitions.
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ConfigParameter:
    """Represents a single configuration parameter with all its metadata."""

    name: str
    default: Any
    type_: type
    choices: Optional[List[str | bool]] = None
    help: str = ""
    cli_arg: Optional[str] = None
    required: bool = False
    is_cli: bool = True

    def __post_init__(self):
        if self.cli_arg is None:
            self.cli_arg = f"--{self.name}"


"""Central configuration class for python_template_project.

All parameters are defined here as class attributes with their metadata.
This serves as the single source of truth for configuration management.
"""
PARAMETERS = [
    ConfigParameter(
        name="sent_from",
        default=True,
        type_=bool,
        choices=[True, False],
        help="Include 'From' field",
    ),
    ConfigParameter(
        name="to",
        default=True,
        type_=bool,
        choices=[True, False],
        help="Include 'To' field",
    ),
    ConfigParameter(
        name="date",
        default=True,
        type_=bool,
        choices=[True, False],
        help="Include 'Date' field",
    ),
    ConfigParameter(
        name="subject",
        default=True,
        type_=bool,
        choices=[True, False],
        help="Include 'Subject' field",
    ),
    ConfigParameter(
        name="format",
        default="txt",
        type_=str,
        choices=["txt", "csv"],
        help="Output format: txt or csv",
    ),
    ConfigParameter(
        name="max_days",
        default=-1,
        type_=int,
        help="Max number of days per output file (-1 for unlimited)",
    ),
    ConfigParameter(
        name="mbox_file",
        default="",
        type_=str,
        help="Path to mbox file",
        required=True,
        cli_arg=None,  # Positional argument
    ),
    ConfigParameter(
        name="date_format",
        default="%Y-%m-%d",
        type_=str,
        help="Date format to use",
        is_cli=False,
    ),
]
