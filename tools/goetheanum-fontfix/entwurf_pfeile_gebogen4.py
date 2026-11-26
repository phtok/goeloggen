#!/usr/bin/env python3
# ENTWURF 4 (26. 11. 2026), kein Paket: Pfeil-Schrift, Variante B (schräg)
# mit dem Strichverlauf der heutigen ‹Goetheanum Pfeile›.
# Inhaber zu Entwurf 3: ‹Schräg kommt dem Entwurf am nächsten. Doch das
# Gestaltungsprinzip scheint noch nicht voll erfasst zu sein: Die Balken
# verjüngen sich leicht am Ende. […] Das gibt Dynamik und Eleganz.›
# Befund: docs/befunde/pfeile-schrift-entwurf-2026-11-25.md (§ Entwurf 4)
#
# Gemessen (26. 11.), senkrecht durch den Schaft von → :
#   Pfeil-Schrift dünn: Schwanz 24 → Kopf 32 (0,75), fett: 58 → 72 (0,81);
#   Arme: Wurzel 0,85, Ende 0,72 des Schafts am Kopf (Befund 2. 11.).
#   Titillium Pro → hat keinen Verlauf (Strich gleich); die Hausschrift
#   verjüngt Diagonalen leicht zum Knoten hin (v 80 → 76, y-Schwanz 79 → 74).
# Der Verlauf ist also das Merkmal der Pfeil-Schrift, nicht der Titillium.
#
# Konstruktion: Schaft wird vom Kopf zum Schwanz schlanker (VERLAUF_SCHAFT),
# Arme von der Wurzel zum Ende (VERLAUF_ARM); Innenkante der Arme darum
# steiler als die Aussenkante; Spitze mit Gehrung (spitz); der Schaft endet
# im inneren Scheitel (Lichtfalle). Geometrie von Entwurf 3 B (Radius 210,
# Achtelkreis, Kopf in 45°), für alle Gewichte gleich.
#
# Aufruf: python3 tools/goetheanum-fontfix/entwurf_pfeile_gebogen4.py [scratch]
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
from entwurf_pfeile_textform import strich, heute, GEBOGEN, ZELLE
from entwurf_pfeile_gebogen3 import (u, linie_B, alle8, d_of, zeile, einpassen,
                                     pfeil as pfeil3, gerade as gerade3, THETA, ARM)

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "docs/befunde/pfeile-gebogen-entwurf4-2026-11-26.svg")
VERLAUF_SCHAFT = 0.78          # Schwanz : Schaft am Kopf (heute 0,75 dünn, 0,81 fett)
VERLAUF_ARM = (0.88, 0.74)     # Wurzel, Ende : Schaft am Kopf (heute 0,85 / 0,72)
J_ZU_S = 2 / (1 + VERLAUF_SCHAFT)   # Schaft im Mittel = Strich des Schnitts


def schnitt(p1, p2, q1, q2):
    """Schnittpunkt der Geraden p1p2 und q1q2."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, q1, q2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a = x1 * y2 - y1 * x2; b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def kopf(T, grad, J):
    """Spitze T (aussen), Richtung grad, Schaft am Kopf J. Arme verjüngt."""
    wr, we = VERLAUF_ARM[0] * J, VERLAUF_ARM[1] * J
    dx, dy = u(grad)
    vor = (wr / 2) / math.sin(THETA)
    C = (T[0] - dx * vor, T[1] - dy * vor)
    teile, aussen, innen = [], [], []
    for sgn in (1, -1):
        a = u(grad + 180 - sgn * math.degrees(THETA))            # Arm nach hinten
        n = (-a[1] * sgn, a[0] * sgn)                             # Normale nach aussen
        if n[0] * dx + n[1] * dy < 0: n = (-n[0], -n[1])
        E = (C[0] + ARM * a[0], C[1] + ARM * a[1])
        q = [(C[0] + n[0] * wr / 2, C[1] + n[1] * wr / 2), (E[0] + n[0] * we / 2, E[1] + n[1] * we / 2),
             (E[0] - n[0] * we / 2, E[1] - n[1] * we / 2), (C[0] - n[0] * wr / 2, C[1] - n[1] * wr / 2)]
        teile.append(Polygon(q)); aussen.append((q[0], q[1])); innen.append((q[3], q[2]))
    apex = schnitt(*aussen[0], *aussen[1])
    scheitel = schnitt(*innen[0], *innen[1])
    teile.append(Polygon([aussen[0][0], apex, aussen[1][0], scheitel]))
    return unary_union(teile).buffer(0), scheitel


def schaft(weg, J):
    """Schaft mit Verlauf: am Anfang (Schwanz) VERLAUF_SCHAFT·J, am Ende J."""
    lang = [0.0]
    for a, b in zip(weg, weg[1:]): lang.append(lang[-1] + math.dist(a, b))
    L, re, li = lang[-1], [], []
    for i, (x, y) in enumerate(weg):
        a, b = weg[max(i - 1, 0)], weg[min(i + 1, len(weg) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; n = math.hypot(tx, ty) or 1; tx, ty = tx / n, ty / n
        w = J * (VERLAUF_SCHAFT + (1 - VERLAUF_SCHAFT) * lang[i] / L) / 2
        li.append((x - ty * w, y + tx * w)); re.append((x + ty * w, y - tx * w))
    return Polygon(li + re[::-1]).buffer(0)


def pfeil(linie, grad, s):
    J = J_ZU_S * s
    k, sch = kopf(linie[-1], grad, J)
    dx, dy = u(grad)
    weg = [p for p in linie[:-1] if (p[0] - sch[0]) * dx + (p[1] - sch[1]) * dy < -1] + [sch]
    # dichte Punkte, damit der Verlauf auch auf Geraden wirkt
    dicht = []
    for a, b in zip(weg, weg[1:]):
        n = max(1, int(math.dist(a, b) / 20))
        dicht += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    dicht.append(weg[-1])
    return unary_union([schaft(dicht, J), k]).buffer(0)


def gerade(s, grad):
    g = pfeil([(0, 0), (0, 820)], 90, s)
    g = affinity.translate(g, 500, 90)
    return affinity.rotate(g, grad - 90, origin=(500, 500))


def gebogen(s, fn=pfeil):
    linie, grad = linie_B()
    roh = fn(linie, grad, s)
    x0, y0, x1, y1 = roh.bounds; f = 820 / (y1 - y0)
    return einpassen(fn([(x * f, y * f) for x, y in linie], grad, s))


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else None
    st = {n: strich(n) for n in ("Ruhig", "Klar", "Deutlich", "Laut")}
    alt = heute(["6", "u", "&", "U"] + GEBOGEN)
    reihen = [("Heute dünn", [alt["6"], alt["u"]] + [alt[k] for k in GEBOGEN]),
              ("Heute fett", [alt["&"], alt["U"]] + [None] * 8),
              ("Entwurf 3 B, Klar", [d_of(gerade3(st["Klar"], 90)), d_of(gerade3(st["Klar"], 0))]
               + [d_of(p) for p in alle8(gebogen(st["Klar"], pfeil3))])]
    for name in ("Ruhig", "Klar", "Deutlich", "Laut"):
        s = st[name]
        reihen.append(("Entwurf 4, %s" % name, [d_of(gerade(s, 90)), d_of(gerade(s, 0))]
                       + [d_of(p) for p in alle8(gebogen(s))]))
    H = 1150
    body = "\n".join(zeile(i * H, lab, ds) for i, (lab, ds) in enumerate(reihen))
    W = 2600 + 10 * ZELLE
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -60 %d %d" role="img" '
           'aria-label="Pfeil-Schrift, Entwurf 4: schräg, mit Strichverlauf, in vier Gewichten">\n'
           '<style>path{fill:#1a1a1a} .l{font:180px \'Goetheanum\',\'Helvetica Neue\',Arial,sans-serif;fill:#1a1a1a}</style>\n'  # ds-ok: Bild
           '<rect x="0" y="-60" width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n') % (W, len(reihen) * H + 60, body)  # ds-ok
    open(OUT, "w", encoding="utf-8").write(svg)
    print("geschrieben:", os.path.relpath(OUT, REPO), "– J je Schnitt:",
          ", ".join("%s %.0f" % (k, J_ZU_S * v) for k, v in st.items()))
    if scratch:
        open(os.path.join(scratch, "gebogen4.html"), "w", encoding="utf-8").write(
            '<!doctype html><meta charset="utf-8"><style>@font-face{font-family:G;src:url("file://%s/assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")}'
            'body{margin:30px;background:#fff}svg{width:100%%;height:auto}text{font-family:G!important}</style>%s' % (REPO, svg))


if __name__ == "__main__":
    main()
