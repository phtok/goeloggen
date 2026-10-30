#!/usr/bin/env python3
# Repariert den Variable Font (Befund 29. 10. 2026 in AUDIT.md): Glyphen, deren
# Konturen über die Achse wght 190–725 kreuzen, starr stehen oder deren
# Vorschub springt. Prinzip – die gesunden Glyphen der Familie zeigen es: jeder
# innere Master (335 · 420 · 440 · 600) ist bis auf < 1 Einheit die lineare
# Mischung der beiden Endmaster 190 und 725, mit festen Faktoren t (≈ 0,27 ·
# 0,43 · 0,46 · 0,76; hier aus a–z A–Z gemessen, nicht eingetippt). Eine
# beschädigte Glyphe wird darum aus ihren zwei heilen Ankern neu als Blend
# gebaut:
#   kreuzend   (« » „ ‚ ÷ ◊ % Ű, Kapitälchen ű, Null mit Strich): die Endmaster
#              sind je für sich heil, aber Konturreihenfolge, Startpunkt oder
#              Drehsinn passen nicht zusammen → 725 auf die Ordnung von 190
#              bringen, Innenmaster aus t.
#   halb starr (Ą Į $ ab Klar; Kapitälchen å ą į ŋ ab Ruhig): 190 und Klar
#              sind heil → 725 = 190 + (Klar − 190) / t(440), Innenmaster aus t.
#   oben flach (beim Prüflauf über alle Glyphen gefunden: € ǿ und die
#              Kapitälchen m y ñ ý ÿ ħ ń ň ŧ ŷ ž ǿ): 725 bleibt fast beim Wert
#              von Deutlich stehen; 190 bis Deutlich sind heil → wie halb starr.
#   Û, Kapitälchen û (ebenfalls beim Durchlauf gefunden): der Zirkumflex steht
#              schon in Klar 83 Einheiten links und 90 zu hoch, in Schreien
#              weit daneben → neu gesetzt aus U plus dem Zirkumflex von Ô, je
#              Master um die Mittendifferenz U/O versetzt.
#   Kapitälchen ǻ: bis Klar starr, darüber kreuzend → neu gesetzt aus dem
#              reparierten Kapitälchen-å plus Akut (wie repair_smallcap_01FA.py).
#   starr      (case-Formen von ¿ ¡ – — · ( ) [ ] { }): Kontur für Kontur von
#              der Grundform abgeleitet (gleiche Form, fester Versatz).
#   •          aus dem Punkt: wächst je Master um so viel wie der Punkt.
#   ⁄          Vorschub klein und mit dem Gewicht wachsend wie in v1.4.43
#              (dort 6 · 19 · 36), statt 600 · … · 17 · … · 54.
# Jede Reparatur ist eine Funktion der Anker, die sie selbst nicht verändert –
# darum idempotent: ein zweiter Lauf schreibt dieselben Zahlen.
# Aufruf:  python3 repair_variable_v28.py [Pfad-zur-Variable.otf]
import os, sys, glob, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.cffLib.specializer import specializeCommands, commandsToProgram
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VARDIR = os.path.join(REPO, "assets/fonts/goetheanum/Variable")

CROSSED = [0x00AB, 0x00BB, 0x201E, 0x201A, 0x00F7, 0x25CA, 0x0025, 0x0170,
           ("smcp", 0x0171), ("zero", 0x0030)]
HALF_RIGID = [0x0104, 0x012E, 0x0024, ("smcp", 0x00E5), ("smcp", 0x0105),
              ("smcp", 0x012F), ("smcp", 0x014B)]
FLAT_TOP = [0x20AC, 0x01FF] + [("smcp", ord(c)) for c in "myñýÿħńňŧŷžǿ"]
ACCENT = [(0x00DB, 0x0055, 0x00D4, 0x004F),     # Ziel, Grundform, Spender, dessen Grundform
          (("smcp", 0x00FB), ("smcp", 0x0075), ("smcp", 0x00F4), ("smcp", 0x006F))]
RING_ACUTE = ("smcp", 0x01FB)                   # ǻ: bis Klar starr, darüber kreuzend
GAP = 28                                        # Akut über dem Ring, wie repair_smallcap_01FA.py
CASE = [0x00BF, 0x00A1, 0x2013, 0x2014, 0x00B7, 0x0028, 0x0029, 0x005B,
        0x005D, 0x007B, 0x007D]
BULLET, PERIOD, FRACTION = 0x2022, 0x002E, 0x2044
FRACTION_ADV = (4, 17)                          # Vorschub bei 190 und Klar (440)


# ---------- Lesen: Master-Umrisse ----------
class VF:
    def __init__(s, ft):
        s.ft = ft; s.cmap = ft.getBestCmap()
        td = ft["CFF2"].cff.topDictIndex[0]; s.cs = td.CharStrings
        vs = td.VarStore.otVarStore
        s.regions = [r.VarRegionAxis[0] for r in vs.VarRegionList.Region]
        s.regions = [(a.StartCoord, a.PeakCoord, a.EndCoord) for a in s.regions]
        s.peaks = [r[1] for r in s.regions]
        assert [len(d.VarRegionIndex) for d in vs.VarData] == [len(s.regions)], \
            "erwartet genau ein VarData über alle Regionen"
        # Master-Reihenfolge hier: 190, …, Klar (Default), …, 725
        s.locs = sorted(s.peaks + [0.0])

    @staticmethod
    def scalar(r, v):
        a, p, b = r
        if v == p: return 1.0
        if v <= a or v >= b: return 0.0
        return (v - a) / (p - a) if v < p else (b - v) / (b - p)

    def outline(s, g, v):
        sc = [s.scalar(r, v) for r in s.regions]
        pen = RecordingPen()
        s.cs[g].draw(pen, blender=lambda vsi, d: sum(x * y for x, y in zip(sc, d)))
        return contours(pen.value)

    def masters(s, g):
        # auf ganze Einheiten: so liest ein zweiter Lauf exakt dieselben Anker
        return [mapc(s.outline(g, v), lambda p: (round(p[0]), round(p[1]))) for v in s.locs]

    def glyph(s, key):
        if isinstance(key, tuple) and isinstance(key[1], str):
            return gsub_liga(s.ft, [s.cmap[ord(c)] for c in key[1]], key[0])
        if isinstance(key, tuple):
            feat, cp = key; return gsub_single(s.ft, s.cmap[cp], feat)
        return s.cmap[key]


def gsub_single(ft, src, feat):
    gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != feat: continue
        for li in fr.Feature.LookupListIndex:
            L = gsub.LookupList.Lookup[li]
            for st in L.SubTable:
                if L.LookupType == 7: st = st.ExtSubTable
                if hasattr(st, "mapping") and src in st.mapping:
                    return st.mapping[src]
    raise KeyError("%s: keine %s-Form" % (src, feat))


def gsub_liga(ft, comps, feat):
    gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != feat: continue
        for li in fr.Feature.LookupListIndex:
            L = gsub.LookupList.Lookup[li]
            for st in L.SubTable:
                if L.LookupType == 7: st = st.ExtSubTable
                for l in getattr(st, "ligatures", {}).get(comps[0], []):
                    if l.Component == comps[1:]: return l.LigGlyph
    raise KeyError("%s: keine %s-Ligatur" % ("+".join(comps), feat))


# Kontur = (start, [(op, [punkte…]), …]); das letzte Segment endet im Start.
def contours(rec):
    out = []; start = cur = None
    for op, a in rec:
        if op == "moveTo": start = a[0]; cur = []; out.append([start, cur])
        elif op in ("closePath", "endPath"):
            last = cur[-1][1][-1] if cur else start
            cur.append(("lineTo", [start]))            # Schlusslinie immer explizit
        else: cur.append((op, list(a)))
    return out

def seg_ops(c): return [op for op, _ in c[1]]
def points(c): return [c[0]] + [p for _, ps in c[1] for p in ps]
def ends(c): return [ps[-1] for _, ps in c[1]]

def signed_area(c):
    p = AreaPen(); p.moveTo(c[0])
    for op, ps in c[1]: getattr(p, op)(*ps)
    p.closePath(); return p.value

def rotate(c, k):
    segs = c[1][k:] + c[1][:k]
    start = c[1][k - 1][1][-1]
    return [start, segs]

def reverse(c):
    nodes = [c[0]] + ends(c)                     # nodes[i] → nodes[i+1] über segs[i]
    segs = []
    for i in range(len(c[1]) - 1, -1, -1):
        op, ps = c[1][i]
        ctrl = ps[:-1][::-1]
        segs.append((op, ctrl + [nodes[i]]))
    return [nodes[-1], segs]

def bbox(c):
    P = points(c); xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return min(xs), min(ys), max(xs), max(ys)

def shape_cost(a, b):
    """Abstand zweier Konturen nach Lage- und Grössenausgleich (gewichtsneutral)."""
    def nrm(c):
        x0, y0, x1, y1 = bbox(c); w = max(x1 - x0, 1); h = max(y1 - y0, 1)
        return [((p[0] - x0) / w, (p[1] - y0) / h) for p in points(c)[1:]]
    return sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(nrm(a), nrm(b)))

def align_contour(ref, c):
    """c so drehen/umkehren, dass Startpunkt, Laufsinn und Segmentfolge zu ref passen."""
    best = None
    for cand in (c, reverse(c)):
        if (signed_area(cand) > 0) != (signed_area(ref) > 0): continue
        for k in range(len(cand[1])):
            r = rotate(cand, k)
            if seg_ops(r) != seg_ops(ref): continue
            cost = shape_cost(ref, r)
            if best is None or cost < best[0]: best = (cost, r)
    if best is None: raise ValueError("Kontur nicht zuordenbar")
    return best[1]

def align_glyph(ref, other):
    """other (Konturenliste) in Konturfolge, Startpunkte, Laufsinn von ref bringen."""
    n = len(ref); assert len(other) == n
    def bcost(a, b):
        if sorted(seg_ops(a)) != sorted(seg_ops(b)): return 1e9
        A, B = bbox(a), bbox(b)
        return abs((A[0] + A[2]) - (B[0] + B[2])) + abs((A[1] + A[3]) - (B[1] + B[3])) + \
            abs((A[2] - A[0]) - (B[2] - B[0])) + abs((A[3] - A[1]) - (B[3] - B[1]))
    perm = min(itertools.permutations(range(n)),
               key=lambda p: sum(bcost(ref[i], other[p[i]]) for i in range(n)))
    return [align_contour(ref[i], other[perm[i]]) for i in range(n)]


# ---------- Rechnen ----------
def flat(cs): return [v for c in cs for p in points(c) for v in p]

def mix(a, b, t):
    """Konturen a, b (gleiche Struktur) linear mischen."""
    out = []
    for ca, cb in zip(a, b):
        start = tuple(x + t * (y - x) for x, y in zip(ca[0], cb[0]))
        segs = [(op, [tuple(x + t * (y - x) for x, y in zip(p, q)) for p, q in zip(pa, pb)])
                for (op, pa), (_, pb) in zip(ca[1], cb[1])]
        out.append([start, segs])
    return out

def mapc(cs, fn):
    return [[fn(c[0]), [(op, [fn(p) for p in ps]) for op, ps in c[1]]] for c in cs]

def measure_t(vf):
    """Mischfaktor je Master aus den gesunden Grundbuchstaben (kleinste Quadrate)."""
    gl = [vf.cmap[ord(ch)] for ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    t = []
    for v in vf.locs:
        num = den = 0.0
        for g in gl:
            A, M, B = flat(vf.outline(g, -1.0)), flat(vf.outline(g, v)), flat(vf.outline(g, 1.0))
            for a, m, b in zip(A, M, B): num += (b - a) * (m - a); den += (b - a) ** 2
        t.append(num / den)
    return t


# ---------- Schreiben: Blend-Charstring ----------
def solve(vf, vals):
    """Masterwerte (in vf.locs-Ordnung) → [Default, Delta je Region]."""
    d0 = vals[vf.locs.index(0.0)]
    order = [vf.locs.index(p) for p in vf.peaks]
    n = len(vf.regions)
    S = [[vf.scalar(vf.regions[r], vf.peaks[i]) for r in range(n)] for i in range(n)]
    rhs = [vals[order[i]] - d0 for i in range(n)]
    # Gauss mit Pivotsuche (5×5)
    M = [row[:] + [rhs[i]] for i, row in enumerate(S)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col])); M[col], M[piv] = M[piv], M[col]
        for r in range(n):
            if r != col and M[r][col]:
                f = M[r][col] / M[col][col]
                M[r] = [x - f * y for x, y in zip(M[r], M[col])]
    d = [M[i][n] / M[i][i] for i in range(n)]
    return [d0] + d

def blend_arg(vf, vals):
    q = [round(x, 2) for x in solve(vf, vals)]
    q = [int(x) if x == int(x) else x for x in q]
    return q[0] if not any(q[1:]) else q + [1]      # Blend-Argument: Default, Deltas, 1

def write_glyph(vf, g, masters):
    """masters: Konturlisten je vf.locs, gleiche Struktur → CFF2-Programm."""
    ref = masters[0]
    for m in masters[1:]:
        assert [seg_ops(c) for c in m] == [seg_ops(c) for c in ref], g
    rnd = lambda cs: mapc(cs, lambda p: (round(p[0]), round(p[1])))
    masters = [rnd(m) for m in masters]
    cmds = []
    prev = [(0.0, 0.0)] * len(masters)
    for ci in range(len(ref)):
        segs = ref[ci][1]
        if segs and segs[-1][0] == "lineTo": segs_used = len(segs) - 1   # Schluss implizit
        else: segs_used = len(segs)
        def rel(pt_of):
            args = []
            for axis in (0, 1):
                vals = [pt_of(mi)[axis] - prev[mi][axis] for mi in range(len(masters))]
                args.append(blend_arg(vf, vals))
            return args
        start = lambda mi: masters[mi][ci][0]
        cmds.append(("rmoveto", rel(start)))
        prev = [start(mi) for mi in range(len(masters))]
        for si in range(segs_used):
            op = segs[si][0]; args = []
            for pi in range(len(segs[si][1])):
                pt = lambda mi: masters[mi][ci][1][si][1][pi]
                args += rel(pt); prev = [pt(mi) for mi in range(len(masters))]
            cmds.append(({"lineTo": "rlineto", "curveTo": "rrcurveto"}[op], args))
    cmds = specializeCommands(cmds, generalizeFirst=False, maxstack=513)
    c = vf.cs[g]
    c.program = commandsToProgram(cmds); c.bytecode = None


# ---------- Reparaturen ----------
def repair_crossed(vf, t, g):
    ms = vf.masters(g); A = ms[0]
    B = align_glyph(A, ms[-1])
    return [mix(A, B, ti) for ti in t]

def repair_half_rigid(vf, t, g):
    ms = vf.masters(g); di = vf.locs.index(0.0); A, D = ms[0], ms[di]
    B = mix(A, D, 1.0 / t[di])                   # 725 = 190 + (Klar − 190) / t(Klar)
    return [mix(A, B, ti) for ti in t]

def repair_composed_ring_acute(vf, t, g, ring_sc, acute):
    """Kapitälchen ǻ wie in repair_smallcap_01FA.py: Kapitälchen-å (repariert) plus
    Akut, mittig und GAP über dem Ring – je Master gesetzt."""
    out = []
    for A, C in zip(ring_sc, vf.masters(acute)):
        ax = [bbox(c) for c in A]; cx = [bbox(c) for c in C]
        ax0, ax1, ay1 = min(b[0] for b in ax), max(b[2] for b in ax), max(b[3] for b in ax)
        cx0, cx1, cy0 = min(b[0] for b in cx), max(b[2] for b in cx), min(b[1] for b in cx)
        dx = (ax0 + ax1) / 2 - (cx0 + cx1) / 2; dy = ay1 + GAP - cy0
        out.append(A + mapc(C, lambda p, dx=dx, dy=dy: (p[0] + dx, p[1] + dy)))
    return out

def repair_accent(vf, t, base, donor, donor_base):
    """Grundform + Akzent des Spenders, je Master um die Mittendifferenz der
    Grundformen waagrecht versetzt (die Höhe des Akzents bleibt die des Spenders)."""
    di = vf.locs.index(0.0)
    bm, dm, dbm = vf.masters(base), vf.masters(donor), vf.masters(donor_base)
    top = max(bbox(c)[3] for c in dbm[di])
    marks = [i for i, c in enumerate(dm[di]) if bbox(c)[1] > top - 60]
    assert marks and len(dm[di]) - len(marks) == len(dbm[di]), donor
    cx = lambda cs: (min(bbox(c)[0] for c in cs) + max(bbox(c)[2] for c in cs)) / 2
    out = []
    for B, D, DB in zip(bm, dm, dbm):
        dx = cx(B) - cx(DB)
        out.append(B + mapc([D[i] for i in marks], lambda p, dx=dx: (p[0] + dx, p[1])))
    return out

def repair_case(vf, t, g, base):
    """Starre case-Form: Grundform je Master, um den festen Versatz der case-Form
    (Mitte zu Mitte, am Default gemessen) verschoben. Vorschub-Variation (HVAR)
    wie die Grundform."""
    di = vf.locs.index(0.0)
    tm, bm = vf.masters(g), vf.masters(base)
    def centre(cs):
        b = [bbox(c) for c in cs]
        return ((min(q[0] for q in b) + max(q[2] for q in b)) / 2,
                (min(q[1] for q in b) + max(q[3] for q in b)) / 2)
    (tx, ty), (bx, by) = centre(tm[di]), centre(bm[di])
    dx, dy = round(tx - bx), round(ty - by)
    pick = []
    for c in tm[di]:
        best = None
        for bi, bc in enumerate(bm[di]):
            for k in range(len(bc[1])):
                cand = rotate(bc, k)
                if seg_ops(cand) != seg_ops(c): continue
                cost = sum(abs(p[0] - q[0] - dx) + abs(p[1] - q[1] - dy)
                           for p, q in zip(points(c), points(cand)))
                if best is None or cost < best[0]: best = (cost, bi, k)
        if best is None: raise ValueError("%s: Kontur ohne Gegenstück in %s" % (g, base))
        pick.append(best[1:])
    assert sorted(bi for bi, _ in pick) == list(range(len(bm[di]))), g
    hv = vf.ft["HVAR"].table.AdvWidthMap.mapping
    hv[g] = hv[base]
    return [mapc([rotate(bm[mi][bi], k) for bi, k in pick], lambda p: (p[0] + dx, p[1] + dy))
            for mi in range(len(vf.locs))]

def repair_bullet(vf, t, g, period):
    """• wächst je Master um so viel wie der Punkt (Breite und Höhe), um seine Mitte."""
    di = vf.locs.index(0.0)
    D = vf.masters(g)[di]; bx = [bbox(c) for c in D]
    X0, Y0 = min(b[0] for b in bx), min(b[1] for b in bx)
    X1, Y1 = max(b[2] for b in bx), max(b[3] for b in bx)
    cx, cy, W, H = (X0 + X1) / 2, (Y0 + Y1) / 2, X1 - X0, Y1 - Y0
    def pdim(cs):
        b = [bbox(c) for c in cs]
        return max(q[2] for q in b) - min(q[0] for q in b), max(q[3] for q in b) - min(q[1] for q in b)
    pD = pdim(vf.outline(period, 0.0)); out = []
    for v in vf.locs:
        pw, ph = pdim(vf.outline(period, v))
        sx, sy = (W + pw - pD[0]) / W, (H + ph - pD[1]) / H
        out.append(mapc(D, lambda p, sx=sx, sy=sy: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy)))
    return out

def repair_fraction_advance(vf, t, g):
    """⁄: Vorschub 190 → Klar wie FRACTION_ADV, darüber mit t fortgeschrieben (HVAR)."""
    ft = vf.ft; di = vf.locs.index(0.0)
    a0, aD = FRACTION_ADV; aB = a0 + (aD - a0) / t[di]
    vals = [a0 + ti * (aB - a0) for ti in t]
    d = solve(vf, vals)
    hv = ft["HVAR"].table; store = hv.VarStore
    # eigene Zeile, damit keine andere Glyphe mitwandert
    vd_index = next(i for i, vd in enumerate(store.VarData) if len(vd.VarRegionIndex) == len(vf.regions))
    vd = store.VarData[vd_index]
    regions = vd.VarRegionIndex
    row = [int(round(d[1 + r])) for r in regions]
    mapped = hv.AdvWidthMap.mapping.get(g)
    others = [k for k, v in hv.AdvWidthMap.mapping.items() if v == mapped and k != g]
    if mapped is not None and (mapped >> 16) == vd_index and not others:
        vd.Item[mapped & 0xFFFF] = row
    else:
        vd.Item.append(row); vd.ItemCount = len(vd.Item)
        hv.AdvWidthMap.mapping[g] = (vd_index << 16) | (len(vd.Item) - 1)
    lsb = ft["hmtx"][g][1]
    ft["hmtx"][g] = (int(round(d[0])), lsb)
    return [round(v, 1) for v in vals]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(VARDIR, "Goetheanum-Variabel-v*.otf")))[-1]
    ft = TTFont(path, recalcTimestamp=False); vf = VF(ft)
    t = measure_t(vf)
    print("Mischfaktoren je Master", [round(unnorm(v)) for v in vf.locs], [round(x, 3) for x in t])
    todo = []
    for k in CROSSED: todo.append((vf.glyph(k), "kreuzend", repair_crossed))
    for k in HALF_RIGID: todo.append((vf.glyph(k), "halb starr", repair_half_rigid))
    for k in FLAT_TOP: todo.append((vf.glyph(k), "oben flach", repair_half_rigid))
    results = {}
    for g, kind, fn in todo:
        results[g] = (kind, fn(vf, t, g))
    for k, b, d, db in ACCENT:
        results[vf.glyph(k)] = ("Akzent neu", repair_accent(vf, t, vf.glyph(b), vf.glyph(d), vf.glyph(db)))
    ring = results[vf.glyph(("smcp", 0x00E5))][1]
    results[vf.glyph(RING_ACUTE)] = ("Ring + Akut",
        repair_composed_ring_acute(vf, t, vf.glyph(RING_ACUTE), ring, vf.cmap[0x00B4]))
    for cp in CASE:
        base = vf.cmap[cp]; g = gsub_single(ft, base, "case")
        results[g] = ("case", repair_case(vf, t, g, base))
    results[vf.cmap[BULLET]] = ("aus dem Punkt", repair_bullet(vf, t, vf.cmap[BULLET], vf.cmap[PERIOD]))
    # erst alles messen, dann schreiben (die Reparaturen lesen den alten Stand)
    for g, (kind, masters) in results.items():
        write_glyph(vf, g, masters)
        print("  %-9s %-12s" % (g, kind))
    adv = repair_fraction_advance(vf, t, vf.cmap[FRACTION])
    print("  %-9s Vorschub je Master %s" % (vf.cmap[FRACTION], adv))
    ft.save(path)
    wf = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
    base = os.path.splitext(os.path.basename(path))[0]
    if os.path.dirname(os.path.abspath(path)) == VARDIR:         # nur die ausgelieferte Datei
        for flv in ("woff", "woff2"):
            w = TTFont(path); w.flavor = flv; w.save(os.path.join(wf, flv, "%s.%s" % (base, flv)))
    print("Variable repariert:", os.path.relpath(path, REPO))

def unnorm(v): return 440 + v * 250 if v < 0 else 440 + v * 285

if __name__ == "__main__":
    main()
