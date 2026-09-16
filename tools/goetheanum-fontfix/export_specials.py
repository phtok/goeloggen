#!/usr/bin/env python3
# Export the v2.5 special glyphs as editable SVG (separate contours + metric lines):
#   Prime ′, Doppelprime ″, schlummernde 0, Figure-Dash, Numero №, Lira ₤.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
ENTW = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "entwuerfe"))
os.makedirs(ENTW, exist_ok=True)
HYW = 73

def recmap(rec, s, dx, dy):
    return [(c, tuple((x*s + dx, y*s + dy) for x, y in p)) for c, p in rec]

def c_prime(x0=0):
    return [("p", [(x0, 430), (x0+85, 430), (x0+155, 690), (x0+70, 690)])], 170
def c_doubleprime():
    return c_prime(0)[0] + c_prime(170)[0], 340
def c_slashzero():
    rec, adv = grec(fK, 0x30)
    return [("g", rec), ("p", [(150, 55), (245, 55), (430, 600), (335, 600)])], adv
def c_figuredash():
    return [("p", [(70, 300), (490, 300), (490, 300+HYW), (70, 300+HYW)])], 560
def c_numero():
    n, adv = grec(fK, 0x4E); o, _ = grec(fK, 0x6F); ow = 0.40
    return [("g", n), ("g", recmap(o, ow, 585, 420)),
            ("p", [(585, 392), (585+ow*486, 392), (585+ow*486, 444), (585, 444)])], 585 + ow*486 + 10
def c_lira():
    rec, adv = grec(fK, 0x4C)
    return [("g", rec), ("p", [(40, 250), (410, 250), (410, 322), (40, 322)]),
            ("p", [(40, 400), (410, 400), (410, 472), (40, 472)])], 430

def export(name, contours, width):
    BASE, LM, Hc = 820, 70, 1120
    W = int(width) + 140
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hc, W, Hc),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hc),
           '<g id="metriken" stroke="#cfcabe" stroke-width="1" fill="none">']
    for fy in (0, 500, 690, -220):
        out.append('<line x1="0" y1="%.0f" x2="%d" y2="%.0f"/>' % (BASE - fy, W, BASE - fy))
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

SPEC = [("prime", c_prime()), ("doppelprime", c_doubleprime()), ("schlummernde-0", c_slashzero()),
        ("figure-dash", c_figuredash()), ("numero", c_numero()), ("lira", c_lira())]
for name, (cont, w) in SPEC:
    export(name, cont, w)
print("exported specials ->", ENTW, [n for n, _ in SPEC])
