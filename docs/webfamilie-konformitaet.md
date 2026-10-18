# Webfamilie – maschineller Konformitäts-Schnellbefund

Erzeugt von `tools/ds-extern.py` am 6. Juli 2026. Geprüft wird nur statisch Belegbares (HTML + bis zu 6 Stylesheets je Seite); gerenderte Kontrast-Paare u. Ä. stehen im Hand-Befund `webfamilie-befund.md`.

| Seite | Score | bestanden |
|---|---|---|
| https://goetheanum.ch/de | 50 % | 6/12 prüfbar |
| https://dasgoetheanum.com | 25 % | 3/12 prüfbar |
| https://goetheanum.tv | 33 % | 4/12 prüfbar |
| https://anthroposophie.org/de | 8 % | 1/12 prüfbar |

## https://goetheanum.ch/de

- ✗ **E01 Fundament** — Fundament nicht eingebunden (DS01-extern: der eigentliche Auftrag)
- ✗ **E02 Tokens** — 454 Farb-Literale in Farb-Properties · 25× var(--…) (DS02)
- ✓ **E03 Grössen** — keine px-Grössen gefunden
- ✓ **E04 Zeilenhöhe** — keine numerische body/p-Zeilenhöhe gefunden
- ✗ **E05 Fokus** — 15× outline:none/0 · :focus-visible fehlt (WCAG 2.4.7)
- ✗ **E06 Sprunglink** — kein Sprunglink gefunden (WCAG 2.4.1)
- ✓ **E07 Sprache** — lang="de"
- ✗ **E08 Versal-UI** — 7× text-transform:uppercase (G05/G23-Indikator)
- ✗ **E09 Hell/Dunkel** — kein Hell/Dunkel-Mechanismus im CSS (B05)
- ✓ **E10 Schriften** — Schriften selbst gehostet
- ✓ **E11 Alt-Kultur** — 40 Bilder · 0 ohne alt · 0 generisch (WCAG 1.1.1)
- ✓ **E12 Auffindbar** — indexierbar

## https://dasgoetheanum.com

- ✗ **E01 Fundament** — Fundament nicht eingebunden (DS01-extern: der eigentliche Auftrag)
- ✗ **E02 Tokens** — 419 Farb-Literale in Farb-Properties · 2× var(--…) (DS02)
- ✗ **E03 Grössen** — 42× font-size unter 14px, kleinste 8px (B03)
- ✗ **E04 Zeilenhöhe** — line-height 1.4 an body/html/p (B04: ≥1.5)
- ✗ **E05 Fokus** — 5× outline:none/0 · :focus-visible fehlt (WCAG 2.4.7)
- ✗ **E06 Sprunglink** — kein Sprunglink gefunden (WCAG 2.4.1)
- ✓ **E07 Sprache** — lang="de-DE"
- ✗ **E08 Versal-UI** — 9× text-transform:uppercase (G05/G23-Indikator)
- ✗ **E09 Hell/Dunkel** — kein Hell/Dunkel-Mechanismus im CSS (B05)
- ✓ **E10 Schriften** — Schriften selbst gehostet
- ✗ **E11 Alt-Kultur** — 189 Bilder · 93 ohne alt · 0 generisch (WCAG 1.1.1)
- ✓ **E12 Auffindbar** — indexierbar

## https://goetheanum.tv

- ✗ **E01 Fundament** — Fundament nicht eingebunden (DS01-extern: der eigentliche Auftrag)
- ✓ **E02 Tokens** — 1213 Farb-Literale in Farb-Properties · 2792× var(--…) (DS02)
- ✗ **E03 Grössen** — 17× font-size unter 14px, kleinste 8px (B03)
- ✓ **E04 Zeilenhöhe** — body/p-Zeilenhöhen ≥1.5 (B04)
- ✗ **E05 Fokus** — 6× outline:none/0 · :focus-visible vorhanden (WCAG 2.4.7)
- ✗ **E06 Sprunglink** — kein Sprunglink gefunden (WCAG 2.4.1)
- ✓ **E07 Sprache** — lang="de"
- ✗ **E08 Versal-UI** — 8× text-transform:uppercase (G05/G23-Indikator)
- ✗ **E09 Hell/Dunkel** — kein Hell/Dunkel-Mechanismus im CSS (B05)
- ✗ **E10 Schriften** — externe Font-Hosts (Google Fonts u. a.) — Selbst-Hosting empfohlen
- ✗ **E11 Alt-Kultur** — 2 Bilder · 1 ohne alt · 0 generisch (WCAG 1.1.1)
- ✓ **E12 Auffindbar** — indexierbar

## https://anthroposophie.org/de

- ✗ **E01 Fundament** — Fundament nicht eingebunden (DS01-extern: der eigentliche Auftrag)
- ✗ **E02 Tokens** — 543 Farb-Literale in Farb-Properties · 14× var(--…) (DS02)
- ✗ **E03 Grössen** — 17× font-size unter 14px, kleinste 10px (B03)
- ✗ **E04 Zeilenhöhe** — line-height 1.42857 an body/html/p (B04: ≥1.5)
- ✗ **E05 Fokus** — 15× outline:none/0 · :focus-visible fehlt (WCAG 2.4.7)
- ✗ **E06 Sprunglink** — kein Sprunglink gefunden (WCAG 2.4.1)
- ✗ **E07 Sprache** — kein lang-Attribut am <html> (WCAG 3.1.1)
- ✗ **E08 Versal-UI** — 6× text-transform:uppercase (G05/G23-Indikator)
- ✗ **E09 Hell/Dunkel** — kein Hell/Dunkel-Mechanismus im CSS (B05)
- ✗ **E10 Schriften** — externe Font-Hosts (Google Fonts u. a.) — Selbst-Hosting empfohlen
- ✗ **E11 Alt-Kultur** — 124 Bilder · 90 ohne alt · 0 generisch (WCAG 1.1.1)
- ✓ **E12 Auffindbar** — indexierbar

---

**Grenzen des Schnellbefunds:** Geprüft wird nur statisch Ablesbares.
JS-injizierte Mechanismen (z. B. ein per Skript eingefügter Sprunglink oder ein
per `data-theme` geschalteter Dunkelmodus wie auf werkzeuge.goetheanum.ch)
sind für den Prüfer unsichtbar — für eigene Seiten bleibt `tools/ds-lint.py`
das Mass; dieser Aussenblick dient dem Gespräch mit den Betreibern.
