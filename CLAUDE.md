# Arbeitsregeln für dieses Repository

## Typografie ist verbindlich — keine freihändigen Griffe

**Vor jeder Satz-, Seiten- oder Gestaltungsarbeit** (HTML-Seiten, Specimen,
Mockups, PDFs, Beipackzettel) zuerst die Hausregeln lesen und befolgen:

- `assets/typografie/goetheanum-typo-tokens.json` → `$regeln` (Quelle der Wahrheit)
- `assets/typografie/typo-regeln.yaml` (ausführbar: `erkennen`/`korrektur`)
- gesetztes Referenzdokument: `typografie.html`

**Beim Gestalten die betroffenen Regel-IDs nennen** (z. B. „Kicker normal,
nicht versal — G05"). Im Zweifel **fragen**, nicht erfinden.

### Kardinalregeln (nicht verletzen)
- **G01** Einfachauszeichnung: Hervorhebung IM Fließtext ändert **genau ein**
  Merkmal (Gewicht ODER Größe ODER Farbe ODER Einzug). Strukturebenen (Titel,
  Lede, Legende, Tabellenkopf) sind eigene Hierarchie, davon ausgenommen.
- **G03** Weglassen: jede entbehrliche Auszeichnung entfällt.
- **G05** Betont wird mit **Laut** — **nie** durch Unterstreichen, Sperren oder
  **VERSALIEN**.
- **G23** Versalien per Laufweite sperren, nie mit Leertasten.
- **G25** Ziffern: in Tabellen tabellarisch (tnum), rechtsbündig, exakt
  untereinander — nie mit Leerzeichen ausrichten.

### Ausdrücklich verboten ohne Regeldeckung
Initialen/Drop-Caps, Versal-Auszeichnung, Sperren oder Unterstreichen als
Hervorhebung, zwei Merkmale gleichzeitig im Fließtext, Schmuck. **Wer eine
Auszeichnung weglassen kann, lässt sie weg.**

### Wenn eine Regel der Schrift widerspricht
Die v2.5-Schrift hat Funktionen erhalten, die ältere Regeln (noch) anders
beschreiben. Solche Widersprüche **melden und vom Auftraggeber entscheiden
lassen** — das Regelwerk **nicht** eigenmächtig umschreiben.

## Schnitt-System (Stand v2.5)
- Installierbare statische Schnitte: **Leise (265) · Klar (440) · Deutlich
  (580) · Laut (680)**. Deutlich = Titel; Laut = Inline-/Office-Fettung (⌘B).
- Variable: 6 Named Instances **Flüstern 190 · Leise · Klar · Deutlich · Laut ·
  Schreien 725**.
Bei Änderungen an der Schnittzahl **alle** Beschreibungen mitziehen
(schriften.html, schrift-webfont.html, README, tools.json, Beipackzettel).

## Fonts reproduzierbar bauen
Änderungen an Schriftdateien über die Skripte in `tools/goetheanum-fontfix/`
(idempotent, aus sauberem Stand) — nicht freihändig Binärdateien patchen.
Nach Font-Änderungen Webfonts (woff/woff2) und das Komplett-ZIP neu packen.
