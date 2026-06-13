#!/usr/bin/env python3
# Proof render for v2.4.1 calibration — Klar cut.
# Kurzziffern: Hoehe 515 / Gewicht 540 / Laufweite 0
# Kapitaelchen: Hoehe 505 / Gewicht 550 / Laufweite +30
# Weight via interpolation between family cuts (Klar 440 <-> Laut 680);
# height via uniform scale H/690 (same model as werkzeug.html).
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fontfix import grec, blend, sig
from fontTools.ttLib import TTFont
import cairosvg

KLAR = glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0]
LAUT = glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0]
fK, fL = TTFont(KLAR), TTFont(LAUT)
W_KLAR, W_LAUT, CAP = 440.0, 680.0, 690.0

FIG_H, FIG_W, FIG_T = 515, 540, 0
CAP_H, CAP_W, CAP_T = 505, 550, 30

def interp(uni, target_w):
    rA, aA = grec(fK, uni)
    rB, aB = grec(fL, uni)
    if rA is None: return None, 0
    if rB is None or sig(rA) != sig(rB):
        return rA, aA                                  # not compatible -> Klar as-is
    t = (target_w - W_KLAR) / (W_LAUT - W_KLAR)
    return blend(rA, aA, rB, aB, t)

def xform(recv, s, dx):
    return [(c, tuple((x * s + dx, y * s) for x, y in p)) for c, p in recv]

def to_path(recv):
    d = []
    for c, p in recv:
        if c == "moveTo":   d.append("M%.1f %.1f" % p[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % p[0])
        elif c == "curveTo":d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (p[0]+p[1]+p[2]))
        elif c == "qCurveTo":
            pts = p
            for i in range(len(pts) - 1):
                d.append("Q%.1f %.1f %.1f %.1f" % (pts[i] + pts[i+1]))
        elif c == "closePath": d.append("Z")
    return "".join(d)

def glyph(ch, mode):
    """mode: 'n' normal Klar, 'd' onum digit, 'k' smcp cap. returns (recv_klarframe, advance)."""
    uni = ord(ch)
    if mode == "d":
        rec, adv = interp(uni, FIG_W); s = FIG_H / CAP
        rec = xform(rec, s, 0); return rec, adv * s + FIG_T
    if mode == "k":
        rec, adv = interp(ord(ch.upper()), CAP_W); s = CAP_H / CAP
        rec = xform(rec, s, 0); return rec, adv * s + CAP_T
    rec, adv = grec(fK, uni)
    if rec is None: rec = []
    return rec, adv

def layout(tokens, baseline_y):
    """tokens: list of (text, mode). returns (svg_paths, width)."""
    x = 0.0; paths = []
    for text, mode in tokens:
        for ch in text:
            if ch == " ":
                _, adv = grec(fK, 0x20); x += adv if adv else 250; continue
            rec, adv = glyph(ch, mode)
            rec = [(c, tuple((px + x, py) for px, py in p)) for c, p in rec]
            paths.append(to_path(rec)); x += adv
    return paths, x

def parse(s):
    """digits -> 'd', {..} -> 'k', else 'n'."""
    toks = []; i = 0
    while i < len(s):
        ch = s[i]
        if ch == "{":
            j = s.index("}", i); toks.append((s[i+1:j], "k")); i = j + 1
        elif ch.isdigit():
            j = i
            while j < len(s) and s[j].isdigit(): j += 1
            toks.append((s[i:j], "d")); i = j
        else:
            toks.append((ch, "n")); i += 1
    return toks

SAMPLE = "Am 24. Juni 1923 bestaetigte die {UNESCO} das {GOETHEANUM}; vgl. {Bd}. II, S. 36 - von 1922 auf 1487 Mitglieder."
def parse_ref(s):
    """reference line: digits default-lining, caps as full caps (drop braces)."""
    return [(s.replace("{", "").replace("}", ""), "n")]

EM = 1000; LH = 1500; PAD = 120; FS_LABEL = 150
lines = [
    ("v2.4.1  –  Kurzziffern 515/540  +  Kapitaelchen 505/550 +30", parse_ref, "lab"),
    (SAMPLE, parse, "main"),
    ("Referenz: Versalziffern + volle Versalien", parse_ref, "lab"),
    (SAMPLE, parse_ref, "ref"),
]
rows = []
maxw = 0
for text, fn, kind in lines:
    toks = fn(text) if fn is parse else fn(text)
    paths, w = layout(toks, 0)
    rows.append((paths, w, kind)); maxw = max(maxw, w)

W = maxw + 2 * PAD
H = PAD + len(rows) * LH + PAD
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W//2, H//2, W, H)]
svg.append('<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H))
y = PAD + EM
for paths, w, kind in rows:
    color = "#23272b" if kind in ("main",) else ("#a07a33" if kind == "ref" else "#9aa0a6")
    g = '<g transform="translate(%d,%d) scale(1,-1)" fill="%s">' % (PAD, y, color)
    g += '<path d="%s"/>' % "".join(paths)
    g += "</g>"
    svg.append(g)
    y += LH
svg.append("</svg>")
svg = "\n".join(svg)
out_png = "/tmp/v241_proof_klar.png"
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out_png, output_width=1800)
print("wrote", out_png)
