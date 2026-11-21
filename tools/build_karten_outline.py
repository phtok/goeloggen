#!/usr/bin/env python3
"""Pfaddaten der Hausschrift für den Visitenkarten-Generator (SVG/PDF-Export mit Textpfaden).

Quelle: assets/fonts/goetheanum/Fonts/ (v2.9). Schnitte wie im Generator:
Gewicht 300 = Ruhig, 400 = Klar, 600 = Deutlich. Schreibt
assets/goetheanum-outline-glyphs.js (UPM 1000). Idempotent.
Aufruf: python3 tools/build_karten_outline.py   (braucht fontTools)
"""
import json, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZEICHEN = [chr(c) for c in list(range(32, 127)) + list(range(160, 384))] + list("–—‘’‚“”„«»‹›•…€−")
SCHNITTE = {"300": "Ruhig", "400": "Klar", "600": "Deutlich"}

def main():
    out = {"upm": 1000, "fonts": {}}
    for gewicht, name in SCHNITTE.items():
        f = TTFont(os.path.join(ROOT, f"assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-{name}.otf"))
        upm = f["head"].unitsPerEm
        cmap, gs, hm = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
        d = {}
        for c in dict.fromkeys(ZEICHEN):
            g = cmap.get(ord(c))
            if g is None:
                continue
            pen = SVGPathPen(gs, ntos=lambda v: "%g" % round(v * 1000 / upm, 1))
            gs[g].draw(pen)
            d[c] = {"path": pen.getCommands(), "width": round(hm[g][0] * 1000 / upm)}
        out["fonts"][gewicht] = d
    p = os.path.join(ROOT, "assets/goetheanum-outline-glyphs.js")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("window.GOETHEANUM_OUTLINE_UPM=1000;window.GOETHEANUM_OUTLINE_GLYPHS="
                 + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")

if __name__ == "__main__":
    main()
