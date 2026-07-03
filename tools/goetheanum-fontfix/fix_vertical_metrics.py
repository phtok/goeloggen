#!/usr/bin/env python3
# Vertikale Metriken der ganzen Familie nach GF-Modell geradeziehen:
#   typo/hhea = Zeilenhöhe (750/-250/0), win = echte Tintengrenzen der GESUNDEN
#   Glyphen (familienweit einheitlich), USE_TYPO_METRICS an.
# Grund: eine kaputte Glyphe (U+01FA Ǻ, Akzente verrutscht bis y 1722) hatte
#   usWinAscent auf 1722 aufgebläht → 2.17× em Zeilenhöhe in Apps, die
#   USE_TYPO_METRICS ignorieren. Ausreisser werden gemeldet (Quelle reparieren),
#   fliessen aber NICHT in die win-Grenzen ein.
# Reproduzierbar; danach Webfonts/Office/ZIPs neu bauen. Idempotent.
import os, sys, glob, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
WF = os.path.join(ROOT, "Webfonts")
SANE_YMAX, SANE_YMIN = 1200, -350

def font_paths():
    return (sorted(glob.glob(os.path.join(ROOT, "Fonts", "Goetheanum-Schrift-v2.7-*.otf"))) +
            [os.path.join(ROOT, "Variable", "Goetheanum-Variabel-v2.7.otf")])

def healthy_bounds(path):
    f = TTFont(path); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    uni = {gn: cp for cp, gn in cmap.items()}
    ymaxs = []; ymins = []; outliers = []
    for gn in f.getGlyphOrder():
        p = BoundsPen(gs)
        try: gs[gn].draw(p)
        except Exception: continue
        if not p.bounds: continue
        _, ymn, _, ymx = p.bounds
        if ymx > SANE_YMAX or ymn < SANE_YMIN:
            cp = uni.get(gn); outliers.append((gn, "U+%04X" % cp if cp else "—", round(ymn), round(ymx)))
        else:
            ymaxs.append(ymx); ymins.append(ymn)
    return max(ymaxs), min(ymins), outliers

def main():
    paths = font_paths()
    # 1) familienweite gesunde Tintengrenzen + Ausreisser sammeln
    fam_ymax = 0; fam_ymin = 0; all_out = {}
    for p in paths:
        ymx, ymn, out = healthy_bounds(p)
        fam_ymax = max(fam_ymax, ymx); fam_ymin = min(fam_ymin, ymn)
        if out: all_out[os.path.basename(p)] = out
    win_asc = math.ceil(fam_ymax); win_desc = math.ceil(-fam_ymin)
    # 2) anwenden
    for p in paths:
        f = TTFont(p); os2 = f["OS/2"]; hhea = f["hhea"]
        hhea.ascent, hhea.descent, hhea.lineGap = os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap
        os2.usWinAscent, os2.usWinDescent = win_asc, win_desc
        os2.fsSelection |= (1 << 7)          # USE_TYPO_METRICS
        f.save(p)
        base = os.path.splitext(os.path.basename(p))[0]
        for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
            g = TTFont(p); g.flavor = flv; g.save(os.path.join(WF, sub, "%s.%s" % (base, flv)))
    # 3) Bericht
    print("== familienweite Metriken ==")
    print("  typo/hhea 750/-250/0 · win %d/%d · USE_TYPO_METRICS an" % (win_asc, win_desc))
    print("  Zeile ohne USE_TYPO: %.2f× em (vorher 2.17×)" % ((win_asc + win_desc) / 1000))
    print("== Ausreisser-Glyphen (in der Quelle reparieren) ==")
    if not all_out: print("  — keine —")
    for fn, out in all_out.items():
        for gn, u, ymn, ymx in out:
            print("  %-34s %-10s %-8s y %d .. %d" % (fn, gn, u, ymn, ymx))

if __name__ == "__main__":
    main()
