#!/usr/bin/env python3
# Pfeilform nach Entwurf 5 (Entscheid des Inhabers 26. 11. 2026), für den Bau:
# Befund docs/befunde/pfeile-schrift-entwurf-2026-11-25.md § Entscheid.
#
# Dieselbe Konstruktion wie entwurf_pfeile_gebogen5.py (Variante B), aber als
# Schriftkontur statt als Bild:
#   - eine geschlossene Kontur je Pfeil, gegen den Uhrzeigersinn, mit fester
#     Punktfolge – darum zwischen allen Mastern interpolierbar;
#   - der Bogen ist eine echte Kurve (eine Bézier-Kurve je Seite), kein
#     Vieleck; der Strichverlauf läuft auch durch den Bogen;
#   - die flache Spitze liegt genau am Ende der Länge (Entwurf 5 schnitt sie
#     hinter der Gehrungsspitze ab, der Pfeil wurde um rund 0,25 × Schaft kürzer).
#
# Masse (Entwurf 3–5): Arm 48° zur Achse, Armlänge 250 bei Pfeillänge 820,
# Bogen Radius 210, Achtelkreis, Kopf in 45°. Schaft vom Kopf zum Schwanz
# schlanker (Verlauf Ruhig 0,82 … Laut 0,72, mit der Fette deutlicher, wie die
# Diagonalen der Titillium); Arme von der Wurzel 0,88 zum Ende (Verlauf − 0,04);
# Spitze flach, 0,55 × Schaft breit. Schaft im Mittel = Strich des Schnitts.
import math

THETA = math.radians(48)        # Arm zur Achse
ARM = 250                       # Armlänge (Mittellinie) bei Pfeillänge KASTEN
KASTEN = 820                    # Länge der geraden Pfeile in der Pfeil-Schrift
RADIUS = 210                    # Bogen der gebogenen Pfeile (Rohmass)
SENKRECHT, SCHRAEG = 470, 330   # gerade Strecken des gebogenen Pfeils (Rohmass)
FLACH = 0.55                    # Breite der flachen Spitze × Schaft am Kopf
WURZEL = 0.88                   # Arm an der Wurzel × Schaft am Kopf


def verlauf(s):
    """Schwanz : Schaft am Kopf, je Strich: Ruhig (60) 0,82 … Laut (113) 0,72."""
    t = max(0.0, min(1.0, (s - 60) / (113 - 60)))
    return 0.82 - 0.10 * t


def _u(grad):
    a = math.radians(grad); return (math.cos(a), math.sin(a))


def _schnitt(p1, p2, q1, q2):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, q1, q2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a = x1 * y2 - y1 * x2; b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def kopf(J, r, arm):
    """Kopf nach +x, flache Spitze vorn bei x = 0, Achse y = 0.
    Liefert die Kanten der oberen Hälfte (die untere ist gespiegelt) und den
    inneren Scheitel (x < 0, auf der Achse)."""
    wr, we = WURZEL * J, (r - 0.04) * J
    a = (-math.cos(THETA), math.sin(THETA))               # Arm nach hinten oben
    n = (math.sin(THETA), math.cos(THETA))                # Normale nach aussen (vorn)
    C = (0.0, 0.0); E = (arm * a[0], arm * a[1])
    aus = ((C[0] + n[0] * wr / 2, C[1] + n[1] * wr / 2), (E[0] + n[0] * we / 2, E[1] + n[1] * we / 2))
    inn = ((C[0] - n[0] * wr / 2, C[1] - n[1] * wr / 2), (E[0] - n[0] * we / 2, E[1] - n[1] * we / 2))
    spiegel = lambda p: (p[0], -p[1])
    apex = _schnitt(*aus, spiegel(aus[0]), spiegel(aus[1]))
    scheitel = _schnitt(*inn, spiegel(inn[0]), spiegel(inn[1]))
    # flach: dort, wo die Aussenkanten FLACH·J auseinander sind
    (ax, ay), (bx, by) = aus
    t = (FLACH * J / 2 - ay) / (by - ay)
    F = (ax + t * (bx - ax), FLACH * J / 2)
    dx = -F[0]                                            # flache Spitze auf x = 0
    mv = lambda p: (p[0] + dx, p[1])
    return {"F": mv(F), "aussen": mv(aus[1]), "innen": mv(inn[1]),
            "innen_wurzel": mv(inn[0]), "scheitel": mv(scheitel)[0]}


class Weg:
    """Mittellinie: Strecken und Kreisbögen vom Schwanz bis zur Spitze; die
    letzte Strecke ist gerade und zeigt in Pfeilrichtung."""
    def __init__(s, start):
        s.start = start; s.teile = []; s.ende = start

    def gerade(s, p):
        s.teile.append(("gerade", s.ende, p)); s.ende = p; return s

    def bogen(s, c, rad, a0, a1):
        s.teile.append(("bogen", c, rad, a0, a1))
        s.ende = (c[0] + rad * math.cos(math.radians(a1)), c[1] + rad * math.sin(math.radians(a1)))
        return s

    @staticmethod
    def laenge(t):
        if t[0] == "gerade": return math.dist(t[1], t[2])
        return abs(math.radians(t[4] - t[3])) * t[2]


def pfeil(weg, s, arm=ARM, verlauf_fix=None):
    """Kontur (Liste aus einer Kontur im Format [start, [(op, [pkte])…]]) des
    Pfeils entlang weg; Strich s im Mittel, flache Spitze am Ende des Wegs."""
    r = verlauf(s) if verlauf_fix is None else verlauf_fix
    J = 2 / (1 + r) * s
    k = kopf(J, r, arm)
    last = weg.teile[-1]; assert last[0] == "gerade"
    P0, T = last[1], last[2]
    d = ((T[0] - P0[0]) / math.dist(P0, T), (T[1] - P0[1]) / math.dist(P0, T))
    nrm = (-d[1], d[0])                                   # links der Laufrichtung
    welt = lambda p: (T[0] + d[0] * p[0] + nrm[0] * p[1], T[1] + d[1] * p[0] + nrm[1] * p[1])
    S = welt((k["scheitel"], 0))
    teile = weg.teile[:-1] + [("gerade", P0, S)]
    L = [Weg.laenge(t) for t in teile]; Lges = sum(L)
    h = lambda l: J * (r + (1 - r) * l / Lges) / 2         # halbe Breite nach Weglänge

    def seite(sgn):
        """Knoten einer Seite (sgn +1 links, −1 rechts) vom Schwanz zum Kopf;
        Bögen als eine Kurve. Liefert [(op, [pkte])…] ab dem Schwanzpunkt."""
        segs, l = [], 0.0
        for t, lt in zip(teile, L):
            if t[0] == "gerade":
                a, b = t[1], t[2]
                tx, ty = (b[0] - a[0]) / lt, (b[1] - a[1]) / lt
                n = (-ty * sgn, tx * sgn)
                l += lt; segs.append(("lineTo", [(b[0] + n[0] * h(l), b[1] + n[1] * h(l))]))
            else:
                _, c, rad, a0, a1 = t
                dphi = math.radians(a1 - a0); sg = 1 if dphi > 0 else -1
                # links der Laufrichtung liegt bei Lauf gegen den Uhrzeiger die Mitte
                def pt(phi, ll):
                    rr = rad - sgn * sg * h(ll)
                    return (c[0] + rr * math.cos(phi), c[1] + rr * math.sin(phi)), rr
                def abl(phi, rr):                         # dp/dphi bei linearem h(l)
                    dr = -sgn * sg * (J * (1 - r) / 2 / Lges) * rad   # dh/dl · dl/dphi
                    return (dr * math.cos(phi) - rr * math.sin(phi), dr * math.sin(phi) + rr * math.cos(phi))
                p0, r0 = pt(math.radians(a0), l); p3, r3 = pt(math.radians(a1), l + lt)
                kap = 4 / 3 * math.tan(abs(dphi) / 4)
                d0 = abl(math.radians(a0), r0); d3 = abl(math.radians(a1), r3)
                p1 = (p0[0] + sg * kap * d0[0], p0[1] + sg * kap * d0[1])
                p2 = (p3[0] - sg * kap * d3[0], p3[1] - sg * kap * d3[1])
                l += lt; segs.append(("curveTo", [p1, p2, p3]))
        return segs

    def kante(sgn):
        """Kopfpunkte der Seite sgn in Weltkoordinaten (y im Kopf = sgn)."""
        return {n: welt((p[0], sgn * p[1])) for n, p in k.items() if n != "scheitel"}

    def treffer(segs_end_prev, segs_end, sgn):
        kk = kante(sgn)
        return _schnitt(segs_end_prev, segs_end, kk["innen"], kk["innen_wurzel"])

    start = weg.start
    t0 = teile[0]
    if t0[0] == "gerade":
        tx, ty = (t0[2][0] - t0[1][0]) / L[0], (t0[2][1] - t0[1][1]) / L[0]
    else:
        a0 = math.radians(t0[3]); sg = 1 if t0[4] > t0[3] else -1
        tx, ty = -math.sin(a0) * sg, math.cos(a0) * sg
    schwanz = lambda sgn: (start[0] - ty * sgn * h(0), start[1] + tx * sgn * h(0))
    re, li = seite(-1), seite(1)

    def vorletzter(segs, sgn):
        if len(segs) > 1: return segs[-2][1][-1]
        return schwanz(sgn)
    Pr = treffer(vorletzter(re, -1), re[-1][1][-1], -1)
    Pl = treffer(vorletzter(li, 1), li[-1][1][-1], 1)
    re[-1] = ("lineTo", [Pr]); li[-1] = ("lineTo", [Pl])
    kr, kl = kante(-1), kante(1)
    segs = [("lineTo", [schwanz(-1)])] + re
    segs += [("lineTo", [kr["innen"]]), ("lineTo", [kr["aussen"]]), ("lineTo", [kr["F"]]),
             ("lineTo", [kl["F"]]), ("lineTo", [kl["aussen"]]), ("lineTo", [kl["innen"]]),
             ("lineTo", [Pl])]
    # linke Seite rückwärts
    knoten = [schwanz(1)] + [sg_[1][-1] for sg_ in li]
    for i in range(len(li) - 1, -1, -1):
        op, ps = li[i]
        if op == "lineTo": segs.append(("lineTo", [knoten[i]]))
        else: segs.append(("curveTo", [ps[1], ps[0], knoten[i]]))
    return [[schwanz(1), segs]]


def doppelt(L, s, arm):
    """↔: zwei Köpfe, Schaft durchgehend J (verjüngt wirkte er eingeschnürt).
    Mitte (0, 0), Spitzen bei ±L/2."""
    r = verlauf(s); J = 2 / (1 + r) * s
    k = kopf(J, r, arm)
    T = L / 2
    w = lambda p: (T + p[0], p[1])
    P = _schnitt(w(k["innen"]), w(k["innen_wurzel"]), (0, J / 2), (1, J / 2))
    rechts = [(P[0], -P[1]), w((k["innen"][0], -k["innen"][1])), w((k["aussen"][0], -k["aussen"][1])),
              w((k["F"][0], -k["F"][1])), w(k["F"]), w(k["aussen"]), w(k["innen"]), P]
    pts = rechts + [(-x, -y) for x, y in rechts]          # linke Hälfte: um 180° gedreht
    return [[pts[0], [("lineTo", [p]) for p in pts[1:]] + [("lineTo", [pts[0]])]]]


def gerade(L, s, arm):
    """Gerader Pfeil nach +x, Schwanz bei −L/2, flache Spitze bei +L/2."""
    return pfeil(Weg((-L / 2, 0)).gerade((L / 2, 0)), s, arm)


def gebogen_weg(f):
    """Gebogener Pfeil 1 (Pfeil-Schrift Taste 2, ↱): senkrecht von unten,
    Achtelkreis nach rechts, schräg weiter (45°). f skaliert die Mittellinie."""
    R = RADIUS * f
    w = Weg((0, 0)).gerade((0, SENKRECHT * f)).bogen((R, SENKRECHT * f), R, 180, 135)
    e = w.ende; d = _u(45)
    return w.gerade((e[0] + SCHRAEG * f * d[0], e[1] + SCHRAEG * f * d[1]))


def gebogen(hoehe, s, arm):
    """Gebogener Pfeil 1 auf Tintenhöhe hoehe: Mittellinie so skaliert, dass
    der ganze Pfeil (mit Kopf in fester Grösse) genau hoehe hoch ist.
    Unten bei y = 0, waagrecht mittig auf x = 0."""
    f = 1.0
    for _ in range(30):
        cs = pfeil(gebogen_weg(f), s, arm)
        x0, y0, x1, y1 = bounds(cs)
        f_neu = f * hoehe / (y1 - y0)                     # Kopf wächst nicht mit: Fixpunkt
        if abs(f_neu - f) < 1e-9: break
        f = f_neu
    x0, y0, x1, y1 = bounds(cs)
    return verschieben(cs, -(x0 + x1) / 2, -y0)


# ---------- Hilfen ----------
def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def bounds(cs):
    xs, ys = [], []
    for c in cs:
        cur = c[0]; xs.append(cur[0]); ys.append(cur[1])
        for op, ps in c[1]:
            if op == "curveTo":
                for i in range(1, 21):
                    x, y = _bez(cur, ps[0], ps[1], ps[2], i / 20); xs.append(x); ys.append(y)
            else:
                xs.append(ps[-1][0]); ys.append(ps[-1][1])
            cur = ps[-1]
    return min(xs), min(ys), max(xs), max(ys)


def abbilden(cs, fn):
    return [[fn(c[0]), [(op, [fn(p) for p in ps]) for op, ps in c[1]]] for c in cs]


def verschieben(cs, dx, dy): return abbilden(cs, lambda p: (p[0] + dx, p[1] + dy))


def drehen(cs, grad):
    a = math.radians(grad); c, s = math.cos(a), math.sin(a)
    return abbilden(cs, lambda p: (p[0] * c - p[1] * s, p[0] * s + p[1] * c))


def umkehren(cs):
    out = []
    for c in cs:
        knoten = [c[0]] + [ps[-1] for _, ps in c[1]]
        segs = []
        for i in range(len(c[1]) - 1, -1, -1):
            op, ps = c[1][i]
            segs.append((op, ps[:-1][::-1] + [knoten[i]]))
        out.append([knoten[-1], segs])
    return out


# Die acht gebogenen Pfeile: Abbildung der Grundform 1 (↱) um die Mitte (0, m)
# des Kastens, Tastenname der Pfeil-Schrift, Unicode, Spiegelung (Laufsinn
# kehrt sich um → Kontur umkehren).
GEBOGEN = [  # Taste, Unicode, Abbildung (x, y) relativ zur Mitte, gespiegelt
    ("2", 0x21B1, lambda x, y: (x, y), False),           # ↱ hoch, dann rechts
    ("0", 0x2B0E, lambda x, y: (y, -x), False),          # ⬎ rechts, dann runter
    ("q", 0x21B2, lambda x, y: (-x, -y), False),         # ↲ runter, dann links
    ("e", 0x2B11, lambda x, y: (-y, x), False),          # ⬑ links, dann hoch
    ("o", 0x21B0, lambda x, y: (-x, y), True),           # ↰ hoch, dann links
    ("ü", 0x2B0F, lambda x, y: (y, x), True),            # ⬏ rechts, dann hoch
    ("s", 0x21B3, lambda x, y: (x, -y), True),           # ↳ runter, dann rechts
    ("ö", 0x2B10, lambda x, y: (-y, -x), True),          # ⬐ links, dann runter
]


def gebogen_acht(cs, mitte):
    """Die acht Lagen der Grundform cs um den Punkt mitte."""
    mx, my = mitte; out = []
    for taste, cp, fn, gesp in GEBOGEN:
        g = abbilden(cs, lambda p, fn=fn: (lambda q: (q[0] + mx, q[1] + my))(fn(p[0] - mx, p[1] - my)))
        out.append(umkehren(g) if gesp else g)
    return out


def flaeche(cs):
    """Vorzeichenbehaftete Fläche (gegen den Uhrzeiger positiv)."""
    from fontTools.pens.areaPen import AreaPen
    p = AreaPen()
    for c in cs:
        p.moveTo(c[0])
        for op, ps in c[1]: getattr(p, op)(*ps)
        p.closePath()
    return p.value


def sauber(cs):
    """True, wenn die Kontur sich nirgends selbst schneidet: Vereinigung mit
    sich selbst (skia-pathops) ergibt dieselbe Fläche und eine Kontur."""
    import pathops
    from fontTools.pens.recordingPen import RecordingPen
    p = pathops.Path(); pen = p.getPen()
    for c in cs:
        pen.moveTo(c[0])
        for op, ps in c[1]: getattr(pen, op)(*ps)
        pen.closePath()
    q = pathops.Path(p); q.simplify()
    rec = RecordingPen(); q.draw(rec)
    n = sum(1 for op, _ in rec.value if op == "moveTo")
    return n == len(cs) and abs(abs(q.area) - abs(flaeche(cs))) < 0.5
