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

    # ‹Wiese gross› bis an die Wege ziehen (Entscheid Auftraggeber, 16. Juli
    # 2026): das .ai-Quellpolygon folgt den Weg-Lücken nicht (gerader
    # impliziter Schluss zur Nordost-Strasse, Südkante 5–14 Einheiten vor der
    # Weg-Innenkante). Die Kontur hier ist VEKTORGENAU aus der Karte selbst
    # berechnet: Boden-Maske (k-campus + k-wiese) geflutet, Aussenkontur der
    # umschlossenen Insel verfolgt, vereinfacht (ε≈0.25 E) und 0.2 E nach
    # innen versetzt; Trennung zur kleinen Wiese in der verlängerten
    # Hauptweg-Achse (x≈341.5). Werkzeug: Session-Notiz 16.7.2026.
    WIESE_GROSS_D = (
        "M-9.46-29.8-12.57-32.91-16.28-35.39-20.61-36.87-24.7-37.37-29.41-37.37-7"
        "9.15-28.24-102.63-21.62-111.42-18.3-111.51-12.53-107.59-11.37-105.77-9.4"
        "2-104.62-6.6-104.74-3.27-105.77-0.96-106.87 0.16-105.95-0.21-103.33-3.71"
        "-99.89-5.87-97.18-6.26-94.49-5.5-92.81-4.46-90.77-2.17-89.74 0.4-89.76 3"
        ".72-87.49 5.25-85.86 5.13-84.75 6.51-85.04 7.8-81.36 10.38-80.47 9.74-78"
        ".85 10.01-78.01 10.98-78.04 11.68-75.74 13.6-80.13 22.52-80.28 23.56-81."
        "85 24.62-82.88 24.75-84.49 23.77-84.51 21.59-84.8 21.35-93.18 15.6-94.97"
        " 14.38-96.67 15.13-98.09 14.57-98.89 12.72-98.6 11.32-97.57 11.09-105.53"
        " 5.62-109.67 5.26-110.62 6.07-111.74 68.81-111.53 69.69-109.32 71.78-103"
        ".74 75.87-99.07 75.9-82.3 92.17-82.28 93.06-78.58 96.77-69.59 101.64-60."
        "45 107.4-43.82 119.4-31.07 129.78-25.21 133.89-19.02 136.87-12.1 136.99-"
        "7.04 134.76-3.85 132.06-1.63 127.74-0.89 123.54-0.64 116.96-2.01 112.99-"
        "5.14 100.48-7.14 88.2-7.51 72.18-6.76 65.63-3.98 58.95 14.78 33.94 25.63"
        " 20.47 25.77 11.42 19.92 11.63 14.51 10.88 8.46 8.74 3.3 4.7-0.24 0.29-2"
        ".76-5.26-6.38-21.77-7.75-25.99-9.5-29.73Z"
    )
    wiese_gross_neu = [0]

    def wiese_gross_ersetzen(match: re.Match) -> str:
        wiese_gross_neu[0] += 1
        return match.group(1) + WIESE_GROSS_D + match.group(2)

    svg = re.sub(
        r'(<g data-wiese-halter="gross"><path[^>]*? d=")[^"]*("[^>]*?/>)',
        wiese_gross_ersetzen, svg, count=1)
    if wiese_gross_neu[0] != 1:
        print("Warnung: Wiese-gross-Kontur nicht ersetzt", file=sys.stderr)
    print("Wiese gross an die Wege gezogen (vektorgenaue Kontur)")

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

    # Kuratierte Ergänzungen, die in der .ai-Vorlage (Stand 2022) fehlen —
    # Quelle ist das Aquarell-Blatt (Entscheid Auftraggeber, 16. Juli 2026):
    # Bienenskulptur (Wabe, sechsseitig) und Präparatepavillon (Trapez,
    # lange Nordkante parallel zur kurzen Südkante, Öffnung zum Heizhaus).
    # Feste ids oberhalb des Auto-Zählers (aktuell 53); wandern die Bauten
    # in eine neue .ai-Fassung, entfällt dieser Block ersatzlos.
    ergaenzungen = (
        '<g id="ergaenzungen-2026-07">'
        "<!-- kuratierte Ergänzungen (Quelle: Aquarell-Blatt, Entscheid "
        "16. Juli 2026; gepflegt in tools/karten/build-gelaende-svg.py) -->\n"
        '<path id="campusbau-54" d="M469.9 151.63 468.26 152.58 468.26 154.48 '
        '469.9 155.43 471.55 154.48 471.55 152.58Z" class="k-gebaeude-campus"/>\n'
        '<path id="campusbau-55" d="M379.1 203.4 392.1 202 383.89 211.5 '
        '382.11 211.7Z" class="k-gebaeude-campus"/>\n'
        "</g>\n"
    )
    svg = svg.replace("</svg>", ergaenzungen + "</svg>", 1)
    print("Ergänzungen angefügt: Bienenskulptur (54), Präparatepavillon (55)")

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
