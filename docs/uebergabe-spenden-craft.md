# Übergabe Spenden an goetheanum.io (Craft CMS)

Für den Developer von goetheanum.io. Stand 31.&nbsp;10.&nbsp;2026,
Design-System 1.30.0. Alles Weitere steht im Repo, hier nur verlinkt.

Schau mit Code zum Kopieren:

- Formular: https://werkzeuge.goetheanum.ch/spenden-formular.html#code
- Akkordeon: https://werkzeuge.goetheanum.ch/akkordeon.html#craft

## a. Geändert seit der ersten Lieferung

- [ ] **Bewegungs-Tokens (1.29.0):** `--kurve-bloom`, `--dauer-hauch`
      120, `--dauer-kurz` 220, `--dauer-mittel` 280, `--dauer-lang`
      400&nbsp;ms, unter `prefers-reduced-motion` 0&nbsp;s. `akkordeon.js`
      liest sie; ohne Tokens gelten die alten Werte. Token-Auszug neu kopieren.
- [ ] **Gast-Variablen (1.30.0):** `--acc-t-frage`, `--acc-t-antwort` am
      `.acc-liste`. Für goetheanum.io: `.acc-liste{--acc-t-frage:21px;--acc-t-antwort:18px}`
      (Lauftext dort 18&nbsp;px, gemessen in
      https://github.com/phtok/goeloggen/blob/main/docs/spenden-befund-2026-10-31.md).
- [ ] **Abstand schmal (1.30.0):** Kleid Faden hält jetzt auch unter
      560&nbsp;px 16&nbsp;px zum Faden und zur rechten Kante.
      `akkordeon.css` neu kopieren.
- [ ] **Formular-Baustein (1.30.0):** neu, siehe c.

## b. Akkordeon

- [ ] `akkordeon.css` kopieren:
      https://github.com/phtok/goeloggen/blob/main/design-system/akkordeon.css
- [ ] `akkordeon.js` kopieren:
      https://github.com/phtok/goeloggen/blob/main/design-system/akkordeon.js
- [ ] Token-Auszug (nur ohne `tokens.css`), mit der Gast-Zeile am Ende:
      https://werkzeuge.goetheanum.ch/akkordeon.html#craft → «Token-Auszug»
- [ ] Twig-Partial (Matrix-Block, Felder `frage`, `antwort`):
      https://werkzeuge.goetheanum.ch/akkordeon.html#craft → «Twig».
      Anker aus `zeile.id`, nicht aus `loop.index`.
- [ ] Kleid `faden`, `data-sek` leer (Gold) auf der Spendenseite.

## c. Formular (Widget auf app.goetheanum.io)

Dateien:

- [ ] `formular.css`:
      https://github.com/phtok/goeloggen/blob/main/design-system/formular.css
- [ ] `formular.js`:
      https://github.com/phtok/goeloggen/blob/main/design-system/formular.js
- [ ] Vorlage HTML: https://werkzeuge.goetheanum.ch/spenden-formular.html#code
      → «Markup» (Quelle: https://github.com/phtok/goeloggen/blob/main/spenden-formular.html,
      zwischen `<!-- formular:anfang -->` und `<!-- formular:ende -->`)
- [ ] Token-Auszug für das Widget-CSS: dieselbe Stelle → «Token-Auszug».
      Dazu braucht das Widget die Feldrollen aus
      https://github.com/phtok/goeloggen/blob/main/design-system/base.css
      (`.field`, `.lab`, `.hint`, `.seg`, `.formgrid`, `.btn`, `.num`,
      `.sr-only`) – entweder `base.css` einbinden oder diese Regeln übernehmen.
- [ ] Anbindung: `GoetheanumFormular.init(form).absenden = function(daten){ return fetch(…) }`
      – Promise erfüllt: Dank erscheint; Promise verworfen: Knopf wird wieder frei.
      `daten` enthält `frequenz`, `betrag`, `waehrung`, `zahlart`,
      `bescheinigung`, `vorname`, `nachname`, `email`, `zweck` und – nur mit
      Bescheinigung – `strasse`, `plz`, `ort`, `land`.

Reihenfolge der Felder (nicht umstellen):

1. Fehlerzusammenfassung (verborgen bis zum ersten Absenden)
2. Häufigkeit: Einmalig · Monatlich, Einmalig vorgewählt
3. Betrag: Stufen, dazu «Anderer Betrag in CHF»
4. Zahlungsart: TWINT · Karte · PayPal · QR-Rechnung, ohne Vorwahl
5. Vorname · Name · E-Mail
6. Kästchen «Spendenbescheinigung gewünscht» → Strasse und Hausnummer ·
   Postleitzahl · Ort · Land
7. Spendenzweck
8. Knopf «Jetzt 50&nbsp;CHF spenden», darunter der Gebührensatz

`autocomplete`:

| Feld | Token |
|---|---|
| Anderer Betrag | `transaction-amount` |
| Vorname | `given-name` |
| Name | `family-name` |
| E-Mail | `email` |
| Strasse und Hausnummer | `address-line1` |
| Postleitzahl | `postal-code` |
| Ort | `address-level2` |
| Land | `country` |

Fehlertexte (im Markup als `data-leer`, `data-format`, `data-min-text`):

- Wählen Sie einen Betrag oder geben Sie einen eigenen ein.
- Geben Sie den Betrag als Zahl ein, zum Beispiel 80.
- Der Betrag muss mindestens 1&nbsp;CHF sein.
- Wählen Sie, wie Sie bezahlen möchten.
- Geben Sie Ihren Vornamen ein.
- Geben Sie Ihren Namen ein.
- Geben Sie Ihre E-Mail-Adresse ein; dorthin geht die Bestätigung.
- Geben Sie die E-Mail-Adresse vollständig ein, etwa name@beispiel.ch.
- Geben Sie Strasse und Hausnummer ein.
- Geben Sie die Postleitzahl ein.
- Geben Sie den Ort ein.

Was das Backend liefern muss – **offen, bitte angeben:**

- [ ] Zahlarten, die wirklich angeboten werden, je mit Hinweistext; TWINT-Höchstbetrag (heute 5&nbsp;000&nbsp;CHF angenommen)
- [ ] Stufen je Häufigkeit und Vorwahl (heute einmalig 20–1000, Vorwahl 50; monatlich 10–200, Vorwahl 20)
- [ ] Spendenzwecke (heute «Wo es am nötigsten ist», «Weihnachtsspende»)
- [ ] Bescheinigung: ab welchem Betrag und wann sie kommt (Buchhaltung) – der Satz unter dem Knopf und der Dank richten sich danach
- [ ] Gebühren je Zahlart, falls sie genannt werden sollen
- [ ] Wortlaut der Bestätigungs-Mail

## d. Abnahme

- [ ] Eingabefelder 16&nbsp;px, Wahl-Pillen 16&nbsp;px, Betrag-Stufen 18&nbsp;px
- [ ] Jedes Ziel ≥44&nbsp;px hoch: Felder, Pillen, Stufen, Kästchenzeile, Knopf
- [ ] Felder, Pillen, Fehler und Label in Source Sans 3; Titel und Knopf in Goetheanum
- [ ] Felder und Knopf Radius 10&nbsp;px (`--r-control`), Pillen rund
- [ ] Gewählt = dunkles Gold mit weisser Schrift
- [ ] Adresse erscheint erst mit dem Kästchen, geschlossen nicht fokussierbar
- [ ] Fehler: Liste oben mit Fokus, Sprunglinks, Text am Feld, kein Wackeln
- [ ] Knopf zeigt Betrag und «monatlich»; Dank erscheint am Ort des Knopfs
- [ ] `prefers-reduced-motion: reduce`: alles erscheint ohne Bewegung
- [ ] Akkordeon schmal (375–420&nbsp;px): Text ≥16&nbsp;px vom Faden und vom rechten Rand
- [ ] axe-core ohne Verstoss (WCAG 2.2 AA) in Ruhe, Fehler, Adresse, Dank; hell und dunkel
- [ ] Angeschaut bei 420 und 1280&nbsp;px

## e. Links

- Formular live: https://werkzeuge.goetheanum.ch/spenden-formular.html
- Akkordeon live: https://werkzeuge.goetheanum.ch/akkordeon.html
- Spendenseite heute: https://goetheanum.io/de/spenden
- Entscheide: https://github.com/phtok/goeloggen/blob/main/docs/spenden-review-2026-10-31.md
- Befund mit Messwerten: https://github.com/phtok/goeloggen/blob/main/docs/spenden-befund-2026-10-31.md
- Formular-Regeln: https://github.com/phtok/goeloggen/blob/main/project-skills/formular-ux/SKILL.md
- Ledger: https://github.com/phtok/goeloggen/blob/main/design-system/CHANGELOG.md
- Tokens: https://github.com/phtok/goeloggen/blob/main/design-system/tokens.css
