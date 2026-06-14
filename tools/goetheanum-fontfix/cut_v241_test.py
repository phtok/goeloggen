#!/usr/bin/env python3
# Validation cut: build v2.4.1 features into a COPY of Klar (no release, no version bump).
#   onum  -> figures interpolated to weight + scaled to height + tracking
#   smcp/c2sc -> small caps from caps, same method
#   U+2010 / U+00AD hyphens
# Then verify with HarfBuzz and render a proof from the BUILT font.
import os, sys, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontfix import grec, blend, sig, add_cid_glyph
from build import _add_alt, _add_gsub_single, OUTROOT, static_out, SCHEMES
from fontTools.ttLib import TTFont

# weight masters = the three finished cuts
MASTERS, ANCH = {}, []
for sch in SCHEMES:
    m = TTFont(os.path.join(OUTROOT, "Fonts", static_out(sch)))
    MASTERS[m["OS/2"].usWeightClass] = m
ANCH = sorted(MASTERS)
print("masters (weights):", ANCH)

CAP = 690.0
FIG_H, FIG_dW, FIG_T = 533, 80, 10     # +80 over cut weight
CAP_H, CAP_dW, CAP_T = 511, 110, 30    # +110 over cut weight
S_FIG, S_CAP = FIG_H/CAP, CAP_H/CAP

def interp_w(uni, target):
    ws = ANCH
    if target <= ws[0]: lo, hi = ws[0], ws[1]
    elif target >= ws[-1]: lo, hi = ws[-2], ws[-1]
    else:
        lo = max(w for w in ws if w <= target); hi = min(w for w in ws if w >= target)
        if lo == hi: hi = ws[ws.index(lo)+1] if ws.index(lo)+1 < len(ws) else ws[ws.index(lo)-1]
    rA, aA = grec(MASTERS[lo], uni); rB, aB = grec(MASTERS[hi], uni)
    if rA is None: return None, 0
    if rB is None or sig(rA) != sig(rB): return rA, aA
    t = (target - lo) / (hi - lo)
    return blend(rA, aA, rB, aB, t)

def mk_alt(ft, src_uni, target_w, s, track):
    rec, adv = interp_w(src_uni, target_w)
    if rec is None: return None
    sh = track / 2.0
    rec = [(c, tuple((x*s + sh, y*s) for x, y in p)) for c, p in rec]
    return _add_alt(ft, rec, adv*s + track)

def build(ft):
    cmap = ft.getBestCmap(); cut_w = ft["OS/2"].usWeightClass
    figW, capW = min(725, cut_w + FIG_dW), min(725, cut_w + CAP_dW)
    # --- onum (replace): interpolate + scale ---
    onum = {}
    for d in range(0x30, 0x3A):
        gn = cmap.get(d)
        if gn: onum[gn] = mk_alt(ft, d, figW, S_FIG, FIG_T)
    _add_gsub_single(ft, "onum", {k: v for k, v in onum.items() if v})
    # --- small caps ---
    smcp, c2sc = {}, {}
    pairs = []
    for cp in list(cmap):
        ch = chr(cp)
        if cp < 0x250 and ch.isalpha() and ch.islower() and len(ch.upper()) == 1:
            up = ord(ch.upper())
            if up in cmap: pairs.append((cp, up))
    pairs.append((0x26, 0x26))                       # & -> small-cap &
    seen = {}
    for low, up in pairs:
        alt = seen.get(up)
        if alt is None:
            alt = mk_alt(ft, up, capW, S_CAP, CAP_T); seen[up] = alt
        if not alt: continue
        smcp[cmap[low]] = alt
        if up in cmap and up != 0x26: c2sc[cmap[up]] = alt
    _add_gsub_single(ft, "smcp", smcp)
    _add_gsub_single(ft, "c2sc", c2sc)
    # --- hyphens ---
    if 0x2D in cmap:
        rh, ah = grec(ft, 0x2D)
        for u in (0x2010, 0x00AD):
            if u not in cmap: add_cid_glyph(ft, u, rh, ah)
    return len(onum), len(smcp), len(c2sc)

src = os.path.join(OUTROOT, "Fonts", static_out("Klar"))
ft = TTFont(src)
no, ns, nc = build(ft)
out = "/tmp/Klar-v241-test.otf"
ft.save(out)
print("built %s  onum=%d smcp=%d c2sc=%d" % (out, no, ns, nc))
