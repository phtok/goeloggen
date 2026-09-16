#!/usr/bin/env python3
# Generischer Version-Bump für die ausgelieferten Schriften (Standard 2.6 -> 2.7).
# Transformiert die vorhandenen OTFs (statische Schnitte + Variable) auf die neue
# Version: name-Tabelle (nameID 3 + 5) und head.fontRevision werden gesetzt, die
# OTFs unter neuem Versionsnamen gespeichert, die alten Binärdateien entfernt und
# die Webfonts (woff/woff2) neu aus den neuen OTFs gezogen. Idempotent: läuft
# auch erneut, wenn schon die Zielversion vorliegt (dann no-op).
# Aufruf:  python3 bump_version.py [ALT] [NEU]     (Default 2.6 2.7)
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
FONTS = os.path.join(ROOT, "Fonts"); VAR = os.path.join(ROOT, "Variable")
WF2 = os.path.join(ROOT, "Webfonts/woff2"); WF = os.path.join(ROOT, "Webfonts/woff")
OLD = sys.argv[1] if len(sys.argv) > 1 else "2.6"
NEW = sys.argv[2] if len(sys.argv) > 2 else "2.7"

def bump_font(path):
    ft = TTFont(path)
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):                       # Unique ID + Version-String
            s = rec.toUnicode()
            if OLD in s: rec.string = s.replace(OLD, NEW)
    ft["head"].fontRevision = float(NEW)
    out = path.replace("v%s" % OLD, "v%s" % NEW)
    ft.save(out)
    if out != path and os.path.exists(path): os.remove(path)
    return out

def main():
    otfs = sorted(glob.glob(os.path.join(FONTS, "*-v%s*.otf" % OLD)) +
                  glob.glob(os.path.join(VAR, "*-v%s.otf" % OLD)))
    if not otfs:
        print("keine v%s-OTFs gefunden — evtl. schon gebumpt" % OLD); return
    new_otfs = []
    for p in otfs:
        out = bump_font(p); new_otfs.append(out)
        print("  ", os.path.basename(p), "->", os.path.basename(out),
              "Version", TTFont(out)["name"].getDebugName(5))
    # alte Webfonts weg
    for d in (WF, WF2):
        for f in glob.glob(os.path.join(d, "*-v%s*" % OLD)): os.remove(f)
    # Webfonts neu aus den neuen OTFs
    for p in new_otfs:
        base = os.path.splitext(os.path.basename(p))[0]
        for flv, d in (("woff", WF), ("woff2", WF2)):
            f = TTFont(p); f.flavor = flv; f.save(os.path.join(d, "%s.%s" % (base, flv)))
    print("  Webfonts neu (%d OTFs)" % len(new_otfs))

if __name__ == "__main__":
    main(); print("Bump %s -> %s fertig" % (OLD, NEW))
