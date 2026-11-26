#!/usr/bin/env python3
# ENTWURF 5 (26. 11. 2026), kein Paket: Pfeil-Schrift, Variante B, mit
# flacher Spitze und Verlauf, der mit der Fette zunimmt.
# Inhaber zu Entwurf 4: ‹Die Pfeilspitze gehören flach, keine zu breite
# Fläche! Die Verjüngung könnte mit der Fette deutlicher werden? Oder
# widerspricht das gemessenen Details an den Urentwürfen aus Urbino?›
# Befund: docs/befunde/pfeile-schrift-entwurf-2026-11-25.md (§ Entwurf 5)
#
# Gemessen (26. 11.):
#   Titillium Urbino (sources/Titillium-*Upright.otf) hat keine Pfeile.
#   Ihre Diagonalen verjüngen sich zum Knoten, mit der Fette stärker:
#   v Thin 0,97 · Light 0,95 · Regular 0,95 · Semibold 0,93 · Bold 0,91.
#   Die heutige Pfeil-Schrift (aus dem Icon-Font) umgekehrt: dünn 0,75,
#   fett 0,81 – nur zwei Gewichte, getrennt gezeichnet.
#   Spitze heute: flach, 0,95 × Schaft (dünn 32/34, fett 76/80).
#
# Hier: Verlauf nach der Urbino-Logik (mit der Fette deutlicher), auf dem
# Niveau der Pfeil-Schrift: Schaft Ruhig 0,82 … Laut 0,72; Arme im gleichen
# Mass. Spitze flach, Breite FLACH × Schaft (0,55; heute 0,95 zum Vergleich).
#
# Aufruf: python3 tools/goetheanum-fontfix/entwurf_pfeile_gebogen5.py [scratch]
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
import entwurf_pfeile_gebogen4 as E4
from entwurf_pfeile_textform import strich, heute, GEBOGEN, ZELLE
from entwurf_pfeile_gebogen3 import u, linie_B, alle8, d_of, zeile, einpassen, THETA

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "docs/befunde/pfeile-gebogen-entwurf5-2026-11-26.svg")
FLACH = 0.55                     # Breite der flachen Spitze × Schaft am Kopf


def verlauf(s):
    """Schaft-Verlauf je Strich: Ruhig (60) 0,82 … Laut (113) 0,72, linear."""
    t = max(0.0, min(1.0, (s - 60) / (113 - 60)))
    return 0.82 - 0.10 * t


def mit(s, flach):
    """Setzt Verlauf und Spitze in Entwurf 4 und liefert dessen pfeil()."""
    r = verlauf(s)
    E4.VERLAUF_SCHAFT = r
    E4.VERLAUF_ARM = (0.88, r - 0.04)
    E4.J_ZU_S = 2 / (1 + r)

    kopf4 = E4.kopf.__wrapped__ if hasattr(E4.kopf, "__wrapped__") else E4.kopf

    def kopf(T, grad, J):
        k, sch = kopf4(T, grad, J)
        if not flach: return k, sch
        dx, dy = u(grad)
        d = flach * J / (2 * math.tan(THETA))       # so weit hinter der Spitze ist der Keil flach·J breit
        # Halbebene: alles mit Projektion > (T·dir − d) weg
        g = affinity.rotate(k, -grad, origin=T, use_radians=False)
        x0, y0, x1, y1 = g.bounds
        g = g.intersection(box(x0 - 10, y0 - 10, x1 - d, y1 + 10))
        return affinity.rotate(g, grad, origin=T, use_radians=False), sch
    kopf.__wrapped__ = kopf4
    E4.kopf = kopf
    return E4.pfeil


def gebogen(s, flach):
    fn = mit(s, flach)
    linie, grad = linie_B()
    roh = fn(linie, grad, s)
    x0, y0, x1, y1 = roh.bounds; f = 820 / (y1 - y0)
    return einpassen(fn([(x * f, y * f) for x, y in linie], grad, s))


def gerade(s, grad, flach):
    fn = mit(s, flach)
    g = fn([(0, 0), (0, 820)], 90, s)
    g = affinity.translate(g, 500, 90)
    return affinity.rotate(g, grad - 90, origin=(500, 500))


def reihe(label, s, flach):
    return (label, [d_of(gerade(s, 90, flach)), d_of(gerade(s, 0, flach))]
            + [d_of(p) for p in alle8(gebogen(s, flach))])


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else None
    st = {n: strich(n) for n in ("Ruhig", "Klar", "Deutlich", "Laut")}
    alt = heute(["6", "u", "&", "U"] + GEBOGEN)
    reihen = [("Heute dünn", [alt["6"], alt["u"]] + [alt[k] for k in GEBOGEN]),
              ("Heute fett", [alt["&"], alt["U"]] + [None] * 8),
              reihe("Spitze 0,95 (heute), Klar", st["Klar"], 0.95)]
    for name in ("Ruhig", "Klar", "Deutlich", "Laut"):
        reihen.append(reihe("Entwurf 5, %s (%.2f)" % (name, verlauf(st[name])), st[name], FLACH))
    H = 1150
    body = "\n".join(zeile(i * H, lab, ds) for i, (lab, ds) in enumerate(reihen))
    W = 2600 + 10 * ZELLE
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -60 %d %d" role="img" '
           'aria-label="Pfeil-Schrift, Entwurf 5: flache Spitze, Verlauf mit der Fette">\n'
           '<style>path{fill:#1a1a1a} .l{font:170px \'Goetheanum\',\'Helvetica Neue\',Arial,sans-serif;fill:#1a1a1a}</style>\n'  # ds-ok: Bild
           '<rect x="0" y="-60" width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n') % (W, len(reihen) * H + 60, body)  # ds-ok
    open(OUT, "w", encoding="utf-8").write(svg)
    print("geschrieben:", os.path.relpath(OUT, REPO))
    if scratch:
        open(os.path.join(scratch, "gebogen5.html"), "w", encoding="utf-8").write(
            '<!doctype html><meta charset="utf-8"><style>@font-face{font-family:G;src:url("file://%s/assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")}'
            'body{margin:30px;background:#fff}svg{width:100%%;height:auto}text{font-family:G!important}</style>%s' % (REPO, svg))


if __name__ == "__main__":
    main()
