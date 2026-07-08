# Werkzeugwissen — Bauwissen für SVG, Druck-Export und Werkzeug-UI

Konstruktionsregeln aus verifizierter Praxis (Quelle: Kartentool-Bau,
Juli 2026, 14 pixel- und PDF-verifizierte Testrunden — siehe
`docs/learnings-kartentool.md`). Dieses Wissen gehört nicht in `base.css`
(es ist kein Seitenstil), sondern hierher: Wer ein Werkzeug baut, das SVG
setzt oder PDF exportiert, liest zuerst diese Seite.

## SVG · Icons einsetzen

**Auf die Tintenbox zentrieren, nie auf die viewBox.** Die
Icon-Einzeldateien tragen **keine einheitliche viewBox** (verifiziert am
6. Juli 2026: nur 46 von 81 Dateien haben die Standardbox
`16.2 -983.8 967.6 967.6`; `wc-rollstuhl.svg` etwa hat
`-0.6 -845.1 817.5 817.5`, die Badges und die WC-Familie weichen stark
ab). Wer stur auf die Standardbox skaliert, setzt solche Icons schief und
zu klein. Bewährte Abhilfe: Inhalt in ein `<g>` laden, per `getBBox()` die
Tintenbox messen, Skala = Zielmass / max(Tintenbreite, Tintenhöhe),
Translation so, dass die **Tintenmitte** auf dem Zielpunkt liegt. Feine
Strichzeichnungen lassen sich mit leichtem Konturauftrag in gleicher Farbe
kräftigen (`stroke` = `fill`, Strichstärke ≈ 0.09 mm im Zielmass).

**Nebenbefund:** `wc-gruppe.svg` ist das fertige Sammel-Piktogramm (Dame,
Herr, Wickelkind, Rollstuhl, WC-Schriftzug) — für ‹alle Toiletten› keine
Einzel-Icons kombinieren.

## Druck-Export (SVG → PDF)

**Kein `text-anchor="middle"`/`end` in Export-SVGs.** PDF-Renderer
(svg2pdf u. a.) messen Textbreiten mit fremden Metriken — im Browser sitzt
alles mittig, im PDF verrutschen Zahlen und Namen um Millimeter. Regel:
Text **start-verankert selbst zentrieren**:
- Marker-Zeichen: Vorschubtabelle aus der TTF vermessen (fontTools,
  `hmtx`-Advances je Glyphe in em) und je Zeichen selbst positionieren.
- Freitexte: Breite zur Laufzeit per Canvas messen
  (`ctx.measureText` mit `100px <Familie>`), vorher
  `document.fonts.load(…)` abwarten — sonst misst die Ausweichschrift.

**Nie auf OpenType-Features verlassen.** PDF-Renderer ignorieren
`font-variant-numeric` und GSUB-Features. Die Hausschrift führt `tnum`/
`lnum` (geprüft an Laut; Standardsatz proportional: ‹1› = 0.433 em,
‹8› = 0.62 em) — im Web greift G25 also auch in der Hausschrift, im
**Druck-Export** aber Ziffern-Slots selbst setzen.

**Ziffern in Kreis-Marken:** Die `.step-num`-Sitzkorrektur aus `base.css`
(translateY 8 %, Tintenmitte ≈ 330/1000) ist unabhängig pixelverifiziert.
Für Karten-Marker hat sich Grad = 0.5 × Kreisdurchmesser bewährt (eine
Spur kräftiger als die UI-Proportion 0.45); zweistellige Zahlen trägt der
feste Kreis problemlos.

## Flächen-Sprache (‹keine Linien, nur Kontraste›)

**Kontur-Zwillinge entfernen.** Illustrator-Quellen legen um Flächen oft
separate Strich-Zwillinge (identische Geometrie als `fill="none"`-Pfad,
teils mit angehängtem Schlusspunkt — exakte d-Duplikat-Erkennung reicht
nicht). Erkennung über (transform, d)-Abgleich plus Grössenschwelle
(< 10 mm = Kontur-Rest, kein Weg). Achtung Zahlen-Parser: Werte wie
`-.255` (führender Dezimalpunkt) brauchen `-?(?:\d+\.?\d*|\.\d+)`.

**Fugendichtung.** Stossen gefüllte Flächen exakt aneinander, entstehen
beim Rastern haarfeine helle Fugen (Bildschirm wie PDF-Viewer). Abhilfe:
jede Fläche trägt eine **Eigenkontur in ihrer Füllfarbe** (`stroke` =
`fill`, 0.35 pt) — unsichtbar, dichtet die Fugen, folgt jeder Umfärbung.

## Druck-Tinten auf Papierweiss (gerechnet)

| Ton       | Kontrast auf #ffffff | Verwendung |
|-----------|----------------------|------------|
| `#4e4f4a` | 8.26:1               | Volltinte (Karten-Lesetexte) |
| `#6e6f6a` | 5.07:1               | leises Strukturbeiwerk, B02-fest für Lesetext |
| `#767771` | 4.52:1               | Untergrenze, nur mit Bedacht |

`#6e6f6a` ist Token-Kandidat (`--ink-print-leise`), sobald ein zweites
Druckwerkzeug ihn braucht — bis dahin gilt er als belegter Wert.

## Werkzeug-UI-Muster (verifiziert im Kartentool)

- **Zweizeilige Werkzeugzeile:** Viele 44-px-Ziele (B04) in einer Zeile
  brechen schmale Titel in Buchstabentürme — Titel oben in voller Breite,
  Werkzeuge darunter; nie die Fingerziele verkleinern.
- **Gruppen-Sammelschalter** (‹alle an/aus›) gehören in den Gruppenkopf,
  aber als **eigenes Element** neben dem Aufklapp-Knopf — verschachtelte
  Buttons sind unzulässig. Muster: `.group-head` mit Titel (flex:1) +
  Toggle. Kandidat für `base.css`, sobald ein zweites Werkzeug es braucht.
- **Kategorie-Titel in Listen/Legenden:** Unterscheidung mit genau einem
  Merkmal (G01) — leiser, gleicher Grad, gleiche Einrückung wie die
  Einträge.
