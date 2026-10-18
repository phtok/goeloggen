# Tagungs-Reader – Anleitung

Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-reader/
Konzept: https://github.com/phtok/goeloggen/blob/main/docs/specs/lt-reader-konzept.md

**Die InDesign-Vorlage ist das Blatt.** Das Werkzeug zeichnet jede Seite aus
`vorlage/LT27-Reader.idml` (Flächen, Tönungen, Dämpfer, Bilder, Logos, QR,
Textrahmen mit Graden und Einzügen) und tauscht nur Texte und Bilder. Die
Karte (Seiten 2–3) zeichnet das Kartentool, unsichtbar eingebettet, in den
Farben der Faltblatt-Palette. Ein Jahrgang (`jahrgaenge/<jahr>.json`, live
im Archiv) trägt nur, was von der Vorlage abweicht.

```
vorlage/LT27-Reader.idml ─▶ idml-seite.js ─┐
Kartentool (apps/karten-generator, ?einbett) ┼─▶ 20 Seiten im Blatt ─▶ Vorschau-PDF (Drucken)
jahrgaenge/2027.json (Texte, Ersetzungen,   │                        └▶ IDML (Etappe 3)
  Bilder, Farben, Karte, Verlauf) ──────────┘
```

## Der normale Ablauf (Sektion)

1. **Öffnen:** https://werkzeuge.goetheanum.ch/apps/lt-reader/ – lädt den
   Jahrgang aus dem Archiv. Oben den Vornamen eintragen (steht bei Sicherung
   und Verlauf).
2. **Im Blatt schreiben:** Text anklicken, tippen, fertig. Jede Änderung wird
   gesichert und im Verlauf festgehalten (vorher/nachher, wer, wann). Rot
   umrandet = Übersatz: mehr Text, als der Rahmen fasst.
3. **Reiter ‹Stand›:** geänderte Rahmen auf ‹geprüft› setzen oder auf die
   Vorlage zurückstellen.
4. **Reiter ‹Ersetzungen›:** Jahreszahlen, Daten, Codes des Vorjahres werden
   beim Setzen auf allen Textseiten ersetzt, in dieser Reihenfolge. So wird
   aus dem Vorjahrsstand der neue Jahrgang, ohne jeden Rahmen anzufassen.
   Leerraum im Suchtext passt auch auf Zeilenumbrüche der Vorlage.
5. **Reiter ‹Motiv & Farben›:** Motiv ersetzen (Vorschau; der Druck nimmt die
   Originaldatei in InDesign). Palette des Faltblatts (neun Felder aus der
   Farbleiste in `apps/lt-programm/vorlage/LT27.idml`). Farben des Zeitplans
   je Swatch der Vorlage zuweisen; Farben der Karte je Rolle des Kartentools.
6. **Reiter ‹Karte›:** Orte an- und abwählen, Sprache und kompakte Legende.
   Feinarbeit (Marken verschieben, Beschriftungen) im Kartentool selbst,
   dann ‹Export → Kartenstand aus dem Kartentool laden›. Nummern sind fest
   (Modus `festeNummern`), damit ‹Speisehaus 45› im Text stimmt.
7. **Export → Vorschau-PDF:** Druckdialog des Browsers, ‹als PDF sichern›,
   Ränder ‹Keine›, Hintergrundgrafiken ein. A5 mit 3 mm Beschnitt, RGB. Das
   Druck-PDF entsteht aus dem IDML in InDesign (Etappe 3).

Hat jemand anderes inzwischen gesichert, meldet es die Seite und sperrt das
Überschreiben – **Neu laden**, dann weiterarbeiten.

## Was die Vorschau kann und was nicht

- Zeichnet die Vorlage eins zu eins in Vektoren; Lauftext in Titillium
  (Schrift der Vorlage, per Google Fonts) mit angeglichener Laufweite,
  Hausschrift aus dem Design-System. Zeilenfall kann um eine Zeile von
  InDesign abweichen; verbindlich ist das IDML.
- Verkettete Rahmen (Arbeitsgruppen 12–15) fliessen über Spalten und Seiten.
- Verlaufs-Feder der Dämpfer ist angenähert, gespiegelte Bilder und
  Beschnitt der Rahmen sind exakt.
- Ändert sich die Vorlage in InDesign: IDML exportieren, als
  `vorlage/LT27-Reader.idml` ablegen. Story-IDs der Rahmen bleiben, solange
  die Rahmen bleiben; Überschreibungen im Jahrgang hängen daran.

## Neues Jahr

**Export → Neues Jahr anlegen** kopiert den Jahrgang: Texte und Vorlage
bleiben, die Ersetzung der Jahreszahl zählt hoch, der Verlauf beginnt neu.
Dann Ersetzungen für die neuen Daten eintragen (oder direkt im Blatt
schreiben), Motiv ersetzen, Farben zuweisen, Vorlage bei Bedarf tauschen.

## Was wo liegt

| Datei | Aufgabe |
| --- | --- |
| `index.html` | Werkstatt, Blatt, Druck-CSS |
| `reader.js` | Jahrgang, Seitenplan, Schreiben im Blatt, Verlauf, Karte, Archiv |
| `idml-seite.js` | zeichnet eine IDML-Seite als SVG (Formen, Bilder, Textrahmen) |
| `vorlage/LT27-Reader.idml` | die InDesign-Vorlage (20 Seiten) |
| `jahrgaenge/<jahr>.json` | der Jahrgang: Texte je Rahmen, Ersetzungen, Bilder, Farben, Karte, Verlauf |
| `jahrgaenge/2027-motiv.jpg`, `2027-logos/` | Vorschau-Bilder (Motiv aus dem Plakat-PDF, Logos aus dem Reader-PDF) |
| `../karten-generator/app.js` | Kartentool; `window.Kartentool` ist die Schnittstelle, `?einbett` lässt den eigenen Stand in Ruhe |
| `services/lt-reader/schema.sql` | Archiv: `reader_jahrgang`, `reader_fassung`, RPCs |

## Etappen

1. Gerüst, Archiv, Vorschau – gebaut
2. Vorlage als Blatt, Schreiben im Blatt, Verlauf, Karte aus dem Kartentool,
   Palette – **dieser Stand**
3. Programm von der Webseite (Zeitplan, Arbeitsgruppen mit Überschreibungen
   je Nummer, Abgleich mit Protokoll), IDML-Export
4. Druckstrasse PDF/X-4 (später)
5. Plakat und Folder aus derselben Datei
