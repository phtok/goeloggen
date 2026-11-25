#!/usr/bin/env python3
# Vorher/Nachher-Blatt zu Fassung 2.93, im Browser gerendert (Chromium):
#   1 ‰ in allen Schnitten und Variable-Stufen, normal und mit synthetischem
#     Fett (der Browser fettet nach dem Drehsinn der Konturen; eine verkehrte
#     Kontur läuft dabei zu statt auf),
#   2 Kapitälchen (smcp, c2sc) der neuen Zeichen in allen Schnitten und Stufen.
# Vorher = Fassung 2.92 aus git (SOURCE_REV), nachher = die Dateien auf der Platte.
# Schreibt docs/befunde/konturrichtung-kapitaelchen-2026-11-25-{promille,kapitaelchen}.png
# Aufruf:  python3 proof_v293.py
import os, sys, subprocess, tempfile, base64
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_v293 as V

ROOT = V.ROOT; REPO = V.REPO
OUT = os.path.join(REPO, "docs/befunde/konturrichtung-kapitaelchen-2026-11-25-%s.png")
CUTS = V.CUTS
STUFEN = (190, 265, 350, 440, 580, 680, 725)
KAP = "ǎ ǐ ǒ ǔ ǧ ǩ ǫ ǹ ȟ ȯ ȳ ḃ ḋ ḍ ḏ ḑ ḟ ḡ ḣ ḥ ḫ ḷ ḹ ḻ ḿ ṁ ṃ ṅ ṇ ṉ ṗ ṛ ṝ ṟ ṡ ṣ ṫ ṭ ṯ ṽ ẁ ẃ ẅ ẓ ẗ ạ ẹ ẽ ị ọ ụ ỳ ỹ ĳ ə ɛ ɨ ɲ ʉ ȷ µ μ π ß ﬁ ﬂ"
PROBE = "Saṃsāra · Dvaṇḍva · Kṛṣṇa · Bǎijiā · Strasse ß · ﬁﬂ · ĳs · Əli · π"
VERSAL = "ǍǏǑǓ ẞ Ĳ ƏƐƗƝɄ ḌṆṢṬ İ"


def b64(data): return base64.b64encode(data).decode()


def alt(rel):
    return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (V.SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout


def faces():
    css = []
    for tag, read in (("vor", alt), ("nach", lambda r: open(os.path.join(REPO, r), "rb").read())):
        for cut in CUTS:
            rel = "assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.9-%s.woff2" % cut
            # Gewicht 100 deklariert: font-weight 700 erzwingt synthetisches Fett
            css.append("@font-face{font-family:'%s-%s';src:url(data:font/woff2;base64,%s);font-weight:100}"
                       % (tag, cut, b64(read(rel))))
        rel = "assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Variabel-v2.9.woff2"
        css.append("@font-face{font-family:'%s-Var';src:url(data:font/woff2;base64,%s);font-weight:100}"
                   % (tag, b64(read(rel))))
    return "\n".join(css)


STIL = """
body{margin:0;padding:28px 36px;background:#fff;color:#111;font:15px/1.4 'Source Sans 3',sans-serif}
h1{font:600 20px 'Source Sans 3',sans-serif;margin:0 0 4px}
p.k{margin:0 0 18px;color:#444}
table{border-collapse:collapse}
td,th{padding:4px 10px;vertical-align:middle;text-align:left}
th{font-weight:600;color:#444;white-space:nowrap}
tr+tr td,tr+tr th{border-top:1px solid #ddd}
.z{font-size:76px;line-height:1.05;font-synthesis:weight}
.fett{font-weight:700}
.s{font-size:30px;line-height:1.35;font-variant-caps:small-caps;font-synthesis:none}
.c{font-size:30px;line-height:1.35;font-variant-caps:all-small-caps;font-synthesis:none}
.n{font-size:30px;line-height:1.35;font-synthesis:none}
.vor{color:#9a1c1c}
.nach{color:#111}
"""


def var(w): return "font-family:'%%s-Var';font-variation-settings:'wght' %d" % w


def promille():
    rows = []
    zeilen = [(c, "font-family:'%%s-%s'" % c) for c in CUTS] + [("Var %d" % w, var(w)) for w in STUFEN]
    for label, st in zeilen:
        cells = []
        for tag in ("vor", "nach"):
            s = st % tag
            cells.append("<td class='z %s' style=\"%s\">‰%%</td><td class='z fett %s' style=\"%s\">‰</td>"
                         % (tag, s, tag, s))
        rows.append("<tr><th>%s</th>%s</tr>" % (label, "".join(cells)))
    return ("<h1>‰: oberer Ring, Fassung 2.92 (rot) und 2.93 (schwarz)</h1>"
            "<p class='k'>Je links normal, rechts mit synthetischem Fett des Browsers. "
            "Verkehrt gedrehte Konturen laufen beim Fetten zu.</p>"
            "<table><tr><th></th><th colspan=2>2.92</th><th colspan=2>2.93</th></tr>%s</table>"
            % "".join(rows))


def kapitaelchen():
    rows = []
    zeilen = [(c, "font-family:'%%s-%s'" % c) for c in CUTS] + [("Var %d" % w, var(w)) for w in STUFEN]
    for label, st in zeilen:
        rows.append("<tr><th>%s</th><td class='s vor' style=\"%s\">%s</td></tr>" % (label, st % "vor", PROBE))
        rows.append("<tr><th></th><td class='s nach' style=\"%s\">%s</td></tr>" % (st % "nach", PROBE))
    alle = []
    for label, st in (("Klar", "font-family:'%s-Klar'"), ("Laut", "font-family:'%s-Laut'")):
        for tag in ("vor", "nach"):
            alle.append("<tr><th>%s %s</th><td class='n %s' style=\"%s\">%s</td></tr>"
                        % (label, "2.92" if tag == "vor" else "2.93", tag, st % tag, KAP.replace(" ", "")))
            alle.append("<tr><th></th><td class='s %s' style=\"%s\">%s</td></tr>" % (tag, st % tag, KAP))
            alle.append("<tr><th></th><td class='c %s' style=\"%s\">%s</td></tr>" % (tag, st % tag, VERSAL))
    return ("<h1>Kapitälchen: Fassung 2.92 (rot) und 2.93 (schwarz)</h1>"
            "<p class='k'>smcp im Satz, je Schnitt und Variable-Stufe. Darunter alle neuen Zeichen: "
            "Gemeine, Kapitälchen (smcp), Versalien als Kapitälchen (c2sc).</p>"
            "<table>%s</table><br><table>%s</table>" % ("".join(rows), "".join(alle)))


def shot(html, path, width):
    from playwright.sync_api import sync_playwright
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(html); tmp.close()
    with sync_playwright() as p:
        try: b = p.chromium.launch()
        except Exception: b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": width, "height": 800}, device_scale_factor=1)
        pg.goto("file://" + tmp.name); pg.wait_for_timeout(400)
        pg.screenshot(path=path, full_page=True); b.close()
    os.unlink(tmp.name)


def main():
    head = "<!doctype html><meta charset=utf-8><style>%s\n%s</style>" % (faces(), STIL)
    shot(head + promille(), OUT % "promille", 760)
    shot(head + kapitaelchen(), OUT % "kapitaelchen", 1500)
    print("geschrieben:", OUT % "promille", OUT % "kapitaelchen")


if __name__ == "__main__":
    main()
