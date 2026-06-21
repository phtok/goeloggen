#!/usr/bin/env python3
# v2.5 ligature injection (patch on the built v2.4.1 static cuts):
#   adds glyphs f_f, f_f.alt (Wortende), f_i, f_l, f_t composed from Philipp's
#   drawings (Laut = neu/korrektes Gewicht, Klar = r0, Leise = r3, je an der
#   gezeichneten Distanz), plus GSUB:  liga (ff/fi/fl/ft) + calt (Wortend-ff
#   vor Leer-/Satzzeichen).  Appends to the existing GSUB (smcp/onum bleiben).
import os, sys, glob, re
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from fontfix import grec, _charstring
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OLD = os.path.join(REPO, "assets/entwuerfe/ligatur-baukasten-ph.svg")
NEW = os.path.join(REPO, "assets/entwuerfe/laut-neu-baukasten-ph.svg")
KEYS = ["ff", "ffe", "fi", "fl", "ft"]
TRAIL_UNI = {"ff": 0x66, "ffe": 0x66, "fi": 0x131, "fl": 0x6C, "ft": 0x74}

# ---------- parse drawings ----------
def parse(path):
    root = ET.parse(path).getroot(); el = {}; anon = []
    def w(e, gid=None):
        for c in e:
            i = c.get("id") or gid
            if c.tag.split('}')[-1] == "path" and c.get("d"):
                rp = RecordingPen(); parse_path(c.get("d"), rp)
                if i: el[i] = rp.value
                anon.append((c.get("class"), rp.value))
            w(c, c.get("id") or gid)
    w(root); return el, anon
oldE, _ = parse(OLD); _, newA = parse(NEW)
def fy(v, b): return [(c, tuple((x, b-y) for x, y in p)) for c, p in v]
def mnx(v): return min(x for c, p in v for x, y in p)
def mxx(v): return max(x for c, p in v for x, y in p)
def sh(v, dx): return [(c, tuple((x+dx, y) for x, y in p)) for c, p in v]
def subpaths(v):
    o = []; cur = []
    for c, p in v:
        if c == "moveTo" and cur: o.append(cur); cur = []
        cur.append((c, p))
    if cur: o.append(cur)
    return o

KLAR_ID = {"ff": "r0-ff-standard", "ffe": "r0-ff-wortende", "fi": "r0-fi-weit", "fl": "r0-fl", "ft": "r0-ft"}
LEISE_ID = {"ff": ["r3-f", "r3-f1"], "ffe": ["r3-f2", "r3-f3"], "fi": ["r3-f4", "r3-dotlessi"],
            "fl": ["r3-f5", "r3-l"], "ft": ["r3-f6", "r3-t"]}
def klar_parts(k):
    s = sorted(subpaths(fy(oldE[KLAR_ID[k]], 859.5)), key=mnx)
    return [s[0]] + [sum(s[1:], [])]
def leise_parts(k):
    lid, tid = LEISE_ID[k]; lead = fy(oldE[lid], 5359.5); trail = fy(oldE[tid], 5359.5)
    off = mnx(lead); return [sh(lead, -off), sh(trail, -off)]
# new Laut: black st5 paths grouped into 5 columns
_blk = sorted([fy(v, 772.9) for cls, v in newA if cls == "st5"], key=mnx)
def _col(x): return 0 if x < 1100 else 1 if x < 2110 else 2 if x < 3000 else 3 if x < 3975 else 4
_cols = {i: [] for i in range(5)}
for v in _blk: _cols[_col(mnx(v))].append(v)
def laut_parts(k):
    idx = KEYS.index(k); parts = sorted(_cols[idx], key=mnx)
    return [parts[0], sum(parts[1:], [])]
SRC = {"Leise": leise_parts, "Klar": klar_parts, "Laut": laut_parts}

# ---------- GSUB appenders (append, do not rebuild) ----------
def add_ligature_subst(ft, tag, mapping):
    """mapping: {(comp1,comp2,...): lig}  -> appended GSUB type-4 feature."""
    from fontTools.otlLib.builder import buildLigatureSubstSubtable, buildLookup
    g = ft["GSUB"].table
    sub = buildLigatureSubstSubtable(mapping)
    g.LookupList.Lookup.append(buildLookup([sub], flags=0))
    g.LookupList.LookupCount = len(g.LookupList.Lookup)
    return g.LookupList.LookupCount - 1

def add_single_lookup(ft, mapping):
    from fontTools.otlLib.builder import buildSingleSubstSubtable, buildLookup
    g = ft["GSUB"].table
    g.LookupList.Lookup.append(buildLookup([buildSingleSubstSubtable(mapping)], flags=0))
    g.LookupList.LookupCount = len(g.LookupList.Lookup)
    return g.LookupList.LookupCount - 1

def add_chain_calt(ft, input_gname, lookahead_gnames, sub_lookup_idx):
    """Append a calt feature: input' lookahead -> apply sub_lookup_idx on input."""
    from fontTools.ttLib.tables import otTables as ot
    from fontTools.otlLib.builder import buildLookup, buildCoverage
    st = ot.ChainContextSubst(); st.Format = 3
    st.BacktrackGlyphCount = 0; st.BacktrackCoverage = []
    st.InputGlyphCount = 1; st.InputCoverage = [buildCoverage([input_gname], ft.getReverseGlyphMap())]
    st.LookAheadGlyphCount = 1; st.LookAheadCoverage = [buildCoverage(lookahead_gnames, ft.getReverseGlyphMap())]
    rec = ot.SubstLookupRecord(); rec.SequenceIndex = 0; rec.LookupListIndex = sub_lookup_idx
    st.SubstCount = 1; st.SubstLookupRecord = [rec]
    g = ft["GSUB"].table
    g.LookupList.Lookup.append(buildLookup([st], flags=0))
    g.LookupList.LookupCount = len(g.LookupList.Lookup)
    return g.LookupList.LookupCount - 1

def register_feature(ft, tag, lookup_idx):
    from fontTools.ttLib.tables import otTables as ot
    g = ft["GSUB"].table
    feat = ot.Feature(); feat.FeatureParams = None; feat.LookupListIndex = [lookup_idx]; feat.LookupCount = 1
    fr = ot.FeatureRecord(); fr.FeatureTag = tag; fr.Feature = feat
    g.FeatureList.FeatureRecord.append(fr)
    g.FeatureList.FeatureCount = len(g.FeatureList.FeatureRecord)
    fidx = g.FeatureList.FeatureCount - 1
    for sr in g.ScriptList.ScriptRecord:
        s = sr.Script
        for ls in ([s.DefaultLangSys] if s.DefaultLangSys else []) + [r.LangSys for r in s.LangSysRecord]:
            ls.FeatureIndex.append(fidx); ls.FeatureCount = len(ls.FeatureIndex)

# ---------- glyph injection ----------
def add_outline_glyph(ft, recv, adv, lsb):
    cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
    cs = _charstring(ft, recv, adv)
    cids = [int(n[3:]) for n in td.charset if re.fullmatch(r"cid\d+", n)]
    name = "cid%05d" % (max(cids) + 1)
    td.CharStrings.charStringsIndex.append(cs)
    td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
    td.charset.append(name)
    if hasattr(td, "FDSelect"): td.FDSelect.append(0)
    ft["hmtx"].metrics[name] = (int(round(adv)), int(round(lsb)))
    ft.setGlyphOrder(list(td.charset))
    return name

def inject(cut, path, outpath):
    ft = TTFont(path); cmap = ft.getBestCmap()
    fr, fa = grec(ft, 0x66); f_lsb = mnx(fr)
    fn = {u: cmap[u] for u in (0x66, 0x69, 0x6C, 0x74)}
    parts_of = SRC[cut]; lig = {}
    for k in KEYS:
        parts = parts_of(k)
        ink = [c for rec in parts for c in rec]
        gmin = mnx(ink); gmax = mxx(ink)
        recv = [sh(rec, -gmin + f_lsb) for rec in parts]      # ink-left at the f's LSB
        tr, ta = grec(ft, TRAIL_UNI[k]); trail_rsb = ta - max(x for c, p in tr for x, y in p)
        width = (gmax - gmin); adv = f_lsb + width + trail_rsb
        flat = [c for rec in recv for c in rec]
        lig[k] = add_outline_glyph(ft, flat, adv, f_lsb)
    # GSUB: liga + calt
    liga = {(fn[0x66], fn[0x66]): lig["ff"], (fn[0x66], fn[0x69]): lig["fi"],
            (fn[0x66], fn[0x6C]): lig["fl"], (fn[0x66], fn[0x74]): lig["ft"]}
    li = add_ligature_subst(ft, "liga", liga); register_feature(ft, "liga", li)
    # calt: f_f' [space/punct] -> f_f.alt  (Wortende)
    bnd = [cmap[u] for u in (0x20, 0x2C, 0x2E, 0x3B, 0x3A, 0x21, 0x3F, 0x29, 0x2013, 0x2014, 0x00BB) if u in cmap]
    sl = add_single_lookup(ft, {lig["ff"]: lig["ffe"]})
    cl = add_chain_calt(ft, lig["ff"], bnd, sl); register_feature(ft, "calt", cl)
    ft.save(outpath)
    return lig

if __name__ == "__main__":
    OUT = "/tmp/v25cuts"; os.makedirs(OUT, exist_ok=True)
    for cut in ["Leise", "Klar", "Laut"]:
        src = glob.glob(os.path.join(REPO, "assets/fonts/goetheanum/**/*v2.4.1-%s.otf" % cut), recursive=True)[0]
        out = os.path.join(OUT, "Goetheanum-Schrift-v2.5-%s.otf" % cut)
        names = inject(cut, src, out)
        print("  %s -> %s  (%s)" % (cut, os.path.basename(out), ", ".join("%s=%s" % (k, names[k]) for k in KEYS)))
    print("done")
