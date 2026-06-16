#!/usr/bin/env python3
# Use Philipp's ACTUAL drawn ligatures in Klar running text, with word-end ff logic:
# mid-word ff = default (id "ff"), word-end ff = swung bow (id "ff5"). Please confirm mapping.
import os, sys, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
SVG = "/tmp/ph_lig/f-ligaturen_ph.svg"; INK = "#23272b"
root = ET.parse(SVG).getroot()
parent = {c: p for p in root.iter() for c in p}
def find(gid):
    for e in root.iter():
        if e.get('id') == gid: return e
def paths_of(el): return [e.get('d') for e in el.iter() if e.tag.split('}')[-1] == 'path' and e.get('d')]
def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
def extract(gid):
    el = find(gid)
    if el is None: return None
    ps = paths_of(el)
    if len(ps) < 2 and el in parent: ps = paths_of(parent[el])
    rp = RecordingPen()
    for d in ps: parse_path(d, rp)
    pts = [p for c, q in rp.value for p in q]
    if not pts: return None
    xs = [x for x, y in pts]; minx = min(xs); By = baseline_for(min(y for x, y in pts))
    return [(c, tuple((x-minx, By-y) for x, y in q)) for c, q in rp.value], max(xs)-minx

GL = {k: extract(v) for k, v in {"ff": "ff", "ffend": "ff5", "fi": "fi", "fl": "fl",
                                 "ft": "ft", "fj": "fj", "fk": "fk"}.items()}
print("extracted:", {k: (round(v[1]) if v else None) for k, v in GL.items()})

def emit(rec, gx, base):
    d = []
    for c, p in rec:
        q = [(gx+x, base-y) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

LIGSEQ = ["ff", "fi", "fl", "fj", "fk", "ft"]
BOUND = set(" ,.;:!?—-–)")
LSB = 30
def layout(text, base, gx0):
    out = []; gx = gx0; i = 0
    while i < len(text):
        seq = next((s for s in LIGSEQ if text[i:i+len(s)] == s), None)
        if seq and GL.get(seq):
            key = seq
            if seq == "ff":
                nxt = text[i+2] if i+2 < len(text) else " "
                if nxt in BOUND and GL.get("ffend"): key = "ffend"   # word-end ff
            rec, w = GL[key]; out.append(emit(rec, gx+LSB, base)); gx += w+LSB+52; i += len(seq); continue
        ch = text[i]
        if ch == " ": gx += grec(fK, 0x20)[1] or 250
        else:
            rec, adv = grec(fK, ord(ch))
            if rec: out.append(emit(rec, gx, base)); gx += adv
            elif adv: gx += adv
        i += 1
    return "".join('<path d="%s" fill="%s"/>' % (d, INK) for d in out), gx

LINES = [
    "Wortende: der Stoff, das Schiff, ein Pfiff.",
    "Wortintern: Koffer, schaffen, treffen, öffnen.",
    "Auflage, Pflaster, Grafik, sanfte Kraft, oft.",
]
PXU = 0.092; mx = max(layout(l, 0, 60)[1] for l in LINES)
W = int(mx)+120; LH = 1300; H = 320 + len(LINES)*LH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
       '<text x="60" y="210" font-family="Helvetica,Arial" font-size="150" fill="#9aa0a6">Deine Ligaturen + Wortend-ff (id ff5) gegen wortinternes ff (id ff)</text>']
for i, l in enumerate(LINES):
    base = 360 + i*LH + 740; svg.append(layout(l, base, 60)[0])
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/ph_wordend.png", output_width=int(W*PXU))
print("wrote /tmp/ph_wordend.png")
