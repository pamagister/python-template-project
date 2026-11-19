"""Unified entry point for the CLI and web UI application.

The installed ``python-template-project`` console script points here. When
started without arguments the web UI is launched; when arguments are present
the argparse CLI handles the invocation.
"""

import sys

from python_template_project.cli.cli import gui_main
from python_template_project.cli.cli import main as cli_main


def main() -> int:
    """Dispatch to the web UI (no arguments) or the CLI (with arguments)."""
    if len(sys.argv) > 1:
        return cli_main()
    return gui_main()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
