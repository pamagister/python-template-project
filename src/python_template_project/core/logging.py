"""Centralized logging configuration for python-template-project.

Provides file logging, console logging and an in-memory ring buffer that the
web UI can read to render recent log lines.
"""

import logging
import logging.handlers
import sys
from collections import deque
from pathlib import Path

from python_template_project.config.config import ConfigManager


class RingBufferHandler(logging.Handler):
    """Keep the most recent log records in memory for the web log view."""

    def __init__(self, capacity: int = 500) -> None:
        super().__init__()
        self.capacity = capacity
        self.records: deque[str] = deque(maxlen=capacity)
        self.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.records.append(self.format(record))
        except Exception:  # pragma: no cover - logging must never raise
            pass

    def recent(self, limit: int | None = None) -> list[str]:
        """Return the most recent log lines, oldest first."""
        if limit is None or limit >= len(self.records):
            return list(self.records)
        return list(self.records)[-limit:]


class LoggerManager:
    """Manages all logging configuration and handlers."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger("python_template_project")
        self.file_handler: logging.Handler | None = None
        self.console_handler: logging.Handler | None = None
        self.ring_handler = RingBufferHandler()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure all logging handlers and formatters."""
        self.logger.handlers.clear()

        app = self.config.category("app")
        log_level = app.get("log_level").value.upper() if app else "INFO"
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        simple_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        if app and app.get("enable_file_logging").value:
            self._setup_file_handler(detailed_formatter)
        if app and app.get("enable_console_logging").value:
            self._setup_console_handler(simple_formatter)

        self.logger.addHandler(self.ring_handler)

    def _setup_file_handler(self, formatter: logging.Formatter) -> None:
        """Setup rotating file handler."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "python_template_project.log"
        self.file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

    def _setup_console_handler(self, formatter: logging.Formatter) -> None:
        """Setup console handler for CLI output."""
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(formatter)
        self.logger.addHandler(self.console_handler)

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance."""
        if name:
            return logging.getLogger(f"python_template_project.{name}")
        return self.logger

    def set_log_level(self, level: str) -> None:
        """Change log level dynamically."""
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        app = self.config.category("app")
        if app and app.has("log_level"):
            app.get("log_level").value = level.upper()

    def recent_logs(self, limit: int | None = None) -> list[str]:
        """Return recent log lines from the in-memory ring buffer."""
        return self.ring_handler.recent(limit)


_logger_manager: LoggerManager | None = None


def initialize_logging(config: ConfigManager) -> LoggerManager:
    """Initialize the global logging system."""
    global _logger_manager
    _logger_manager = LoggerManager(config)
    return _logger_manager


def get_logger_manager() -> LoggerManager:
    """Return the global logger manager, raising if it was not initialized."""
    if _logger_manager is None:
        raise RuntimeError("Logging not initialized. Call initialize_logging() first.")
    return _logger_manager


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger instance from the global manager."""
    return get_logger_manager().get_logger(name)
