#!/usr/bin/env python3
"""Favicons erzeugen – Goetheanum-Bildmarke weiss im Kreis oder Quadrat, je Hausfarbe.

Aufruf (aus der Repo-Wurzel):  python3 tools/build_favicons.py .

Quelle der Wahrheit:
  · Standard der Werkzeugseiten: kreis-blau (Entscheid Inhaber 19. 11. 2026)
  · Marke:  assets/logos/goetheanum-marke.svg (Pfade und Lage im Kasten 28.3465)
  · Farben: design-system/tokens.json (Markenblau, Gold dunkel, Sektions- und
            Bereichsfarben in der Stufe ‹dunkel›: Weiss drauf, B01/B02)

Ergebnis je Variante  assets/favicons/<form>-<farbe>/ :
  favicon.svg · favicon.ico (16/32/48) · apple-touch-icon.png (180, immer volle
  Fläche – iOS rundet selbst) · icon-192.png · icon-512.png
dazu  assets/favicons/<form>-<farbe>.zip  und  assets/favicons/favicons.json.

Gerastert wird mit dem vorinstallierten Chromium (Playwright über node).
Idempotent: gleiche Eingaben ergeben byte-gleiche SVG/JSON/ZIP-Hüllen.
"""
import json, re, struct, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OUT = ROOT / "assets" / "favicons"
BOX = 28.3465

def tok(path):
    o = json.loads((ROOT / "design-system" / "tokens.json").read_text())["color"]
    for k in path.split("."):
        o = o[k]
    return o["$value"]

# Reihenfolge = Reihenfolge auf der Seite. Sektion ‹goetheanum› = Markenblau, darum nicht doppelt.
FARBEN = [
    ("blau",     "Goetheanum",            tok("blue")),
    ("gold",     "Gold",                  tok("gold-deep")),
    ("aas",      "Allgemeine Anthroposophie", tok("sektion-varianten.aas.dunkel")),
    ("js",       "Jugendsektion",         tok("sektion-varianten.js.dunkel")),
    ("mas",      "Mathematik und Astronomie", tok("sektion-varianten.mas.dunkel")),
    ("ms",       "Medizin",               tok("sektion-varianten.ms.dunkel")),
    ("nws",      "Naturwissenschaften",   tok("sektion-varianten.nws.dunkel")),
    ("ps",       "Pädagogik",             tok("sektion-varianten.ps.dunkel")),
    ("sbk",      "Bildende Künste",       tok("sektion-varianten.sbk.dunkel")),
    ("hpise",    "Inklusive soziale Entwicklung", tok("sektion-varianten.hpise.dunkel")),
    ("lws",      "Landwirtschaft",        tok("sektion-varianten.lws.dunkel")),
    ("srmk",     "Redende und Musizierende Künste", tok("sektion-varianten.srmk.dunkel")),
    ("ssw",      "Schöne Wissenschaften", tok("sektion-varianten.ssw.dunkel")),
    ("szw",      "Sozialwissenschaften",  tok("sektion-varianten.szw.dunkel")),
    ("buehne",   "Bühne",                 tok("bereich-varianten.buehne.dunkel")),
    ("bauadmin", "Bau-Administration",    tok("bereich-varianten.bauadmin.dunkel")),
]
FORMEN = [("kreis", "Kreis"), ("quadrat", "Quadrat")]

def lum(hexv):
    c = [int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def kontrast_weiss(hexv):
    return 1.05 / (lum(hexv) + 0.05)

PFADE = re.findall(r'<path d="([^"]+)"', (ROOT / "assets/logos/goetheanum-marke.svg").read_text())
assert len(PFADE) == 3, "goetheanum-marke.svg: drei Pfade erwartet"

RUNDUNG = BOX * 0.08   # Quadrat minimal gerundet (Entscheid Inhaber 19. 11. 2026): 1.3 px bei 16 px

def svg(form, farbe, voll=False):
    if voll:      # apple-touch-icon: volle Fläche, iOS rundet selbst
        grund = f'<rect width="{BOX}" height="{BOX}" fill="{farbe}"/>'
    elif form == "quadrat":
        grund = f'<rect width="{BOX}" height="{BOX}" rx="{RUNDUNG:.4f}" fill="{farbe}"/>'
    else:
        grund = f'<circle cx="{BOX/2:.4f}" cy="{BOX/2:.4f}" r="{BOX/2:.4f}" fill="{farbe}"/>'
    marke = "".join(f'<path d="{d}"/>' for d in PFADE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX} {BOX}" width="64" height="64">'
            f'{grund}<g fill="#ffffff">{marke}</g></svg>\n')

def ico(pngs):
    """ICO mit eingebetteten PNG (Vista+, alle Browser)."""
    kopf = struct.pack("<HHH", 0, 1, len(pngs))
    eintraege, daten, off = b"", b"", 6 + 16 * len(pngs)
    for groesse, png in pngs:
        g = 0 if groesse >= 256 else groesse
        eintraege += struct.pack("<BBBBHHII", g, g, 0, 0, 1, 32, len(png), off)
        daten += png
        off += len(png)
    return kopf + eintraege + daten

RASTER = r"""
const { chromium } = require('playwright');
const jobs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const j of jobs) {
    await p.setViewportSize({ width: j.size, height: j.size });
    const src = 'data:image/svg+xml;base64,' + Buffer.from(j.svg).toString('base64');
    await p.setContent(`<html><body style="margin:0;background:transparent"><img src="${src}" width="${j.size}" height="${j.size}" style="display:block"></body></html>`);
    await p.waitForFunction(() => document.images[0].complete);
    await p.screenshot({ path: j.out, omitBackground: true, clip: { x: 0, y: 0, width: j.size, height: j.size } });
  }
  await b.close();
})();
"""

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs, varianten = [], []
    for slug, name, farbe in FARBEN:
        k = kontrast_weiss(farbe)
        assert k >= 4.5, f"{slug}: Weiss auf {farbe} nur {k:.2f}:1 (B02 verlangt hier ≥4.5)"
        for form, formname in FORMEN:
            d = OUT / f"{form}-{slug}"
            d.mkdir(exist_ok=True)
            s = svg(form, farbe)
            (d / "favicon.svg").write_text(s)
            for g in (16, 32, 48, 192, 512):
                jobs.append({"svg": s, "size": g, "out": str(d / f"_{g}.png" if g < 192 else d / f"icon-{g}.png")})
            jobs.append({"svg": svg(form, farbe, voll=True), "size": 180, "out": str(d / "apple-touch-icon.png")})
            varianten.append({"id": f"{form}-{slug}", "form": form, "farbe": slug, "name": name,
                              "hex": farbe, "kontrast": round(k, 2)})
    subprocess.run(["node", "-e", RASTER], input=json.dumps(jobs).encode(), check=True, cwd=ROOT)

    for v in varianten:
        d = OUT / v["id"]
        teile = [(g, (d / f"_{g}.png").read_bytes()) for g in (16, 32, 48)]
        (d / "favicon.ico").write_bytes(ico(teile))
        for g in (16, 32, 48):
            (d / f"_{g}.png").unlink()
        with zipfile.ZipFile(OUT / f"{v['id']}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for n in ("favicon.svg", "favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png"):
                info = zipfile.ZipInfo(f"{v['id']}/{n}", date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, (d / n).read_bytes())

    (OUT / "favicons.json").write_text(json.dumps(
        {"$beschreibung": "Erzeugt von tools/build_favicons.py – nicht von Hand ändern.",
         "formen": [{"id": f, "name": n} for f, n in FORMEN],
         "farben": [{"id": s, "name": n, "hex": h} for s, n, h in FARBEN],
         "varianten": varianten}, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(varianten)} Varianten in {OUT.relative_to(ROOT)}/")

if __name__ == "__main__":
    main()
