#!/usr/bin/env python3
# Consolidated v2.5 figure refinements, applied freshly from the clean v2.5 base
# (git 1574a03) so in-place patches never stack. Two stages:
#
# A) spacing of the proportional figures + figure dash
#    - pnum proportional figures ship at a flat 40/40 (gap 80, cramped): widen
#      +24 per side; the light "1" only +12 so it does not float.
#    - figureDash bar -> 0.729 of the (tabular) digit width: sits airy next to
#      the proportional digits (~140 to solids, ~128 to the light 1).
#
# B) make proportional the DEFAULT (tables opt in via tnum). Done by swapping
#    glyph CONTENTS, not the cmap: the default digit glyphs receive the
#    proportional outline+advance, fresh tabular copies are created and tnum is
#    pointed at them. Because the default glyph NAMES are untouched, every other
#    figure feature (onum, frac, zero, sups/subs) keeps working unchanged. The
#    slashed zero (zero feature) is rebuilt at the proportional width. The old
#    figureDash<->1 kern is intentionally dropped (it was for the tabular 1).
import os, sys, glob, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontfix import grec, _charstring
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
BASE = "1574a03"
PNUM_DX, PNUM_ONE_DX = 24, 12
FIGDASH_RATIO = 0.729
PROPORTIONAL_DEFAULT = True

def rect(x0,y0,x1,y1):
    return [("moveTo",((x0,y0),)),("lineTo",((x1,y0),)),("lineTo",((x1,y1),)),("lineTo",((x0,y1),)),("closePath",())]
def mnx(r): return min(x for c,p in r for x,y in p)
def mxx(r): return max(x for c,p in r for x,y in p)
def mny(r): return min(y for c,p in r for x,y in p)
def mxy(r): return max(y for c,p in r for x,y in p)

def grecn(ft, gname):
    gs = ft.getGlyphSet(); rp = RecordingPen(); gs[gname].draw(rp)
    return rp.value, ft["hmtx"][gname][0]
def set_glyph(ft, gname, recv, adv, lsb):
    cs = _charstring(ft, recv, adv)
    td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[gname]] = cs
    ft["hmtx"][gname] = (int(round(adv)), int(round(lsb)))
def respace(ft, gname, dx):
    rec, adv = grecn(ft, gname)
    sh = [(op, tuple((x+dx, y) for (x, y) in pts)) for op, pts in rec]
    set_glyph(ft, gname, sh, adv+2*dx, ft["hmtx"][gname][1]+dx)
def add_glyph(ft, recv, adv):                       # new CID glyph, no cmap entry
    cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
    cs = _charstring(ft, recv, adv)
    name = "cid%05d" % (max(int(n[3:]) for n in td.charset if re.fullmatch(r"cid\d+", n)) + 1)
    td.CharStrings.charStringsIndex.append(cs); td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex)-1
    td.charset.append(name)
    if hasattr(td, "FDSelect"): td.FDSelect.append(0)
    ft["hmtx"].metrics[name] = (int(round(adv)), int(round(mnx(recv))))
    ft.setGlyphOrder(list(td.charset)); return name

def prop_zeroslash(ft, zero_name):
    # proportional 0 outline + diagonal slash ending inside the ring
    z0,za = grecn(ft, zero_name)
    rI,_ = grec(ft, 0x49); stem = mxx(rI)-mnx(rI)
    zx0,zx1,zy0,zy1 = mnx(z0),mxx(z0),mny(z0),mxy(z0); zh=zy1-zy0; cxz=(zx0+zx1)/2
    yA=zy0+zh*0.13; yB=zy1-zh*0.13; bw=stem*0.92; sl=(yB-yA)*0.42; bx=cxz-sl/2-bw/2
    slash=[("moveTo",((bx,yA),)),("lineTo",((bx+bw,yA),)),("lineTo",((bx+bw+sl,yB),)),("lineTo",((bx+sl,yB),)),("closePath",())]
    return list(z0)+slash, za

def refine(path):
    name = os.path.basename(path)
    raw = subprocess.run(["git","show","%s:assets/fonts/goetheanum/Fonts/%s"%(BASE,name)],
                         cwd=REPO, capture_output=True, check=True).stdout
    tmp = "/tmp/_clean_"+name; open(tmp,"wb").write(raw)
    ft = TTFont(tmp); cmap = ft.getBestCmap()
    gsub = ft["GSUB"].table; L = gsub.LookupList.Lookup
    # locate the figure-feature lookups by tag
    feat = {}
    for fr in gsub.FeatureList.FeatureRecord: feat.setdefault(fr.FeatureTag, fr.Feature.LookupListIndex[0])
    D = [cmap[0x30+i] for i in range(10)]
    P = [L[feat["pnum"]].SubTable[0].mapping[d] for d in D]
    # A1) respace pnum
    for i, pg in enumerate(P): respace(ft, pg, PNUM_ONE_DX if i == 1 else PNUM_DX)
    # A2) figure dash (tabular digit width, taken before any flip)
    rd,_ = grec(ft, 0x2013); d0, d1 = mny(rd), mxy(rd)
    digitW = ft["hmtx"][D[0]][0]; barw = digitW*FIGDASH_RATIO; x0 = (digitW-barw)/2
    set_glyph(ft, cmap[0x2012], rect(x0,d0,x0+barw,d1), digitW, x0)
    # B) proportional default via content swap
    if PROPORTIONAL_DEFAULT:
        Tab = [add_glyph(ft, *grecn(ft, d)) for d in D]             # tabular copies
        for i, d in enumerate(D):                                   # default -> proportional
            pv, pa = grecn(ft, P[i]); set_glyph(ft, d, pv, pa, ft["hmtx"][P[i]][1])
        L[feat["tnum"]].SubTable[0].mapping = {D[i]: Tab[i] for i in range(10)}
        zname = L[feat["zero"]].SubTable[0].mapping[D[0]]           # slashed-zero glyph
        zr, za = prop_zeroslash(ft, D[0]); set_glyph(ft, zname, zr, za, mnx(zr))
    ft.save(path)
    base = os.path.splitext(name)[0]
    for fl, d in (("woff","Webfonts/woff"), ("woff2","Webfonts/woff2")):
        f = TTFont(path); f.flavor = fl; f.save(os.path.join(FONTS, d, "%s.%s"%(base, fl)))
    print("  refined:", name)

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(FONTS, "Fonts", "*v2.5-*.otf"))):
        refine(p)
    print("done")
