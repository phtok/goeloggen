#!/usr/bin/env python3
"""Begleitschriften-Probe: Kandidaten holen, auf die Mustertexte zuschneiden.

Baut die woff2-Subsets für begleitschriften.html nach
assets/fonts/schriftsysteme/. Je Kandidat zwei statische Schnitte:
Text (400) und Titel (nächster Schnitt zu Deutlich 580; variable Schriften
werden genau auf 580 instanziert). Der Zeichenvorrat kommt aus den Seiten
selbst – wer einen Mustertext ändert, lässt das Skript neu laufen.

    pip install fonttools brotli
    python3 tools/schriftsysteme-probe.py .

Quellen: google/fonts (ofl/…), bBoxType/FiraGO, vahanhovh/mardoto.
Lizenzen und Reserved Font Names: docs/schriften-verteilung.md.
"""
import html, io, re, sys, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

RAW = "https://raw.githubusercontent.com"
GF = RAW + "/google/fonts/main/ofl/"

# slug: (Quelle, Text-Datei, Titel-Datei, Titel-Gewicht falls variabel)
# Quelle "gf:<ordner>" → google/fonts; sonst volle URL-Basis.
KANDIDATEN = {
    # Noto als Lese-Grotesk für alle Systeme (lesetext-noto.html)
    "notosans":        ("gf:notosans", "NotoSans[wdth,wght].ttf", None),
    "notoarabic":      ("gf:notosansarabic", "NotoSansArabic[wdth,wght].ttf", None),
    # Griechisch (Source Sans 3 kommt aus dem Repo)
    "firasans":        ("gf:firasans", "FiraSans-Regular.ttf", "FiraSans-SemiBold.ttf"),
    "commissioner":    ("gf:commissioner", "Commissioner[FLAR,VOLM,slnt,wght].ttf", None),
    "ibmplexsans":     ("gf:ibmplexsans", "IBMPlexSans[wdth,wght].ttf", None),
    # Hebräisch
    "assistant":       ("gf:assistant", "Assistant[wght].ttf", None),
    "heebo":           ("gf:heebo", "Heebo[wght].ttf", None),
    "ibmplexhebrew":   ("gf:ibmplexsanshebrew", "IBMPlexSansHebrew-Regular.ttf", "IBMPlexSansHebrew-SemiBold.ttf"),
    "notohebrew":      ("gf:notosanshebrew", "NotoSansHebrew[wdth,wght].ttf", None),
    # Georgisch
    "notogeorgian":    ("gf:notosansgeorgian", "NotoSansGeorgian[wdth,wght].ttf", None),
    "firago":          (RAW + "/bBoxType/FiraGO/master/Fonts/FiraGO_TTF_1001/Roman/", "FiraGO-Regular.ttf", "FiraGO-SemiBold.ttf"),
    "googlesans":      ("gf:googlesans", "GoogleSans[GRAD,opsz,wght].ttf", None),
    # Armenisch
    "notoarmenian":    ("gf:notosansarmenian", "NotoSansArmenian[wdth,wght].ttf", None),
    "mardoto":         (RAW + "/vahanhovh/mardoto/master/fonts/ttf/", "Mardoto-Regular.ttf", "Mardoto-Medium.ttf"),
    # Chinesisch
    "sourcehansc":     ("gf:notosanssc", "NotoSansSC[wght].ttf", None),
    "sourcehanserifsc":("gf:notoserifsc", "NotoSerifSC[wght].ttf", None),
    "zcoolxiaowei":    ("gf:zcoolxiaowei", "ZCOOLXiaoWei-Regular.ttf", "ZCOOLXiaoWei-Regular.ttf"),
    # Japanisch
    "sourcehanjp":     ("gf:notosansjp", "NotoSansJP[wght].ttf", None),
    "zenkaku":         ("gf:zenkakugothicnew", "ZenKakuGothicNew-Regular.ttf", "ZenKakuGothicNew-Medium.ttf"),
    "ibmplexjp":       ("gf:ibmplexsansjp", "IBMPlexSansJP-Regular.ttf", "IBMPlexSansJP-SemiBold.ttf"),
    "bizudp":          ("gf:bizudpgothic", "BIZUDPGothic-Regular.ttf", "BIZUDPGothic-Bold.ttf"),
    # Koreanisch
    "sourcehankr":     ("gf:notosanskr", "NotoSansKR[wght].ttf", None),
    "ibmplexkr":       ("gf:ibmplexsanskr", "IBMPlexSansKR-Regular.ttf", "IBMPlexSansKR-SemiBold.ttf"),
    "gothica1":        ("gf:gothica1", "GothicA1-Regular.ttf", "GothicA1-SemiBold.ttf"),
}
TITEL_WGHT = 580  # Deutlich


def holen(quelle, datei, cache):
    basis = GF + quelle[3:] + "/" if quelle.startswith("gf:") else quelle
    ziel = cache / (quelle.replace("/", "_").replace(":", "_") + "__" + datei)
    if not ziel.exists():
        url = basis + urllib.request.quote(datei)
        print("  holen", url)
        ziel.write_bytes(urllib.request.urlopen(url).read())
    return ziel


def zeichen(seiten) -> str:
    t = " ".join(s.read_text(encoding="utf-8") for s in seiten if s.exists())
    t = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    basis = "".join(chr(c) for c in range(0x20, 0x7F)) + "–—‹›«»„“”’…·  "
    return "".join(sorted(set(t + basis)))


def schneiden(font: TTFont, text: str, ziel: Path):
    opt = subset.Options()
    opt.flavor = "woff2"
    opt.layout_features = ["*"]
    opt.name_IDs = ["*"]          # Copyright, Lizenz, RFN bleiben im Subset
    opt.name_languages = ["*"]
    opt.notdef_outline = True
    s = subset.Subsetter(opt)
    s.populate(text=text)
    s.subset(font)
    # Ein Subset ist eine veränderte Fassung: eigener Name, damit kein
    # Reserved Font Name («Source», «Plex» …) daran hängt. Copyright (0),
    # Lizenz (13/14) und Herkunft bleiben stehen.
    probe = "Probe " + ziel.stem
    name = font["name"]
    for nid in (1, 3, 4, 6, 16, 17, 21, 22):
        name.removeNames(nameID=nid)
    for nid, wert in ((1, probe), (2, "Regular"), (3, probe), (4, probe),
                      (6, probe.replace(" ", "-"))):
        name.setName(wert, nid, 3, 1, 0x409)
    font.flavor = "woff2"
    font.save(ziel)
    print("  ->", ziel.name, ziel.stat().st_size // 1024, "KB")


def instanz(pfad: Path, wght: float) -> TTFont:
    f = TTFont(pfad)
    if "fvar" not in f:
        return f
    achsen = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
    achsen["wght"] = wght
    if "slnt" in achsen:
        achsen["slnt"] = 0
    return instancer.instantiateVariableFont(f, achsen, updateFontNames=False)


def main(root="."):
    root = Path(root)
    seiten = [root / "begleitschriften.html", root / "lesetext-noto.html"]
    aus = root / "assets/fonts/schriftsysteme"
    aus.mkdir(parents=True, exist_ok=True)
    cache = Path.home() / ".cache/schriftsysteme-probe"
    cache.mkdir(parents=True, exist_ok=True)
    text = zeichen(seiten)
    # Source Sans 3 (Griechisch) aus dem Repo
    ss = root / "assets/fonts/goetheanum/Fallback/SourceSans3-Variable.ttf"
    jobs = {"sourcesans": (ss, None)}
    for slug, (q, t, ti) in KANDIDATEN.items():
        print(slug)
        jobs[slug] = (holen(q, t, cache), holen(q, ti, cache) if ti else None)
    for slug, (tpfad, tipfad) in jobs.items():
        schneiden(instanz(tpfad, 400), text, aus / f"{slug}-text.woff2")
        titel = TTFont(tipfad) if tipfad else instanz(tpfad, TITEL_WGHT)
        schneiden(titel, text, aus / f"{slug}-titel.woff2")


if __name__ == "__main__":
    main(*sys.argv[1:])
