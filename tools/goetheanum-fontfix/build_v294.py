#!/usr/bin/env python3
# Hausschrift v2.9, Fassung 2.94 (26. 11. 2026). Entscheide des Inhabers vom
# 26. 11.; Befund docs/befunde/konturrichtung-kapitaelchen-2026-11-25.md § 4.
#
# Aus sauberem Stand: liest Variable und die fünf statischen Schnitte aus git
# (SOURCE_REV, Fassung 2.93), schreibt dieselben Dateinamen, intern 2.94;
# zweiter Lauf bitgleich.
#
#  1 ‰ neu konstruiert: genau das % der Schrift (oberer Ring, Schrägstrich,
#    unterer Ring) plus ein zweiter, gleicher unterer Ring. Regel für den
#    Abstand: die Ringe sind verkleinerte o (gleiche Proportion), also stehen
#    sie so weit auseinander wie zwei o der Schrift, auf Ringhöhe verkleinert
#    (Flüstern 60, Klar 49, Schreien 34 Einheiten – im Fetten enger wie «oo»,
#    aber nie zu). Die drei Ringe folgen dem Gewicht zu 85 % (Mischfaktor
#    0,85 · t), damit die Punzen ab Deutlich offen bleiben; der Schrägstrich
#    folgt dem Schnitt. Bisher (aus v1.4.43): Ringe an festen Stellen, Abstand
#    52 → 17, ab Deutlich liefen sie ineinander.
#  2 Kapitälchen ß → Kapitälchen-ẞ (statt ss): Namen bleiben unterscheidbar
#    (Weiß/Weiss), etwa in Literaturangaben. Dieselbe Glyphe wie c2sc ẞ.
#  3 Kerning der zusammengesetzten Kapitälchen (ĳ ﬁ ﬂ) richtig herum: steht
#    die Glyphe links, zählt ihr rechter Teil (j, i, l), steht sie rechts, ihr
#    linker (i, f). Kapitälchen-ẞ kernt links wie B, rechts wie S.
#
# Aufruf:  python3 build_v294.py
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
import repair_variable_v28 as R
import sync_statics_v28 as SY
import build_v29_pro as B
import build_v29_listen as Lst
import build_v293 as V3

REPO = B.REPO
SOURCE_REV = "36e1930"                 # main mit Fassung 2.93 (#781)
VER_OLD, VER_NEW = "2.93", "2.94"
CUTS = V3.CUTS
LEICHT = 0.85                           # Anteil des Gewichts, dem die Ringe folgen
PROMILLE, PROZENT = 0x2030, 0x0025
# Konturen des %: 0 Punze oben, 1 Schrägstrich, 2 Ring oben, 3 Ring unten, 4 Punze unten
STRICH, UNTEN = 1, (3, 4)


def git_font(rel):
    blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return TTFont(tmp.name, recalcTimestamp=False)


def promille(vs):
    """Master und Vorschübe des neuen ‰ aus % und o."""
    vf = vs.vf; t = R.measure_t(vf)
    pm = vs.out(vs.cmap[PROZENT]); padv = vs.adv(vs.cmap[PROZENT])
    om = vs.out(vs.cmap[ord("o")]); oadv = vs.adv(vs.cmap[ord("o")])
    assert len(pm[0]) == 5, "Konturfolge des % hat sich geändert"
    out, advs, luft = [], [], []
    for i, ti in enumerate(t):
        leicht = R.mix(pm[0], pm[-1], ti * LEICHT)      # Ringe mit weniger Gewicht
        m = [leicht[k] if k != STRICH else pm[i][k] for k in range(5)]
        r0, _, r1, r3 = R.bbox(m[UNTEN[0]])[0], 0, R.bbox(m[UNTEN[0]])[2], R.bbox(m[UNTEN[0]])[3]
        ob = B.ink(om[i])
        s = (r3 - R.bbox(m[UNTEN[0]])[1]) / (ob[3] - ob[1])
        gap = s * (oadv[i] - (ob[2] - ob[0]))           # Abstand zweier o, auf Ringgrösse
        dx = (r1 - r0) + gap
        out.append(m + R.mapc([m[k] for k in UNTEN], lambda p, dx=dx: (p[0] + dx, p[1])))
        advs.append(int(round(padv[i] + dx))); luft.append(round(gap))
    return out, advs, luft


def kern_setzen(ft, neu, rechts_wie, links_wie):
    """Klassen der Glyphe neu setzen (überschreibt): als erste Glyphe eines
    Paars wie rechts_wie, als zweite wie links_wie."""
    gpos = ft["GPOS"].table
    for L in gpos.LookupList.Lookup:
        for st in L.SubTable:
            t = L.LookupType
            if t == 9: t = st.ExtensionLookupType; st = st.ExtSubTable
            if t != 2 or st.Format != 2: continue
            cov = st.Coverage.glyphs; c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
            c1.pop(neu, None); c2.pop(neu, None)
            if rechts_wie in cov:
                if neu not in cov: cov.append(neu)
                if rechts_wie in c1: c1[neu] = c1[rechts_wie]
            elif neu in cov:
                cov.remove(neu)
            if links_wie in c2: c2[neu] = c2[links_wie]
            st.Coverage.glyphs = sorted(cov, key=ft.getGlyphID)


def kapitaelchen(ft):
    cm = ft.getBestCmap(); sm, c2 = V3.gsub_map(ft, "smcp"), V3.gsub_map(ft, "c2sc")
    sc = lambda ch: sm[cm[ord(ch)]]
    gross_ss = c2[cm[0x1E9E]]
    sm[cm[0x00DF]] = gross_ss                            # ß → Kapitälchen-ẞ
    kern_setzen(ft, gross_ss, sc("s"), sc("b"))
    for cp, (a, b) in ((0x0133, "ij"), (0xFB01, "fi"), (0xFB02, "fl")):
        kern_setzen(ft, sm[cm[cp]], sc(b), sc(a))


def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s_ = rec.toUnicode()
            if VER_NEW not in s_: rec.string = s_.replace(VER_OLD, VER_NEW, 1)
    ft["head"].fontRevision = float(VER_NEW)


def main():
    ft = git_font(V3.VAR); vs = B.VarSrc(ft)
    g = vs.cmap[PROMILLE]
    ms, advs, luft = promille(vs)
    R.write_glyph(vs.vf, g, ms); R.set_advances(vs.vf, g, advs)
    lsb = int(round(B.ink(ms[vs.vf.locs.index(0.0)])[0]))
    ft["hmtx"][g] = (ft["hmtx"][g][0], lsb)
    kapitaelchen(ft); bump(ft)
    out = os.path.join(REPO, V3.VAR); ft.save(out); Lst.webfonts(out)
    print("Variabel: ‰ aus %% + Ring, Abstand %s, Vorschub %s" % (luft, advs))
    vf = TTFont(out); vs2 = B.VarSrc(vf); L = vs2.vf.locs
    a = R.advances(vs2.vf, g)
    for cut, w in CUTS.items():
        rel = V3.STAT % cut; st = git_font(rel)
        v = (w - 440) / 250 if w < 440 else (w - 440) / 285
        cs = B.rnd(vs2.vf.outline(g, v))
        k = next(k for k in range(len(L) - 1) if L[k] <= v <= L[k + 1])
        adv = int(round(a[k] + (a[k + 1] - a[k]) * (v - L[k]) / (L[k + 1] - L[k])))
        td = st["CFF "].cff.topDictIndex[0]; fds = td.FDArray if hasattr(td, "FDArray") else None
        sg = st.getBestCmap()[PROMILLE]
        SY.draw_into(st, td, fds, sg, lambda pen, cs=cs: B.draw(pen, cs), adv)
        kapitaelchen(st); bump(st)
        out = os.path.join(REPO, rel); st.save(out); Lst.webfonts(out)
        print("  %-9s ‰ Vorschub %d" % (cut, adv))
    print("v2.9 (intern %s) geschrieben." % VER_NEW)


if __name__ == "__main__":
    main()
