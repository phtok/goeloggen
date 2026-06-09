# Goetheanum Schriften v1.4.43 — Audit & Reparatur

Technisches Audit der Original-Auslieferung v1.4.43 und Dokumentation der in
`v1.4.43-fix1` (dieser Ordner) durchgeführten Korrekturen.

Werkzeuge: `fontTools` (Outline-/Tabellenanalyse, Interpolation), `fontbakery`
(Industrie-QA). Quelle für geliehene Glyphen: die OFL-lizenzierten **Titillium
Upright**-Schnitte (Thin/Light/Regular/Semibold/Bold), aus denen die Goetheanum
Schriften ursprünglich abgeleitet wurden.

Leitsatz: **keine Fehler importieren.** Jede geliehene Outline wird per
Interpolation exakt auf das Zielgewicht des jeweiligen Schnitts gebracht, und
der defekte Titillium-`fraction`-Glyph (Vorschub 65521 = ungültig) wird nie
verwendet.

## Gewichtszuordnung (gemessen an der H-Fläche)

| Goetheanum | H-Fläche | entspricht Titillium |
|-----------|----------|----------------------|
| Leise (280) | 87 500 | zwischen Thin (63 006) und Light (103 435) |
| Klar (450)  | 140 000 | zwischen Regular (126 847) und Semibold |
| Laut (600)  | 177 400 | ≈ Semibold (177 393) |

## Behobene Fehler

### Gestaltung / Funktion
- **`&` folgte nicht dem Gewicht.** Das Ampersand war in Leise/Klar/Laut/Variabel
  *bytegleich mit Titillium Regular* (Fläche 158 338, ×1.00), während jede andere
  Glyphe mit dem Gewicht wächst. → in Laut zu dünn, in Leise zu fett. Neu pro
  Schnitt interpoliert; die `&`-Stege folgen jetzt der Familie
  (Leise 48 ≈ `l` 49, Klar 78 ≈ 84, Laut 101 ≈ 109).
- **Fehlende Zeichen ergänzt:** `!` `"` `$` `§` (gewichtsrichtig aus Titillium
  Upright) sowie **NBSP** (U+00A0).
- **Einfache Guillemets `‹ ›`** waren zu weit und nicht spiegelgleich
  (‹ 94/94, › 102/94). Jetzt exakt gespiegelt.

### Metadaten / Technik (fontbakery-FAILs)
- `head.fontRevision` 1.0 → 1.443 (passend zum Namens-String).
- CFF-`FontName` `CFF2Font` (Export-Platzhalter) → korrekter PostScript-Name.
- Caret/Italic-Reste (`caretSlopeRun 231`, `caretOffset -81`) → aufrecht (1/0/0).
- `.notdef` war leer → sichtbares Kästchen.
- Veraltete **Mac-Plattform-Name-Records** entfernt.
- Doppelte Full-Names („Goetheanum Variabel **Variabel**", „… Icons **Icons**")
  bereinigt.
- **Vertikalmetriken vereinheitlicht:** typo 750/−250, `lineGap = 0`,
  `USE_TYPO_METRICS` gesetzt, `winAscent/Descent` über alle Textschnitte gleich
  → konsistente Zeilenhöhe schnitt- und plattformübergreifend.
- **Vietnamesische Halb-Paare** (U+1EAB/1EB0/1EC5/1ED7 — Großbuchstaben fehlen
  auch in Titillium) aus der cmap genommen, damit die Groß/Klein-Zuordnung in
  sich konsistent ist. Symbol-Zeichen **µ ƒ π Ω bleiben erhalten**.
- Variable Font: `OS/2.usWeightClass` 400 → 450 (= fvar-Default).
- **SIL-OFL-Lizenzfelder** in allen Fonts gefüllt (Copyright, Lizenz, URL,
  Hersteller, Designer), `OFL.txt` beigelegt.

Ergebnis fontbakery: **Textschnitte & Icons = 0 FAIL** (eine WARN „unreachable
glyphs" verbleibt: legacy/feature-bezogene Glyphen, harmlos).

## Offene Punkte (brauchen Marken-Entscheidung)
- **Guillemets-Feinabstand:** aktuell nur spiegel-korrigiert, nicht enger
  gestellt. Falls insgesamt zu luftig empfunden, lege ich eine engere Variante
  an (für `‹ ›` und `« »` gemeinsam).
- **Variable Font, Namens-Konvention:** fontbakery erwartet eine „Regular"-
  Instanz und Default-Instanz-Namen nach Google-Fonts-Schema; das kollidiert mit
  der Marken-Benennung Leise/Klar/Laut. Bewusst unverändert gelassen.
- **`fi`/`fl`-Ligaturen** (`liga`): in den Titillium-Uprights nicht vorhanden;
  brauchen eine vollständigere Quelle oder eine Neuzeichnung.
- **Variable Font auf Glyphenebene** (fehlende Interpunktion, `&`-Interpolation):
  am saubersten in der Glyphs-Quelle zu lösen; hier nur Metadaten korrigiert.
- **Master-Drift** (CapHeight 685/690/697): Outline-Thema der Quelle, nicht am
  Binary reparierbar.

## Reproduzieren
Siehe `tools/goetheanum-fontfix/` (Skripte, Titillium-Quellen, Original-Inputs):
```
cd tools/goetheanum-fontfix && python3 build.py
```
