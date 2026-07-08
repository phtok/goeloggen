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

    # Die visuelle Sprache der Karte kennt keine Linien, nur Flächen-
    # kontraste (Entscheid Auftraggeber, 8. Juli 2026): die Strich-
    # Zwillinge um Häuser und Campusflächen (Kontur-Duplikate der Füll-
    # pfade) entfallen ersatzlos; ebenso nicht zugeordnete Restlinien.
    # Es bleiben die weissen Wege (Karteninhalt, lesen sich als Flächen)
    # und die helle Baum-Textur der Umgebung.
    KONTUR_ROLLEN = ("campus", "gebaeude", "gebaeude-campus")
    konturen = [0]

    # Auch weisse Wege-Striche können Kontur-Zwillinge sein (weisse Ränder
    # an einzelnen Häusern): ein Strichpfad, dessen Geometrie (transform+d)
    # ein Füllpfad-Duplikat ist, ist Kontur — echte Fusswege haben keinen
    # Füll-Zwilling und bleiben.
    fuellformen = set(re.findall(
        r'<path transform="([^"]+)"[^>]*?class="k-[a-z-]+"[^>]*? d="([^"]+)"', svg))
    fuellformen |= set(re.findall(
        r'<path transform="([^"]+)" d="([^"]+)"[^>]*?class="k-[a-z-]+"', svg))

    def konturen_entfernen(match: re.Match) -> str:
        tag = match.group(0)
        if 'fill="none"' not in tag:
            return tag
        if any(f'data-ks="{rolle}"' in tag for rolle in KONTUR_ROLLEN) or 'stroke="#' in tag:
            konturen[0] += 1
            return ""
        if 'data-ks="wege"' in tag:
            # Haarlinien (Strichstärke ≤ 0.5 pt) sind Kontur-Zeichnung an
            # Häusern (Glashaus, Heizhaus, Halde …) — echte Fusswege tragen
            # ≥ 0.769 pt. Sichtabgleich 8. Juli 2026: Wegenetz unverändert.
            staerke = re.search(r'stroke-width="([.\d]+)"', tag)
            if staerke and float(staerke.group(1)) <= 0.5:
                konturen[0] += 1
                return ""
            form = re.search(r'transform="([^"]+)"[^>]*? d="([^"]+)"', tag)
            if form and (form.group(1), form.group(2)) in fuellformen:
                konturen[0] += 1
                return ""
            # Kleine weisse Strichstücke (< ~10 mm) sind Kontur-Reste an
            # Häusern, keine Wege — Sichtabgleich: ihr Wegfall ändert das
            # Wegenetz nicht (die Wege selbst sind Füllflächen oder lang).
            if form:
                # auch ‹-.255›/‹.091› (führender Dezimalpunkt) korrekt lesen
                zahlen = [float(z) for z in re.findall(r"-?(?:\d+\.?\d*|\.\d+)", form.group(2))]
                xs, ys = zahlen[0::2], zahlen[1::2]
                if xs and ys and max(max(xs) - min(xs), max(ys) - min(ys)) < 20.1:
                    konturen[0] += 1
                    return ""
        return tag

    svg = re.sub(r"<path[^>]*/>", konturen_entfernen, svg)
    print(f"Kontur-Zwillinge entfernt: {konturen[0]}")

    # Die Umgebungsfläche nördlich von Holzhaus und Studierendenwohnheim
    # liest papierweiss (Entscheid Auftraggeber, 8. Juli 2026) — sie folgt
    # der Wege-Rolle (weiss in allen Varianten).
    NORDFELD_SIGNATUR = "M0 0-13.446-14.817-21.558-33.096"
    anfang = svg.find(NORDFELD_SIGNATUR)
    if anfang >= 0:
        pfad_anfang = svg.rfind("<path", 0, anfang)
        pfad_ende = svg.find("/>", anfang) + 2
        segment = svg[pfad_anfang:pfad_ende]
        neu = segment.replace('class="k-umgebung"', 'class="k-wege" id="nordfeld"')
        svg = svg[:pfad_anfang] + neu + svg[pfad_ende:]
        print("Nordfeld auf Wege-Rolle (weiss) gesetzt")
    else:
        print("Warnung: Nordfeld-Pfad nicht gefunden", file=sys.stderr)

    # Parkflächen einzeln adressierbar machen (Lesereihenfolge = Dokument-
    # reihenfolge; IDs stabil, solange die Quelle unverändert ist).
    zaehler = [0]

    def nummeriere(match: re.Match) -> str:
        zaehler[0] += 1
        return f'{match.group(1)} id="parkflaeche-{zaehler[0]}"'

    svg = re.sub(r'(class="k-parkflaeche")', nummeriere, svg)

    # Die zwei Wiesenflächen vor dem Haupteingang (einfärbbar; identifiziert
    # per Treffer-Test an den beschrifteten Punkten des Auftraggebers):
    # ‹Wiese klein› westlich des Hauptwegs, ‹Wiese gross› mit dem
    # Rudolf-Steiner-Archiv-Umfeld östlich davon.
    WIESEN = {
        "wiese-klein": "M0 0 .784-57.775 .849-61.683",
        "wiese-gross": "M0 0-2.46-5.55-12.039-1.456-18.235",
    }
    for wiesen_id, d_signatur in WIESEN.items():
        kurz = wiesen_id.replace("wiese-", "")
        # Alle Vorkommen: der Füllpfad und sein Strich-Zwilling (identische
        # Geometrie, nur Kontur) — beide müssen der Wiesenfarbe folgen und
        # werden für den Beschnitt des Südzipfels in einen Halter gehüllt
        # (die Quellpolygone laufen unter dem Weg am Rondell weiter).
        suchpos = 0
        gefunden = 0
        while True:
            anfang = svg.find(d_signatur, suchpos)
            if anfang < 0:
                break
            pfad_anfang = svg.rfind("<path", 0, anfang)
            pfad_ende = svg.find("/>", anfang) + 2
            segment = svg[pfad_anfang:pfad_ende]
            if 'class="k-campus"' in segment:
                segment = segment.replace('class="k-campus"', f'class="k-wiese" id="{wiesen_id}"')
            elif 'data-ks="campus"' in segment:
                segment = segment.replace('data-ks="campus"', f'data-wiese-strich="{kurz}"')
            neu = f'<g data-wiese-halter="{kurz}">{segment}</g>'
            svg = svg[:pfad_anfang] + neu + svg[pfad_ende:]
            suchpos = pfad_anfang + len(neu)
            gefunden += 1
        if not gefunden:
            print(f"Warnung: Wiesenpfad {wiesen_id} nicht gefunden", file=sys.stderr)

    # Dunkle Gebäudeflächen sind flach gemeint — weisse Quell-Striche
    # (Wege-Strichrolle) an ihnen zeichnen Konturen: Strich entfernen.
    def strich_von_dunklen(match: re.Match) -> str:
        tag = match.group(0)
        if re.search(r'class="k-(akzent|goetheanum|gebaeude-campus|gebaeude)"', tag):
            return tag.replace(' data-ks="wege"', "")
        return tag

    svg = re.sub(r"<path[^>]*>", strich_von_dunklen, svg)

    # Campus-Gebäude einzeln adressierbar (Aktiv-/Passiv-Schaltung):
    bau_zaehler = [0]

    def bau_nummerieren(match: re.Match) -> str:
        tag = match.group(0)
        if "id=" in tag:
            return tag
        if re.search(r'class="k-(akzent|goetheanum|gebaeude-campus)"', tag):
            bau_zaehler[0] += 1
            return tag.replace("<path", f'<path id="campusbau-{bau_zaehler[0]}"', 1)
        return tag

    svg = re.sub(r"<path[^>]*>", bau_nummerieren, svg)
    print(f"Campus-Gebäude nummeriert: {bau_zaehler[0]}")

    stil = "\n".join(
        f".k-{rolle} {{ fill: var(--karte-{rolle}, {farbe}); }}"
        for rolle, farbe in STANDARD.items()
    ) + "\n" + "\n".join(
        f'[data-ks="{rolle}"] {{ stroke: var(--karte-{rolle}, {STANDARD[rolle]}); }}'
        for rolle in sorted(set(STRICH_ROLLEN.values()))
    ) + "\n.k-wiese { fill: var(--karte-campus, #a2b7ce); }"
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
