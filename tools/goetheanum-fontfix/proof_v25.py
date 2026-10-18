#!/usr/bin/env python3
# Reference sheets (coords mapped to SVG in Python; no transforms):
#  A) Ligatur A (verfeinert): f-Bogen verlängert + ff-Querbalken-Verschränkung.
#  B) v2.5 Glyphenuebersicht: verbesserte konstruierte Entwuerfe.
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
    return [(c, tuple((x*s + dx, y*s + dy) for x, y in p)) for c, p in rec]

def shear(rec, k, y0):
    return [(c, tuple((x + k*(y - y0), y) for x, y in p)) for c, p in rec]

def ext_f(rec, bow=88):
    """Lengthen the f's top bow by pushing the upper-right arch points right."""
    return [(c, tuple((x + bow if (x > 175 and y > 640) else x, y) for x, y in p)) for c, p in rec]

def emit(contours, scale, gx, base):
    d = []
    for kind, data in contours:
        if kind == "p":
            q = [(gx + scale*x, base - scale*y) for x, y in data]
            d.append("M" + " L".join("%.1f %.1f" % t for t in q) + "Z")
        else:
            for c, p in data:
                q = [(gx + scale*x, base - scale*y) for x, y in p]
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

def path(d, fill=INK): return '<path d="%s" fill="%s"/>' % (d, fill)

f, af = grec(fK, 0x66); gi, ai = grec(fK, 0x131); gl, al = grec(fK, 0x6C)
gI, aI = grec(fK, 0x69)
CB0, CB1 = 500, 540
BOW, OVL = 88, 90

def lig(word, ligate):
    cont = []; px = 0.0; fcount = 0; prev_f = False
    bridges = []
    seq = list(word)
    for idx, ch in enumerate(seq):
        if ch == "f":
            rec = ext_f(f, BOW) if ligate else f
            cont.append(("g", recmap(rec, 1, px, 0)))
            if ligate and prev_f:                      # crossbar bridge between two f's
                bridges.append(("p", [(px-af+250, CB0), (px+150, CB0), (px+150, CB1), (px-af+250, CB1)]))
            px += af; prev_f = True
        else:
            rec = gi if (ch == "i" and ligate) else (grec(fK, ord(ch))[0])
            adv = ai if (ch == "i" and ligate) else grec(fK, ord(ch))[1]
            if ligate and prev_f and ch in "il": px -= OVL
            cont.append(("g", recmap(rec, 1, px, 0))); px += adv; prev_f = False
    return cont + bridges, px

# ===================== IMAGE A =====================
WA, rowh = 2400, 540
HA = 120 + 2 * rowh
s = frame(WA, HA)
s.append(txt(60, 64, "Ligatur A — verfeinert: f-Bogen länger + ff-Querbalken verschränkt", 38, INK))
for i, (label, lg) in enumerate([("ohne Ligatur (Referenz)", False), ("Entwurf A verfeinert", True)]):
    base = 200 + i*rowh + 250
    s.append(txt(60, base - 280, label, 28))
    s.append('<line x1="60" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="2"/>' % (base, WA-60, base, GUIDE))
    gx = 640
    for w in ("fi", "fl", "ffi", "ffl"):
        cont, width = lig(w, lg); s.append(path(emit(cont, 0.5, gx, base))); gx += width*0.5 + 150
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/v25_ligvariants.png", output_width=int(WA*SCALE))

# ===================== IMAGE B =====================
HYW = 73
def c_prime(x0=0):                                     # erster Wurf: schlanker Keil
    return [("p", [(x0, 430), (x0+85, 430), (x0+155, 690), (x0+70, 690)])]
def c_doubleprime():
    return c_prime(0) + c_prime(170)
def c_slashzero():
    rec, adv = grec(fK, 0x30)                          # erster Wurf: Schrägstrich im Innern, ohne Eckchen
    return [("g", rec), ("p", [(150, 55), (245, 55), (430, 600), (335, 600)])], adv
def c_figuredash(): return [("p", [(70, 300), (490, 300), (490, 300+HYW), (70, 300+HYW)])], 560
def c_numero():
    n, adv = grec(fK, 0x4E); o, _ = grec(fK, 0x6F)
    ow = 0.40
    cont = [("g", n), ("g", recmap(o, ow, 585, 420)),
            ("p", [(585, 392), (585+ow*486, 392), (585+ow*486, 392+52), (585, 392+52)])]
    return cont, 585 + ow*486 + 10
def c_lira():
    rec, adv = grec(fK, 0x4C)                          # L + zwei Querbalken = ₤
    bars = [("p", [(40, 250), (410, 250), (410, 322), (40, 322)]),
            ("p", [(40, 400), (410, 400), (410, 472), (40, 472)])]
    return [("g", rec)] + bars, 430
def c_fig(off, weight=700, h=320):
    s2 = h/690.0; r1, a1 = interp(ord("1"), weight); r2, a2 = interp(ord("2"), weight)
    return [("g", recmap(r1, s2, 0, off)), ("g", recmap(r2, s2, a1*s2+20, off))], (a1+a2)*s2+20

def cells():
    out = []
    out.append(("Prime  ′", c_prime(), 200, "Entwurf"))
    out.append(("Doppelprime  ″", c_doubleprime(), 350, "Entwurf"))
    c, w = c_slashzero();  out.append(("schlummernde 0", c, w, "Entwurf"))
    c, w = c_figuredash(); out.append(("Figure-Dash  ‒", c, w, "Entwurf"))
    c, w = c_numero();     out.append(("Numero  №", c, w, "Entwurf"))
    c, w = c_lira();       out.append(("Lira  ₤", c, w, "Entwurf"))
    c, w = c_fig(460);     out.append(("Hochstellung 320/700", c, w, "kalibriert"))
    c, w = c_fig(-110);    out.append(("Tiefstellung 320/700", c, w, "kalibriert"))
    return out

cl = cells(); COLS = 4; CW, CH = 720, 760
WB = COLS*CW + 80; ROWSn = (len(cl) + COLS - 1)//COLS; HB = 150 + ROWSn*CH
s = frame(WB, HB)
s.append(txt(50, 64, "Glyphen-Übersicht v2.5 — verbesserte Entwürfe", 38, INK))
for idx, (label, cont, w, status) in enumerate(cl):
    r, c = divmod(idx, COLS); cx = 40 + c*CW; cy = 150 + r*CH; base = cy + 470
    s.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>' % (cx, cy, CW-30, CH-40, GUIDE))
    s.append('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="1.5"/>' % (cx+40, base, cx+CW-70, base, GUIDE))
    sc = min(0.6, (CW-180)/max(w, 1)); gx = cx + (CW-30 - w*sc)/2
    s.append(path(emit(cont, sc, gx, base)))
    s.append(txt(cx + (CW-30)/2, cy + CH - 80, label, 30, INK, "middle"))
    s.append(txt(cx + (CW-30)/2, cy + CH - 48, status, 24, GOLD if status != "kalibriert" else GREEN, "middle"))
s.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s).encode(), write_to="/tmp/v25_overview.png", output_width=int(WB*SCALE))

# ===================== editierbare SVG-Vektoren =====================
ENTW = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "entwuerfe"))
os.makedirs(ENTW, exist_ok=True)

def export_svg(name, contours, width):
    BASE, LM, Hc = 820, 70, 1120
    W = int(width) + 140
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hc, W, Hc),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hc),
           '<g id="metriken" stroke="#cfcabe" stroke-width="1" fill="none">']
    for fy in (0, 500, 690, -220):
        sy = BASE - fy; out.append('<line x1="0" y1="%.0f" x2="%d" y2="%.0f"/>' % (sy, W, sy))
    out.append('</g><g id="%s" fill="#111">' % name)
    for kind, data in contours:
        if kind == "p":
            q = [(LM + x, BASE - y) for x, y in data]
            out.append('<path d="%s"/>' % ("M" + " L".join("%.1f %.1f" % t for t in q) + "Z"))
        else:
            d = []
            for c, p in data:
                q = [(LM + x, BASE - y) for x, y in p]
                if c == "moveTo": d.append("M%.1f %.1f" % q[0])
                elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
                elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
                elif c == "qCurveTo":
                    for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
                elif c == "closePath": d.append("Z")
            out.append('<path d="%s"/>' % "".join(d))
    out.append('</g></svg>')
    open(os.path.join(ENTW, name + ".svg"), "w").write("\n".join(out))

for nm in ("fi", "fl", "ffi", "ffl"):
    cont, w = lig(nm, True); export_svg(nm, cont, w)
cn, wn = c_numero(); export_svg("numero", cn, wn)
cli, wl = c_lira(); export_svg("lira", cli, wl)
print("wrote PNGs + editable SVGs ->", ENTW)
