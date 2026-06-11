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
                     add_cid_glyph, replace_glyph_outline, _charstring, sig, blend)
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
VERSION = "2.1.0"                       # wide variable (Flüstern–Schreien) + Office bold linking
FREV = 2.1                              # head.fontRevision
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
    hm = ft["hmtx"]                                            # clamp the broken Titillium 'fraction' advance
    for gn, (aw, lsb) in list(hm.metrics.items()):
        if aw > 3000 or aw < 0:
            hm.metrics[gn] = (600, lsb)
    if "CFF " in ft: ft["CFF "].cff.fontNames = [ps]


def set_win(ft, wa, wd):
    o = ft["OS/2"]; o.usWinAscent = wa; o.usWinDescent = wd


# Office/Word style-linking. Modern apps group by the typographic family (16/17)
# = "Goetheanum Schrift" + weight; the legacy RIBBI family (1/2) is what Office's
# Cmd/Ctrl+B follows, so Klar/Laut form one Regular+Bold pair (bold toggles
# Klar->Laut) while the other weights are their own Regular-only RIBBI families.
def office_names(ft, ribbi_family, ribbi_style, typo_sub, bold=False):
    n = ft["name"]

    def setn(i, v): n.setName(v, i, 3, 1, 0x409)
    setn(1, ribbi_family); setn(2, ribbi_style)
    setn(16, "Goetheanum Schrift"); setn(17, typo_sub)
    o = ft["OS/2"]                                             # bit0 ITALIC, bit5 BOLD, bit6 REGULAR
    if bold:
        o.fsSelection = (o.fsSelection & ~0x41) | 0x20         # clear REGULAR+ITALIC, set BOLD
        ft["head"].macStyle |= 0x1
    else:
        o.fsSelection = (o.fsSelection & ~0x21) | 0x40         # clear BOLD+ITALIC, set REGULAR
        ft["head"].macStyle &= ~0x1


OFFICE = {"Leise": ("Goetheanum Schrift Leise", "Regular", False),
          "Klar":  ("Goetheanum Schrift", "Regular", False),
          "Laut":  ("Goetheanum Schrift", "Bold", True)}


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
        office_names(ft, *OFFICE[sch][:2], sch, bold=OFFICE[sch][2])
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


# Wide variable font, derived from the Titillium upright masters. Each master is
# placed on the wght axis by its H-area (fitted to the Leise/Klar/Laut anchors);
# Flüstern (thin) and Schreien (black) extend the range past Leise/Laut.
WIDE_MASTERS = [("Thin", 63006, 190), ("Light", 103435, 335), ("Regular", 126847, 420),
                ("Klar", 140000, 450), ("Semibold", 177393, 600), ("Bold", 212760, 725)]
WIDE_INSTANCES = [("Flüstern", 190), ("Leise", 280), ("Klar", 450), ("Laut", 600), ("Schreien", 725)]
VAR_DEFAULT = 450


def _compat_group(M, H, uni):
    """Largest point-compatible Titillium master group for this glyph."""
    from collections import defaultdict
    cand = [(n, grec(M[n], uni)[0]) for n in M]
    cand = [(n, r) for n, r in cand if r is not None]
    if not cand:
        return None
    groups = defaultdict(list)
    for n, r in cand:
        groups[sig(r)].append(n)
    return max(groups.values(),
               key=lambda ns: (len(ns), H[max(ns, key=lambda n: H[n])] - H[min(ns, key=lambda n: H[n])]))


def _outline_at(M, H, uni, targetH, ns):
    ns = sorted(ns, key=lambda n: H[n])
    lo = max([n for n in ns if H[n] <= targetH], key=lambda n: H[n], default=ns[0])
    hi = min([n for n in ns if H[n] >= targetH], key=lambda n: H[n], default=ns[-1])
    if lo == hi:
        if len(ns) == 1:
            return grec(M[ns[0]], uni)
        lo, hi = ns[0], ns[-1]
    rA, aA = grec(M[lo], uni); rB, aB = grec(M[hi], uni)
    t = (targetH - H[lo]) / (H[hi] - H[lo]) if H[hi] != H[lo] else 0.0
    t = max(0.0, min(1.0, t))                                   # clamp: no extrapolation -> no degeneration
    return blend(rA, aA, rB, aB, t)


def build_variable(M, H):
    import tempfile
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.designspaceLib import DesignSpaceDocument
    from fontTools import varLib
    from fontTools.otlLib.builder import buildStatTable

    base = os.path.join(OUTROOT, "Fonts", static_out("Klar"))   # built by build_statics
    cmap = TTFont(base).getBestCmap()
    groups = {cp: _compat_group(M, H, cp) for cp in cmap}

    tmp = tempfile.mkdtemp(); paths = []
    for name, Ht, wght in WIDE_MASTERS:                          # one master per Titillium weight
        ft = TTFont(base); td = ft["CFF "].cff[ft["CFF "].cff.fontNames[0]]
        for cp, ns in groups.items():
            gn = cmap.get(cp)
            if gn is None or not ns:
                continue
            rec, adv = _outline_at(M, H, cp, Ht, ns)
            td.CharStrings[gn] = _charstring(ft, [(c, p) for c, p in rec], adv)
            ft["hmtx"].metrics[gn] = (int(round(adv)), ft["hmtx"][gn][1])
        p = os.path.join(tmp, "m_%d.otf" % wght); ft.save(p); paths.append(p)

    # force-constant any glyph whose drawn outline is not identical across all masters
    fonts = [TTFont(p) for p in paths]; gsets = [f.getGlyphSet() for f in fonts]
    di = [w for _, _, w in WIDE_MASTERS].index(VAR_DEFAULT)

    def cmds(gs, gn):
        r = RecordingPen(); gs[gn].draw(r); return tuple(c for c, _ in r.value)

    for gn in fonts[0].getGlyphOrder():
        if len({cmds(g, gn) for g in gsets}) != 1:
            rd = RecordingPen(); gsets[di][gn].draw(rd); adv = fonts[di]["hmtx"][gn][0]
            for f in fonts:
                td = f["CFF "].cff[f["CFF "].cff.fontNames[0]]
                td.CharStrings[gn] = _charstring(f, list(rd.value), adv)
                f["hmtx"].metrics[gn] = (adv, f["hmtx"][gn][1])
    for f, p in zip(fonts, paths):
        f.save(p)

    ds = DesignSpaceDocument()
    ds.addAxisDescriptor(name="Weight", tag="wght", minimum=WIDE_MASTERS[0][2],
                         default=VAR_DEFAULT, maximum=WIDE_MASTERS[-1][2])
    for p, (name, Ht, wght) in zip(paths, WIDE_MASTERS):
        s = ds.addSourceDescriptor(path=p, location={"Weight": wght})
        if wght == VAR_DEFAULT:
            s.copyInfo = True
    for nm, w in WIDE_INSTANCES:
        ds.addInstanceDescriptor(familyName="Goetheanum Variabel", styleName=nm, location={"Weight": w})
    ft, _, _ = varLib.build(ds)

    fix_meta(ft, "GoetheanumVariabel", "Goetheanum Variabel", weight_class=450)
    nm = ft["name"]
    nm.setName("Goetheanum Variabel", 1, 3, 1, 0x409); nm.setName("Regular", 2, 3, 1, 0x409)
    nm.setName("Goetheanum Variabel", 16, 3, 1, 0x409); nm.setName("Klar", 17, 3, 1, 0x409)
    nm.names = [r for r in nm.names if r.nameID not in (21, 22)]   # drop WWS names from the Klar master

    def _ascii(s):
        return (s.replace("ü", "ue").replace("ö", "oe").replace("ä", "ae")
                 .replace("ß", "ss").replace(" ", ""))

    nextid = max(r.nameID for r in nm.names) + 1
    for inst in ft["fvar"].instances:                          # every instance gets a PS name -> uniform records
        if abs(inst.coordinates.get("wght", 0) - VAR_DEFAULT) < 0.5:
            inst.subfamilyNameID = 17; inst.postscriptNameID = 6
        else:
            nm.setName("GoetheanumVariabel-" + _ascii(nm.getDebugName(inst.subfamilyNameID)),
                       nextid, 3, 1, 0x409)
            inst.postscriptNameID = nextid; nextid += 1
    buildStatTable(ft, [{"tag": "wght", "name": "Weight", "values": [
        {"value": 190, "name": "Flüstern"},
        {"value": 280, "name": "Leise"},
        {"value": 450, "name": "Klar", "flags": 0x2},
        {"value": 600, "name": "Laut"},
        {"value": 725, "name": "Schreien"}]}])
    ft["name"].names = [r for r in ft["name"].names if r.platformID != 1]
    ym, yn = gbbox(ft); set_win(ft, int(round(ym)), int(round(-yn)))
    out = "Goetheanum-Variabel-v%s.otf" % VERSION
    ft.save(os.path.join(OUTROOT, "Variable", out))
    print("  Variable/%s (Flüstern–Schreien)" % out)


def build_extra_statics():
    """Flüstern (190) and Schreien (725) as installable statics, instanced from
    the variable. Each is its own Regular-only RIBBI family; modern apps still
    group them under 'Goetheanum Schrift' via the typographic names."""
    from fontTools.varLib.instancer import instantiateVariableFont
    vf = os.path.join(OUTROOT, "Variable", "Goetheanum-Variabel-v%s.otf" % VERSION)
    for nm, w, ps in [("Flüstern", 190, "Fluestern"), ("Schreien", 725, "Schreien")]:
        ft = TTFont(vf)
        instantiateVariableFont(ft, {"wght": w}, inplace=True)
        fix_meta(ft, "GoetheanumSchrift-%s" % ps, "Goetheanum Schrift %s" % nm, weight_class=w)
        office_names(ft, "Goetheanum Schrift %s" % nm, "Regular", nm, bold=False)
        ym, yn = gbbox(ft); set_win(ft, int(round(ym)), int(round(-yn)))
        out = "Goetheanum-Schrift-v%s-%s.otf" % (VERSION, ps)
        ft.save(os.path.join(OUTROOT, "Fonts", out))
        print("  Fonts/%s" % out)


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
    build_extra_statics()
    build_webfonts()
    build_icon_exports()
    build_zip()
    print("done.")


if __name__ == "__main__":
    main()
