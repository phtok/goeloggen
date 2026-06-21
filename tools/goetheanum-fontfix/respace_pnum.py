#!/usr/bin/env python3
# Optimize the proportional LINING figures (pnum): they ship with a flat 40/40
# sidebearing (ink gap 80) which reads cramped. Widen each side by +16
# (ink gap ~112), evenly. The oldstyle figures (onum) are individually spaced
# and left untouched. Then regenerate webfonts.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontfix import _charstring
import uharfbuzz as hb
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
DX = 16

def pnum_names(path, ft):
    fn = hb.Font(hb.Face(hb.Blob.from_file_path(path))); names = set()
    for d in "0123456789":
        b = hb.Buffer(); b.add_str(d); b.guess_segment_properties(); hb.shape(fn, b, {"pnum": True})
        names.add(ft.getGlyphName(b.glyph_infos[0].codepoint))
    return names

def respace(ft, gname, dx):
    gs = ft.getGlyphSet(); rp = RecordingPen(); gs[gname].draw(rp)
    shifted = [(op, tuple((x+dx, y) for (x, y) in pts)) for op, pts in rp.value]
    adv = ft["hmtx"][gname][0] + 2*dx
    cs = _charstring(ft, shifted, adv)
    cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
    td.CharStrings.charStringsIndex[td.CharStrings.charStrings[gname]] = cs
    lsb = ft["hmtx"][gname][1]; ft["hmtx"][gname] = (adv, lsb+dx)

def opt(path):
    ft = TTFont(path)
    for gn in pnum_names(path, ft): respace(ft, gn, DX)
    ft.save(path)
    base = os.path.splitext(os.path.basename(path))[0]
    for fl, d in (("woff","Webfonts/woff"), ("woff2","Webfonts/woff2")):
        f = TTFont(path); f.flavor = fl; f.save(os.path.join(FONTS, d, "%s.%s"%(base, fl)))
    print("  pnum +%d:" % DX, os.path.basename(path))

if __name__ == "__main__":
    for p in sorted(glob.glob(os.path.join(FONTS, "Fonts", "*v2.5-*.otf"))):
        opt(p)
    print("done")
