#!/usr/bin/env python3
"""Baut «Goetheanum Pfeile» — einen eigenen, klein gehaltenen Font nur für die
Pfeile und den Kompass, abgeleitet aus dem Icon-Font.

Warum ein eigener Font? Die Pfeil-/Kompass-Zeichen liegen im Icon-Font im
Zeichen-Privatbereich (PUA) und sind daher nur über Option/Alt oder eine
Glyphenpalette erreichbar. Dieser Font legt dieselben 20 Zeichen zusätzlich auf
NORMALE Tasten (Belegung ‹A›, Beipackzettel-treu): Schrift wählen, Taste tippen –
kein Option, kein PUA, keine Tastaturbelegungsdatei. Die PUA-Codepoints bleiben
zusätzlich erhalten (Abwärtskompatibilität).

Belegung A (Grundtaste → Zeichen):
  6 t u h            gerade Pfeile  ↑ ← → ↓
  & T U H (Umschalt) fette Pfeile   (Umschalt = fett)
  2 0 q e o ü s ö    gebogene Pfeile 1–8
  y x c v            Kompass 1–4

Reproduzierbar aus sauberem Stand:
  python3 tools/goetheanum-fontfix/build_pfeile.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(ROOT, "assets/fonts/goetheanum")
ICON_OTF = os.path.join(FONTS, "Fonts/Goetheanum-Icons-v2.7.otf")
VERSION = "2.7"

# Grundtaste (Unicode) → Pfeil-/Kompass-Codepoint (PUA) desselben Glyphs.
SCHEME = {
    0x36: 0xE264, 0x74: 0xE267, 0x75: 0xE265, 0x68: 0xE266,   # 6 t u h  ↑ ← → ↓
    0x26: 0xE268, 0x54: 0xE26B, 0x55: 0xE269, 0x48: 0xE26A,   # & T U H  fett
    0x32: 0xE260, 0x30: 0xE261, 0x71: 0xE262, 0x65: 0xE263,   # 2 0 q e  gebogen 1–4
    0x6F: 0xE26C, 0xFC: 0xE26D, 0x73: 0xE26E, 0xF6: 0xE26F,   # o ü s ö  gebogen 5–8
    0x79: 0xE243, 0x78: 0xE244, 0x63: 0xE245, 0x76: 0xE246,   # y x c v  Kompass 1–4
}
PUA = sorted(set(SCHEME.values()))

OUT_OTF = os.path.join(FONTS, "Fonts/Goetheanum-Pfeile-v%s.otf" % VERSION)
OUT_WOFF = os.path.join(FONTS, "Webfonts/woff/Goetheanum-Pfeile-v%s.woff" % VERSION)
OUT_WOFF2 = os.path.join(FONTS, "Webfonts/woff2/Goetheanum-Pfeile-v%s.woff2" % VERSION)


def _bbox(ft):
    gs = ft.getGlyphSet(); asc = 0; desc = 0
    for gn in ft.getGlyphOrder():
        bp = BoundsPen(gs); gs[gn].draw(bp)
        if bp.bounds:
            asc = max(asc, bp.bounds[3]); desc = min(desc, bp.bounds[1])
    return int(round(asc)), int(round(-desc))


def build():
    ft = TTFont(ICON_OTF)
    # Auf die 20 Pfeil-/Kompass-Glyphen + Leerzeichen verkleinern.
    opt = Options(); opt.name_IDs = ["*"]; opt.notdef_outline = True
    opt.glyph_names = True; opt.layout_features = []; opt.recalc_bounds = True
    ss = Subsetter(options=opt); ss.populate(unicodes=PUA + [0x20]); ss.subset(ft)
    # Grundtasten zusätzlich belegen (PUA bleibt erhalten).
    name_by_pua = {c: ft.getBestCmap()[c] for c in PUA}
    for base, pua in SCHEME.items():
        for t in ft["cmap"].tables:
            t.cmap[base] = name_by_pua[pua]
    # Namen: Lizenz/Copyright/Vendor/Version aus dem Icon-Font übernehmen,
    # nur die Familien-/Stil-/PS-Namen auf «Goetheanum Pfeile» setzen.
    n = ft["name"]; n.names = [r for r in n.names if r.platformID != 1]
    def setn(i, v): n.setName(v, i, 3, 1, 0x409)
    setn(1, "Goetheanum Pfeile"); setn(2, "Regular"); setn(4, "Goetheanum Pfeile")
    setn(3, "%s;GOEA;GoetheanumPfeile" % VERSION); setn(5, "Version %s" % VERSION)
    setn(6, "GoetheanumPfeile-Regular")
    setn(16, "Goetheanum Pfeile"); setn(17, "Regular")
    for extra in (21, 22):
        n.setName("Goetheanum Pfeile" if extra == 21 else "Regular", extra, 3, 1, 0x409)
    if "CFF " in ft:
        cff = ft["CFF "].cff; cff.fontNames = ["GoetheanumPfeile"]
        try: cff[cff.fontNames[0]].rawDict["FullName"] = "Goetheanum Pfeile"
        except Exception: pass
    # Vertikale Metriken an den Zeichenbestand anpassen (typo bleibt 750/-250).
    wa, wd = _bbox(ft); o = ft["OS/2"]; o.usWinAscent = wa; o.usWinDescent = wd

    ft.flavor = None; ft.save(OUT_OTF)
    ft.flavor = "woff"; ft.save(OUT_WOFF)
    ft.flavor = "woff2"; ft.save(OUT_WOFF2)
    print("✓ Goetheanum Pfeile: %d Glyphen · %d Grundtasten + %d PUA belegt" %
          (len(TTFont(OUT_OTF).getGlyphOrder()), len(SCHEME), len(PUA)))
    for p in (OUT_OTF, OUT_WOFF, OUT_WOFF2):
        print("  →", os.path.relpath(p, ROOT))
    _office_ttf()
    _bundle_zips()


def _office_ttf():
    """Office-TTF (glyf/cu2qu) bauen und in Office/ + Office-TTF.zip aufnehmen."""
    import sys, glob, zipfile
    sys.path.insert(0, HERE)
    from build_office_ttf import otf_to_ttf, setname
    office_dir = os.path.join(FONTS, "Office")
    out_ttf = os.path.join(office_dir, "GoetheanumPfeile.ttf")
    ft = TTFont(OUT_OTF); otf_to_ttf(ft); setname(ft, "Goetheanum Pfeile", "GoetheanumPfeileOffice")
    ft.save(out_ttf)
    print("  →", os.path.relpath(out_ttf, ROOT))
    # Office-TTF.zip: die eine TTF ergänzen (übrige Einträge unverändert lassen).
    zpath = os.path.join(FONTS, "Goetheanum-Office-TTF.zip")
    z = zipfile.ZipFile(zpath); items = {n: z.read(n) for n in z.namelist()}; z.close()
    items["GoetheanumPfeile.ttf"] = open(out_ttf, "rb").read()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in sorted(items):
            zi = zipfile.ZipInfo(n, date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            zo.writestr(zi, items[n])
    print("  → Goetheanum-Office-TTF.zip (+ GoetheanumPfeile.ttf)")


def _bundle_zips():
    """Die vier Pfeile-Dateien ins Komplett-Bündel Goetheanum-Schriften-v2.7.zip legen."""
    import zipfile
    zpath = os.path.join(FONTS, "Goetheanum-Schriften-v2.7.zip")
    z = zipfile.ZipFile(zpath); items = {n: z.read(n) for n in z.namelist()}; z.close()
    base = "Goetheanum-Schriften-v%s/" % VERSION
    add = {
        base + "Fonts/Goetheanum-Pfeile-v%s.otf" % VERSION: OUT_OTF,
        base + "Webfonts/woff/Goetheanum-Pfeile-v%s.woff" % VERSION: OUT_WOFF,
        base + "Webfonts/woff2/Goetheanum-Pfeile-v%s.woff2" % VERSION: OUT_WOFF2,
        base + "Office/GoetheanumPfeile.ttf": os.path.join(FONTS, "Office/GoetheanumPfeile.ttf"),
    }
    for arc, src in add.items():
        items[arc] = open(src, "rb").read()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in sorted(items):
            zi = zipfile.ZipInfo(n, date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            zo.writestr(zi, items[n])
    print("  → Goetheanum-Schriften-v%s.zip (+ 4 Pfeile-Dateien)" % VERSION)


if __name__ == "__main__":
    build()
