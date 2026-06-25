#!/usr/bin/env python3
# Baut das Versaleszett ẞ (U+1E9E, Entwurf 5 von Philipp, Stamm auf Klar 82
# angeglichen) in die Goetheanum Schrift KLAR ein. Idempotent: überspringt,
# wenn U+1E9E schon belegt ist. Die Glyphendaten liegen in eszett-klar.json
# (Recording + Advance), aus dem emboldneten Entwurf 5 abgeleitet.
# Andere Schnitte (Leise/Deutlich/Laut/Variable) folgen separat zur Abnahme.
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_specials as BS
from fontTools.ttLib import TTFont
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
KLAR = os.path.join(REPO, "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.5-Klar.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
DATA = os.path.join(HERE, "eszett-klar.json")

def main():
    g = json.load(open(DATA))
    rec = [(op, tuple(tuple(p) for p in pts)) for op, pts in g["recording"]]
    ft = TTFont(KLAR)
    if g["unicode"] in ft.getBestCmap():
        print("ẞ schon vorhanden — übersprungen")
    else:
        nm = BS.add_glyph(ft, rec, g["advance"], g["lsb"], g["unicode"])
        ft.save(KLAR); print("ẞ eingebaut als", nm)
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(KLAR); f.flavor = flv
        f.save(os.path.join(WF, sub, "Goetheanum-Schrift-v2.5-Klar.%s" % flv))
    print("Webfonts neu")

if __name__ == "__main__":
    main()
