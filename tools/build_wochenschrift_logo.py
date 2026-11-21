#!/usr/bin/env python3
"""Wochenschrift-Logo (neu): Bildmarke + «Das Goetheanum» in der Hausschrift.

Mass nach der Wochenschrift-Website (wochenschrift.xdev.ai, .brand-mark):
Höhe H, Wort in Goetheanum Schrift Variable wght 595, Versalhöhe 0,7396 H,
Laufweite −0,0079 em, Grundlinie bei 0,9115 H (gemessen), Wortabstand so, dass
die Tinte des ‹D› bei 1,1302 H beginnt (Bildmarke 0,745 H breit).
Erzeugt SVG (Farbe, Schwarz, Weiss) und PNG/JPG unter
assets/logos/medien/wochenschrift/weblogo/. Aufruf: python3 tools/build_wochenschrift_logo.py
Braucht fontTools, uharfbuzz, cairosvg, Pillow. Idempotent.
"""
import os, io
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets/logos/medien/wochenschrift/weblogo")
FONT = os.path.join(ROOT, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf")
TEXT = "Das Goetheanum"
H = 960.0                     # Logohöhe in Einheiten (24 px × 40)
K = H / 24.0                  # Einheiten je Website-Pixel bei H = 24
CAP = 0.7396 * H              # Versalhöhe der Website (17,75 von 24 px)
FS = None                     # Schriftgrad: aus der Versalhöhe der Hausschrift abgeleitet
TRACK = -0.0079               # Laufweite in em
WGHT = 595
WORT_ABSTAND = 1.0            # Faktor auf die Breite des Leerzeichens (1 = wie Website)
BASE_Y = 0.9115 * H           # Grundlinie von oben
D_INK_X = 27.125 * K          # Tinte-Beginn des ‹D›
MARK_W = 17.88 * K

MARK = [  # Bildmarke, Koordinaten 15,8254 × 21,07
 "M5.7224,3.472L15.8254,0v21.07h-6.002l.007-7.74c.003-.501-.086-.969-.242-1.438-.475-1.43-3.866-8.42-3.866-8.42",
 "M5.292,7.1965s3.062,4.895,3.062,6.039l.048,7.834h-3.538l-.022-2.693c-.035-1.633-3.74-6.24-3.74-6.24l4.19-4.94Z",
 "M0,17.9464l2.355-1.673s1.103,1.842,1.201,2.488c.099.646.02,2.309.02,2.309H1.072s.005-.607.008-.876c.007-.476-.144-.883-.375-1.274-.108-.183-.609-.818-.705-.974",
]
MARK_SCALE = H / 21.07

def schriftgrad():
    face = hb.Face(open(FONT, "rb").read()); font = hb.Font(face); font.set_variations({"wght": WGHT})
    bp = BoundsPen(None); font.draw_glyph_with_pen(font.get_nominal_glyph(ord("H")), bp)
    return CAP / (bp.bounds[3] / face.upem)

def wort():
    global FS
    FS = FS or schriftgrad()
    face = hb.Face(open(FONT, "rb").read()); font = hb.Font(face)
    font.set_variations({"wght": WGHT}); upm = face.upem
    buf = hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties(); hb.shape(font, buf, {"kern": True, "liga": True})
    s = FS / upm; x = 0.0; teile = []; dx0 = None
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(None, ntos=lambda v: "%g" % round(v, 2))
        # Pfad in Schrifteinheiten, Transform setzt Grad und Lage
        font.draw_glyph_with_pen(info.codepoint, pen)
        d = pen.getCommands()
        if dx0 is None:
            bp = BoundsPen(None); font.draw_glyph_with_pen(info.codepoint, bp); dx0 = bp.bounds[0] * s
        if d:
            teile.append((x + pos.x_offset * s, d))
        f = WORT_ABSTAND if info.cluster is not None and TEXT[info.cluster] == " " else 1.0
        x += pos.x_advance * s * f + TRACK * FS
    return teile, dx0, s

def svg(farbe):
    teile, dx0, s = wort()
    ox = D_INK_X - dx0
    breite = ox + sum(0 for _ in teile)  # Platzhalter, Endbreite unten
    g = "".join('<path transform="translate(%.2f,%.2f) scale(%.5f,%.5f)" d="%s"/>' % (ox + x, BASE_Y, s, -s, d) for x, d in teile)
    # rechte Kante: Position des letzten Glyphen plus dessen Breite wird aus Bounds geholt
    face = hb.Face(open(FONT, "rb").read()); font = hb.Font(face); font.set_variations({"wght": WGHT})
    last_x, last_d = teile[-1]
    buf = hb.Buffer(); buf.add_str(TEXT[-1]); buf.guess_segment_properties(); hb.shape(font, buf)
    bp = BoundsPen(None); font.draw_glyph_with_pen(buf.glyph_infos[0].codepoint, bp)
    w = ox + last_x + bp.bounds[2] * s
    m = "".join('<path d="%s"/>' % p for p in MARK)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.1f %.1f"><g fill="%s">'
            '<g transform="scale(%.5f)">%s</g>%s</g></svg>') % (w, H, farbe, MARK_SCALE, m, g)

VARIANTEN = {"farbe": "#373949", "schwarz": "#000000", "weiss": "#ffffff"}

def main():
    import cairosvg
    from PIL import Image
    for name, farbe in VARIANTEN.items():
        d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
        s = svg(farbe)
        open(os.path.join(d, "web.svg"), "w", encoding="utf-8").write(s)
        png = cairosvg.svg2png(bytestring=s.encode(), output_width=2592)
        open(os.path.join(d, "web.png"), "wb").write(png)
        if name != "weiss":
            im = Image.open(io.BytesIO(png)).convert("RGBA"); bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[3])
            bg.save(os.path.join(d, "web.jpg"), quality=92)

if __name__ == "__main__":
    main()
