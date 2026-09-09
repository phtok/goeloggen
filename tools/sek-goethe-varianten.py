#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Varianten an der Kontrastgrenze – Paletten und Ordnungen zum Vergleich (Labor).

Ergänzt tools/sek-goethe.py: dieselben zwölf Sektionen, aber mehrere Paletten
nebeneinander, alle an der Grenze, die die erste Vorgabe zieht (Weiss auf der
Basis UND die Basis als Schrift auf Papier ≥ 4.5:1). Zwei Vergleichsreihen an
der 3:1-Grenze (WCAG für grosse Schrift ≥ 24 px) zeigen, was Pastell kostet.

Die Physik dahinter: 4.5:1 auf Weiss heisst relative Leuchtdichte ≤ 0.183.
Weil Grün die Leuchtdichte dominiert, ist die hellste erlaubte Stufe je Farbton
verschieden – Gelb und Grün bleiben tief (OKLCH L ≈ 0.55), Blau und Violett
dürfen heller (L ≈ 0.62). Pastell (viel Weiss) und 4.5:1 schliessen sich für
EINE Hex-Farbe aus; ‹leuchtend› heisst hier: volle Buntheit an der Grenze.

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-goethe-varianten.py            Vorschau
  python3 tools/sek-goethe-varianten.py --apply    schreibt assets/sek-goethe-varianten.js
Die Seite sektionsfarben-goethe-varianten.html liest diese Datei.
"""
import json, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, "assets", "sek-goethe-varianten.js")

def _lade(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

sv = _lade("sek-varianten")
sg = _lade("sek-goethe")

WEISS, SOFT = "#ffffff", sg.theme_tokens()["soft"][0]
KEYS = [s["key"] for s in sg.ORDNUNG]
HEUTE = {k: v for k, v in ((s["key"], sg.orgs()[s["key"]]["color"].lower()) for s in sg.ORDNUNG)}
H_F2 = {s["key"]: s["H"] for s in sg.ORDNUNG}
NAMEN = {k: sg.orgs()[k]["short_de"] for k in KEYS}

# --- Löser ------------------------------------------------------------------------
def max_C(L, H):
    lo, hi = 0.0, 0.4
    for _ in range(40):
        mid = (lo + hi) / 2
        if sv._im_gamut(L, mid, H): lo = mid
        else: hi = mid
    return lo

def an_der_grenze(H, ziel, gegen=WEISS, c_faktor=1.0, c_max=None):
    """Hellste Stufe L, bei der die Farbe (Buntheit = c_faktor × Gamut-Maximum,
    gedeckelt) auf `gegen` noch ≥ ziel hält. Sucht von hell nach dunkel."""
    L = 0.90
    while L > 0.15:
        C = max_C(L, H) * c_faktor
        if c_max is not None: C = min(C, c_max)
        hx = sv.from_oklch(L, C, H)
        if sv.kontrast(hx, gegen) >= ziel:
            return hx
        L -= 0.0025
    raise SystemExit("keine Stufe für H %s" % H)

def winkel_zu_H(w):
    """Umkehrung von sek-goethe.winkel: Platz auf Goethes Blatt → OKLCH-Farbton."""
    pts = [((a[2] - 350) % 360, a[1]) for a in sg.ANKER] + [(360, 360)]
    w %= 360
    for (h0, w0), (h1, w1) in zip(pts, pts[1:]):
        if w0 <= w <= w1:
            return (350 + h0 + (h1 - h0) * (w - w0) / (w1 - w0)) % 360
    return 350

def gleichmaessig(hues_heute, schritt=30):
    """Zwölf Töne im gleichen Abstand; die Reihenfolge von heute bleibt (zyklisch),
    der Drehwinkel wird so gewählt, dass die Summe der Verschiebungen minimal ist."""
    reihe = sorted(hues_heute, key=lambda k: hues_heute[k])
    best = None
    for off in range(0, 360):
        for start in range(12):
            ziel = {k: (off + schritt * ((i + start) % 12)) % 360 for i, k in enumerate(reihe)}
            d = sum(min(abs(ziel[k] - hues_heute[k]), 360 - abs(ziel[k] - hues_heute[k])) for k in reihe)
            if best is None or d < best[0]: best = (d, ziel)
    return best[1]

# --- Paletten ---------------------------------------------------------------------
def palette(name, titel, desc, farben, grenze):
    out = []
    for k in KEYS:
        hx = farben[k]; L, C, H = sv.to_oklch(hx)
        out.append({"key": k, "hex": hx, "L": round(L, 3), "C": round(C, 3), "H": round(H, 1),
                    "winkel": sg.winkel(H), "weiss": round(sv.kontrast(hx, WEISS), 2), "soft": round(sv.kontrast(hx, SOFT), 2)})
    return {"id": name, "titel": titel, "desc": desc, "grenze": grenze, "farben": out}

def paletten():
    P = []
    P.append(palette("heute", "Heute", "Die Sektionsfarben, wie sie in den Tokens stehen. Sechs von zwölf tragen kein Weiss.", HEUTE, "keine"))
    f2 = {s["key"]: s["basis"] for s in sg.palette()}
    P.append(palette("f2", "Fassung 2", "Der Stand der Laborseite: Farbtöne von heute, Buntheit je Ort gesetzt, hellste Stufe für 4.6:1 auf Weiss und 4.5:1 auf der Karte.", f2, "4.5 Karte"))
    P.append(palette("leuchtend", "Leuchtend, Grenze Papier",
        "Volle Buntheit des Bildschirms, hellste Stufe für genau 4.5:1 auf Weiss. Auf der Karte (--soft) fällt sie knapp darunter – das ist die äusserste Grenze.",
        {k: an_der_grenze(H_F2[k], 4.5) for k in KEYS}, "4.5 Papier"))
    P.append(palette("leuchtend_karte", "Leuchtend, Grenze Karte",
        "Volle Buntheit, hellste Stufe, die auch auf der Karte 4.5:1 hält. Die Empfehlung, wenn die Basis Schrift sein soll.",
        {k: an_der_grenze(H_F2[k], 4.5, SOFT) for k in KEYS}, "4.5 Karte"))
    P.append(palette("pastell60", "Gedämpft, Grenze Karte",
        "Sechs Zehntel der Buntheit. An der Grenze wird ‹pastellig› zu ‹staubig›: weniger Farbe bei gleicher Tiefe.",
        {k: an_der_grenze(H_F2[k], 4.5, SOFT, 0.6) for k in KEYS}, "4.5 Karte"))
    P.append(palette("pastell35", "Stumpf, Grenze Karte",
        "Ein Drittel der Buntheit – die untere Schwelle, ab der sich Nachbarn nicht mehr unterscheiden.",
        {k: an_der_grenze(H_F2[k], 4.5, SOFT, 0.35) for k in KEYS}, "4.5 Karte"))
    g = gleichmaessig(H_F2)
    P.append(palette("gleich", "Gleichmässig, 30° im Farbraum",
        "Zwölf Farbtöne im gleichen Abstand (OKLCH), Reihenfolge von heute, Drehung mit der kleinsten Verschiebung. Volle Buntheit, Grenze Karte.",
        {k: an_der_grenze(g[k], 4.5, SOFT) for k in KEYS}, "4.5 Karte"))
    gw = {k: winkel_zu_H(30 * i) for i, k in enumerate(KEYS)}
    P.append(palette("gleich_goethe", "Gleichmässig auf Goethes Blatt",
        "Zwölf Plätze im gleichen Abstand auf dem Kreis von 1809 (je 30°), Reihenfolge der Fassung 2. Die warme Seite drängt sich im Farbraum, die kühle dehnt sich.",
        {k: an_der_grenze(gw[k], 4.5, SOFT) for k in KEYS}, "4.5 Karte"))
    P.append(palette("grenze3", "Leuchtend, Grenze 3:1",
        "Zum Vergleich: die hellste Stufe für 3:1 auf Weiss – WCAG-Grenze nur für grosse Schrift (≥ 24 px) und Ränder. So hell dürfte die Basis sein, wenn kleine Schrift die Tinte nähme.",
        {k: an_der_grenze(H_F2[k], 3.0) for k in KEYS}, "3.0 Papier"))
    P.append(palette("grenze3_pastell", "Pastell, Grenze 3:1",
        "Zum Vergleich: halbe Buntheit an der 3:1-Grenze. Das ist das Pastell, das die 4.5-Regel ausschliesst.",
        {k: an_der_grenze(H_F2[k], 3.0, WEISS, 0.5) for k in KEYS}, "3.0 Papier"))
    return P

# --- Ordnungen --------------------------------------------------------------------
# Reihenfolge im Uhrzeigersinn ab Purpur (oben), zwölf Plätze à 30°.
ORDNUNGEN = [
    {"id": "wirkung", "titel": "Goethes Wirkung (Fassung 2)",
     "lesart": "Purpur oben das Ganze; rechts herab die warme Seite mit Tat, Glut, Wärme und Licht; unten Grün und Meergrün, die Erde und ihre Erforschung; links hinauf Blau, Blaurot und Rotblau: Klang, Himmel, Sprache, Wirksamkeit.",
     "reihe": ["aas", "sbk", "szw", "js", "hpise", "ps", "lws", "nws", "srmk", "mas", "ssw", "ms"]},
    {"id": "aufgabe", "titel": "Nach Aufgabe",
     "lesart": "Vier Bögen, die jede Sektion sofort findet: rechts Erziehung und Gesellschaft (warm), unten die Erde (Grün), links die Wissenschaften vom Leben und vom Kosmos (Blau), oben links die Künste (Blaurot bis Purpur). Im Scheitel das Ganze.",
     "reihe": ["aas", "szw", "js", "hpise", "ps", "lws", "nws", "ms", "mas", "srmk", "ssw", "sbk"]},
    {"id": "mensch_welt", "titel": "Geist – Mensch – Welt – Erde",
     "lesart": "Eine senkrechte Achse: oben der Geist (Purpur), unten die Erde (Grün). Der rechte Bogen ist der Mensch – Leib, Kindheit, Jugend, Gemeinschaft –, der linke die Welt – Natur, Kosmos, Klang, Wort, Bild.",
     "reihe": ["aas", "ms", "hpise", "ps", "js", "szw", "lws", "nws", "mas", "srmk", "ssw", "sbk"]},
]

def ordnungen():
    out = []
    basis = ORDNUNGEN[0]["reihe"]
    for o in ORDNUNGEN:
        plaetze = [{"key": k, "winkel": 30 * i, "H": round(winkel_zu_H(30 * i), 1),
                    "hex": an_der_grenze(winkel_zu_H(30 * i), 4.5, SOFT)} for i, k in enumerate(o["reihe"])]
        # «bewegt» = mehr als einen Platz (30°) von der Fassung 2 entfernt – die
        # Sektionen, über die die Ordnung tatsächlich entscheidet.
        def dist(k):
            d = abs(30 * o["reihe"].index(k) - 30 * basis.index(k)) % 360
            return min(d, 360 - d)
        bewegt = [k for k in o["reihe"] if dist(k) > 30]
        out.append({"id": o["id"], "titel": o["titel"], "lesart": o["lesart"], "plaetze": plaetze, "bewegt": bewegt})
    return out

def grenzen():
    """Hellste erlaubte OKLCH-Stufe je Anker – die Physik der Grenze, als Zahl."""
    return [{"name": a[0], "H": a[2], "L45": round(sv.to_oklch(an_der_grenze(a[2], 4.5))[0], 2),
             "L3": round(sv.to_oklch(an_der_grenze(a[2], 3.0))[0], 2)} for a in sg.ANKER]

def main():
    P, O, G = paletten(), ordnungen(), grenzen()
    for p in P:
        print("%-34s" % p["titel"], " ".join("%s %s(%.1f/%.1f)" % (f["key"], f["hex"], f["weiss"], f["soft"]) for f in p["farben"]))
    print("Grenzen:", G)
    for o in O:
        print(o["titel"], "→", " ".join(o["reihe"] if "reihe" in o else [p["key"] for p in o["plaetze"]]), "bewegt:", o["bewegt"])
    if "--apply" in sys.argv:
        daten = {"$quelle": "GENERIERT von tools/sek-goethe-varianten.py – nicht von Hand ändern.",
                 "namen": NAMEN, "keys": KEYS, "paletten": P, "ordnungen": O, "grenzen": G, "soft": SOFT}
        js = "/* GENERIERT von tools/sek-goethe-varianten.py – nicht von Hand ändern. */\nwindow.GOE_SEK_GOETHE_VARIANTEN = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n"
        alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
        if alt != js:
            open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
        else:
            print("unverändert:", os.path.relpath(OUT_JS, ROOT))

if __name__ == "__main__":
    main()
