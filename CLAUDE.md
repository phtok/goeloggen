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

### Barrierefreiheit ist verbindlich (WCAG 2.2 AA)
Für jede Web-Oberfläche gilt, geprüft (Kontraste rechnen, nicht schätzen):
- **B01 Kein dunkler Text auf farbigem Grund.** Auf Blau/Gold/Grün steht
  **Weiss** (`--on-accent`). Auswahl-Pille = dunkles Gold + Weiss (≥4.5:1),
  Aktion = volles Blau + Weiss. Nie Schwarz auf Farbe.
- **B02 Kontrast** (WCAG 1.4.3/1.4.11): Lesetext ≥ **4.5:1**, grosse/fette
  Schrift und UI-/Grafik-Ränder ≥ **3:1**. `--muted` nur dort, wo es das hält.
- **B03 Mindestgrössen mobil:** Fliesstext **≥16px** (Standard 17–19), Meta
  **≥14px**, nichts unter 13. Eingabefelder **≥16px** (sonst zoomt iOS).
- **B04 Fingerziele ≥44px** (`--tap`); Zeilenhöhe Lesetext ≥1.5.
- **B05 Hell/Dunkel** kommt allein aus den Tokens; Flächen tokenisieren
  (`--paper`/`--field-bg`/`--bar-bg`), nie `#fff` hart verdrahten.

### Grenzen der Hausschrift (bewusst einsetzen)
Goetheanum ist **Display** – die Stimme. Sie hat zwei Grenzen:
- **Textmasse:** ein paar gut gesetzte Zeilen (magisches Quadrat) sind kein
  Problem; **echter Mengentext** läuft in **Source Sans 3** (`.prose`).
- **Kleine UI-Schrift:** **Leise** verschwimmt klein – Minimum ist **Klar**,
  Titel/Marken **Deutlich**. Kleine Labels nie in Leise setzen.
Das Menü **koordiniert, es erklärt nicht**: nur Titel, kein Beiwerk-Text.

## Bauen neuer Seiten und Werkzeuge — vom Fundament aus, nicht freihändig
Konformität entsteht durch Konstruktion, nicht durch Nachkontrolle. Darum gilt
für **jede** neue HTML-Seite oder jedes neue Werkzeug:

1. **Vom Starter ausgehen:** `design-system/starter.html` kopieren — nicht bei
   null beginnen. Das Schaufenster `design-system/` zeigt, was bereitsteht.
2. **Einbinden statt kopieren:** `design-system/tokens.css` und
   `design-system/base.css` per `<link>` einbinden. Tokens nutzen
   (`var(--gold)`, `var(--s6)`, `var(--w-deutlich)` …), **keine** eigenen Farb-,
   Schnitt- oder Abstandswerte erfinden. (Bestehende Apps mit kopiertem Block
   werden schrittweise auf diese Schicht gehoben — neue Seiten starten richtig.)
3. **Registrieren:** einen Eintrag in `tools.json` ergänzen (erscheint im Hub).
4. **Hook aktiv halten:** `git config core.hooksPath tools/hooks` — `tools/typo-check.py`
   prüft die geänderten HTML-Texte beim Commit und blockiert bei Schwere ‹fehler›.
   Vor dem Commit gilt weiterhin: betroffene Regel-IDs nennen.

Die eingebauten Defaults in `base.css` setzen die Hausregeln bereits um (Trennung,
‹…› über `<q>`, tabellarische Ziffern, Betonung = Laut, Leise statt Kursive). Für
Falsches (Unterstreichen, Versal-Hervorhebung, Sperren) gibt es **kein** Utility.

### Optimierungen fließen zurück ins Fundament
Was an **einer** Seite am Design verbessert wird (z. B. die Gold/Weiss-Anwahl der
Buttons und Pillen), gehört **sofort in `tokens.css`/`base.css`** und von dort in
alle Werkzeuge — nicht lokal in einer Seite belassen. Eine Verbesserung am Rand
ist erst fertig, wenn sie im Design-System steht und überall gilt.

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
