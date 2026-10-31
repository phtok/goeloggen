---
name: formular-ux
description: Hausregeln für Formulare im Goetheanum. Diesen Skill bei jedem Formular laden – jeder Eingabemaske, jedem Spenden-, Abo-, Bestell- oder Anmeldeformular, jedem einzelnen Eingabefeld mit Absenden-Knopf, auch bei Review oder Umbau eines bestehenden Formulars (goetheanum.io, werkzeuge.goetheanum.ch, Widgets). Er regelt Schrift, Masse, Aufbau, Texte, Bewegung, Barrierefreiheit und die Schweizer Besonderheiten, je Regel mit Quelle, und trennt Belegtes von Erfahrungswerten.
---

# Formulare im Haus

Ein Formular ist ein Gespräch, kein Verhör: es fragt nur, was es braucht,
in der Reihenfolge, in der man antwortet. Jede Regel hier hat eine Quelle
in Klammern – eine Hausregel-ID oder eine URL. Was keine hat, steht unter
«Was wir nicht belegen können». Ausführlich: `docs/recherche_spendenformular-ux.md`,
`docs/recherche_uebergaenge-lebendig.md`, Befund `docs/spenden-befund-2026-10-31.md`.

**Vom Fundament bauen, nicht freihändig:** `design-system/base.css` § Formular
liefert `.field`, `.seg`, `button.kachel`, `.formgrid`. Wer etwas Neues braucht,
nimmt es dort auf (CLAUDE.md § Optimierungen fliessen zurück).

## 1. Schrift

- Label, Feld, Wert, Chip, Pille, Kästchen-Text und Fehlertext tragen die
  Lese-Grotesk Source Sans 3, `var(--font-text)` (CLAUDE.md § Schrift-Grenze).
- Die Hausschrift trägt nur Titel und Lede des Formulars, dazu den Knopf
  (CLAUDE.md § Grenzen der Hausschrift).
- `base.css` setzt `input, select, textarea, option` schon auf Source – nicht
  überschreiben (`design-system/base.css` § Formularfelder).
- Betrag ohne «.00», Ziffern tabellarisch: «50 CHF», nicht «50.00» (G25).
- Hervorhebung im Formular ändert ein Merkmal, die Anwahl ist Fläche und
  Weiss, kein zusätzlicher Fettschnitt im Fliesstext (G01, B01).

## 2. Masse

- Eingabefelder 16 px Schrift, nie darunter; Zoom nie sperren (B03;
  https://docs.squirrelscan.com/rules/mobile/input-zoom).
- Label und Hinweis `--t-small` (15–16 px), nichts Lesbares unter 14 px (B03).
- Jedes Ziel 44 px hoch, `--tap`: Feld, Kachel, Pille, Knopf und Kästchen
  samt Beschriftung (B04; https://www.nngroup.com/articles/touch-target-size/).
- Felder und Knöpfe `--r-control` (10 px), Wahl-Pillen `--r-pill`, Karten
  `--r-card` (`design-system/tokens.css`).
- Feldrand `--line-control`, ≥3:1 gegen den Grund (B02).
- Einspaltig, Label über dem Feld (https://design-system.service.gov.uk/components/text-input/).
- Wo Felder sich eine Zeile teilen (PLZ und Ort), das `.formgrid`; auf dem
  Telefon fällt es auf eine Spalte (`design-system/base.css` § Eingabe-Raster).
- Feldbreite folgt der Antwort: PLZ schmal, Strasse breit (GOV.UK Text input, s. o.).
- Höhen mit `min-height` und `em`, nie fest – erhöhte Laufweite darf nichts
  abschneiden (WCAG 1.4.12, https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html).

## 3. Aufbau eines Spendenformulars

Reihenfolge, von oben nach unten:

1. **Frequenz** einmalig · monatlich als `.seg` – sichtbar, nicht versteckt;
   «monatlich» nicht vorwählen ohne Test, weil Einmalspenden sinken können
   (https://www.nextafter.com/experiments/how-defaulting-a-form-to-monthly-adding-a-monthly-callout-affects-donor-conversion/;
   https://mrbenchmarks.com/fundraising/).
2. **Betrag** als `button.kachel` in aufsteigender Folge, dazu «Anderer
   Betrag» als freies Feld mit `inputmode="decimal"` und «CHF» im Label
   (https://www.nextafter.com/experiments/how-adding-suggested-gift-amounts-affects-donor-conversion/;
   GOV.UK Text input).
3. Monatlich hat eigene, tiefere Stufen
   (https://www.nextafter.com/experiments/how-more-donation-options-with-a-lower-initial-ask-affects-recurring-donations/).
4. **Zahlart sichtbar** vor dem Absenden, TWINT zuerst (§ 7).
5. **Person minimal:** Vorname, Nachname, E-Mail. Kein Konto, keine
   Telefonnummer (https://baymard.com/research-articles/current-state-of-checkout-ux).
6. **Adresse nur bei Bescheinigung:** das Kästchen «Spendenbescheinigung»
   öffnet die Adressfelder, sonst fragt das Formular nicht danach
   (https://design-system.service.gov.uk/components/radios/ – Conditional reveal).
7. Höchstens zwei Ebenen aufdecken; Betrag und Bescheinigung sind die
   Obergrenze (https://www.nngroup.com/articles/progressive-disclosure/).
8. **Pflichtfelder** sichtbar von freiwilligen getrennt; freiwillige Felder
   lieber streichen (https://www.nngroup.com/videos/required-fields-forms/;
   https://baymard.com/blog/checkout-flow-average-form-fields).
9. **Knopf mit Betrag:** «50 CHF spenden», «20 CHF monatlich spenden» – die
   Beschriftung folgt der Wahl (Befund 31. 10. 2026, heute schon gut gelöst).
10. Formular eingebettet auf der Seite, nicht hinter einem Knopf
    (https://www.nextafter.com/experiments/how-embedding-a-donation-form-impacts-donations-2/ – nur Suchtreffer).

Für Abo und Anmeldung gilt dieselbe Ordnung: zuerst die Wahl (was, wie oft),
dann die Person, dann die Zahlung.

## 4. Texte

- Label statt Platzhalter; Platzhalter höchstens als Formatbeispiel
  (https://www.nngroup.com/articles/form-design-placeholders/).
- Fehlertext sagt, was fehlt und wie es geht: «Geben Sie Ihre E-Mail-Adresse
  ein», nie «Pflichtfeld» (https://design-system.service.gov.uk/components/error-message/).
- Bei mehreren Fehlern eine Übersicht oben, Fokus darauf, jeder Eintrag
  springt zum Feld, gleicher Wortlaut wie am Feld
  (https://design-system.service.gov.uk/components/error-summary/).
- Prüfen, wenn das Feld verlassen wird, nicht beim Tippen
  (https://www.nngroup.com/articles/errors-forms-design-guidelines/).
- Eingaben bleiben nach einem Fehler stehen (WCAG 3.3.7, s. § 6).
- Der Dank steht in `role="status"`, sofort, und sagt, was als Nächstes
  kommt: Mail, Bescheinigung, wann
  (https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html;
  https://arxiv.org/pdf/1503.02729 – Korrelation).
- Anführung mit «…» bzw. `<q>`, feste Leerzeichen zwischen Zahl und Einheit:
  «50&nbsp;CHF» (CLAUDE.md § Umbrüche).
- Knöpfe, Titel und Meldungen `text-wrap: balance` (CLAUDE.md § Umbrüche).

## 5. Bewegung

- Eine Kurve für das Haus: Bloom, `cubic-bezier(.32,.08,.24,1)`, heute
  `--acc-kurve` (`docs/recherche_uebergaenge-lebendig.md` § Bestand).
- Bedingte Felder öffnen Raum: Höhe und Deckkraft zusammen, eine Uhr,
  280 ms auf, 220 ms zu – Eintritt länger als Austritt
  (`docs/recherche_uebergaenge-lebendig.md` § Vorschlag; Memo 31. 10. 2026).
- «Anderer Betrag» weitet sich aus der Kachel zum Feld, statt ein zweites
  Feld darunter zu stellen (`docs/recherche_uebergaenge-lebendig.md` § Formular).
- Fehler erscheinen ohne Animation: der Raum darf sich öffnen, der Text
  steht sofort (https://www.nngroup.com/articles/errors-forms-design-guidelines/).
- Der Dank wächst am Ort des Knopfs, binnen 500 ms, mit `transform` statt
  Höhe (https://web.dev/articles/cls).
- Hover, Fokus und Farbwechsel 100–150 ms, nie länger
  (`docs/recherche_uebergaenge-lebendig.md` § Wahrnehmung von Dauer).
- `prefers-reduced-motion: reduce` setzt jede Dauer auf 0 s; der neue
  Zustand erscheint trotzdem (https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html).
- Kein Überschwingen, kein Federn, solange der Auftraggeber nichts anderes
  entscheidet (`docs/recherche_uebergaenge-lebendig.md` § Offene Fragen).
- Erscheint ein Feld, erfährt es der Screenreader: `aria-expanded` am
  Auslöser, das Feld folgt im DOM direkt (GOV.UK Radios, s. o.; WCAG 4.1.2).

## 6. Barrierefreiheit (WCAG 2.2 AA)

- **1.3.5** `autocomplete` an jedem Personenfeld: `given-name`, `family-name`,
  `email`, `street-address`, `postal-code`, `address-level2`, `country`
  (https://www.w3.org/WAI/WCAG22/Understanding/identify-input-purpose.html).
- **2.5.8** Mindestens 24 px je Ziel; im Haus 44 px, auch das Kästchen
  (https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html; B04).
- **3.3.7** Nichts zweimal fragen: keine E-Mail-Wiederholung, Adresse der
  Bescheinigung = Spenderadresse, Betrag bleibt beim Rücksprung
  (https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html).
- **3.3.8** Kein Rätsel-Captcha, Einfügen in Code-Felder erlauben
  (https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html).
- **3.3.1 / 3.3.3** Fehler in Worten, nie nur Farbe; `aria-invalid` und
  `aria-describedby` am Feld (https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html).
- Auf farbigem Grund steht Weiss; Anwahl Gold-dunkel und Weiss (B01).
- Gemessen wird mit `node tools/barrierefreiheit.mjs --seite <pfad>` (DS08),
  angeschaut auf 420 px und 1280 px (CLAUDE.md § Das Auge prüft das Gewicht).

## 7. Schweiz

- TWINT als erste Zahlart, danach Karte und Wallets, dann PayPal (RaiseNow
  2025: TWINT 68,1 % des CHF-Volumens,
  https://www.raisenow.com/en/about/press/fundraising-study-2025).
- Beide TWINT-Wege erklären: mobil App-Wechsel, am Rechner QR-Code
  (https://fundraiseup.com/docs/twint/).
- TWINT trägt höchstens 5&nbsp;000 CHF; daneben Überweisung oder
  QR-Rechnung nennen (https://docs.stripe.com/payments/twint).
- QR-Rechnung zum Herunterladen neben dem Formular (Einzahlungsscheine seit
  30. 9. 2022 abgelöst, https://www.postfinance.ch/de/ueber-uns/medien/newsroom/einzahlungsscheine-werden-2022-vom-markt-genommen.html).
- Gebühren je Zahlart offen nennen, Übernahme anbieten
  (https://www.projuventute.ch/de/spenden).
- Bescheinigung ehrlich benennen: wann sie kommt, keine feste Zusage zum
  Abzug, weil die Kantone abweichen; Deutschland gesondert klären
  (https://www.zh.ch/de/steuern-finanzen/steuern/steuern-natuerliche-personen/spenden-an-gemeinnuetzige-organisationen.html;
  https://www.finanzverwaltung.nrw.de/spenden).
- Ein Cookie-Hinweis sperrt den Zahlschritt nicht; «Alle akzeptieren» und
  «Ablehnen» gleich gross (EDÖB-Merkblatt 27. 3. 2026,
  https://www.edoeb.admin.ch/dam/de/sd-web/ByXs53ExpIEy/20260327%20Merkblatt%20Cookies_DE.pdf;
  https://www.nber.org/papers/w34025). Rechtsfrage: Anwalt, nicht Skill.

## 8. Was wir nicht belegen können

Als **Erfahrungswert** führen, nie als Studie ausgeben:

- dass sichtbare Zahlungslogos oder ein Sicherheitshinweis mehr Spenden bringen;
- dass «50 CHF» statt «50.00» mehr Spenden bringt (es ist Hausregel G25, kein Effekt);
- dass eine Wirkungsangabe je Betrag wirkt – und sie steht nur, wenn sie wahr ist;
- dass die Reihenfolge der Zahlarten die Quote hebt (Stripe dokumentiert nur die Technik);
- dass «Adresse nur bei Bescheinigung» die Quote hebt (Baymard misst Felder, nicht diesen Fall);
- dass die amerikanischen A/B-Tests auf Dornach und CHF übertragbar sind;
- dass eine Zweitanfrage «monatlich» auf der Dankesseite wirkt;
- dass die Bloom-Bewegung die Quote beeinflusst – sie ist Gestalt, kein Hebel;
- die Zahl «Label oben ist doppelt so schnell» (Wroblewski, nicht verifiziert);
- Blog-Zahlen wie «Dank binnen 48 Stunden, viermal mehr Wiederkehr».

Wer eine dieser Fragen klären will: A/B-Test auf dem eigenen Formular,
Ergebnis in `docs/` festhalten.
