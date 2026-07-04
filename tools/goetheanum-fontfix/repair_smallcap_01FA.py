#!/usr/bin/env python3
# Repariert die KAPITÄLCHEN-Variante von Ǻ (small-cap, erreichbar über smcp/c2sc
# von U+01FA/U+01FB). In Leise war sie verrissen (Konturen bis y 1275/−333, der
# letzte Metrik-Ausreisser); in Klar sass der Akut zu hoch. Wie beim grossen Ǻ
# wird sie sauber neu zusammengesetzt: das gesunde Kapitälchen-Å (smcp von U+00C5)
# plus der Akut, knapp über den Ring. Die Zielglyphe wird je Schnitt dynamisch
# über GSUB gefunden (die CID ist nicht schnittübergreifend gleich).
# Reproduzierbar, idempotent; danach Webfonts/Office/ZIPs neu.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
GAP = 28

def sub_target(ft, cp, feats):
    cmap = ft.getBestCmap(); src = cmap.get(cp)
    if not src or "GSUB" not in ft: return None
    gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag in feats:
            for li in fr.Feature.LookupListIndex:
                for st in gsub.LookupList.Lookup[li].SubTable:
                    if hasattr(st, "mapping") and src in st.mapping:
                        return st.mapping[src]
    return None

def bb(gs, gn):
    p = BoundsPen(gs); gs[gn].draw(p); return p.bounds

def webfonts(path):
    b = os.path.splitext(os.path.basename(path))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(path); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))

def repair(path):
    ft = TTFont(path); cmap = ft.getBestCmap(); gs = ft.getGlyphSet()
    goal = sub_target(ft, 0x01FA, ("c2sc",)) or sub_target(ft, 0x01FB, ("smcp",))
    scA = sub_target(ft, 0x00C5, ("smcp", "c2sc"))
    if not goal or not scA or 0x00B4 not in cmap:
        return None
    acute = cmap[0x00B4]
    ax0, ay0, ax1, ay1 = bb(gs, scA); cx0, cy0, cx1, cy1 = bb(gs, acute)
    dx = ((ax0 + ax1) / 2) - ((cx0 + cx1) / 2); dy = ay1 + GAP - cy0
    width = ft["hmtx"][goal][0]
    pen = T2CharStringPen(width, None)
    gs[scA].draw(pen)
    gs[acute].draw(TransformPen(pen, (1, 0, 0, 1, dx, dy)))
    cs = pen.getCharString()
    td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
    td.CharStrings[goal].bytecode = None
    td.CharStrings[goal].program = cs.program
    ft.save(path); webfonts(path)
    return goal

def main():
    for p in sorted(glob.glob(os.path.join(FONTS, "Goetheanum-Schrift-v2.7-*.otf"))):
        cut = os.path.basename(p).split("-")[-1].replace(".otf", "")
        g = repair(p)
        print("  small-cap Ǻ neu:", cut, "(%s)" % g if g else "— nicht vorhanden")
    print("Kapitälchen-Ǻ repariert.")

if __name__ == "__main__":
    main()
