#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Farbmodell der Sektionen – fünf Stufen je Farbe, jede mit einer Aufgabe (Labor).

Die eine Farbe, die zugleich leuchten, Weiss tragen und als Schrift stehen soll,
war überfordert: an der 4.5-Grenze wird Orange braun und Gelb Ocker. Das Modell
trennt die Aufgaben. Je Sektion (Farbtöne der Fassung 3, ohne Gelb):

  leuchten  Erkennungsfarbe – volle Buntheit, hellste Stufe für 3:1 auf Papier.
            Trägt als Objekt (Marke, Linie, Punkt, Diagramm, Wallpaper) und
            grosse weisse Schrift (≥ 24 px); nie Lesetext.        WCAG 1.4.11
  tinte     die Sektion als Schrift – volle Buntheit, hellste Stufe für 4.5:1
            auf Papier, Karte und Hauch.                           WCAG 1.4.3
  grund     matte tiefe Fläche – trägt Weiss auch klein (≥ 5.5:1). Kopfband,
            Knopf, Titelfeld. Rezept wie tools/sek-varianten.py «dunkel».
  pastell   helle bunte Fläche – trägt Lesetext in --ink (≥ 7:1). Plakat,
            Folie, Wallpaper, Seitenhintergrund. NEU.
  hauch     ein Farbhauch über Papier – trägt --ink und die Tinte. Chip,
            Hinweis, markierte Zeile. Rezept «hell».
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
sgv = _lade("sek-goethe-varianten")

T = sg.theme_tokens()
WEISS, SOFT, INK = "#ffffff", T["soft"][0], T["ink"][0]
PAPER_DK, SOFT_DK, INK_DK = T["paper"][1], T["soft"][1], T["ink"][1]

STUFEN = [
    {"id": "hauch",    "name": "Hauch",    "traegt": "Lesetext in --ink und die Tinte",
     "faelle": "Chip, Hinweiskasten, markierte Tabellenzeile, aktives Feld, Zeile im Menü",
     "regel": "Tinte darauf ≥ 4.5:1 (1.4.3)"},
    {"id": "pastell",  "name": "Pastell",  "traegt": "Lesetext in --ink, die Marke in Tinte oder Grund",
     "faelle": "Plakat, Folienhintergrund, Wallpaper, Hintergrund einer Sektionsseite, grosse Kachel",
     "regel": "--ink darauf ≥ 7:1 (1.4.6); Tinte darauf ≥ 3:1 als Objekt"},
    {"id": "leuchten", "name": "Leuchten", "traegt": "grosse weisse Schrift (≥ 24 px) – keinen Lesetext",
     "faelle": "Marke und Logo, Linie und Kante, Punkt im Menü, Diagramm, Wallpaper-Motiv, Plakattitel gross in Weiss, Icon",
     "regel": "auf Papier ≥ 3:1 als Objekt (1.4.11); Weiss darauf ≥ 3:1 nur gross (1.4.3)"},
    {"id": "tinte",    "name": "Tinte",    "traegt": "sich selbst als Schrift",
     "faelle": "Kicker, Link, Titel in Sektionsfarbe, Zahl, Label, Icon neben Text, Schrift im Chip",
     "regel": "auf Papier, Karte und Hauch ≥ 4.5:1 (1.4.3)"},
    {"id": "grund",    "name": "Grund",    "traegt": "Weiss, auch klein",
     "faelle": "Kopfband, Titelfeld, Knopf, Fusszeile, Auswahl, tiefe Fläche im Dunkelmodus",
     "regel": "Weiss darauf ≥ 5.5:1 (B01, Ziel über AA)"},
]

def stufen(H, key, pos):
    C_voll = sgv.max_C(0.6, H)
    leuchten = sgv.an_der_grenze(H, 3.0)
    hauch = sv.from_oklch(0.965, min(C_voll * 0.20, 0.022), H)
    pastell = sv.from_oklch(0.86, min(C_voll * 0.60, 0.09), H)
    # Tinte: hellste Stufe voller Buntheit, die auf Papier, Karte und Hauch hält.
    L = 0.9
    while True:
        C = sgv.max_C(L, H); hx = sv.from_oklch(L, C, H)
        if min(sv.kontrast(hx, WEISS), sv.kontrast(hx, SOFT), sv.kontrast(hx, hauch)) >= 4.5: break
        L -= 0.0025
    tinte = hx
    tL, tC, _ = sv.to_oklch(tinte)
    # Grund: Rezept «dunkel» (L 0.47 ± Spanne, vier Fünftel der Buntheit), mind. 0.05 unter der Tinte.
    r = sv.REZEPT["dunkel"]
    grund = sv.from_oklch(min(r["L"] + r["spanne"] * pos, tL - 0.05), min(tC * r["C_faktor"], r["C_max"]), H)
    while sv.kontrast(grund, WEISS) < 5.5:
        gL, gC, _ = sv.to_oklch(grund); grund = sv.from_oklch(gL - 0.01, gC, H)
    hauch_dk = sv.from_oklch(0.27, min(C_voll * 0.25, 0.035), H)
    r = sv.REZEPT["ink_dk"]
    tinte_dk = sv.from_oklch(r["L"] + r["spanne"] * pos, min(tC * r["C_faktor"], r["C_max"]), H)
    while min(sv.kontrast(tinte_dk, PAPER_DK), sv.kontrast(tinte_dk, hauch_dk)) < 4.5:
        dL, dC, _ = sv.to_oklch(tinte_dk); tinte_dk = sv.from_oklch(dL + 0.01, dC, H)
    return {"hauch": hauch, "pastell": pastell, "leuchten": leuchten, "tinte": tinte, "grund": grund,
            "hauch_dk": hauch_dk, "tinte_dk": tinte_dk}

def modell():
    O = sg.orgs()
    Ls = [sv.to_oklch(s["basis"])[0] for s in sg.palette()]
    lo, hi = min(Ls), max(Ls)
    out = []
    for s, L in zip(sg.ORDNUNG, Ls):
        pos = (L - lo) / (hi - lo) - 0.5
        st = stufen(s["H"], s["key"], pos)
        k = {"leuchten_papier": sv.kontrast(st["leuchten"], WEISS), "weiss_auf_leuchten": sv.kontrast(st["leuchten"], WEISS),
             "tinte_papier": sv.kontrast(st["tinte"], WEISS), "tinte_karte": sv.kontrast(st["tinte"], SOFT),
             "tinte_hauch": sv.kontrast(st["tinte"], st["hauch"]), "weiss_grund": sv.kontrast(st["grund"], WEISS),
             "ink_pastell": sv.kontrast(INK, st["pastell"]), "tinte_pastell": sv.kontrast(st["tinte"], st["pastell"]),
             "ink_hauch": sv.kontrast(INK, st["hauch"]), "tinte_dk_papier": sv.kontrast(st["tinte_dk"], PAPER_DK),
             "tinte_dk_hauch": sv.kontrast(st["tinte_dk"], st["hauch_dk"]), "ink_dk_hauch_dk": sv.kontrast(INK_DK, st["hauch_dk"])}
        out.append({"key": s["key"], "name": O[s["key"]]["name_de"], "kurz": O[s["key"]]["short_de"],
                    "ort": s["ort"], "H": s["H"], "heute": O[s["key"]]["color"].lower(),
                    "stufen": st, "kontrast": {a: round(b, 2) for a, b in k.items()}})
    return out

def main():
    M = modell()
    print("%-6s %-8s %-8s %-8s %-8s %-8s | Leucht/Papier Tinte/Papier Tinte/Karte Tinte/Hauch Weiss/Grund Ink/Pastell Tinte/Pastell" %
          ("Key", "hauch", "pastell", "leuchten", "tinte", "grund"))
    schlecht = 0
    for m in M:
        s, k = m["stufen"], m["kontrast"]
        ok = k["leuchten_papier"] >= 3 and k["tinte_papier"] >= 4.5 and k["tinte_karte"] >= 4.5 and k["tinte_hauch"] >= 4.5 \
             and k["weiss_grund"] >= 5.5 and k["ink_pastell"] >= 7 and k["tinte_pastell"] >= 3 and k["tinte_dk_papier"] >= 4.5 and k["tinte_dk_hauch"] >= 4.5
        schlecht += not ok
        print("%-6s %s %s %s %s %s | %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %s" %
              (m["key"], s["hauch"], s["pastell"], s["leuchten"], s["tinte"], s["grund"], k["leuchten_papier"], k["tinte_papier"],
               k["tinte_karte"], k["tinte_hauch"], k["weiss_grund"], k["ink_pastell"], k["tinte_pastell"], "" if ok else "✗"))
    if schlecht:
        raise SystemExit("%d Sektion(en) verletzen das Modell" % schlecht)
    if "--apply" in sys.argv:
        daten = {"$quelle": "GENERIERT von tools/sek-modell.py – nicht von Hand ändern.", "stufen": STUFEN, "sektionen": M,
                 "theme": {"paper": [WEISS, PAPER_DK], "soft": [SOFT, SOFT_DK], "ink": [INK, INK_DK]}}
        js = "/* GENERIERT von tools/sek-modell.py – nicht von Hand ändern. */\nwindow.GOE_SEK_MODELL = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n"
        alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
        if alt != js:
            open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
        else:
            print("unverändert:", os.path.relpath(OUT_JS, ROOT))

if __name__ == "__main__":
    main()
