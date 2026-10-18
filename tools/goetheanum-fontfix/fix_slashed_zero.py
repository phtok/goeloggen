#!/usr/bin/env python3
# Säubert die schlummernde Null (Feature ‹zero›, Glyphe cid00626) in den
# statischen Schnitten: der Schrägstrich lag als eigene, roh überlappende Kontur
# über dem Oval – an den Überschneidungen entstanden an kleinen Graden sichtbare
# Knoten/Kerben (die Schräg-Spitze bekam eine Stufe, wo sie das Oval kreuzt).
# Die Boolesche Vereinigung (skia-pathops) legt die drei Konturen zu sauberen,
# überschneidungsfreien Umrissen zusammen; die Silhouette bleibt, der Knoten geht.
# Idempotent: erneut ausgeführt ist die schon vereinigte Glyphe ein No-op.
# Reproduzierbar (keine Handpatches); danach Webfonts/Office/ZIPs neu bauen.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
import pathops
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
GLYPH = "cid00626"     # slashed zero (zero -> zero.slashed)

def union_glyph(ft, name):
    gs = ft.getGlyphSet()
    if name not in gs: return False
    width = gs[name].width
    p = pathops.Path()
    gs[name].draw(p.getPen())
    p.simplify()                                   # union + winding-korrekt, overlap-frei
    pen = T2CharStringPen(width, None)
    p.draw(pen)
    cff = ft["CFF "].cff
    cs = cff[cff.fontNames[0]].CharStrings[name]
    cs.bytecode = None
    cs.program = pen.getCharString().program
    return True

def webfonts(src):
    b = os.path.splitext(os.path.basename(src))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(src); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))

def main():
    otfs = sorted(glob.glob(os.path.join(FONTS, "Goetheanum-Schrift-v2.7-*.otf")))
    for p in otfs:
        ft = TTFont(p)
        if "CFF " not in ft:      # nur statische CFF-Schnitte
            continue
        ok = union_glyph(ft, GLYPH)
        if ok:
            ft.save(p); webfonts(p)
            print("  vereinigt:", os.path.basename(p))
        else:
            print("  (keine schlummernde Null):", os.path.basename(p))
    print("Schlummernde Null gesäubert.")

if __name__ == "__main__":
    main()
