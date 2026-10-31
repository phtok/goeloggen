# Review: Spendenformular goetheanum.io (31. 10. 2026)

Das Formular auf https://goetheanum.io/de/spenden fragt sieben Personenfelder
vor der Zahlung ab, bietet weder «monatlich» noch eine sichtbare Zahlart und
steht in der Hausschrift mit 15&nbsp;px-Feldern, 39&nbsp;px-Zielen und 6&nbsp;px-Ecken –
damit verletzt es die Schrift-Grenze, B03 und B04. Die schnellsten Gewinne
liegen in Kürzen, Sichtbarmachen und Heben auf das Fundament, nicht in neuer
Gestalt. Das Akkordeon darunter ist auf dem breiten Blatt zu laut, weil seine
Antwort grösser läuft als der Lauftext der Seite.

Grundlagen: Befund https://github.com/phtok/goeloggen/blob/main/docs/spenden-befund-2026-10-31.md,
Recherche https://github.com/phtok/goeloggen/blob/main/docs/recherche_spendenformular-ux.md,
Bewegung https://github.com/phtok/goeloggen/blob/main/docs/recherche_uebergaenge-lebendig.md,
Memo https://github.com/phtok/goeloggen/blob/main/docs/memo-lebendige-gesten-2026-10-31.md,
Hausregeln https://github.com/phtok/goeloggen/blob/main/project-skills/formular-ux/SKILL.md.

Im Bau: der Prototyp https://werkzeuge.goetheanum.ch/spenden-formular.html
und das Moodboard https://werkzeuge.goetheanum.ch/moodboard-lebendig.html.

## Was heute steht

Gemessen am 31. 10. 2026 mit Chromium auf 1280&nbsp;px und 420&nbsp;px; das
Formular ist ein iframe von https://app.goetheanum.io/spende/spenden-goetheanum-ch
mit eigenem CSS.

- **Reihenfolge:** Zweck (vorbelegt «Weihnachtsspende» am 31. Oktober) ·
  Währung · Betrag (vier Kacheln 25.00 bis 300.00 und Feld mit − / +) ·
  Privatperson oder Institution · sieben Personen- und Adressfelder ·
  zwei Kästchen · Knopf «Jetzt 25 CHF spenden».
- **Es fehlt:** einmalig oder monatlich, sichtbare Zahlart (TWINT steht nur
  im Lede-Text), Wirkung am Betrag, ein Satz, warum.
- **Schrift:** alles in der Hausschrift, auch Felder, Labels und Zahlen –
  die Schrift-Grenze verlangt Source Sans 3.
- **Masse:** Felder 15.2&nbsp;px Schrift (B03 verlangt 16), Felder 39&nbsp;px,
  Kacheln 42&nbsp;px, Pillen 39&nbsp;px, Kästchen 22&nbsp;px (B04 verlangt 44,
  WCAG 2.5.8 mindestens 24), ein Radius von 6&nbsp;px überall (Haus 10&nbsp;px).
- **Ziffern:** «25.00» mit Nachkommastellen, ohne tnum (G25).
- **Hält:** Anwahl dunkle Fläche und Weiss (B01); Knopf nennt den Betrag.
- **Telefon:** zuerst eine Cookie-Wand mit «1233 ausgewählte Dritte».

## Was wir ändern

**A** sofort, ohne Test – Fehler gegen Hausregel oder WCAG.
**B** mit Test – belegt anderswo, Wirkung hier offen.
**C** später – braucht einen Entscheid oder einen Partner.

1. **A · Auf das Fundament heben:** Source in Label, Feld, Wert und Chip;
   Felder 16&nbsp;px; jedes Ziel 44&nbsp;px, Kästchen eingeschlossen;
   `--r-control` statt 6&nbsp;px (Schrift-Grenze, B03, B04, WCAG 2.5.8).
2. **A · Beträge ohne «.00»,** tabellarische Ziffern: «50 CHF»
   (G25).
3. **A · Adresse nur bei Bescheinigung:** das Kästchen öffnet die
   Adressfelder; ohne Bescheinigung bleiben Vorname, Nachname, E-Mail
   (Baymard Feldzahl; NextAfter Care Net +107&nbsp;%; GOV.UK Conditional reveal).
4. **A · Zweck nicht vorbelegen mit einer Saison,** die noch nicht ist;
   Standard «Wo es am nötigsten ist» (GOV.UK Radios: Vorauswahl wird
   übersehen).
5. **A · `autocomplete` an allen Personenfeldern,** `inputmode="decimal"`
   am Betrag, Fehler als Satz mit `aria-describedby` (WCAG 1.3.5, 3.3.1,
   3.3.3; GOV.UK Error message).
6. **A · Zahlart sichtbar, TWINT zuerst,** dann Karte und Wallets, PayPal;
   QR-Rechnung zum Herunterladen daneben (RaiseNow 2025: TWINT 68,1&nbsp;% des
   CHF-Volumens; Stripe TWINT-Grenze 5&nbsp;000 CHF).
7. **B · Frequenz einmalig · monatlich** als Pille über dem Betrag, ohne
   Vorauswahl; monatlich mit eigenen, tieferen Stufen (M+R 2026: 27&nbsp;%
   des Online-Umsatzes; NextAfter 2025: Monatsstandard kostet −34,2&nbsp;%
   Einmalspenden; Leadership Institute).
8. **B · Fünf bis sechs Betragsstufen** statt vier, aufsteigend, freies
   Feld als sechste Kachel, die sich zum Feld weitet (NextAfter
   CaringBridge +104&nbsp;%; Jerusalem Prayer Team; GetUp, schwach).
9. **B · Tiefste Stufe als Anker prüfen:** 25 CHF halten oder 30 CHF
   testen, nie unter 10 CHF (NextAfter Jerusalem Prayer Team +60,6&nbsp;% Umsatz
   je Besucher; RaiseNow: Ø 33,5 CHF).
10. **B · Privatperson oder Institution streichen** oder hinter «Ich spende
    für eine Institution» falten (NextAfter Care Net; Gegenbeispiel Buckner,
    darum Test).
11. **C · Cookie-Wand vom Zahlschritt lösen,** «Alle akzeptieren» und
    «Ablehnen» gleich gross – nach Rechtsprüfung (EDÖB-Merkblatt 27. 3.
    2026; Farronato u.&nbsp;a. 2025).
12. **C · Gebühren je Zahlart nennen** und Übernahme anbieten; Termin der
    Bescheinigung sagen, keine Kantonszusage (Pro Juventute; Kanton Zürich).
13. **C · Dankesseite und Mail sofort,** mit dem, was geschieht
    (DonorsChoose, Korrelation; WCAG 4.1.3).

## Akkordeon im Kontext

**Empfehlung:** Den Antwortgrad an den Lauftext der Gastseite binden, die
Frage eine Stufe darüber setzen. Auf goetheanum.io heisst das: Antwort
18&nbsp;px wie der Lauftext, Frage 20–21&nbsp;px, Meta 15–16&nbsp;px.

| Element | heute 1280&nbsp;px | heute 420&nbsp;px | Gastseite | Vorschlag |
|---|--:|--:|--:|--:|
| Frage (Deutlich) | 23.2&nbsp;px | 18.2&nbsp;px | Titel 28&nbsp;px | 20–21&nbsp;px |
| Antwort (Klar) | 20&nbsp;px | 18.2&nbsp;px | Lauftext 18&nbsp;px | 18&nbsp;px |
| Meta, «Alle aufklappen» | 16&nbsp;px | 15.2&nbsp;px | Fuss 15&nbsp;px | 15–16&nbsp;px |

Begründung: Auf 420&nbsp;px ist das Modul schon ruhig (Frage und Antwort
gleich gross, nur das Gewicht unterscheidet – G01). Auf 1280&nbsp;px laufen
die Fluid-Tokens `--t-h3` und `--t-body` an ihr oberes Ende, die Seite
skaliert nicht mit; die Antwort steht dann 2&nbsp;px grösser als der Lauftext
und in einer anderen Schrift. Das ist das «Aufgeregte». Ein Modul, das zu
Gast ist, nimmt den Grad des Hauses an, in dem es steht – technisch über
eine Variable am Wurzelelement des Akkordeons (`--acc-t-body`), die die
Gastseite setzt. Nebenbei: Die Hausschrift wird zweimal geladen
(«GoetheanumAccordion» und «Goetheanum Schrift» im Widget); einmal genügt.

## Wie es stimmiger wird für das Goetheanum

**Sprache.** Das Formular spricht wie ein Mensch am Empfang, nicht wie eine
Kasse: «Wie möchten Sie helfen?» statt «Spendenzweck», «Ihre Spende wirkt
dort, wo sie gerade fehlt» als ein Satz Begründung, Knopf «50 CHF schenken»
oder «50 CHF spenden». Kein «Jetzt», kein Ausrufezeichen. Fehler sagen, was
fehlt, und duzen nicht.

**Wirkung.** Eine Zeile unter dem Betrag, nur wenn sie wahr ist: was 50 CHF
am Goetheanum tragen. Ohne belegte Angabe bleibt die Zeile weg (G03; die
Wirkung von Wirkungsangaben selbst ist nicht belegt).

**Gesten des Lebendigen** (Memo 31. 10. 2026) – im Formular drei, alle mit
der Bloom-Kurve `cubic-bezier(.32,.08,.24,1)`, 280&nbsp;ms auf, 220&nbsp;ms zu,
bei reduzierter Bewegung 0&nbsp;s:

- **Betrag wählen – Steigerung.** Die Kacheln stehen aufsteigend; die
  gewählte nimmt Fläche und Weiss an (ein Merkmal, G01). «Anderer Betrag»
  weitet sich aus seiner Kachel zum Feld – eins geht aus dem anderen hervor,
  statt dass ein zweites Feld darunter auftaucht.
- **Felder wachsen – Polarität.** Das Kästchen «Bescheinigung» öffnet den
  Raum für die Adresse und schliesst ihn wieder; auf und zu sind ein Paar,
  das Schliessen ist kürzer (Reduktion). Fehlertexte wachsen nicht, sie
  stehen sofort da.
- **Der Dank geht aus dem Knopf hervor – Übergang.** Nach dem Absenden
  wird der Knopf zur Dankesfläche am selben Ort, binnen 400&nbsp;ms, in einer
  `role="status"`-Region. Keine neue Seite, kein Sprung: der Mensch sieht,
  dass seine Handlung angekommen ist.

So enthält das Formular das Ganze: dieselbe Kurve wie Menü und Akkordeon,
dieselben Tokens, dieselbe Stimme.

## Entscheide für den Auftraggeber

1. **Formular auf das Fundament heben – als eigener Baustein
   `design-system/formular.css`, den das Widget einbindet.** Empfehlung: ja,
   weil dann jede Verbesserung (Grösse, Bewegung, Fehlertext) einmal gebaut
   wird und überall gilt.
2. **«Monatlich» anbieten, ohne Vorauswahl.** Empfehlung: ja, weil
   Dauerspenden ein Viertel des Online-Umsatzes tragen, die Vorauswahl aber
   nachweislich Einmalspenden kostet.
3. **Adresse nur bei Bescheinigung abfragen.** Empfehlung: ja, weil vier
   von sieben Feldern dann für die meisten Spendenden entfallen; dafür
   klärt die Buchhaltung, ab welchem Betrag eine Bescheinigung kommt.
4. **Akkordeon-Antwort an den Lauftext der Gastseite binden (18&nbsp;px),
   Frage 20–21&nbsp;px.** Empfehlung: ja, weil ein Modul zu Gast den Grad des
   Hauses annimmt und so auf jedem Blatt ruhig steht.
5. **Bewegungs-Tokens ins Fundament (`--kurve-bloom`, `--dauer-kurz` 220&nbsp;ms,
   `--dauer-mittel` 280&nbsp;ms, `--dauer-lang` 400&nbsp;ms), erste Anwendung
   im Spendenformular.** Empfehlung: ja, weil sonst jede nächste Seite ihre
   eigene Bewegung erfindet.
