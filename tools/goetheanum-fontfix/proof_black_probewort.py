#!/usr/bin/env python3
# Etappe E5 (31. 10. 2026): ein Probewort über Laut (680) hinaus, kein Schnitt.
# Die Variable v2.8 ist bei den gesunden Glyphen linear zwischen den
# Endmastern 190 und 725 (AUDIT.md, Reparatur v2.8). Das Wort wird darum aus
# diesen beiden Instanzen fortgeschrieben: P = P725 + k·(P725 − P190), k so,
# dass der I-Stamm den Zielwert erreicht. Ausgabe: ein SVG mit Laut, Schreien
# und der Fortschreibung, im Befund als Bild.
#
#   python3 tools/goetheanum-fontfix/proof_black_probewort.py [Ziel-Stamm] [Ausgabe.svg]
import os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.8.otf")
WORT = "Goetheanum"


def inst(w):
    f = instantiateVariableFont(TTFont(VAR), {"wght": w})
    return f, f.getGlyphSet(), f.getBestCmap()


def rec(gs, name):
    p = RecordingPen(); gs[name].draw(p); return p.value


def stem(gs, cmap):
    g = gs[cmap[ord("I")]]; a = AreaPen(gs); g.draw(a); b = BoundsPen(gs); g.draw(b)
    return abs(a.value) / (b.bounds[3] - b.bounds[1])


def mix(r0, r1, k):
    out = []
    for (op, a0), (_, a1) in zip(r0, r1):
        out.append((op, tuple((p1[0] + k * (p1[0] - p0[0]), p1[1] + k * (p1[1] - p0[1]))
                              for p0, p1 in zip(a0, a1))))
    return out


def path(r, dx):
    pen = SVGPathPen(None)
    for op, a in r:
        getattr(pen, op)(*[(x + dx, y) for x, y in a])
    return pen.getCommands()


def main():
    ziel = float(sys.argv[1]) if len(sys.argv) > 1 else 180.0
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        REPO, "docs/befunde/black-probewort-e5-2026-10-31.svg")
    f0, g0, c = inst(190); f1, g1, _ = inst(725); f6, g6, _ = inst(680)
    s0, s1, s6 = stem(g0, c), stem(g1, c), stem(g6, c)
    k = (ziel - s1) / (s1 - s0)
    zeilen = []
    for label, gs, fn in (("Laut 680, Stamm %.0f" % s6, g6, None),
                          ("Schreien 725, Stamm %.0f" % s1, g1, None),
                          ("Fortschreibung, Stamm %.0f" % ziel, None, k)):
        x, d = 0, []
        for ch in WORT:
            n = c[ord(ch)]
            if fn is None:
                r = rec(gs, n); w = gs[n].width
            else:
                r = mix(rec(g0, n), rec(g1, n), fn)
                w = g1[n].width + fn * (g1[n].width - g0[n].width)
            d.append(path(r, x)); x += w
        zeilen.append((label, " ".join(d), x))
    W = max(z[2] for z in zeilen) + 160; H = 1250 * len(zeilen)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
           % (W, H, W // 5, H // 5), '<rect width="100%" height="100%" fill="#fff"/>']  # ds-ok
    for i, (label, d, _) in enumerate(zeilen):
        y = 1250 * i + 950
        svg.append('<text x="40" y="%d" font-family="sans-serif" font-size="110" fill="#555">%s</text>'
                   % (1250 * i + 160, label))  # ds-ok
        svg.append('<path transform="translate(40 %d) scale(1 -1)" d="%s" fill="#111"/>' % (y, d))  # ds-ok
    svg.append("</svg>")
    open(out, "w").write("\n".join(svg))
    print("k = %.2f (Gewicht ≈ %.0f), %s" % (k, 725 + k * (725 - 190), os.path.relpath(out, REPO)))


if __name__ == "__main__":
    main()
