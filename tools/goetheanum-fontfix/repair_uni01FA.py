#!/usr/bin/env python3
# Repariert Ǻ (U+01FA, A mit Ring und Akut). In Leise/Ruhig/Klar/Variabel waren
# die Akzent-Konturen verrissen (Punze bis y −450, Ring bis y +1722) – das war
# auch die Glyphe, die usWinAscent aufblähte. Å (U+00C5) und der Akut (U+00B4)
# sind in jedem Schnitt gesund; Ǻ wird gewichtsrichtig neu daraus zusammengesetzt:
# Å + Akut, knapp über den Ring gesetzt. Statisch je Schnitt, in der Variable als
# geblendete CFF2-Charstring über die sechs Master-Lagen (wie das Versaleszett).
# Reproduzierbar, idempotent; danach Webfonts/Office/ZIPs neu.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.varLib.models import VariationModel
from fontTools.varLib.cff import CFF2CharStringMergePen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.7.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
UNI = 0x01FA; GAP = 28
LOCS = [{}, {"wght": -0.08}, {"wght": -0.42}, {"wght": -1.0}, {"wght": 0.561}, {"wght": 1.0}]
MW = [440, 420, 335, 190, 600, 725]

def placement(gs, gnA, gnAcute):
    """dx/dy: Akut waagerecht über die Å-Mitte, senkrecht knapp über den Ring."""
    def bb(gn):
        p = BoundsPen(gs); gs[gn].draw(p); return p.bounds
    ax0, ay0, ax1, ay1 = bb(gnA); cx0, cy0, cx1, cy1 = bb(gnAcute)
    return ((ax0 + ax1) / 2) - ((cx0 + cx1) / 2), ay1 + GAP - cy0

def webfonts(path):
    b = os.path.splitext(os.path.basename(path))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(path); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))

def repair_static(path):
    ft = TTFont(path); cmap = ft.getBestCmap()
    if UNI not in cmap: return False
    gs = ft.getGlyphSet(); gn = cmap[UNI]; gnA = cmap[0x00C5]; gnAc = cmap[0x00B4]
    dx, dy = placement(gs, gnA, gnAc)
    width = ft["hmtx"][gn][0]
    pen = T2CharStringPen(width, None)
    gs[gnA].draw(pen)
    gs[gnAc].draw(TransformPen(pen, (1, 0, 0, 1, dx, dy)))
    cs = pen.getCharString()
    td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
    td.CharStrings[gn].bytecode = None
    td.CharStrings[gn].program = cs.program
    ft.save(path); webfonts(path); return True

def compose_recording_at(w):
    f = TTFont(VAR); instantiateVariableFont(f, {"wght": w}, inplace=True)
    gs = f.getGlyphSet(); cmap = f.getBestCmap()
    gnA = cmap[0x00C5]; gnAc = cmap[0x00B4]
    dx, dy = placement(gs, gnA, gnAc)
    rec = RecordingPen()
    gs[gnA].draw(rec)
    gs[gnAc].draw(TransformPen(rec, (1, 0, 0, 1, dx, dy)))
    return rec

def replay(rec, pen):
    for op, pts in rec.value:
        getattr(pen, op)(*pts) if pts else getattr(pen, op)()

def repair_variable():
    ft = TTFont(VAR); cmap = ft.getBestCmap(); gn = cmap[UNI]
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    recs = [compose_recording_at(w) for w in MW]
    model = VariationModel(LOCS, axisOrder=["wght"])
    pen = CFF2CharStringMergePen([], gn, 6, 0)
    replay(recs[0], pen)
    for i in range(1, 6):
        pen.restart(i); replay(recs[i], pen)
    cs = pen.getCharString(private=td.FDArray[0].Private, globalSubrs=cff.GlobalSubrs,
                           var_model=model, optimize=True)
    gid = td.CharStrings.charStrings[gn]
    td.CharStrings.charStringsIndex[gid] = cs
    ft.save(VAR); webfonts(VAR)

def main():
    for cut in ("Leise", "Ruhig", "Klar", "Deutlich", "Laut"):
        p = os.path.join(FONTS, "Goetheanum-Schrift-v2.7-%s.otf" % cut)
        print("  Ǻ neu:", cut if repair_static(p) else cut + " (fehlt)")
    repair_variable(); print("  Ǻ neu: Variabel (CFF2-Blend)")
    print("Ǻ (U+01FA) repariert – Å + Akut, gewichtsrichtig.")

if __name__ == "__main__":
    main()
