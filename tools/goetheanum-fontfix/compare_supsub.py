#!/usr/bin/env python3
# Context comparison: existing (inherited) vs 700-calibrated super/subscript, in running text.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontfix import grec, blend, sig
from fontTools.ttLib import TTFont
import cairosvg

fK = TTFont("../../assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.4.1-Klar.otf")
fL = TTFont(glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0])
INK = "#23272b"; MUT = "#9aa0a6"; SCALE = 0.5
SUP_CP = {0:0x2070,1:0x00B9,2:0x00B2,3:0x00B3,4:0x2074,5:0x2075,6:0x2076,7:0x2077,8:0x2078,9:0x2079}
SUB_CP = {d:0x2080+d for d in range(10)}
S_CAL = 320/690.0

def interp(u, w):
    rA, aA = grec(fK, u); rB, aB = grec(fL, u)
    if rA is None or rB is None or sig(rA) != sig(rB): return rA, aA
    return blend(rA, aA, rB, aB, (w - 440) / (680 - 440))

def pathstr(rec, scale, gx, base, dyf=0.0):
    d = []
    for c, p in rec:
        q = [(gx + scale*x, base - scale*(y + dyf)) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

def line(segs, gx, base):
    out = []
    for text, kind in segs:
        for ch in text:
            if ch == " ":
                out.append(("", 0)); gx += grec(fK, 0x20)[1]; continue
            if kind == "n":
                rec, adv = grec(fK, ord(ch)); out.append((pathstr(rec, 1, gx, base), 0)); gx += adv
            elif kind in ("se", "be"):
                cp = (SUP_CP if kind == "se" else SUB_CP)[int(ch)]
                rec, adv = grec(fK, cp); out.append((pathstr(rec, 1, gx, base), 0)); gx += adv
            else:                                      # sc / bc : 700-calibrated
                off = 460 if kind == "sc" else -110
                rec, adv = interp(0x30 + int(ch), 700)
                out.append((pathstr(rec, S_CAL, gx, base, off / S_CAL), 0)); gx += adv*S_CAL
    return "".join('<path d="%s" fill="%s"/>' % (d, INK) for d, _ in out if d), gx

def txt(x, y, s, sz=30, f=MUT):
    return '<text x="%d" y="%d" font-family="Helvetica,Arial" font-size="%d" fill="%s">%s</text>' % (x, y, sz, f, s)

rows = [
    ("Hochgestellt — VORHANDEN (geerbt)", [("Goethe", "n"), ("1", "se"), (" x", "n"), ("2", "se"), (" m", "n"), ("3", "se")]),
    ("Hochgestellt — KALIBRIERUNG 700", [("Goethe", "n"), ("1", "sc"), (" x", "n"), ("2", "sc"), (" m", "n"), ("3", "sc")]),
    ("Tiefgestellt — VORHANDEN (geerbt)", [("H", "n"), ("2", "be"), ("O  CO", "n"), ("2", "be")]),
    ("Tiefgestellt — KALIBRIERUNG 700", [("H", "n"), ("2", "bc"), ("O  CO", "n"), ("2", "bc")]),
]
def txt(x, y, s, sz=200, f=MUT):
    return '<text x="%d" y="%d" font-family="Helvetica,Arial" font-size="%d" fill="%s">%s</text>' % (x, y, sz, f, s)
PXU, X0, ROWH = 0.12, 60, 1320
ends = [line(segs, X0, 0)[1] for _, segs in rows]
W = int(max(ends)) + 120; H = 320 + len(rows)*ROWH
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
     '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
     txt(60, 230, "Hoch-/Tiefstellung im Satz: vorhanden vs. Kalibrierung 700", 250, INK)]
for i, (label, segs) in enumerate(rows):
    base = 360 + i*ROWH + 820
    s.append(txt(60, base - 830, label, 190))
    g, _ = line(segs, X0, base); s.append(g)
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/cmp_supsub.png", output_width=int(W*PXU))
print("wrote /tmp/cmp_supsub.png  W=%d -> %dpx" % (W, int(W*PXU)))
