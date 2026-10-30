#!/usr/bin/env python3
# Repariert den Variable Font (Befund 29. 10. 2026 in AUDIT.md): Glyphen, deren
# Konturen über die Achse wght 190–725 kreuzen, starr stehen oder deren
# Vorschub springt. Prinzip – die gesunden Glyphen der Familie zeigen es: jeder
# innere Master (335 · 420 · 440 · 600) ist bis auf < 1 Einheit die lineare
# Mischung der beiden Endmaster 190 und 725, mit festen Faktoren t (≈ 0,27 ·
# 0,43 · 0,46 · 0,76; hier aus a–z A–Z gemessen, nicht eingetippt). Eine
# beschädigte Glyphe wird darum aus ihren zwei heilen Ankern neu als Blend
# gebaut:
#   kreuzend   (« » „ ‚ ÷ ◊ % Ű, Null mit Strich): die Endmaster
#              sind je für sich heil, aber Konturreihenfolge, Startpunkt oder
#              Drehsinn passen nicht zusammen → 725 auf die Ordnung von 190
#              bringen, Innenmaster aus t.
#   halb starr (Ą Į $ ab Klar): 190 und Klar sind heil →
#              725 = 190 + (Klar − 190) / t(440), Innenmaster aus t.
#   Kapitälchen å ŋ (zweite Prüfung, 30. 10. 2026): in der Variable ab Klar
#              zu leicht. Die statischen Schnitte Leise und Klar der
#              v1.4.43-Linie tragen sie gesund (Laut ist von derselben Klemme
#              betroffen) → 190 und 725 aus diesen zwei Stützstellen.
#   Kapitälchen q &: in Flüstern zu schwer; Klar und Deutlich sind heil →
#              190 und 725 aus diesen zwei Mastern.
#   Kapitälchen ű: neu aus Kapitälchen u plus dem Doppelakut des
#              Kapitälchen-ő (wie Û).
#   Kapitälchen ą į: in beiden Linien ab Klar zu leicht oder starr → neu aus
#              Kapitälchen a bzw. i plus dem Ogonek ˛ der Schrift, gesetzt wie
#              bei ą bzw. į (Abstand zum rechten Rand und Tiefe je Master).
#   oben flach (€ Å Ǻ Ŋ ẞ, alle Kapitälchen und Kurzziffern): 725 bleibt fast
#              beim Wert von Deutlich stehen; 190 bis Deutlich sind heil → wie
#              halb starr. Ursache bei Kapitälchen/Kurzziffern: build.py nimmt
#              die Versalie/Ziffer bei Gewicht +110 bzw. +80 und verkleinert
#              sie, klemmt das Gewicht aber auf min(725, …) – oberhalb Deutlich
#              entsteht so fast dieselbe Form. Das kalibrierte Modell bleibt,
#              nur die Klemme fällt. Für Kapitälchen und Kurzziffern greift die
#              Regel selbsttätig, wo 190–600 auf der Mischgeraden liegen und
#              725 davon abweicht.
#   Ø ø Ǿ ǿ, Kapitälchen ø ǿ: der Schrägstrich ist in die Kontur des O
#              eingeschnitten und wächst über die Achse nur auf das 1,9-Fache
#              (der Schrägstrich / auf das 3,7-Fache) – in Laut viel zu
#              dünn. Neu: das gesunde O/o plus ein eigener Strich in Lage und
#              Länge des alten, Strichstärke senkrecht 0,92 × Seitenstrich des
#              O, wie beim / (das Verhältnis wird je Master gemessen). Unter
#              dem Akut von Ǿ ǿ endet der Strich bündig mit dem O, sonst
#              stösst er in den fetten Schnitten an den Akzent.
#   Û, Kapitälchen û (ebenfalls beim Durchlauf gefunden): der Zirkumflex steht
#              schon in Klar 83 Einheiten links und 90 zu hoch, in Schreien
#              weit daneben → neu gesetzt aus U plus dem Zirkumflex von Ô, je
#              Master um die Mittendifferenz U/O versetzt.
#   Kapitälchen ǻ: bis Klar starr, darüber kreuzend → neu gesetzt aus dem
#              reparierten Kapitälchen-å plus dem Akut des Kapitälchen-á, mit
#              dessen Abstand über dem Ring.
#   starr      (case-Formen von ¿ ¡ – — · ( ) [ ] { }): Kontur für Kontur von
#              der Grundform abgeleitet (gleiche Form und Vorschub, fester
#              Versatz). Die Striche – — standen nur 30 Einheiten höher als im
#              Gemeinsatz, unter der Versalmitte; jetzt steht ihre Mitte auf dem
#              Querbalken des H (349, +82). Neu: case-Form des Bindestrichs
#              (- ‐ ‑ und weiches Trennzeichen), bisher fehlte sie.
#   « »        danach exakt aus zwei ‹ bzw. › gesetzt (» stand 5–8 Einheiten zu
#              hoch), mit der engen Lücke der Titillium-Extreme (38 in Flüstern,
#              51 in Schreien, dazwischen über t; Entscheid des Inhabers
#              30. 10. 2026 gegen die weite Lücke 84 der Auslieferung v1.4.43).
#   ‚ „        danach exakt ’ bzw. ” nach unten auf die Tiefe des Kommas
#              versetzt, die linke Kante bleibt (die v1.4.43 taugt hier nicht
#              als Vorbild, ihr ‚ ist ein Splitter).
#   •          bleibt bewusst starr: in jedem Schnitt dasselbe Quadrat wie in
#              Titillium und v1.4.43 (Entscheid des Inhabers 30. 10. 2026).
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
           ("zero", 0x0030)]
HALF_RIGID = [0x0104, 0x012E, 0x0024]
STATIC_FIT = [("smcp", ord(c)) for c in "åŋ"]
STATIC_SOURCE = ("4ee0d72", "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.7-%s.otf",
                 {"Leise": 265, "Klar": 440})   # Stand vor der Reparatur; Laut trägt die Klemme
TWO_MASTER = [("smcp", ord(c)) for c in "q&"]   # aus Klar (440) und Deutlich-Master (600)
SMALLCAP_FEATURES = ("smcp", "c2sc", "onum")
SLASH = [(0x00D8, 0x004F, None), (0x00F8, 0x006F, None),       # Ziel, Grundform, Lage des Strichs von
         (("smcp", 0x00F8), ("smcp", 0x006F), None),
         (0x01FE, 0x004F, 0x00D8), (0x01FF, 0x006F, 0x00F8),
         (("smcp", 0x01FF), ("smcp", 0x006F), ("smcp", 0x00F8))]
OGONEK = [(("smcp", 0x0105), ("smcp", 0x0061), 0x0105, 0x0061),   # Ziel, Grundform, Vorbild, dessen Grundform
          (("smcp", 0x012F), ("smcp", 0x0069), 0x012F, 0x0069)]
FLAT_TOP = [0x20AC, 0x00C5, 0x01FA, 0x014A, 0x1E9E]
ACCENT = [(0x00DB, 0x0055, 0x00D4, 0x004F),     # Ziel, Grundform, Spender, dessen Grundform
          (("smcp", 0x00FB), ("smcp", 0x0075), ("smcp", 0x00F4), ("smcp", 0x006F)),
          (("smcp", 0x0171), ("smcp", 0x0075), ("smcp", 0x0151), ("smcp", 0x006F))]
RING_ACUTE = ("smcp", 0x01FB)                   # ǻ: bis Klar starr, darüber kreuzend
ACUTE_SC = (("smcp", 0x00E1), ("smcp", 0x0061))  # Akut-Spender: Kapitälchen á über a
CASE = [0x00BF, 0x00A1, 0x2013, 0x2014, 0x00B7, 0x0028, 0x0029, 0x005B,
        0x005D, 0x007B, 0x007D, 0x002D]
CASE_DASH = (0x002D, 0x2013, 0x2014)            # Striche: zur Versalmitte gestellt
HYPHENS = (0x002D, 0x2010, 0x2011, 0x00AD)      # teilen sich die neue case-Form
GUILL = [(0x00AB, 0x2039), (0x00BB, 0x203A)]     # doppelt aus einfach
GUILL_GAP = (38, 51)                             # Lücke bei 190 und 725 (Titillium Thin/Bold)
LOWQ = [(0x201A, 0x2019), (0x201E, 0x201D)]      # tief aus hoch, auf Kommatiefe
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
        s.fixed = {}
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
        # schon reparierte Glyphen liefern ihre neuen Master (Bausteine für Komposita)
        if g in s.fixed: return s.fixed[g]
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

def bounds(cs):
    b = [bbox(c) for c in cs]
    return (min(q[0] for q in b), min(q[1] for q in b), max(q[2] for q in b), max(q[3] for q in b))

def repair_composed_ring_acute(vf, t, ring_sc, acute_src, acute_base):
    """Kapitälchen ǻ: Kapitälchen-å (repariert) plus der Akut des Kapitälchen-á,
    waagrecht auf den Ring gemittelt, mit dem Abstand, den er über dem a hat."""
    out = []
    for R, D, B in zip(ring_sc, vf.masters(acute_src), vf.masters(acute_base)):
        top = bounds(B)[3]
        acute = [c for c in D if bbox(c)[1] > top - 20]
        ring = [c for c in R if bbox(c)[1] > top - 60] or R
        rx0, _, rx1, ry1 = bounds(ring)
        ax0, ay0, ax1, _ = bounds(acute)
        dx = (rx0 + rx1) / 2 - (ax0 + ax1) / 2; dy = ry1 + (ay0 - top) - ay0
        out.append(R + mapc(acute, lambda p, dx=dx, dy=dy: (p[0] + dx, p[1] + dy)))
    return out

def static_masters(vf, t, key):
    """Kapitälchen aus den statischen Schnitten der v1.4.43-Linie (git-Stand vor
    der Reparatur): 190 und 725 per kleinste Quadrate auf der Mischgeraden."""
    import subprocess, io
    rev, pattern, cuts = STATIC_SOURCE
    def t_at(w):
        v = (w - 440) / 250 if w < 440 else (w - 440) / 285
        L = vf.locs
        for i in range(len(L) - 1):
            if L[i] <= v <= L[i + 1]:
                return t[i] + (t[i + 1] - t[i]) * (v - L[i]) / (L[i + 1] - L[i])
    samples = []
    for cut, w in cuts.items():
        blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, pattern % cut)],
                              capture_output=True, check=True).stdout
        f = TTFont(io.BytesIO(blob)); g = gsub_single(f, f.getBestCmap()[key[1]], key[0])
        pen = RecordingPen(); f.getGlyphSet()[g].draw(pen)
        samples.append((t_at(w), contours(pen.value)))
    ref = samples[-1][1]
    samples = [(tt, cs) for tt, cs in samples
               if [seg_ops(c) for c in cs] == [seg_ops(c) for c in ref]]
    n = len(samples); mt = sum(tt for tt, _ in samples) / n
    sxx = sum((tt - mt) ** 2 for tt, _ in samples)
    def fit(*pts):                                # ein Punkt je Schnitt → (190, 725)
        my = [sum(p[i] for p in pts) / n for i in (0, 1)]
        b = [sum((tt - mt) * (p[i] - my[i]) for (tt, _), p in zip(samples, pts)) / sxx for i in (0, 1)]
        a = [my[i] - b[i] * mt for i in (0, 1)]
        return (a[0], a[1]), (a[0] + b[0], a[1] + b[1])
    A = []; B = []
    for ci, c in enumerate(ref):
        sA = fit(*[cs[ci][0] for _, cs in samples]); sa, sb = sA
        segA, segB = [], []
        for si, (op, ps) in enumerate(c[1]):
            pa, pb = [], []
            for pi in range(len(ps)):
                a, b = fit(*[cs[ci][1][si][1][pi] for _, cs in samples]); pa.append(a); pb.append(b)
            segA.append((op, pa)); segB.append((op, pb))
        A.append([sa, segA]); B.append([sb, segB])
    return [mix(A, B, ti) for ti in t]

def repair_ogonek(vf, t, base, model, model_base):
    """Kapitälchen mit Ogonek: Grundform plus ˛, je Master so gesetzt wie das
    Ogonek im Vorbild (ą/į) zur rechten Kante seiner Grundform (a/i) steht."""
    ogo = vf.masters(vf.cmap[0x02DB])
    out = []
    for B, M, MB, O in zip(vf.masters(base), vf.masters(model), vf.masters(model_base), ogo):
        mp = [p for c in M for p in points(c) if p[1] < -20]          # Ogonek-Teil im Vorbild
        mx1, my0 = max(p[0] for p in mp), min(p[1] for p in mp)
        ox0, oy0, ox1, _ = bounds(O)
        dx = bounds(B)[2] + (mx1 - bounds(MB)[2]) - ox1; dy = my0 - oy0
        out.append(B + mapc(O, lambda p, dx=dx, dy=dy: (p[0] + dx, p[1] + dy)))
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

def flat_top_error(vf, t, g):
    """(Abweichung 335, 600, 725) von der Mischgeraden durch 190 und Klar."""
    ms = vf.masters(g); di = vf.locs.index(0.0)
    F = [flat(m) for m in ms]
    B = [a + (d - a) / t[di] for a, d in zip(F[0], F[di])]
    err = lambda i: max([abs(a + t[i] * (b - a) - x) for a, b, x in zip(F[0], B, F[i])] or [0])
    return err(1), err(len(t) - 2), err(len(t) - 1)

def feature_targets(ft, feats):
    out = set(); gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag not in feats: continue
        for li in fr.Feature.LookupListIndex:
            L = gsub.LookupList.Lookup[li]
            for st in L.SubTable:
                if L.LookupType == 7: st = st.ExtSubTable
                out.update(getattr(st, "mapping", {}).values())
    return sorted(out)

def repair_two_master(vf, t, g):
    """190 und 725 aus Klar (440) und dem Master bei 600, die heil sind."""
    ms = vf.masters(g); di = vf.locs.index(0.0); pi = len(t) - 2
    k = t[di] / (t[pi] - t[di])
    A = mix(ms[di], ms[pi], -k)                  # = D − t(D)·(P − D)/(t(P) − t(D))
    B = mix(A, ms[di], 1.0 / t[di])
    return [mix(A, B, ti) for ti in t]

def perp_width(c):
    """Senkrechte Strichstärke eines Parallelogramm-Strichs (/)."""
    P = points(c)[:4]
    d = (P[1][0] - P[0][0], P[1][1] - P[0][1]); L = (d[0] ** 2 + d[1] ** 2) ** 0.5
    o = (P[3][0] - P[0][0], P[3][1] - P[0][1])
    return abs(o[0] * d[1] - o[1] * d[0]) / L

def side_stem(cs):
    """Seitenstrich eines O: linke Innenkante minus linke Aussenkante."""
    outer = max(cs, key=lambda c: abs(signed_area(c)))
    inner = [c for c in cs if c is not outer]
    return min(bbox(c)[0] for c in inner) - bbox(outer)[0], outer

def repair_slash(vf, t, target, base, line_from=None):
    """Ø-Formen: gesundes O/o plus eigener Strich (Lage und Länge des alten,
    senkrechte Stärke wie beim / im Verhältnis zum Seitenstrich des O)."""
    tm = repair_half_rigid(vf, t, target)        # Akzente (Ǿ ǿ) mit gesundem Verlauf
    sm = vf.masters(vf.cmap[0x002F]); om = vf.masters(vf.cmap[0x004F])
    out = []
    lm = vf.masters(line_from) if line_from else tm
    for T, B, SL, O, LN in zip(tm, vf.masters(base), sm, om, lm):
        ratio = perp_width(SL[0]) / side_stem(O)[0]
        stem, outer = side_stem(B)
        x0, y0, x1, y1 = bounds(B)
        acute = [c for c in T if bbox(c)[1] > y1 + 20]
        P = {p for c in LN if bbox(c)[1] <= y1 + 20 for p in points(c)}
        lo = [p for p in P if p[1] < y0 - 5]; hi = [p for p in P if p[1] > y1 + 5]
        cb = (sum(p[0] for p in lo) / len(lo), sum(p[1] for p in lo) / len(lo))
        ct = (sum(p[0] for p in hi) / len(hi), sum(p[1] for p in hi) / len(hi))
        d = (ct[0] - cb[0], ct[1] - cb[1]); L = (d[0] ** 2 + d[1] ** 2) ** 0.5
        h = ratio * stem / 2; n = (-d[1] / L * h, d[0] / L * h)
        if acute:                                # unter dem Akzent endet der Strich bündig im O
            ytop = y1 - abs(n[1]); f = (ytop - cb[1]) / d[1]
            ct = (cb[0] + f * d[0], ytop)
        q = [(cb[0] - n[0], cb[1] - n[1]), (ct[0] - n[0], ct[1] - n[1]),
             (ct[0] + n[0], ct[1] + n[1]), (cb[0] + n[0], cb[1] + n[1])]
        slash = [q[0], [("lineTo", [q[1]]), ("lineTo", [q[2]]), ("lineTo", [q[3]]), ("lineTo", [q[0]])]]
        if (signed_area(slash) > 0) != (signed_area(outer) > 0): slash = reverse(slash)
        out.append(B + [slash] + acute)
    return out

def ensure_case_hyphen(ft):
    """Legt die case-Form des Bindestrichs an, falls sie fehlt (Kopie des
    Bindestrichs, die Lage setzt repair_case) und hängt - ‐ ‑ und das weiche
    Trennzeichen in die case-Ersetzung."""
    cmap = ft.getBestCmap(); hy = cmap[0x002D]
    gsub = ft["GSUB"].table
    sub = None
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != "case": continue
        for li in fr.Feature.LookupListIndex:
            for st in gsub.LookupList.Lookup[li].SubTable:
                if hasattr(st, "mapping"): sub = st
    if hy in sub.mapping: return sub.mapping[hy]
    td = ft["CFF2"].cff.topDictIndex[0]
    src = td.CharStrings[hy]; src.decompile()
    cs = type(src)(program=list(src.program), private=src.private, globalSubrs=src.globalSubrs)
    name = "cid%05d" % (max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1)
    td.CharStrings.charStringsIndex.append(cs)
    td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
    td.charset.append(name)
    if hasattr(td, "FDSelect") and td.FDSelect is not None: td.FDSelect.append(0)
    ft["hmtx"].metrics[name] = ft["hmtx"][hy]
    ft.setGlyphOrder(list(td.charset))
    hv = ft["HVAR"].table.AdvWidthMap.mapping; hv[name] = hv[hy]
    for cp in HYPHENS:
        if cp in cmap: sub.mapping[cmap[cp]] = name
    return name

def repair_case(vf, t, g, base, dash=False):
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
    dx, dy = 0, round(ty - by)                  # gleiche Form, gleicher Vorschub
    if dash:                                     # Mitte des Strichs auf den Querbalken des H
        Hc = vf.masters(vf.cmap[0x0048])[di]; top = bounds(Hc)[3]
        ys = {p[1] for c in Hc for p in points(c) if 10 < p[1] < top - 10}
        B = bounds(bm[di])
        dy = round(sum(ys) / len(ys) - (B[1] + B[3]) / 2)
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
    hv[g] = hv[base]; vf.ft["hmtx"][g] = vf.ft["hmtx"][base]
    if dash:                                     # der Strich ist eine Kontur: kein Suchen nötig
        pick = [(i, 0) for i in range(len(bm[di]))]
    return [mapc([rotate(bm[mi][bi], k) for bi, k in pick], lambda p: (p[0] + dx, p[1] + dy))
            for mi in range(len(vf.locs))]

def repair_bullet(vf, t, g, period):
    """• starr: in jedem Master die Form des Defaults (Quadrat wie Titillium)."""
    D = vf.masters(g)[vf.locs.index(0.0)]
    return [D for _ in vf.locs]

def t_at(vf, t, w):
    v = (w - 440) / 250 if w < 440 else (w - 440) / 285
    L = vf.locs
    for i in range(len(L) - 1):
        if L[i] <= v <= L[i + 1]:
            return t[i] + (t[i + 1] - t[i]) * (v - L[i]) / (L[i + 1] - L[i])

def advances(vf, g):
    """Vorschub je Master (hmtx + HVAR)."""
    hv = vf.ft["HVAR"].table; m = hv.AdvWidthMap.mapping[g]
    vd = hv.VarStore.VarData[m >> 16]; row = vd.Item[m & 0xFFFF]
    base = vf.ft["hmtx"][g][0]
    return [base + sum(vf.scalar(vf.regions[r], v) * d for r, d in zip(vd.VarRegionIndex, row))
            for v in vf.locs]

def set_advances(vf, g, vals):
    """Vorschub je Master über eine eigene HVAR-Zeile setzen."""
    ft = vf.ft; d = solve(vf, vals)
    hv = ft["HVAR"].table; store = hv.VarStore
    vd_index = next(i for i, vd in enumerate(store.VarData) if len(vd.VarRegionIndex) == len(vf.regions))
    vd = store.VarData[vd_index]
    row = [int(round(d[1 + r])) for r in vd.VarRegionIndex]
    mapped = hv.AdvWidthMap.mapping.get(g)
    others = [k for k, v in hv.AdvWidthMap.mapping.items() if v == mapped and k != g]
    if mapped is not None and (mapped >> 16) == vd_index and not others:
        vd.Item[mapped & 0xFFFF] = row
    else:
        vd.Item.append(row); vd.ItemCount = len(vd.Item)
        hv.AdvWidthMap.mapping[g] = (vd_index << 16) | (len(vd.Item) - 1)
    ft["hmtx"][g] = (int(round(d[0])), ft["hmtx"][g][1])

def guillemet_gap(vf, t):
    """Lücke zwischen den Winkeln von « je Master: linear über t zwischen den
    Titillium-Extremen."""
    a, b = GUILL_GAP
    return [a + ti * (b - a) for ti in t]

def repair_guillemet(vf, t, g, single, gaps):
    """« » aus zwei exakten Kopien von ‹ ›: erste an ihrem Ort, zweite um Breite +
    Lücke versetzt; der Vorschub wächst um denselben Versatz."""
    sm = vf.masters(single); out = []; offs = []
    for S, gap in zip(sm, gaps):
        x0, _, x1, _ = bounds(S); off = round(x1 - x0 + gap); offs.append(off)
        out.append(S + mapc(S, lambda p, off=off: (p[0] + off, p[1])))
    set_advances(vf, g, [a + o for a, o in zip(advances(vf, single), offs)])
    return out

def repair_low_quote(vf, t, g, high):
    """‚ „ = ’ ” nach unten auf die Tiefe des Kommas, linke Kante wie bisher."""
    out = []
    for T, H, C in zip(vf.masters(g), vf.masters(high), vf.masters(vf.cmap[0x002C])):
        dx = bounds(T)[0] - bounds(H)[0]; dy = bounds(C)[1] - bounds(H)[1]
        out.append(mapc(H, lambda p, dx=dx, dy=dy: (p[0] + dx, p[1] + dy)))
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
    ft = TTFont(path, recalcTimestamp=False)
    ensure_case_hyphen(ft); vf = VF(ft)
    t = measure_t(vf)
    print("Mischfaktoren je Master", [round(unnorm(v)) for v in vf.locs], [round(x, 3) for x in t])
    results = {}
    def put(g, kind, masters):                    # ganzzahlig, wie sie auch gelesen würden
        masters = [mapc(m, lambda p: (round(p[0]), round(p[1]))) for m in masters]
        results[g] = (kind, masters); vf.fixed[g] = masters
    for k in CROSSED: put(vf.glyph(k), "kreuzend", repair_crossed(vf, t, vf.glyph(k)))
    for k in HALF_RIGID: put(vf.glyph(k), "halb starr", repair_half_rigid(vf, t, vf.glyph(k)))
    for k in FLAT_TOP: put(vf.glyph(k), "oben flach", repair_half_rigid(vf, t, vf.glyph(k)))
    explicit = {vf.glyph(k) for k in STATIC_FIT + TWO_MASTER + [RING_ACUTE]} | \
               {vf.glyph(a[0]) for a in ACCENT + OGONEK} | {vf.glyph(a[0]) for a in SLASH}
    for g in feature_targets(ft, SMALLCAP_FEATURES):
        if g in explicit or g in results: continue
        e335, e600, e725 = flat_top_error(vf, t, g)
        if e335 <= 3 and e600 <= 6.5 and e725 > 6:
            put(g, "oben flach", repair_half_rigid(vf, t, g))
    for k in STATIC_FIT: put(vf.glyph(k), "aus Leise/Klar", static_masters(vf, t, k))
    for k in TWO_MASTER: put(vf.glyph(k), "aus Klar/600", repair_two_master(vf, t, vf.glyph(k)))
    for k, b, d, db in ACCENT:
        put(vf.glyph(k), "Akzent neu", repair_accent(vf, t, vf.glyph(b), vf.glyph(d), vf.glyph(db)))
    for k, b, m, mb in OGONEK:
        put(vf.glyph(k), "+ Ogonek", repair_ogonek(vf, t, vf.glyph(b), vf.glyph(m), vf.glyph(mb)))
    put(vf.glyph(RING_ACUTE), "Ring + Akut", repair_composed_ring_acute(
        vf, t, vf.masters(vf.glyph(("smcp", 0x00E5))), vf.glyph(ACUTE_SC[0]), vf.glyph(ACUTE_SC[1])))
    gaps = guillemet_gap(vf, t)
    for k, sgl in GUILL: put(vf.cmap[k], "aus ‹ ›", repair_guillemet(vf, t, vf.cmap[k], vf.cmap[sgl], gaps))
    for k, hi in LOWQ: put(vf.cmap[k], "aus ’ ”", repair_low_quote(vf, t, vf.cmap[k], vf.cmap[hi]))
    print("  Lücke « » je Master", [round(x) for x in gaps])
    for k, b, ln in SLASH:
        put(vf.glyph(k), "Schrägstrich", repair_slash(vf, t, vf.glyph(k), vf.glyph(b),
                                                     vf.glyph(ln) if ln else None))
    for cp in CASE:
        base = vf.cmap[cp]; g = gsub_single(ft, base, "case")
        put(g, "case", repair_case(vf, t, g, base, dash=cp in CASE_DASH))
    put(vf.cmap[BULLET], "starr (Entscheid)", repair_bullet(vf, t, vf.cmap[BULLET], vf.cmap[PERIOD]))
    # erst alles messen, dann schreiben (die Reparaturen lesen den alten Stand)
    from collections import Counter
    for g, (kind, masters) in results.items():
        write_glyph(vf, g, masters)
    for kind, n in Counter(k for k, _ in results.values()).items():
        print("  %3d × %s" % (n, kind))
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
