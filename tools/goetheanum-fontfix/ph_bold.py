#!/usr/bin/env python3
# Weg 1 bold pass: graft Philipp's join (extended bow + crossbar bridge) onto the
# font's BOLD (Laut) f + letters. Compare to his Klar drawing; show bold running text.
import os, sys, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
import cairosvg

fL = TTFont(glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0])
fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
LIGSVG = "/tmp/ph_lig/f-ligaturen_ph.svg"
INK = "#23272b"; MUT = "#9aa0a6"; GUIDE = "#e2ddd0"
BOW, OVL = 92, 95
CB0, CB1 = 500, 530                       # Laut crossbar band

def recmap(rec, dx, dy=0):
    return [(c, tuple((x+dx, y+dy) for x, y in p)) for c, p in rec]
def ext_f(rec):
    return [(c, tuple((x + BOW if (x > 175 and y > 610) else x, y) for x, y in p)) for c, p in rec]
def split_contours(rec):
    cs, cur = [], []
    for seg in rec:
        if seg[0] == "moveTo":
            if cur: cs.append(cur)
            cur = [seg]
        else: cur.append(seg)
    if cur: cs.append(cur)
    return cs
def dotless_j(ft):
    rec, adv = grec(ft, 0x6A); cs = split_contours(rec)
    if len(cs) > 1:
        cs.sort(key=lambda ct: min(y for _, p in ct for _, y in p)); cs = cs[:-1]
    return [seg for ct in cs for seg in ct], adv

f, af = grec(fL, 0x66); dj = dotless_j(fL)
def comp(ch):
    if ch == "i": return grec(fL, 0x131)
    if ch == "j": return dj
    return grec(fL, ord(ch))

def build_bold(word):
    cont = []; px = 0.0; prev_f = False
    for ch in word:
        if ch == "f":
            cont.append(ext_f(recmap(f, px)))
            if prev_f:
                cont.append([("moveTo", ((px-af+250, CB0),)), ("lineTo", ((px+150, CB0),)),
                             ("lineTo", ((px+150, CB1),)), ("lineTo", ((px-af+250, CB1),)), ("closePath", ())])
            px += af; prev_f = True
        else:
            rec, adv = comp(ch)
            if prev_f: px -= OVL
            cont.append(recmap(rec, px)); px += adv; prev_f = False
    return cont, px

# Philipp's Klar drawings (for comparison)
def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
def extract_lig(gid):
    root = ET.parse(LIGSVG).getroot(); t = None
    for e in root.iter():
        if e.get('id') == gid: t = e; break
    if t is None: return None
    rp = RecordingPen()
    for e in t.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'): parse_path(e.get('d'), rp)
    pts = [p for c, ps in rp.value for p in ps]
    xs = [x for x, y in pts]; By = baseline_for(min(y for x, y in pts)); minx = min(xs)
    return [(c, tuple((x-minx, By-y) for x, y in ps)) for c, ps in rp.value], max(xs)-minx

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
def normalize(cont):
    xs = [x for rec in cont for c, p in rec for x, y in p]; mn = min(xs)
    flat = [(c, tuple((x-mn, y) for x, y in p)) for rec in cont for c, p in rec]
    return flat, max(xs)-mn

# ---------- comparison sheet ----------
LIGS = ["ff", "fi", "fl", "ft", "fj", "fk"]
PXU = 0.16; CW = 1500; CH = 1500
W = 120 + 2*CW; rows = len(LIGS); H = 200 + rows*CH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W*PXU), int(H*PXU), W, H),
       '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
       '<text x="60" y="150" font-family="Helvetica,Arial" font-size="110" fill="#23272b">links: dein Klar-Entwurf · rechts: mein Fett-Durchgang (Laut)</text>']
for r, w in enumerate(LIGS):
    cy = 240 + r*CH; base = cy + 980
    for fy in (0, 500, 690):
        gy = base - fy; svg.append('<line x1="40" y1="%.0f" x2="%d" y2="%.0f" stroke="%s" stroke-width="3"/>' % (gy, W-40, gy, GUIDE))
    pk = extract_lig(w)
    if pk: svg.append('<path d="%s" fill="%s"/>' % (emit(pk[0], 1.0, 80, base), INK))
    bc, bw = normalize(build_bold(w)[0]); svg.append('<path d="%s" fill="%s"/>' % (emit(bc, 1.0, 120+CW, base), INK))
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/ph_bold_cmp.png", output_width=int(W*PXU))

# ---------- bold running text (Laut body + bold ligatures) ----------
BSUB = {w: normalize(build_bold(w)[0]) for w in LIGS}
LSB = 34
def layout(text, base, gx0):
    out = []; gx = gx0; i = 0
    while i < len(text):
        seq = next((s for s in LIGS if text[i:i+len(s)] == s), None)
        if seq:
            rec, w = BSUB[seq]; out.append(emit(rec, 1.0, gx+LSB, base)); gx += w+LSB+58; i += len(seq); continue
        ch = text[i]
        if ch == " ": gx += grec(fL, 0x20)[1] or 250
        else:
            rec, adv = grec(fL, ord(ch))
            if rec: out.append(emit(rec, 1.0, gx, base)); gx += adv
            elif adv: gx += adv
        i += 1
    return "".join('<path d="%s" fill="%s"/>' % (d, INK) for d in out), gx
LINES = ["Auffällige, fließende Schriftzüge:", "Pfiff, Schiff, Stoff, fünf Koffer,",
         "die Auflage, das Pflaster, sanfte Kraft — schaffen."]
PXU2 = 0.082; mx = max(layout(l, 0, 60)[1] for l in LINES)
W2 = int(mx)+120; LH = 1320; H2 = 300 + len(LINES)*LH
s2 = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (int(W2*PXU2), int(H2*PXU2), W2, H2),
      '<rect width="%d" height="%d" fill="#fff"/>' % (W2, H2),
      '<text x="60" y="200" font-family="Helvetica,Arial" font-size="150" fill="#9aa0a6">Fett-Durchgang im Fliesstext (Laut)</text>']
for i, l in enumerate(LINES):
    base = 360 + i*LH + 740; s2.append(layout(l, base, 60)[0])
s2.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(s2).encode(), write_to="/tmp/ph_bold_fliess.png", output_width=int(W2*PXU2))
print("wrote /tmp/ph_bold_cmp.png and /tmp/ph_bold_fliess.png")
