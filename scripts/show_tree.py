#!/usr/bin/env python3
import os
import re
from pathlib import Path

BASE_PATH = Path.cwd()

FOLDER_SYMBOL = "[D]"
FILE_SYMBOL = "[F]"

INDENT = "    "
BRANCH = "|-- "
LAST_BRANCH = "``-- "
VERTICAL = "|   "

# Paths or patterns to exclude (mirrors the PS1 script)
EXCLUDE_PATTERNS = [
    r"\.pytest_cache",
    r"\.git",
    r"\.ruff",
    r"\.venv",
    r"\.github",
    r"build",
    r"dist",
    r"\.idea",
    r"htmlcov",
    r"__pycache__",
    r"__main__",
    r"site",
    r"\.pyc$",
]

def is_excluded(path: Path) -> bool:
    full = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, full):
            return True
    return False


def show_tree(path: Path, prefix: str = ""):
    try:
        entries = [e for e in path.iterdir() if not is_excluded(e)]
    except PermissionError:
        return

    # Sort: directories first, then files (alphabetical)
    entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

    total = len(entries)
    for i, entry in enumerate(entries):
        is_last = (i == total - 1)

        connector = LAST_BRANCH if is_last else BRANCH
        symbol = FOLDER_SYMBOL if entry.is_dir() else FILE_SYMBOL

        print(f"{prefix}{connector}{symbol} {entry.name}")

        if entry.is_dir():
            next_prefix = prefix + (INDENT if is_last else VERTICAL)
            show_tree(entry, next_prefix)


def main():
    show_tree(BASE_PATH)


if __name__ == "__main__":
    main()
