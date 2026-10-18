# Learnings aus dem Kartentool-Bau — Rückfluss ins Design-System

Quelle: Bau- und Testrunden des Kartentools (`apps/karten-generator/`),
Juli 2026, 14 Rückmelderunden mit pixel- und PDF-verifizierten Befunden.
Ratifizierung durch den Auftraggeber steht aus — diese Datei ist die
Vorlage für die Aufnahme (CHANGELOG-Einträge, Token-Kandidaten,
Beipackzettel-Hinweise) in einer eigenen Design-System-Session.

## 1. Icons v2.7: Einzeldateien sind nicht einheitlich normiert

**Befund.** Die Standard-viewBox der Icon-Einzeldateien ist
`16.2 -983.8 967.6 967.6` — aber nicht alle Dateien tragen sie.
Gemessen: `wc-rollstuhl.svg` hat `-0.6 -845.1 817.5 817.5`.
Wer stur auf die Standardbox skaliert (`scale(g/967.6)`,
`translate(-500 500)`), setzt solche Icons schief und zu klein —
so geschehen beim Rollstuhl-Marker des Kartentools.

**Bewährte Abhilfe (im Kartentool im Einsatz).** Konsumenten zentrieren
Icons auf ihre **Tintenbox** statt auf die viewBox: Inhalt in ein `<g>`
laden, `getBBox()` messen, Skala = Zielmass / max(Tintenbreite,
Tintenhöhe), Translation so, dass die Tintenmitte auf dem Zielpunkt
liegt. Feine Strichzeichnungen lassen sich mit einem leichten
Konturauftrag in gleicher Farbe kräftigen (`stroke` = `fill`,
Strichstärke ≈ 0.09 mm im Zielmass).

**Empfohlener Rückfluss.**
- Entweder: fontfix-Pipeline (`tools/goetheanum-fontfix/`) normalisiert
  die Einzeldateien auf eine einheitliche viewBox (idempotent, aus
  sauberem Stand — dann alle Webfonts/ZIPs neu packen).
- Oder: Beipackzettel/README der Icons schreibt die Tintenbox-Zentrierung
  als Konsumentenregel fest.

**Nebenbefund.** `wc-gruppe.svg` ist das fertige Sammel-Piktogramm
(Dame, Herr, Wickelkind, Rollstuhl, WC-Schriftzug) — für ‹alle
Toiletten›-Marken braucht es keine Einzel-Icon-Kombination.

## 2. Druck-Export: `text-anchor="middle"` ist nicht druckfest

**Befund.** Der SVG→PDF-Renderer (svg2pdf) misst Textbreiten für die
Mittel-Verankerung mit fremden Metriken. Im Browser sass alles mittig,
im PDF verrutschten zweistellige Markerzahlen und die Gebäudenamen
(‹Goetheanum›, ‹Schreinerei›) um mehrere Millimeter.

**Bewährte Abhilfe.** Text in Export-SVGs **start-verankert selbst
zentrieren**:
- Marker-Zeichen: Vorschubtabelle aus der TTF vermessen (fontTools,
  `hmtx`-Advances je Glyphe in em) und je Zeichen selbst positionieren.
- Freitexte (Gebäudenamen): Breite zur Laufzeit per Canvas messen
  (`ctx.font = '100px <Familie>'`, `measureText`), vorher
  `document.fonts.load(...)` abwarten — sonst misst die Ausweichschrift.
Nachgemessen: Goetheanum-Label-Mitte im PDF exakt auf Soll.

**Empfohlener Rückfluss.** Als Konstruktionsregel ins Werkzeugwissen
des Design-Systems (überall, wo SVG→PDF exportiert wird): *Kein
`text-anchor="middle"`/`end` in Export-SVGs; Breiten selbst messen.*

## 3. Gerechneter ‹Leise-Tinte auf Weiss›-Wert für den Druck

**Befund.** Für Strukturbeiwerk auf Papierweiss (Kategorie-Titel der
Kartenlegende) fehlte ein leiser Tintenton mit belegtem Kontrast.
Gerechnet (WCAG-Relativleuchtdichte):

| Ton       | Kontrast auf #ffffff | Verwendung |
|-----------|----------------------|------------|
| `#4e4f4a` | 8.26 : 1             | Volltinte (Karten-Lesetexte) |
| `#6e6f6a` | **5.07 : 1**         | leises Strukturbeiwerk, B02-fest für Lesetext |
| `#767771` | 4.52 : 1             | Untergrenze, nur mit Bedacht |

**Empfohlener Rückfluss.** `#6e6f6a` als Token-Kandidat
(z. B. `--ink-print-leise`) aufnehmen, sobald ein zweites Druckwerkzeug
ihn braucht; bis dahin als belegter Wert im CHANGELOG.

## 4. `.step-num`: Messwerte bestätigt, zweistellig geklärt

**Befund.** Die in `base.css` dokumentierte Sitz-Korrektur (translateY
8 %, Tintenmitte der Ziffern ≈ 330/1000 über der Grundlinie) wurde im
Kartentool unabhängig pixelverifiziert — sie stimmt exakt. Für
zweistellige Zahlen trägt der feste Kreis (1.6 em) die Proportion
0.72 em problemlos; im Kartenmassstab hat sich für Marker
**Grad = 0.5 × Kreisdurchmesser** bewährt (eine Spur kräftiger als
0.72/1.6 = 0.45), mit selbst gesetzten Vorschüben (siehe Befund 2).

**Zusatz.** Die Goetheanum-Schnitte führen `tnum`/`lnum` als
GSUB-Features (geprüft an Laut) — die G25-Umsetzung über
`font-variant-numeric` greift also auch in der Hausschrift. Der
Standardsatz ist proportional (`1` = 0.433 em, `8` = 0.62 em);
PDF-Renderer ignorieren Features — im Druck-Export darum nie auf
`tabular-nums` verlassen, sondern Slots selbst setzen.

## 5. Flächenkarten ohne Linien: zwei Bau-Muster

**Befund A — Kontur-Zwillinge.** Die Quell-Illustrator-Karte legt um
viele Flächen separate Strich-Zwillinge (identische Geometrie als
`fill="none"`-Pfad, teils mit angehängtem Schlusspunkt — exakte
d-Duplikat-Erkennung reicht nicht). Für die Flächen-Sprache des Hauses
(‹keine Linien, nur Kontraste›) müssen sie raus: 341 Strichpfade
entfernt, Erkennung über (transform, d)-Abgleich + Grössenschwelle
(< 10 mm = Kontur-Rest, kein Weg). Achtung Zahlen-Parser: Werte wie
`-.255` (führender Dezimalpunkt) brauchen `-?(?:\d+\.?\d*|\.\d+)`.

**Befund B — Fugendichtung.** Stossen gefüllte Flächen exakt aneinander,
entstehen beim Rastern (Bildschirm wie PDF-Viewer) haarfeine helle
Fugen. Abhilfe: jede Fläche trägt eine **Eigenkontur in ihrer
Füllfarbe** (`stroke` = `fill`, 0.35 pt) — unsichtbar, dichtet die
Fugen, folgt jeder Umfärbung.

**Empfohlener Rückfluss.** Beide Muster als Werkzeugwissen für künftige
Karten-/Grafik-Werkzeuge dokumentieren (nicht base.css — es ist
SVG-Bauwissen, kein Seitenstil).

## 6. Kleinere UI-Befunde aus den Testrunden (bereits umgesetzt)

- Zeilen mit vielen Werkzeugknöpfen (je 44-px-Ziele, B04) brechen
  schmale Titel in Buchstabentürme — Abhilfe: zweizeilige Zeile
  (Titel oben in voller Breite, Werkzeuge unten), statt die
  Fingerziele zu verkleinern.
- Gruppen-Sammelschalter (‹alle an/aus›) gehören in den Gruppenkopf,
  brauchen aber ein eigenes Element neben dem Aufklapp-Knopf
  (verschachtelte Buttons sind unzulässig) — Muster `.group-head`
  mit `.object-group-title` (flex:1) + `.group-toggle`.
- Kategorie-Titel in Listen/Legenden: Unterscheidung mit genau einem
  Merkmal (G01) — leiser, gleicher Grad, gleiche Einrückung wie die
  Einträge.
