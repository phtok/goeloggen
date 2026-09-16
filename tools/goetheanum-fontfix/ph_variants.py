#!/usr/bin/env python3
# Lay out Philipp's ligature variants side by side, labelled.
import os, sys, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
import cairosvg
INK = "#23272b"; MUT = "#9aa0a6"; GUIDE = "#e2ddd0"
SVG = "/tmp/ph_lig/f-ligaturen_ph.svg"

def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
def extract(gid):
    root = ET.parse(SVG).getroot(); target = None
    for e in root.iter():
        if e.get('id') == gid: target = e; break
    if target is None: return None
    rp = RecordingPen()
    for e in target.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'): parse_path(e.get('d'), rp)
    pts = [p for c, ps in rp.value for p in ps]
    if not pts: return None
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    minx = min(xs); By = baseline_for(min(ys))
    return [(c, tuple((x - minx, By - y) for x, y in ps)) for c, ps in rp.value], max(xs)-minx
def emit(rec, s, gx, base):
    d = []
    for c, p in rec:
        q = [(gx+s*x, base-s*y) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

GROUPS = [["ff","ff1","ff2","ff3","ff4","ff5","ff6","ff7","ff8"],
          ["fi","fi1","fi2"], ["ft","ft1"], ["fj","fk","fl"]]
PXU = 0.16; CW = 760; CH = 1500
cols = 9
W = 80 + cols*CW; rows = len(GROUPS); H = 200 + rows*CH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
       '<text x="50" y="150" font-family="Helvetica,Arial" font-size="120" fill="#23272b">Deine Varianten</text>']
for r, ids in enumerate(GROUPS):
    cy = 240 + r*CH; base = cy + 980
    for fy in (0, 500, 690):
        gy = base - fy
        svg.append('<line x1="40" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="3"/>' % (gy, W-40, gy, GUIDE))
    for c, gid in enumerate(ids):
        ex = extract(gid)
        if not ex: continue
        rec, w = ex; cx = 60 + c*CW
        svg.append('<path d="%s" fill="%s"/>' % (emit(rec, 1.0, cx, base), INK))
        svg.append('<text x="%d" y="%d" font-family="Helvetica,Arial" font-size="90" fill="%s">%s</text>' % (cx, cy-30, MUT, gid))
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/ph_variants.png", output_width=int(W*PXU))
print("wrote /tmp/ph_variants.png  W=%d -> %dpx" % (W, int(W*PXU)))
