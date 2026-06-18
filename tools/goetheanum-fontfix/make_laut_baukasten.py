#!/usr/bin/env python3
# Build a Laut redraw baukasten: the v2.4.1 Laut letters at the CORRECT (heavier)
# weight as the editable base, laid out per ligature, with Philipp's previous bow
# shapes overlaid as a faint guide (shape/reach reference, not weight). Metric
# lines included. Philipp extends the bows by hand at the right weight.
import glob, os, sys, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.chdir(os.path.join(HERE, "..", ".."))
from fontTools.ttLib import TTFont
from fontfix import grec
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

laut = TTFont(glob.glob("assets/fonts/goetheanum/**/*v2.4.1-Laut.otf", recursive=True)[0])
def gly(uni):
    r, a = grec(laut, uni); return r, a

BASE = 800.0  # svg-y of baseline
def emit(rec, dx, base=BASE):
    d = []
    for c, p in rec:
        Q = [(x + dx, base - y) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % Q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % Q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
        elif c == "qCurveTo":
            for i in range(len(Q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (Q[i]+Q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)
def gminx(rec): return min(x for c, p in rec for x, y in p)

# old drawn Laut stretched-f bows (faint guides) from the previous baukasten
root = ET.parse("assets/entwuerfe/ligatur-baukasten-ph.svg").getroot(); old = {}
def walk(e, g=None):
    for c in e:
        i = c.get("id") or g
        if c.tag.split('}')[-1] == "path" and c.get("d"):
            rp = RecordingPen(); parse_path(c.get("d"), rp); old[i or "_a%d" % len(old)] = rp.value
        walk(c, c.get("id") or g)
walk(root)
OLDBASE = 3859.5
def old_fontY(v): return [(c, tuple((x, OLDBASE - y) for x, y in p)) for c, p in v]

fR, fA = gly(0x66); iR, iA = gly(0x131); lR, lA = gly(0x6C); tR, tA = gly(0x74)
COLS = [
 ("ff-standard", [(fR, fA, False, None), (fR, fA, False, None)]),
 ("ff-wortende", [(fR, fA, False, None), (fR, fA, True, "r2-f3")]),
 ("fi-weit",     [(fR, fA, True, "r2-f6"), (iR, iA, False, None)]),
 ("fl",          [(fR, fA, True, "r2-f4"), (lR, lA, False, None)]),
 ("ft",          [(fR, fA, True, "r2-f5"), (tR, tA, False, None)]),
]

paths = []; guides = []; col_label_x = []
x = 120.0; LSP = 70.0; COLGAP = 300.0
for name, letters in COLS:
    col_start = x
    for (rec, adv, stretch, oldid) in letters:
        gx = x - gminx(rec)
        paths.append((emit(rec, gx), stretch))
        if oldid and oldid in old:
            ov = old_fontY(old[oldid]); ox = x - gminx(ov)
            guides.append(emit(ov, ox))
        x += adv + LSP
    col_label_x.append((name, col_start))
    x += COLGAP - LSP

WIDTH = x + 120; HEIGHT = 1320
LINES = [("Grundlinie", 800), ("x-Höhe", 300), ("Versal/Oberlänge", 85), ("Unterlänge", 1050)]
svg = ['<?xml version="1.0" encoding="UTF-8"?>',
 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f">' % (WIDTH, HEIGHT),
 '<defs><style>.base{fill:#111}.stretch{fill:#111}'
 '.guide{fill:none;stroke:#c98a2b;stroke-width:3;stroke-dasharray:10 8;opacity:.75}'
 '.ml{fill:none;stroke:#cdd2d6;stroke-width:2}.mt{fill:#9aa0a6;font:28px Helvetica}'
 '.lab{fill:#23272b;font:30px Helvetica}.title{fill:#23272b;font:36px Helvetica}.note{fill:#6b7177;font:24px Helvetica}</style></defs>']
svg.append('<text class="title" x="40" y="58">Laut neu zeichnen — am korrekten Gewicht (v2.4.1)</text>')
svg.append('<text class="note" x="40" y="98">Schwarz = echte v2.4.1-Laut-Buchstaben (richtige Fette, editierbar). Gold gestrichelt = deine bisherige Bogenform (Form/Reichweite). Ziehe die Bögen am schwarzen f auf diese Reichweite.</text>')
for nm, yy in LINES:
    svg.append('<line class="ml" x1="40" y1="%.1f" x2="%.0f" y2="%.1f"/>' % (yy, WIDTH-40, yy))
    svg.append('<text class="mt" x="%.0f" y="%.1f">%s</text>' % (WIDTH-300, yy-10, nm))
for d in guides: svg.append('<path class="guide" d="%s"/>' % d)
for d, stretch in paths: svg.append('<path class="%s" d="%s"/>' % ("stretch" if stretch else "base", d))
for nm, lx in col_label_x: svg.append('<text class="lab" x="%.0f" y="1180">%s</text>' % (lx, nm))
svg.append('</svg>')
out = "assets/entwuerfe/laut-neu-baukasten.svg"
open(out, "w").write("\n".join(svg))
print("wrote", out, "width", int(WIDTH))
