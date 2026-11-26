#!/usr/bin/env python3
# Vorher/Nachher-Blatt zu Fassung 2.94 (Chromium): ‰ in allen Schnitten und
# Variable-Stufen neben % und «oo», Kapitälchen-ẞ im Satz.
# Vorher = Fassung 2.93 aus git, nachher = die Dateien auf der Platte.
# Schreibt docs/befunde/konturrichtung-kapitaelchen-2026-11-26-promille.png
# Aufruf:  python3 proof_v294.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_v293 as V
import build_v294 as V4
import proof_v293 as P

V.SOURCE_REV = V4.SOURCE_REV
OUT = os.path.join(P.REPO, "docs/befunde/konturrichtung-kapitaelchen-2026-11-26-promille.png")


def main():
    zeilen = [(c, "font-family:'%%s-%s'" % c) for c in P.CUTS] + [("Var %d" % w, P.var(w)) for w in P.STUFEN]
    rows = []
    for label, st in zeilen:
        cells = "".join("<td class='z %s' style=\"%s\">3,5‰ 12%% oo</td>" % (t, st % t) for t in ("vor", "nach"))
        rows.append("<tr><th>%s</th>%s</tr>" % (label, cells))
    satz = "".join("<tr><th>%s</th><td colspan=2 class='s %s' style=\"font-family:'%s-Klar'\">Strauß · Weiß · Großmann</td></tr>"
                   % ("2.93" if t == "vor" else "2.94", t, t) for t in ("vor", "nach"))
    html = ("<!doctype html><meta charset=utf-8><style>%s\n%s .z{font-size:64px;font-synthesis:none;white-space:nowrap}</style>"
            "<h1>‰ und Kapitälchen-ẞ: Fassung 2.93 (rot) und 2.94 (schwarz)</h1>"
            "<p class='k'>‰ aus dem %% der Schrift plus zweitem Ring; Abstand wie zwei o, Ringe leichter.</p>"
            "<table><tr><th></th><th>2.93</th><th>2.94</th></tr>%s%s</table>"
            % (P.faces(), P.STIL, "".join(rows), satz))
    P.shot(html, OUT, 1100)
    print("geschrieben:", OUT)


if __name__ == "__main__":
    main()
