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

## Reparatur v2.8 (29. 10. 2026)
Kreuzende, starre und verrutschte Glyphen des Variable Font (Befund in
`AUDIT.md`), danach alle Lieferformen. Reihenfolge:
```bash
python3 repair_variable_v28.py     # Variable reparieren (+ ihre Webfonts)
python3 proof_variable_axis.py     # Prüfmass, Exit 1 bei Verstoss (--alle: jede Glyphe)
python3 sync_statics_v28.py        # Reparatur in die statischen Schnitte (+ Webfonts)
python3 build_beipackzettel.py     # aus der Repo-Wurzel
python3 build_office_ttf.py
python3 pack_release_zip.py
```
Die Skripte sind idempotent; ein zweiter Lauf schreibt dieselben Glyphen.

## v2.9: Abgleich mit Titillium Sans Pro (31. 10. 2026)
Neue Zeichen, Kerning der Pro, `¨`; Befund in
`docs/befunde/schrift-v29-titillium-pro.md`. Die Pro ist fremder Stand: in
einen eigenen leeren Ordner klonen und nur mit `python3 -I` lesen.
```bash
git clone --depth 1 https://github.com/chialab/titillium_pro /tmp/pro/tp   # Branch main
python3 -I build_v29_pro.py /tmp/pro/tp   # liest v2.8 aus git, schreibt v2.9 (+ Webfonts)
python3 bump_version.py 2.8 2.9           # nur Icons und Pfeile (einmalig)
python3 proof_variable_axis.py --alle
python3 build_beipackzettel.py            # aus der Repo-Wurzel
python3 build_office_ttf.py
python3 pack_release_zip.py
```
`build_v29_pro.py` ist idempotent (zweiter Lauf bitgleich). `pro_quelle.py`
liest die UFO-Master (Umrisse, Anker, Kerning), führt nichts aus.

## Fassung 2.91: Listenzeichen ss03–ss06 (2. 11. 2026)
Kreis und Quadrat, Kontur und gefüllt, A–Z und 1–99 (Etappe E3); Befund in
`docs/befunde/listenziffern-e3-2026-11-02.md`. Liest v2.9 aus git, schreibt
dieselben Dateinamen (intern 2.91), zweiter Lauf bitgleich.
```bash
python3 build_v29_listen.py
python3 proof_variable_axis.py --alle      # gefüllte Formen: Fläche muss fallen
python3 build_beipackzettel.py             # aus der Repo-Wurzel, Seite 6
python3 build_office_ttf.py
python3 pack_release_zip.py
```

## Fassung 2.92: Pfeile in der Textschrift (2. 11. 2026)
`← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙` in der Form der ‹Goetheanum Pfeile›, an jedem Master
neu gezogen, mit ihrem Strichverlauf, Strich im Mittel = Minus; Befund
`docs/befunde/pfeile-textschrift-2026-11-02.md`. Liest Fassung 2.91 aus git,
schreibt dieselben Dateinamen (intern 2.92), zweiter Lauf bitgleich.
```bash
python3 build_v29_pfeile.py
python3 proof_variable_axis.py --alle
python3 build_beipackzettel.py             # aus der Repo-Wurzel, Seite 2
python3 build_office_ttf.py
python3 pack_release_zip.py
```

## Verifikation
```bash
pip install fontbakery
fontbakery check-universal assets/fonts/goetheanum/Fonts/*.otf
```
Ziel: 0 FAIL bei den Textschnitten und Icons.

## QA-Tools (Build-Abhängigkeiten)
`fonttools`, `brotli` (woff2); optional `fontbakery` (QA). Nicht ins Repo gepinnt.
