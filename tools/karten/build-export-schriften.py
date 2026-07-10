#!/usr/bin/env python3
"""Baut die statischen Export-Schnitte für das Kartentool.

Quelle:  assets/fonts/goetheanum/Fallback/SourceSans3-Variable.ttf
Ziel:    apps/karten-generator/assets/fonts/SourceSans3-SemiBold.ttf

Der Vektor-PDF-Export (jsPDF) kann nur statische TrueType-Schnitte
einbetten. Source Sans 3 trägt auf der Karte Werte und Badges
(Markernummern, Treppen-Buchstaben, Gebäudenamen, Kompass) — gemäss
Hausregel ‹Label/Wert/Badge = Lese-Grotesk›; die Beispielkarten setzten
dafür die damalige Grotesk (Titillium Bold/Semibold).

Idempotent. Benötigt: pip install fonttools
"""

from __future__ import annotations

import pathlib
import sys

from fontTools import varLib  # noqa: F401 — klare Fehlermeldung, falls fontTools fehlt
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

REPO = pathlib.Path(__file__).resolve().parents[2]
QUELLE = REPO / "assets/fonts/goetheanum/Fallback/SourceSans3-Variable.ttf"
ZIEL = REPO / "apps/karten-generator/assets/fonts/SourceSans3-SemiBold.ttf"
GEWICHT = 600  # SemiBold


def main() -> int:
    if not QUELLE.exists():
        print(f"Quelle fehlt: {QUELLE}", file=sys.stderr)
        return 1
    schrift = TTFont(QUELLE)
    instantiateVariableFont(schrift, {"wght": GEWICHT}, inplace=True)
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    schrift.save(ZIEL)
    print(f"geschrieben: {ZIEL.relative_to(REPO)} ({ZIEL.stat().st_size // 1024} KB, wght={GEWICHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
