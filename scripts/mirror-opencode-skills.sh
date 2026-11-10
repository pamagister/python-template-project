#!/usr/bin/env bash
#
# Spiegelt die vier Opencode-Skills aus dem Repository nach dem globalen
# Opencode-Skills-Verzeichnis.
#
# Kopiert exakt:
#   git-workflow, mission-planning, workflow-autopilot, workflow-standard
#
# aus .agents/skills/ (Quelle, relativ zum Repository-Root) nach
# /home/paul/.config/opencode/skills/ (Ziel, über OPENCODE_SKILLS_DIR
# überschreibbar).
#
# Bestehende gleichnamige Skills im Ziel werden vor dem Kopieren entfernt und
# frisch kopiert; alle anderen globalen Skills bleiben unangetastet. Das Skript
# ist idempotent.
set -euo pipefail

# Repository-Root (unabhaengig vom Aufrufverzeichnis).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE_DIR="$REPO_ROOT/.agents/skills"
TARGET_DIR="${OPENCODE_SKILLS_DIR:-/home/paul/.config/opencode/skills}"

# Die vier zu spiegelnden Skills (Reihenfolge beliebig, exakt diese vier).
SKILLS=(
  git-workflow
  mission-planning
  workflow-autopilot
  workflow-standard
)

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Fehler: Quelle nicht gefunden: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

for skill in "${SKILLS[@]}"; do
  if [[ ! -d "$SOURCE_DIR/$skill" ]]; then
    echo "Fehler: Skill nicht in Quelle gefunden: $skill" >&2
    exit 1
  fi

  # Vorhandenes gleichnamiges Skill im Ziel komplett entfernen, dann frisch
  # kopieren (idempotent, andere Skills bleiben unberuehrt).
  rm -rf "$TARGET_DIR/$skill"
  cp -r "$SOURCE_DIR/$skill" "$TARGET_DIR/$skill"
  echo "Spiegelt: $skill -> $TARGET_DIR/$skill"
done

echo "Fertig: ${#SKILLS[@]} Skills gespiegelt nach $TARGET_DIR"
