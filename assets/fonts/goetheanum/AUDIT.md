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
- **SIL-OFL-Lizenzfelder** in allen Fonts gefüllt (Copyright, Lizenz, URL,
  Hersteller, Designer), `OFL.txt` mit voller Titillium-Autorenliste beigelegt.

### Variable Font (CFF2)
- `OS/2.usWeightClass` 400 → 450 (= fvar-Default).
- **Gleiches Repertoire wie die Statics:** `! " §` als **echte, interpolierende
  Blends** ergänzt; das **`&` variiert** jetzt über die `wght`-Achse (vorher in
  allen Instanzen identisch) — per Instanziierung verifiziert (Flächen
  280/450/600 = 113 383 / 173 201 / 211 653). `$` nicht-variabel (Klar-Gewicht,
  da die Titillium-Master dafür nicht punktkompatibel sind), NBSP ergänzt.
- **STAT-Tabelle** für die Gewichtsachse neu gebaut (Leise/Klar/Laut, Klar
  elidiert); `.notdef`-Kästchen ergänzt; Default-Instanz-Namen korrigiert
  (nameID 17 = „Klar", Verweis auf Familien-Default).

Ergebnis fontbakery: **Textschnitte & Icons = 0 FAIL** (eine WARN „unreachable
glyphs" verbleibt: legacy/feature-bezogene Glyphen, harmlos).

## Offene Punkte (brauchen Marken-Entscheidung)
- **Guillemets-Feinabstand:** aktuell nur spiegel-korrigiert, nicht enger
  gestellt. Falls insgesamt zu luftig empfunden, lege ich eine engere Variante
  an (für `‹ ›` und `« »` gemeinsam).
- **Variable Font, „Regular"-Instanz:** fontbakery erwartet (Google-Fonts-
  Konvention) eine Instanz namens „Regular" am Default. Das kollidiert mit dem
  bewussten Marken-Schema Leise/Klar/Laut — daher belassen (1 verbleibender
  FAIL). Die übrigen Variable-Font-Punkte sind behoben.
- **`fi`/`fl`-Ligaturen** (`liga`): in den Titillium-Uprights nicht vorhanden;
  brauchen eine vollständigere Quelle oder eine Neuzeichnung.
- **`$` im Variable Font** ist nicht-variabel (konstantes Klar-Gewicht), weil die
  Titillium-`$`-Master über den Bereich nicht punktkompatibel sind.
- **Master-Drift** (CapHeight 685/690/697): Outline-Thema der Quelle, nicht am
  Binary reparierbar.

## Befund 29. 10. 2026: Doppel-Guillemets « » kreuzen sich (v2.7)

Anschauung: https://werkzeuge.goetheanum.ch/guillemets.html (alle sieben
Schnitte im Satz, dazu der Vorher-Vergleich mit v1.4.43).

- **Was.** In `« »` (U+00AB/BB) stehen die beiden Winkel im Variable Font
  v2.7 am dünnen Ende (Flüstern 190) in der Reihenfolge links/rechts, am
  fetten Ende (Schreien 725) rechts/links. Dazwischen wandern die Konturen
  durcheinander hindurch: in **Klar liegen sie fast deckungsgleich** – das
  Zeichen liest sich als eine einzelne, fette Winkelklammer (Breite 198
  Einheiten gegen 181 für `‹`). Ruhig und Deutlich zeigen überlappende
  Winkel. Die statischen Schnitte v2.7 und die Office-TTF sind aus dem
  Variable Font instanziert und tragen denselben Schaden.
- **Gleiche Ursache** bei `„` (U+201E), `‚` (U+201A, in Klar nur 7 Einheiten
  breit – praktisch unsichtbar), `÷` (U+00F7) und `◊` (U+25CA).
- **Herkunft.** Die Original-Auslieferung v1.4.43 (`tools/goetheanum-fontfix/
  input/`) ist heil: beide Winkel getrennt, über alle Gewichte konsistent.
  Der Schaden entstand beim Neubau des Variable Fonts in v2.5 (die
  Masterkonturen wurden ohne gleiche Konturreihenfolge zusammengeführt).
- **Nicht betroffen:** `‹ ›` (U+2039/203A), die Hausform nach G16.
- **Reparatur (offen).** Im Variable Font die Konturreihenfolge der
  genannten Glyphen über alle Master angleichen (am dünnen Master messen,
  fetten Master danach sortieren) oder die Glyphen aus v1.4.43 gewichtsrichtig
  neu interpolieren; danach die statischen Schnitte, Office-TTF und Webfonts
  aus `tools/goetheanum-fontfix/` neu erzeugen und die Messung in
  `guillemets.html` nachführen. Prüfmass: Breite `«` muss mit dem Gewicht
  monoton wachsen (heute 350 · 294 · 232 · 198 · 332 · 428 · 471).

## Reproduzieren
Siehe `tools/goetheanum-fontfix/` (Skripte, Titillium-Quellen, Original-Inputs):
```
cd tools/goetheanum-fontfix && python3 build.py
```
