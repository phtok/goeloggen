#!/bin/bash
# =============================================================================
# SessionStart-Hook · Goetheanum-Werkzeuge
# -----------------------------------------------------------------------------
# Macht jede frische Claude-Code-Session sofort startklar – vor allem im Web
# (claude.ai/code), wo das Repo frisch geklont ist:
#
#   · Aktiviert den Prüf-Hook (git core.hooksPath tools/hooks). Danach laufen
#     tools/typo-check.py (Sprache) UND tools/ds-lint.py (Gestalt) bei JEDEM
#     Commit – genau wie CLAUDE.md verlangt. Diese Einstellung wohnt je
#     Arbeitskopie und wird NICHT mitversioniert, muss also je Session gesetzt
#     werden.
#
# Keine Installationen nötig: die Prüfmaschinen sind reines python3
# (Standardbibliothek). Der Schritt ist idempotent und harmlos – auch lokal.
# =============================================================================
set -euo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}"

# 1) Hausregeln beim Commit erzwingen.
git config core.hooksPath tools/hooks
chmod +x tools/hooks/pre-commit 2>/dev/null || true

# 2) Kurzer Selbsttest – laufen die Prüfmaschinen? (informativ, nie blockierend)
if command -v python3 >/dev/null 2>&1; then
  echo "Goetheanum-Werkzeuge bereit: Prüf-Hook aktiv – typo-check + ds-lint prüfen jeden Commit. Neue Seiten aus design-system/starter.html bauen, Eintrag in tools.json."
else
  echo "Hinweis: python3 nicht gefunden – die Prüfmaschinen (typo-check/ds-lint) können nicht laufen; bitte python3 bereitstellen."
fi
