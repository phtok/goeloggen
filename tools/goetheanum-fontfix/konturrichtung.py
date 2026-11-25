#!/usr/bin/env python3
# Konturrichtung prüfen (Befund 25. 11. 2026, Fassung 2.93). Hausregel wie in
# CFF üblich: eine Kontur, die eine gefüllte Fläche umschliesst, läuft gegen
# den Uhrzeigersinn (Fläche > 0 nach AreaPen), eine Punze mit dem
# Uhrzeigersinn (< 0). Ob eine Kontur Fläche oder Punze ist, entscheidet nicht
# ihr Drehsinn, sondern das gerenderte Blatt: Ein Punkt knapp innerhalb der
# Kontur wird mit der Non-Zero-Regel über die ganze Glyphe ausgewertet –
# gefüllt heisst Fläche, leer heisst Punze. So zählen auch überlappende Teile
# (Schrägstrich der Null, angesetzte Akzente) richtig.
#
# Eine falsch gedrehte Kontur fällt beim normalen Rendern nicht auf, solange
# alle Konturen eines Rings gemeinsam verkehrt laufen (Windungszahl −1 statt
# +1). Sie läuft aber zu, sobald gefettet oder geweitet wird (synthetisches
# Fett, Kontur-Effekte, Dilatation beim Rastern), und sie stört Werkzeuge, die
# Überlappungen auflösen.
#
# Als Modul: richtung(konturen) → Liste der Konturindizes, die zu drehen sind.
# Als Skript:  python3 konturrichtung.py DATEI.otf …   (Variable: je Master)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import repair_variable_v28 as R

EPS = 1.5          # Abstand des Prüfpunkts von der Kontur (Einheiten)


def polygon(c, n=12):
    out = [c[0]]; cur = c[0]
    for op, ps in c[1]:
        if op == "curveTo":
            p0, (p1, p2, p3) = cur, ps
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                out.append(tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c_ + t**3 * d
                                 for a, b, c_, d in zip(p0, p1, p2, p3)))
        else: out.append(ps[-1])
        cur = ps[-1]
    if out[-1] == out[0]: out.pop()
    return out


def winding(pt, poly):
    x, y = pt; w = 0; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if y1 <= y < y2 and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) > 0: w += 1
        elif y2 <= y < y1 and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) < 0: w -= 1
    return w


def area(poly):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1])) / 2


def probes(poly, k=9):
    """Punkte knapp innerhalb der eigenen Kontur, an den längsten Kanten."""
    a = area(poly); n = len(poly)
    edges = sorted(range(n), key=lambda i: -((poly[(i + 1) % n][0] - poly[i][0]) ** 2 +
                                             (poly[(i + 1) % n][1] - poly[i][1]) ** 2))
    out = []
    for i in edges[:k]:
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if L < 4 * EPS: continue
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L        # links der Laufrichtung
        if a < 0: nx, ny = -nx, -ny                    # Innenseite der eigenen Kontur
        p = ((x1 + x2) / 2 + EPS * nx, (y1 + y2) / 2 + EPS * ny)
        if winding(p, poly) != 0: out.append(p)
    return out


def richtung(cs):
    """Indizes der Konturen, deren Drehsinn nicht zum gerenderten Blatt passt."""
    polys = [polygon(c) for c in cs]
    bad = []
    for i, P in enumerate(polys):
        a = area(P)
        if abs(a) < 1: continue
        votes = [sum(winding(p, Q) for Q in polys) != 0 for p in probes(P)]
        if not votes: continue
        filled = sum(votes) * 2 > len(votes)
        if filled != (a > 0): bad.append(i)
    return bad


def pruefe(path):
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import RecordingPen
    ft = TTFont(path); cm = {}
    for cp, g in ft.getBestCmap().items(): cm.setdefault(g, cp)
    funde = {}
    if "CFF2" in ft:
        vf = R.VF(ft)
        for g in ft.getGlyphOrder():
            ms = vf.masters(g)
            je = [tuple(richtung(m)) for m in ms]
            if any(je): funde[g] = je
    else:
        gs = ft.getGlyphSet()
        for g in ft.getGlyphOrder():
            p = RecordingPen(); gs[g].draw(p)
            b = richtung(R.contours(p.value))
            if b: funde[g] = b
    return funde, cm


if __name__ == "__main__":
    for path in sys.argv[1:]:
        funde, cm = pruefe(path)
        print("%s: %d Glyphen" % (os.path.basename(path), len(funde)))
        for g, b in funde.items():
            z = "%s U+%04X" % (chr(cm[g]), cm[g]) if g in cm else "–"
            print("  %-9s %-9s %s" % (g, z, b))
