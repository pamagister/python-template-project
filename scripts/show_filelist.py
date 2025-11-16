#!/usr/bin/env python3
import os
import re
from pathlib import Path

EXCLUDE_PATTERN = re.compile(
    r"""
    (\.pytest_cache)|
    (\.git)|
    (\.ruff)|
    (\.venv)|
    (\.github)|
    ([/\\]build)|
    ([/\\]dist)|
    (\.idea)|
    ([/\\]htmlcov)|
    ([/\\]__pycache__)|
    ([/\\]__main__)|
    ([/\\]__init__)|
    ([/\\]site)|
    (\.pyc$)
    """,
    re.VERBOSE,
)

def should_exclude(path: Path) -> bool:
    return bool(EXCLUDE_PATTERN.search(str(path)))


def main():
    base_path = Path.cwd()

    for root, dirs, files in os.walk(base_path):
        all_entries = dirs + files

        for name in all_entries:
            full_path = Path(root) / name

            # apply exclusion filter
            if should_exclude(full_path):
                continue

            # compute relative path
            rel = str(full_path.relative_to(base_path))

            # match PowerShell behavior: always start with "\"
            print("\\" + rel.replace("/", "\\"))


if __name__ == "__main__":
    main()
