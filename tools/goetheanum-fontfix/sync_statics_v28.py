#!/usr/bin/env python3
# Überträgt die Reparaturen des Variable Font (repair_variable_v28.py) in die
# statischen Schnitte. Je Schnitt wird die reparierte Variable an seinem
# Gewicht (usWeightClass) instanziert und jede reparierte Glyphe – über cmap
# und GSUB des Schnitts aufgelöst, denn in Klar liegen andere CIDs – ersetzt:
#   - Ruhig und Deutlich sind ganz aus der Variable instanziert → immer.
#   - Leise, Klar, Laut stammen aus der v1.4.43-Linie und tragen einige eigene,
#     gesunde Formen (z. B. die case-Klammern in Laut). Ersetzt wird nur, wo die
#     Glyphe der alten Variable gleicht (also deren Schaden trägt) oder der
#     reparierten schon nahe ist; eigene Formen bleiben (Ausnahme: IMMER).
# Der Vorschub kommt aus der Instanz (⁄ wird so klein wie in der Variable).
# Vergleichsbasis «alte Variable» ist der Stand vor der Reparatur aus git
# (Standard: die letzte Variable-Datei in HEAD). Schreibt die Webfonts
# (woff/woff2) der Schnitte mit. Idempotent.
# Aufruf:  python3 sync_statics_v28.py [ALT-VARIABLE.otf]
import os, sys, glob, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.areaPen import AreaPen
import repair_variable_v28 as R
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
VARDIR = os.path.join(REPO, "assets/fonts/goetheanum/Variable")
AUS_VARIABLE = ("Ruhig", "Deutlich")
# eigene Formen, die selbst beschädigt sind (gemessen und mit dem Auge geprüft,
# 29. 10. 2026): „ in Leise (schmaler als in Flüstern, die Striche kreuzen),
# Kapitälchen-ű in Klar (Doppelakut verschmilzt), Kapitälchen-û in Klar und
# Laut (Zirkumflex verrutscht wie in der Variable).
IMMER = {("Leise", 0x201E), ("Klar", ("smcp", 0x0171)),
         ("Klar", ("smcp", 0x00FB)), ("Laut", ("smcp", 0x00FB))}
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")

def webfonts(path):
    b = os.path.splitext(os.path.basename(path))[0]
    for flv in ("woff", "woff2"):
        f = TTFont(path); f.flavor = flv; f.save(os.path.join(WF, flv, "%s.%s" % (b, flv)))


def keys():
    return (R.CROSSED + R.HALF_RIGID + R.FLAT_TOP + [a[0] for a in R.ACCENT] +
            [R.RING_ACUTE] + [("case", c) for c in R.CASE] + [R.BULLET, R.FRACTION])

def resolve(ft, k):
    cm = ft.getBestCmap()
    if isinstance(k, tuple): return R.gsub_single(ft, cm[k[1]], k[0])
    return cm[k]

def measure(ft, g):
    gs = ft.getGlyphSet(); b = BoundsPen(gs); gs[g].draw(b); a = AreaPen(gs); gs[g].draw(a)
    return b.bounds, abs(a.value)

def close(m1, m2, dmax, frac):
    if not m1[0] or not m2[0]: return m1[0] == m2[0]
    return (max(abs(x - y) for x, y in zip(m1[0], m2[0])) <= dmax and
            abs(m1[1] - m2[1]) <= frac * max(m2[1], 1) + 5)

def old_variable():
    if len(sys.argv) > 1: return sys.argv[1]
    rel = os.path.relpath(sorted(glob.glob(os.path.join(VARDIR, "Goetheanum-Variabel-v*.otf")))[-1], REPO)
    names = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", "HEAD", os.path.dirname(rel) + "/"],
                           capture_output=True, text=True).stdout.split()
    src = [n for n in names if os.path.basename(n).startswith("Goetheanum-Variabel-v")][-1]
    blob = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + src], capture_output=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return tmp.name

def main():
    new_path = sorted(glob.glob(os.path.join(VARDIR, "Goetheanum-Variabel-v*.otf")))[-1]
    old_path = old_variable()
    for path in sorted(glob.glob(os.path.join(FONTS, "Goetheanum-Schrift-v*-*.otf"))):
        cut = os.path.basename(path)[:-4].split("-")[-1]
        st = TTFont(path, recalcTimestamp=False); w = st["OS/2"].usWeightClass
        old = TTFont(old_path); instantiateVariableFont(old, {"wght": w}, inplace=True)
        new = TTFont(new_path); instantiateVariableFont(new, {"wght": w}, inplace=True)
        td = st["CFF "].cff.topDictIndex[0]
        fds = td.FDArray if hasattr(td, "FDArray") else None
        ngs = new.getGlyphSet(); done = []; kept = []
        for k in keys():
            gs_, go, gn = resolve(st, k), resolve(old, k), resolve(new, k)
            ms = measure(st, gs_)
            if cut not in AUS_VARIABLE and (cut, k) not in IMMER and not (close(ms, measure(old, go), 2, 0.01) or
                                                close(ms, measure(new, gn), 6, 0.05)):
                kept.append(gs_); continue
            cs = td.CharStrings[gs_]
            priv = fds[td.FDSelect[st.getGlyphID(gs_)]].Private if fds else td.Private
            adv = new["hmtx"][gn][0]
            pen = T2CharStringPen(adv - priv.nominalWidthX, None)
            ngs[gn].draw(pen)
            cs.program = pen.getCharString(private=priv, globalSubrs=td.GlobalSubrs).program
            cs.bytecode = None
            b = BoundsPen(ngs); ngs[gn].draw(b)
            st["hmtx"][gs_] = (adv, int(round(b.bounds[0])) if b.bounds else 0)
            done.append(gs_)
        st.save(path); webfonts(path)
        print("  %-8s %3d ersetzt, eigene Form behalten: %s" % (cut, len(done), " ".join(kept) or "–"))
    print("Statische Schnitte nachgezogen.")

if __name__ == "__main__":
    main()
