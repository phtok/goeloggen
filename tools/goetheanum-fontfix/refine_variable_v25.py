#!/usr/bin/env python3
# Variable font: bring the figures to parity with the static cuts —
# proportional figures as DEFAULT, tabular via a newly built `tnum` feature.
# The variable shipped with only one (tabular) set and no pnum/tnum.
#
# Tabular and proportional share outlines (proportional = tabular shifted +
# re-advanced), so we DERIVE proportional from the existing digits:
#   - copy each tabular digit -> a new glyph (kept tabular, for tnum)
#   - shift the default digit by tx and set its proportional advance, matching
#     the static cuts' final proportional metrics at the Klar weight. Shifting a
#     CFF2 charstring by tx (program[0]+=tx, the leading move's dx) translates it
#     uniformly across the whole weight axis (verified).
#   - add a `tnum` GSUB feature mapping the (now proportional) defaults back to
#     the tabular copies.
# onum/frac keep working (default glyph NAMES are unchanged).
import os, sys, copy, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.otlLib import builder as ob
from fontTools.ttLib.tables import otTables as ot
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
BASE = "1574a03"   # clean v2.5 variable (tabular only) — read fresh, so re-runs stay idempotent
VARREL = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.5.otf"
VAR = os.path.join(REPO, VARREL)
KLAR = os.path.join(REPO, "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.5-Klar.otf")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")

def inkleft(gs, name):
    bp = BoundsPen(gs); gs[name].draw(bp); return round(bp.bounds[0]) if bp.bounds else 0

def add_feature(gsub, tag, lookup_indices):
    feat = ot.Feature(); feat.FeatureParams = None
    feat.LookupListIndex = lookup_indices; feat.LookupCount = len(lookup_indices)
    fr = ot.FeatureRecord(); fr.FeatureTag = tag; fr.Feature = feat
    fl = gsub.FeatureList; fl.FeatureRecord.append(fr); fl.FeatureCount = len(fl.FeatureRecord)
    idx = len(fl.FeatureRecord)-1
    for sr in gsub.ScriptList.ScriptRecord:
        s = sr.Script
        langs = ([s.DefaultLangSys] if s.DefaultLangSys else []) + [r.LangSys for r in s.LangSysRecord]
        for ls in langs:
            ls.FeatureIndex.append(idx); ls.FeatureCount = len(ls.FeatureIndex)
    return idx

def main():
    # static proportional targets (final, at Klar weight)
    st = TTFont(KLAR); sc = st.getBestCmap(); sgs = st.getGlyphSet()
    target = {i: (inkleft(sgs, sc[0x30+i]), st["hmtx"][sc[0x30+i]][0]) for i in range(10)}
    # clean variable base (read fresh from git so re-runs are idempotent)
    raw = subprocess.run(["git", "show", "%s:%s" % (BASE, VARREL)], cwd=REPO, capture_output=True, check=True).stdout
    open("/tmp/_clean_var.otf", "wb").write(raw)
    # variable tabular ink-left @440 (before edits)
    vi = TTFont("/tmp/_clean_var.otf"); instantiateVariableFont(vi, {"wght": 440}, inplace=True); vgs = vi.getGlyphSet()
    ft = TTFont("/tmp/_clean_var.otf"); cmap = ft.getBestCmap(); D = [cmap[0x30+i] for i in range(10)]
    tabL = {d: inkleft(vgs, d) for d in D}
    td = ft["CFF2"].cff[ft["CFF2"].cff.fontNames[0]]
    nextcid = max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1
    Tab = []
    for i, d in enumerate(D):
        # 1) tabular copy -> new glyph
        src = td.CharStrings[d]; src.decompile()
        new = type(src)(program=list(src.program), private=src.private, globalSubrs=src.globalSubrs)
        nm = "cid%05d" % (nextcid + i)
        td.CharStrings.charStringsIndex.append(new)
        td.CharStrings.charStrings[nm] = len(td.CharStrings.charStringsIndex)-1
        td.charset.append(nm)
        if hasattr(td, "FDSelect"): td.FDSelect.append(td.FDSelect[ft.getGlyphID(d)])
        ft["hmtx"].metrics[nm] = (560, ft["hmtx"][d][1])
        Tab.append(nm)
        # 2) shift default -> proportional
        lsb_t, adv_t = target[i]; tx = lsb_t - tabL[d]
        src.program[0] = src.program[0] + tx
        ft["hmtx"].metrics[d] = (adv_t, lsb_t)
    ft.setGlyphOrder(list(td.charset))
    # 3) tnum feature: default(proportional) -> tabular copies
    gsub = ft["GSUB"].table
    lk = ob.buildLookup([ob.buildSingleSubstSubtable({D[i]: Tab[i] for i in range(10)})], flags=0)
    gsub.LookupList.Lookup.append(lk); gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
    add_feature(gsub, "tnum", [len(gsub.LookupList.Lookup)-1])
    ft.save(VAR); print("variable saved")
    base = os.path.splitext(os.path.basename(VAR))[0]
    for fl, sub in (("woff","woff"), ("woff2","woff2")):
        f = TTFont(VAR); f.flavor = fl; f.save(os.path.join(WF, sub, "%s.%s" % (base, fl)))
    print("webfonts done")

if __name__ == "__main__":
    main()
