#!/usr/bin/env python3
# Patch the figureDash (U+2012) glyph in the shipped v2.5 static cuts:
# widen the bar 0.62 -> 0.78 of the digit width so its sidebearings (~62) match
# the en-dash instead of being ~2x a digit. Advance stays = digit width (tabular).
# Then regenerate the woff/woff2 webfonts for the patched cuts.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontfix import grec, _charstring
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")

def rect(x0,y0,x1,y1):
    return [("moveTo",((x0,y0),)),("lineTo",((x1,y0),)),("lineTo",((x1,y1),)),("lineTo",((x0,y1),)),("closePath",())]

def patch(path):
    ft = TTFont(path); cmap = ft.getBestCmap()
    rd,_ = grec(ft, 0x2013); d0 = min(y for c,p in rd for x,y in p); d1 = max(y for c,p in rd for x,y in p)
    _,digitW = grec(ft, 0x30)
    barw = digitW*0.78; x0 = (digitW-barw)/2
    recv = rect(x0, d0, x0+barw, d1)
    cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
    name = cmap[0x2012]
    cs = _charstring(ft, recv, digitW)
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[name]] = cs
    ft["hmtx"][name] = (int(round(digitW)), int(round(x0)))
    ft.save(path)
    print("  patched figuredash:", os.path.basename(path), "sb=%.0f"%x0)
    # webfonts
    base = os.path.splitext(os.path.basename(path))[0]
    for fl, d in (("woff","Webfonts/woff"), ("woff2","Webfonts/woff2")):
        f = TTFont(path); f.flavor = fl; f.save(os.path.join(FONTS, d, "%s.%s"%(base, fl)))

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(FONTS, "Fonts", "*v2.5-*.otf"))):
        patch(p)
    print("done")
