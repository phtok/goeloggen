# Tagungs-Reader – Anleitung

Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-reader/
Konzept: https://github.com/phtok/goeloggen/blob/main/docs/specs/lt-reader-konzept.md

Ein Jahrgang ist eine Datei. Alles, was der Reader braucht, steht in
`jahrgaenge/<jahr>.json` – live im Archiv (Supabase `reader_jahrgang`),
eingecheckt als Ausgangsstand. Vier Werkstätten füllen die Datei, die
Vorschau zeigt alle Seiten, die Exporte lesen sie.

```
Tagungsprogramm (apps/lt-programm/webseite.json) ─▶ Programm      ─┐
Motiv (JPG des Plakats)                           ─▶ Motiv & Farben ─┤
Standardplan (Kartentool)                         ─▶ Karte          ─┼─▶ jahrgaenge/2027.json ─▶ Vorschau (20 Seiten)
Texte DE/EN (vom Vorjahr)                         ─▶ Inhalte        ─┘                            ├─▶ Vorschau-PDF (Drucken)
                                                                                                   └─▶ IDML (Etappe 3)
```

## Der normale Ablauf (Sektion)

1. **Öffnen:** https://werkzeuge.goetheanum.ch/apps/lt-reader/ – lädt den
   aktuellen Jahrgang aus dem Archiv. Oben den eigenen Vornamen eintragen
   (steht bei der Sicherung dabei).
2. **Inhalte** durchgehen: jeder Block (Welcome, Languages, Meals …) hat
   eine Ampel. Gold = noch vom Vorjahr, Grün = geprüft, Blau = geändert.
   Block aufklappen, lesen, anpassen, auf **geprüft** setzen. Die Zeile
   oben zählt, wie viele Blöcke noch offen sind.
3. **Motiv & Farben:** das Bild des Plakats hochladen, **Farben aus dem
   Motiv ableiten**, Vorschlag anklicken oder von Hand setzen. Jede Rolle
   zeigt ihren Kontrast; Rollen werden automatisch so weit abgedunkelt,
   dass Weiss darauf 4,5:1 hält (B01/B02).
4. **Karte:** Legende pflegen (Nummern, Treppen). Die Karte selbst kommt in
   Etappe 2 aus dem Kartentool.
5. **Programm:** zeigt den Stand der Webseite, den das Tagungsprogramm liest
   (https://werkzeuge.goetheanum.ch/apps/lt-programm/). Neu holen dort,
   hier **Stand neu laden**.
6. **Vorschau** rechts: jede Seite in Endformat mit 3 mm Beschnitt
   (gestrichelte Linie = Endformat). Läuft eine Seite über, steht es rot
   unten rechts und in der Zeile oben.
7. **Export → Vorschau-PDF:** öffnet den Druckdialog des Browsers; ‹als PDF
   sichern›, Ränder ‹Keine›, Hintergrundgrafiken ein. A5 mit Beschnitt und
   Schnittmarken, RGB – für Korrekturläufe. Das Druck-PDF für die Druckerei
   entsteht aus dem IDML in InDesign (Etappe 3).

Gesichert wird beim Tippen im Hintergrund. Hat jemand anderes inzwischen
gesichert, meldet es die Seite und sperrt das Überschreiben – **Neu laden**
drücken, dann weiterarbeiten.

## Schreibweise in den Texten

- Leerzeile = neuer Absatz. Eine Zeile, die mit `> ` beginnt, steht
  eingerückt (Adressen wie `tickets.goetheanum.ch/…`).
- `[45]` = Nummer auf der Karte (Marke), `[M]` `[N]` `[S]` = Treppe oder
  Lift (blaue Marke). Auch in Köpfen erlaubt: `Internet [12] [20]`.
- Platzhalter werden beim Setzen ersetzt: `{jahr}`, `{datum_de}`,
  `{datum_en}`, `{motto_de}`, `{motto_en}`, `{webseite}`, `{rabattcode}`,
  `{aufzeichnung_bis_de}`, `{aufzeichnung_bis_en}`; aus dem ersten Tag der
  Tagung (Block ‹Tagung›, Feld ‹Erster Tag›): `{tag1_de}` … `{tag4_de}`,
  `{tag2_en}`, `{tag2_fr}`, `{tag2_es}`, `{tag2_it}`, `{tag2_nl}`,
  `{tag2_zh}`, `{tag3_kurz}`, `{wochentag2_de}`.
- Zweisprachig nach G01: Englisch steht Deutlich, Deutsch Ruhig – gleiche
  Grösse. Keine Fettung im Text von Hand.

## Neues Jahr

**Export → Neues Jahr anlegen.** Kopiert den Jahrgang: Texte bleiben und
stehen auf ‹vom Vorjahr›, Jahreszahlen in den Stammdaten werden
hochgezählt, Motiv, Logos und Farben beginnen neu. Danach im Block ‹Tagung›
Motto, Datum und ersten Tag setzen – die Platzhalter ziehen nach.

Der eingecheckte Ausgangsstand (`jahrgaenge/2027.json`) wurde einmalig aus
dem IDML-Arbeitsstand 2027 erzeugt (Texte 2026, Jahreszahlen als
Platzhalter). Einen Jahrgang einchecken: **Export → Herunterladen (JSON)**
und die Datei nach `apps/lt-reader/jahrgaenge/` legen.

## Was wo liegt

| Datei | Aufgabe |
| --- | --- |
| `index.html` | Werkstatt und Seiten (Gestalt) |
| `reader.js` | Modell, Satz der Seiten, Werkstätten, Sicherung |
| `jahrgaenge/<jahr>.json` | der Jahrgang (eingecheckter Stand) |
| `jahrgaenge/<jahr>-motiv.jpg` | Vorschau-Motiv (der Druck nimmt das Original in InDesign) |
| `../lt-programm/webseite.json` | Stand der Tagungswebseite (liest das Tagungsprogramm) |
| `../programmheft/lageplan-standard.svg` | Standardplan, in der Tagungsfarbe eingefärbt (bis Etappe 2) |
| `services/lt-reader/schema.sql` | Archiv: `reader_jahrgang`, `reader_fassung`, RPCs |

## Etappen

1. Gerüst, Inhalte, Vorschau, Sicherung, Vorschau-PDF – **dieser Stand**
2. Motiv & Farben vollständig (Rollen der Programm-Doppelseite), Karte aus
   dem Kartentool mit Marken aus den Räumen des Programms
3. Programm-Seiten direkt von der Webseite, Zeitplan-Doppelseite, IDML-Export
4. Druckstrasse PDF/X-4 (später, nach Erfahrung mit dem InDesign-Weg)
