#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalisiert die Icon-Einzeldateien auf EINE einheitliche viewBox.

Befund (docs/learnings-kartentool.md, verifiziert 6.7.2026): nur 46 von 81
SVG-Einzeldateien trugen die Standardbox — die übrigen (WC-Familie, Badges,
einige Reihen) hatten enge Eigen-Boxen. Konsumenten, die auf die viewBox
skalieren, setzten solche Icons schief und zu klein.

Lösung (ratifiziert 9.7.2026): Alle Einzeldateien werden idempotent AUS DEM
ICON-FONT regeneriert (Metriken = Font-Wahrheit) mit einheitlicher Em-Box
  viewBox="-2 -1002 1004 1004"
(2 Einheiten Rand: die Badge-Tinte reicht bis x=1001). Konvention wie bisher:
ein <path transform="scale(1,-1)"> mit Font-Koordinaten (y-oben).

Ausnahme: die Wortmarke (icon-0021, U+0021) ist kein Piktogramm — Tinte
5970×1000; sie behält eine proportionale Box (0 -1000 5970 1000) und ist in
design-system/werkzeugwissen.md als Ausnahme vermerkt.

Erzeugt je Icon svg/ + png/ (512 px Kante) + pdf/ und packt das
Einzeldateien-ZIP deterministisch neu (Beipackzettel bleibt enthalten).
Idempotent: zweiter Lauf ändert nichts.
"""
import os, json, zipfile, io
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(ROOT, "assets/fonts/goetheanum")
OTF = os.path.join(FONTS, "Fonts/Goetheanum-Icons-v2.7.otf")
D = os.path.join(FONTS, "Icons-Einzeldateien")
ZIPP = os.path.join(FONTS, "Goetheanum-Icons-v2.7-Einzeldateien.zip")
BOX = "-2 -1002 1004 1004"            # einheitliche Em-Box (2 Einheiten Rand)
WORTMARKE = "icon-0021"                # Ausnahme: proportionale Box

def main():
    ft = TTFont(OTF)
    gs = ft.getGlyphSet(); cm = ft.getBestCmap()
    icons = json.load(open(os.path.join(D, "icons.json"), encoding="utf-8"))
    # ‹mit Text›-Varianten sind bewusst NUR Webfont (icons.html) – keine Einzeldateien.
    aktiv = [it for it in icons if not it.get("fontonly")]
    soll = {it["slug"] for it in aktiv}
    # Waisen entfernen: Dateien ohne Eintrag (z. B. die alten unbenannten
    # Grossbuchstaben-Singles icon-0041 …, deren Glyphen jetzt ‹mit Text› heissen).
    for sub, ext in (("svg", ".svg"), ("png", ".png"), ("pdf", ".pdf")):
        for f in sorted(os.listdir(os.path.join(D, sub))):
            slug = f[:-len(ext)]
            if f.endswith(ext) and slug not in soll:
                os.remove(os.path.join(D, sub, f)); print("entfernt:", sub + "/" + f)
    n = 0
    for it in aktiv:
        cp = int(it["codepoint"][2:], 16)
        gn = cm.get(cp)
        if not gn:
            print("!! kein Glyph:", it["slug"]); continue
        pen = SVGPathPen(gs); gs[gn].draw(pen)
        d = pen.getCommands()
        if it["slug"] == WORTMARKE:
            bp = BoundsPen(gs); gs[gn].draw(bp)
            x0, y0, x1, y1 = bp.bounds
            box = f"{x0:g} {-y1:g} {x1-x0:g} {y1-y0:g}"
        else:
            box = BOX
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}">'
               f'<path transform="scale(1,-1)" d="{d}"/></svg>')
        p_svg = os.path.join(D, "svg", it["slug"] + ".svg")
        p_png = os.path.join(D, "png", it["slug"] + ".png")
        p_pdf = os.path.join(D, "pdf", it["slug"] + ".pdf")
        alt = open(p_svg, encoding="utf-8").read() if os.path.exists(p_svg) else ""
        geaendert = alt != svg
        if geaendert:
            open(p_svg, "w", encoding="utf-8").write(svg)
        # Derivate nur bei geänderter Quelle neu (cairo bettet Zeitstempel in die
        # PDF-Metadaten – Neuerzeugen ohne Not bräche die Idempotenz).
        if geaendert or not os.path.exists(p_png):
            cairosvg.svg2png(bytestring=svg.encode(), write_to=p_png, output_width=512)
        if geaendert or not os.path.exists(p_pdf):
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p_pdf)
        n += 1
    print(f"{n} Icons regeneriert (Box {BOX}; Ausnahme {WORTMARKE} proportional)")

    # ZIP deterministisch neu packen: Beipackzettel aus dem alten ZIP übernehmen.
    beipack = None
    if os.path.exists(ZIPP):
        with zipfile.ZipFile(ZIPP) as z:
            for name in z.namelist():
                if name.endswith(".pdf") and "/" not in name:
                    beipack = (name, z.read(name))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        def put(name, data):
            zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
        if beipack:
            put(*beipack)
        for sub in ("pdf", "png", "svg"):
            for f in sorted(os.listdir(os.path.join(D, sub))):
                put(f"{sub}/{f}", open(os.path.join(D, sub, f), "rb").read())
    neu = buf.getvalue()
    alt_zip = open(ZIPP, "rb").read() if os.path.exists(ZIPP) else b""
    if neu != alt_zip:
        open(ZIPP, "wb").write(neu)
    with zipfile.ZipFile(ZIPP) as z:
        print("ZIP:", len(z.namelist()), "Einträge",
              "(unverändert)" if neu == alt_zip else "(neu gepackt)",
              "->", os.path.relpath(ZIPP, ROOT))

if __name__ == "__main__":
    main()
