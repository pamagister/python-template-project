# generic_config_cli_gui/cli.py
"""Generic CLI generator for configuration framework."""

import argparse
import traceback
from collections.abc import Callable
from typing import Any

from generic_config_cli_gui.config_framework import ConfigManager


class CliGenerator:
    """Generates CLI interface from ConfigManager."""

    def __init__(self, config_manager: ConfigManager, app_name: str = "app"):
        self.config_manager = config_manager
        self.app_name = app_name

    def create_argument_parser(self, description: str = None) -> argparse.ArgumentParser:
        """Create argument parser from configuration."""
        if description is None:
            description = f"Command line interface for {self.app_name}"

        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Config file argument
        parser.add_argument(
            "--config",
            default=None,
            help="Path to configuration file (JSON or YAML)",
        )

        # Verbose/quiet options for log level override
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)"
        )
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Enable quiet mode (WARNING level only)"
        )

        # Get CLI parameters
        cli_params = self.config_manager.get_cli_parameters()

        # Generate arguments from CLI config parameters
        for param in cli_params:
            if param.required and param.cli_arg is None:
                # Positional argument
                parser.add_argument(param.name, help=param.help)
            else:
                # Optional argument
                kwargs = {
                    "default": argparse.SUPPRESS,
                    "help": f"{param.help} (default: {param.default})",
                }

                # Handle different parameter types
                if param.choices and param.type_ != bool:
                    kwargs["choices"] = param.choices

                if param.type_ == int:
                    kwargs["type"] = int
                elif param.type_ == float:
                    kwargs["type"] = float
                elif param.type_ == bool:
                    kwargs["action"] = "store_true" if not param.default else "store_false"
                    kwargs["help"] = f"{param.help} (default: {param.default})"
                elif param.type_ == str:
                    kwargs["type"] = str

                parser.add_argument(param.cli_arg, **kwargs)

        return parser

    def create_config_overrides(self, args: argparse.Namespace) -> dict[str, Any]:
        """Create configuration overrides from CLI arguments."""
        cli_params = self.config_manager.get_cli_parameters()
        overrides = {}

        for param in cli_params:
            if hasattr(args, param.name):
                arg_value = getattr(args, param.name)
                # Add CLI category prefix for override system
                overrides[f"cli__{param.name}"] = arg_value

        # Handle log level overrides from verbose/quiet flags
        if hasattr(args, "verbose") and args.verbose:
            overrides["app__log_level"] = "DEBUG"
        elif hasattr(args, "quiet") and args.quiet:
            overrides["app__log_level"] = "WARNING"

        return overrides

    def run_cli(
        self,
        main_function: Callable[[ConfigManager], int],
        description: str = None,
        validator: Callable[[ConfigManager], bool] = None,
    ) -> int:
        """Run the CLI application with error handling.

        Args:
            main_function: Function that takes ConfigManager and returns exit code
            description: CLI description
            validator: Optional function to validate configuration

        Returns:
            Exit code
        """
        logger = None

        try:
            # Parse command line arguments
            parser = self.create_argument_parser(description)
            args = parser.parse_args()

            # Create configuration overrides from CLI arguments
            cli_overrides = self.create_config_overrides(args)

            # Create new config manager with overrides
            config_file = args.config if hasattr(args, "config") and args.config else None
            updated_config = ConfigManager(config_file=config_file, **cli_overrides)

            # Copy categories from original config manager
            for name, category in self.config_manager._categories.items():
                updated_config.add_category(name, category)

            # Apply overrides again after copying categories
            updated_config._apply_kwargs(cli_overrides)

            # Try to get logger if logging is configured
            try:
                from .logging import get_logger

                logger = get_logger(f"{self.app_name}.cli")
                logger.info(f"Starting {self.app_name} CLI")
                logger.debug(f"Command line arguments: {vars(args)}")
            except ImportError:
                pass

            # Validate configuration if validator provided
            if validator and not validator(updated_config):
                if logger:
                    logger.error("Configuration validation failed")
                else:
                    print("Configuration validation failed")
                return 1

            # Run main function
            return main_function(updated_config)

        except FileNotFoundError as e:
            if logger:
                logger.error(f"File not found: {e}")
                logger.debug("Full traceback:", exc_info=True)
            else:
                print(f"Error: {e}")
                traceback.print_exc()
            return 1

        except KeyboardInterrupt:
            if logger:
                logger.warning("Process interrupted by user")
            else:
                print("Process interrupted by user")
            return 130

        except Exception as e:
            if logger:
                logger.error(f"Unexpected error: {e}")
                logger.debug("Full traceback:", exc_info=True)
            else:
                print(f"Unexpected error: {e}")
                traceback.print_exc()
            return 1
