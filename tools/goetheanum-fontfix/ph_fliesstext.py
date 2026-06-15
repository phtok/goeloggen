#!/usr/bin/env python3
# Place Philipp's drawn ligatures into running text (Klar body), at font scale.
import os, sys, glob, re
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
SVG = "/tmp/ph_lig/f-ligaturen_ph.svg"
INK = "#23272b"

# baseline per grid row (from the combined export coord system)
def baseline_for(top_y):
    return 1020 if top_y < 1400 else (2340 if top_y < 2900 else 3660)

def extract(group_id):
    """Return (recording in font units, advance) for the named group, baseline-relative y-up."""
    tree = ET.parse(SVG); root = tree.getroot()
    # find element with this id anywhere
    target = None
    for e in root.iter():
        if e.get('id') == group_id:
            target = e; break
    if target is None: return None
    paths = [e.get('d') for e in target.iter() if e.tag.split('}')[-1] == 'path' and e.get('d')]
    rp = RecordingPen()
    for d in paths: parse_path(d, rp)
    pts = [p for c, ps in rp.value for p in ps]
    if not pts: return None
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    minx = min(xs); By = baseline_for(min(ys))
    rec = [(c, tuple((x - minx, By - y) for x, y in ps)) for c, ps in rp.value]
    width = (max(xs) - minx)
    return rec, width

def emit(rec, scale, gx, base):
    d = []
    for c, p in rec:
        q = [(gx + scale*x, base - scale*y) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

# primary ligatures from Philipp's file (id -> sequence)
PRIM = {"ff": "ff", "fi": "fi", "fl": "fl", "fj": "fj", "fk": "fk", "ft": "ft"}
LIG = {}
for gid, seq in PRIM.items():
    r = extract(gid)
    if r: LIG[seq] = r            # (rec, width)
print("extracted:", {k: round(v[1]) for k, v in LIG.items()})

LSB, RSB = 30, 55                 # approx sidebearings for the ligature box

def layout(text, base, gx0):
    out = []; gx = gx0; i = 0
    order = ["ff", "fi", "fl", "fj", "fk", "ft"]
    while i < len(text):
        hit = None
        for seq in order:
            if seq in LIG and text[i:i+len(seq)] == seq: hit = seq; break
        if hit:
            rec, w = LIG[hit]
            out.append(emit(rec, 1.0, gx + LSB, base)); gx += w + LSB + RSB; i += len(hit)
        else:
            ch = text[i]
            if ch == " ":
                gx += grec(fK, 0x20)[1] or 250
            else:
                rec, adv = grec(fK, ord(ch))
                if rec: out.append(emit(rec, 1.0, gx, base)); gx += adv
            i += 1
    return "".join('<path d="%s" fill="%s"/>' % (d, INK) for d in out), gx

LINES = [
    "Auffällige, fließende Schriftzüge:",
    "der Pfiff, das Schiff, der Stoff,",
    "fünf Koffer, die Auflage, das Pflaster,",
    "sanfte Kraft, oft geprüft — schaffen.",
]
PXU = 0.085
maxx = 0; rendered = []
for ln in LINES:
    g, ex = layout(ln, 0, 60); rendered.append(g); maxx = max(maxx, ex)
W = int(maxx) + 120; LH = 1350; H = 300 + len(LINES)*LH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
       '<text x="60" y="210" font-family="Helvetica,Arial" font-size="150" fill="#9aa0a6">Deine Ligaturen im Fliesstext (Klar)</text>']
for i, ln in enumerate(LINES):
    base = 360 + i*LH + 760
    g, _ = layout(ln, base, 60); svg.append(g)
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/ph_fliess.png", output_width=int(W*PXU))
print("wrote /tmp/ph_fliess.png  W=%d -> %dpx" % (W, int(W*PXU)))
