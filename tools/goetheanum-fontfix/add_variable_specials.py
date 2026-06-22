#!/usr/bin/env python3
# Bring the v2.5 specials into the variable font, weight-variable:
#   figureDash U+2012  — derived from the en-dash (its bar LENGTH is a fixed
#     charstring value, the THICKNESS is blended -> varies with weight for free).
#     We shorten the bar to 408 and centre it in a 560 (figure-width) advance.
#   prime U+2032, doublePrime U+2033 — the raised comma (quoteright), re-spaced;
#     the double is the comma drawn twice with a fixed gap.
# Runs idempotently from the clean v2.5 base (after the figure refinements).
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontfix import grec
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VARREL = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.5.otf"
VAR = os.path.join(REPO, VARREL)
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
FIGW = 560; BARLEN = 408

def mnx(r): return min(x for c,p in r for x,y in p)
def mxx(r): return max(x for c,p in r for x,y in p)

def add_glyph(ft, uni, cs, adv, lsb):
    td = ft["CFF2"].cff[ft["CFF2"].cff.fontNames[0]]
    name = "cid%05d" % (max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1)
    td.CharStrings.charStringsIndex.append(cs); td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex)-1
    td.charset.append(name)
    if hasattr(td, "FDSelect"): td.FDSelect.append(0)
    ft["hmtx"].metrics[name] = (int(round(adv)), int(round(lsb)))
    ft.setGlyphOrder(list(td.charset))
    for t in ft["cmap"].tables:
        if t.isUnicode(): t.cmap[uni] = name
    return name

def main():
    # Runs after refine_variable_v25.py, on the working file; the per-glyph
    # guards (skip if the codepoint already exists) keep it idempotent.
    ft = TTFont(VAR); cmap = ft.getBestCmap()
    td = ft["CFF2"].cff[ft["CFF2"].cff.fontNames[0]]
    def clone(gname):
        cs = td.CharStrings[gname]; cs.decompile()
        return type(cs)(program=list(cs.program), private=cs.private, globalSubrs=cs.globalSubrs)
    # ---- figure dash from en-dash ----
    if 0x2012 not in cmap:
        cs = clone(cmap[0x2013]); prog = cs.program
        x0 = (FIGW-BARLEN)/2                       # 76: centre the bar
        prog[0] = prog[0] + (x0 - mnx(grec(ft, 0x2013)[0]))   # shift start to x0
        prog[prog.index(500)] = BARLEN             # bar length 500 -> 408
        add_glyph(ft, 0x2012, cs, FIGW, x0)
    # ---- prime / double prime from quoteright ----
    if 0x2032 not in cmap:
        rq, aq = grec(ft, 0x2019); qx0, qx1 = mnx(rq), mxx(rq); qw = qx1-qx0
        rI, _ = grec(ft, 0x49); stem = mxx(rI)-mnx(rI); sb = stem*0.42; gap = stem*0.55
        padv = qw + 2*sb
        cs = clone(cmap[0x2019]); cs.program[0] = cs.program[0] + (sb - qx0)
        add_glyph(ft, 0x2032, cs, padv, sb)
        # double prime: draw the comma twice, fixed gap (qw+gap) between them
        start1 = rq[0][1][0]; P1 = [p for c, pts in rq for p in pts][-1]
        cdx = (start1[0] + qw + gap) - P1[0]; cdy = start1[1] - P1[1]
        cs2 = clone(cmap[0x2019]); prog = cs2.program; prog[0] = prog[0] + (sb - qx0)
        ri = prog.index("rmoveto"); draw = prog[ri+1:]
        cs2.program = prog + [cdx, cdy, "rmoveto"] + draw
        add_glyph(ft, 0x2033, cs2, qw + gap + padv, sb)
    ft.save(VAR); print("variable specials added")
    base = os.path.splitext(os.path.basename(VAR))[0]
    for fl, sub in (("woff","woff"), ("woff2","woff2")):
        f = TTFont(VAR); f.flavor = fl; f.save(os.path.join(WF, sub, "%s.%s"%(base, fl)))
    print("webfonts done")

if __name__ == "__main__":
    main()
