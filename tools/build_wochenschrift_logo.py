#!/usr/bin/env python3
"""Wochenschrift-Logo (neu): Bildmarke + «Das Goetheanum» in der Hausschrift.

Mass nach der Wochenschrift-Website (wochenschrift.xdev.ai, .brand-mark):
Wort in Goetheanum Schrift Variable wght 595, Versalhöhe 0,7396 H, Laufweite
−0,0079 em, Grundlinie bei 0,9115 H, Tinte des ‹D› bei 1,1302 H. Wortabstand
auf 75 % des Leerzeichens (Entscheid Inhaber 21. 11. 2026; Website: 100 %).

Formen (assets/logos/medien/wochenschrift/):
  weblogo           Bildmarke + Wort
  point-einzeilig   Bildmarke im Kreis + Wort (Kreis 1,776 Versalhöhen, Abstand
                    zum Wort 0,467 Versalhöhen, Mitte auf Mitte der Versalhöhe)
je Farbe, Schwarz, Weiss als SVG, PNG, JPG (Weiss ohne JPG).
Aufruf: python3 tools/build_wochenschrift_logo.py
Braucht fontTools, uharfbuzz, cairosvg, Pillow. Idempotent.
"""
import os, io
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets/logos/medien/wochenschrift")
FONT = os.path.join(ROOT, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf")
KREIS_SVG = os.path.join(ROOT, "assets/logos/goetheanum-icon-kreis.svg")
TEXT = "Das Goetheanum"
H = 960.0                     # Logohöhe der Bildmarken-Form in Einheiten (24 px × 40)
K = H / 24.0
CAP = 0.7396 * H              # Versalhöhe der Website (17,75 von 24 px)
FS = None                     # Schriftgrad: aus der Versalhöhe der Hausschrift abgeleitet
TRACK = -0.0079               # Laufweite in em
WGHT = 595
WORT_ABSTAND = 0.75           # Faktor auf die Breite des Leerzeichens
BASE_Y = 0.9115 * H           # Grundlinie von oben (Bildmarken-Form)
D_INK_X = 27.125 * K          # Tinte-Beginn des ‹D› (Bildmarken-Form)
KREIS_D = 1.776 * CAP         # Kreisdurchmesser
KREIS_GAP = 0.467 * CAP       # Kreis bis Tinte des ‹D›

MARK = [  # Bildmarke, Koordinaten 15,8254 × 21,07
 "M5.7224,3.472L15.8254,0v21.07h-6.002l.007-7.74c.003-.501-.086-.969-.242-1.438-.475-1.43-3.866-8.42-3.866-8.42",
 "M5.292,7.1965s3.062,4.895,3.062,6.039l.048,7.834h-3.538l-.022-2.693c-.035-1.633-3.74-6.24-3.74-6.24l4.19-4.94Z",
 "M0,17.9464l2.355-1.673s1.103,1.842,1.201,2.488c.099.646.02,2.309.02,2.309H1.072s.005-.607.008-.876c.007-.476-.144-.883-.375-1.274-.108-.183-.609-.818-.705-.974",
]
MARK_SCALE = H / 21.07

def _font():
    face = hb.Face(open(FONT, "rb").read()); font = hb.Font(face); font.set_variations({"wght": WGHT})
    return face, font

def schriftgrad():
    face, font = _font()
    bp = BoundsPen(None); font.draw_glyph_with_pen(font.get_nominal_glyph(ord("H")), bp)
    return CAP / (bp.bounds[3] / face.upem)

def wort():
    """Glyphen von «Das Goetheanum»: Liste (x, Pfad), linke Tinte des ‹D›, Skalierung, rechte Tinte."""
    global FS
    FS = FS or schriftgrad()
    face, font = _font(); upm = face.upem
    buf = hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties(); hb.shape(font, buf, {"kern": True, "liga": True})
    s = FS / upm; x = 0.0; teile = []; dx0 = None; rechts = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(None, ntos=lambda v: "%g" % round(v, 2)); font.draw_glyph_with_pen(info.codepoint, pen)
        bp = BoundsPen(None); font.draw_glyph_with_pen(info.codepoint, bp)
        if dx0 is None: dx0 = bp.bounds[0] * s
        if pen.getCommands():
            teile.append((x + pos.x_offset * s, pen.getCommands())); rechts = x + bp.bounds[2] * s
        f = WORT_ABSTAND if TEXT[info.cluster] == " " else 1.0
        x += pos.x_advance * s * f + TRACK * FS
    return teile, dx0, s, rechts

def _text(ox, base, farbe):
    teile, dx0, s, rechts = wort()
    g = "".join('<path transform="translate(%.2f,%.2f) scale(%.5f,%.5f)" d="%s"/>' % (ox - dx0 + x, base, s, -s, d) for x, d in teile)
    return g, ox - dx0 + rechts

def svg_weblogo(farbe):
    g, w = _text(D_INK_X, BASE_Y, farbe)
    m = "".join('<path d="%s"/>' % p for p in MARK)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f"><g fill="%s">'
            '<g transform="scale(%.5f)">%s</g>%s</g></svg>') % (w, H, farbe, MARK_SCALE, m, g)

def svg_kreis(farbe, weiss=False):
    import re
    d = re.search(r'<path[^>]*\sd="([^"]+)"', open(KREIS_SVG, encoding="utf-8").read()).group(1)
    k = KREIS_D / 28.3466
    base = KREIS_D / 2 + CAP / 2 - 0.07 * CAP         # Kreismitte 0,07 Versalhöhen unter der Mitte der Versalhöhe (wie Vorlage)
    g, w = _text(KREIS_D + KREIS_GAP, base, farbe)
    grund = "" if weiss else '<circle cx="14.2058" cy="14.1895" r="14.1733" fill="#ffffff"/>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f"><g transform="scale(%.5f)">%s'
            '<path d="%s" fill="%s"/></g><g fill="%s">%s</g></svg>') % (w, KREIS_D, k, grund, d, farbe, farbe, g)

VARIANTEN = {"farbe": "#373949", "schwarz": "#000000", "weiss": "#ffffff"}

def main():
    import cairosvg
    from PIL import Image
    formen = {"weblogo": lambda f, n: svg_weblogo(f), "point-einzeilig": lambda f, n: svg_kreis(f, n == "weiss")}
    for form, bau in formen.items():
        for name, farbe in VARIANTEN.items():
            d = os.path.join(OUT, form, name); os.makedirs(d, exist_ok=True)
            s = bau(farbe, name)
            open(os.path.join(d, "web.svg"), "w", encoding="utf-8").write(s)
            png = cairosvg.svg2png(bytestring=s.encode(), output_width=2592)
            open(os.path.join(d, "web.png"), "wb").write(png)
            if name != "weiss":
                im = Image.open(io.BytesIO(png)).convert("RGBA"); bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[3])
                bg.save(os.path.join(d, "web.jpg"), quality=92)

if __name__ == "__main__":
    main()
