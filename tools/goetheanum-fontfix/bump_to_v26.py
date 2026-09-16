#!/usr/bin/env python3
# Version-Bump 2.5 -> 2.6 für die ausgelieferten Schriften. Transformiert die
# vorhandenen v2.5-Dateien (mit allen Zugängen: Versaleszett, pnum/lnum,
# Deutlich) auf 2.6: name-Tabelle (nameID 3 + 5) und head.fontRevision werden
# gesetzt, die OTFs unter v2.6-Namen gespeichert, die alten v2.5-Binärdateien
# entfernt und die Webfonts (woff/woff2) neu aus den v2.6-OTFs gezogen.
# Idempotent: läuft auch erneut, wenn schon v2.6 vorliegt (dann no-op).
import os, sys, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
FONTS = os.path.join(ROOT, "Fonts"); VAR = os.path.join(ROOT, "Variable")
WF2 = os.path.join(ROOT, "Webfonts/woff2"); WF = os.path.join(ROOT, "Webfonts/woff")
OLD, NEW = "2.5", "2.6"

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
    # alte v2.5-Webfonts weg
    for d in (WF, WF2):
        for f in glob.glob(os.path.join(d, "*-v%s*" % OLD)): os.remove(f)
    # Webfonts neu aus den v2.6-OTFs
    for p in new_otfs:
        base = os.path.splitext(os.path.basename(p))[0]
        for flv, d in (("woff", WF), ("woff2", WF2)):
            f = TTFont(p); f.flavor = flv; f.save(os.path.join(d, "%s.%s" % (base, flv)))
    print("  Webfonts neu (%d OTFs)" % len(new_otfs))

if __name__ == "__main__":
    main(); print("Bump auf v%s fertig" % NEW)
