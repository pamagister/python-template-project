#!/usr/bin/env bash
#
# Mirrors AGENTS_GLOBAL.md from the repository into the global OpenCode
# configuration file.
#
# Copies AGENTS_GLOBAL.md (source, relative to repository root) to
# $HOME/.config/opencode/AGENTS.md (target, overridable via
# OPENCODE_AGENTS_FILE).
#
# An existing target file is replaced before copying. All other files in the
# global OpenCode directory remain untouched. The script is idempotent.
set -euo pipefail

# Repository root (independent of invocation directory).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE_FILE="$REPO_ROOT/AGENTS_GLOBAL.md"
TARGET_FILE="${OPENCODE_AGENTS_FILE:-$HOME/.config/opencode/AGENTS.md}"

if [[ ! -f "$SOURCE_FILE" ]]; then
  echo "Error: source file not found: $SOURCE_FILE" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_FILE")"

cp -f "$SOURCE_FILE" "$TARGET_FILE"
echo "Mirrored: $SOURCE_FILE -> $TARGET_FILE"
