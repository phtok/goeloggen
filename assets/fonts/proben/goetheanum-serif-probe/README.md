# Goetheanum Serif Probe (Version 0.1)

**Probe, nicht im Paket, nicht für den Einsatz.** Etappe E4 aus
`docs/recherche_titillium-pro.md`. Befund und Entscheidvorlage:
`docs/befunde/serif-probe-2026-10-31.md`. Anschauen:
https://werkzeuge.goetheanum.ch/schrift-serif-probe.html

- Quelle: Titillium Pro Serif «version_00» (Chialab, Lorenzo Volpe, ISIA
  Faenza), https://github.com/chialab/titillium_pro/tree/serif, Commit
  65ca153 (4. 2. 2026), Kopie in `tools/goetheanum-fontfix/sources/titillium-pro-serif-beta/`.
- Lizenz: SIL Open Font License 1.1 (`OFL.txt`). Umbenannt, weil
  «Titillium» als Reserved Font Name der Familie gilt.
- Gebaut mit `python3 tools/goetheanum-fontfix/build_serif_probe.py`
  (idempotent, bytegleich).
- Ergänzt: ä ö ü ë ï ÿ Ä Ö Ü Ë Ï, ß, kombinierendes Trema, einstöckiges a
  als `ss01`, feste und schmale Leerzeichen, weiches Trennzeichen.
- Ein Gewicht (Regular, Stamm 82 Einheiten, Klar 81), dazu eine Kursive.
