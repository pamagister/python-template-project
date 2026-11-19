"""Path helpers for source and export directories."""

from __future__ import annotations

from pathlib import Path


def default_pictures_dir() -> Path:
    """Return the OS-specific default pictures directory."""
    return Path.home() / "Pictures"


def resolve_output_root(value: str | Path | None) -> Path:
    """Resolve the configured output root, falling back to the pictures dir."""
    if value:
        return Path(value).expanduser()
    return default_pictures_dir()


def resolve_source_dir(value: str | Path | None) -> Path:
    """Resolve the configured source directory."""
    if value:
        return Path(value).expanduser()
    return default_pictures_dir()
