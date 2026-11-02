#!/usr/bin/env python3
# Hausschrift v2.9, Fassung 2.92: Pfeile ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ (U+2190–2199)
# in der Textschrift. Entscheid des Inhabers 2. 11. 2026: «Pfeile ja». Befund
# und Masse: docs/befunde/pfeile-textschrift-2026-11-02.md.
#
# Aus sauberem Stand: liest Variable und die fünf statischen Schnitte aus git
# (SOURCE_REV, Fassung 2.91), nie von der Platte; ein zweiter Lauf schreibt
# dieselben Dateien. Dateinamen bleiben v2.9, intern Version 2.92.
#
#  Form der ‹Goetheanum Pfeile› (build_pfeile.py, aus dem Icon-Font): Schaft
#  und offene Spitze aus zwei Armen, 53° zum Schaft, Armenden rechtwinklig
#  abgeschnitten, Spitze stumpf um eine Strichbreite. Die Pfeil-Schrift hat
#  sie dünn (Strich 24) und fett (58) bei 820 Einheiten Länge; die Armlänge
#  ist in beiden das 7,6-Fache des Strichs. Hier wird die Form an jedem Master
#  der Variable neu gezogen (gleiche Punktzahl, also kompatibel), der Strich
#  folgt dem Gewicht: Stärke des Minus (−, waagrechter Strich der Schrift).
#  Die Spitze wächst mit dem Strich, aber flacher als in der Pfeil-Schrift
#  (dort würde sie im Laut breiter als der Pfeil lang ist).
#
#  Lage: Länge = Versalhöhe (Oberkante H), Mitte auf halber Versalhöhe –
#  ↑ steht von der Grundlinie bis zur Versalhöhe, → liegt auf der Mitte der
#  Versalien und Ziffern (wie die Listenzeichen, CY 345). Schräge Pfeile sind
#  der um 45° gedrehte Pfeil auf derselben Mitte, so lang wie ↑
#  (feste Länge: bei fester Tintenhöhe bliebe im Laut kaum Schaft). ↔ und ↕
#  sind um 1/5 länger, damit zwischen den Spitzen Schaft bleibt.
#  Seitenrand = linker Rand des Minus.
#
#  Die statischen Schnitte bekommen die Instanz der Variable an ihrem
#  Gewicht (deckungsgleich), Vorschub stückweise linear zwischen den Mastern.
#
# Aufruf:  python3 build_v29_pfeile.py
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import repair_variable_v28 as R
import build_v29_pro as B
import build_v29_listen as Lst

REPO = B.REPO; ROOT = B.ROOT
SOURCE_REV = "a79148a"                 # main mit Fassung 2.91 (#751, #752)
VER_OLD, VER_NEW = "2.91", "2.92"
CUTS = Lst.CUTS

THETA = math.radians(53)    # Arm zum Schaft, wie ‹Goetheanum Pfeile›
HEAD = (0.27, 0.9)          # halbe Spitzenbreite = 0,27 × Länge + 0,9 × Strich
DIAG = 1.00                 # Länge der schrägen Pfeile, × Versalhöhe
DOPPEL = 1.20               # Länge ↔ ↕, × Versalhöhe

# Codepunkt → (Richtung in Grad, doppelt)
PFEILE = {0x2190: (180, False), 0x2191: (90, False), 0x2192: (0, False), 0x2193: (270, False),
          0x2194: (0, True), 0x2195: (90, True),
          0x2196: (135, False), 0x2197: (45, False), 0x2198: (315, False), 0x2199: (225, False)}


def kopf(tip, s, A, sign):
    """Eine Spitze bei x=tip, nach +x (sign=1) oder −x (sign=−1) zeigend:
    Punkte von unten über die stumpfe Spitze nach oben, dann bis zur
    Schaftkante (y = s/2). Gibt (Punkte oben, Punkte unten) je in Laufrichtung."""
    c, sn = math.cos(THETA), math.sin(THETA)
    f = s                                         # Stumpf der Spitze = Strich
    T1 = (tip, f / 2)
    E1 = (tip - sign * A * c, f / 2 + A * sn)
    E2 = (E1[0] - sign * s * sn, E1[1] - s * c)
    t = (E2[1] - s / 2) / sn
    J1 = (E2[0] + sign * t * c, s / 2)
    oben = [T1, E1, E2, J1]
    unten = [(x, -y) for (x, y) in oben]
    return oben, unten


def pfeil(L, s, doppelt):
    """Waagrechter Pfeil nach rechts, Spitze bei x = L/2, Mitte (0, 0).
    Eine Kontur gegen den Uhrzeigersinn (Aussenkontur der Hausschrift)."""
    hh = HEAD[0] * L + HEAD[1] * s
    A = (hh - s / 2) / math.sin(THETA)
    ob, un = kopf(L / 2, s, A, 1)
    pts = [un[0]] + ob                             # Spitze unten → oben → Schaftkante oben
    if doppelt:
        ob2, un2 = kopf(-L / 2, s, A, -1)
        pts += [ob2[3], ob2[2], ob2[1], ob2[0], un2[0], un2[1], un2[2], un2[3]]
    else:
        pts += [(-L / 2, s / 2), (-L / 2, -s / 2)]
    pts += [un[3], un[2], un[1]]
    return pts


def drehen(pts, grad):
    a = math.radians(grad); c, sn = math.cos(a), math.sin(a)
    return [(x * c - y * sn, x * sn + y * c) for x, y in pts]


def gestalt(cp, cap, s, sb):
    """Kontur und Vorschub eines Pfeils an einem Master."""
    grad, doppelt = PFEILE[cp]
    L = cap * (DOPPEL if doppelt else 1.0)
    if grad % 90: L = DIAG * cap                   # schräg: feste Länge, Schaft bleibt sichtbar
    P = drehen(pfeil(L, s, doppelt), grad)
    x0 = min(x for x, _ in P); x1 = max(x for x, _ in P)
    P = [(x - x0 + sb, y + cap / 2) for x, y in P]
    cs = [Lst.closed(P[0], [("lineTo", [p]) for p in P[1:]])]
    return cs, x1 - x0 + 2 * sb


class Bau:
    def __init__(s, src):
        s.src = src; n = src.n
        H = src.cmap[ord("H")]; M = src.cmap[0x2212]
        s.cap = [B.ink(src.out(H)[i])[3] for i in range(n)]
        mi = [B.ink(src.out(M)[i]) for i in range(n)]
        s.s = [b[3] - b[1] for b in mi]           # Strich = Stärke des Minus
        s.sb = [b[0] for b in mi]                 # Seitenrand = linker Rand des Minus

    def glyph(s, cp):
        ms, advs = [], []
        for i in range(s.src.n):
            cs, adv = gestalt(cp, s.cap[i], s.s[i], s.sb[i])
            ms.append(B.rnd(cs)); advs.append(int(round(adv)))
        return ms, advs


def build_variable(src):
    bau = Bau(src); plan = []
    for cp in sorted(PFEILE):
        if cp in src.cmap: raise SystemExit("schon belegt: U+%04X" % cp)
        ms, advs = bau.glyph(cp)
        name = src.add(cp, ms, advs); plan.append((cp, name, advs))
    return bau, plan


def build_static(ft, vsrc, plan, weight):
    """Instanz der Variable am Gewicht des Schnitts, Vorschub stückweise linear."""
    src = B.StatSrc(ft); v = (weight - 440) / 250 if weight < 440 else (weight - 440) / 285
    L = vsrc.vf.locs
    for cp, vname, advs in plan:
        if cp in src.cmap: raise SystemExit("schon belegt: U+%04X" % cp)
        cs = B.rnd(vsrc.vf.outline(vname, v))
        a = R.advances(vsrc.vf, vname)
        k = next(k for k in range(len(L) - 1) if L[k] <= v <= L[k + 1])
        adv = int(round(a[k] + (a[k + 1] - a[k]) * (v - L[k]) / (L[k + 1] - L[k])))
        src.add(cp, [cs], [adv])


def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s_ = rec.toUnicode()
            if VER_NEW not in s_: rec.string = s_.replace(VER_OLD, VER_NEW, 1)
    ft["head"].fontRevision = float(VER_NEW)


def main():
    Lst.SOURCE_REV = SOURCE_REV
    rel = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf"
    ft = Lst.git_font(rel); vsrc = B.VarSrc(ft)
    bau, plan = build_variable(vsrc); bump(ft)
    out = os.path.join(REPO, rel); ft.save(out); Lst.webfonts(out)
    print("Variabel: +%d Pfeile, Strich %s, Versalhöhe %s" % (len(plan), bau.s, bau.cap))
    for cp, _, advs in plan: print("  %s U+%04X Vorschub %s" % (chr(cp), cp, advs))
    from fontTools.ttLib import TTFont
    vf = TTFont(out); vsrc2 = B.VarSrc(vf)
    for cut, w in CUTS.items():
        rel = "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-%s.otf" % cut
        st = Lst.git_font(rel); build_static(st, vsrc2, plan, w); bump(st)
        out = os.path.join(REPO, rel); st.save(out); Lst.webfonts(out)
        print("  %-9s +%d Pfeile" % (cut, len(plan)))
    print("v2.9 (intern %s) geschrieben." % VER_NEW)


if __name__ == "__main__":
    main()
