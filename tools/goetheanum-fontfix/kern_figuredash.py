#!/usr/bin/env python3
# Kern the figure dash against the tabular "1" so number ranges like 1914‒1918
# and 0761‒44 read evenly. The default figures are TABULAR (adv 560); the "1"
# carries lsb 110 / rsb 169 of padding, which blows up the gap on both sides of
# the dash whenever a 1 is adjacent. We do NOT touch the digit (that would
# desync tabular columns) — we add two GPOS kern pairs instead, matching the
# 1's dash-gaps to those of the solid digits. Then regenerate webfonts.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.otlLib import builder as ob
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
PAIRS = {("one","figuredash"): -145, ("figuredash","one"): -83}   # XAdvance on 1st glyph

def kern(path):
    ft = TTFont(path); cmap = ft.getBestCmap()
    nm = {"one": cmap[0x31], "figuredash": cmap[0x2012]}
    gpos = ft["GPOS"].table
    pairs = {(nm[a], nm[b]): (ob.buildValue({"XAdvance": v}), None) for (a,b),v in PAIRS.items()}
    sub = ob.buildPairPosGlyphsSubtable(pairs, ft.getReverseGlyphMap())
    lk = ob.buildLookup([sub], flags=0)
    gpos.LookupList.Lookup.append(lk); idx = len(gpos.LookupList.Lookup) - 1
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(idx)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    ft.save(path)
    base = os.path.splitext(os.path.basename(path))[0]
    for fl, d in (("woff","Webfonts/woff"), ("woff2","Webfonts/woff2")):
        f = TTFont(path); f.flavor = fl; f.save(os.path.join(FONTS, d, "%s.%s"%(base, fl)))
    print("  kerned + webfonts:", os.path.basename(path))

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(FONTS, "Fonts", "*v2.5-*.otf"))):
        kern(p)
    print("done")
