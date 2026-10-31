# Spendenformular goetheanum.io – Befund am gerenderten Blatt (31. 10. 2026)

Gemessen mit Chromium (Playwright) auf 1280 px und 420 px (iPhone 13),
Skript `docs/spenden-messen.js`. Seite: https://goetheanum.io/de/spenden.
Das Formular ist ein iframe von
https://app.goetheanum.io/spende/spenden-goetheanum-ch (Widget
`widget.js?v=donation-20261007`, eigenes CSS, nicht das Design-System).
Darunter das Akkordeon aus `design-system/akkordeon.css`, Kleid Faden,
fünf Themen – die erste Anwendung des Moduls auf goetheanum.io.

## 1. Das Formular – was dort steht (Reihenfolge wie auf der Seite)

1. Spendenzweck (Klappliste, vorbelegt «Weihnachtsspende» – am 31. Oktober)
2. Währung (Klappliste, CHF)
3. Betrag: vier Kacheln 25.00 · 50.00 · 100.00 · 300.00, darunter
   Feld mit − / + und Einheit CHF
4. «Ich spende als» Privatperson · Institution
5. Vorname, Nachname, E-Mail, Strasse und Hausnummer, Postleitzahl, Ort,
   Land – alle vor der Zahlung
6. Kästchen «Spendenbescheinigung gewünscht», Kästchen Datenschutz (Pflicht)
7. Knopf «Jetzt 25 CHF spenden» (dynamische Beschriftung, gut)

Nicht vorhanden: einmalig/monatlich, Zahlungsart sichtbar (Kreditkarte,
PayPal, TWINT werden nur im Lede-Text genannt), Wirkungsangabe am Betrag,
Begründung neben dem Formular. Auf dem Telefon steht vor allem eine
Cookie-Wand (iubenda, «1233 ausgewählte Dritte») – auf einer Spendenseite.

## 2. Messwerte Formular (1280 px; 420 px gleich, da feste px)

| Element | Schrift | Grad | Gewicht | Radius | Höhe |
|---|---|---|---|---|---|
| Klappliste Zweck/Währung | Goetheanum Schrift | 15.2 px | 440 | 6 px | 44 px |
| Legende «Betrag (CHF)» | Goetheanum Schrift | 16 px | 650 | – | – |
| Betrag-Kacheln | Goetheanum Schrift | 16 px | 440 / 580 gewählt | 6 px | 42 px |
| Betragsfeld | Goetheanum Schrift | 18.4 px | 580 | 6 px | 43 px |
| «Privatperson / Institution» (Klasse `pill`) | Goetheanum Schrift | 16 px | 440 / 580 | 6 px | 39 px |
| Feld-Label | Goetheanum Schrift | 15.2 px | 440 | – | – |
| Eingabefelder | Goetheanum Schrift | 15.2 px | 440 | 6 px | 39 px |
| Kästchen | – | – | – | 6 px | 22 px |
| Knopf «Jetzt … spenden» | Goetheanum Schrift | 16.8 px | 680 | 6 px | 47 px |

Es gibt genau einen Radius (6 px) und genau eine Schrift (Goetheanum,
variabel 190–725) – auch in Feldern, Labels, Zahlen und Klapplisten.

Abgleich mit dem Fundament (`design-system/base.css`, `tokens.css`):

- **Schrift-Grenze verletzt.** Label, Wert, Formularfelder, Chips tragen
  im Haus die Lese-Grotesk Source Sans 3 (`--font-text`); hier trägt alles
  die Hausschrift. Das ist der «eingesperrte» Eindruck in den Klapplisten:
  Display-Schrift in 15 px, in einem 6-px-Kasten.
- **B03:** Eingabefelder 15.2 px, Haus verlangt ≥16 px (iOS zoomt sonst);
  Labels 15.2 px knapp über dem Boden 15.
- **B04:** Felder 39 px, Kacheln 42 px, Pillen 39 px; Haus: `--tap` 44 px.
- **Radien:** Haus `--r-control` 10 px (Felder, Knöpfe), `--r-pill` für
  Wahl-Pillen (`.seg`), `--r-card` 14 px. 6 px überall wirkt eckig.
- **G25:** Beträge «25.00» mit Nachkommastellen; Ziffern ohne tnum.
- **B01** hält: Anwahl dunkle Fläche + Weiss.

## 3. Das Akkordeon im Kontext – Messwerte

Umgebung der Seite: Titel «Das Goetheanum unterstützen» 28 px (Titillium),
Lauftext 18 px / 27 px (Source Sans Pro), Fuss 15 px.

| Element | 1280 px | 420 px |
|---|---|---|
| Frage (`.frage`, Deutlich) | 23.2 px / 29 px | 18.2 px / 22.8 px |
| Antwort (`.acc-inner p`, Klar, Hausschrift) | 20 px / 32 px | 18.2 px / 27.3 px |
| Meta «5 Themen» | 16 px | 15.2 px |
| «Alle aufklappen», «Link kopieren» | 16 px | 15.2 px |

Lesart: Auf dem Telefon ist das Modul ruhig (Frage und Antwort gleich
gross, nur das Gewicht unterscheidet, Beiwerk eine Stufe kleiner). Auf dem
breiten Blatt öffnen sich drei Stufen (23 / 20 / 16) in einem Streifen,
dessen Umgebung mit 28 / 18 / 15 läuft – und die Antwort steht mit 20 px
Hausschrift **grösser als der Lauftext der Seite** (18 px Source), zudem
in einer anderen Schrift. Daher das «dynamisch-aufgeregt»: die
Fluid-Tokens (`--t-h3` 20–23, `--t-body` 18–20) laufen auf 1280 px an ihr
oberes Ende, die Seite selbst skaliert nicht mit. Die Hausschrift wird
als «GoetheanumAccordion» separat geladen, das Widget lädt «Goetheanum
Schrift» ein zweites Mal.

## 4. Offene Entscheide (für den Auftraggeber)

1. Antwortgrad im Akkordeon an den Lauftext der Gastseite binden (18 px),
   Frage eine Stufe darüber (20–21 px) – oder die Tokens so lassen und die
   Seite anheben?
2. Formular: auf das Design-System heben (Source in Feldern, 16 px, 44 px,
   `--r-control`) – im Widget oder als eigener Baustein im Fundament?
