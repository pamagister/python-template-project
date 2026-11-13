#!/usr/bin/env bash
#
# Mirrors the OpenCode workflow skills from the repository into the global
# OpenCode skills directory.
#
# Copies exactly:
#   git-workflow, mission-planning, workflow-core, workflow-task,
#   workflow-feature, workflow-autopilot
#
# from .agents/skills/ (source, relative to repository root) to
# /home/paul/.config/opencode/skills/ (target, overridable via
# OPENCODE_SKILLS_DIR).
#
# Same-named existing skills in the target are removed before copying and
# copied fresh; all other global skills remain untouched. Legacy skill names
# are removed from the target. The script is idempotent.
set -euo pipefail

# Repository root (independent of invocation directory).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE_DIR="$REPO_ROOT/.agents/skills"
TARGET_DIR="${OPENCODE_SKILLS_DIR:-/home/paul/.config/opencode/skills}"

# The skills to mirror (order arbitrary, exactly these six).
SKILLS=(
  git-workflow
  mission-planning
  workflow-core
  workflow-task
  workflow-feature
  workflow-autopilot
)

# Skills that were consolidated away and must not remain in the target.
LEGACY_SKILLS=(
  workflow-standard
)

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: source not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

for skill in "${LEGACY_SKILLS[@]}"; do
  if [[ -e "$TARGET_DIR/$skill" ]]; then
    rm -rf "$TARGET_DIR/$skill"
    echo "Removed legacy skill: $skill"
  fi
done

for skill in "${SKILLS[@]}"; do
  if [[ ! -d "$SOURCE_DIR/$skill" ]]; then
    echo "Error: skill not found in source: $skill" >&2
    exit 1
  fi

  # Remove existing same-named skill in target completely, then copy fresh
  # (idempotent, other skills remain untouched).
  rm -rf "$TARGET_DIR/$skill"
  cp -r "$SOURCE_DIR/$skill" "$TARGET_DIR/$skill"
  echo "Mirrored: $skill -> $TARGET_DIR/$skill"
done

echo "Done: ${#SKILLS[@]} skills mirrored to $TARGET_DIR"
