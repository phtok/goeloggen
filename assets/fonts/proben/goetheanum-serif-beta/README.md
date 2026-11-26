# Goetheanum Serif Beta (Version 0.3)

**Ergänzung, nicht Teil der Hausschrift.** Eine Serif zum freien Gebrauch
neben der Goetheanum Schrift, gedacht für Titel und grosse Grade (Display),
nicht für Lesetext. Beta: ein Gewicht, aufrecht und kursiv.

- Ansehen: https://werkzeuge.goetheanum.ch/schrift-serif-probe.html
- Quelle: Titillium Pro Serif «version_00» (Chialab, Lorenzo Volpe, ISIA
  Faenza), https://github.com/chialab/titillium_pro/tree/serif, Commit
  65ca153 (4. 2. 2026).
- Lizenz: SIL Open Font License 1.1 (`OFL.txt`). Umbenannt, weil
  «Titillium» als Reserved Font Name der Familie gilt.
- Ergänzt: ä ö ü ë ï ÿ Ä Ö Ü Ë Ï, ß, einstöckiges a als Grundform (seit 0.3;
  das zweistöckige der Quelle als Stilset `ss01`),
  feste und schmale Leerzeichen, weiches Trennzeichen.
- Seit 0.2 (26. 11. 2026), aus Titillium Sans Pro (Chialab, OFL): Akzente
  für die west- und mitteleuropäischen Sprachen (é à ñ ç č ř ő ą ș …), ẞ,
  Zeichen & % ‰ € $ £ § ¶ @ © ® + = × ÷ ± ° · • †, Kerning der Pro
  (nur schliessende Paare, mit Kollisionswache für die Serifen).
- Fehlt noch: Ł ł Ø ø Æ æ Œ œ Đ đ ď ľ ť, Brüche, tabellarische Ziffern,
  Griechisch, Kyrillisch.
- Schnitte: Regular und Italic.
- Gebaut mit `tools/goetheanum-fontfix/build_serif_beta.py`; Befund:
  `docs/befunde/serif-probe-2026-10-31.md`.
