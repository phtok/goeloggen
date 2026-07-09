# Werkzeugwissen — Konstruktionsregeln für Werkzeuge, die drucken und zeichnen

Dieses Wissen gehört zum Design-System, aber nicht in `base.css`: Es sind
**Bau-Regeln für Werkzeuge** (SVG-Grafik, PDF-Export, Icon-Konsum), keine
Seitenstile. Quelle: Bau- und Testrunden des Kartentools
(`apps/karten-generator/`), Juli 2026 — pixel- und PDF-verifiziert,
ratifiziert vom Auftraggeber (8. Juli 2026). Ledger-Eintrag: Version 1.6.0.

## 1. Druck-Export: `text-anchor="middle"` ist nicht druckfest

Der SVG→PDF-Renderer (svg2pdf) misst Textbreiten für die Mittel-Verankerung
mit fremden Metriken: Im Browser sitzt alles mittig, im PDF verrutschen
Texte um Millimeter. **Regel für Export-SVGs: kein `text-anchor="middle"`
oder `end` — Breiten selbst messen, start-verankert selbst zentrieren.**

- Feste Zeichenvorräte (Markerzeichen): Vorschubtabelle aus der TTF
  vermessen (fontTools, `hmtx`-Advances je Glyphe in em, upm beachten)
  und je Zeichen selbst positionieren. Deterministisch und ladeunabhängig.
- Freitexte: Breite zur Laufzeit per Canvas messen (`ctx.font`,
  `measureText`), vorher `document.fonts.load(...)` abwarten — sonst
  misst die Ausweichschrift. Nur als Rückfall für Zeichen ausserhalb
  der Tabelle.
- PDF-Renderer ignorieren OpenType-Features: `tabular-nums` (G25) im
  Druck-Export nie voraussetzen — Ziffern-Slots selbst setzen.

## 2. Icons v2.7: auf die Tintenbox zentrieren, nicht auf die viewBox

**Stand seit 9. Juli 2026: normalisiert.** Die Einzeldateien werden per
`tools/goetheanum-fontfix/normalize_icon_svgs.py` idempotent aus dem
Icon-Font regeneriert — alle Piktogramme tragen die einheitliche Em-Box
`viewBox="-2 -1002 1004 1004"` (einzige Ausnahme: die Wortmarke
`icon-0021`, proportional 5970×1000); die ‹mit Text›-Varianten sind bewusst
nur Webfont, keine Einzeldateien. Historischer Befund: die Dateien waren
nicht einheitlich normiert (Standard-viewBox `16.2 -983.8 967.6 967.6`,
aber z. B. `wc-rollstuhl.svg` trug `-0.6 -845.1 817.5 817.5`) — wer stur
auf die Standardbox skalierte, setzte solche Icons schief und zu klein. **Regel: Konsumenten zentrieren Icons
auf ihre Tintenbox** — Inhalt in ein `<g>` laden, `getBBox()` messen,
Skala = Zielmass / max(Tintenbreite, Tintenhöhe), Tintenmitte auf den
Zielpunkt. Feine Strichzeichnungen mit Konturauftrag in gleicher Farbe
kräftigen (`stroke` = `fill`, ≈ 0.09 mm im Zielmass).

`wc-gruppe.svg` ist das fertige Sammel-Piktogramm (Dame, Herr, Wickelkind,
Rollstuhl, WC-Schriftzug) — für ‹alle Toiletten› keine Einzel-Icons kombinieren.

## 3. Flächengrafik ohne Linien: zwei Bau-Muster

- **Kontur-Zwillinge entfernen:** Illustrator-Quellkarten legen um Flächen
  separate Strich-Zwillinge (identische Geometrie als `fill="none"`-Pfad,
  teils mit angehängtem Schlusspunkt oder als Haarlinie ≤ 0.5 pt). Für die
  Flächen-Sprache des Hauses (‹keine Linien, nur Kontraste›) müssen sie
  raus: Erkennung über (transform, d)-Abgleich, Grössenschwelle und
  Strichstärke. Achtung Zahlen-Parser: Werte wie `-.255` brauchen
  `-?(?:\d+\.?\d*|\.\d+)`.
- **Fugendichtung:** Stossen gefüllte Flächen exakt aneinander, entstehen
  beim Rastern haarfeine helle Fugen. Jede Fläche trägt eine Eigenkontur
  in ihrer Füllfarbe (`stroke` = `fill`, 0.35 pt) — unsichtbar, dichtet
  die Fugen, folgt jeder Umfärbung.

## 4. Leise Tinte auf Papierweiss: `--ink-print-leise`

Für Strukturbeiwerk auf dem gedruckten Blatt (Kategorie-Titel in Legenden)
gilt der gerechnete Ton `#6e6f6a` (**5.07:1** auf Weiss, B02-fest für
Lesetext) — als Token `--ink-print-leise` im Fundament. Volltinte der
Karten-Lesetexte: `#4e4f4a` (8.26:1). Untergrenze `#767771` (4.52:1) nur
mit Bedacht.

## 5. `.step-num` im Kartenmassstab

Die dokumentierte Sitz-Korrektur (Tintenmitte der Ziffern ≈ 330/1000 über
der Grundlinie) ist unabhängig pixelverifiziert — sie stimmt. Für Marker
im Kartenmassstab hat sich **Grad = 0.5 × Kreisdurchmesser** bewährt
(kräftiger als die 0.72/1.6-Proportion der Web-Komponente); Einzel-Piktos
im Kreis laufen mit **1.26 × Radius** (Luft zum Rand, optisch der
Ziffernsitz). Zweistellige Zahlen brauchen selbst gesetzte Vorschübe
(siehe 1.).

## 6. Token-Treue gilt auch für Abstände

Ein erfundenes Token (`var(--s5)` — die Skala führt s1–s4, s6, s8) fällt
**still auf 0 zurück**: kein Fehler, nur gequetschtes Layout. DS02 meint
auch Abstands- und Grössen-Tokens, nicht nur Farben; im Zweifel die Skala
in `tokens.css` nachschlagen. (Kandidat für `ds-lint`: unbekannte
`var(--…)`-Namen melden.)

## 7. UI-Muster aus den Testrunden

- Zeilen mit vielen 44-px-Werkzeugknöpfen (B04) brechen schmale Titel in
  Buchstabentürme — zweizeilige Zeile (Titel oben in voller Breite,
  Werkzeuge unten), nie die Fingerziele verkleinern.
- Gruppen-Sammelschalter gehören in den Gruppenkopf als **eigenes**
  Element neben dem Aufklapp-Knopf (verschachtelte Buttons sind
  unzulässig) — Muster `.group-head` mit Titel (flex:1) + Schalter.
- Kategorie-Titel in Listen/Legenden: Unterscheidung mit genau einem
  Merkmal (G01) — leiser (`--ink-print-leise` im Druck), gleicher Grad,
  gleiche Einrückung wie die Einträge.
