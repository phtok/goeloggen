#!/usr/bin/env python3
# Satzprobe Fassung 2.96 (Pfeile) aus den echten Schriftdateien: heute (2.94,
# aus git) und neu, in Gebrauchsgrösse 16 · 20 · 24 px bei 1×, schmal 375 und
# breit 1280. Schreibt docs/befunde/pfeile-296-satzprobe-{375,1280}.png.
# Aufruf:  python3 proof_v296.py      (braucht Playwright/Chromium)
import os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts/woff2")
ALT = "b4756f9"
NAMEN = ("Goetheanum-Schrift-v2.9-Klar", "Goetheanum-Schrift-v2.9-Laut", "Goetheanum-Pfeile-v2.9")

TEXT = "Ausgang →&nbsp;Saal&nbsp;12 · Foyer&nbsp;↱ · Garderobe&nbsp;↰ · ←&nbsp;zurück"
ZEICHEN = "← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ↱ ⬎ ↲ ⬑ ↰ ⬏ ↳ ⬐"


def seite(tmp):
    css = []
    for n in NAMEN:
        alt = os.path.join(tmp, "alt-%s.woff2" % n)
        open(alt, "wb").write(subprocess.run(
            ["git", "-C", REPO, "show", "%s:assets/fonts/goetheanum/Webfonts/woff2/%s.woff2" % (ALT, n)],
            capture_output=True, check=True).stdout)
        k = n.split("-")[-1]
        css.append('@font-face{font-family:"neu %s";src:url("file://%s/%s.woff2")}' % (k, WF, n))
        css.append('@font-face{font-family:"alt %s";src:url("file://%s")}' % (k, alt))
    zeilen = []
    for px in (16, 20, 24):
        for st in ("alt", "neu"):
            for cut in ("Klar", "Laut"):
                zeilen.append('<p style="font:%dpx \'%s %s\'"><span class="m">%s %s %d</span><br>%s</p>'
                              % (px, st, cut, "heute" if st == "alt" else "2.96", cut, px, TEXT))
    pf = []
    for px in (16, 20, 24):
        for st in ("alt", "neu"):
            pf.append('<p><span class="m">Pfeil-Schrift %s %d</span><br><span style="font:%dpx \'%s v2.9\'">'
                      '6 t u h 2 0 q e o ü s ö</span><br><span style="font:%dpx \'%s v2.9\'">& T U H " = Q E O Ü S Ö</span></p>'
                      % ("heute" if st == "alt" else "2.96", px, px, st, px, st))
    return ('<!doctype html><meta charset="utf-8"><style>%s'
            'body{margin:16px;background:#fff;color:#1a1a1a;font-family:"neu Klar"}'  # ds-ok: Probebild
            'p{margin:0 0 14px;line-height:1.5}.m{font:13px "neu Klar";color:#666}'  # ds-ok: Probebild
            'h2{font:20px "neu Laut";margin:24px 0 8px}.z{font:24px "neu Klar";letter-spacing:.1em}'
            '.z2{font:24px "neu Laut";letter-spacing:.1em}</style>'
            '<h2>Textschrift</h2><p class="z">%s</p><p class="z2">%s</p>%s<h2>Goetheanum Pfeile</h2>%s'
            % ("".join(css), ZEICHEN, ZEICHEN, "".join(zeilen), "".join(pf)))


def main():
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    html = os.path.join(tmp, "probe.html"); open(html, "w", encoding="utf-8").write(seite(tmp))
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": "/opt/pw-browsers/chromium"} if os.path.exists("/opt/pw-browsers/chromium") and not os.path.isdir("/opt/pw-browsers/chromium") else {}))
        for w in (375, 1280):
            pg = b.new_page(viewport={"width": w, "height": 800}, device_scale_factor=1)
            pg.goto("file://" + html); pg.wait_for_timeout(400)
            out = os.path.join(REPO, "docs/befunde/pfeile-296-satzprobe-%d.png" % w)
            pg.screenshot(path=out, full_page=True); print("geschrieben:", os.path.relpath(out, REPO))
        b.close()


if __name__ == "__main__":
    main()
