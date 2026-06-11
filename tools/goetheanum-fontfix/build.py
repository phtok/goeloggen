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
from fontTools.varLib.cff import CFF2CharStringMergePen
from fontTools.varLib.models import VariationModel

# Variable font: wght axis 280/450/600, no avar -> normalized 280=-1, 450=0, 600=+1.
# Masters drawn into the merge pen in order [default(Klar), region -1 (Leise), region +1 (Laut)].
VAR_TARGETS = {280: 87500, 450: 140000, 600: 177400}     # H-area weight targets
_VMODEL = VariationModel([{}, {"wght": -1.0}, {"wght": 1.0}], axisOrder=["wght"])

INPUT = os.path.join(HERE, "input")
OUTROOT = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "fonts", "goetheanum"))
VERSION = "2.0.0"                       # repaired/optimized release (fresh major)
FREV = 2.0                              # head.fontRevision
SCHEMES = ["Leise", "Klar", "Laut"]
IMPORTS = [("exclam", 0x21), ("quotedbl", 0x22), ("dollar", 0x24), ("section", 0xA7)]


def static_in(sch):
    return glob.glob(os.path.join(INPUT, "Goetheanum-Schrift-*-%s.otf" % sch))[0]


def static_out(sch):
    return "Goetheanum-Schrift-v%s-%s.otf" % (VERSION, sch)

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
    setn(4, full); setn(6, ps); setn(3, f"{VERSION};GOEA;{ps}"); setn(5, f"Version {VERSION}")
    setn(0, COPYRIGHT)
    setn(7, "Titillium is a Reserved Font Name of Accademia di Belle Arti di Urbino.")
    setn(8, "Goetheanum Kommunikation")
    setn(9, "Goetheanum Kommunikation; based on Titillium by Accademia di Belle Arti di "
            "Urbino (Luca Antonucci et al.)")
    setn(11, "https://www.goetheanum.org")
    setn(13, LICENSE); setn(14, "https://openfontlicense.org")
    ft["head"].fontRevision = FREV; ft["head"].macStyle = 0
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
    for sch in SCHEMES:
        ft = TTFont(static_in(sch))
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
        ft.save(os.path.join(OUTROOT, "Fonts", static_out(sch)))
        print("  Fonts/%s" % static_out(sch))


def build_icons():
    # The icon font ships a documented keyboard layout (letters -> pictograms,
    # Option/Alt -> arrows; see Beipackzettel). That cmap is the intended
    # interface and is kept intact; we only fix metadata, .notdef and NBSP.
    p = glob.glob(os.path.join(INPUT, "Goetheanum-Icons-*.otf"))[0]
    ft = TTFont(p)
    fix_meta(ft, "GoetheanumIcons", "Goetheanum Icons")
    add_notdef_box(ft)
    sp = ft.getBestCmap()[0x20]
    add_cid_glyph(ft, 0xA0, [], ft["hmtx"][sp][0], prefer_name="uni00A0")
    ym, yn = gbbox(ft); set_win(ft, int(round(ym)), int(round(-yn)))
    out = "Goetheanum-Icons-v%s.otf" % VERSION
    ft.save(os.path.join(OUTROOT, "Fonts", out))
    print("  Fonts/%s" % out)


def _replay(pen, recv):
    for c, p in recv:
        getattr(pen, c)(*p) if p else getattr(pen, c)()


def _cff2_blend(outl, priv, gsubrs):
    """Build a CFF2 charstring that interpolates the three master outlines
    (keys 450/280/600) across the wght axis."""
    pen = CFF2CharStringMergePen([], "tmp", 3, 0)
    _replay(pen, outl[450]); pen.restart(1); _replay(pen, outl[280]); pen.restart(2); _replay(pen, outl[600])
    return pen.getCharString(private=priv, globalSubrs=gsubrs, var_model=_VMODEL, optimize=True)


def _cff2_add(ft, uni, cs, adv, name):
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    cmap = ft.getBestCmap()
    if uni in cmap:
        name = cmap[uni]; td.CharStrings[name] = cs           # replace existing
    else:
        td.CharStrings.charStringsIndex.append(cs)
        td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
        td.charset.append(name)
        if hasattr(td, "FDSelect"): td.FDSelect.append(0)
        ft.setGlyphOrder(list(td.charset))
        for t in ft["cmap"].tables: t.cmap[uni] = name
    ft["hmtx"].metrics[name] = (adv, 0)
    ft["HVAR"].table.AdvWidthMap.mapping[name] = 0xFFFFFFFF    # constant advance for added glyph
    return name


def complete_variable(ft, M, H):
    """Give the variable font the same glyph repertoire as the statics: import
    ! " § as interpolating blends, rebuild the ampersand so it varies, add $
    (non-varying: its Titillium masters are not point-compatible across the
    range) and NBSP."""
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    priv = td.FDArray[0].Private; gsubrs = cff.GlobalSubrs

    def outl(uni, w):
        r, a, _ = pick_and_interp(M, H, uni, VAR_TARGETS[w]); return r, a

    for uni, nm in [(0x26, None), (0x21, "uni0021"), (0x22, "uni0022"), (0xA7, "uni00A7")]:
        ow = {w: outl(uni, w)[0] for w in (280, 450, 600)}
        _cff2_add(ft, uni, _cff2_blend(ow, priv, gsubrs), outl(uni, 450)[1], nm)
    dr, da = outl(0x24, 450)                                   # dollar: non-varying (Klar weight)
    _cff2_add(ft, 0x24, _cff2_blend({280: dr, 450: dr, 600: dr}, priv, gsubrs), da, "dollar")
    spn = ft.getBestCmap()[0x20]                               # NBSP: reuse the space charstring
    _cff2_add(ft, 0xA0, td.CharStrings[spn], ft["hmtx"][spn][0], "uni00A0")


def _cff2_notdef(ft):
    cff = ft["CFF2"].cff; td = cff[cff.fontNames[0]]
    box = [("moveTo", ((60, 0),)), ("lineTo", ((440, 0),)), ("lineTo", ((440, 700),)),
           ("lineTo", ((60, 700),)), ("closePath", ()),
           ("moveTo", ((120, 60),)), ("lineTo", ((120, 640),)), ("lineTo", ((380, 640),)),
           ("lineTo", ((380, 60),)), ("closePath", ())]
    td.CharStrings[".notdef"] = _cff2_blend({280: box, 450: box, 600: box},
                                            td.FDArray[0].Private, cff.GlobalSubrs)
    ft["hmtx"].metrics[".notdef"] = (500, 60)


def build_variable(M, H):
    from fontTools.otlLib.builder import buildStatTable
    src = glob.glob(os.path.join(INPUT, "Goetheanum-Variabel-*.otf"))[0]
    p = "Goetheanum-Variabel-v%s.otf" % VERSION
    ft = TTFont(src)
    complete_variable(ft, M, H)
    _cff2_notdef(ft)
    remove_case_orphans(ft)
    fix_meta(ft, "GoetheanumVariabel", "Goetheanum Variabel", weight_class=450)
    # default (450) instance must carry the family default style/PS names
    ft["name"].setName("Klar", 17, 3, 1, 0x409)
    for inst in ft["fvar"].instances:
        if abs(inst.coordinates.get("wght", 0) - 450) < 0.5:
            inst.subfamilyNameID = 17
            inst.postscriptNameID = 6
    # proper STAT table for the weight axis (Klar elided as default)
    buildStatTable(ft, [{"tag": "wght", "name": "Weight", "values": [
        {"value": 280, "name": "Leise"},
        {"value": 450, "name": "Klar", "flags": 0x2},
        {"value": 600, "name": "Laut"}]}])
    ft["name"].names = [r for r in ft["name"].names if r.platformID != 1]  # STAT re-adds Mac names
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


# Documented keyboard layout -> stable slug + label (from the Beipackzettel).
# Lower-case keys carry the plain pictograms (page 3); digits 1/2 the badges.
ICON_KEYS = {
    "2": ("goetheanum-badge", "Goetheanum Badge"),
    "1": ("goetheanum-badge-invers", "Goetheanum Badge invers"),
    "q": ("bitte-anfassen", "Bitte anfassen"),
    "w": ("nur-mit-augen", "Nur mit den Augen"),
    "e": ("eintritt", "Eintritt"),
    "r": ("hunde-anleinen", "Hunde anleinen"),
    "t": ("keine-hunde", "Keine Hunde"),
    "z": ("keine-fotos", "Keine Fotos"),
    "u": ("draussen-essen", "Draussen essen"),
    "i": ("keine-taschen", "Keine Taschen"),
    "o": ("geraete-abschalten", "Geräte abschalten"),
    "a": ("fahrstuhl", "Fahrstuhl"),
    "s": ("treppe", "Treppe"),
    "d": ("schliessfaecher", "Schliessfächer"),
    "f": ("garderobe", "Garderobe"),
    "g": ("wlan", "WLAN"),
    "h": ("bioabfall", "Bioabfall"),
    "j": ("papier", "Papier"),
    "k": ("restmuell", "Restmüll"),
    "<": ("wc-herren", "WC Herren"),
    "y": ("wc-damen", "WC Damen"),
    "x": ("wc-rollstuhl", "WC Rollstuhl"),
    "c": ("wickelraum", "Wickelraum"),
    "v": ("wc-gruppe", "WC Gruppe"),
    "b": ("wc-familie", "WC Familie"),
}


def _glyph_svg(gs, gn, upm):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    if not bp.bounds:
        return None
    x0, y0, x1, y1 = bp.bounds
    side = max(x1 - x0, y1 - y0, 1) * 1.18
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pen = SVGPathPen(gs); gs[gn].draw(pen)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f">'
            '<path transform="scale(1,-1)" d="%s" fill="#1a1a1a"/></svg>'
            % (cx - side / 2, -cy - side / 2, side, side, pen.getCommands()))


def build_icon_exports():
    """Per-icon SVG/PNG/PDF (named from the keyboard layout) + a manifest and a
    download bundle, so every pictogram is individually downloadable."""
    import cairosvg, json, zipfile
    base = os.path.join(OUTROOT, "Icons-Einzeldateien")
    for sub in ("svg", "png", "pdf"):
        d = os.path.join(base, sub)
        for old in glob.glob(os.path.join(d, "*")):
            os.remove(old)
        os.makedirs(d, exist_ok=True)
    ft = TTFont(os.path.join(OUTROOT, "Fonts", "Goetheanum-Icons-v%s.otf" % VERSION))
    cmap = ft.getBestCmap(); gs = ft.getGlyphSet(); upm = ft["head"].unitsPerEm
    named = {cmap[ord(k)]: v for k, v in ICON_KEYS.items() if ord(k) in cmap}
    manifest, seen = [], set()
    for cp, gn in sorted(cmap.items()):
        if cp in (0x20, 0xA0) or gn in seen:
            continue
        svg = _glyph_svg(gs, gn, upm)
        if svg is None:
            continue
        seen.add(gn)
        slug, label = named.get(gn, ("icon-%04x" % cp, "U+%04X" % cp))
        with open(os.path.join(base, "svg", slug + ".svg"), "w") as fh:
            fh.write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(base, "png", slug + ".png"),
                         output_width=512, output_height=512, background_color="rgba(0,0,0,0)")
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=os.path.join(base, "pdf", slug + ".pdf"))
        manifest.append({"slug": slug, "label": label, "codepoint": "U+%04X" % cp})
    manifest.sort(key=lambda m: m["slug"])
    with open(os.path.join(base, "icons.json"), "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    zip_out = os.path.join(OUTROOT, "Goetheanum-Icons-v%s-Einzeldateien.zip" % VERSION)
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
        for src in sorted(glob.glob(os.path.join(base, "*", "*"))):
            zi = zipfile.ZipInfo(os.path.relpath(src, base), date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(src, "rb") as fh:
                z.writestr(zi, fh.read())
    print("  Icons-Einzeldateien/{svg,png,pdf}/* (%d Icons) + ZIP" % len(manifest))


def build_zip():
    """Reproducible distribution bundle (top folder Goetheanum-Schriften-vVERSION)."""
    import zipfile
    top = "Goetheanum-Schriften-v%s" % VERSION
    members = (sorted(glob.glob(os.path.join(OUTROOT, "Fonts", "*.otf"))) +
               sorted(glob.glob(os.path.join(OUTROOT, "Variable", "*.otf"))) +
               sorted(glob.glob(os.path.join(OUTROOT, "Webfonts", "woff", "*.woff"))) +
               sorted(glob.glob(os.path.join(OUTROOT, "Webfonts", "woff2", "*.woff2"))) +
               [os.path.join(OUTROOT, f) for f in
                ("Beipackzettel-Goetheanum-Schriften.pdf", "OFL.txt", "README.md")
                if os.path.exists(os.path.join(OUTROOT, f))])
    out = os.path.join(OUTROOT, top + ".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for src in members:
            arc = os.path.join(top, os.path.relpath(src, OUTROOT))
            zi = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))  # deterministic
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(src, "rb") as fh:
                z.writestr(zi, fh.read())
    print("  %s.zip (%d files)" % (top, len(members)))


def _clean_outputs():
    """Remove previously generated fonts/webfonts/zips so only the current
    version remains (filenames carry the version)."""
    pats = ["Fonts/*.otf", "Variable/*.otf", "Webfonts/woff/*.woff",
            "Webfonts/woff2/*.woff2", "Goetheanum-Schriften-v*.zip",
            "Goetheanum-Icons-v*-Einzeldateien.zip"]
    for pat in pats:
        for f in glob.glob(os.path.join(OUTROOT, pat)):
            os.remove(f)


def main():
    for sub in ("Fonts", "Variable", "Webfonts/woff", "Webfonts/woff2"):
        os.makedirs(os.path.join(OUTROOT, sub), exist_ok=True)
    _clean_outputs()
    M, H = load_uprights()
    print("Building corrected Goetheanum Schriften ->", OUTROOT)
    build_statics(M, H)
    build_icons()
    build_variable(M, H)
    build_webfonts()
    build_icon_exports()
    build_zip()
    print("done.")


if __name__ == "__main__":
    main()
