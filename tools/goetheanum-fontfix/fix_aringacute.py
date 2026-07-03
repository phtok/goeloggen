#!/usr/bin/env python3
"""Reparatur der Glyphe Ǻ (U+01FA) und Aufräumen verwaister Ausreisser-Glyphen.

Befund (aus #204): U+01FA (Aringacute) ist in mehreren statischen Schnitten und
im Variablen defekt — dieselbe kaputte Kontur (Bounds 20,−450,531,1722) wurde in
Klar/Leise/Ruhig und den Variablen kopiert. Deutlich/Laut liegen zwar in sanen
Grenzen, widersprechen sich aber (ymax 1126 vs 836): ein Ǻ MIT Akut über dem Ring
muss höher als das Å sein — Lauts 836 ≈ Å ist selbst verdächtig. Die QUELLE ist
also uneinheitlich, nicht bloss „vier Schnitte".

Reproduzierbare Wiederherstellung je Schnitt aus GESUNDEN Bestandteilen DESSELBEN
Schnitts, damit Strichstärke/Charakter erhalten bleiben:

    Ǻ  =  Å (Aring, gesund)  +  Akut (aus Á/Aacute), angehoben um die Ringhöhe
          (Aring_ymax − A_ymax), sodass der Akut den Ring genauso überragt wie
          zuvor das blosse A.

Verwaiste Ausreisser (NICHT im cmap, z. B. cid00612) mit Bounds ausserhalb der
sanen Grenzen werden geleert (sie werden nie gerendert, blähten nur die Box).

Nur statische CFF-Schnitte. Der Variable Font (glyf + gvar) braucht eine
MASTER-basierte Neuinterpolation und wird hier bewusst NICHT angefasst — ein
Post-hoc-Patch einer einzelnen Instanz zerstörte die Achsen-Interpolation.

WICHTIG — Grenze der Automatik: Die rekonstruierte Akzentform ist BOUNDS-
verifiziert, aber NICHT visuell abgenommen. Vor einem Release muss ein Designer
die Ǻ-Form prüfen; die eigentliche Kur gehört in den Design-Quellfont (CLAUDE.md:
Schrift-Widersprüche meldet die Maschine, der Mensch entscheidet).

Aufruf:
    fix_aringacute.py            # nur Bericht (Bounds aller Kandidaten, alle Schnitte)
    fix_aringacute.py --apply    # schreibt die statischen OTFs; danach Webfonts/ZIP neu
Idempotent (erneuter Lauf auf schon gesunden Ǻ ändert nichts).
"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
SANE_YMAX, SANE_YMIN = 1200, -350          # gleiche Schwelle wie fix_vertical_metrics.py
U_A, U_ARING, U_AACUTE, U_ARINGACUTE = 0x41, 0xC5, 0xC1, 0x1FA


def static_paths():
    return sorted(glob.glob(os.path.join(ROOT, "Fonts", "Goetheanum-Schrift-v2.7-*.otf")))


def variable_path():
    return os.path.join(ROOT, "Variable", "Goetheanum-Variabel-v2.7.otf")


def gbounds(gs, gn):
    p = BoundsPen(gs)
    try:
        gs[gn].draw(p)
    except Exception:
        return None
    return p.bounds


def contours(gs, gn):
    """Glyphe als Liste von Konturen; jede Kontur = Liste von (op, pts)."""
    rp = RecordingPen(); gs[gn].draw(rp)
    out, cur = [], []
    for op, args in rp.value:
        cur.append((op, args))
        if op == "closePath" or op == "endPath":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def contour_ymin(c):
    ys = [pt[1] for op, args in c for pt in args]
    return min(ys) if ys else 0


def replay(pen, conts, dy=0.0):
    for c in conts:
        for op, args in c:
            moved = tuple((x, y + dy) for (x, y) in args)
            getattr(pen, op)(*moved) if op not in ("closePath", "endPath") else getattr(pen, op)()


def cff_charstrings(ft):
    cff = ft["CFF "].cff
    return cff[cff.fontNames[0]].CharStrings


def rebuild_aringacute(ft):
    """Ǻ neu aus Å + angehobenem Akut. Gibt (alt_bounds, neu_bounds) oder None."""
    gs = ft.getGlyphSet(); cmap = ft.getBestCmap()
    for u in (U_A, U_ARING, U_AACUTE, U_ARINGACUTE):
        if u not in cmap:
            return None
    gnA, gnAring, gnAacute, gnDst = (cmap[u] for u in (U_A, U_ARING, U_AACUTE, U_ARINGACUTE))
    bA, bAring = gbounds(gs, gnA), gbounds(gs, gnAring)
    if not bA or not bAring:
        return None
    ring_h = bAring[3] - bA[3]                      # Ringhöhe über der A-Oberkante
    a_top = bA[3]
    aacute = [c for c in contours(gs, gnAacute) if contour_ymin(c) >= a_top - 40]  # Akut-Kontur(en)
    base = contours(gs, gnAring)                    # A + korrekt platzierter Ring
    width = ft["hmtx"][gnDst][0]
    pen = T2CharStringPen(width, gs)
    replay(pen, base, 0.0)
    replay(pen, aacute, ring_h)                     # Akut über den Ring heben
    old = gbounds(gs, gnDst)
    cff_charstrings(ft)[gnDst].program = pen.getCharString().program
    new = gbounds(ft.getGlyphSet(), gnDst)
    return old, new


def blank_orphans(ft):
    """Verwaiste (nicht im cmap) Glyphen mit unsanen Bounds leeren."""
    gs = ft.getGlyphSet(); mapped = set(ft.getBestCmap().values())
    cs = cff_charstrings(ft); cleaned = []
    for gn in ft.getGlyphOrder():
        if gn in mapped or gn == ".notdef":
            continue
        b = gbounds(gs, gn)
        if b and (b[3] > SANE_YMAX or b[1] < SANE_YMIN):
            width = ft["hmtx"][gn][0]
            cs[gn].program = T2CharStringPen(width, gs).getCharString().program
            cleaned.append((gn, tuple(round(v) for v in b)))
    return cleaned


def report():
    print("Bericht — Ǻ (U+01FA) und verwaiste Ausreisser je Schnitt\n")
    for p in static_paths() + [variable_path()]:
        ft = TTFont(p); gs = ft.getGlyphSet(); cmap = ft.getBestCmap()
        name = os.path.basename(p); cff = "CFF " in ft
        gn = cmap.get(U_ARINGACUTE)
        b = gbounds(gs, gn) if gn else None
        bad = b and (b[3] > SANE_YMAX or b[1] < SANE_YMIN)
        flag = "  ← DEFEKT" if bad else ""
        print(f"  {name:42} Ǻ={tuple(round(v) for v in b) if b else None}{flag}{'  [variabel: nur Master-Rebuild]' if not cff else ''}")
        mapped = set(cmap.values())
        for on in ft.getGlyphOrder():
            if on in mapped or on == ".notdef":
                continue
            ob = gbounds(gs, on)
            if ob and (ob[3] > SANE_YMAX or ob[1] < SANE_YMIN):
                print(f"      verwaist {on}: {tuple(round(v) for v in ob)}")


def apply():
    changed = 0
    for p in static_paths():                        # nur statische CFF-Schnitte
        ft = TTFont(p); gs = ft.getGlyphSet(); cmap = ft.getBestCmap()
        gn = cmap.get(U_ARINGACUTE); b = gbounds(gs, gn) if gn else None
        name = os.path.basename(p); touched = False
        if b and (b[3] > SANE_YMAX or b[1] < SANE_YMIN):
            r = rebuild_aringacute(ft)
            if r:
                old, new = r
                print(f"  {name}: Ǻ {tuple(round(v) for v in old)} → {tuple(round(v) for v in new)}")
                touched = True
        orphans = blank_orphans(ft)
        for on, ob in orphans:
            print(f"  {name}: verwaist {on} {ob} → geleert")
            touched = True
        if touched:
            ft.save(p); changed += 1
    print(f"\n{changed} statische Schnitte geschrieben." if changed else "\nNichts zu tun (bereits gesund).")
    if changed:
        print("Jetzt Webfonts (woff/woff2), Office-TTF und das Komplett-ZIP neu packen.")
        print("Variabler Font: Ǻ separat über den Master-Rebuild (build_variable) korrigieren.")


if __name__ == "__main__":
    (apply if "--apply" in sys.argv[1:] else report)()
