# Tagungs-Reader: IDML-Export – Spezifikation und Übergabe

Stand: 31. Oktober 2026 · Status: **gebaut, Öffnungstest in InDesign offen** ·
Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-reader/

Auftrag des Inhabers (31. 10. 2026): Der Tagungs-Reader soll ein IDML für
InDesign ausgeben. Auf der ersten Doppelseite (Seiten 2–3) sitzt die
Campus-Karte als **bearbeitbare InDesign-Objekte**, nicht als Bild.

Grundlagen (verweisen, nicht nacherzählen):

- Reader: https://github.com/phtok/goeloggen/blob/main/apps/lt-reader/ANLEITUNG.md,
  `reader.js` (Jahrgang, Ersetzungen, Schreiben im Blatt), `idml-seite.js`
  (Absatzmodell `storyAbsaetze`).
- Karten-IDML: https://github.com/phtok/goeloggen/blob/main/docs/specs/campus-karte-idml.md
  (Abschnitt «Wie gebaut»), `apps/karten-generator/idml.js`, `export.js`
  (`exportIdml`, `grundkartePdfBytes`, `idmlTextBreite`), `app.js`
  (`szeneModell`, `window.Kartentool`).
- Zip lesen und schreiben: `apps/lt-programm/idml-export.js`
  (`zipLesen`, `zipSchreiben`; Muster für das Befüllen einer Vorlage:
  `exportIdml` dort).

## Ausgangslage, gemessen an der Vorlage

`apps/lt-reader/vorlage/LT27-Reader.idml` (DOMVersion 21.5): 20 Seiten A5
hoch (419.528 × 595.276 pt = 148 × 210 mm), Doppelseiten, Beschnitt
8.504 pt = 3 mm, eine Ebene «Ebene 1», 249 Stories.

- Seiten 2–3 liegen auf `Spreads/Spread_u1d5.xml`: Seite 2 bei x −419.528,
  Seite 3 bei x 0, beide bei y −297.638 – der Druckbogen ist um den
  Nullpunkt zentriert. Darauf steht noch die **alte Karte** von 2025:
  47 Gruppen, 10 Polygone, 3 Textrahmen (48 Rahmen insgesamt, alle Stories
  nur hier, nicht verkettet), ein Link auf `Gelaende_ph1_weltkonferenz.ai`.
- Die Doppelseite misst **296 × 210 mm**, das Kartentool-Blatt
  **297 × 210 mm** (Falz bei 148.5). Die Karte wird **1 : 1** und
  **auf den Falz zentriert** gesetzt: Falz auf Falz, je 0.5 mm laufen
  aussen in den Beschnitt. Die Grundkarte bringt 3 mm Beschnitt mit und
  deckt so den Beschnitt der Vorlage (3.5 mm über den Seitenrand). Keine
  Verzerrung, keine Skalierung.
- Die Musterseite trägt keine Objekte; nichts liegt unter der Karte.

## Was «sauber» heisst

1. **Die Vorlage bleibt das Dokument.** Ausgeliefert wird die Vorlage
   selbst, mit allen Formaten, Farbfeldern, Musterseiten, Links und
   Seiten; geändert werden nur Stories, Farbwerte und der Druckbogen 2–3.
   Kein Neuaufbau, keine Normalisierung fremder Teile.
2. **Texte wie im Blatt.**
   - Rahmen ohne Überschreibung: die **Ersetzungen** des Jahrgangs werden
     je `<Content>` angewendet – genau so wie in der Vorschau, die sie je
     Lauf anwendet (`storyText` in `reader.js`), auf denselben Seiten
     (Ersetzung ohne `seiten` → Textseiten 4–9, 12–19). Alles andere am
     Story-XML bleibt Byte für Byte.
   - Rahmen mit Überschreibung (`S.texte[story]`): der Text des
     Absatzmodells wird **zeichengenau mit dem Text der Vorlage verglichen**
     (Myers-Diff); nur die Änderungen wandern in die `<Content>`-Knoten,
     ein neuer Absatz wird `<Br />` im selben Lauf. Alles, was das Modell
     nicht trägt, bleibt: verankerte Objekte (der Rahmen der
     Arbeitsgruppen trägt 30 Gruppen und 26 Rahmen im Text), Hyperlinks,
     Spalten- und Rahmenumbrüche, Kerning, Sonderzeichen. Gelesen wird wie
     in der Vorschau: `<Content>` und `<Br/>` direkt im Lauf.
     (Erster Entwurf: Story aus dem Modell neu bauen, Tags aus der Vorlage
     klonen – verworfen, weil verankerte Objekte verloren gingen.)
3. **Farben wie im Blatt.** Jahrgangsfarben (`S.farben.swatches`,
   Farbfeld → Hex) ändern den Wert des **Farbfelds selbst** (Raum RGB,
   Name bleibt), damit jedes Objekt, das es nutzt, folgt. Eine Tönung
   (`Tint/…`) bekommt ein eigenes RGB-Farbfeld «<Name> Jahrgang», auf das
   die Objekte der Seiten 10–11 umgehängt werden.
4. **Karte nativ auf Seiten 2–3.** Die alte Karte wird vom Druckbogen
   entfernt (Objekte, ihre 48 Stories, Einträge in `designmap.xml`). An
   ihre Stelle kommen die Objekte des Kartentools, gebaut von **derselben**
   Objekt-Erzeugung wie das eigenständige Karten-IDML:
   - Grundkarte als verknüpftes PDF (`Links/grundkarte.pdf`, Endformat plus
     3 mm), Ebene gesperrt;
   - Marken als Gruppen aus Ovalen, Rundrechtecken, Polygonen; Ziffern,
     Schriftzüge, Legende als Textrahmen mit Absatzformaten;
   - Logo als verknüpftes PDF (`Links/logo.pdf`), wenn das Kartentool eines
     zeigt.
   Damit nichts mit der Vorlage zusammenstösst: alle neuen `Self`-IDs mit
   eigenem Präfix (`k…`), Absatzformate als «Karte Titel», «Karte Legende
   Eintrag» …, Farbfelder als «Karte Tinte», «Karte Marke Rot» …, vier
   Ebenen «Karte Grundkarte», «Karte Marken», «Karte Beschriftung»,
   «Karte Legende» über «Ebene 1».
5. **Schrift reist mit.** `Document fonts/` im ZIP: Goetheanum Variabel
   v2.8 samt `OFL.txt` (wie beim Karten-IDML). Titillium (Lauftext der
   Vorlage) liegt nicht bei; es ist beim Satz installiert.
6. **Bilder:** Die Links der Vorlage bleiben, wie sie sind; der Druck
   nimmt die Originaldateien (wie bisher in der Anleitung). Die Vorschau-
   Bilder des Jahrgangs (Motiv, Logos) gehen nicht ins IDML.
7. **Auslieferung als ZIP:** `Reader_<Jahr>_A5.idml`, `Links/grundkarte.pdf`,
   ggf. `Links/logo.pdf`, `Document fonts/…`. ZIP-Name
   `Reader_<Jahr>_A5.zip` (sinngemäss zu `Campuskarte_<Titel>_A4`).

## Bauplan (Etappen, einzeln committen)

1. **Diese Spezifikation** – eigener PR.
2. **Kartentool-Schnittstelle und geteilte Objekt-Erzeugung.**
   - `idml.js`: die Erzeugung der Objekte (Formen → Oval/Polygon/
     TextFrame/Gruppe, PDF-Rahmen, Farbfelder, Absatzformate, Ebenen) als
     eigene Funktion `kartenObjekte(e)` exportieren – mit Präfix für IDs,
     Formate, Farben und Ebenen und mit wählbarem Nullpunkt. `baueIdml`
     nutzt sie selbst; das eigenständige Karten-IDML bleibt gleich
     (Gegenprobe: Paket vor und nach dem Umbau inhaltsgleich).
   - `export.js`: `idmlTeile()` liefert alles, was `baueIdml` braucht
     (Modell, Geometrie, Links, Farbnamen, Textbreite); `exportIdml`
     nutzt sie.
   - `window.Kartentool`: `modell()` (= `szeneModell`) und
     `idmlTeile()` (async) dazu.
3. **Reader-IDML** in `apps/lt-reader/idml-export.js` (ES-Modul, per
   `import()` beim Klick geladen): Vorlage lesen, Stories nach Punkt 2,
   Farben nach Punkt 3, Druckbogen 2–3 nach Punkt 4, Schrift und Links
   nach 5 und 7. Knopf «IDML für InDesign» im Reiter ‹Export› wird
   aktiv; während des Packens gesperrt, Fehler als Meldung im Werkzeug.
4. **Dokumentieren:** `ANLEITUNG.md` (Export, Etappen), diese Datei auf
   «gebaut», `tools.json` (Beschreibung des Readers).

## Prüfplan

- **Strukturell, in der Sandbox** (Node, ohne Browser für den Paketbau,
  Playwright für den Knopf):
  - jede XML-Datei des Pakets mit `xmllint --noout`;
  - `Self`-IDs im ganzen Paket eindeutig; jede `ParentStory`, jedes
    Farbfeld, jedes Absatzformat und jede Ebene, auf die verwiesen wird,
    existiert; keine Story ohne Rahmen, kein Rahmen ohne Story;
  - `mimetype` erster Eintrag, unkomprimiert;
  - Druckbogen 2–3 nach SVG zurückgebaut und über die Vorschau des
    Readers gelegt (Marken, Legende, Falz deckungsgleich);
  - Texte: für jeden Rahmen ohne Überschreibung entspricht der Text der
    Story im IDML dem Text der Vorschau (`storyText`); für überschriebene
    Rahmen ebenso; unveränderte Stories sind Byte-gleich mit der Vorlage.
- **Gegenprobe Karten-IDML:** Paket aus dem Kartentool vor und nach dem
  Umbau inhaltsgleich (gleiche Dateien, gleiche XML).
- **Werkzeug:** `node tools/barrierefreiheit.mjs --seite apps/lt-reader/index.html`;
  `typo-check` und `ds-lint` im Hook.
- **InDesign öffnet der Inhaber selbst** (kein InDesign in der Sandbox):
  Datei öffnet ohne Warnung über fehlende Teile (fehlende Bild-Links der
  Vorlage ausgenommen), Seiten 2–3 zeigen die Karte, Marken verschiebbar,
  Legende als Text mit Formaten «Karte …», Grundkarte verknüpft, Schrift
  aktiv. Der Befund kommt als Issue oder in den PR.

## Wie gebaut (31. 10. 2026)

- **Kartentool:** `kartenObjekte()` in
  https://github.com/phtok/goeloggen/blob/main/apps/karten-generator/idml.js
  baut die Karte als Objekte ohne Dokument (Optionen `praefix`, `namen`,
  `sprache`); `baueIdml` nutzt sie selbst. `idmlTeile()` in `export.js`
  liefert Modell, Geometrie, PDF-Links, Farbnamen und Textbreite;
  `window.Kartentool` gibt `modell()` und `idmlTeile()` heraus.
  Gegenprobe: Karten-IDML vor und nach dem Umbau Byte für Byte gleich.
- **Reader:** https://github.com/phtok/goeloggen/blob/main/apps/lt-reader/idml-export.js
  (`readerIdml`, `storyNeu`, `storyErsetzen`), Knopf im Reiter ‹Export›
  (`idmlExport` in `reader.js`). Die Seite je Rahmen für die Ersetzungen
  kommt aus `seitenStories`, wie in der Vorschau.
- **Karte im Dokument:** IDs `k…`, Formate «Karte Titel» … «Karte Ziffer»,
  Farbfelder «Karte Tinte», «Karte Marke Rot» …, Ebenen «Karte Grundkarte»
  (gesperrt), «Karte Marken», «Karte Beschriftung», «Karte Legende» über
  «Ebene 1». Sprache der Formate nach der Legende (English: UK oder
  German: Swiss, beide in der Vorlage vorhanden).
- **Geprüft (Jahrgang 2027 aus dem Archiv):** `xmllint` über alle Teile,
  Self-IDs eindeutig, alle Verweise (Farbe, Format, Ebene, Story)
  aufgelöst – die einzigen Auffälligkeiten (`u97` in der StoryList,
  134 Stories verankerter Rahmen) stehen identisch in der Vorlage; alle
  67 Rahmen der Vorschau wortgleich im IDML; Seiten 2–3 aus dem IDML
  zurückgezeichnet und neben die Vorschau gelegt (deckungsgleich);
  Bearbeitung im Blatt auf Seite 4 und 12: genau die zwei Stellen
  geändert, verankerte Objekte vollständig; Farbfeld und Tönung des
  Jahrgangs gesetzt; `barrierefreiheit.mjs` ohne Verstoss.

## Offen, entscheidet der Inhaber beim ersten Öffnen

- Ob die Karte statt zentriert (je 0.5 mm in den Beschnitt) auf 296 mm
  verkleinert werden soll (99.66 %). Empfehlung: zentriert, 1 : 1 –
  die Grade der Legende bleiben die des Kartentools.
- Ob die Bilder des Jahrgangs (neues Motiv) ins Paket unter `Links/`
  sollen. Heute: nein, die Vorschau-Bilder sind verkleinert.
