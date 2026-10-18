#!/usr/bin/env python3
# Reference images for werkzeug.html:
#  1) sup/sub Schaubild  — metric lines + figures at type-design reference
#     positions (after Titillium: superior h~315 bottom~478; inferior bottom~-100).
#  2) Ligature drafts    — fi/fl/ffi/ffl as f + dotless-i / l vs unligated.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontfix import grec, blend, sig
from fontTools.ttLib import TTFont
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
fL = TTFont(glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0])
W_KLAR, W_LAUT = 440.0, 680.0
INK = "#23272b"; GOLD = "#a07a33"; MUT = "#9aa0a6"; GUIDE = "#d8d2c4"; SCALE = 0.5

def interp(uni, w):
    rA, aA = grec(fK, uni); rB, aB = grec(fL, uni)
    if rA is None: return None, 0
    if rB is None or sig(rA) != sig(rB): return rA, aA
    return blend(rA, aA, rB, aB, (w - W_KLAR) / (W_LAUT - W_KLAR))

def gpath(rec, s, dx, dy):
    d = []
    for c, p in rec:
        q = [(x * s + dx, y * s + dy) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

def cluster(seq, x0, base, s=1.0, w=None, dy=0):
    """seq: list of (unicode, overlap). Draw at baseline `base` (svg-y), font-up flipped."""
    inner = []; px = 0.0
    for uni, ovl in seq:
        rec, adv = (interp(uni, w) if w else grec(fK, uni))
        if rec is None: continue
        px -= ovl * s
        inner.append('<path d="%s"/>' % gpath(rec, s, px, dy))
        px += adv * s
    g = '<g transform="translate(%.0f,%.0f) scale(1,-1)" fill="%s">%s</g>' % (x0, base, INK, "".join(inner))
    return g, x0 + px

def txt(x, y, s, fill, size=30, anchor="start"):
    return '<text x="%.0f" y="%.0f" font-family="Helvetica,Arial,sans-serif" font-size="%d" fill="%s" text-anchor="%s">%s</text>' % (x, y, size, fill, anchor, s)

def frame(w, h):
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (w*SCALE, h*SCALE, w, h),
            '<rect width="%d" height="%d" fill="#fff"/>' % (w, h)]

# ============ IMAGE 1 — sup/sub Schaubild ============
W, H, yB, PADL = 3100, 1240, 900, 360
def Y(fy): return yB - fy
s = frame(W, H)
s.append(txt(PADL-30, 50, "Schaubild Hoch-/Tiefstellung — Referenzproportionen nach Titillium (OFL)", INK, 38))
for fy, lbl in [(-210,"Unterlänge"),(0,"Grundlinie"),(500,"x-Höhe 500"),(690,"Versalhöhe 690"),(790,"Oberlänge ~790")]:
    s.append('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2"/>' % (PADL-30, Y(fy), W-60, Y(fy), GUIDE))
    s.append(txt(PADL-50, Y(fy)+10, lbl, MUT, 28, "end"))
# recommended bands
s.append('<rect x="%d" y="%.0f" width="%d" height="312" fill="%s" opacity="0.12"/>' % (PADL, Y(790), W-60-PADL, GOLD))   # superior 478..790
s.append('<rect x="%d" y="%.0f" width="%d" height="312" fill="%s" opacity="0.12"/>' % (PADL, Y(212), W-60-PADL, GOLD))   # inferior -100..212
SUPS = 315/671.0
x = PADL + 20
g, x = cluster([(0x31,0),(0x32,0)], x, Y(0), 1.0, None, 0);   s.append(g); x += 180   # baseline 12
g, x = cluster([(0x31,0),(0x32,0)], x, Y(0), SUPS, 600, 478); s.append(g); x += 180   # superior 12
g, x = cluster([(0x31,0),(0x32,0)], x, Y(0), SUPS, 600, -100);s.append(g)             # inferior 12
s.append(txt(PADL+20, Y(-300), "Grundziffern (voll)", MUT, 28))
s.append(txt(PADL+20+1480, Y(-300), "Hochgestellt · H≈315 · oben ~790 · schwerer", MUT, 28))
s.append(txt(PADL+20+2300, Y(-300), "Tiefgestellt · H≈315 · unten ~-100", MUT, 28))
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/feat_supsub.png", output_width=int(W*SCALE))

# ============ IMAGE 2 — ligature drafts ============
W2, H2, LS = 2700, 1280, 0.55
s = frame(W2, H2)
s.append(txt(60, 56, "Ligatur-Entwurf — f + dotless-i / l (Überhang tuckt unter den f-Bogen)", INK, 38))
yo, ye = 470, 1090           # baselines (svg-y) for the two rows
s.append('<line x1="520" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2"/>' % (yo, W2-60, yo, GUIDE))
s.append('<line x1="520" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2"/>' % (ye, W2-60, ye, GUIDE))
s.append(txt(60, yo-8, "ohne (Kollision):", MUT, 28))
s.append(txt(60, ye-8, "Entwurf (Ligatur):", MUT, 28))
OVL = 95
unl = [[(0x66,0),(0x69,0)], [(0x66,0),(0x6C,0)], [(0x66,0),(0x66,0),(0x69,0)], [(0x66,0),(0x66,0),(0x6C,0)]]
lig = [[(0x66,0),(0x131,OVL)], [(0x66,0),(0x6C,OVL)], [(0x66,0),(0x66,OVL),(0x131,OVL)], [(0x66,0),(0x66,OVL),(0x6C,OVL)]]
x = 560
for u, l in zip(unl, lig):
    gu, _ = cluster(u, x, yo, LS); s.append(gu)
    gl, xe = cluster(l, x, ye, LS); s.append(gl)
    x = xe + 150
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/feat_ligatures.png", output_width=int(W2*SCALE))
print("wrote /tmp/feat_supsub.png and /tmp/feat_ligatures.png")
