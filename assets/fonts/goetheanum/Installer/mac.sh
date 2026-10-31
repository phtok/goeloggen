#!/bin/bash
# Goetheanum-Schriften installieren (Mac)
#
# Entfernt alle früheren Goetheanum-Schriften und installiert die aktuelle
# Fassung: das Office-Set (Goetheanum Schrift, Ruhig, Deutlich, Icons, Pfeile),
# auf Wunsch dazu die variable Schrift für die Gestaltung.
#
# Für alle (pro Benutzer, ohne Adminrechte), im Terminal:
#   curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash
# Mit variabler Schrift:
#   curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash -s -- --variabel
#
# Für die IT (als root, für alle Benutzer des Geräts):
#   sudo bash mac.sh --alle [--variabel] [--quelle <entpackter Ordner Goetheanum-Schriften-v2.9>]
#
# Exit-Codes: 0 fertig · 1 Fehler (Download, Datei gesperrt) ·
#             2 alte Fassung für alle Benutzer gefunden, Löschen abgelehnt
#
# Die Dateiliste folgt assets/fonts/goetheanum/Office und Variable – bei neuer
# Fassung hier mitziehen (CLAUDE-REF.md § Schnitt-System).
# Läuft mit dem bash 3.2 von macOS: keine assoziativen Arrays, kein mapfile.

set -u

FASSUNG=2.9
BASIS=https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum
SCHRIFTEN="Office/GoetheanumSchriftKlar.ttf
Office/GoetheanumSchriftLaut.ttf
Office/GoetheanumSchriftLeise.ttf
Office/GoetheanumSchriftRuhig.ttf
Office/GoetheanumSchriftDeutlich.ttf
Office/GoetheanumIcons.ttf
Office/GoetheanumPfeile.ttf"

NUTZER_ORDNER="${GOETHEANUM_NUTZER_ORDNER:-$HOME/Library/Fonts}"
SYSTEM_ORDNER="${GOETHEANUM_SYSTEM_ORDNER:-/Library/Fonts}"
PROFIL_WURZEL="${GOETHEANUM_PROFIL_WURZEL:-/Users}"

# Programme, die Schriften festhalten
PROGRAMME='/Contents/MacOS/(Microsoft (Word|PowerPoint|Excel|Outlook|OneNote)|Adobe (InDesign|Illustrator|Photoshop|Acrobat)|Affinity|Keynote|Pages|Numbers|Figma)'

VARIABEL=0; ALLE=0; QUELLE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --variabel) VARIABEL=1 ;;
    --alle) ALLE=1 ;;
    --quelle) QUELLE="${2:-}"; shift ;;
    *) echo "Unbekannte Angabe: $1" >&2; exit 1 ;;
  esac
  shift
done
[ "$VARIABEL" = 1 ] && SCHRIFTEN="$SCHRIFTEN
Variable/Goetheanum-Variabel-v$FASSUNG.otf"

melde() { printf '  %s\n' "$1"; }
halt() { printf '\n  %s\n\n' "$1" >&2; rm -rf "${TMP:-}"; exit "$2"; }

# Rückfragen gehen ans Terminal, auch wenn das Skript über curl | bash läuft
if [ -r /dev/tty ] && [ -w /dev/tty ] && { : < /dev/tty; } 2>/dev/null; then
  INTERAKTIV=1
else
  INTERAKTIV=0
fi
frage() { printf '  %s' "$1" > /dev/tty; read -r ANTWORT < /dev/tty; }

# Alte Goetheanum-Schriften in einem Ordner (auch in Unterordnern)
finde_alte() {
  [ -d "$1" ] || return 0
  find "$1" -maxdepth 3 -type f -iname '*goetheanum*' \
    \( -iname '*.ttf' -o -iname '*.otf' -o -iname '*.ttc' -o -iname '*.dfont' \) 2>/dev/null
}

entferne() { # $1 = Befehlspräfix ("" oder "sudo"), Dateien auf stdin
  local f
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if $1 rm -f "$f" 2>/dev/null && [ ! -e "$f" ]; then
      melde "entfernt: $(basename "$f")"
    else
      GESPERRT="$GESPERRT
$f"
    fi
  done
}

echo
melde "Goetheanum-Schriften $FASSUNG installieren"
echo

if [ "$ALLE" = 1 ] && [ "$(id -u)" != 0 ]; then
  halt 'Für alle Benutzer braucht es Adminrechte: mit sudo starten.' 1
fi

# 1. Laden, bevor irgendetwas gelöscht wird
TMP="$(mktemp -d "${TMPDIR:-/tmp}/goetheanum.XXXXXX")" || halt 'Kein temporärer Ordner.' 1
for datei in $SCHRIFTEN; do
  ziel="$TMP/$(basename "$datei")"
  if [ -n "$QUELLE" ]; then
    cp "$QUELLE/$datei" "$ziel" 2>/dev/null || halt "Nicht gefunden: $QUELLE/$datei. Nichts wurde verändert." 1
  else
    curl -fsSL --retry 2 -o "$ziel" "$BASIS/$datei" || halt "Laden fehlgeschlagen: $datei. Nichts wurde verändert." 1
  fi
  [ "$(wc -c < "$ziel")" -gt 1000 ] || halt "Unvollständig: $datei. Nichts wurde verändert." 1
done
melde 'Schriften geladen.'

# 2. Offene Programme schliessen lassen
offen() { ps -axo comm= 2>/dev/null | grep -E "$PROGRAMME" | sed 's#.*/##' | sort -u; }
if [ "$INTERAKTIV" = 1 ]; then
  while [ -n "$(offen)" ]; do
    echo
    melde 'Bitte zuerst beenden (sie halten die alten Schriften fest):'
    offen | while IFS= read -r p; do melde "  – $p"; done
    frage 'Danach Return drücken. '
  done
fi

# 3. Alte Fassungen entfernen
GESPERRT=""
ALT_NUTZER="$(finde_alte "$NUTZER_ORDNER")"
ALT_SYSTEM="$(finde_alte "$SYSTEM_ORDNER")"
if [ "$ALLE" = 1 ]; then
  for profil in "$PROFIL_WURZEL"/*; do
    [ "$profil/Library/Fonts" = "$NUTZER_ORDNER" ] && continue
    weitere="$(finde_alte "$profil/Library/Fonts")"
    [ -n "$weitere" ] && ALT_NUTZER="$ALT_NUTZER
$weitere"
  done
fi

if [ -z "$ALT_NUTZER$ALT_SYSTEM" ]; then
  melde 'Keine alte Fassung gefunden.'
fi
entferne "" <<< "$ALT_NUTZER"

if [ -n "$ALT_SYSTEM" ]; then
  if [ "$(id -u)" = 0 ]; then
    entferne "" <<< "$ALT_SYSTEM"
  elif [ "$INTERAKTIV" = 1 ]; then
    echo
    melde 'Eine alte Fassung ist für alle Benutzer installiert:'
    printf '%s\n' "$ALT_SYSTEM" | while IFS= read -r f; do melde "  – $(basename "$f")"; done
    melde 'Zum Entfernen fragt der Mac jetzt nach deinem Anmelde-Passwort'
    melde '(beim Tippen erscheinen keine Zeichen).'
    sudo -v < /dev/tty || halt 'Ohne Passwort bleibt die alte Fassung. Bitte die IT fragen.' 2
    entferne sudo <<< "$ALT_SYSTEM"
  else
    halt 'Alte Fassung für alle Benutzer gefunden; Entfernen braucht Adminrechte.' 2
  fi
fi

if [ -n "$GESPERRT" ]; then
  melde 'Diese Dateien liessen sich nicht entfernen:'
  printf '%s\n' "$GESPERRT" | while IFS= read -r f; do [ -n "$f" ] && melde "  – $(basename "$f")"; done
  halt 'Bitte den Mac neu starten und den Befehl gleich danach wiederholen.' 1
fi

# 4. Neue Fassung installieren
if [ "$ALLE" = 1 ]; then ordner="$SYSTEM_ORDNER"; else ordner="$NUTZER_ORDNER"; fi
mkdir -p "$ordner" || halt "Ordner fehlt: $ordner" 1
for datei in $SCHRIFTEN; do
  name="$(basename "$datei")"
  cp "$TMP/$name" "$ordner/$name" || halt "Kopieren fehlgeschlagen: $name" 1
  chmod 644 "$ordner/$name"
  melde "installiert: $name"
done
rm -rf "$TMP"

echo
melde "Fertig: Goetheanum-Schriften $FASSUNG sind installiert."
melde 'Word, PowerPoint und Co. jetzt (neu) starten.'
echo
exit 0
