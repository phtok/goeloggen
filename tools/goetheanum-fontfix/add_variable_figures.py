#!/usr/bin/env python3
# Bringt die proportionalen Ziffern (pnum) und das explizite Versalziffern-
# Toggle (lnum) in den Variable Font — die einzige verbliebene Feature-Lücke
# gegenüber den statischen Schnitten (tnum/onum/zero sind schon da). Methode wie
# bei den variablen f-Ligaturen: die pnum-Ziffern liegen punktkompatibel in den
# drei statischen Schnitten (wght 265/440/680) vor, werden auf die sechs Master-
# Lagen des Variable Fonts interpoliert und zu geblendeten CFF2-Charstrings
# vereint. lnum ist die Identität auf die ohnehin tabellarisch-versalen Default-
# Ziffern. Idempotent: überspringt, wenn pnum schon vorhanden ist.
# Läuft nach add_variable_ligatures.py / add_variable_eszett.py.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.models import VariationModel
from fontTools.varLib.cff import CFF2CharStringMergePen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.otlLib import builder as ob
import fontTools.ttLib.tables.otTables as ot
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.5.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
BASE = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
CUTW = {265: "Leise", 440: "Klar", 680: "Laut"}
LOCS = [{}, {"wght": -0.08}, {"wght": -0.42}, {"wght": -1.0}, {"wght": 0.561}, {"wght": 1.0}]
MW = [440, 420, 335, 190, 600, 725]

def lerp(a, b, t): return a + (b - a) * t

def pnum_map(f):
    g = f["GSUB"].table; idxs = set()
    for fr in g.FeatureList.FeatureRecord:
        if fr.FeatureTag == "pnum": idxs |= set(fr.Feature.LookupListIndex)
    m = {}
    for li in idxs:
        for st in g.LookupList.Lookup[li].SubTable:
            m.update(getattr(st, "mapping", {}))
    return m

def add_feature(g, tag, lidx):
    feat = ot.Feature(); feat.FeatureParams = None
    feat.LookupListIndex = [lidx]; feat.LookupCount = 1
    fr = ot.FeatureRecord(); fr.FeatureTag = tag; fr.Feature = feat
    g.FeatureList.FeatureRecord.append(fr)
    g.FeatureList.FeatureCount = len(g.FeatureList.FeatureRecord)
    fidx = g.FeatureList.FeatureCount - 1
    for sr in g.ScriptList.ScriptRecord:
        s = sr.Script
        for ls in ([s.DefaultLangSys] if s.DefaultLangSys else []) + [r.LangSys for r in s.LangSysRecord]:
            ls.FeatureIndex.append(fidx); ls.FeatureCount = len(ls.FeatureIndex)

def main():
    ft = TTFont(VAR)
    if "pnum" in {fr.FeatureTag for fr in ft["GSUB"].table.FeatureList.FeatureRecord}:
        print("pnum schon vorhanden — übersprungen"); return
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    cmap = ft.getBestCmap()
    cutfonts = {w: TTFont(os.path.join(BASE, "Goetheanum-Schrift-v2.5-%s.otf" % nm)) for w, nm in CUTW.items()}
    pmaps = {w: pnum_map(cf) for w, cf in cutfonts.items()}
    # punktkompatible pnum-Umrisse + Vorschübe je Ziffer aus den drei Schnitten
    digits = list(range(0x30, 0x3A))
    rec = {}; adv = {}
    for d in digits:
        rec[d] = {}; adv[d] = {}
        for w, cf in cutfonts.items():
            cc = cf.getBestCmap(); tgt = pmaps[w].get(cc[d], cc[d])
            rp = RecordingPen(); cf.getGlyphSet()[tgt].draw(rp)
            rec[d][w] = rp.value; adv[d][w] = cf["hmtx"][tgt][0]
    model = VariationModel(LOCS, axisOrder=["wght"])

    def ic(vals, w):
        return lerp(vals[265], vals[440], (w - 265) / 175.0) if w <= 440 else lerp(vals[440], vals[680], (w - 440) / 240.0)
    def interp(recs, w):
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
    nextn = max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1
    pnum = {}
    for k, d in enumerate(digits):
        pen = CFF2CharStringMergePen([], "pnum%d" % d, 6, 0)
        replay(interp(rec[d], MW[0]), pen)
        for i in range(1, 6):
            pen.restart(i); replay(interp(rec[d], MW[i]), pen)
        cs = pen.getCharString(private=td.FDArray[0].Private, globalSubrs=cff.GlobalSubrs, var_model=model, optimize=True)
        nm = "cid%05d" % (nextn + k)
        td.CharStrings.charStringsIndex.append(cs); td.CharStrings.charStrings[nm] = len(td.CharStrings.charStringsIndex) - 1
        td.charset.append(nm)
        if hasattr(td, "FDSelect"): td.FDSelect.append(0)
        ft["hmtx"].metrics[nm] = (int(round(ic(adv[d], 440))), 0)
        pnum[cmap[d]] = nm
    ft.setGlyphOrder(list(td.charset))
    # GSUB: pnum (proportional) + lnum (= tabellarisch-versaler Default, Identität)
    g = ft["GSUB"].table
    g.LookupList.Lookup.append(ob.buildLookup([ob.buildSingleSubstSubtable(pnum)], flags=0))
    g.LookupList.LookupCount = len(g.LookupList.Lookup)
    add_feature(g, "pnum", g.LookupList.LookupCount - 1)
    ident = {cmap[d]: cmap[d] for d in digits}
    g.LookupList.Lookup.append(ob.buildLookup([ob.buildSingleSubstSubtable(ident)], flags=0))
    g.LookupList.LookupCount = len(g.LookupList.Lookup)
    add_feature(g, "lnum", g.LookupList.LookupCount - 1)
    ft.save(VAR); print("variable pnum (%d Ziffern) + lnum eingebaut" % len(pnum))
    b = os.path.splitext(os.path.basename(VAR))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(VAR); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))
    print("webfonts done")

if __name__ == "__main__":
    main()
