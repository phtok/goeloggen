#!/usr/bin/env python3
# Bring the f-ligatures and the slashed zero into the variable font, as REAL
# variable glyphs: Philipp's drawings exist point-compatible in the three static
# cuts (wght 265/440/680), so we interpolate them onto the variable's master
# locations and merge into blended CFF2 charstrings. Then wire up liga / calt
# (word-end ff overswing) / zero — replicating the static cuts' GSUB rules.
# Runs after refine_variable_v25.py + add_variable_specials.py, idempotently.
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
# static glyph (CID) for each new variable glyph
GLYPHS = {  # newname: static-cid (same name in all cuts)
    "lig_ff": "cid00618", "lig_ffend": "cid00619", "lig_fi": "cid00620",
    "lig_fl": "cid00621", "lig_ft": "cid00622", "slashzero": "cid00626"}
# liga: component tuple (variable cids, == static) -> new ligature glyph
LIGA = {("cid00389", "cid00389"): "lig_ff", ("cid00389", "cid00390"): "lig_fi",
        ("cid00389", "cid00393"): "lig_fl", ("cid00389", "cid00398"): "lig_ft"}
# calt lookahead: word-boundary glyphs (space, dashes, punctuation) from static
BOUNDARY = ["cid00001", "cid00143", "cid00212", "cid00231", "cid00232", "cid00234",
            "cid00235", "cid00236", "cid00238", "cid00384", "cid00454"]

def lerp(a, b, t): return a + (b - a) * t

def main():
    ft = TTFont(VAR)
    if "liga" in {fr.FeatureTag for fr in ft["GSUB"].table.FeatureList.FeatureRecord}:
        print("liga schon vorhanden — übersprungen"); return
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    # static master recordings + advances per target glyph
    cutfonts = {w: TTFont(os.path.join(BASE, "Goetheanum-Schrift-v2.5-%s.otf" % nm)) for w, nm in CUTW.items()}
    rec = {}; adv = {}
    for new, cid in GLYPHS.items():
        rec[new] = {}; adv[new] = {}
        for w, cf in cutfonts.items():
            rp = RecordingPen(); cf.getGlyphSet()[cid].draw(rp)
            rec[new][w] = rp.value; adv[new][w] = cf["hmtx"][cid][0]
    # variation model on the variable's master locations (= VarStore region peaks)
    locs = [{}, {"wght": -0.08}, {"wght": -0.42}, {"wght": -1.0}, {"wght": 0.561}, {"wght": 1.0}]
    model = VariationModel(locs, axisOrder=["wght"])
    mw = [440] + [440 + n * (250 if n <= 0 else 285) for n in (-0.08, -0.42, -1.0, 0.561, 1.0)]

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
    newcid = {}
    for k, new in enumerate(GLYPHS):
        pen = CFF2CharStringMergePen([], new, 6, 0)
        replay(interp(rec[new], mw[0]), pen)
        for i in range(1, 6):
            pen.restart(i); replay(interp(rec[new], mw[i]), pen)
        cs = pen.getCharString(private=td.FDArray[0].Private, globalSubrs=cff.GlobalSubrs, var_model=model, optimize=True)
        nm = "cid%05d" % (nextn + k); newcid[new] = nm
        td.CharStrings.charStringsIndex.append(cs); td.CharStrings.charStrings[nm] = len(td.CharStrings.charStringsIndex) - 1
        td.charset.append(nm); td.FDSelect.append(0)
        ft["hmtx"].metrics[nm] = (int(round(ic(adv[new], 440))), 0)
    ft.setGlyphOrder(list(td.charset))
    gmap = ft.getReverseGlyphMap()
    # ---- GSUB: liga / calt / zero ----
    g = ft["GSUB"].table; LK = g.LookupList.Lookup
    def add_lookup(lk): LK.append(lk); g.LookupList.LookupCount = len(LK); return len(LK) - 1
    liga_sub = ob.buildLigatureSubstSubtable({comp: newcid[v] for comp, v in LIGA.items()})
    i_liga = add_lookup(ob.buildLookup([liga_sub], flags=0))
    ffend_sub = ob.buildSingleSubstSubtable({newcid["lig_ff"]: newcid["lig_ffend"]})
    i_ffend = add_lookup(ob.buildLookup([ffend_sub], flags=0))
    chain = ot.ChainContextSubst(); chain.Format = 3
    chain.BacktrackGlyphCount = 0; chain.BacktrackCoverage = []
    chain.InputGlyphCount = 1; chain.InputCoverage = [ob.buildCoverage([newcid["lig_ff"]], gmap)]
    bnd = [b for b in BOUNDARY if b in gmap]
    chain.LookAheadGlyphCount = 1; chain.LookAheadCoverage = [ob.buildCoverage(bnd, gmap)]
    slr = ot.SubstLookupRecord(); slr.SequenceIndex = 0; slr.LookupListIndex = i_ffend
    chain.SubstCount = 1; chain.SubstLookupRecord = [slr]
    lk_calt = ot.Lookup(); lk_calt.LookupType = 6; lk_calt.LookupFlag = 0
    lk_calt.SubTable = [chain]; lk_calt.SubTableCount = 1
    i_calt = add_lookup(lk_calt)
    zero_sub = ob.buildSingleSubstSubtable({"cid00414": newcid["slashzero"]})
    i_zero = add_lookup(ob.buildLookup([zero_sub], flags=0))
    # features
    def add_feature(tag, idxs):
        feat = ot.Feature(); feat.FeatureParams = None; feat.LookupListIndex = idxs; feat.LookupCount = len(idxs)
        fr = ot.FeatureRecord(); fr.FeatureTag = tag; fr.Feature = feat
        fl = g.FeatureList; fl.FeatureRecord.append(fr); fl.FeatureCount = len(fl.FeatureRecord)
        ni = len(fl.FeatureRecord) - 1
        for sr in g.ScriptList.ScriptRecord:
            s = sr.Script
            for ls in ([s.DefaultLangSys] if s.DefaultLangSys else []) + [r.LangSys for r in s.LangSysRecord]:
                ls.FeatureIndex.append(ni); ls.FeatureCount = len(ls.FeatureIndex)
    add_feature("liga", [i_liga]); add_feature("calt", [i_calt]); add_feature("zero", [i_zero])
    ft.save(VAR); print("ligatures + slashed zero injected")
    b = os.path.splitext(os.path.basename(VAR))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(VAR); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))
    print("webfonts done")

if __name__ == "__main__":
    main()
