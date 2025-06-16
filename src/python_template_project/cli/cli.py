"""Auto-generated CLI interface for python_template_project project.

This file was generated from config.py parameter definitions.
Do not modify manually - regenerate using ConfigParameterManager CLI generation methods.
"""

import argparse
from pathlib import Path
from typing import Any

from ..config.config import ConfigParameterManager
from ..core.base import PythonProject


def parse_arguments():
    """Parse command line arguments with config file support."""
    parser = argparse.ArgumentParser(
        description="Process input files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m python_template_project.cli input.txt
  python -m python_template_project.cli --output result.txt input.txt
  python -m python_template_project.cli --config custom_config.yaml input.txt
        """,
    )

    # Config file argument
    parser.add_argument(
        "--config",
        default=None,
        help="Path to configuration file (JSON or YAML)",
    )

    # Get CLI parameters from ConfigParameterManager
    config_manager = ConfigParameterManager()
    cli_params = config_manager.get_cli_parameters()

    # Generate arguments from CLI config parameters
    for param in cli_params:
        if param.required and param.cli_arg is None:
            # Positional argument (like 'input')
            parser.add_argument(param.name, help=param.help)
        else:
            # Optional argument
            kwargs = {
                "default": argparse.SUPPRESS,  # Don't set default here, handle in config
                "help": f"{param.help} (default: {param.default})",
            }

            # Handle different parameter types
            if param.choices:
                kwargs["choices"] = param.choices

            if param.type_ == int:
                kwargs["type"] = int
            if param.type_ == float:
                kwargs["type"] = float
            elif param.type_ == bool:
                kwargs["action"] = "store_true" if not param.default else "store_false"
                kwargs["help"] = f"{param.help} (default: {param.default})"
            elif param.type_ == str:
                kwargs["type"] = str

            parser.add_argument(param.cli_arg, **kwargs)

    return parser.parse_args()


def create_config_overrides(args: argparse.Namespace) -> dict[str, Any]:
    """Create configuration overrides from CLI arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Dictionary with CLI parameter overrides in format cli__parameter_name
    """
    config_manager = ConfigParameterManager()
    cli_params = config_manager.get_cli_parameters()
    overrides = {}

    for param in cli_params:
        if hasattr(args, param.name):
            arg_value = getattr(args, param.name)
            # Add CLI category prefix for override system
            overrides[f"cli__{param.name}"] = arg_value

    return overrides


def validate_config(config: ConfigParameterManager) -> bool:
    """Validate the configuration parameters.

    Args:
        config: Configuration manager instance

    Returns:
        True if configuration is valid, False otherwise
    """
    # Check required parameters
    if not config.cli.input.default:
        print("Error: input is required")
        return False

    # Check if input file exists
    input_path = Path(config.cli.input.default)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}")
        return False

    return True


def main():
    """Main entry point for the CLI application."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Create configuration overrides from CLI arguments
        cli_overrides = create_config_overrides(args)

        # Create config object with file and CLI overrides
        config = ConfigParameterManager(
            config_file=args.config if hasattr(args, "config") and args.config else None,
            **cli_overrides,
        )

        # Validate configuration
        if not validate_config(config):
            return 1

        # Create and run PythonProject
        project = PythonProject(config)
        project.convert()

        print(f"Successfully processed: {config.cli.input.default}")
        if config.cli.output.default:
            print(f"Output written to: {config.cli.output.default}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
