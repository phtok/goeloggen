#!/usr/bin/env python3
# Export the FULL set of f-ligatures as editable SVG in the original/simple form:
#   f + following letter, tucked (overlap) under the preceding f, dotless i/j,
#   WITHOUT the bow-extension / crossbar-bridge refinement. Separate contours.
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont

fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
ENTW = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "entwuerfe"))
os.makedirs(ENTW, exist_ok=True)
OVL = 90

def split_contours(rec):
    cs, cur = [], []
    for seg in rec:
        if seg[0] == "moveTo":
            if cur: cs.append(cur)
            cur = [seg]
        else:
            cur.append(seg)
    if cur: cs.append(cur)
    return cs

def dotless_j():
    rec, adv = grec(fK, 0x6A)
    cs = split_contours(rec)
    if len(cs) > 1:
        cs.sort(key=lambda ct: min(y for _, p in ct for _, y in p))
        cs = cs[:-1]                                   # drop the dot (highest contour)
    return [seg for ct in cs for seg in ct], adv

DJ = dotless_j()
def glyphrec(ch):
    if ch == "i": return grec(fK, 0x131)               # dotless i
    if ch == "j": return DJ                            # dotless j (constructed)
    return grec(fK, ord(ch))

def recmap(rec, dx):
    return [(c, tuple((x + dx, y) for x, y in p)) for c, p in rec]

def build(word):
    """contours (one per glyph) + total width; tuck non-f letters under preceding f."""
    cont = []; px = 0.0; prev_f = False
    for ch in word:
        rec, adv = glyphrec(ch)
        if prev_f and ch != "f": px -= OVL
        cont.append(recmap(rec, px)); px += adv
        prev_f = (ch == "f")
    return cont, px

def export(name, contours, width):
    BASE, LM, Hc = 820, 70, 1120
    W = int(width) + 140
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hc, W, Hc),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hc),
           '<g id="metriken" stroke="#cfcabe" stroke-width="1" fill="none">']
    for fy in (0, 500, 690, -220):
        out.append('<line x1="0" y1="%.0f" x2="%d" y2="%.0f"/>' % (BASE - fy, W, BASE - fy))
    out.append('</g><g id="%s" fill="#111">' % name)
    for rec in contours:
        d = []
        for c, p in rec:
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

LIGS = ["ff", "fb", "fh", "fi", "fj", "fk", "fl", "ft",
        "ffb", "ffh", "ffi", "ffj", "ffk", "ffl", "fft"]
for w in LIGS:
    cont, width = build(w); export(w, cont, width)

# contact sheet PNG of all ligatures (matches the downloads)
import cairosvg
COLS, CW, CH, BASE = 5, 560, 640, 470
ROWS = (len(LIGS) + COLS - 1) // COLS
WB, HB = COLS * CW + 60, 120 + ROWS * CH
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (WB//2, HB//2, WB, HB),
       '<rect width="%d" height="%d" fill="#fff"/>' % (WB, HB),
       '<text x="40" y="64" font-family="Helvetica,Arial" font-size="34" fill="#23272b">f-Ligaturen — schlichte Ursprungsfassung (editierbare SVG)</text>']
for idx, w in enumerate(LIGS):
    cont, width = build(w)
    r, c = divmod(idx, COLS); cx = 30 + c*CW; cy = 110 + r*CH; base = cy + BASE
    sc = min(0.52, (CW-150) / max(width, 1)); gx = cx + (CW - width*sc) / 2
    d = []
    for rec in cont:
        for cm, p in rec:
            q = [(gx + sc*x, base - sc*y) for x, y in p]
            if cm == "moveTo": d.append("M%.1f %.1f" % q[0])
            elif cm == "lineTo": d.append("L%.1f %.1f" % q[0])
            elif cm == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (q[0]+q[1]+q[2]))
            elif cm == "qCurveTo":
                for i in range(len(q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (q[i]+q[i+1]))
            elif cm == "closePath": d.append("Z")
    svg.append('<path d="%s" fill="#23272b"/>' % "".join(d))
    svg.append('<text x="%d" y="%d" font-family="Helvetica,Arial" font-size="22" fill="#9aa0a6" text-anchor="middle">%s</text>' % (cx + CW/2, cy + CH - 30, w))
svg.append("</svg>")
cairosvg.svg2png(bytestring="\n".join(svg).encode(), write_to="/tmp/lig_sheet.png", output_width=WB//2)
print("exported %d f-ligature SVGs + contact sheet ->" % len(LIGS), ENTW)
print(" ".join(LIGS))
