#!/usr/bin/env python3
# Specimen: Philipp's ligatures + numero + (my) prime/doubleprime/figure-dash in running text.
import os, sys, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
import cairosvg

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
LIGSVG = "/tmp/ph_lig/f-ligaturen_ph.svg"
NUMSVG = "/tmp/ph_num/numero_ph.svg"
INK = "#23272b"

def extract(svgfile, gid, baseline):
    root = ET.parse(svgfile).getroot(); target = None
    for e in root.iter():
        if e.get('id') == gid: target = e; break
    if target is None: return None
    rp = RecordingPen()
    for e in target.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'): parse_path(e.get('d'), rp)
    pts = [p for c, ps in rp.value for p in ps]
    if not pts: return None
    xs = [x for x, y in pts]; minx = min(xs)
    rec = [(c, tuple((x - minx, baseline - y) for x, y in ps)) for c, ps in rp.value]
    return rec, (max(xs) - minx)

def poly_rec(pts):
    out = [("moveTo", (pts[0],))] + [("lineTo", (p,)) for p in pts[1:]] + [("closePath", ())]
    return out

def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
def extract_lig(gid):
    root = ET.parse(LIGSVG).getroot(); target = None
    for e in root.iter():
        if e.get('id') == gid: target = e; break
    if target is None: return None
    rp = RecordingPen()
    for e in target.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'): parse_path(e.get('d'), rp)
    pts = [p for c, ps in rp.value for p in ps]
    if not pts: return None
    xs = [x for x, y in pts]; ys = [y for x, y in pts]; minx = min(xs); By = baseline_for(min(ys))
    return [(c, tuple((x - minx, By - y) for x, y in ps)) for c, ps in rp.value], max(xs)-minx

# substitutions: sequence -> (rec baseline-relative y-up, width)
SUBS = {}
for seq in ("ff", "fi", "fl", "fj", "fk", "ft"):
    r = extract_lig(seq)
    if r: SUBS[seq] = r
n = extract(NUMSVG, "numero", 820)
if n: SUBS["№"] = n
SUBS["′"] = (poly_rec([(0,430),(85,430),(155,690),(70,690)]), 165)
SUBS["″"] = (poly_rec([(0,430),(85,430),(155,690),(70,690)]) + poly_rec([(170,430),(255,430),(325,690),(240,690)]), 335)
SUBS["‒"] = (poly_rec([(0,300),(420,300),(420,373),(0,373)]), 480)
print("substitutions:", {k: round(v[1]) for k, v in SUBS.items()})

def emit(rec, gx, base):
    d = []
    for c, p in rec:
        q = [(gx + x, base - y) for x, y in p]
        if c == "moveTo": d.append("M%.1f %.1f" % q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
        elif c == "qCurveTo":
            for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

LIGSEQ = ["ff", "fi", "fl", "fj", "fk", "ft"]
LSB = 32
def layout(text, base, gx0):
    out = []; gx = gx0; i = 0
    while i < len(text):
        seq = None
        for s in LIGSEQ:
            if text[i:i+len(s)] == s and s in SUBS: seq = s; break
        if seq:
            rec, w = SUBS[seq]; out.append(emit(rec, gx+LSB, base)); gx += w + LSB + 55; i += len(seq); continue
        ch = text[i]
        if ch in SUBS:
            rec, w = SUBS[ch]; out.append(emit(rec, gx+LSB, base)); gx += w + LSB + 55; i += 1; continue
        if ch == " ":
            gx += grec(fK, 0x20)[1] or 250
        else:
            rec, adv = grec(fK, ord(ch))
            if rec: out.append(emit(rec, gx, base)); gx += adv
            elif adv: gx += adv
        i += 1
    return "".join('<path d="%s" fill="%s"/>' % (d, INK) for d in out), gx

LINES = [
    "Auffällige, fließende Schriftzüge — Saal № 7,",
    "Reihe 1914‒1918, das Schiff, der Stoff, der Pfiff.",
    "Die Auflage, das Pflaster, fünf Koffer, sanfte Kraft.",
    "Standort 47° 32′ 18″, Höhe 5′ 11″ — oft geprüft, schaffen.",
]
PXU = 0.13; maxx = 0
for ln in LINES:
    _, ex = layout(ln, 0, 60); maxx = max(maxx, ex)
W = int(maxx) + 120; LH = 1320; H = 320 + len(LINES)*LH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
       '<text x="60" y="210" font-family="Helvetica,Arial" font-size="150" fill="#9aa0a6">Alle Entwürfe im Einsatz (Ligaturen · № · Prime ′ ″ · Figure-Dash)</text>']
for i, ln in enumerate(LINES):
    base = 380 + i*LH + 740
    g, _ = layout(ln, base, 60); svg.append(g)
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/ph_specimen.png", output_width=int(W*PXU))
print("wrote /tmp/ph_specimen.png  W=%d -> %dpx" % (W, int(W*PXU)))
