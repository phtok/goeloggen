#!/usr/bin/env python3
# Proof from the BUILT test font: HarfBuzz shapes each run with real features.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
import cairosvg

PATH = "../../assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.4.1-Klar.otf"
data = open(PATH, "rb").read()
face = hb.Face(data); HBF = hb.Font(face)
ft = TTFont(PATH); gs = ft.getGlyphSet(); order = ft.getGlyphOrder()
INK = "#23272b"; MUT = "#9aa0a6"; SCALE = 0.5

def gpath_at(gn, x, y, s=1.0):
    rp = RecordingPen()
    gs[gn].draw(rp)
    d = []
    for c, p in rp.value:
        q = [(px*s + x, py*s + y) for px, py in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

def run(text, feats, x):
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(HBF, buf, feats)
    paths = []; px = x
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gn = order[info.codepoint]
        paths.append(gpath_at(gn, px + pos.x_offset, pos.y_offset))
        px += pos.x_advance
    return "".join(paths), px

def line(segments, x0, base):
    inner = []; x = x0
    for text, feats in segments:
        d, x = run(text, feats, x); inner.append('<path d="%s"/>' % d)
    return '<g transform="translate(0,%d) scale(1,-1)" fill="%s">%s</g>' % (base, INK, "".join(inner)), x

def esc(s): return s.replace("&", "&amp;")
def txt(x, y, s, size=30, fill=MUT): return '<text x="%d" y="%d" font-family="Helvetica,Arial" font-size="%d" fill="%s">%s</text>' % (x, y, size, fill, esc(s))
SC = {"smcp": True}; ON = {"onum": True}; SCON = {"smcp": True, "onum": True}
X0 = 560
rows = [
    ("Mischsatz", [("Mitglied ", {}), ("be3477", SCON), (" trat ", {}), ("1923", ON),
                    (" bei; vgl. ", {}), ("bd", SC), (". II — ", {}), ("unesco", SC),
                    (", ", {}), ("din", SC), (" ", {}), ("476", ON), (".", {})]),
    ("Kapitälchen a–z & ä ö ü", [("abcdefghijklmnopqrstuvwxyz äöü &", SC)]),
    ("Ziffern Grund / Kurz", [("0123456789", {}), ("   ", {}), ("0123456789", ON)]),
]
built = []; maxx = 0
for i, (label, segs) in enumerate(rows):
    base = 520 + i * 760
    g, ex = line(segs, X0, base)
    built.append((label, g, base)); maxx = max(maxx, ex)
W = maxx + 120; H = 520 + len(rows) * 760 - 360
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*SCALE), int(H*SCALE), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H)]
for label, g, base in built:
    svg.append(txt(60, base - 30, label, 30))
    svg.append(g)
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/v241_built.png", output_width=1800)
print("wrote /tmp/v241_built.png  W=%d H=%d" % (W, H))
