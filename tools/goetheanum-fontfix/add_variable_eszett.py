#!/usr/bin/env python3
# Bringt das Versaleszett ẞ (U+1E9E) als ECHT variable Glyphe in den Variable
# Font — geblendet über die sechs Master-Lagen des Fonts (wght 440/420/335/190/
# 600/725). Quelle sind dieselben zwei punktkompatiblen Master wie für die
# statischen Schnitte (eszett-masters.json). An jeder Master-Lage wird so
# interpoliert, dass Stamm und Versalhöhe der dort gemessenen I/H entsprechen
# und die Seitenränder dem ‹B› der Lage folgen; die so erzeugten, untereinander
# punktkompatiblen Umrisse werden zu einer geblendeten CFF2-Charstring vereint.
# Läuft idempotent nach add_variable_ligatures.py (überspringt, wenn U+1E9E da).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.varLib.models import VariationModel
from fontTools.varLib.cff import CFF2CharStringMergePen
from fontTools.pens.boundsPen import BoundsPen
from build_eszett_v25 import Esz

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.6.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
MASTERS = os.path.join(HERE, "eszett-masters.json")
# Die Master-Lagen des Variable Fonts (Regionen-Peaks) und ihre wght-Werte —
# identisch zu add_variable_ligatures.py.
LOCS = [{}, {"wght": -0.08}, {"wght": -0.42}, {"wght": -1.0}, {"wght": 0.561}, {"wght": 1.0}]
MW = [440, 420, 335, 190, 600, 725]

def cut_metrics_at(w):
    f = TTFont(VAR); instantiateVariableFont(f, {"wght": w}, inplace=True)
    gs = f.getGlyphSet(); cmap = f.getBestCmap()
    def bb(ch):
        p = BoundsPen(gs); gs[cmap[ord(ch)]].draw(p); return p.bounds
    I = bb("I"); H = bb("H"); B = bb("B")
    Badv = f["hmtx"][cmap[ord("B")]][0]
    return I[2] - I[0], H[3] - H[1], B[0], Badv - B[2]

def replay(rec, pen):
    for op, pts in rec:
        getattr(pen, op)(*pts) if pts else getattr(pen, op)()

def main():
    ft = TTFont(VAR); cmap = ft.getBestCmap()
    if 0x1E9E in cmap:
        print("ẞ schon im Variable Font — übersprungen"); return
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    esz = Esz(MASTERS)
    # punktkompatible Umrisse + Vorschübe pro Master-Lage
    recs = []; advs = []
    for w in MW:
        stem, cap, blsb, brsb = cut_metrics_at(w)
        sg, adv, lsb = esz.fit(stem, cap, blsb, brsb)
        recs.append(esz.recording(sg)); advs.append(adv)
    model = VariationModel(LOCS, axisOrder=["wght"])
    pen = CFF2CharStringMergePen([], "eszett", 6, 0)
    replay(recs[0], pen)
    for i in range(1, 6):
        pen.restart(i); replay(recs[i], pen)
    cs = pen.getCharString(private=td.FDArray[0].Private, globalSubrs=cff.GlobalSubrs,
                           var_model=model, optimize=True)
    name = "cid%05d" % (max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1)
    td.CharStrings.charStringsIndex.append(cs)
    td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
    td.charset.append(name)
    if hasattr(td, "FDSelect"): td.FDSelect.append(0)
    _, _, blsb0, _ = cut_metrics_at(440)
    ft["hmtx"].metrics[name] = (int(round(advs[0])), int(round(blsb0)))   # Default-Lage 440
    ft.setGlyphOrder(list(td.charset))
    for t in ft["cmap"].tables:
        if t.isUnicode(): t.cmap[0x1E9E] = name
    ft.save(VAR); print("variables ẞ eingebaut als", name, "adv(440)=", int(round(advs[0])))
    b = os.path.splitext(os.path.basename(VAR))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(VAR); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))
    print("webfonts done")

if __name__ == "__main__":
    main()
