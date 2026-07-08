#!/usr/bin/env python3
"""Extrahiert die Ortsmarken des Kartentools aus den Beispielkarten.

Quelle:  assets/maps/src/LT25-Reader-Kartenseiten.pdf
         (Doppelseite der Landwirtschaftlichen Tagung 2025, A5-Falz —
         zusammen die A4-quer-Karte, von grafik.goetheanum.ch/kartierung)
         Ergänzend: assets/maps/src/Karten-mit-spezifischen-
         Lokalisierungen-231106.pdf (gleiche Sammlung; Seite 4 liefert
         Kepler-Sternwarte, Helene Finckh Häuschen, Haus de Jaager und
         Eurythmiehaus in exakter Form-Passung — siehe WILLKOMMEN).
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

# Kategorien der Editor-Liste (Reihenfolge = Reihenfolge in Liste und
# Legende); zweisprachig, weil die Legende die Gruppen benennt.
KATEGORIEN = [
    ("eingaenge", {"de": "Eingänge & Empfang", "en": "Entrances & Reception"}),
    ("verkehr", {"de": "Verkehr & Anreise", "en": "Transport & Arrival"}),
    ("treppen", {"de": "Treppenhäuser", "en": "Staircases"}),
    ("saele", {"de": "Säle & Veranstaltungsräume", "en": "Halls & Event Rooms"}),
    ("ausstellung", {"de": "Ausstellung & Orientierung", "en": "Exhibition & Orientation"}),
    ("haeuser", {"de": "Häuser auf dem Campus", "en": "Houses on Campus"}),
    ("sektionen", {"de": "Sektionen", "en": "Sections"}),
    ("gaerten", {"de": "Gärten & Orte im Grünen", "en": "Gardens & Green Spaces"}),
]

# Legende aus dem LT25-Reader (Reihenfolge wie gedruckt), Beschriftungen
# zweisprachig: en wörtlich aus der Vorlage, de nach den deutschen
# Beschriftungen der Weltkonferenz-Karte bzw. Hausgebrauch.
# art: orientierung (blau) | ort (rot) | treppe.
# ‹teile›: gemeinsame Marke, aber einzeln zu- und abschaltbare Orte.
LEGENDE = [
    ("o1", "1", "orientierung", {"de": "Haupteingang", "en": "Main Entrance"}),
    ("o2", "2", "orientierung", {"de": "Südeingang", "en": "South Entrance"}),
    ("o3", "3", "orientierung", {"de": "Empfang", "en": "Reception"}),
    ("o4", "4", "orientierung", {"de": "Infotisch", "en": "Info Desk"}),
    ("o5", "5", "orientierung", {"de": "Buchhandlung", "en": "Bookshop"}),
    ("o6", "6", "orientierung", {"de": "Nordgalerie", "en": "North Gallery"}),
    ("o7", "7", "orientierung", {"de": "Bibliothek", "en": "Library"}),
    ("v10", "10", "ort", {"de": "Grundsteinsaal", "en": "Grundsteinsaal"}),
    ("v11", "11", "ort", {"de": "Terrassensaal", "en": "Terrassensaal"}),
    ("v12", "12", "ort", {"de": "Wandelhalle", "en": "Wandelhalle"}),
    ("v13", "13", "ort", {"de": "Im Hof", "en": "Im Hof"}),
    ("v14", "14", "ort", {"de": "Ostsäle 1-4", "en": "Ostsäle 1-4"}),
    ("v15", "15", "ort", {"de": "Foyer", "en": "Foyer"}),
    ("t-main", "M", "treppe", {"de": "Haupttreppe", "en": "Main Stairs"}, {
        "notizen": [
            {"de": "Galerie · 1. Etage", "en": "Gallery · 1st Floor"},
            {"de": "Grosser Saal · 2. Etage", "en": "Grosser Saal · 2nd Floor"},
        ],
    }),
    ("t-nord", "N", "treppe", {"de": "Nordtreppe", "en": "North Stairs"}, {
        "notizen": [
            {"de": "Nord-Lift", "en": "North Lift", "badge": "lift"},
            {"de": "Galerie · 1. Etage", "en": "Gallery · 1st Floor"},
            {"de": "Grosser Saal · 2. Etage", "en": "Grosser Saal · 2nd Floor"},
            {"de": "Nordsaal · 5. Etage", "en": "Nordsaal · 5th Floor"},
            {"de": "Nordatelier · 6. Etage", "en": "Nordatelier · 6th Floor"},
        ],
    }),
    ("t-sued", "S", "treppe", {"de": "Südtreppe", "en": "South Stairs"}, {
        "notizen": [
            {"de": "Süd-Lift", "en": "South Lift", "badge": "lift"},
            {"de": "Konferenzraum · 1. Etage", "en": "Konferenzraum · 1st Floor"},
            {"de": "Galerie · 1. Etage", "en": "Gallery · 1st Floor"},
            {"de": "Grosser Saal · 2. Etage", "en": "Grosser Saal · 2nd Floor"},
            {"de": "Seminarraum · 4. Etage", "en": "Seminarraum · 4th Floor"},
            {"de": "Holzplastik · 5. Etage", "en": "Wooden Sculpture · 5th Floor"},
            {"de": "Südatelier · 6. Etage", "en": "Südatelier · 6th Floor"},
        ],
    }),
    ("v20", "20", "ort", {"de": "Schreinereisaal", "en": "Schreinereisaal"}),
    ("v21", "21", "ort", {"de": "Plastizierraum", "en": "Plastizierraum"}),
    ("v22", "22", "ort", {"de": "Gartenatelier", "en": "Gartenatelier"}),
    ("v23", "23", "ort", {"de": "Backofen", "en": "Backofen"}),
    ("v24", "24", "ort", {"de": "Schreinerei Südsaal", "en": "Schreinerei Südsaal"}),
    ("v30", "30", "ort", {"de": "English Studies", "en": "English Studies"}),
    # Halde und Puppentheater sind zwei ineinander gebaute Gebäude —
    # die Teile schalten ihre Gebäude einzeln (gebaeudeTeile, Reihenfolge
    # wie die Teile; Ids aus dem Treffer-Test der Gebäudepfade).
    ("v31", "31", "ort", {"de": "Rudolf Steiner Halde", "en": "Rudolf Steiner Halde"}, {
        "teile": [
            {"de": "Rudolf Steiner Halde", "en": "Rudolf Steiner Halde"},
            {"de": "Puppentheater Felicia", "en": "Puppet Theatre Felicia"},
        ],
        "gebaeudeTeile": ["campusbau-41", "campusbau-6"],
    }),
    ("v32", "32", "ort", {"de": "Glashaus", "en": "Glashaus"}),
    ("v33", "33", "ort", {"de": "Studierendenwohnheim", "en": "Students Residence"}),
    ("v34", "34", "ort", {"de": "Haus Schuurman", "en": "Haus Schuurman"}),
    ("v35", "35", "ort", {"de": "Färberei", "en": "Färberei"}),
    ("v36", "36", "ort", {"de": "Holzhaus", "en": "Holzhaus"}),
    ("v37", "37", "ort", {"de": "AfaP", "en": "AfaP"}, {"pfeil": "rechts"}),
    ("v38", "38", "ort", {"de": "Trigon", "en": "Trigon"}, {"pfeil": "rechts"}),
    ("o40", "40", "orientierung", {"de": "Rudolf-Steiner-Atelier", "en": "Rudolf Steiner Atelier"}),
    ("o41", "41", "orientierung", {"de": "Baugeschichte + Modell Erstes Goetheanum", "en": "Building History + 1st Goetheanum Model"}),
    ("o42", "42", "orientierung", {"de": "Hochatelier", "en": "Hochatelier"}),
    ("o43", "43", "orientierung", {"de": "Edith-Maryon-Zimmer", "en": "Edith Maryon Flat"}),
    ("o44", "44", "orientierung", {"de": "Haus Duldeck · Rudolf-Steiner-Archiv", "en": "Haus Duldeck · Rudolf Steiner Archive"}),
    ("o45", "45", "orientierung", {"de": "Speisehaus · Laden", "en": "Restaurant · Shop"}, {
        "pfeil": "unten-rechts",
        "teile": [
            {"de": "Speisehaus · Laden", "en": "Restaurant · Shop"},
            {"de": "Schweizer Landesgesellschaft", "en": "Schweizer Landesgesellschaft"},
            {"de": "Bushaltestelle", "en": "Bus Stop"},
        ],
    }),
    ("f46", "46", "orientierung", {"de": "Bahnhof", "en": "Train Station"}, {"pfeil": "unten-links"}),
    ("f-p", "P", "orientierung", {"de": "Parkplatz", "en": "Parking"}),
]

# Kategorie je Ort (Editor-Liste und Legenden-Sortierung).
KATEGORIE_JE_ORT = {
    "o1": "eingaenge", "o2": "eingaenge", "o3": "eingaenge", "o4": "eingaenge",
    "f-p": "verkehr", "f46": "verkehr",
    "t-main": "treppen", "t-nord": "treppen", "t-sued": "treppen",
    "v10": "saele", "v11": "saele", "v12": "saele", "v13": "saele",
    "v14": "saele", "v15": "saele", "v20": "saele", "v21": "saele",
    "v22": "saele", "v23": "saele", "v24": "saele", "v30": "saele",
    "o5": "ausstellung", "o6": "ausstellung", "o7": "ausstellung",
    "o40": "ausstellung", "o41": "ausstellung", "o42": "ausstellung", "o43": "ausstellung",
    "v31": "haeuser", "v32": "haeuser", "v33": "haeuser", "v34": "haeuser",
    "v35": "haeuser", "v36": "haeuser", "v37": "haeuser", "v38": "haeuser",
    "o44": "haeuser", "o45": "haeuser",
}

# Sektionen, Gärten und weitere Häuser. Quellen und Methode:
# - Karten-mit-spezifischen-Lokalisierungen-231106.pdf Seite 4 (Nachtwache)
#   liegt exakt in Form-Passung zur Grundkarte (Residuum 0.000 mm) —
#   Kepler-Sternwarte, Helene Finckh Häuschen, Haus de Jaager und
#   Eurythmiehaus sind daraus mm-genau übernommen (Kontrolle: die ‹19›
#   Eurythmiehaus trifft die bestehende o43-Marke auf 0.1 mm).
# - Seite 1 (Willkommensschilder, ‹gequetscht auf A4›) ist anisotrop
#   verzerrt UND gedreht — kein mm-genauer Fit möglich (Affin-Residuen
#   ≥ 5 mm). Die Sektionen/Gärten daraus sind darum GEBÄUDE-genau gesetzt:
#   lokale Passung plus Sichtabgleich mit den Gebäudepfaden der Grundkarte
#   (Treffer-Test). Feinlagen folgen aus dem PDF-Export des aktuellen
#   Willkommensbanners, sobald er vorliegt.
WILLKOMMEN = [
    # Barrierefreier Zugang: fixiert am Südeingang (Entscheid Auftraggeber,
    # 8. Juli 2026), Marke mit Rollstuhl-Symbol.
    ("b-zugang", "BF", "eingaenge",
     {"de": "Barrierefreier Zugang", "en": "Barrier-free access"},
     [[222.5, 130.6]], {"symbol": "wc-rollstuhl"}),

    # Sektionen (Buchstaben wie auf dem Willkommensschild):
    ("s-allgemein", "a", "sektionen",
     {"de": "Allgemeine Anthroposophische Sektion", "en": "General Anthroposophical Section"},
     [[179.5, 131.5]], {"gebaeude": "campusbau-52"}),
    ("s-natur", "b", "sektionen",
     {"de": "Naturwissenschaftliche Sektion", "en": "Natural Science Section"},
     [[124.0, 113.5]], {"gebaeude": "campusbau-46"}),
    ("s-paedagogik", "c", "sektionen",
     {"de": "Pädagogische Sektion", "en": "Pedagogical Section"},
     [[189.5, 128.5]], {"gebaeude": "campusbau-53"}),
    ("s-schoene", "d", "sektionen",
     {"de": "Sektion für Schöne Wissenschaften", "en": "Section for the Literary Arts and Humanities"},
     [[142.0, 165.5]], {"gebaeude": "campusbau-41"}),
    ("s-jugend", "e", "sektionen",
     {"de": "Jugendsektion", "en": "Youth Section"},
     [[288.5, 196.5]]),
    ("s-medizin", "f", "sektionen",
     {"de": "Medizinische Sektion", "en": "Medical Section"},
     [[285.5, 104.0]], {"pfeil": "rechts"}),
    ("s-landwirtschaft", "g", "sektionen",
     {"de": "Sektion für Landwirtschaft", "en": "Section for Agriculture"},
     [[124.5, 121.5]], {"gebaeude": "campusbau-46"}),
    ("s-bildende", "h", "sektionen",
     {"de": "Sektion für Bildende Künste", "en": "Visual Art Section"},
     [[104.5, 149.0]]),
    ("s-redende", "i", "sektionen",
     {"de": "Sektion für Redende und Musizierende Künste", "en": "Section for the Performing Arts"},
     [[207.9, 123.4]], {"gebaeude": "campusbau-53"}),
    ("s-sozial", "j", "sektionen",
     {"de": "Sektion für Sozialwissenschaften", "en": "Section for Social Sciences"},
     [[164.3, 62.3]], {"gebaeude": "campusbau-9"}),
    ("s-mathematik", "k", "sektionen",
     {"de": "Mathematisch-Astronomische Sektion", "en": "Section for Mathematics and Astronomy"},
     [[255.5, 31.8]], {"gebaeude": "campusbau-15"}),
    ("s-heilpaedagogik", "m", "sektionen",
     {"de": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
      "en": "Section for Inclusive Social Development"},
     [[285.5, 111.0]], {"pfeil": "rechts"}),

    # Gärten (Nummern wie auf dem Willkommensschild; fortlaufende
    # Nummerierung des Werkzeugs zählt aktive Orte ohnehin neu):
    ("g-felsli", "10", "gaerten", {"de": "Felsli", "en": "Felsli"}, [[230.5, 196.0]]),
    ("g-wasserspiel", "11", "gaerten", {"de": "Wasserspiel", "en": "Flowforms"}, [[107.9, 129.6]]),
    ("g-gedenkhain", "12", "gaerten", {"de": "Gedenkhain", "en": "Memorial Grove"}, [[157.3, 175.4]]),
    ("g-heilkraeuter", "13", "gaerten",
     {"de": "Heilkräutergarten", "en": "Medicinal Plant Garden"}, [[247.2, 94.2]]),
    ("g-faerberpflanzen", "14", "gaerten",
     {"de": "Färberpflanzengarten", "en": "Plant Dye Garden"}, [[242.9, 31.6]]),
    ("g-schnittblumen", "15", "gaerten",
     {"de": "Schnittblumengarten", "en": "Cut Flower Garden"}, [[228.7, 26.1]]),
    ("g-duftkraeuter", "16", "gaerten",
     {"de": "Duftkräutergarten", "en": "Fragrant Herb Garden"}, [[239.3, 39.0]]),
    ("g-bienen", "17", "gaerten",
     {"de": "Bienenskulptur", "en": "Bee Sculpture"}, [[266.0, 43.5]]),
    ("g-praeparate", "18", "gaerten",
     {"de": "Präparatepavillon", "en": "Präparatepavillon"}, [[219.0, 62.1]]),

    # Weitere Häuser (Seite 4 der Beispielkarten, mm-genau):
    ("h-kepler", "50", "haeuser",
     {"de": "Kepler-Sternwarte", "en": "Kepler Observatory"},
     [[255.47, 36.32]], {"gebaeude": "campusbau-15"}),
    ("h-finckh", "51", "haeuser",
     {"de": "Helene Finckh Häuschen", "en": "Helene Finckh Häuschen"},
     [[190.85, 67.22]]),
    ("h-jaager", "52", "haeuser",
     {"de": "Haus de Jaager", "en": "Haus de Jaager"},
     [[266.08, 134.87]]),
    ("h-eurythmie", "53", "haeuser",
     {"de": "Eurythmiehaus", "en": "Eurythmiehaus"},
     [[268.5, 97.0]]),
    ("h-jugendhaus", "54", "haeuser",
     {"de": "Jugendsektionshaus", "en": "House of the Youth Section"},
     [[292.0, 192.5]]),
    ("h-friedwart", "55", "haeuser",
     {"de": "Gästehaus Friedwart", "en": "Guesthouse Friedwart"},
     [[118.0, 202.5]], {"pfeil": "unten-links"}),
    # Sitz der Sektion für Sozialwissenschaften; wird auch für Seminare
    # genutzt — darum eigener Ort samt Gebäude.
    ("h-kristall", "56", "haeuser",
     {"de": "Kristallisationslabor", "en": "Kristallisationslabor"},
     [[168.0, 60.3]], {"gebaeude": "campusbau-9"}),
]

# Eingänge & Empfang tragen standardmässig Gold (Entscheid Auftraggeber,
# 8. Juli 2026); dunkles Hausgold hält Weiss lesbar (B01).
WILLKOMMEN_FARBEN = {"eingaenge": "gold", "sektionen": "grau", "gaerten": "gruen", "haeuser": "blau"}

# Ort → Campus-Gebäude (ids aus build-gelaende-svg.py). Per Treffer-Test der
# Markerpositionen gegen die Gebäudepfade ermittelt (Suchradius ≤ 4.5 mm),
# kuratiert. Die beiden Goetheanum-Schalen (52/53) schalten als Einheit.
GEBAEUDE_JE_ORT = {
    "o3": "campusbau-52", "o4": "campusbau-52", "o5": "campusbau-52",
    "o6": "campusbau-53", "o7": "campusbau-52",
    "t-main": "campusbau-53", "t-nord": "campusbau-53", "t-sued": "campusbau-53",
    "v10": "campusbau-53", "v11": "campusbau-52", "v12": "campusbau-52",
    "v13": "campusbau-53", "v14": "campusbau-52", "v15": "campusbau-53",
    "v20": "campusbau-19", "v21": "campusbau-19", "v22": "campusbau-19",
    "v23": "campusbau-19", "v24": "campusbau-19",
    "v30": "campusbau-6", "v31": "campusbau-41", "v32": "campusbau-46",
    "v33": "campusbau-10", "v34": "campusbau-44", "v35": "campusbau-16",
    "o40": "campusbau-19", "o41": "campusbau-19", "o42": "campusbau-19",
}

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
        oid, marker, art, label = eintrag[:4]
        extra = eintrag[4] if len(eintrag) > 4 else {}
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
            print(f"  ! {marker} ({label['de']}): keine Kartenmarke gefunden")
        kategorie = KATEGORIE_JE_ORT.get(oid, "haeuser")
        # Eingänge & Empfang standardmässig Gold (B01: dunkles Hausgold).
        farbe = "gold" if kategorie == "eingaenge" \
            else ("rot" if art in ("ort", "treppe") else "blau")
        ort = {
            "id": oid, "marker": marker, "art": art,
            "kategorie": kategorie,
            "farbe": farbe,
            "label": label,
            "positionen": positionen,
        }
        ort.update(extra)
        if badges:
            ort["badges"] = badges
        if oid in GEBAEUDE_JE_ORT:
            ort["gebaeude"] = GEBAEUDE_JE_ORT[oid]
        orte.append(ort)

    for eintrag in WILLKOMMEN:
        oid, marker, kategorie, label, positionen = eintrag[:5]
        extra = eintrag[5] if len(eintrag) > 5 else {}
        ort = {
            "id": oid, "marker": marker, "art": "orientierung",
            "kategorie": kategorie,
            "farbe": WILLKOMMEN_FARBEN.get(kategorie, "blau"),
            "label": label,
            "positionen": positionen,
        }
        ort.update(extra)
        orte.append(ort)

    reihenfolge = {schluessel: index for index, (schluessel, _) in enumerate(KATEGORIEN)}
    orte.sort(key=lambda o: reihenfolge.get(o["kategorie"], 99))
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
        + "const KATEGORIEN = " + json.dumps(
            [{"id": k, "name": n} for k, n in KATEGORIEN], ensure_ascii=False, indent=2) + ";\n\n"
        + "const ORTE = " + json.dumps(orte, ensure_ascii=False, indent=2) + ";\n"
    )
    ZIEL.write_text(body, encoding="utf-8")
    mit_position = sum(1 for o in orte if o["positionen"] or o.get("badges"))
    print(f"geschrieben: {ZIEL.relative_to(REPO)} ({len(orte)} Orte, {mit_position} mit Kartenmarke)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
