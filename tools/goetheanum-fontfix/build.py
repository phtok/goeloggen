#!/usr/bin/env python3
"""Reproducible repair build for the Goetheanum Schriften v1.4.43 package.

Inputs  : ./input/*.otf            (original v1.4.43 fonts, as shipped)
Sources : ./sources/Titillium-*Upright.otf  (OFL, interpolation donors)
Output  : ../../assets/fonts/goetheanum/{Fonts,Variable,Webfonts}

What it does (see AUDIT.md for the why):
  * imports the missing  ! " $ §  per weight (weight-matched interpolation)
  * rebuilds the ampersand so it follows the weight (was identical in all cuts)
  * adds NBSP, mirrors the single guillemets ‹ ›
  * removes inconsistent Vietnamese half-pairs (keeps symbols µ ƒ π Ω)
  * fixes metadata: version, CFF FontName, caret/italic leftovers, .notdef,
    Mac name records, doubled full names, vertical metrics + USE_TYPO_METRICS,
    OS/2 weight class (variable), SIL OFL license fields
No design errors are imported: the broken Titillium 'fraction' glyph is never used.

Run:  python3 build.py
"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontfix import (load_uprights, glyph_area, grec, area_of, pick_and_interp,
                     add_cid_glyph, replace_glyph_outline, _charstring)
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

INPUT = os.path.join(HERE, "input")
OUTROOT = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "fonts", "goetheanum"))
STATICS = {"Leise": "Goetheanum-Schrift-v1.4.43-Leise.otf",
           "Klar":  "Goetheanum-Schrift-v1.4.43-Klar.otf",
           "Laut":  "Goetheanum-Schrift-v1.4.43-Laut.otf"}
IMPORTS = [("exclam", 0x21), ("quotedbl", 0x22), ("dollar", 0x24), ("section", 0xA7)]

COPYRIGHT = ("Copyright 2026 Goetheanum Kommunikation. Based on Titillium, Copyright (c) "
             "2008-2010 Accademia di Belle Arti di Urbino, with Reserved Font Name Titillium.")
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")


def gbbox(ft):
    gs = ft.getGlyphSet(); ym, yn = -1e9, 1e9
    for gn in ft.getGlyphOrder():
        bp = BoundsPen(gs)
        try: gs[gn].draw(bp)
        except Exception: continue
        if bp.bounds:
            ym = max(ym, bp.bounds[3]); yn = min(yn, bp.bounds[1])
    return ym, yn


def fix_meta(ft, ps, full, weight_class=None):
    name = ft["name"]
    name.names = [r for r in name.names if r.platformID != 1]   # drop Mac records

    def setn(i, v): name.setName(v, i, 3, 1, 0x409)
    setn(4, full); setn(6, ps); setn(3, f"1.4.43;GOEA;{ps}"); setn(5, "Version 1.443")
    setn(0, COPYRIGHT)
    setn(7, "Titillium is a Reserved Font Name of Accademia di Belle Arti di Urbino.")
    setn(8, "Goetheanum Kommunikation")
    setn(9, "Goetheanum Kommunikation; based on Titillium by Accademia di Belle Arti di "
            "Urbino (Luca Antonucci et al.)")
    setn(11, "https://www.goetheanum.org")
    setn(13, LICENSE); setn(14, "https://openfontlicense.org")
    ft["head"].fontRevision = 1.443; ft["head"].macStyle = 0
    h = ft["hhea"]; h.caretSlopeRise = 1; h.caretSlopeRun = 0; h.caretOffset = 0
    ft["post"].italicAngle = 0.0
    o = ft["OS/2"]
    if o.version < 4: o.version = 4
    o.fsSelection = (o.fsSelection & ~0b100001) | 0b11000000   # REGULAR + USE_TYPO_METRICS
    if weight_class is not None: o.usWeightClass = weight_class
    o.sTypoAscender = 750; o.sTypoDescender = -250; o.sTypoLineGap = 0
    h.ascent = 750; h.descent = -250; h.lineGap = 0
    if "CFF " in ft: ft["CFF "].cff.fontNames = [ps]


def set_win(ft, wa, wd):
    o = ft["OS/2"]; o.usWinAscent = wa; o.usWinDescent = wd


def add_notdef_box(ft):
    o = [("moveTo", ((60, 0),)), ("lineTo", ((440, 0),)), ("lineTo", ((440, 700),)),
         ("lineTo", ((60, 700),)), ("closePath", ())]
    i = [("moveTo", ((120, 60),)), ("lineTo", ((120, 640),)), ("lineTo", ((380, 640),)),
         ("lineTo", ((380, 60),)), ("closePath", ())]
    cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
    td.CharStrings[".notdef"] = _charstring(ft, o + i, 500)
    ft["hmtx"].metrics[".notdef"] = (500, 60)


def remove_case_orphans(ft):
    """Drop Vietnamese (U+1E00-1EFF) glyphs whose case partner is absent, so the
    case mapping is self-consistent. Symbols like µ ƒ π Ω are out of range -> kept."""
    enc = set(ft.getBestCmap()); drop = set()
    for cp in list(enc):
        if not (0x1E00 <= cp <= 0x1EFF):
            continue
        ch = chr(cp); up = ch.upper(); lo = ch.lower()
        if up != ch and len(up) == 1 and ord(up) not in enc: drop.add(cp)
        if lo != ch and len(lo) == 1 and ord(lo) not in enc: drop.add(cp)
    for t in ft["cmap"].tables:
        for cp in drop: t.cmap.pop(cp, None)
    return sorted(drop)


def build_statics(M, H):
    fonts = {}
    for sch, fn in STATICS.items():
        ft = TTFont(os.path.join(INPUT, fn))
        targetH = glyph_area(ft, 0x48)
        for _, uni in IMPORTS:
            recI, advI, _ = pick_and_interp(M, H, uni, targetH)
            add_cid_glyph(ft, uni, recI, advI)
        recA, advA, _ = pick_and_interp(M, H, 0x26, targetH)   # ampersand
        replace_glyph_outline(ft, 0x26, recA, advA)
        sp = ft.getBestCmap()[0x20]
        add_cid_glyph(ft, 0xA0, [], ft["hmtx"][sp][0])         # NBSP
        # mirror the single guillemets: make › the exact mirror of ‹
        rL, aL = grec(ft, 0x2039); rR, aR = grec(ft, 0x203A)
        Lx1 = max(x for _, p in rL for x, _ in p); Lrsb = aL - Lx1
        Rx0 = min(x for _, p in rR for x, _ in p); shift = Lrsb - Rx0
        rR2 = [(c, tuple((x + shift, y) for x, y in p)) for c, p in rR]
        replace_glyph_outline(ft, 0x203A, rR2, aL)
        add_notdef_box(ft)
        remove_case_orphans(ft)
        fix_meta(ft, f"GoetheanumSchrift-{sch}", f"Goetheanum Schrift {sch}")
        fonts[sch] = ft
    wa = int(round(max(gbbox(f)[0] for f in fonts.values())))
    wd = int(round(-min(gbbox(f)[1] for f in fonts.values())))
    for sch, ft in fonts.items():
        set_win(ft, wa, wd)
        ft.save(os.path.join(OUTROOT, "Fonts", STATICS[sch]))
        print("  Fonts/%s" % STATICS[sch])


def build_icons():
    p = glob.glob(os.path.join(INPUT, "Goetheanum-Icons-*.otf"))[0]
    ft = TTFont(p)
    fix_meta(ft, "GoetheanumIcons", "Goetheanum Icons")
    add_notdef_box(ft)
    sp = ft.getBestCmap()[0x20]
    add_cid_glyph(ft, 0xA0, [], ft["hmtx"][sp][0], prefer_name="uni00A0")
    ym, yn = gbbox(ft); set_win(ft, int(round(ym)), int(round(-yn)))
    ft.save(os.path.join(OUTROOT, "Fonts", os.path.basename(p)))
    print("  Fonts/%s" % os.path.basename(p))


def build_variable():
    p = glob.glob(os.path.join(INPUT, "Goetheanum-Variabel-*.otf"))[0]
    ft = TTFont(p)
    fix_meta(ft, "GoetheanumVariabel", "Goetheanum Variabel", weight_class=450)
    ym, yn = gbbox(ft); set_win(ft, int(round(ym)), int(round(-yn)))
    ft.save(os.path.join(OUTROOT, "Variable", os.path.basename(p)))
    print("  Variable/%s" % os.path.basename(p))


def build_webfonts():
    for p in (glob.glob(os.path.join(OUTROOT, "Fonts", "*.otf")) +
              glob.glob(os.path.join(OUTROOT, "Variable", "*.otf"))):
        base = os.path.splitext(os.path.basename(p))[0]
        for fl in ("woff", "woff2"):
            f = TTFont(p); f.flavor = fl
            f.save(os.path.join(OUTROOT, "Webfonts", fl, "%s.%s" % (base, fl)))
    print("  Webfonts/{woff,woff2}/*")


def main():
    for sub in ("Fonts", "Variable", "Webfonts/woff", "Webfonts/woff2"):
        os.makedirs(os.path.join(OUTROOT, sub), exist_ok=True)
    M, H = load_uprights()
    print("Building corrected Goetheanum Schriften ->", OUTROOT)
    build_statics(M, H)
    build_icons()
    build_variable()
    build_webfonts()
    print("done.")


if __name__ == "__main__":
    main()
