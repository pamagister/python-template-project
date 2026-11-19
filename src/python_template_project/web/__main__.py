"""Web UI entry point for ``python -m python_template_project.web``."""

import sys

from python_template_project.config.config import build_default_config
from python_template_project.web.server import run_server

if __name__ == "__main__":  # pragma: no cover
    sys.exit(run_server(build_default_config()))
