"""Generate the default config file and the config/CLI Markdown docs."""

from python_template_project.cli.cli import build_parser
from python_template_project.cli.docgen import generate_cli_markdown
from python_template_project.config.config import build_default_config
from python_template_project.config.docgen import (
    generate_config_markdown,
    generate_default_config_file,
)

DEFAULT_CONFIG = "config.yaml"
DEFAULT_CLI_DOC = "docs/usage/cli.md"
DEFAULT_CONFIG_DOC = "docs/usage/config.md"


def main() -> None:
    """Generate all derived configuration artifacts."""
    config = build_default_config()

    generate_default_config_file(config, DEFAULT_CONFIG)
    print(f"Generated: {DEFAULT_CONFIG}")

    generate_config_markdown(config, DEFAULT_CONFIG_DOC)
    print(f"Generated: {DEFAULT_CONFIG_DOC}")

    generate_cli_markdown(
        build_parser(config), DEFAULT_CLI_DOC, app_name=config.get_app_name()
    )
    print(f"Generated: {DEFAULT_CLI_DOC}")


if __name__ == "__main__":
    main()