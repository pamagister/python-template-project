#!/usr/bin/env bash

# Hilfsfunktion für Fehlermeldungen und Beenden
function die { echo "$*" >&2; exit 1; }

echo "Initializing project from template..."

# 1. Repository-Informationen ermitteln
# Beachte: repo_name wird zu snake_case, repo_urlname bleibt kebab-case (oder wie im Repo-Namen)
# Diese Logik spiegelt die Erwartungen deines rename_project.sh wider.
REPO_BASE_NAME=$(basename -s .git `git config --get remote.origin.url`)
NEW_PACKAGE_NAME=$(echo "$REPO_BASE_NAME" | tr '-' '_') # Für interne Python-Paketnamen (snake_case)
NEW_PROJECT_NAME=$(echo "$REPO_BASE_NAME" | tr '_' '-') # Für externe Projektnamen (kebab-case)
REPOSITORY_OWNER=$(git config --get remote.origin.url | awk -F ':' '{print $2}' | awk -F '/' '{print $1}')
DESCRIPTION="Feature-rich Python project created by ${REPOSITORY_OWNER}." # Standardbeschreibung

echo "Repository Owner: ${REPOSITORY_OWNER}"
echo "New Python Package Name (internal): ${NEW_PACKAGE_NAME}"
echo "New Project Name (external/PyPI): ${NEW_PROJECT_NAME}"
echo "Project Description: ${DESCRIPTION}"

# 2. Aufrufen des Umbenennungsskripts
# Dies ist der Kern der Funktionalität, die du behalten möchtest.
# Es wird überprüft, ob das rename_project.sh Skript existiert.
if [ -f ".github/rename_project.sh" ]; then
    echo "Running rename_project.sh..."
    .github/rename_project.sh \
        -a "${REPOSITORY_OWNER}" \
        -p "${NEW_PACKAGE_NAME}" \
        -n "${NEW_PROJECT_NAME}" \
        -d "${DESCRIPTION}"
else
    die "Error: .github/rename_project.sh not found. Cannot rename project."
fi

# 3. Aufräumarbeiten
# Die template.yml sollte nach erfolgreicher Umbenennung entfernt werden.
# Dies signalisiert, dass das Template angewendet wurde.
if [ -f ".github/template.yml" ]; then
    echo "Removing .github/template.yml"
    rm -f .github/template.yml
fi

echo "Project initialization complete! Review, commit, and push your changes."