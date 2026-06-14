#!/usr/bin/env python3
# Two reference sheets (coordinates mapped to SVG space in Python; no transforms):
#  A) Ligatur-Varianten   B) v2.5 Glyphenuebersicht (konstruierte Entwuerfe)
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontfix import grec, blend, sig
from fontTools.ttLib import TTFont
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
fL = TTFont(glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0])
WK, WL = 440.0, 680.0
INK = "#23272b"; MUT = "#9aa0a6"; GOLD = "#a07a33"; GREEN = "#3a7a3a"; GUIDE = "#e2ddd0"; SCALE = 0.5

def interp(uni, w):
    rA, aA = grec(fK, uni); rB, aB = grec(fL, uni)
    if rA is None: return None, 0
    if rB is None or sig(rA) != sig(rB): return rA, aA
    return blend(rA, aA, rB, aB, (w - WK) / (WL - WK))

def recmap(rec, s, dx, dy):
    return [(c, tuple((x * s + dx, y * s + dy) for x, y in p)) for c, p in rec]

def emit(contours, scale, gx, base):
    """contours: list of ('g', rec) or ('p', [pts]); map font coords -> svg (y flipped)."""
    d = []
    for kind, data in contours:
        if kind == "p":
            q = [(gx + scale * x, base - scale * y) for x, y in data]
            d.append("M" + " L".join("%.1f %.1f" % t for t in q) + "Z")
        else:
            for c, p in data:
                q = [(gx + scale * x, base - scale * y) for x, y in p]
                if c == "moveTo": d.append("M%.1f %.1f" % q[0])
                elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
                elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
                elif c == "qCurveTo":
                    for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
                elif c == "closePath": d.append("Z")
    return "".join(d)

def txt(x, y, s, size=30, fill=MUT, anchor="start"):
    return '<text x="%.0f" y="%.0f" font-family="Helvetica,Arial" font-size="%d" fill="%s" text-anchor="%s">%s</text>' % (x, y, size, fill, anchor, s.replace("&", "&amp;"))

def frame(w, h):
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(w*SCALE), int(h*SCALE), w, h),
            '<rect width="%d" height="%d" fill="#fff"/>' % (w, h)]

def path(d, fill=INK):
    return '<path d="%s" fill="%s"/>' % (d, fill)

# ===================== IMAGE A: ligature variants =====================
def lig_contours(letters, ovl, dotless):
    cont = []; px = 0.0; prev_f = False
    for ch in letters:
        uni = 0x131 if (ch == "i" and dotless) else ord(ch)
        rec, adv = grec(fK, uni)
        if prev_f and ch in "il" and ovl: px -= ovl
        cont.append(("g", recmap(rec, 1.0, px, 0)))
        px += adv; prev_f = (ch == "f")
    return cont, px

VARIANTS = [
    ("ohne Ligatur — f + i mit Punkt, Normalabstand", None, False),
    ("Entwurf A — dotless-i, Überhang klein (95)", 95, True),
    ("Entwurf B — dotless-i, Überhang gross (170)", 170, True),
    ("Entwurf C — dotless-i, nur Punkt getilgt (35)", 35, True),
]
WA, rowh, sclA = 2700, 500, 0.5
HA = 120 + len(VARIANTS) * rowh
s = frame(WA, HA)
s.append(txt(60, 64, "Ligatur-Varianten — wähle eine Richtung (fi · fl · ffi · ffl)", 38, INK))
for i, (label, ovl, dl) in enumerate(VARIANTS):
    base = 200 + i * rowh + 250
    s.append(txt(60, base - 270, label, 28))
    s.append('<line x1="60" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2"/>' % (base, WA-60, base, GUIDE))
    gx = 640
    for w in ("fi", "fl", "ffi", "ffl"):
        cont, width = lig_contours(w, ovl, dl)
        s.append(path(emit(cont, sclA, gx, base)))
        gx += width * sclA + 150
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/v25_ligvariants.png", output_width=int(WA*SCALE))

# ===================== IMAGE B: v2.5 glyph overview =====================
HYW = 73
def c_prime(x0=0): return [("p", [(x0,430),(x0+85,430),(x0+155,690),(x0+70,690)])]
def c_doubleprime(): return c_prime(0) + c_prime(170)
def c_slashzero():
    rec, adv = grec(fK, 0x30)
    return [("g", rec), ("p", [(150,55),(245,55),(430,600),(335,600)])], adv
def c_figuredash(): return [("p", [(90,300),(470,300),(470,300+HYW),(90,300+HYW)])], 560
def c_numero():
    n, adv = grec(fK, 0x4E); o, _ = grec(fK, 0x6F)
    cont = [("g", n), ("g", recmap(o, 0.46, 575, 360)),
            ("p", [(575,330),(575+0.46*486,330),(575+0.46*486,330+58),(575,330+58)])]
    return cont, 575 + 0.46*486 + 20
def c_lira():
    rec, adv = grec(fK, 0xA3)
    return [("g", rec), ("p", [(120,250),(470,250),(470,250+HYW),(120,250+HYW)])], adv
def c_fig(off, weight=700, h=320):
    s2 = h/690.0; r1, a1 = interp(ord("1"), weight); r2, a2 = interp(ord("2"), weight)
    return [("g", recmap(r1, s2, 0, off)), ("g", recmap(r2, s2, a1*s2+20, off))], (a1+a2)*s2+20

def cells():
    out = []
    out.append(("Prime  ′", c_prime(), 155, "Entwurf"))
    out.append(("Doppelprime  ″", c_doubleprime(), 325, "Entwurf"))
    c, w = c_slashzero();  out.append(("schlummernde 0", c, w, "Entwurf"))
    c, w = c_figuredash(); out.append(("Figure-Dash  ‒", c, w, "Entwurf"))
    c, w = c_numero();     out.append(("Numero  №", c, w, "Entwurf"))
    c, w = c_lira();       out.append(("Lira  ₤", c, w, "Entwurf"))
    c, w = c_fig(460);     out.append(("Hochstellung 320/700", c, w, "kalibriert"))
    c, w = c_fig(-110);    out.append(("Tiefstellung 320/700", c, w, "kalibriert"))
    return out

cl = cells(); COLS = 4; CW, CH = 720, 760
WB = COLS * CW + 80; ROWSn = (len(cl) + COLS - 1) // COLS; HB = 150 + ROWSn * CH
s = frame(WB, HB)
s.append(txt(50, 64, "Glyphen-Übersicht v2.5 — Entwürfe der ausstehenden Zeichen", 38, INK))
for idx, (label, cont, w, status) in enumerate(cl):
    r, c = divmod(idx, COLS); cx = 40 + c*CW; cy = 150 + r*CH; base = cy + 470
    s.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>' % (cx, cy, CW-30, CH-40, GUIDE))
    s.append('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="1.5"/>' % (cx+40, base, cx+CW-70, base, GUIDE))
    sc = min(0.6, (CW-180) / max(w, 1)); gx = cx + (CW-30 - w*sc) / 2
    s.append(path(emit(cont, sc, gx, base)))
    s.append(txt(cx + (CW-30)/2, cy + CH - 80, label, 30, INK, "middle"))
    s.append(txt(cx + (CW-30)/2, cy + CH - 48, status, 24, GOLD if status != "kalibriert" else GREEN, "middle"))
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/v25_overview.png", output_width=int(WB*SCALE))
print("wrote /tmp/v25_ligvariants.png and /tmp/v25_overview.png")
