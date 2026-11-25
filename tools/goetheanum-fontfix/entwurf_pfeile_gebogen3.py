#!/usr/bin/env python3
# ENTWURF 3 (25. 11. 2026), kein Paket: gebogene Pfeile der ‹Goetheanum Pfeile›
# neu. Rückmeldung des Inhabers zu Entwurf 1 und 2: ‹crumpy, dumpf, stumpf›.
# Befund: docs/befunde/pfeile-schrift-entwurf-2026-11-25.md (§ Entwurf 3)
#
# Was anders ist als in Entwurf 1/2 (Kritik im Befund):
#   - gleichmässiger Strich, keine Verjüngung (die wirkt gross wie ein Keil);
#   - Kopf als Winkel mit Gehrung: spitze Spitze statt stumpfer, Arme lang
#     und offen wie in der heutigen Pfeil-Schrift;
#   - Lichtfalle: der Schaft endet im inneren Scheitel des Kopfs, kein Knoten;
#   - der Kopf sitzt auf einer geraden Strecke, nicht im Bogen;
#   - eine Geometrie für alle Gewichte (Radius, Wege), nur der Strich wächst –
#     also interpolierbar;
#   - Konturen als echte Vereinigung (shapely), keine überlappenden Polygone.
#
# Varianten des gebogenen Pfeils 1 (Taste 2, ‹hoch, dann rechts›); die übrigen
# sieben sind Drehungen und Spiegelungen wie heute:
#   A Winkel:  senkrecht, Viertelkreis, waagrecht in die Ausfahrt (Kopf 0°)
#   B Schräg:  senkrecht, Achtelkreis, gerade schräg weiter (Kopf 45°)
#   C Schwung: ein einziger weiter Bogen, Kopf waagrecht
#   D Heute:   die heutige Mittellinie, nur Strich und Kopf neu
#
# Schreibt nur Bilder: docs/befunde/pfeile-gebogen-entwurf3-2026-11-25.svg
# Aufruf: python3 tools/goetheanum-fontfix/entwurf_pfeile_gebogen3.py [scratch]
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from shapely import affinity
from entwurf_pfeile_textform import strich, heute, mittellinie_heute, SYM, GEBOGEN, ZELLE

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "docs/befunde/pfeile-gebogen-entwurf3-2026-11-25.svg")
THETA = math.radians(48)   # Arm zur Achse
ARM = 250                  # Armlänge (Mittellinie), wie die offenen Arme heute
R = 210                    # Radius der Bögen, für alle Gewichte gleich


def u(grad):
    a = math.radians(grad); return math.cos(a), math.sin(a)


def kopf(T, grad, s):
    """Winkel mit Gehrung; T = äussere Spitze. Liefert (Form, innerer Scheitel)."""
    dx, dy = u(grad)
    vor = (s / 2) / math.sin(THETA)                       # Gehrung ragt so weit vor
    C = (T[0] - dx * vor, T[1] - dy * vor)                # Spitze der Mittellinie
    a1, a2 = u(grad + 180 - math.degrees(THETA)), u(grad + 180 + math.degrees(THETA))
    P = LineString([(C[0] + ARM * a1[0], C[1] + ARM * a1[1]), C,
                    (C[0] + ARM * a2[0], C[1] + ARM * a2[1])])
    form = P.buffer(s / 2, cap_style="flat", join_style="mitre", mitre_limit=4)
    innen = (C[0] - dx * vor, C[1] - dy * vor)            # innerer Scheitel
    return form, innen


def bogen(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def pfeil(linie, grad, s):
    """linie: Mittellinie bis zur äusseren Spitze; Kopf in Richtung grad."""
    T = linie[-1]
    k, innen = kopf(T, grad, s)
    dx, dy = u(grad)                                      # nichts über den Scheitel hinaus
    weg = [p for p in linie[:-1] if (p[0] - innen[0]) * dx + (p[1] - innen[1]) * dy < -1] + [innen]
    schaft = LineString(weg).buffer(s / 2, cap_style="flat", join_style="round")
    return unary_union([schaft, k])


def einpassen(g):
    """Senkrecht 90 … 910, waagrecht auf die Mitte 500."""
    x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, 500 - (x0 + x1) / 2, 90 - y0)


def linie_A():   # Winkel
    x = 0; top = 700
    return [(x, 0), (x, top - R)] + bogen((x + R, top - R), R, 180, 90)[1:] + [(x + R + 330, top)], 0


def linie_B():   # schräg
    x = 0; y = 470
    b = bogen((x + R, y), R, 180, 135)
    e = b[-1]; d = u(45)
    return [(x, 0)] + b + [(e[0] + 330 * d[0], e[1] + 330 * d[1])], 45


def linie_C():   # Schwung: ein Viertel einer Ellipse
    rx, ry = 430, 640
    pts = [(rx - rx * math.cos(math.radians(t)), ry * math.sin(math.radians(t))) for t in range(0, 91, 3)]
    return pts + [(pts[-1][0] + 120, pts[-1][1])], 0


def linie_D():   # heutige Mittellinie
    M = mittellinie_heute()
    (ax, ay), (bx, by) = M[-6], M[-1]
    g = math.degrees(math.atan2(by - ay, bx - ax))
    d = u(g)
    return M + [(bx + 60 * d[0], by + 60 * d[1])], g


VARIANTEN = [("A Winkel", linie_A), ("B Schräg", linie_B), ("C Schwung", linie_C), ("D Heute", linie_D)]


def gerade(s, grad):
    g = pfeil([(0, 0), (0, 820)], 90, s)
    g = affinity.translate(g, 500, 90)
    return affinity.rotate(g, grad - 90, origin=(500, 500))


def alle8(g):
    out = []
    for k in GEBOGEN:
        f = SYM[k]
        ext = [f(x, y) for x, y in g.exterior.coords]
        holes = [[f(x, y) for x, y in r.coords] for r in g.interiors]
        out.append(Polygon(ext, holes))
    return out


def d_of(g):
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    parts = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)
            parts.append("M" + " L".join("%.1f %.1f" % q for q in c) + " Z")
    return " ".join(parts)


def zeile(y, label, ds):
    g = ['<text x="0" y="%d" class="l">%s</text>' % (y + 560, label)]
    for i, d in enumerate(ds):
        if d is None: continue
        g.append('<path transform="translate(%d %d) scale(1 -1)" d="%s"/>' % (2600 + i * ZELLE + 125, y + 1000, d))
    return "\n".join(g)


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else None
    st = {n: strich(n) for n in ("Klar", "Laut")}
    alt = heute(["6", "u"] + GEBOGEN)
    reihen = [("Heute dünn", [alt["6"], alt["u"]] + [alt[k] for k in GEBOGEN])]
    for name, fn in VARIANTEN:
        for schnitt in ("Klar", "Laut"):
            s = st[schnitt]; linie, grad = fn()
            # Linie im Rohmass bauen, dann einpassen; Strich nach dem Einpassen
            # gleich: darum zuerst mit Strich 1 einpassen, Faktor merken.
            roh = pfeil(linie, grad, s)
            x0, y0, x1, y1 = roh.bounds; f = 820 / (y1 - y0)
            linie2 = [(x * f, y * f) for x, y in linie]
            g = einpassen(pfeil(linie2, grad, s))
            reihen.append(("%s, %s" % (name, schnitt),
                           [d_of(gerade(s, 90)), d_of(gerade(s, 0))] + [d_of(p) for p in alle8(g)]))
    H = 1150
    body = "\n".join(zeile(i * H, lab, ds) for i, (lab, ds) in enumerate(reihen))
    W = 2600 + 10 * ZELLE
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -60 %d %d" role="img" '
           'aria-label="Gebogene Pfeile, Entwurf 3: vier Varianten in Klar und Laut">\n'
           '<style>path{fill:#1a1a1a} .l{font:180px \'Goetheanum\',\'Helvetica Neue\',Arial,sans-serif;fill:#1a1a1a}</style>\n'  # ds-ok: Bild
           '<rect x="0" y="-60" width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n') % (W, len(reihen) * H + 60, body)  # ds-ok
    open(OUT, "w", encoding="utf-8").write(svg)
    print("geschrieben:", os.path.relpath(OUT, REPO))
    if scratch:
        open(os.path.join(scratch, "gebogen3.html"), "w", encoding="utf-8").write(
            '<!doctype html><meta charset="utf-8"><style>@font-face{font-family:G;src:url("file://%s/assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")}'
            'body{margin:30px;background:#fff}svg{width:100%%;height:auto}text{font-family:G!important}</style>%s' % (REPO, svg))


if __name__ == "__main__":
    main()
