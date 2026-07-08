#!/usr/bin/env python3
"""Extrahiert die Ortsmarken des Kartentools aus den Beispielkarten.

Quelle:  assets/maps/src/LT25-Reader-Kartenseiten.pdf
         (Doppelseite der Landwirtschaftlichen Tagung 2025, A5-Falz —
         zusammen die A4-quer-Karte, von grafik.goetheanum.ch/kartierung)
Ziel:    apps/karten-generator/orte.js

Was passiert:
- Die Platzierung der Geländekarte wird über Form-Fingerprints (identische
  Pfade in Quelle und Grundkarte) je Halbseite bestimmt und gegengeprüft.
- Jede Nummern-/Buchstabenmarke wird über ihren Kreis (Zentrum, Füllfarbe)
  millimetergenau in Blattkoordinaten (297×210, Falz 148.5) übernommen.
- Die Legendentexte (mit Umlauten) stammen wörtlich aus der Beispiel-Legende;
  die Struktur (Spalten, Treppen-Untereinträge) ist hier abgebildet.

Idempotent. Benötigt: pip install pymupdf
"""

from __future__ import annotations

import json
import pathlib
import re
import statistics
import sys
from collections import Counter

import fitz  # PyMuPDF

REPO = pathlib.Path(__file__).resolve().parents[2]
QUELLE = REPO / "assets/maps/src/LT25-Reader-Kartenseiten.pdf"
GELAENDE = REPO / "assets/maps/src/Gelaende_jo_ergaenzt-2022.ai"
ZIEL = REPO / "apps/karten-generator/orte.js"

MM = 25.4 / 72
BLATT = (297.0, 210.0)
FALZ = 148.5
# Halbseiten: linke Seite beginnt bei 0.5 mm (296-mm-Doppelseite mittig
# auf dem 297-mm-Blatt), rechte an der Falzlinie minus Bundversatz.
SEITEN_OFFSET = {0: 0.5, 1: 148.49}

# Legende wörtlich aus dem LT25-Reader (Spalte, Reihenfolge wie gedruckt).
# art: orientierung (blau) | ort (rot) | treppe | hinweis (nur Legende).
LEGENDE = [
    ("o1", "1", "orientierung", "Main Entrance", 0),
    ("o2", "2", "orientierung", "South Entrance", 0),
    ("o3", "3", "orientierung", "Reception/Empfang", 0),
    ("o4", "4", "orientierung", "Info Desk", 0),
    ("o5", "5", "orientierung", "Bookshop", 0),
    ("o6", "6", "orientierung", "North Gallery", 0),
    ("o7", "7", "orientierung", "Library", 0),
    ("v10", "10", "ort", "Grundsteinsaal", 0),
    ("v11", "11", "ort", "Terrassensaal", 0),
    ("v12", "12", "ort", "Wandelhalle", 0),
    ("v13", "13", "ort", "Im Hof", 0),
    ("v14", "14", "ort", "Ostsäle 1-4", 0),
    ("v15", "15", "ort", "Foyer", 0),
    ("t-main", "M", "treppe", "Main Stairs", 0, {
        "notizen": [
            {"label": "Gallery · 1st Floor"},
            {"label": "Grosser Saal · 2nd Floor"},
        ],
    }),
    ("t-nord", "N", "treppe", "North Stairs", 0, {
        "notizen": [
            {"label": "North Lift", "badge": "lift"},
            {"label": "Gallery · 1st Floor"},
            {"label": "Grosser Saal · 2nd Floor"},
            {"label": "Nordsaal · 5th Floor"},
            {"label": "Nordatelier · 6th Floor"},
        ],
    }),
    ("t-sued", "S", "treppe", "South Stairs", 0, {
        "notizen": [
            {"label": "South Lift", "badge": "lift"},
            {"label": "Konferenzraum · 1st Floor"},
            {"label": "Gallery · 1st Floor"},
            {"label": "Grosser Saal · 2nd Floor"},
            {"label": "Seminarraum · 4th Floor"},
            {"label": "Wooden Sculpture · 5th Floor"},
            {"label": "Südatelier · 6th Floor"},
        ],
    }),
    ("v20", "20", "ort", "Schreinereisaal", 1),
    ("v21", "21", "ort", "Plastizierraum", 1),
    ("v22", "22", "ort", "Gartenatelier", 1),
    ("v23", "23", "ort", "Backofen", 1),
    ("v24", "24", "ort", "Schreinerei Südsaal", 1),
    ("v30", "30", "ort", "English Studies", 1),
    ("v31", "31", "ort", "Halde", 1),
    ("v32", "32", "ort", "Glashaus", 1),
    ("v33", "33", "ort", "Studierendenwohnheim", 1),
    ("v34", "34", "ort", "Haus Schuurman", 1),
    ("v35", "35", "ort", "Färberei", 1),
    ("v36", "36", "ort", "Holzhaus", 1),
    ("v37", "37", "ort", "AfaP", 1, {"pfeil": "rechts"}),
    ("v38", "38", "ort", "Trigon", 1, {"pfeil": "rechts"}),
    ("o40", "40", "orientierung", "Rudolf Steiner Atelier", 1),
    ("o41", "41", "orientierung", "1st Goetheanum Model", 1),
    ("o42", "42", "orientierung", "Hochatelier", 1),
    ("o43", "43", "orientierung", "Edith Maryon Flat", 1),
    ("o44", "44", "orientierung", "Rudolf Steiner Archive", 1),
    ("o45", "45", "orientierung", "Speisehaus · Schweizer\nLandesgesellschaft\nBus Stop", 1,
     {"pfeil": "unten-rechts"}),
    ("f46", "46", "orientierung", "Train Station", 1, {"pfeil": "unten-links"}),
    ("f-p", "P", "orientierung", "Parking", 1),
]

# Kartenbereich je Halbseite (Blatt-mm): links liegt die Legende, dort
# gelten nur x > 100 als Kartenmarken.
KARTENBEREICH_X = {0: 100.0, 1: 0.0}

# Ratifizierte Ausnahmen gegenüber der Quelle: (marker, x, y, Toleranz mm).
# Die LT25-Vorlage trägt die ‹5› (Bookshop) zweimal — die Zweitmarke auf dem
# Südweg ist dort falsch gesetzt und wird nicht übernommen
# (Entscheid Auftraggeber, 8. Juli 2026).
AUSNAHMEN = [
    ("5", 198.99, 172.47, 1.0),
]


def pfadpunkte(pfad):
    punkte = []
    for element in pfad["items"]:
        if element[0] == "l":
            punkte += [element[1], element[2]]
        elif element[0] == "c":
            punkte += [element[1], element[4]]
        elif element[0] == "re":
            r = element[1]
            punkte += [fitz.Point(r.x0, r.y0), fitz.Point(r.x1, r.y1)]
        elif element[0] == "qu":
            q = element[1]
            punkte += [q.ul, q.ur, q.ll, q.lr]
    return punkte


def fingerprint(pfad):
    r = pfad["rect"]
    hoehe = max(0.01, r.y1 - r.y0)
    return (len(pfadpunkte(pfad)), round((r.x1 - r.x0) / hoehe, 2))


def kartenplatzierung(seiten):
    """Skala/Versatz der Geländekarte je Halbseite über Form-Fingerprints."""
    grund = fitz.open(GELAENDE)[0]
    gp = [p for p in grund.get_drawings() if p.get("fill")]
    haeufig = Counter(fingerprint(p) for p in gp)
    eindeutig = {fingerprint(p): p for p in gp
                 if haeufig[fingerprint(p)] == 1 and len(pfadpunkte(p)) >= 8}

    ergebnisse = []
    for index, seite in enumerate(seiten):
        sp = [p for p in seite.get_drawings() if p.get("fill")]
        haeufig2 = Counter(fingerprint(p) for p in sp)
        eindeutig2 = {fingerprint(p): p for p in sp if haeufig2[fingerprint(p)] == 1}
        gemeinsam = sorted(set(eindeutig) & set(eindeutig2), key=lambda s: -s[0])[:14]
        if len(gemeinsam) < 6:
            raise SystemExit(f"Seite {index + 1}: zu wenige gemeinsame Formen")
        skalen, tx, ty = [], [], []
        for s in gemeinsam:
            ra, rs = eindeutig[s]["rect"], eindeutig2[s]["rect"]
            skalen.append((rs.x1 - rs.x0) / (ra.x1 - ra.x0))
            skalen.append((rs.y1 - rs.y0) / (ra.y1 - ra.y0))
        skala = statistics.median(skalen)
        for s in gemeinsam:
            ra, rs = eindeutig[s]["rect"], eindeutig2[s]["rect"]
            tx.append(rs.x0 - skala * ra.x0)
            ty.append(rs.y0 - skala * ra.y0)
        ergebnisse.append((skala, statistics.median(tx), statistics.median(ty)))

    breite_pt, hoehe_pt = grund.rect.width, grund.rect.height
    plaetze = []
    for index, (skala, tx, ty) in enumerate(ergebnisse):
        plaetze.append({
            "x": SEITEN_OFFSET[index] + tx * MM,
            "y": ty * MM,
            "breite": breite_pt * skala * MM,
            "hoehe": hoehe_pt * skala * MM,
        })
    delta = max(abs(plaetze[0][k] - plaetze[1][k]) for k in ("x", "y", "breite", "hoehe"))
    if delta > 0.05:
        raise SystemExit(f"Halbseiten widersprechen sich um {delta:.3f} mm")
    print(f"Kartenplatzierung: {plaetze[0]} (Abweichung der Halbseiten {delta:.4f} mm)")
    return {k: round((plaetze[0][k] + plaetze[1][k]) / 2, 3) for k in plaetze[0]}


def kreisfarbe(rgb):
    r, g, b = rgb
    if all(c > 0.95 for c in rgb):
        return "weiss"
    if r - b > 0.3:
        return "rot"
    if b - r > 0.2 and b > 0.7:
        return "blau"
    return None


def marken_extrahieren(seiten):
    """Alle Kreis-/Badge-Marken mit Zentrum (Blatt-mm) und Farbe."""
    funde = []
    for index, seite in enumerate(seiten):
        offset = SEITEN_OFFSET[index]
        kreise, lifte = [], []
        for p in seite.get_drawings():
            fuellung = p.get("fill")
            if not fuellung:
                continue
            r = p["rect"]
            w, h = r.x1 - r.x0, r.y1 - r.y0
            farbe = kreisfarbe(tuple(fuellung))
            if not farbe:
                continue
            if 6 < w < 16 and abs(w - h) < 1.5:
                kreise.append((r, farbe))
            elif farbe == "weiss" and 6 < w < 12 and 1.2 < h / max(w, 0.01) < 2.0:
                lifte.append((r, farbe))
        for wort in seite.get_text("words"):
            text = wort[4]
            if not re.fullmatch(r"\d{1,2}|[PMNS]", text):
                continue
            cx, cy = (wort[0] + wort[2]) / 2, (wort[1] + wort[3]) / 2
            blatt_x = offset + cx * MM
            if blatt_x < KARTENBEREICH_X[index]:
                continue  # Legendenspalte
            treffer = [(r, f) for r, f in kreise
                       if r.x0 - 1 < cx < r.x1 + 1 and r.y0 - 1 < cy < r.y1 + 1]
            lift = [(r, f) for r, f in lifte
                    if r.x0 - 1 < cx < r.x1 + 1 and r.y0 - 2 < cy < r.y1 + 2]
            if treffer:
                r, farbe = treffer[0]
                funde.append({
                    "marker": text, "farbe": farbe, "form": "kreis",
                    "x": round(offset + (r.x0 + r.x1) / 2 * MM, 2),
                    "y": round((r.y0 + r.y1) / 2 * MM, 2),
                })
            elif lift:
                r, _ = lift[0]
                funde.append({
                    "marker": text, "farbe": "weiss", "form": "lift",
                    "x": round(offset + (r.x0 + r.x1) / 2 * MM, 2),
                    "y": round((r.y0 + r.y1) / 2 * MM, 2),
                })
            else:
                funde.append({
                    "marker": text, "farbe": None, "form": "wort",
                    "x": round(blatt_x, 2), "y": round(cy * MM, 2),
                })
    def ratifiziert(fund):
        for marker, x, y, toleranz in AUSNAHMEN:
            if fund["marker"] == marker and abs(fund["x"] - x) < toleranz and abs(fund["y"] - y) < toleranz:
                print(f"  Ausnahme angewandt: {marker} bei ({fund['x']}, {fund['y']}) nicht übernommen")
                return False
        return True
    return [f for f in funde if ratifiziert(f)]


def orte_bauen(funde):
    orte = []
    for eintrag in LEGENDE:
        oid, marker, art, label, spalte = eintrag[:5]
        extra = eintrag[5] if len(eintrag) > 5 else {}
        passend = [f for f in funde if f["marker"] == marker]
        if art == "treppe":
            badges = ([{"x": f["x"], "y": f["y"], "form": "treppe"}
                       for f in passend if f["form"] == "kreis"]
                      + [{"x": f["x"], "y": f["y"], "form": "lift"}
                         for f in passend if f["form"] == "lift"])
            positionen = []
        else:
            badges = []
            kreise = [f for f in passend if f["form"] == "kreis"]
            woerter = [f for f in passend if f["form"] == "wort"]
            gewaehlt = kreise or woerter
            positionen = [[f["x"], f["y"]] for f in gewaehlt]
        if not positionen and not badges:
            print(f"  ! {marker} ({label.splitlines()[0]}): keine Kartenmarke gefunden")
        ort = {
            "id": oid, "marker": marker, "art": art,
            "farbe": "rot" if art in ("ort", "treppe") else "blau",
            "label": label, "spalte": spalte,
            "positionen": positionen,
        }
        ort.update(extra)
        if badges:
            ort["badges"] = badges
        orte.append(ort)
    return orte


def main() -> int:
    if not QUELLE.exists():
        print(f"Quelle fehlt: {QUELLE}", file=sys.stderr)
        return 1
    doc = fitz.open(QUELLE)
    seiten = [doc[0], doc[1]]
    platz = kartenplatzierung(seiten)
    funde = marken_extrahieren(seiten)
    orte = orte_bauen(funde)

    kopf = (
        "// GENERIERT von tools/karten/extract-marker-positionen.py —\n"
        "// nicht von Hand ändern. Quelle: LT25-Reader-Kartenseiten\n"
        "// (grafik.goetheanum.ch/kartierung), Masse in mm auf dem A4-quer-Blatt.\n"
    )
    karte = {
        "blatt": {"breite": BLATT[0], "hoehe": BLATT[1]},
        "falz": FALZ,
        "gelaende": platz,
    }
    body = (
        kopf
        + "const KARTE = " + json.dumps(karte, ensure_ascii=False, indent=2) + ";\n\n"
        + "const ORTE = " + json.dumps(orte, ensure_ascii=False, indent=2) + ";\n"
    )
    ZIEL.write_text(body, encoding="utf-8")
    mit_position = sum(1 for o in orte if o["positionen"] or o.get("badges"))
    print(f"geschrieben: {ZIEL.relative_to(REPO)} ({len(orte)} Orte, {mit_position} mit Kartenmarke)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
