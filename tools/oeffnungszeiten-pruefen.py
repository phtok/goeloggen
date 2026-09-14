#!/usr/bin/env python3
"""Wächter über die Öffnungszeiten des Campusplans.

Die Zeiten in apps/campusplan/gaeste.js stammen von fünf Seiten im Netz.
Dieses Skript holt den sichtbaren Text dieser Seiten, legt ihn als
Stand unter docs/oeffnungszeiten-stand/ ab und meldet, wenn sich seit dem
letzten Stand etwas geändert hat — dann ist gaeste.js von Hand zu prüfen.

  python3 tools/oeffnungszeiten-pruefen.py            # Stand neu schreiben
  python3 tools/oeffnungszeiten-pruefen.py --pruefen  # vergleichen; Abweichung → Exit 1

Der monatliche Lauf steht in .github/workflows/oeffnungszeiten-waechter.yml
und eröffnet bei Abweichung ein Issue mit dem Unterschied. Die Seiten mit
tagesaktuellen Ausnahmen (Grosser Saal, Glashaus) gehören NICHT hierher —
sie liest die Edge Function campusplan-ausnahmen live.

Ohne Fremdpakete: urllib, re, difflib.
"""

from __future__ import annotations

import difflib
import html
import pathlib
import re
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
STAND = REPO / "docs" / "oeffnungszeiten-stand"

QUELLEN = {
    "goetheanum-oeffnungszeiten": "https://goetheanum.ch/de/campus/oeffnungszeiten",
    "goetheanum-besuch": "https://goetheanum.ch/de/besuch",
    "buchhandlung": "https://www.goetheanum-buchhandlung.ch/pages/oeffnungszeiten",
    "bibliothek": "https://goetheanum.ch/en/documentation/library",
    "rudolf-steiner-archiv": "https://www.rudolf-steiner.com/",
    "speisehaus": "https://www.speisehaus.ch/",
}

# Zeilen, die Zeiten tragen: Uhrzeiten, Wochentage, «geschlossen», «täglich».
RELEVANT = re.compile(
    r"(\d{1,2}[.:]\d{2}|\d{1,2}\s*[-–]\s*\d{1,2}\s*Uhr|\bUhr\b|\b(Mo|Di|Mi|Do|Fr|Sa|So)\b\.?|"
    r"Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag|täglich|Täglich|geschlossen|"
    r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|daily|closed|\d\s*(am|pm)\b)"
)


def sichtbarer_text(seite: str) -> list[str]:
    t = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", seite, flags=re.I)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    zeilen = [re.sub(r"\s+", " ", z).strip() for z in t.split("\n")]
    return [z for z in zeilen if z]


def zeiten_zeilen(zeilen: list[str]) -> list[str]:
    # Nur Zeilen mit Zeitbezug plus ihre Vorgängerzeile (die Ortsangabe),
    # doppelte weg, Reihenfolge erhalten.
    aus: list[str] = []
    for i, z in enumerate(zeilen):
        if RELEVANT.search(z):
            if i and zeilen[i - 1] not in aus and not RELEVANT.search(zeilen[i - 1]):
                aus.append(zeilen[i - 1])
            if z not in aus:
                aus.append(z)
    return aus


def holen(url: str) -> str:
    anfrage = urllib.request.Request(url, headers={"User-Agent": "goetheanum-werkzeuge/oeffnungszeiten-waechter"})
    with urllib.request.urlopen(anfrage, timeout=40) as antwort:
        return antwort.read().decode("utf-8", errors="replace")


def main() -> int:
    pruefen = "--pruefen" in sys.argv
    STAND.mkdir(parents=True, exist_ok=True)
    abweichungen: list[str] = []
    for name, url in QUELLEN.items():
        try:
            neu = zeiten_zeilen(sichtbarer_text(holen(url)))
        except Exception as fehler:  # Netz, 5xx — melden, nicht abbrechen
            print(f"  ! {name}: {fehler}")
            abweichungen.append(f"{name}: nicht erreichbar ({fehler})")
            continue
        datei = STAND / f"{name}.txt"
        alt = datei.read_text(encoding="utf-8").splitlines() if datei.exists() else []
        if pruefen:
            if neu != alt:
                diff = "\n".join(difflib.unified_diff(alt, neu, "bisher", "jetzt", lineterm=""))
                abweichungen.append(f"{name} ({url}):\n{diff}")
                print(f"  ≠ {name}: geändert")
            else:
                print(f"  = {name}: unverändert")
        else:
            datei.write_text("\n".join(neu) + "\n", encoding="utf-8")
            print(f"  ✓ {name}: {len(neu)} Zeilen")
    if pruefen and abweichungen:
        bericht = REPO / "oeffnungszeiten-abweichungen.md"
        bericht.write_text(
            "# Öffnungszeiten: Abweichungen zum letzten Stand\n\n"
            "Bitte `apps/campusplan/gaeste.js` prüfen und danach den Stand neu schreiben "
            "(`python3 tools/oeffnungszeiten-pruefen.py`).\n\n```diff\n"
            + "\n\n".join(abweichungen) + "\n```\n",
            encoding="utf-8",
        )
        print(f"\n{len(abweichungen)} Abweichung(en) — Bericht: {bericht}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
