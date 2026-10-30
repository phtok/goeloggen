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

### Durchgang durch alle 637 Glyphen (29. 10. 2026, Kontur für Kontur)

Gemessen am Variable Font v2.7 an sieben Gewichten (190 … 725): Konturlage,
Konturbreite und -höhe, Drehsinn, Vorschub, Tintenfläche gegen den
Familien-Median. Dazu Proof-Bögen bei 350/440/580 mit dem Auge geprüft.

**Kreuzende Konturen (sichtbarer Schaden), neben « » „ ‚ ÷ ◊:**
- `%` (U+0025): der obere Kreis kippt – Fläche bei Flüstern 1,6-mal so gross
  wie in Klar, bei Ruhig und Leise ein Halbmond mit Kerbe, bei Deutlich ein
  gefüllter Punkt. **Häufig gebraucht, dringendster Fall nach « ».**
- `Ű` (U+0170): die zwei Akut-Striche kreuzen sich, in Ruhig und Klar ein
  einzelner Winkel. `ű` (U+0171) ist heil.
- Kleinkapitalen (`smcp`/`c2sc`): `ű` → cid00595 (Doppelakut verschmilzt zu
  Punkten) und `ǻ` → cid00602 (Ring kippt bei Deutlich zum Klecks).

**Vorschub:** `⁄` Bruchstrich (U+2044): 600 · 600 · 600 · **17** · 527 ·
251 · 54 – ab Klar läuft ‹1⁄2› ineinander. Das ist der bekannte
Titillium-`fraction`-Fehler (65521), der über die Variable zurückkam.

**Starr (gleiche Form in jedem Gewicht, also in Flüstern zu fett, in
Schreien zu dünn):** die `case`-Formen von `¿ ¡ – — · ( ) [ ] { }` (elf
Glyphen, greifen bei Versalsatz), der Punkt `•` (U+2022). **Ab Klar starr**
(wachsen nicht mehr mit): `Ą` (U+0104), `Į` (U+012E), `$` (bekannt).
**Ab Ruhig starr:** Kleinkapitalen von `å ą į ŋ`. Dazu 53 unkodierte,
über kein Feature erreichbare Restglyphen mit starrer Form – kein Schaden,
nur Ballast (u. a. ein zweiter Satz Ziffern und Akzente).

**Geringfügig:** `ĺ` (U+013A) trägt den Akut in Flüstern über dem Stamm, ab
Deutlich rechts daneben; `¨` (U+00A8) halbiert seinen Vorschub 791 → 514.

**Heil, ausdrücklich geprüft:** Ziffern (Flächenverlauf wie `n`/`o`),
`: ; = " ! ? … ‰ ( ) @ & ß ẞ`, alle Umlaute, `‹ ›`.
- **Behoben in v2.8 (29. 10. 2026).** Alle oben genannten Glyphen sind im
  Variable Font neu als Blend gebaut (`tools/goetheanum-fontfix/
  repair_variable_v28.py`). Grundlage: Bei den gesunden Glyphen ist jeder
  innere Master (335 · 420 · 440 · 600) bis auf < 1 Einheit die lineare
  Mischung der Endmaster 190 und 725 (Faktoren 0,27 · 0,43 · 0,46 · 0,76).
  Kreuzende Glyphen: 725 auf Konturfolge, Startpunkt und Drehsinn von 190
  gebracht, Innenmaster daraus. Halb starre (`Ą Į $`, Kapitälchen `å ą į ŋ`):
  725 aus 190 und Klar fortgeschrieben. `case`-Formen aus der Grundform mit
  festem Versatz, Kapitälchen `ǻ` aus dem
  reparierten Kapitälchen-`å` plus Akut.
  **Beim Prüflauf über alle 581 erreichbaren Glyphen nachgefunden und mit
  behoben:** `€ ǿ` und die Kapitälchen `m y ñ ý ÿ ħ ń ň ŧ ŷ ž ǿ` blieben über
  Deutlich fast stehen; bei `Û` und Kapitälchen-`û` sass der Zirkumflex schon
  in Klar 83 Einheiten links und 90 zu hoch (neu aus `U` + Zirkumflex von `Ô`).
  **Bruchstrich `⁄`:** Der Vorschub ist wieder klein und wächst mit dem
  Gewicht (4 · 8 · 12 · 17 · 25 · 30 · 32), wie in v1.4.43 (6 · 19 · 36),
  Titillium (0) und Source Sans (86). Die 600 der unteren Schnitte stammten
  aus der Klemme für den Titillium-Fehler 65521; damit zerfiel die Bruchform
  (`frac`) in ‹1⁄ 2›. Ohne `frac` überlappt der Strich die vollen Ziffern –
  so ist das Zeichen gebaut.
  **Statische Schnitte:** Ruhig und Deutlich sind ganz aus der Variable
  instanziert und übernehmen jede Reparatur; Leise, Klar und Laut stammen aus
  der v1.4.43-Linie und behalten ihre eigenen, gesunden Formen (z. B. die
  `case`-Klammern in Laut). Selbst beschädigte Eigenformen wurden mit
  ersetzt: `„` in Leise, Kapitälchen `ű` in Klar, Kapitälchen `û` in Klar
  und Laut (`sync_statics_v28.py`).
  **Prüfmass** (`proof_variable_axis.py`, an 190 · 265 · 350 · 440 · 580 ·
  680 · 725): Tintenfläche wächst, Breite fällt nicht, Konturzentren wandern
  höchstens 40 Einheiten je Stufe – 0 Verstösse über alle erreichbaren
  Glyphen. Breite `«` jetzt 350 · 367 · 386 · 406 · 437 · 461 · 471.
  Vorher/Nachher: https://werkzeuge.goetheanum.ch/guillemets.html

### Zweite Prüfung (30. 10. 2026, nach Rückmeldung des Inhabers)

Jede reparierte Glyphe gross an allen sieben Stufen gegen v1.4.43, Titillium
Thin…Bold und ihre natürlichen Partner gesetzt; dazu je Glyphe der Zuwachs
oben (Fläche 580 → 725 gegen 440 → 580), der jetzt im Prüfmass steht.

- **Kapitälchen und Kurzziffern, alle (117 Glyphen):** standen oberhalb von
  Deutlich still. Ursache in `build.py` (v2.4.1): Versalie bzw. Ziffer bei
  Gewicht +110 bzw. +80, verkleinert – aber `min(725, …)` geklemmt. Der
  Kapitälchenstamm wuchs darum 76 (Klar) → 102 (Laut) → 103 (Schreien), die
  Gemeinen 81 → 126 → 134. Dieselbe Klemme trägt der statische Laut. Behoben:
  das kalibrierte Modell bleibt, die Klemme fällt (725 aus 190 und Klar
  fortgeschrieben); in allen statischen Schnitten neu aus der Variable gesetzt.
- **Kapitälchen å ą į ŋ q & ǻ:** zusätzlich in sich falsch (å ŋ ab Klar zu
  leicht, q & in Flüstern zu schwer, ą į ab Klar starr – auch in den
  statischen Schnitten). Neu: å ŋ aus Leise/Klar der v1.4.43-Linie, q & aus
  Klar und Deutlich, ą į aus Kapitälchen a/i plus Ogonek ˛ (gesetzt wie bei
  ą/į), ǻ aus Kapitälchen-å plus Akut des Kapitälchen-á (der Akut ´ war zu
  gross), ű aus Kapitälchen-u plus Doppelakut des ő.
- **Ø ø Ǿ ǿ, Kapitälchen ø ǿ:** Der eingeschnittene Schrägstrich wuchs nur
  auf das 1,9-Fache (der / auf das 3,7-Fache): Strichstärke in Klar 58 statt
  79, in Schreien 85 statt 130. Neu: gesundes O/o plus eigener Strich, senkrecht
  0,92 × Seitenstrich des O wie beim /; unter dem Akut endet er bündig.
- **Å Ǻ Ŋ ẞ €:** oben flach wie die Kapitälchen, gleich behoben.
- **« »:** aus zwei exakten ‹ ›; » stand 5–8 Einheiten höher als ›. Lücke:
  die enge der Titillium-Extreme (38 in Flüstern … 51 in Schreien), nicht die
  weite 84 der Auslieferung v1.4.43 (Entscheid des Inhabers, 30. 10. 2026,
  nach Gegenüberstellung im Satz).
- **‚ „:** exakt ’ ” auf Kommatiefe; vorher bis 30 Einheiten abweichend. Die
  v1.4.43 taugt hier nicht als Vorbild (ihr ‚ ist ein Splitter, „ verschmolzen).
- **case-Striche:** – — standen nur 30 Einheiten über dem Gemeinsatz (Mitte
  297 statt Versalmitte); jetzt Mitte auf dem Querbalken des H (349). Die
  case-Form des Bindestrichs fehlte ganz – angelegt für - ‐ ‑ und das weiche
  Trennzeichen.
- **Bewusst belassen:** • bleibt in jedem Schnitt dasselbe Quadrat wie in
  Titillium und v1.4.43 (Entscheid des Inhabers, 30. 10. 2026; das Prüfmass
  nimmt ihn aus). Die Kapitälchen behalten das kalibrierte Gewicht (Versalie
  bei +110, verkleinert; in Klar Stamm 76 gegen 81 der Gemeinen) – ebenfalls
  entschieden. Die f-Ligaturen und µ verlaufen nicht linear, sind aber in
  sich stimmig; ◊ folgt den Titillium-Extremen.

## Reproduzieren
Siehe `tools/goetheanum-fontfix/` (Skripte, Titillium-Quellen, Original-Inputs):
```
cd tools/goetheanum-fontfix && python3 build.py
```
