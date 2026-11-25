#!/usr/bin/env python3
# ENTWURF (25. 11. 2026), kein Paket: ‹Goetheanum Pfeile› auf die Form der
# Textschrift-Pfeile heben. Auftrag des Inhabers: «ja, ich möchte die Entwürfe
# sehen» (offener Punkt aus docs/befunde/pfeile-textschrift-2026-11-02.md).
# Befund: docs/befunde/pfeile-schrift-entwurf-2026-11-25.md
#
# Schreibt nur Bilder, keine Schriftdatei:
#   docs/befunde/pfeile-schrift-entwurf-2026-11-25.svg  (Glyphentafel)
#   <scratch>/pfeile-entwurf.html                       (Tafel + Satzprobe, für das PNG)
#
# Form: dieselbe Konstruktion wie die Textschrift-Pfeile (build_v29_pfeile.py:
# Arm 50° zum Schaft, stumpfe Spitze, Strichverlauf 0,71/0,85/0,72, Kopfgrösse
# 0,27 × Länge + 0,9 × Strich), aber im Kasten der Pfeil-Schrift: Länge 820,
# Mitte 500, Vorschub 1250 – Belegung und Lage bleiben, wie sie sind.
# Strich = Stärke des Minus im gewählten Hausschnitt (gemessen aus den
# statischen Schnitten). Gebogene Pfeile 1–8: die Mittellinie der heutigen
# Glyphe ‹2› (senkrecht bis 484, Bogen bis zur Spitze in 40°), mit demselben
# Kopf und Verlauf; die übrigen sieben sind ihre Spiegelungen und Drehungen,
# wie in der heutigen Schrift (geprüft: 100 von 100 Punkten je Glyphe).
#
# Aufruf: python3 tools/goetheanum-fontfix/entwurf_pfeile_textform.py [scratch-ordner]
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_v29_pfeile import kopf, pfeil, drehen, VERLAUF, J_ZU_S, HEAD, THETA
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
OUT_SVG = os.path.join(REPO, "docs/befunde/pfeile-schrift-entwurf-2026-11-25.svg")
OUT_SVG2 = os.path.join(REPO, "docs/befunde/pfeile-gebogen-entwurf2-2026-11-25.svg")
L = 820          # Länge der geraden Pfeile in der Pfeil-Schrift (90 … 910)
ZELLE = 1250     # Vorschub der Pfeil-Schrift
L_BOGEN = 340    # Kopfgrösse der gebogenen Pfeile wie bei einem geraden Pfeil dieser Länge
BOGEN = 436      # Ende des senkrechten Teils bei Strich 24 (heute 484)

# Belegung der Pfeil-Schrift: gerade ↑ ← → ↓ (6 t u h), gebogen 1–8 (2 0 q e o ü s ö)
GERADE = [("6", 90), ("t", 180), ("u", 0), ("h", 270)]
SYM = {"2": lambda x, y: (x, y), "0": lambda x, y: (y, 1000 - x),
       "q": lambda x, y: (1000 - x, 1000 - y), "e": lambda x, y: (1000 - y, x),
       "o": lambda x, y: (1000 - x, y), "ü": lambda x, y: (y, x),
       "s": lambda x, y: (x, 1000 - y), "ö": lambda x, y: (1000 - y, 1000 - x)}
GEBOGEN = list(SYM)


def strich(schnitt):
    f = TTFont(os.path.join(FONTS, "Goetheanum-Schrift-v2.9-%s.otf" % schnitt))
    gs = f.getGlyphSet(); b = BoundsPen(gs); gs[f.getBestCmap()[0x2212]].draw(b)
    return b.bounds[3] - b.bounds[1]


def gerade(grad, s):
    P = drehen(pfeil(L, s, False), grad)
    return [[(x + 500, y + 500) for x, y in P]]


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def gebogen(s):
    """Gebogener Pfeil 1 (Taste 2): senkrecht von unten, Bogen nach rechts oben."""
    J = J_ZU_S * s; e = VERLAUF["ende"] * J
    # Mit dem Strich wächst der Kopf; damit der Bogen offen bleibt, rückt der
    # Schaft nach links, die Spitze nach rechts und der Bogen tiefer (bei
    # Strich 24 genau die heutige Lage).
    m = s - 24
    d = math.radians(40); T = (606.0 + 0.6 * m, 862.0)
    x0 = 396.0 - 1.2 * m; bogen = BOGEN - 1.5 * m
    hh = HEAD[0] * L_BOGEN + HEAD[1] * s
    A = (hh - VERLAUF["stumpf"] * J / 2) / math.sin(THETA)
    ob, un = kopf(0.0, J, A, 1)
    # Der Schaft läuft die letzte Strecke gerade in Pfeilrichtung, bis in den Kopf
    # hinein – so schliesst der Kopf ohne Kerbe an (wie beim geraden Pfeil).
    gerade_ab = ob[3][0] - 1.5 * J
    E = (T[0] + gerade_ab * math.cos(d), T[1] + gerade_ab * math.sin(d))
    F = (T[0] + 0.5 * ob[3][0] * math.cos(d), T[1] + 0.5 * ob[3][0] * math.sin(d))
    mitte = [(x0, 90 + i * (bogen - 90) / 20) for i in range(20)]
    P0, P3 = (x0, bogen), E
    k1 = 0.55 * (E[1] - bogen)                 # senkrecht aus dem Schaft
    k2 = 0.55 * (E[0] - x0) / math.cos(d)       # in Pfeilrichtung in den Kopf
    P1 = (x0, bogen + k1); P2 = (E[0] - k2 * math.cos(d), E[1] - k2 * math.sin(d))
    mitte += [bezier(P0, P1, P2, P3, i / 40) for i in range(41)]
    n_e = len(mitte) - 1                      # ab E voller Schaft J, wie am Kopf
    mitte += [(E[0] + (F[0] - E[0]) * i / 6, E[1] + (F[1] - E[1]) * i / 6) for i in range(1, 7)]
    # Länge entlang der Linie, Breite von e (Ende) nach J (Kopf), wie gerade Pfeile
    lang = [0.0]
    for a, b in zip(mitte, mitte[1:]): lang.append(lang[-1] + math.dist(a, b))
    links, rechts = [], []
    for i, (x, y) in enumerate(mitte):
        a, b = mitte[max(i - 1, 0)], mitte[min(i + 1, len(mitte) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; n = math.hypot(tx, ty); tx, ty = tx / n, ty / n
        w = (e + (J - e) * min(1.0, lang[i] / lang[n_e])) / 2
        links.append((x - ty * w, y + tx * w)); rechts.append((x + ty * w, y - tx * w))
    schaft = links + rechts[::-1]
    c, sn = math.cos(d), math.sin(d)
    K = [un[0]] + ob + [(ob[3][0] - J, J / 2), (ob[3][0] - J, -J / 2)] + [un[3], un[2], un[1]]
    K = [(T[0] + x * c - y * sn, T[1] + x * sn + y * c) for x, y in K]
    return [schaft, K]


def mittellinie_heute():
    """Mittellinie des heutigen gebogenen Pfeils 1 (Taste 2), aus seinen beiden
    Schaftkanten: Kanten flach gerechnet, je nach Bogenlänge auf 80 Punkte
    verteilt, gemittelt. Liefert Punkte von unten bis zur Kopfwurzel."""
    from fontTools.pens.recordingPen import RecordingPen
    pf = TTFont(os.path.join(FONTS, "Goetheanum-Pfeile-v2.9.otf"))
    gs = pf.getGlyphSet(); r = RecordingPen(); gs[pf.getBestCmap()[ord("2")]].draw(r)
    pts = []; cur = None
    for op, a in r.value:
        if op == "moveTo": cur = a[0]; pts.append([cur])
        elif op == "lineTo": cur = a[0]; pts.append([cur])
        elif op == "curveTo":
            seg = [bezier(cur, a[0], a[1], a[2], t / 8) for t in range(1, 9)]
            cur = a[2]; pts.append(seg)
        else: pts.append([])
    # Kanten finden: die beiden Punkte bei y=90 (Schaftende) und die
    # Kopfwurzeln (Punkt vor dem Arm innen, Punkt nach dem Arm aussen)
    flat = [(i, q) for i, seg in enumerate(pts) for q in seg]
    def idx(x, y): return min(range(len(flat)), key=lambda k: math.dist(flat[k][1], (x, y)))
    a0, a1 = idx(406, 90), idx(587, 822)          # innen: unten → Kopfwurzel
    b0, b1 = idx(383, 90), idx(569, 850)          # aussen: unten → Kopfwurzel (rückwärts im Umlauf)
    innen = [q for _, q in flat[a0:a1 + 1]]
    aussen = [q for _, q in (flat[b1:] + flat[:b0 + 1])][::-1]
    def verteilen(L, n=80):
        d = [0.0]
        for u, v in zip(L, L[1:]): d.append(d[-1] + math.dist(u, v))
        out = []
        for k in range(n + 1):
            t = d[-1] * k / n; j = max(i for i in range(len(d)) if d[i] <= t)
            j = min(j, len(L) - 2); f = (t - d[j]) / ((d[j + 1] - d[j]) or 1)
            out.append((L[j][0] + f * (L[j + 1][0] - L[j][0]), L[j][1] + f * (L[j + 1][1] - L[j][1])))
        return out
    return [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(verteilen(innen), verteilen(aussen))]


def gebogen_treu(s):
    """Entwurf 2: Schaft genau auf der heutigen Mittellinie, nur Strich,
    Verlauf und Kopf der Textschrift. Die Spitze sitzt in Verlängerung der
    letzten Schaftrichtung (heute rund 38°)."""
    J = J_ZU_S * s; e = VERLAUF["ende"] * J
    M = mittellinie_heute()
    (ax, ay), (bx, by) = M[-6], M[-1]
    d = math.atan2(by - ay, bx - ax)
    hh = HEAD[0] * L_BOGEN + HEAD[1] * s
    A = (hh - VERLAUF["stumpf"] * J / 2) / math.sin(THETA)
    ob, un = kopf(0.0, J, A, 1)
    T = (bx - 0.5 * ob[3][0] * math.cos(d), by - 0.5 * ob[3][0] * math.sin(d))
    lang = [0.0]
    for u, v in zip(M, M[1:]): lang.append(lang[-1] + math.dist(u, v))
    links, rechts = [], []
    for i, (x, y) in enumerate(M):
        u, v = M[max(i - 1, 0)], M[min(i + 1, len(M) - 1)]
        tx, ty = v[0] - u[0], v[1] - u[1]; n = math.hypot(tx, ty); tx, ty = tx / n, ty / n
        w = (e + (J - e) * lang[i] / lang[-1]) / 2
        links.append((x - ty * w, y + tx * w)); rechts.append((x + ty * w, y - tx * w))
    c, sn = math.cos(d), math.sin(d)
    K = [un[0]] + ob + [(ob[3][0] - J, J / 2), (ob[3][0] - J, -J / 2)] + [un[3], un[2], un[1]]
    K = [(T[0] + x * c - y * sn, T[1] + x * sn + y * c) for x, y in K]
    return [links + rechts[::-1], K]


def gebogen_alle(s, treu=False):
    g = gebogen_treu(s) if treu else gebogen(s)
    return {k: [[SYM[k](x, y) for x, y in poly] for poly in g] for k in GEBOGEN}


def heute(keys):
    pf = TTFont(os.path.join(FONTS, "Goetheanum-Pfeile-v2.9.otf"))
    gs = pf.getGlyphSet(); cm = pf.getBestCmap(); out = {}
    for k in keys:
        p = SVGPathPen(gs); gs[cm[ord(k)]].draw(p); out[k] = p.getCommands()
    return out


def orient(poly):
    """Alle Konturen gleich herum: Überlappung von Schaft und Kopf bleibt gefüllt."""
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if a > 0 else poly[::-1]


def poly_d(polys):
    polys = [orient(p) for p in polys]
    return " ".join("M" + " L".join("%.1f %.1f" % p for p in poly) + " Z" for poly in polys)


def zeile(y, label, glyphs):
    """glyphs: Liste von d-Strings (Font-Koordinaten, y nach oben)."""
    g = ['<text x="0" y="%d" class="l">%s</text>' % (y + 330, label)]
    for i, d in enumerate(glyphs):
        x = 2600 + i * ZELLE
        g.append('<path transform="translate(%d %d) scale(1 -1)" d="%s"/>' % (x + 125, y + 1000, d))
    return "\n".join(g)


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else None
    st = {n: strich(n) for n in ("Ruhig", "Klar", "Deutlich", "Laut")}
    alt = heute([k for k, _ in GERADE] + ["&", "T", "U", "H"] + GEBOGEN)
    reihen = [("Heute dünn (24)", [alt[k] for k, _ in GERADE] + [alt[k] for k in GEBOGEN]),
              ("Heute fett (58)", [alt[k] for k in "&TUH"])]
    for name in ("Ruhig", "Klar", "Deutlich", "Laut"):
        s = st[name]; gb = gebogen_alle(s)
        reihen.append(("Entwurf %s (%d)" % (name, round(s)),
                       [poly_d(gerade(g, s)) for _, g in GERADE] + [poly_d(gb[k]) for k in GEBOGEN]))
    H = 1300
    body = "\n".join(zeile(i * H, lab, gl) for i, (lab, gl) in enumerate(reihen))
    W = 2600 + 12 * ZELLE
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
           'aria-label="Pfeil-Schrift heute und Entwurf in der Form der Textschrift">\n'
           '<style>path{fill:#1a1a1a} .l{font:200px \'Goetheanum\',\'Helvetica Neue\',Arial,sans-serif;fill:#1a1a1a}</style>\n'  # ds-ok: Bild, keine Theme-Fläche
           '<rect width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n') % (W, len(reihen) * H, body)  # ds-ok
    open(OUT_SVG, "w", encoding="utf-8").write(svg)
    print("geschrieben:", os.path.relpath(OUT_SVG, REPO), "– Strich je Schnitt:",
          ", ".join("%s %d" % (k, round(v)) for k, v in st.items()))
    # Gebogene Pfeile: Entwurf 1 (Bogen weitet sich mit dem Gewicht) gegen
    # Entwurf 2 (heutige Mittellinie, nur Strich und Kopf neu)
    reihen2 = [("Heute dünn (24)", [alt[k] for k in GEBOGEN])]
    for name in ("Klar", "Laut"):
        for treu, lab in ((False, "1"), (True, "2")):
            gb = gebogen_alle(st[name], treu)
            reihen2.append(("Entwurf %s, %s" % (lab, name), [poly_d(gb[k]) for k in GEBOGEN]))
    body2 = "\n".join(zeile(i * H, lab, gl) for i, (lab, gl) in enumerate(reihen2))
    svg2 = svg.split("\n")[0] + "\n"
    svg2 = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
            'aria-label="Gebogene Pfeile: heute, Entwurf 1 und 2 in Klar und Laut">\n'
            '<style>path{fill:#1a1a1a} .l{font:200px \'Goetheanum\',\'Helvetica Neue\',Arial,sans-serif;fill:#1a1a1a}</style>\n'  # ds-ok: Bild
            '<rect width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n') % (2600 + 8 * ZELLE, len(reihen2) * H, body2)  # ds-ok
    open(OUT_SVG2, "w", encoding="utf-8").write(svg2)
    print("geschrieben:", os.path.relpath(OUT_SVG2, REPO))
    if scratch:
        open(os.path.join(scratch, "pfeile-gebogen.html"), "w", encoding="utf-8").write(
            '<!doctype html><meta charset="utf-8"><style>@font-face{font-family:G;src:url("file://%s/assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")}'
            'body{margin:40px;background:#fff}svg{width:100%%;height:auto}text{font-family:G!important}</style>%s' % (REPO, svg2))
        satz = []
        for lab, d in [("Textschrift Klar", None), ("Pfeil-Schrift heute", alt["u"]),
                       ("Entwurf Klar", poly_d(gerade(0, st["Klar"]))),
                       ("Entwurf Ruhig", poly_d(gerade(0, st["Ruhig"])))]:
            pf = ("→" if d is None else
                  '<svg viewBox="0 0 1250 1000" style="height:1em;width:1.25em;vertical-align:-0.2em">'
                  '<path transform="translate(125 1000) scale(1 -1)" d="%s"/></svg>' % d)
            satz.append('<p><span class="lb">%s</span><span class="s">Ausgang %s Grosser Saal</span></p>' % (lab, pf))
        html = ('<!doctype html><meta charset="utf-8"><style>'
                '@font-face{font-family:G;src:url("file://%s/assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")}'
                'body{margin:40px;background:#fff;color:#1a1a1a;font-family:G}'
                '.t svg{width:100%%;height:auto} .t text{font-family:G!important}'
                'p{display:grid;grid-template-columns:420px 1fr;align-items:baseline;margin:10px 0}'
                '.lb{font-size:22px;color:#555}.s{font-size:44px}'
                '</style><div class="t">%s</div>%s') % (REPO, svg, "".join(satz))
        out = os.path.join(scratch, "pfeile-entwurf.html")
        open(out, "w", encoding="utf-8").write(html); print("Vorschau:", out)


if __name__ == "__main__":
    main()
