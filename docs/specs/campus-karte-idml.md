# Campus-Karte: IDML-Export – Spezifikation und Übergabe

Stand: 30. Oktober 2026 · Status: **gebaut, erster Öffnungstest in InDesign offen** · Werkzeug:
https://werkzeuge.goetheanum.ch/apps/karten-generator/

Auftrag des Inhabers (30. 10. 2026): Die Campus-Karte soll neben PDF und SVG
ein **sauberes IDML** ausgeben, damit die Karte in InDesign weiterbearbeitet
werden kann: Texte korrigieren und übersetzen, Marken verschieben, mit
anderen Drucksachen montieren.

## Was «sauber» heisst

Die Karte kommt nicht als ein verknüpftes Bild in InDesign, sondern als
Dokument mit echten Objekten, dort, wo Bearbeitung Nutzen bringt:

1. **Grundkarte als verknüpftes PDF** im Ordner `Links/`. Das Gelände
   (1689 Pfade, 337 davon mit Kurven, Clips für Wiesen und Aquarell) bleibt
   exakt wie im Druck-PDF; es wird mit dem bestehenden jsPDF-Pfad erzeugt.
   Eine Übersetzung der Pfade in native IDML-Polygone bringt Grösse und
   Risiko, keinen Nutzen – darum nicht.
2. **Marken nativ:** Zahlkreise als Ovale in der Kategoriefarbe mit weissem
   Rand (wie `markenKreis`), die Ziffer als Textrahmen (Hausschrift Laut,
   zentriert). Pillen (`<rect rx>`) als Rechteck mit Eckenrundung. Symbol-
   Marken (Piktogramme, Treppen-Badges, Pfeile): Kreis nativ, das Zeichen
   als kleines verknüpftes PDF oder als Polygon aus dem Pfad – je nachdem,
   was der Pfad-Parser (nur M/L/C/Z) hergibt; Bögen (A) in Kurven wandeln
   oder als PDF liefern.
3. **Alle Beschriftung als Textrahmen** mit Absatzformaten: Titel (5.3 mm
   Grad ≈ 15 pt), Untertitel (3.35 mm ≈ 9.5 pt), Gebäude-Schriftzüge
   (weiss, gedreht per `ItemTransform`), Legende mit Gruppenköpfen
   (`TINTE_LEISE`), Einträgen (`TINTE`) und Notizen. Schriften:
   «Goetheanum Schrift» Schnitt Deutlich für Sprache, Laut für Ziffern,
   «Source Sans 3» Semibold für Werte – wie im PDF (`PDF_SCHRIFTEN` in
   `export.js`). InDesign findet die Schriften, wenn sie installiert sind;
   das ZIP legt keine Fonts bei (Lizenz).
4. **Dokument korrekt angelegt:** A4 oder A3 quer nach `state.format`,
   3 mm Beschnitt in `DocumentPreference` (wenn `state.beschnitt`),
   Schnittmarken zeichnet InDesign beim Export selbst – keine Haarlinien
   aus `schnittmarkenMarkup`. Masseinheit Millimeter, Sprache
   «German: Swiss 2006 Reform», Profile wie im Folder-Export.
5. **Vier Ebenen:** Grundkarte, Marken, Beschriftung, Legende (plus Logo
   auf der Ebene Beschriftung). Ebenen in dieser Reihenfolge in
   `designmap.xml`, Objekte je Ebene über `ItemLayer`.
6. **Farbfelder:** je Kategoriefarbe der aktiven Orte ein RGB-Farbfeld mit
   sprechendem Namen (`ortFarbeHex`), dazu Tinte (`TINTE`, `TINTE_LEISE`),
   Paper, Black. Keine Farbe hart in Objekten, nur über Farbfeld.
7. **Auslieferung als ZIP** wie beim Folder: `<dateiname>.idml` plus
   `Links/grundkarte.pdf`, `Links/logo.pdf` (Goetheanum-Marke aus
   `logoMarkup`, über jsPDF als Vektor), ggf. `Links/titellogo.pdf`.
   Dateiname über `dateiname("zip")` aus `export.js` (Titel-Slug, Format).

## Bausteine, die schon da sind

- Zip-Schreiber: `zipSchreiben` in
  https://github.com/phtok/goeloggen/blob/main/apps/lt-programm/idml-export.js
  (ES-Modul, CompressionStream, kein Fremdpaket).
- Vorlagenfreies IDML mit Absatzformaten, Farbfeldern, Musterseite,
  `designmap.xml`, `Links/`-Konvention:
  https://github.com/phtok/goeloggen/blob/main/apps/programmheft/idml.js
  (`pfad`, `flaeche`, `bild`, `rahmen`, `story`, `absatzformat` dort
  kopieren und anpassen; `bild` für PDF-Links um
  `LinkResourceFormat="$ID/Adobe PDF"` ergänzen, die Grösse des PDF kommt
  aus `exportGeometrie()`).
- Knopf-Muster mit Modul-Import zur Laufzeit und Cache-Stand `BAU`:
  https://github.com/phtok/goeloggen/blob/main/apps/programmheft/live.html
  (Suche `$("idml").onclick`).
- Szene und Geometrie: `szeneMarkup`, `exportGeometrie`, `dateiname`,
  `exportPdf` in
  https://github.com/phtok/goeloggen/blob/main/apps/karten-generator/export.js
  und `app.js` (`ortMarkup`, `markenKreis`, `legendeMarkup`,
  `gebaeudeLabelMarkup`, `logoMarkup`, `anp`, `ortFarbeHex`,
  `LEGENDE_NORMAL`/`LEGENDE_KOMPAKT`, `TINTE`, `TINTE_LEISE`).

## Bauplan (Etappen, einzeln committen)

1. **`apps/karten-generator/idml.js`** (ES-Modul, wird per
   `import()` vom Knopf geladen). Export `baueIdml()` liefert ein ZIP als
   `Uint8Array`. Die Szene wird **nicht** aus dem SVG-String zurückgeparst:
   `app.js` bekommt eine Funktion `szeneModell()`, die dieselben Daten wie
   `szeneMarkup` als Objekte liefert (Marken mit x/y/r/Farbe/Text/Symbol,
   Labels mit x/y/Grad/Winkel/Text, Legendenzeilen mit Spalte/y/Typ/Text,
   Titel/Untertitel, Logo-Lage). `szeneMarkup` und `szeneModell` müssen
   dieselben Rechenwege nutzen (Umbau: Markup aus dem Modell erzeugen).
2. **Grundkarte als PDF:** `exportPdf` in `export.js` so aufteilen, dass
   eine Funktion `grundkartePdfBytes()` nur Gelände, Aquarell und Clips
   (ohne Marken, Texte, Legende, Logo, Schnittmarken) ins PDF schreibt,
   Blattgrösse = Trim plus Beschnitt.
3. **IDML schreiben:** Preferences, Musterseite, Graphic (Farbfelder),
   Styles (Absatz- und Zeichenformate), ein Spread, Stories je Textrahmen,
   `designmap.xml` mit vier Ebenen.
4. **Knopf «InDesign»** neben PDF und SVG in `index.html` (Zeile um 431),
   Handler in `export.js` nach dem Muster von `download-pdf` (Knopf
   sperren, Beschriftung «IDML wird gepackt …», `varianteAblegen()` nach
   dem Download, Fehlermeldung per `window.alert`).
5. **Registrieren und dokumentieren:** `tools.json` (Eintrag `karten`,
   `desc` und `such` um IDML/InDesign ergänzen), `design-system/CHANGELOG.md`
   (Beschluss-Ledger: Grundkarte als PDF-Link, Rest nativ), diese Datei
   auf Status «gebaut» setzen.

## Prüfen

- Strukturell: jede XML-Datei des Pakets mit `xmllint --noout` prüfen;
  Aufbau gegen den funktionierenden Folder-Export vergleichen
  (`mimetype` als erster, unkomprimierter Eintrag; `designmap.xml`
  verweist auf alle Teile; alle `Self`-IDs eindeutig).
- Werkzeug: `node tools/barrierefreiheit.mjs --seite apps/karten-generator/index.html`
  nach dem neuen Knopf; `tools/ds-lint.py --staged` und `tools/typo-check.py`
  laufen im Hook.
- **InDesign öffnet der Inhaber selbst** (kein InDesign in der Sandbox):
  Datei öffnet ohne Warnung, Grundkarte verknüpft, Marken verschiebbar,
  Legende als Text mit Formaten, Beschnitt 3 mm sichtbar. Der erste Befund
  kommt als Issue oder in den PR.

## Wie gebaut (30. 10. 2026)

- **Modell:** `szeneModell()` in `app.js` liefert Elemente aus Formen
  (`kreis`, `rechteck`, `pfad` mit Matrix, `text` mit Rolle); `szeneMarkup`
  zeichnet genau diese Formen. Vor- und Nachher-Vergleich der Vorschau in
  sechs Zuständen pixelgleich.
- **Symbol-Marken nativ:** Die Icons v2.7 und die Treppen-Badges sind reine
  Pfade (M/L/H/V/C/Z) – sie gehen als Polygone ins IDML, keine Zeichen-PDFs.
  Jede Marke (Scheibe, Zeichen, Pfeil) ist eine Gruppe.
- **Text:** ein Textrahmen je Text, Grundlinie fest auf dem Modell
  (`FirstBaselineOffset="FixedHeight"`), Rahmen wächst mit dem Text
  (automatische Grösse, keine Umbrüche). Formate: Titel, Untertitel, Gebäude,
  Legende Gruppe, Legende Eintrag, Legende Notiz, Ziffer.
- **Schriften:** Sprache in ‹Goetheanum Variabel› Deutlich, Ziffern in Laut.
  Die Variable v2.8 liegt samt `OFL.txt` im Ordner `Document fonts/` des
  Pakets; InDesign aktiviert Schriften aus diesem Ordner beim Öffnen selbst
  (Wunsch des Inhabers, 30. 10.: ‹die Schriften bitte mitliefern›).
- **Dateiname** (PDF, SVG, IDML, ZIP): `Campuskarte_<Titel>_A4`, Titel wie
  getippt, Umlaute aufgelöst, Wörter mit Bindestrich; ohne Titel
  `Campuskarte_A4`.
- **Ebenen:** in `designmap.xml` von unten nach oben (so stapelt auch die
  InDesign-Vorlage `apps/lt-programm/vorlage/LT27.idml`); die Grundkarte ist
  gesperrt.
- **Geprüft:** `xmllint --noout` über alle Teile, `Self`-IDs eindeutig,
  `mimetype` zuerst und unkomprimiert, alle Farb- und Story-Verweise
  aufgelöst; der Druckbogen nach SVG zurückgebaut und über die Vorschau
  gelegt (Vektor, Aquarell, A3 mit Ausschnitt, Sonderlogo).
- Der Pfadleser kennt nur absolute Befehle; ein anderes Zeichen bricht den
  Export mit Meldung ab, statt still Falsches zu liefern.

## Offen, entscheidet der Inhaber beim ersten Öffnen

- Ob die Symbol-Marken (Piktogramme) nativ gut genug sind oder lieber als
  PDF-Links kommen. (Gebaut: nativ.)
- Ob die Gebäude-Schriftzüge auf der Grundkarte (im PDF) oder als eigene
  Textrahmen (verschiebbar, aber über dem verknüpften PDF) liegen sollen.
  Empfehlung: Textrahmen, weil Übersetzung der Hauptnutzen ist. (Gebaut:
  Textrahmen auf der Ebene Beschriftung.)
