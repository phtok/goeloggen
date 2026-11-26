#!/usr/bin/env python3
# Fassung 2.96 (26. 11. 2026): Pfeile nach Entwurf 5. Entscheid des Inhabers
# vom 26. 11.; Befund docs/befunde/pfeile-schrift-entwurf-2026-11-25.md
# § Entscheid und § Bau 2.96. Form: pfeilform.py.
#
# Aus sauberem Stand: liest Pfeil-Schrift, Variable und die fünf statischen
# Schnitte aus git (SOURCE_REV), schreibt dieselben Dateinamen, intern 2.96;
# zweiter Lauf bitgleich.
#
#  1 ‹Goetheanum Pfeile› neu gezeichnet: dünn = Strich von Klar, fett = Laut
#    (Stärke des Minus im statischen Schnitt). Gerade Pfeile 6 t u h, fett
#    mit Umschalt (& T U H) wie bisher; gebogene Pfeile 2 0 q e o ü s ö, neu
#    auch fett mit Umschalt (" = Q E O è S é, deutsche Tastatur Ü Ö). Kompass
#    y x c v unverändert. PUA-Adressen bleiben auf denselben Glyphen.
#  2 Grundschrift (Variable + fünf Schnitte): ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ in derselben
#    Form, dazu die acht gebogenen ↱ ⬎ ↲ ⬑ ↰ ⬏ ↳ ⬐ (U+21B0–21B3, U+2B0E–2B11).
#    An jedem Master neu gezogen (feste Punktfolge, also interpolierbar).
#    Lage wie 2.92: Länge = Versalhöhe, Mitte auf halber Versalhöhe; schräge
#    Pfeile so lang wie ↑, ↔ ↕ um 1/5 länger. Strich im Mittel = Minus,
#    Seitenrand = linker Rand des Minus. Kopf im Verhältnis der Pfeil-Schrift
#    (Arm 250/820 der Länge). Gebogene Pfeile so hoch wie ↑ (bzw. so lang
#    wie →, wenn sie waagrecht beginnen), Mitte auf halber Versalhöhe.
#  Die Kursive (2.95) bleibt unberührt: ihre Pfeile stammen aus der Pro.
#
# Aufruf:  python3 build_v296.py
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import repair_variable_v28 as R
import sync_statics_v28 as SY
import build_v29_pro as B
import build_v29_listen as Lst
import pfeilform as P

REPO = B.REPO
SOURCE_REV = "b4756f9"                 # main mit Fassung 2.94 (#790) und 2.95 (#789)
VER_NEU = "2.96"
CUTS = {"Leise": 265, "Ruhig": 350, "Klar": 440, "Deutlich": 580, "Laut": 680}
VAR = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf"
STAT = "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-%s.otf"
PFEILE = "assets/fonts/goetheanum/Fonts/Goetheanum-Pfeile-v2.9.otf"

# Pfeil-Schrift: Kasten 0 … 1000, Mitte 500, Länge 820, Vorschub 1250
MITTE, VORSCHUB = 500, 1250
GERADE_TASTEN = {"6": (90, "&"), "t": (180, "T"), "u": (0, "U"), "h": (270, "H")}
FETT_GEBOGEN = {"2": '"', "0": "=", "q": "Q", "e": "E", "o": "O", "ü": "è", "s": "S", "ö": "é"}
FETT_DEUTSCH = {"ü": "Ü", "ö": "Ö"}

# Grundschrift: Codepunkt → (Richtung, doppelt)
GERADE = {0x2190: (180, False), 0x2191: (90, False), 0x2192: (0, False), 0x2193: (270, False),
          0x2194: (0, True), 0x2195: (90, True),
          0x2196: (135, False), 0x2197: (45, False), 0x2198: (315, False), 0x2199: (225, False)}
DOPPEL = 1.20


def git_font(rel):
    blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return TTFont(tmp.name, recalcTimestamp=False)


def pruefen(cs, wo):
    assert P.flaeche(cs) > 0, "Laufsinn: %s" % wo
    assert P.sauber(cs), "Kontur schneidet sich: %s" % wo
    return cs


def strich(cut):
    """Stärke des Minus im statischen Schnitt (wie entwurf_pfeile_textform.strich)."""
    f = git_font(STAT % cut); gs = f.getGlyphSet(); b = BoundsPen(gs)
    gs[f.getBestCmap()[0x2212]].draw(b)
    return b.bounds[3] - b.bounds[1]


def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s_ = rec.toUnicode()
            for alt in ("2.94", "2.93"):
                if alt in s_: s_ = s_.replace(alt, VER_NEU, 1); break
            rec.string = s_
    ft["head"].fontRevision = float(VER_NEU)


# ---------- 1 Pfeil-Schrift ----------
def pfeil_schrift(s_duenn, s_fett):
    ft = git_font(PFEILE); src = B.StatSrc(ft); cm = ft.getBestCmap()
    td = ft["CFF "].cff.topDictIndex[0]

    def setzen(name, cs):
        cs = B.rnd(cs)
        SY.draw_into(ft, td, None, name, lambda pen, cs=cs: B.draw(pen, cs), VORSCHUB)

    for taste, (grad, fett) in GERADE_TASTEN.items():
        for t, s in ((taste, s_duenn), (fett, s_fett)):
            cs = pruefen(P.verschieben(P.drehen(P.gerade(P.KASTEN, s, P.ARM), grad), MITTE, MITTE), t)
            setzen(cm[ord(t)], cs)
    for s, fett in ((s_duenn, False), (s_fett, True)):
        g = P.verschieben(P.gebogen(P.KASTEN, s, P.ARM), MITTE, (1000 - P.KASTEN) / 2)
        for (taste, cp, _, _), cs in zip(P.GEBOGEN, P.gebogen_acht(g, (MITTE, MITTE))):
            pruefen(cs, taste)
            if not fett:
                setzen(cm[ord(taste)], cs)
            else:
                name = src.add(ord(FETT_GEBOGEN[taste]), [B.rnd(cs)], [VORSCHUB])
                if taste in FETT_DEUTSCH: src.map(ord(FETT_DEUTSCH[taste]), name)
    bump(ft)
    out = os.path.join(REPO, PFEILE); ft.save(out); Lst.webfonts(out)
    print("Pfeil-Schrift: dünn %.0f, fett %.0f, %d Glyphen" % (s_duenn, s_fett, len(ft.getGlyphOrder())))


# ---------- 2 Grundschrift ----------
def gestalt(cp, cap, s, sb):
    """Kontur und Vorschub eines Pfeils an einem Master."""
    arm = P.ARM * cap / P.KASTEN
    if cp in GERADE:
        grad, dop = GERADE[cp]
        cs = P.doppelt(cap * DOPPEL, s, arm) if dop else P.gerade(cap, s, arm)
        cs = P.verschieben(P.drehen(cs, grad), 0, cap / 2)
    else:
        i = [g[1] for g in P.GEBOGEN].index(cp)
        cs = P.gebogen_acht(P.gebogen(cap, s, arm), (0, cap / 2))[i]
    x0, _, x1, _ = P.bounds(cs)
    cs = P.verschieben(cs, sb - x0, 0)
    return pruefen(cs, "U+%04X" % cp), x1 - x0 + 2 * sb


ALLE = sorted(GERADE) + [g[1] for g in P.GEBOGEN]


def grundschrift():
    ft = git_font(VAR); vs = B.VarSrc(ft); n = vs.n
    H = vs.cmap[ord("H")]; M = vs.cmap[0x2212]
    cap = [B.ink(vs.out(H)[i])[3] for i in range(n)]
    mi = [B.ink(vs.out(M)[i]) for i in range(n)]
    st = [b[3] - b[1] for b in mi]; sb = [b[0] for b in mi]
    di = vs.vf.locs.index(0.0)
    for cp in ALLE:
        ms, advs = [], []
        for i in range(n):
            cs, adv = gestalt(cp, cap[i], st[i], sb[i])
            ms.append(B.rnd(cs)); advs.append(int(round(adv)))
        if cp in vs.cmap:
            g = vs.cmap[cp]
            R.write_glyph(vs.vf, g, ms); R.set_advances(vs.vf, g, advs)
            ft["hmtx"][g] = (ft["hmtx"][g][0], int(round(B.ink(ms[di])[0])))
        else:
            vs.add(cp, ms, advs)
    bump(ft)
    out = os.path.join(REPO, VAR); ft.save(out); Lst.webfonts(out)
    print("Variabel: %d Pfeile, Strich %s" % (len(ALLE), [round(x) for x in st]))
    vf = TTFont(out); v2 = B.VarSrc(vf); L = v2.vf.locs
    for cut, w in CUTS.items():
        rel = STAT % cut; sft = git_font(rel); ss = B.StatSrc(sft)
        td = sft["CFF "].cff.topDictIndex[0]; fds = td.FDArray if hasattr(td, "FDArray") else None
        v = (w - 440) / 250 if w < 440 else (w - 440) / 285
        k = next(k for k in range(len(L) - 1) if L[k] <= v <= L[k + 1])
        for cp in ALLE:
            g = v2.cmap[cp]; cs = B.rnd(v2.vf.outline(g, v))
            a = R.advances(v2.vf, g)
            adv = int(round(a[k] + (a[k + 1] - a[k]) * (v - L[k]) / (L[k + 1] - L[k])))
            if cp in ss.cmap:
                SY.draw_into(sft, td, fds, ss.cmap[cp], lambda pen, cs=cs: B.draw(pen, cs), adv)
            else:
                ss.add(cp, [cs], [adv])
        bump(sft)
        out = os.path.join(REPO, rel); sft.save(out); Lst.webfonts(out)
        print("  %-9s %d Pfeile" % (cut, len(ALLE)))


def main():
    pfeil_schrift(strich("Klar"), strich("Laut"))
    grundschrift()
    print("Fassung %s geschrieben." % VER_NEU)


if __name__ == "__main__":
    main()
