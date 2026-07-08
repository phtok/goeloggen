#!/usr/bin/env python3
"""Baut die Vektor-Geländekarte für das Kartentool.

Quelle:  assets/maps/src/Gelaende_jo_ergaenzt-2022.ai  (PDF-1.6-kompatibel,
         Stand Dezember 2021/2022, von grafik.goetheanum.ch/kartierung)
Ziel:    apps/karten-generator/assets/gelaende.svg

Was passiert:
- Die AI-Datei wird via PyMuPDF als Vektor-SVG ausgespielt (355×230 mm,
  1006.3×651.968 pt, keine Rasterbilder).
- Die Füllfarben der Karte werden zu benannten Rollen gebündelt; jede Rolle
  wird eine CSS-Klasse mit Custom-Property (--karte-…), damit die Grundfarben
  je Kartenvariante umgefärbt werden können.
- Die Parkflächen (Füllung #e7e7e7) erhalten einzeln IDs (parkflaeche-N,
  West→Ost sortiert), damit einzelne Flächen eingefärbt werden können.

Idempotent: gleiche Quelle -> gleiches Ergebnis. Benötigt: pip install pymupdf
"""

from __future__ import annotations

import pathlib
import re
import sys

import fitz  # PyMuPDF

REPO = pathlib.Path(__file__).resolve().parents[2]
QUELLE = REPO / "assets/maps/src/Gelaende_jo_ergaenzt-2022.ai"
ZIEL = REPO / "apps/karten-generator/assets/gelaende.svg"

# Rollen der Grundkarte. Quelle der Zuordnung: Farbanalyse der AI-Datei
# (14 Füllfarben) und Form-Abgleich mit den Beispielkarten (LT25-Reader,
# Karten-mit-spezifischen-Lokalisierungen 231106).
ROLLEN = {
    "#c5d1d9": "umgebung",        # Flächen der Umgebung
    "#d9e5ec": "umgebung-hell",   # hellere Umgebungsflächen/Bäume
    "#a2b7ce": "campus",          # Campus-Gelände
    "#455055": "gebaeude",        # Gebäude der Umgebung
    "#4f7095": "gebaeude-campus", # Campus-Gebäude
    "#004070": "goetheanum",      # der Bau selbst
    "#ffffff": "wege",            # Wege und Plätze
    "#e7e7e7": "parkflaeche",     # Parkflächen (einzeln einfärbbar)
    "#c2afbd": "akzent",          # Akzentgebäude (z. B. Rundbauten)
}

# Strichfarben der Quelle gehören zu denselben Rollen — die Original-
# Varianten (LT25 usw.) färben Striche mit der Palette um, sonst entstehen
# beim Umfärben Konturen an Flächen, die flach gemeint sind.
STRICH_ROLLEN = {
    "#d9e5ec": "umgebung-hell",
    "#ffffff": "wege",
    "#a2b1c9": "campus",          # Strichton der Campusfläche
    "#455055": "gebaeude",
    "#4f7095": "gebaeude-campus",
    "#a2b7ce": "campus",
    "#737e8f": "gebaeude",
}

# Standardfarben = Original 2022 (die Presets liegen in app.js).
STANDARD = {rolle: hexwert for hexwert, rolle in ROLLEN.items()}


def main() -> int:
    if not QUELLE.exists():
        print(f"Quelle fehlt: {QUELLE}", file=sys.stderr)
        return 1

    seite = fitz.open(QUELLE)[0]
    svg = seite.get_svg_image()

    # Wurzelelement vereinfachen: mm-Masse, stabile viewBox.
    breite_pt, hoehe_pt = seite.rect.width, seite.rect.height
    svg = re.sub(
        r"<svg[^>]*>",
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{breite_pt}" height="{hoehe_pt}" '
            f'viewBox="0 0 {breite_pt} {hoehe_pt}">'
        ),
        svg,
        count=1,
    )
    # Inkscape-Namespace der PyMuPDF-Ausgabe wird nicht gebraucht.
    svg = svg.replace(' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"', "")
    svg = re.sub(r' inkscape:[a-z-]+="[^"]*"', "", svg)

    # Füllfarben -> Rollen-Klassen. Farben, die keiner Rolle angehören
    # (Kleinstflächen), bleiben wörtlich stehen.
    def ersetze(match: re.Match) -> str:
        farbe = match.group(1).lower()
        rolle = ROLLEN.get(farbe)
        if not rolle:
            return match.group(0)
        return f'class="k-{rolle}"'

    svg = re.sub(r'fill="(#[0-9a-fA-F]{6})"', ersetze, svg)

    def ersetze_strich(match: re.Match) -> str:
        rolle = STRICH_ROLLEN.get(match.group(1).lower())
        if not rolle:
            return match.group(0)
        return f'data-ks="{rolle}"'

    svg = re.sub(r'stroke="(#[0-9a-fA-F]{6})"', ersetze_strich, svg)

    # Parkflächen einzeln adressierbar machen (Lesereihenfolge = Dokument-
    # reihenfolge; IDs stabil, solange die Quelle unverändert ist).
    zaehler = [0]

    def nummeriere(match: re.Match) -> str:
        zaehler[0] += 1
        return f'{match.group(1)} id="parkflaeche-{zaehler[0]}"'

    svg = re.sub(r'(class="k-parkflaeche")', nummeriere, svg)

    stil = "\n".join(
        f".k-{rolle} {{ fill: var(--karte-{rolle}, {farbe}); }}"
        for rolle, farbe in STANDARD.items()
    ) + "\n" + "\n".join(
        f'[data-ks="{rolle}"] {{ stroke: var(--karte-{rolle}, {STANDARD[rolle]}); }}'
        for rolle in sorted(set(STRICH_ROLLEN.values()))
    )
    svg = svg.replace("<defs>", f"<style>\n{stil}\n</style>\n<defs>", 1)

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(svg, encoding="utf-8")
    print(
        f"geschrieben: {ZIEL.relative_to(REPO)} "
        f"({len(svg) // 1024} KB, {zaehler[0]} Parkflächen, "
        f"{svg.count('<path')} Pfade)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
