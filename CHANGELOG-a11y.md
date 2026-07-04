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
Optional, **nur nach Rückfrage** (noch offen).

## Bewahrt (nicht angefasst)
Fluide rem-Skala · Zeilenhöhe 1.66 · Mass ~62 ch · Betonung nur über Gewicht ·
`hyphens`/`text-wrap:pretty`/orphans/widows · Flattersatz · 44-px-Ziele ·
`:focus-visible` · selbstgehostete OFL-Schriften · `scroll-padding-top` · Landmarken.

## Prüfhinweis (PR)
Empfohlen: eine Runde reine Tastaturbedienung durch Karussell (Halt/Weiter, Punkte)
und Schublade (Öffnen→Fokus, Tab-Falle, Escape→Burger), plus ein Screenreader-Durchgang
(VoiceOver/NVDA). Keine visuelle Regression Hell **und** Dunkel (Startseite + Schriften geprüft).
Design-System-Score bleibt 100 % (29/29).
