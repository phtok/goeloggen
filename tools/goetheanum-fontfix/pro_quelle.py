#!/usr/bin/env python3
# Lesen der Titillium Sans Pro (Chialab, OFL) als Quelle für v2.9
# (Etappe E2, docs/recherche_titillium-pro.md). Nur Daten aus den UFO-Mastern
# Thin · Regular · Bold: Umrisse, Vorschub, Anker, Kerning samt Gruppen.
# Die Pro ist fremder Code-Stand: hier wird nichts ausgeführt, nur XML gelesen.
#
# Gewichtszuordnung: die Pro-Master treffen die Achsenenden der Hausschrift
# genau (Stamm des I: Thin 36 = Flüstern 190, Bold 138 = Schreien 725,
# Regular 78 ≈ 420). Für einen Hausschnitt wird darum nach der Stammbreite
# zwischen den drei Mastern linear gemischt (stückweise, ohne Extrapolation).
import os
from fontTools.ufoLib import UFOReader
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.pointPen import PointToSegmentPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

MASTERS = ("Thin", "Regular", "Bold")


class _Obj:
    pass


class _Seg:
    """Segment-Pen, der Komponenten aufgelöst zeichnet."""
    def __init__(s, pen, ufo): s.pen = pen; s.ufo = ufo
    def moveTo(s, p): s.pen.moveTo(p)
    def lineTo(s, p): s.pen.lineTo(p)
    def curveTo(s, *p): s.pen.curveTo(*p)
    def qCurveTo(s, *p): s.pen.qCurveTo(*p)
    def closePath(s): s.pen.closePath()
    def endPath(s): s.pen.endPath()
    def addComponent(s, name, t): s.ufo.draw(name, TransformPen(s.pen, t))


class Master:
    def __init__(s, path):
        s.r = UFOReader(path, validate=False)
        s.gs = s.r.getGlyphSet(validateRead=False)
        s.raw = {}
        s.cmap = {}
        for n in s.gs.keys():
            for u in s.glyph(n).unicodes:
                s.cmap.setdefault(u, n)
        s.kern = s.r.readKerning()
        s.groups = s.r.readGroups()

    def glyph(s, n):
        if n not in s.raw:
            o = _Obj(); o.unicodes = []; o.width = 0; o.anchors = []
            s.gs.readGlyph(n, o)
            s.raw[n] = o
        return s.raw[n]

    def draw(s, n, pen):
        s.gs.readGlyph(n, _Obj(), PointToSegmentPen(_Seg(pen, s)))

    def record(s, n):
        p = RecordingPen(); s.draw(n, p); return p.value

    def anchor(s, n, name):
        for a in s.glyph(n).anchors:
            if a.get("name") == name: return a["x"], a["y"]
        return None

    def ink(s, n):
        b = BoundsPen(None); s.draw(n, b); return b.bounds

    def flat_kerning(s):
        """Kerning aufgelöst auf Glyphenpaare, mit der UFO-Vorrangregel
        (Glyphe/Glyphe vor Glyphe/Gruppe vor Gruppe/Glyphe vor Gruppe/Gruppe)."""
        def members(x):
            return s.groups.get(x, []) if x.startswith("public.kern") else [x]
        def prio(k):
            a, b = k
            return 2 * a.startswith("public.kern") + b.startswith("public.kern")
        out = {}
        for k, v in sorted(s.kern.items(), key=lambda kv: -prio(kv[0])):
            for x in members(k[0]):
                for y in members(k[1]):
                    out[(x, y)] = v
        return out


class Pro:
    """Die drei Pro-Master und ihre Mischung nach Stammbreite."""
    def __init__(s, root):
        ufo = os.path.join(root, "Sans", "UFO")
        s.m = [Master(os.path.join(ufo, "Titillium Sans Pro-%s.ufo" % n)) for n in MASTERS]
        s.cmap = s.m[1].cmap
        s.stems = [s._stem(m) for m in s.m]
        s._kern = [m.flat_kerning() for m in s.m]

    @staticmethod
    def _stem(m):
        x0, _, x1, _ = m.ink(m.cmap[ord("I")]); return x1 - x0

    def weights(s, stem):
        """Mischgewichte (Thin, Regular, Bold) für eine Ziel-Stammbreite."""
        a, b, c = s.stems
        stem = max(a, min(c, stem))
        if stem <= b:
            t = (stem - a) / (b - a); return (1 - t, t, 0.0)
        t = (stem - b) / (c - b); return (0.0, 1 - t, t)

    def compatible(s, n):
        recs = [m.record(n) for m in s.m]
        return all([op for op, _ in r] == [op for op, _ in recs[0]] and
                   [len(a) for _, a in r] == [len(a) for _, a in recs[0]] for r in recs)

    def outline(s, n, w):
        """Mischung der Master-Umrisse (RecordingPen-Liste) mit Gewichten w."""
        recs = [m.record(n) for m in s.m]
        out = []
        for segs in zip(*recs):
            op = segs[0][0]
            pts = [tuple(sum(wi * seg[1][k][ax] for wi, seg in zip(w, segs)) for ax in (0, 1))
                   for k in range(len(segs[0][1]))]
            out.append((op, pts))
        return out

    def width(s, n, w):
        return sum(wi * m.glyph(n).width for wi, m in zip(w, s.m))

    def anchor(s, n, name, w):
        a = [m.anchor(n, name) for m in s.m]
        if any(x is None for x in a): return None
        return tuple(sum(wi * p[ax] for wi, p in zip(w, a)) for ax in (0, 1))

    def ink(s, n, w):
        b = BoundsPen(None)
        for op, pts in s.outline(n, w): getattr(b, op)(*pts)
        return b.bounds

    def kern(s, a, b, w):
        """Kerning des Paars (Glyphennamen der Pro), gemischt; fehlt = 0."""
        return sum(wi * k.get((a, b), 0) for wi, k in zip(w, s._kern))

    def kerned_pairs(s):
        out = set()
        for k in s._kern: out |= set(k)
        return out
