#!/usr/bin/env python3
# Refine the slashed zero (zero feature): the diagonal now dies inside the black
# ring instead of floating in the white counter — no negative-space wedges, no
# overhang. New geometry lives in build_specials.py; here we apply it to the
# three static cuts (rebuild cid00626) and the variable (re-interpolate the
# blended cid00626 from the updated cuts). Idempotent: always rebuilds from the
# proportional 0 + current slash params.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_specials as S
from fontTools.ttLib import TTFont
from fontTools.varLib.models import VariationModel
from fontTools.varLib.cff import CFF2CharStringMergePen
from fontTools.pens.recordingPen import RecordingPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.5.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
ZCID = "cid00626"
CUTW = {265: "Leise", 440: "Klar", 680: "Laut"}

def replace_cff(td, name, cs):
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[name]] = cs

def main():
    # 1) static cuts: rebuild cid00626 with the new slash
    for nm in CUTW.values():
        p = os.path.join(FONTS, "Goetheanum-Schrift-v2.5-%s.otf" % nm)
        ft = TTFont(p); sp = S.build_specials(ft)
        _, recv, adv, lsb = sp["zeroslash"]
        cs = S._charstring(ft, recv, adv)
        cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
        replace_cff(td, ZCID, cs)
        ft["hmtx"].metrics[ZCID] = (int(round(adv)), int(round(lsb)))
        ft.save(p)
    print("static cuts: slashed zero rebuilt")
    # 2) variable: re-interpolate blended cid00626 from the updated cuts
    recs = {}
    for w, nm in CUTW.items():
        cf = TTFont(os.path.join(FONTS, "Goetheanum-Schrift-v2.5-%s.otf" % nm))
        rp = RecordingPen(); cf.getGlyphSet()[ZCID].draw(rp); recs[w] = rp.value
    locs = [{}, {"wght": -0.08}, {"wght": -0.42}, {"wght": -1.0}, {"wght": 0.561}, {"wght": 1.0}]
    model = VariationModel(locs, axisOrder=["wght"])
    mw = [440] + [440 + n * (250 if n <= 0 else 285) for n in (-0.08, -0.42, -1.0, 0.561, 1.0)]
    def lerp(a, b, t): return a + (b - a) * t
    def ic(vals, w):
        return lerp(vals[265], vals[440], (w - 265) / 175.0) if w <= 440 else lerp(vals[440], vals[680], (w - 440) / 240.0)
    def interp(w):
        out = []
        for items in zip(*[recs[t] for t in (265, 440, 680)]):
            op = items[0][0]; pp = [it[1] for it in items]
            if not pp[0]: out.append((op, ())); continue
            npts = tuple((ic({t: pp[k][j][0] for k, t in enumerate((265, 440, 680))}, w),
                          ic({t: pp[k][j][1] for k, t in enumerate((265, 440, 680))}, w)) for j in range(len(pp[0])))
            out.append((op, npts))
        return out
    def replay(r, pen):
        for op, pts in r:
            getattr(pen, op)(*pts) if pts else getattr(pen, op)()
    ft = TTFont(VAR); cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    pen = CFF2CharStringMergePen([], ZCID, 6, 0)
    replay(interp(mw[0]), pen)
    for i in range(1, 6):
        pen.restart(i); replay(interp(mw[i]), pen)
    cs = pen.getCharString(private=td.FDArray[0].Private, globalSubrs=cff.GlobalSubrs, var_model=model, optimize=True)
    replace_cff(td, ZCID, cs)
    ft.save(VAR)
    print("variable: slashed zero re-interpolated")
    # 3) webfonts
    for src in [os.path.join(FONTS, "Goetheanum-Schrift-v2.5-%s.otf" % n) for n in CUTW.values()] + [VAR]:
        b = os.path.splitext(os.path.basename(src))[0]
        for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
            f = TTFont(src); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))
    print("webfonts done")

if __name__ == "__main__":
    main()
