# goetheanum-fontfix

Reproduzierbare Reparatur-Pipeline für die **Goetheanum Schriften v1.4.43**
(Binär-Patch mit fontTools). Erzeugt das korrigierte Paket in
`assets/fonts/goetheanum/`. Was und warum repariert wird, steht in
`assets/fonts/goetheanum/AUDIT.md`.

## Ausführen
```bash
pip install fonttools brotli
cd tools/goetheanum-fontfix
python3 build.py
```

## Inhalt
- `build.py` — Treiber: Glyphen-Import, `&`-Fix, Guillemets, Metadaten, Webfonts, Paket
- `fontfix.py` — Kern-Helfer: gewichtsangepasste Interpolation der Titillium-
  Uprights + CID/Name-keyed CFF-Glyphenoperationen
- `input/` — Original-Fonts v1.4.43 (Build-Eingang, unverändert)
- `sources/` — Titillium **Upright**-Schnitte (SIL OFL) als Interpolations-Quelle
  + `OFL-Titillium.txt`

## Prinzip
Die Goetheanum Schriften sind aus Titillium Upright abgeleitet. Fehlende oder
fehlerhafte Glyphen werden aus den passenden Titillium-Mastern **auf das exakte
Zielgewicht interpoliert** (gemessen an der H-Fläche), nicht bloß kopiert.
Bekannte Titillium-Fehler (z. B. der `fraction`-Glyph mit Vorschub 65521) werden
nie übernommen.

## Verifikation
```bash
pip install fontbakery
fontbakery check-universal assets/fonts/goetheanum/Fonts/*.otf
```
Ziel: 0 FAIL bei den Textschnitten und Icons.

## QA-Tools (Build-Abhängigkeiten)
`fonttools`, `brotli` (woff2); optional `fontbakery` (QA). Nicht ins Repo gepinnt.
