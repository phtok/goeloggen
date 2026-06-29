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
Die v2.6-Schrift hat Funktionen erhalten, die ältere Regeln (noch) anders
beschreiben. Solche Widersprüche **melden und vom Auftraggeber entscheiden
lassen** — das Regelwerk **nicht** eigenmächtig umschreiben.

### Barrierefreiheit ist verbindlich (WCAG 2.2 AA)
Für jede Web-Oberfläche gilt, geprüft (Kontraste rechnen, nicht schätzen):
- **B01 Kein dunkler Text auf farbigem Grund.** Auf Blau/Gold/Grün steht
  **Weiss** (`--on-accent`). Auswahl-Pille = dunkles Gold + Weiss (≥4.5:1),
  Aktion = volles Blau + Weiss. Nie Schwarz auf Farbe.
- **B02 Kontrast** (WCAG 1.4.3/1.4.11): Lesetext ≥ **4.5:1**, grosse/fette
  Schrift und UI-/Grafik-Ränder ≥ **3:1**. `--muted` nur dort, wo es das hält.
- **B03 Mindestgrössen (inklusiv, Stand 2026):** Fliesstext **≥16px**
  (Standard **18–20**, `--t-body`), Meta/Label **≥15** (`--t-small`), nichts
  Lesbares **unter 14** (Floor `--t-micro`). Eingabefelder **≥16px** (sonst zoomt
  iOS). Norm: ‹bei 16 beginnen und hochskalieren› – feste px unter 14 = DS03-Fehler.
- **B04 Fingerziele ≥44px** (`--tap`; WCAG 2.2 SC 2.5.8 fordert ≥24, wir geben 44);
  Zeilenhöhe Lesetext **≥1.5** (`--lh-body` 1.6). Layout muss erhöhte Laufweiten
  überstehen (WCAG 1.4.12): Container in `ch`/`%`, nicht in festen px-Höhen.
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
4. **Hook aktiv halten:** `git config core.hooksPath tools/hooks` — beim Commit
   laufen `tools/typo-check.py` (Sprache, blockiert bei ‹fehler›) **und**
   `tools/ds-lint.py --staged` (Gestalt, vorerst berichtend). Vor dem Commit gilt
   weiterhin: betroffene Regel-IDs nennen — sprachlich (G/B) wie strukturell (DS).

Die eingebauten Defaults in `base.css` setzen die Hausregeln bereits um (Trennung,
‹…› über `<q>`, tabellarische Ziffern, Betonung = Laut, Leise statt Kursive). Für
Falsches (Unterstreichen, Versal-Hervorhebung, Sperren) gibt es **kein** Utility.

### Optimierungen fließen zurück ins Fundament
Was an **einer** Seite am Design verbessert wird (z. B. die Gold/Weiss-Anwahl der
Buttons und Pillen), gehört **sofort in `tokens.css`/`base.css`** und von dort in
alle Werkzeuge — nicht lokal in einer Seite belassen. Eine Verbesserung am Rand
ist erst fertig, wenn sie im Design-System steht und überall gilt.

## Konformitäts-Engine — das System prüft, korrigiert, atmet selbst
Konformität wird **konstruiert und durch eine Maschine erzwungen**, nicht von Hand
nachkontrolliert. Symmetrisch zur sprachlichen Schleife (`typo-check`/`typo-sync`)
gibt es die **Gestalt-Schleife**:

- **Vertrag:** `design-system/contract.json` (Regeln DS01–DS07: Pflicht-Includes,
  nur Token-Farben, Grössen-Untergrenze B03, kanonische Rollen, verbotene Muster).
- **Prüfen:** `tools/ds-lint.py` — `ds-lint.py` (Audit + **Score**),
  `--staged` (Hook), `--score`. Meldet Verstösse nach Regel-ID + `Datei:Zeile`.
- **Korrigieren:** `tools/ds-fix.py` — hebt die Hauspalette **property-bewusst**
  auf Tokens (weisse Schrift → `--on-accent`, weisse Fläche → `--paper`).
  Vorschau ohne, schreiben mit `--apply`. Idempotent.

**Artefakt-Farben schützen:** physische Farben (gedruckte Karte ist immer weiss,
ein Telefon-Mockup zeigt die echte App) sind **keine** Theme-Flächen. Solche
Literale mit `# ds-ok` in der Zeile markieren — Checker und Codemod lassen sie
dann in Ruhe. Die Maschine *schlägt vor*, der Mensch *ratifiziert* die echte
Ausnahme; diese Ratifizierung wird Teil des Codes.

### Der Atem (Aufnahme-Schleife)
Neue Lösung auf einer Seite → `ds-lint` erkennt die Abweichung (DS04) → **aufnehmen**
(in `tokens.css`/`base.css` + ggf. `contract.json`, Eintrag in
`design-system/CHANGELOG.md`, `version` erhöhen) **oder auflösen** (`ds-fix`).
Aufgenommenes gilt ab dann überall. Der **Beschluss-Ledger**
(`design-system/CHANGELOG.md`) ist das Gedächtnis; der Score (`ds-lint --score`)
macht „wie weit weg" zu einer Zahl statt eines Gefühls.

## Schnitt-System (Stand v2.6)
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
