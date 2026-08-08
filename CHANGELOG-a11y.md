# A11y- & Typografie-Sanierung (WCAG 2.2 AA · Sofie Beier)

Branch `a11y-typo-refactor`, ein Commit pro Aufgabe. Nachweis je Aufgabe:
**Was · Datei · Begründung (SC / Beier / Messwert)**.

## Block A — Zugänglichkeit

| ID | Was | Datei | Begründung |
|----|-----|-------|------------|
| A1 | Verstecktes `h1` als erstes `main`-Kind; Kachel-Titel `h3`→`h2`; `main#inhalt` | `index.html` | WCAG 1.3.1 / 2.4.6 – genau ein `h1`, keine übersprungene Ebene (verifiziert: 1× h1, dann h2) |
| A2 | Dauerhafter Halt/Weiter-Schalter; Timer läuft nicht bei `paused`; bei `prefers-reduced-motion` von Anfang gestoppt; Punkt-Trefferfläche 26 px via `::before`; aktiver Punkt `aria-current` | `index.html` | WCAG 2.2.2 (Auto-Lauf 6.5 s) · 2.5.8 (Ziel ≥ 24 px). Verifiziert: Index bleibt nach Halt über 7 s stehen; Auto-Lauf ohne Halt läuft |
| A3 | Fokus in den Dialog (erst Schliessen-Knopf, kein Auto-Fokus ins Suchfeld), `aria-modal`, Tab-Falle nur sichtbare Elemente, Fokus zurück auf Burger | `design-system/nav.js` | WCAG 2.4.3 + ARIA-Dialog. Verifiziert: Öffnen→Close-Knopf, Shift+Tab wraps, Escape→Burger |
| A4 | Globaler Sprunglink „Zum Inhalt" (setzt `id=inhalt` auf `<main>`, nach DOM-Ready) | `design-system/nav.js`, `design-system/nav.css` | WCAG 2.4.1 (Verbesserung). Verifiziert auf Startseite + Icons: erstes Tab zeigt/aktiviert den Link |
| A5 | `--gold-ink` `#94702e`→`#8a6728` | `design-system/tokens.css` | WCAG 1.4.3 – auf `--soft` von **4.29** → **4.89:1**, auf Weiss **5.18:1** (Formel des Auftrags) |
| A6 | Je Sektionsfarbe `--on-sek-*` (Weiss nur ≥ 4.5:1, sonst dunkler Sektionston); Checker im Hook | `design-system/tokens.css`, `tools/check-on-sek.py`, `tools/hooks/pre-commit` | WCAG 1.4.3 – lws/js/hpise u. a. versagen mit Weiss; 6 dunkle Töne ≥ 4.6:1, 7× Weiss. Build bricht bei Unterschreiten |
| A7 | Text-tragende Seiten-Toolbars `height`→`min-height`; kanonische Rollen waren schon padding-/`min-height`-basiert | `typografie.html`, `werkzeug.html` | WCAG 1.4.12 – Text-Spacing-Test (LH 1.5 / LS .12 / WS .16 / ¶ 2em) auf Startseite, Icons, Sektionsfarben: kein Clipping |
| A8 | Globaler `@media(prefers-reduced-motion:reduce)`-Block; `.tile:hover` ohne transform | `design-system/base.css`, `index.html` | WCAG 2.3.3 – Übergänge und weiches Scrollen aus |
| A9 | `lang` je fremdsprachiger Tabellenzelle (en/fr/es) | `uebersetzungen.html` | WCAG 3.1.2 – verifiziert: Zell-`lang` = `["-","en","fr","es","-"]` |

## Block B — Typografie & Lesbarkeit (Beier)

| ID | Was | Datei | Begründung |
|----|-----|-------|------------|
| B1 | `.note/.hint/.help/.desc/.subhead` → `--font-text` (Source) | `design-system/base.css` | Kondensierung/geschlossene Aperturen der Display schaden kleinem, dichtem Lesetext |
| B2 | `.kicker/.kick` Klar→Deutlich; `.btn`, `.seg button` explizit Deutlich | `design-system/base.css` | Fettung hilft bei kleinen Sehwinkeln; Stammbreite Klar bei ~13.5 px grenzwertig |
| B3 | `body` (→`.lede`) `letter-spacing:.02em`; `h1,h2` auf 0 | `design-system/base.css` | Tracking-/Crowding-Nutzen gilt Lese-/Kleingraden, nicht grossen Titeln |
| B4 | `size-adjust:103%` (500/486) auf alle Source-Faces | `design-system/tokens.css` | Wahrgenommene Grösse = x-Höhe; gleiche px → gleiche Wirkung, stabiler Fallback |
| B5 | `ascent-override:75%; descent-override:25%; line-gap-override:0%` auf BEIDE Faces | `design-system/tokens.css` | `usWinAscent` 1114 ⇒ uneinheitlicher Durchschuss/Grundlinie. Verifiziert: À/Ü/Ǻ clippen bei LH 1.66 nicht, beide Faces gleiche Boxhöhe; Font-Bug U+01FA separat behoben (#213/#218) |
| B6 | `type-scale.json` (kanonische Leiter) + `tools/check-type-scale.py` (TS1/TS2) im Hook | `design-system/type-scale.json`, `tools/check-type-scale.py`, `tools/hooks/pre-commit` | „Konformität durch Konstruktion": Goetheanum-Rolle < 18 px braucht Deutlich; Leise ≥ 22 px. Regeln an synthetischen Verstössen getestet |
| B7 | Dunkelmodus-Gewichtsabsenkung nur an grossen Display-Rollen (h1/h2/`.h-display`→540); Kleintext/UI behält Hell-Gewicht | `design-system/tokens.css`, `design-system/base.css` | Beier – Fettung hilft klein; kleiner Text soll im Dunkeln nicht dünner werden. Verifiziert: h1 580→540, Kicker/Knopf/Body unverändert. **Abweichung:** Kicker (klein) bleibt Deutlich statt reduziert – erfüllt die Abnahme „kleiner Text nicht leichter" und wahrt B2 |

## Block C — Leseschrift-Umschalter

| ID | Was | Datei | Begründung |
|----|-----|-------|------------|
| C | Kopfzeilen-Schalter „Lesemodus" neben Hell/Dunkel (A-Icon, das die Leseschrift zeigt + Gold-Ring als Zustand); tauscht `body` + `.lede` Display→Source, erhöht Spacing; Titel/Kicker/Kopfzeile bleiben Goetheanum; Zustand in `localStorage('goeRead')`, vor dem Paint gesetzt | `design-system/nav.js`, `design-system/nav.css`, `design-system/base.css` | Nutzerkontrolle ist der best belegte inklusive Faktor. Verifiziert: aus→body Goetheanum; ein→body/lede Source, h1/Kicker bleiben Goetheanum, Icon-A wird Source, Zustand überlebt Reload (kein FOUC). Grösse via B4 stabil; Reflow durch A7 abgesichert. **Symbol:** A mit Font-Wechsel + Gold-Ring statt reiner Buchstabenform (bei 17 px sonst zu subtil) |

## Bewahrt (nicht angefasst)
Fluide rem-Skala · Zeilenhöhe 1.66 · Mass ~62 ch · Betonung nur über Gewicht ·
`hyphens`/`text-wrap:pretty`/orphans/widows · Flattersatz · 44-px-Ziele ·
`:focus-visible` · selbstgehostete OFL-Schriften · `scroll-padding-top` · Landmarken.

## Prüfhinweis (PR)
Empfohlen: eine Runde reine Tastaturbedienung durch Karussell (Halt/Weiter, Punkte)
und Schublade (Öffnen→Fokus, Tab-Falle, Escape→Burger), plus ein Screenreader-Durchgang
(VoiceOver/NVDA). Keine visuelle Regression Hell **und** Dunkel (Startseite + Schriften geprüft).
Design-System-Score bleibt 100 % (29/29).


---

# Block D — die Maschine misst (8. August 2026)

Bis hierher war die Sanierung Handarbeit mit Nachweis. Seit dem 8. August
misst sie eine Maschine: **`tools/barrierefreiheit.mjs`** (Regel **DS08** im
Kontrakt) lädt jede Seite des Geltungsbereichs in Chromium auf zwei Achsen —
390 px (Telefon) und 1440 px (Schreibtisch) — und lässt `axe-core` die
**normativen** Erfolgskriterien der WCAG 2.2 auf Stufe A und AA prüfen. Damit
gelten B01–B05 gemessen statt behauptet.

    node tools/barrierefreiheit.mjs                          # Bericht
    node tools/barrierefreiheit.mjs --check                  # als Tor
    node tools/barrierefreiheit.mjs --seite ordner.html      # nur eine Seite
    node tools/barrierefreiheit.mjs --regel select-name      # nur eine Regelsorte
    node tools/barrierefreiheit.mjs --alles                  # samt Empfehlungen
    node tools/barrierefreiheit.mjs --spur                   # Fortschritt je Seite

Einmalig `cd tools && npm install`. Der ganze Lauf dauert rund sechs Minuten —
darum läuft er **nicht** im Commit-Hook, sondern als eigener Job in
`pruefmaschinen.yml`. Mit `--seite` sind es Sekunden.

## Zwei Griffe, ohne die der Lauf lügt

**Durchblättern vor dem Messen.** Wer eine Seite misst, ohne sie einmal
durchzuscrollen, misst bei allen Blättern mit Einblende-Effekt Schrift in
Grundfarbe auf Grund. Der Prüfer blättert darum jede Seite einmal durch.

**Wer weiterleitet, wird übersprungen.** `services/sommer-zaehler/kurzlink-site/404.html`
ist eine Brücke: sie liest den Pfad und schickt weiter. Ihr Ziel liegt
ausserhalb, wird abgewiesen, und Chromium malt an ihrer Stelle seine eigene
Fehlerseite — die dann gemessen würde. Genau das war der einzige
`meta-viewport`-Fund der Erstmessung: nicht unsere Seite, sondern die des
Browsers. Solche Blätter werden gezählt und übersprungen.

## Sofort behoben

| ID | Was | Datei | Begründung |
|----|-----|-------|------------|
| D1 | `role="tablist"` → `role="group"` auf beiden Tastatur-Umschaltern | `icons.html` | WCAG 1.3.1 – die Knöpfe sind Umschalter mit `aria-pressed`, keine Reiter; `tablist` verlangt Kinder mit `role="tab"` |
| D2 | `role="group"` auf dem Ausgabe-Block ergänzt | `apps/bewegte-schrift/index.html` | WCAG 4.1.2 – `aria-label` auf einem `<pre>` ohne Rolle ist unzulässig; erst die Rolle macht die Beschriftung gültig |

## Rückstand aus der Erstmessung

**69 Verstösse, 399 betroffene Stellen, 120 Messungen.** Sechs Regelsorten —
und der Rückstand ist stark konzentriert: **zwei Seiten tragen ein Viertel
davon.**

| Regel | Stellen | Seiten | Was zu tun ist |
|---|---:|---:|---|
| `color-contrast` | 145 | 14 | Kontrast unter 4.5:1 (B02). Rechnen, nicht schätzen; der Fund nennt Ist-Wert und Sollwert |
| `select-name` | 106 | 2 | Auswahlfelder ohne zugänglichen Namen — ein Platzhalter genügt dort nicht |
| `label` | 82 | 8 | Eingabefelder ohne Beschriftung (WCAG 4.1.2) |
| `target-size` | 28 | 2 | Fingerziele unter dem Mass (B04) |
| `link-in-text-block` | 22 | 4 | Links im Fliesstext, die sich allein durch Farbe unterscheiden (WCAG 1.4.1) |
| `scrollable-region-focusable` | 16 | 10 | Behälter mit `overflow: auto` ohne `tabindex="0"` — die Tastatur kommt nicht an den verborgenen Teil |

Die dicksten Brocken zuerst:

| Stellen | Seite | Was |
|---:|---|---|
| 52 | `ordner.html` | ausschliesslich `select-name` — eine Seite, ein Muster, ein Durchgang |
| 38 | `werkzeug.html` | 23× Kontrast, 15× fehlende Beschriftung |
| 12 | `index.html` | `target-size` |
| 12 | `ineinander.html` | `label` |
| 12 | `schrift-webfont.html` | 11× Kontrast, 1× `label` |
| 10 | `apps/gtv-naming/index.html` | Kontrast |

**Merke für neue Seiten**

- Jeder Behälter mit `overflow: auto` braucht `tabindex="0"`.
- Jedes Auswahl- und Eingabefeld braucht einen Namen — `<label for>` oder
  `aria-label`; ein Platzhalter ist keiner.
- Links im Fliesstext brauchen mehr als Farbe (Unterstreichung).
- Kontrast wird gerechnet: 4.5:1 für Lesetext, 3:1 für grosse oder fette
  Schrift und für Ränder von Bedienelementen.

## Aus dem Bericht wird ein Tor

Der Job `barrierefreiheit` in `pruefmaschinen.yml` läuft bereits mit
`--check`, darf aber scheitern (`continue-on-error`), solange der Rückstand
oben offen ist. Ist er abgetragen, verschwindet diese eine Zeile — dann
blockiert ein Verstoss den Merge wie `typo-check` und `ds-lint`. Ein Tor, das
von Anfang an rot steht, hütet nichts.

**Grenze:** rund ein Drittel der WCAG-Kriterien ist überhaupt maschinell
prüfbar. Ein grüner Lauf heisst «keine der prüfbaren Regeln verletzt» — nicht
«zugänglich». Der Prüfhinweis oben (Tastaturrunde, Screenreader-Durchgang)
bleibt gültig; die Maschine ersetzt ihn nicht, sie hält ihm den Rücken frei.
