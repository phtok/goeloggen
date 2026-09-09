#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sektionsfarben nach Goethes Farbenkreis – Laborpalette, gerechnet, nicht gefühlt.

Alternatives Farbkonzept (Labor, nicht ratifiziert): die zwölf Sektionen der
Hochschule werden auf Goethes sinnlich-sittlichen Farbenkreis gelegt (Zur
Farbenlehre, 1810, Didaktischer Teil, 6. Abteilung, §§ 758–829; Farbenkreis
«zur Symbolisierung des menschlichen Geistes- und Seelenlebens», 1809). Jede
Sektion bekommt einen ORT auf dem Kreis (Goethes Farbname), eine SPHÄRE des
äusseren Rings (Vernunft · Verstand · Sinnlichkeit · Phantasie) und einen
Grund aus Goethes Text. Aus dem Ort folgt der Farbton (OKLCH H); Helligkeit
und Buntheit sind je Ort gesetzt, damit die Reihe als eine Reihe wirkt.

Die drei Gestalten (dunkel · hell · ink, je Theme) entstehen mit DEMSELBEN
Rezept wie die heutigen Sektionsfarben (tools/sek-varianten.py wird
importiert); wo der sRGB-Körper das Rezept nicht trägt (Gelb wird bei L 0.47
ein Braun), setzt eine Ausnahme die Helligkeit, und eine Sicherung senkt sie
in Hundertstel-Schritten, bis jeder Kontrast ≥ 4.5:1 hält (B02).

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-goethe.py            Vorschau (Werte, Kontraste, Kreis)
  python3 tools/sek-goethe.py --apply    schreibt assets/sek-goethe.js (idempotent)
Die Seite sektionsfarben-goethe.html liest diese Datei.
"""
import json, os, re, sys, math, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_CSS = os.path.join(ROOT, "design-system", "tokens.css")
ORGS_JS = os.path.join(ROOT, "assets", "goe-orgs.js")
OUT_JS = os.path.join(ROOT, "assets", "sek-goethe.js")

_spec = importlib.util.spec_from_file_location("sekvar", os.path.join(ROOT, "tools", "sek-varianten.py"))
sv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sv)

# --- Goethes Kreis: sechs Farben, Purpur oben, tätige Seite rechts -------------
# (Grad im Uhrzeigersinn, OKLCH-Farbton des Ankers). Zwischen den Ankern wird der
# Platz einer Sektion linear aus ihrem Farbton bestimmt.
ANKER = [  # (Goethes Name, Winkel auf dem Blatt, OKLCH-H, Wort des inneren Rings 1809, L, C fürs Kreisbild)
    ("Purpur",  0,   350, "schön",    0.55, 0.18),
    ("Gelbrot", 60,  35,  "edel",     0.62, 0.19),
    ("Gelb",    120, 96,  "gut",      0.85, 0.17),
    ("Grün",    180, 140, "nützlich", 0.66, 0.16),
    ("Blau",    240, 250, "gemein",   0.55, 0.15),
    ("Blaurot", 300, 300, "unnötig",  0.50, 0.16),
]
# Äusserer Ring 1809: vier Sphären, je anderthalb Sektoren – Rot und Grün gehören zweien.
SPHAEREN = [
    {"id": "vernunft",     "name": "Vernunft",     "von": 0,   "bis": 90,  "farben": "Purpur und Gelbrot"},
    {"id": "verstand",     "name": "Verstand",     "von": 90,  "bis": 180, "farben": "Gelb und Grün"},
    {"id": "sinnlichkeit", "name": "Sinnlichkeit", "von": 180, "bis": 270, "farben": "Grün und Blau"},
    {"id": "phantasie",    "name": "Phantasie",    "von": 270, "bis": 360, "farben": "Blaurot und Purpur"},
]

# --- Die Ordnung: Sektion → Ort auf dem Kreis (H), Helligkeit, Buntheit --------
# Reihenfolge im Uhrzeigersinn ab Purpur. «grund» ist der Satz für die Seite,
# «para» die Belegstelle in Goethes Text.
ORDNUNG = [
    {"key": "aas",   "ort": "Purpur",           "sph": "vernunft",     "H": 350, "L": 0.52, "C": 0.170,
     "grund": "Der Scheitel des Kreises: Purpur entsteht, wo sich beide gesteigerten Seiten vereinigen – ‹diese höchste aller Farbenerscheinungen› enthält alle anderen. Die Sektion, die das Ganze trägt, steht dort.",
     "para": "§§ 793–796"},
    {"key": "ms",    "ort": "Karmin",           "sph": "vernunft",     "H": 18,  "L": 0.55, "C": 0.190,
     "grund": "Goethe denkt sich das reine Rot als ‹vollkommenen Karmin› und gibt ihm ‹Ernst und Würde› wie ‹Huld und Anmut› – Blut und Leben, Sorge um den ganzen Menschen.",
     "para": "§§ 792, 796"},
    {"key": "szw",   "ort": "Gelbrot",          "sph": "vernunft",     "H": 38,  "L": 0.62, "C": 0.190,
     "grund": "‹Die aktive Seite ist hier in ihrer höchsten Energie›: Zinnober ist die Farbe des Tuns – Sozialwissenschaft als Wille und Tat im Sozialen.",
     "para": "§§ 774–775"},
    {"key": "js",    "ort": "Rotgelb",          "sph": "vernunft",     "H": 58,  "L": 0.70, "C": 0.170,
     "grund": "Orange gibt ‹das Gefühl von Wärme und Wonne›, es ist ‹die Farbe der höhern Glut› und erscheint ‹mächtiger und herrlicher› als Gelb – die Jugend als Glut.",
     "para": "§§ 772–773"},
    {"key": "hpise", "ort": "Gelb, gesättigt",  "sph": "verstand",     "H": 78,  "L": 0.76, "C": 0.150,
     "grund": "Gelb macht ‹einen durchaus warmen und behaglichen Eindruck› und hat ‹in seiner ganzen Kraft etwas Heiteres und Edles› – Wärme, die einschliesst.",
     "para": "§§ 768–770"},
    {"key": "ps",    "ort": "Gelb",             "sph": "verstand",     "H": 96,  "L": 0.84, "C": 0.160,
     "grund": "‹Die nächste Farbe am Licht›, ‹heiter, munter, sanft reizend› – die Kindheit, das Lernen, das Licht, das die Pädagogik hütet.",
     "para": "§§ 765–766"},
    {"key": "lws",   "ort": "Grün",             "sph": "verstand",     "H": 140, "L": 0.66, "C": 0.160,
     "grund": "Grün ist die reale Mischung der beiden Mutterfarben: ‹Unser Auge findet in derselben eine reale Befriedigung› – Erde, Wachstum, das Nützliche.",
     "para": "§§ 801–802"},
    {"key": "nws",   "ort": "Meergrün",         "sph": "sinnlichkeit", "H": 178, "L": 0.58, "C": 0.110,
     "grund": "Wo Blau ‹vom Plus partizipiert›, nennt Goethe das Meergrün ‹eine liebliche Farbe›. Die Sphäre heisst Sinnlichkeit: die Sektion, die Goethes anschauende Naturforschung weiterführt.",
     "para": "§ 785"},
    {"key": "srmk",  "ort": "Blau",             "sph": "sinnlichkeit", "H": 238, "L": 0.64, "C": 0.130,
     "grund": "Blau ist ‹als Farbe eine Energie›, ‹ein reizendes Nichts›, das wir gern ansehen, ‹weil es uns nach sich zieht› – die weiche, sehnende Seite, aus der Sprache und Musik kommen.",
     "para": "§§ 777, 779, 781"},
    {"key": "mas",   "ort": "Blau, dunkel",     "sph": "sinnlichkeit", "H": 265, "L": 0.45, "C": 0.160,
     "grund": "‹Blau führt immer etwas Dunkles mit sich›; ‹wie wir den hohen Himmel, die fernen Berge blau sehen› – Ferne, Nacht und Himmel: Mathematik und Astronomie.",
     "para": "§§ 778, 780"},
    {"key": "ssw",   "ort": "Blaurot",          "sph": "phantasie",    "H": 298, "L": 0.52, "C": 0.160,
     "grund": "Blau ‹steigert sich sehr sanft ins Rote› und wird wirksam; man wünscht ‹mit dieser Farbe immer fortzugehen›. Goethes Sphäre dafür heisst Phantasie – Sprache, Dichtung, Geistesgeschichte.",
     "para": "§§ 787–788"},
    {"key": "sbk",   "ort": "Lila, zum Purpur", "sph": "phantasie",    "H": 325, "L": 0.62, "C": 0.170,
     "grund": "Das verdünnte Blaurot, Lila, hat ‹etwas Lebhaftes›, und die Steigerung strebt ‹zu dem Kardinalpurpur hinauf›: Phantasie auf dem Weg zum Schönen – die bildenden Künste.",
     "para": "§§ 789, 791"},
]

# --- Ausnahmen des Rezepts für warme, helle Töne --------------------------------
# Das Rezept (sek-varianten.py) legt die dunkle Fläche auf L 0.47. Gelb und Orange
# sind dort Braun (die Form des sRGB-Körpers, kein Fehler) – wie beim Kürbis-Beschluss
# vom 8. September 2026 stehen sie darum heller und schöpfen ihre Buntheit aus.
AUSNAHMEN = {
    "ps":    {"dunkel": {"L": 0.58, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0},
              "ink":    {"L": 0.52, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0}},
    "hpise": {"dunkel": {"L": 0.56, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0},
              "ink":    {"L": 0.50, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0}},
    "js":    {"dunkel": {"L": 0.54, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0},
              "ink":    {"L": 0.49, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0}},
    "szw":   {"dunkel": {"L": 0.52, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0},
              "ink":    {"L": 0.48, "spanne": 0, "C_max": 0.20, "C_faktor": 1.0}},
    "lws":   {"dunkel": {"L": 0.50, "spanne": 0, "C_max": 0.20, "C_faktor": 0.9},
              "ink":    {"L": 0.46, "spanne": 0, "C_max": 0.20, "C_faktor": 0.9}},
}
AA, ZIEL_WEISS = 4.5, 5.0

def theme_tokens():
    """--paper/--soft/--ink je Theme aus tokens.css (erste Definition = hell, zweite = dunkel)."""
    css = open(TOKENS_CSS, encoding="utf-8").read()
    out = {}
    for name in ("paper", "soft", "ink"):
        vals = re.findall(r"--%s\s*:\s*(#[0-9a-fA-F]{3,6})" % name, css)
        out[name] = (vals[0].lower(), vals[1].lower())
    return out

def orgs():
    js = open(ORGS_JS, encoding="utf-8").read()
    m = re.search(r"const GCI_ORGS = (\{.*?\});", js, re.S)
    return json.loads(m.group(1))

def winkel(H):
    """OKLCH-Farbton → Platz auf Goethes Kreis (Grad, Purpur = 0, im Uhrzeigersinn)."""
    h = (H - 350) % 360
    pts = [((a[2] - 350) % 360, a[1]) for a in ANKER] + [(360, 360)]
    for (h0, w0), (h1, w1) in zip(pts, pts[1:]):
        if h0 <= h <= h1:
            return round(w0 + (w1 - w0) * (h - h0) / (h1 - h0), 1)
    return 0.0

def ableiten(H, L, C, rolle, key, pos):
    r = dict(sv.REZEPT[rolle]); r.update(AUSNAHMEN.get(key, {}).get(rolle, {}))
    return sv.from_oklch(r["L"] + r.get("spanne", 0) * pos, min(C * r["C_faktor"], r["C_max"]), H)

def sichern(hexv, H, C, pruef, schritt=-0.01):
    """Helligkeit in Hundertstel-Schritten verschieben, bis pruef(hex) wahr ist."""
    L, Cc, _ = sv.to_oklch(hexv)
    for _ in range(40):
        if pruef(hexv):
            return hexv
        L += schritt
        hexv = sv.from_oklch(L, Cc, H)
    raise SystemExit("keine Helligkeit gefunden für H %s" % H)

def palette():
    T = theme_tokens(); O = orgs()
    Ls = [s["L"] for s in ORDNUNG]; lo, hi = min(Ls), max(Ls)
    out = []
    for s in ORDNUNG:
        H, L, C = s["H"], s["L"], s["C"]
        pos = (L - lo) / (hi - lo) - 0.5
        basis = sv.from_oklch(L, C, H)
        # Vordergrund auf der Basis: Weiss, wo es hält – sonst ein tiefer Ton der Sektion.
        if sv.kontrast(basis, "#ffffff") >= AA:
            on = "#fff"
        else:
            on = sichern(sv.from_oklch(0.30, min(C, 0.09), H), H, C, lambda x: sv.kontrast(x, basis) >= AA)
        dunkel = sichern(ableiten(H, L, C, "dunkel", s["key"], pos), H, C, lambda x: sv.kontrast(x, "#ffffff") >= ZIEL_WEISS)
        hell = ableiten(H, L, C, "hell", s["key"], pos)
        hell_dk = ableiten(H, L, C, "hell_dk", s["key"], pos)
        ink = sichern(ableiten(H, L, C, "ink", s["key"], pos), H, C,
                      lambda x: min(sv.kontrast(x, T["paper"][0]), sv.kontrast(x, T["soft"][0]), sv.kontrast(x, hell)) >= AA)
        ink_dk = sichern(ableiten(H, L, C, "ink_dk", s["key"], pos), H, C,
                         lambda x: min(sv.kontrast(x, T["paper"][1]), sv.kontrast(x, T["soft"][1]), sv.kontrast(x, hell_dk)) >= AA, +0.01)
        o = O.get(s["key"], {})
        anker = min(ANKER, key=lambda a: min(abs(winkel(H) - a[1]), 360 - abs(winkel(H) - a[1])))
        out.append({
            "key": s["key"], "name": o.get("name_de", s["key"]), "kurz": o.get("short_de", s["key"]),
            "ort": s["ort"], "sphaere": s["sph"], "sektor": anker[0], "wort": anker[3],
            "winkel": winkel(H), "H": H, "L": L, "C": C,
            "basis": basis, "on": on, "dunkel": dunkel, "hell": hell, "hell_dk": hell_dk,
            "ink": ink, "ink_dk": ink_dk, "heute": (o.get("color") or "").lower(),
            "heute_winkel": winkel(sv.to_oklch(o["color"])[2]) if o.get("color") else None,
            "grund": s["grund"], "para": s["para"],
            "kontrast": {
                "weiss_auf_basis": round(sv.kontrast(basis, "#ffffff"), 2),
                "on_auf_basis": round(sv.kontrast(basis, on if on != "#fff" else "#ffffff"), 2),
                "weiss_auf_dunkel": round(sv.kontrast(dunkel, "#ffffff"), 2),
                "ink_auf_hell": round(sv.kontrast(T["ink"][0], hell), 2),
                "tinte_auf_papier": round(sv.kontrast(ink, T["paper"][0]), 2),
                "tinte_auf_hell": round(sv.kontrast(ink, hell), 2),
                "tinte_dk_auf_papier": round(sv.kontrast(ink_dk, T["paper"][1]), 2),
                "tinte_dk_auf_hell": round(sv.kontrast(ink_dk, hell_dk), 2),
                "ink_dk_auf_hell_dk": round(sv.kontrast(T["ink"][1], hell_dk), 2),
            }})
    return out

def harmonien(pal):
    """Goethe § 810: der bewegliche Durchmesser – jede Farbe fordert ihre Gegenfarbe.
    Für jede Sektion die Sektion, die ihrem Gegenüber am nächsten liegt."""
    def gegen(a):
        ziel = (a["winkel"] + 180) % 360
        return min((p for p in pal if p is not a), key=lambda p: min(abs(p["winkel"] - ziel), 360 - abs(p["winkel"] - ziel)))
    paare, seen = [], set()
    for a in pal:
        b = gegen(a)
        if gegen(b) is not a: continue          # nur, wo beide einander fordern
        k = tuple(sorted((a["key"], b["key"])))
        if k in seen: continue
        seen.add(k); paare.append({"a": a["key"], "b": b["key"]})
    return paare

def schreiben(pal):
    daten = {"$quelle": "GENERIERT von tools/sek-goethe.py – nicht von Hand ändern. Goethe, Zur Farbenlehre (1810), Didaktischer Teil, 6. Abteilung, §§ 758–829; Farbenkreis 1809 (Freies Deutsches Hochstift).",
             "anker": [{"name": a[0], "winkel": a[1], "H": a[2], "wort": a[3], "hex": sv.from_oklch(a[4], a[5], a[2])} for a in ANKER],
             "sphaeren": SPHAEREN, "sektionen": pal, "harmonien": harmonien(pal)}
    js = "/* GENERIERT von tools/sek-goethe.py – nicht von Hand ändern. */\nwindow.GOE_SEK_GOETHE = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n"
    alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
    if alt != js:
        open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
    else:
        print("unverändert:", os.path.relpath(OUT_JS, ROOT))

def main():
    pal = palette()
    print("%-6s %-18s %-13s %6s  %-7s %-7s %-7s %-7s %-7s %-7s  Weiss/dunkel Tinte/Papier Tinte/hell Ink/hell dk:Tinte/Papier dk:Tinte/hell" %
          ("Key", "Ort", "Sphäre", "Winkel", "Basis", "on", "dunkel", "hell", "ink", "ink_dk"))
    schlecht = 0
    for p in pal:
        k = p["kontrast"]
        werte = [k["weiss_auf_dunkel"], k["tinte_auf_papier"], k["tinte_auf_hell"], k["ink_auf_hell"], k["tinte_dk_auf_papier"], k["tinte_dk_auf_hell"], k["on_auf_basis"]]
        if min(werte) < AA: schlecht += 1
        print("%-6s %-18s %-13s %6.1f  %-7s %-7s %-7s %-7s %-7s %-7s  %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f  on %.2f" %
              (p["key"], p["ort"], p["sphaere"], p["winkel"], p["basis"], p["on"], p["dunkel"], p["hell"], p["ink"], p["ink_dk"], *werte))
    print("\nHarmonien (§ 810, Gegenüber auf dem Kreis):")
    for h in harmonien(pal):
        print("  %s ↔ %s" % (h["a"], h["b"]))
    if schlecht:
        raise SystemExit("%d Sektion(en) unter 4.5:1" % schlecht)
    if "--apply" in sys.argv:
        schreiben(pal)

if __name__ == "__main__":
    main()
