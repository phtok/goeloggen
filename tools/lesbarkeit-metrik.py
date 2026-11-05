#!/usr/bin/env python3
"""Lesbarkeits-Metrik einer Schrift, aus der Datei gemessen (Skill lesbarkeit).

Alle Werte in Tausendstel em (Geviert = 1000), Verfahren nach
designs/texter/SITZUNG-SCHRIFTEN.md: x-Höhe, Strich, Breite des o.

  python3 tools/lesbarkeit-metrik.py DATEI [DATEI …] [--wght 400]

Spalten:
  x flach   Oberkante des x (gleich OS/2 sxHeight, wenn gepflegt)
  x rund    Oberkante des o, mit Überhang (das misst, wer am o abliest)
  Strich    Breite des l auf halber x-Höhe
  o/x       Breite des o zur flachen x-Höhe (Öffnung, Laufbreite)
  a–z       mittlerer Vorschub der Kleinbuchstaben
  0/O       Breite Null zu Breite O (1.0 = gleich breit, verwechselbar)

Braucht fontTools (pip install fonttools brotli).
"""
import argparse
import sys

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


class _Strecken(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.segs, self.cur, self.start = [], None, None

    def _moveTo(self, p):
        self.cur = self.start = p

    def _lineTo(self, p):
        self.segs.append((self.cur, p))
        self.cur = p

    def _kurve(self, punkt):
        p0 = self.cur
        for i in range(1, 17):
            q = punkt(p0, i / 16)
            self.segs.append((self.cur, q))
            self.cur = q

    def _curveToOne(self, a, b, c):
        self._kurve(lambda p0, t: tuple(
            (1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * a[k]
            + 3 * (1 - t) * t * t * b[k] + t ** 3 * c[k] for k in (0, 1)))

    def _qCurveToOne(self, a, c):
        self._kurve(lambda p0, t: tuple(
            (1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * a[k] + t * t * c[k]
            for k in (0, 1)))

    def _closePath(self):
        if self.cur != self.start:
            self.segs.append((self.cur, self.start))


def messen(pfad, wght):
    f = TTFont(pfad)
    k = 1000 / f["head"].unitsPerEm
    gs = f.getGlyphSet(location={"wght": wght}) if "fvar" in f else f.getGlyphSet()
    cmap = f.getBestCmap()
    name = lambda ch: cmap[ord(ch)]

    def box(ch):
        p = BoundsPen(gs)
        gs[name(ch)].draw(p)
        return p.bounds

    def vorschub(ch):
        p = BoundsPen(gs)
        g = gs[name(ch)]
        return g.width

    xh = box("x")[3]
    ob = box("o")
    p = _Strecken(gs)
    gs[name("l")].draw(p)
    y = xh / 2
    xs = sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                for a, b in p.segs if (a[1] - y) * (b[1] - y) < 0)
    strich = xs[1] - xs[0] if len(xs) >= 2 else float("nan")
    az = sum(vorschub(c) for c in "abcdefghijklmnopqrstuvwxyz") / 26
    return {
        "x flach": xh * k, "x rund": ob[3] * k, "Strich": strich * k,
        "Strich/x": strich / xh, "o/x": (ob[2] - ob[0]) / xh,
        "a–z": az * k, "0/O": vorschub("0") / vorschub("O"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dateien", nargs="+")
    ap.add_argument("--wght", type=float, default=400,
                    help="Achse bei variablen Schriften (Standard 400)")
    a = ap.parse_args()
    kopf = ["x flach", "x rund", "Strich", "Strich/x", "o/x", "a–z", "0/O"]
    print("Datei".ljust(44) + "".join(s.rjust(9) for s in kopf))
    for d in a.dateien:
        try:
            m = messen(d, a.wght)
        except Exception as e:  # fehlende Glyphe, kaputte Datei
            print(f"{d}: {e}", file=sys.stderr)
            continue
        zellen = [f"{m[s]:.0f}" if m[s] > 10 else f"{m[s]:.3f}" for s in kopf]
        print(d.split("/")[-1][:43].ljust(44) + "".join(z.rjust(9) for z in zellen))


if __name__ == "__main__":
    main()
