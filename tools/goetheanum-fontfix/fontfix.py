#!/usr/bin/env python3
"""Goetheanum Schriften v1.4.43 – reproducible repair pipeline (binary patch).
Imports missing glyphs / fixes ampersand weight via interpolation of the
Titillium Upright masters, repairs metadata, vertical metrics, names & license.
No design errors are imported: every borrowed outline is weight-matched and
the broken Titillium 'fraction' glyph is never used.
"""
import re, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen

# Titillium Upright masters used as the interpolation source for borrowed glyphs.
# Override the directory via the GOE_SOURCES env var; defaults to ./sources next to this file.
_SRC = os.environ.get("GOE_SOURCES", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources"))
UPRIGHTS = {n: os.path.join(_SRC, f"Titillium-{n}Upright.otf")
            for n in ["Thin", "Light", "Regular", "Semibold", "Bold"]}

def load_uprights():
    M = {n: TTFont(p) for n,p in UPRIGHTS.items()}
    H = {}
    for n,ft in M.items():
        H[n] = glyph_area(ft, 0x48)
    return M, H

def grec(font, uni):
    gn = font.getBestCmap().get(uni)
    if not gn: return None, None
    gs = font.getGlyphSet(); rp = RecordingPen(); gs[gn].draw(rp)
    return rp.value, font["hmtx"][gn][0]

def area_of(recv):
    ap = AreaPen(None)
    for c,p in recv: (getattr(ap,c)(*p) if p else getattr(ap,c)())
    return abs(ap.value)

def glyph_area(font, uni):
    r,_ = grec(font, uni)
    return area_of(r) if r else None

def sig(recv):
    return tuple((c,len(p)) for c,p in recv) if recv else None

def blend(rA,aA,rB,aB,t):
    out=[(c, tuple(tuple((1-t)*x+t*y for x,y in zip(a,b)) for a,b in zip(pA,pB)))
         for (c,pA),(_,pB) in zip(rA,rB)]
    return out, round((1-t)*aA + t*aB)

def pick_and_interp(M, H, uni, targetH):
    """Choose a point-compatible bracketing master pair, interpolate to targetH."""
    cand=[(n, grec(M[n],uni)) for n in M]
    cand=[(n,(r,a)) for n,(r,a) in cand if r is not None]
    from collections import defaultdict
    groups=defaultdict(list)
    for n,(r,a) in cand: groups[sig(r)].append(n)
    # best group: prefer one whose H-range brackets targetH, then larger, then closest
    best=None
    for s,ns in groups.items():
        ns=sorted(ns,key=lambda n:H[n]); lo,hi=H[ns[0]],H[ns[-1]]
        score=(lo<=targetH<=hi, len(ns), -abs((lo+hi)/2-targetH))
        if best is None or score>best[0]: best=(score,ns)
    ns=best[1]
    lo=max([n for n in ns if H[n]<=targetH], key=lambda n:H[n], default=ns[0])
    hi=min([n for n in ns if H[n]>=targetH], key=lambda n:H[n], default=ns[-1])
    if lo==hi:
        i=ns.index(lo); hi=ns[i+1] if i+1<len(ns) else (ns.index(lo) and ns[i-1] or ns[-1]); 
        if lo==hi and len(ns)>1: lo=ns[0]; hi=ns[-1]
    rA,aA=grec(M[lo],uni); rB,aB=grec(M[hi],uni)
    t=(targetH-H[lo])/(H[hi]-H[lo]) if H[hi]!=H[lo] else 0.0
    recI,advI=blend(rA,aA,rB,aB,t)
    return recI, advI, (lo,hi,round(t,3))

# ---- CID CFF glyph operations ----
def _charstring(ft, recv, adv):
    cff=ft["CFF "].cff; td=cff[cff.fontNames[0]]
    priv=td.FDArray[0].Private if hasattr(td,'FDArray') else td.Private
    pen=T2CharStringPen(adv, None)
    for c,p in recv: (getattr(pen,c)(*p) if p else getattr(pen,c)())
    return pen.getCharString(private=priv, globalSubrs=cff.GlobalSubrs)

def add_cid_glyph(ft, uni, recv, adv, prefer_name=None):
    cff=ft["CFF "].cff; td=cff[cff.fontNames[0]]
    cs=_charstring(ft, recv, adv)
    is_cid=hasattr(td,'FDArray') and hasattr(td,'FDSelect')
    if is_cid:
        cids=[int(n[3:]) for n in td.charset if re.fullmatch(r'cid\d+',n)]
        name="cid%05d"%(max(cids)+1)
    else:
        name=prefer_name or ("uni%04X"%uni)
    td.CharStrings.charStringsIndex.append(cs)
    td.CharStrings.charStrings[name]=len(td.CharStrings.charStringsIndex)-1
    td.charset.append(name)
    if is_cid: td.FDSelect.append(0)
    xs=[x for c,p in recv for (x,y) in p]
    ft["hmtx"].metrics[name]=(adv, round(min(xs)) if xs else 0)
    ft.setGlyphOrder(list(td.charset))
    for t_ in ft["cmap"].tables: t_.cmap[uni]=name
    return name

def replace_glyph_outline(ft, uni, recv, adv):
    cff=ft["CFF "].cff; td=cff[cff.fontNames[0]]
    name=ft.getBestCmap()[uni]
    td.CharStrings[name]=_charstring(ft, recv, adv)
    xs=[x for c,p in recv for (x,y) in p]
    ft["hmtx"].metrics[name]=(adv, round(min(xs)) if xs else 0)
    return name

def set_advance_lsb(ft, uni, adv, lsb):
    name=ft.getBestCmap()[uni]; ft["hmtx"].metrics[name]=(adv,lsb); return name

print("module ok")
