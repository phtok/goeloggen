#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Farbmodell der Sektionen – fünf Stufen je Farbe, jede mit einer Aufgabe (Labor).

Zweite Fassung des Modells (Rückmeldung 9. 9. 2026: Leuchten mit voller
Buntheit war Neon, der Grund stumpf; dazwischen fehlte die Farbe, die man
kennt). Der Gesamtcharakter der heutigen Sektionsfarben ist gedeckt-natürlich:
Buntheit (OKLCH C) 0.09 bis 0.19, im Mittel 0.14 – Pigment, nicht Licht. Diese
Buntheit ist jetzt die Buntheit der Reihe. Je Sektion (Farbtöne der Fassung 3):

  leuchten  Erkennungsfarbe – natürliche Buntheit, hellste Stufe für 3:1 auf
            Papier: der Charakter von heute. Marke, Linie, Punkt, Diagramm,
            Wallpaper; Weiss darauf nur gross (≥ 24 px).          WCAG 1.4.11
  grund     dieselbe Buntheit, tief genug für Weiss auch klein (≥ 4.5:1) –
            Kopfband, Knopf, Titelfeld, Fusszeile, tiefe Fläche im Dunkelmodus.
            = Basis der Fassung 3. (Der frühere «Kern»; der frühere Grund war
            fast derselbe Ton und entfällt – Anmerkung 10. 9. 2026.)
  tinte     eigene Stufe für Schrift auf Weiss – etwas mehr Buntheit, tiefer
            als der Grund (≥ 5.5:1 auf Papier, ≥ 5:1 auf Karte, ≥ 4.5:1 auf Hauch).
  pastell   ganz zarte Fläche für Plakat, Folie, Wallpaper – trägt Marke und
            Bild, aber keinen Text: Text steht auf einem Papierfeld darauf.
            (Schwarz auf Farbe ist verboten; nur der ganz zarte Hauch trägt
            dunklen Text – Anmerkung 9./10. 9. 2026.)
  hauch     ein Farbhauch über Papier – Chip, Hinweis. Rezept «hell».
  warm      Orange und Rotgelb dunkeln nicht ins Braun: Grund und Tinte der
            warmen Töne (H 30–110) rücken 15° zum Rot und nehmen die volle
            Buntheit – Terracotta statt Braun.
  gelb      selbstlos (Pädagogik): Leuchten ist reines Gelb, es trägt keine
            Schrift und kein Weiss; Tinte und Grund sind das reine Haus-Schwarz
            (--ink), kein getöntes Grau. So bleibt Gold der Bühne. Die
            Landwirtschaft behält ihr etabliertes Grün #63b145 als Leuchten exakt.
Dunkelmodus: hauch_dk und tinte_dk aus dem Rezept; leuchten und grund sind
markenfest; Pastell weicht dem Grund.

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-modell.py            Vorschau (Werte, Kontraste)
  python3 tools/sek-modell.py --apply    schreibt assets/sek-modell.js (idempotent)
Die Seite sektionsfarben-modell.html liest diese Datei.
"""
import json, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, "assets", "sek-modell.js")

def _lade(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

sv = _lade("sek-varianten")
sg = _lade("sek-goethe")

T = sg.theme_tokens()
WEISS, SOFT, INK = "#ffffff", T["soft"][0], T["ink"][0]
PAPER_DK, SOFT_DK, INK_DK = T["paper"][1], T["soft"][1], T["ink"][1]

# Natürliche Buntheit je Sektion: die Buntheit von heute, auf die Reihe geglättet
# (0.11 bis 0.17; Rot und Orange dürfen mehr, Meergrün und Violett weniger).
C_NAT = {"aas": 0.14, "sbk": 0.14, "szw": 0.17, "js": 0.17, "hpise": 0.15, "lws": 0.163,
         "nws": 0.11, "ps": 0.17, "srmk": 0.13, "mas": 0.14, "ssw": 0.14, "ms": 0.12}
# Feste Werte: etabliertes Grün der Landwirtschaft (Leuchten exakt); reines Gelb der Pädagogik.
FEST_LEUCHTEN = {"lws": "#63b145", "ps": None}
SELBSTLOS = {"ps"}   # keine eigenen Schriftstufen – Tinte und Grund sind das Haus-Schwarz

STUFEN = [
    {"id": "hauch",    "name": "Hauch",    "traegt": "Lesetext in --ink und die Tinte",
     "faelle": "Chip, Hinweiskasten, markierte Tabellenzeile, aktives Feld, Zeile im Menü",
     "regel": "Tinte darauf ≥ 4.5:1 (1.4.3)"},
    {"id": "pastell",  "name": "Pastell",  "traegt": "die Marke in Leuchten oder Grund, Bild – keinen Text",
     "faelle": "Plakat, Folienhintergrund, Wallpaper, Hintergrund einer Sektionsseite, grosse Kachel; Text darauf steht auf einem Papierfeld",
     "regel": "kein Schwarz auf Farbe; Grund darauf ≥ 3:1 als Objekt (1.4.11)"},
    {"id": "leuchten", "name": "Leuchten", "traegt": "Objekte und grosse weisse Schrift (≥ 24 px) – keinen Lesetext",
     "faelle": "Marke und Logo, Linie und Kante, Punkt im Menü, Diagramm, Wallpaper-Motiv, Plakattitel gross in Weiss, Icon",
     "regel": "auf Papier ≥ 3:1 als Objekt (1.4.11); Weiss darauf ≥ 3:1 nur gross"},
    {"id": "tinte",    "name": "Tinte",    "traegt": "sich selbst als Schrift auf Papier und Hauch",
     "faelle": "Kicker, Link, Titel in Sektionsfarbe, Zahl, Label, Icon neben Text, Schrift im Chip",
     "regel": "auf Papier ≥ 5.5:1, auf Karte ≥ 5:1, auf Hauch ≥ 4.5:1 (1.4.3)"},
    {"id": "grund",    "name": "Grund",    "traegt": "Weiss, auch klein",
     "faelle": "Kopfband, Titelfeld, Knopf, Auswahl, Fusszeile, Hintergrundelement, tiefe Fläche im Dunkelmodus",
     "regel": "Weiss darauf ≥ 4.5:1 (1.4.3, B01)"},
]

def hellste(H, C, pruef):
    """Hellste OKLCH-Stufe (Schritt 0.0025), bei der pruef(hex) hält; Buntheit
    wird am Gamut-Rand automatisch gesenkt (sek-varianten.from_oklch)."""
    L = 0.92
    while L > 0.15:
        hx = sv.from_oklch(L, C, H)
        if pruef(hx): return hx
        L -= 0.0025
    raise SystemExit("keine Stufe für H %s" % H)

def warm_verschiebung(H):
    """Orange und Rotgelb (H 30–110) dunkeln ins Braun; ihre tiefen Stufen rücken 15° zum Rot."""
    return -15 if 30 <= H <= 110 else 0

def stufen(key, H, grund, pos):
    C = C_NAT[key]
    Hd = (H + warm_verschiebung(H)) % 360   # Farbton der tiefen Stufen
    leuchten = hellste(H, C, lambda x: sv.kontrast(x, WEISS) >= 3.0)
    if key in SELBSTLOS:
        leuchten = sv.from_oklch(0.88, C, H)              # reines Gelb, ohne Kontrastpflicht
    elif FEST_LEUCHTEN.get(key):
        leuchten = FEST_LEUCHTEN[key]
    hauch = sv.from_oklch(0.965, min(C * 0.16, 0.022), H)
    pastell = sv.from_oklch(0.94, min(C * 0.4, 0.045), H)   # ganz zart, trägt keinen Text
    tinte = hellste(Hd, C + 0.03, lambda x: sv.kontrast(x, WEISS) >= 5.5 and sv.kontrast(x, SOFT) >= 5.0 and sv.kontrast(x, hauch) >= 4.5)
    if warm_verschiebung(H):
        # Grund der warmen Töne: natürliche Buntheit plus ein wenig, zum Rot gerückt, hellste Stufe für 4.6:1 – Terracotta statt Braun.
        grund = hellste(Hd, C + 0.04, lambda x: sv.kontrast(x, WEISS) >= 4.6)
    hauch_dk = sv.from_oklch(0.27, min(C * 0.25, 0.035), H)
    r = sv.REZEPT["ink_dk"]
    tinte_dk = sv.from_oklch(r["L"] + r["spanne"] * pos, min(C * r["C_faktor"], r["C_max"]), H)
    while min(sv.kontrast(tinte_dk, PAPER_DK), sv.kontrast(tinte_dk, hauch_dk)) < 4.5:
        dL, dC, _ = sv.to_oklch(tinte_dk); tinte_dk = sv.from_oklch(dL + 0.01, dC, H)
    if key in SELBSTLOS:
        # Gelb tritt zurück: Tinte und Grund sind das reine Haus-Schwarz.
        tinte = INK; grund = INK; tinte_dk = INK_DK
    return {"hauch": hauch, "pastell": pastell, "leuchten": leuchten, "tinte": tinte, "grund": grund,
            "hauch_dk": hauch_dk, "tinte_dk": tinte_dk}

def modell():
    O = sg.orgs(); pal = sg.palette()
    Ls = [sv.to_oklch(p["basis"])[0] for p in pal]
    lo, hi = min(Ls), max(Ls)
    out = []
    for s, p, L in zip(sg.ORDNUNG, pal, Ls):
        pos = (L - lo) / (hi - lo) - 0.5
        st = stufen(s["key"], s["H"], p["basis"], pos)
        k = {"leuchten_papier": sv.kontrast(st["leuchten"], WEISS),
             "tinte_papier": sv.kontrast(st["tinte"], WEISS), "tinte_karte": sv.kontrast(st["tinte"], SOFT),
             "tinte_hauch": sv.kontrast(st["tinte"], st["hauch"]), "weiss_grund": sv.kontrast(st["grund"], WEISS),
             "grund_pastell": sv.kontrast(st["grund"], st["pastell"]),
             "tinte_dk_papier": sv.kontrast(st["tinte_dk"], PAPER_DK), "tinte_dk_hauch": sv.kontrast(st["tinte_dk"], st["hauch_dk"])}
        out.append({"key": s["key"], "name": O[s["key"]]["name_de"], "kurz": O[s["key"]]["short_de"],
                    "ort": s["ort"], "satz": s.get("satz", ""), "para": s["para"], "H": s["H"], "winkel": sg.winkel(s["H"]),
                    "heute": O[s["key"]]["color"].lower(), "selbstlos": s["key"] in SELBSTLOS, "fest": bool(FEST_LEUCHTEN.get(s["key"])),
                    "stufen": st, "kontrast": {a: round(b, 2) for a, b in k.items()}})
    return out

def main():
    M = modell()
    print("%-6s %-8s %-8s %-8s %-8s %-8s | Leucht/Pap Tinte/Pap Tinte/Karte Tinte/Hauch Weiss/Grund Grund/Pastell" %
          ("Key", "hauch", "pastell", "leuchten", "tinte", "grund"))
    schlecht = 0
    for m in M:
        s, k = m["stufen"], m["kontrast"]
        ok = (k["leuchten_papier"] >= 3 or m["key"] in SELBSTLOS or FEST_LEUCHTEN.get(m["key"])) and k["tinte_papier"] >= 5.5 and k["tinte_karte"] >= 4.5 and k["tinte_hauch"] >= 4.5 \
             and k["weiss_grund"] >= 4.5 and k["grund_pastell"] >= 3 and k["tinte_dk_papier"] >= 4.5 and k["tinte_dk_hauch"] >= 4.5
        schlecht += not ok
        print("%-6s %s %s %s %s %s | %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %s" %
              (m["key"], s["hauch"], s["pastell"], s["leuchten"], s["tinte"], s["grund"], k["leuchten_papier"],
               k["tinte_papier"], k["tinte_karte"], k["tinte_hauch"], k["weiss_grund"], k["grund_pastell"], "" if ok else "✗"))
    if schlecht:
        raise SystemExit("%d Sektion(en) verletzen das Modell" % schlecht)
    if "--apply" in sys.argv:
        daten = {"$quelle": "GENERIERT von tools/sek-modell.py – nicht von Hand ändern.", "stufen": STUFEN, "sektionen": M,
                 "anker": [{"name": a[0], "winkel": a[1], "hex": sv.from_oklch(a[3], a[4], a[2])} for a in sg.ANKER],
                 "sphaeren": sg.SPHAEREN, "sonder": [dict(x, winkel=sg.winkel(x["H"])) for x in sg.SONDER],
                 "theme": {"paper": [WEISS, PAPER_DK], "soft": [SOFT, SOFT_DK], "ink": [INK, INK_DK]}}
        js = "/* GENERIERT von tools/sek-modell.py – nicht von Hand ändern. */\nwindow.GOE_SEK_MODELL = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n"
        alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
        if alt != js:
            open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
        else:
            print("unverändert:", os.path.relpath(OUT_JS, ROOT))

if __name__ == "__main__":
    main()
