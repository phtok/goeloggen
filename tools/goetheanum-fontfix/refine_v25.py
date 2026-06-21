#!/usr/bin/env python3
# Consolidated v2.5 spacing refinements, applied freshly from the clean v2.5
# base (git 1574a03) so in-place patches never stack:
#   1) figureDash bar -> 0.664 of digit width (sidebearing ~94): a heavy bar
#      needs more air than two digits; solids land at ~140 ink-gap.
#   2) figureDash <-> "1" kerning: the tabular "1" (lsb 110 / rsb 169) blows up
#      the dash gap on both sides; pull it back to the solid-digit gap.
#   3) pnum proportional figures: ship at a flat 40/40 (gap 80, cramped). Widen
#      +24 per side; the light "1" only +12 so it doesn't float.
# Then regenerate the woff/woff2 webfonts. Variable font is out of scope here.
import os, sys, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.otlLib import builder as ob
from fontfix import grec, _charstring
import uharfbuzz as hb
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
BASE = "1574a03"
FIGDASH_RATIO = 0.664
KERN = {("one","figuredash"): -145, ("figuredash","one"): -83}
PNUM_DX, PNUM_ONE_DX = 24, 12

def rect(x0,y0,x1,y1):
    return [("moveTo",((x0,y0),)),("lineTo",((x1,y0),)),("lineTo",((x1,y1),)),("lineTo",((x0,y1),)),("closePath",())]

def respace(ft, gname, dx):
    gs = ft.getGlyphSet(); rp = RecordingPen(); gs[gname].draw(rp)
    sh = [(op, tuple((x+dx, y) for (x, y) in pts)) for op, pts in rp.value]
    adv = ft["hmtx"][gname][0] + 2*dx
    cs = _charstring(ft, sh, adv)
    td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[gname]] = cs
    ft["hmtx"][gname] = (adv, ft["hmtx"][gname][1] + dx)

def set_glyph(ft, gname, recv, adv, lsb):
    cs = _charstring(ft, recv, adv)
    td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[gname]] = cs
    ft["hmtx"][gname] = (int(round(adv)), int(round(lsb)))

def refine(path):
    name = os.path.basename(path)
    raw = subprocess.run(["git","show","%s:assets/fonts/goetheanum/Fonts/%s"%(BASE,name)],
                         cwd=REPO, capture_output=True, check=True).stdout
    tmp = "/tmp/_clean_"+name; open(tmp,"wb").write(raw)
    ft = TTFont(tmp); cmap = ft.getBestCmap()
    fn = hb.Font(hb.Face(hb.Blob.from_file_path(tmp)))
    # 1) figure dash
    rd,_ = grec(ft, 0x2013); d0 = min(y for c,p in rd for x,y in p); d1 = max(y for c,p in rd for x,y in p)
    _,digitW = grec(ft, 0x30); barw = digitW*FIGDASH_RATIO; x0 = (digitW-barw)/2
    set_glyph(ft, cmap[0x2012], rect(x0,d0,x0+barw,d1), digitW, x0)
    # 2) figuredash <-> one kern
    nm = {"one": cmap[0x31], "figuredash": cmap[0x2012]}
    gpos = ft["GPOS"].table
    pairs = {(nm[a],nm[b]):(ob.buildValue({"XAdvance":v}),None) for (a,b),v in KERN.items()}
    lk = ob.buildLookup([ob.buildPairPosGlyphsSubtable(pairs, ft.getReverseGlyphMap())], flags=0)
    gpos.LookupList.Lookup.append(lk); gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(len(gpos.LookupList.Lookup)-1)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    # 3) pnum respace (+24, "1" +12)
    for d in "0123456789":
        b = hb.Buffer(); b.add_str(d); b.guess_segment_properties(); hb.shape(fn, b, {"pnum": True})
        respace(ft, ft.getGlyphName(b.glyph_infos[0].codepoint), PNUM_ONE_DX if d=="1" else PNUM_DX)
    ft.save(path)
    base = os.path.splitext(name)[0]
    for fl, d in (("woff","Webfonts/woff"), ("woff2","Webfonts/woff2")):
        f = TTFont(path); f.flavor = fl; f.save(os.path.join(FONTS, d, "%s.%s"%(base, fl)))
    print("  refined:", name)

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(FONTS, "Fonts", "*v2.5-*.otf"))):
        refine(p)
    print("done")
