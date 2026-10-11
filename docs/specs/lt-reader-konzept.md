# Tagungs-Reader – Konzept (Landwirtschaftliche Tagung, ab 2027)

Stand: 11. Oktober 2026 · Status: **beschlossen; Etappe 1 gebaut** (Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-reader/, Anleitung: `apps/lt-reader/ANLEITUNG.md`)
Beschluss des Auftraggebers (11. 10. 2026): Druckweg 2027 über IDML → InDesign → PDF/X;
die Druckstrasse (Etappe 4) folgt, wenn mehr Erfahrung da ist.
Auftrag: Der Reader der Landwirtschaftlichen Tagung soll online zusammengebaut
werden – von den Mitarbeitenden der Sektion, jedes Jahr neu, mit sauberer
Vorschau, integrierter Campus-Karte in der Tagungsfarbe, Programmdaten von der
Tagungswebseite, Ausgabe als IDML und als Druck-PDF (PDF/X, Farbprofil,
Beschnitt).

Grundlagen, die gelesen wurden: Reader 2026 (PDF, 20 Seiten), Arbeitsstand
2027 (IDML, 20 Seiten, Texte noch von 2026), Plakat A1 2027 (PDF/X-4, Motiv
von Esther Gerster), und im Repo das Tagungsprogramm
(https://werkzeuge.goetheanum.ch/apps/lt-programm/), das Kartentool
(https://werkzeuge.goetheanum.ch/apps/karten-generator/) und der Folder
(https://werkzeuge.goetheanum.ch/apps/programmheft/live.html).

## Die Idee in einem Satz

**Ein Jahrgang ist eine Datei.** Alles, was der Reader 2027 braucht, steht in
`jahrgaenge/2027.json`: Motiv, Farben, Karte, Texte, Programm-Stand. Vier
Werkstätten füllen diese Datei, eine Vorschau zeigt alle 20 Seiten, zwei
Exporte lesen sie. Im Januar 2028 wird die Datei kopiert, und der Reader 2028
beginnt nicht bei null.

```
Webseite (agriculture-conference.org) ─▶ Programm-Werkstatt ─┐
Motiv (JPG)                            ─▶ Motiv & Farben     ─┤
Kartentool (gelaende.svg, orte.js)     ─▶ Karten-Werkstatt   ─┼─▶ jahrgaenge/2027.json ─▶ Vorschau (20 Seiten)
Texte DE/EN (vom Vorjahr vorbefüllt)   ─▶ Inhalte-Werkstatt  ─┘                           ├─▶ IDML + Links/
                                                                                           └─▶ PDF (Vorschau · Druck PDF/X-4)
```

Werkzeug: `apps/lt-reader/` (aus `design-system/starter.html`, Eintrag in
`tools.json`, Tag «Landwirtschaft», neben dem Tagungsprogramm).

## Was schon da ist und wiederverwendet wird

| Baustein | Woher | Was er dem Reader gibt |
| --- | --- | --- |
| Webseiten-Leser | `apps/lt-programm/webseite-lesen.js`, Edge Function `lt-programm-quelle` | Plenum, Arbeitsgruppen mit Nummer, Sprachen, Mitwirkenden, Raum; Motto und Datum |
| Blattmodell | `apps/lt-programm/programm.js` | Offene Punkte (Platzhalter, N.N., fehlende Zweitsprache), Abgleich Hand/Webseite |
| Programm-Doppelseite | `apps/lt-programm/idml-export.js` + `vorlage/LT27.idml` | Seiten 10–11 des Readers sind die Rückseite des Faltblatts – derselbe Export |
| Campus-Karte | `apps/karten-generator/` (Vektor-Gelände, Orte, Marker, Icons für Treppen/Lifte) | Seiten 2–3: Karte und Legende |
| Karte einfärben | `apps/programmheft/live.html › karteFaerben` | Die vier Blaustufen werden zu Stufen der Tagungsfarbe (100 / 68 / 45 / 7 %) |
| IDML ohne Vorlage | `apps/programmheft/idml.js` | A5-Seiten, Absatzformate, Bilder im Ordner `Links/` |
| PDF im Browser | `apps/karten-generator/export.js`, `apps/programmheft/pdf.js` (jsPDF + svg2pdf) | Beschnitt 3 mm, Schnittmarken, TrimBox/BleedBox |
| Speichern ohne Login | `services/folder/schema.sql` (`folder_archiv`, RPC `folder_sichern`) | Gleiches Muster: `reader_archiv`, ein Datensatz je Jahrgang |

Neu zu bauen sind die vier Werkstätten, die 20-Seiten-Vorschau, der
zusammengesetzte IDML-Export und die Druckstrasse.

## Der Seitenplan (20 Seiten, 5 Bogen A5, Rückenheftung)

Aus Reader 2026 und IDML 2027; jede Seite hat eine Quelle und eine Werkstatt.

| Seiten | Inhalt | Quelle | Werkstatt |
| --- | --- | --- | --- |
| 1 | Titel: Motiv, Motto EN/DE, Tagungsname, Datum, QR | Webseite (Motto, Datum) + Motiv | Motiv & Farben |
| 2–3 | Legende + Campus-Karte | Kartentool, Räume aus dem Programm | Karte |
| 4 | Support (Sponsorenlogos) | Logos hochladen, Reihenfolge ziehen | Inhalte |
| 5 | Welcome · Languages | Text DE/EN | Inhalte |
| 6 | Introductions (EN, FR, ES, IT, 中文, NL) mit Raum und Zeit | Text je Sprache | Inhalte |
| 7 | Meals · Opening hours | Text + Zeilen «Ort · Zeit» | Inhalte |
| 8 | Financial Support · Certificate · Feedback | Text DE/EN | Inhalte |
| 9 | Publications | Liste | Inhalte |
| 10–11 | Programm-Doppelseite (Zeitplan) | Webseite + `blatt.json` | Programm (bestehend) |
| 12–13 | Morning Workshops | Webseite | Programm |
| 14–15 | Afternoon Workshops | Webseite | Programm |
| 16 | Guided tours · Open Spaces | Webseite, Rest von Hand | Programm + Inhalte |
| 17 | Festive Evening · Recordings | Text DE/EN | Inhalte |
| 18–19 | Notes · leer | – | – |
| 20 | Rückseite: Motiv, Adresse der Sektion, QR | Stammdaten | Motiv & Farben |

Der Seitenplan steht als Daten (`seitenplan` in der Jahrgangsdatei), nicht im
Code: fällt 2028 eine Seite weg oder kommt eine dazu, ändert sich die Liste,
nicht das Werkzeug. Workshops fliessen über so viele Seiten, wie sie brauchen;
die Vorschau meldet, wenn die Bogenzahl nicht mehr durch vier teilbar ist.

## Die vier Werkstätten (Reiter im Werkzeug)

### 1 · Motiv & Farben

- Motiv hochladen (JPG, das Bild des Plakats). Das Werkzeug liest die Palette
  aus dem Bild (Canvas, Quantisierung auf acht Farben) und schlägt vor:
  **Tagungsfarbe** (dominanter, gesättigter Ton), **Zweitton**, **Akzent**.
  Beim Plakat 2027 sind das die Grüntöne des Motivs; der Vorschlag ist
  anklickbar, jede Farbe von Hand übersteuerbar.
- Daraus die abgeleiteten Rollen, alle gerechnet (B01/B02): Köpfe und Vollton
  (Weiss darauf ≥ 4,5:1, sonst wird der Ton automatisch abgedunkelt), die vier
  Kartenstufen, die Flächen der Programm-Doppelseite (Vortrag, Workshops
  Vormittag/Nachmittag, Pause, Festabend, Eurythmie) als Tönungen, die
  Markerfarbe der Karte. Jede Rolle zeigt ihren Kontrastwert.
- Ergebnis: benannte Farbfelder (`Tagung 2027 Vollton`, `… Stufe 68` …), die
  Vorschau und IDML gleichermassen verwenden. Der Bildnachweis («Artwork:
  Esther Gerster») wird hier einmal gepflegt und steht auf Titel und Rückseite.

### 2 · Karte

- Die Kartentool-Engine, eingebettet: Gelände als Vektor, Orte aus `orte.js`,
  Marker mit Nummer, Icons für Treppen und Lifte mit Stockwerk (wie 2026:
  Main/North/South Stairs mit Etagenliste).
- **Orte kommen aus dem Programm:** jeder Raum, der in einer Arbeitsgruppe,
  Führung oder Einführung vorkommt, wird automatisch markiert und nummeriert;
  die Legende entsteht daraus. Unbekannte Raumnamen werden gemeldet und per
  Spitzname zugeordnet (Liste wie in `live.html › SPITZNAMEN`).
- Farbe: die Kartenstufen aus Werkstatt 1. Marker in der Markerfarbe. Die blaue
  Illustrator-Karte des IDML 2027 entfällt; der Kartenausschnitt (Hochformat,
  Seite 3 randabfallend, Legende links auf Seite 2) ist eine gespeicherte
  Ansicht des Kartentools.
- Die Nummern der Karte sind dieselben Nummern, die auf den Workshop-Seiten
  hinter dem Raum stehen (rote Pille «31»). Eine Quelle, kein Abtippen.

### 3 · Inhalte

- Ein Formular je Seite des Seitenplans: Kopf EN/DE, Text EN/DE, bei den
  Einführungen sechs Sprachen. Felder sind schlicht (Textzeilen, Absätze,
  Listen «Ort · Zeit»), keine Formatierung von Hand – die Formate kommen aus
  dem Seitenplan (Header EN/DE, Text EN/DE wie im IDML 2027).
- **Vorbefüllt vom Vorjahr**, mit Platzhaltern: `{jahr}`, `{datum}`,
  `{datum_kurz}`, `{rabattcode}`, `{aufzeichnung_bis}` werden beim Anlegen
  eines Jahrgangs ersetzt. Im IDML 2027 stehen heute noch «2026»,
  «LWT2026TN» und «bis März 2026» – genau diese Stellen.
- Jedes Feld trägt eine Ampel: **vom Vorjahr** (noch nicht angeschaut) ·
  **geprüft** (bestätigt) · **geändert**. Die Übersicht zeigt, wie viele Felder
  noch ungeprüft sind. So weiss die Sektion, was fehlt, ohne zu suchen.
- Sponsorenlogos: hochladen, Reihenfolge ziehen, Raster 3 × n wie 2026.
- Typografie-Prüfung beim Tippen (Anführungszeichen ‹…›, Gedankenstrich,
  geschütztes Leerzeichen vor «Uhr»), dieselben Regeln wie `typo-check`.

### 4 · Programm

- Der Knopf «Von der Webseite holen» wie im Tagungsprogramm, derselbe Leser.
  Dazu die Seiten, die das Faltblatt nicht hat: Workshops Vormittag und
  Nachmittag mit Nummer, Sprachen, Titel in beiden Sprachen, Mitwirkenden,
  Raum + Kartennummer; Führungen; Open Spaces.
- Offene Punkte wie heute (Platzhalter, N.N., fehlende Übersetzung), plus:
  Raum ohne Ort auf der Karte, Workshop ohne Raum.
- Umbrüche von Hand bleiben über `blatt.json` erhalten (bestehender Weg
  `holen.mjs --umbrueche`).

### Vorschau

- Alle 20 Seiten als Doppelseiten, in HTML aus der Jahrgangsdatei gesetzt:
  Hausschrift, Formate, Farben der Werkstatt 1, Karte als SVG. Das ist
  dieselbe Darstellung, die später das Druck-PDF rendert – was man sieht,
  wird gedruckt.
- Je Seite ein Füllstand: passt der Text in die Seite, läuft er über
  (Messung in Chromium, wie `tools/lt-programm-passt.mjs`).
- Zwei Breiten anschauen ist Pflicht der Gestaltungsarbeit, nicht der
  Vorschau: die Vorschau zeigt das Blatt in Blattgrösse, die Werkstätten
  bleiben auf 390 px bedienbar.

## Speichern, Teilen, Jahrgänge

- Ein Datensatz je Jahrgang in Supabase (`reader_jahrgang`, Muster
  `folder_archiv`): Autosave beim Tippen, kein Login, versteckter Link im
  Backstage. Jede Sicherung legt eine Fassung ab; «zuletzt gesichert um …
  von …» (Name aus einem freiwilligen Feld) steht oben. Mehrere Personen
  arbeiten nacheinander, nicht gleichzeitig – das genügt der Sektion und
  spart ein Konfliktsystem.
- **Stand einfrieren:** ein Knopf schreibt die Jahrgangsdatei ins Repo
  (`apps/lt-reader/jahrgaenge/2027.json`, Edge Function nach dem Muster
  `sortierer-commit`). Git ist das Gedächtnis; der Reader 2027 bleibt
  reproduzierbar, auch wenn die Datenbank weg wäre.
- **Neues Jahr anlegen:** kopiert den letzten Jahrgang, leert Motiv, Farben,
  Programm-Stand, Logos und Karte, behält alle Texte mit Ampel «vom Vorjahr»
  und ersetzt die Platzhalter. Dafür gibt es eine `ANLEITUNG.md` wie beim
  Tagungsprogramm – niemand muss sich den Ablauf merken.

## Ausgabe

### IDML (für InDesign)

- Aus der Jahrgangsdatei erzeugt, ohne Vorlage (Muster `programmheft/idml.js`):
  20 Seiten A5, Beschnitt 3 mm, Absatz- und Zeichenformate mit den Namen des
  IDML 2027 (Header EN/DE, Text EN/DE, AG_Sprache, AG_Titel, AG_Namen,
  AG Orte …), Farbfelder aus Werkstatt 1, Ordner `Links/` mit Motiv, Logos
  und Karte (SVG, bleibt Vektor).
- Die Programm-Doppelseite 10–11 kommt aus dem bestehenden Export des
  Tagungsprogramms (vorlagenbasiert, mit den von Hand gesetzten Rahmen) und
  wird als Seiten 10–11 eingesetzt – so bleibt die Feinarbeit des Faltblatts
  erhalten.
- In InDesign bleibt, was das Werkzeug nicht kann: Unterschneidung, letzte
  Umbrüche, Bildretusche. Das ist der bewährte Weg zur Druckerei (PDF/X aus
  InDesign mit dem Hausprofil).

### PDF

- **Vorschau-PDF** im Browser, sofort: RGB, Beschnitt, Schnittmarken,
  TrimBox/BleedBox – wie Kartentool und Folder heute. Für Korrekturläufe,
  die Webseite und die Sektion.
- **Druck-PDF PDF/X-4** über eine Druckstrasse, nicht im Browser: ein
  Browser kann kein Farbprofil einbetten und keine Konformität prüfen.
  Die Strasse läuft in GitHub Actions (wie `lt-programm-stand.yml`):
  Chromium druckt die Vorschau Seite für Seite (A5 + 3 mm), Ghostscript
  macht daraus PDF/X-4 mit Output Intent **PSO Coated v3 (FOGRA51)**,
  Text- und Vektorschwarz als reines K, Schriften eingebettet, TrimBox und
  BleedBox gesetzt, XMP-Kennung PDF/X-4. Der Knopf im Werkzeug löst den Lauf
  aus (Edge Function `reader-druck` → `workflow_dispatch`), das Werkzeug
  zeigt den Fortschritt und holt die Datei (Release-Asset).
- Prüfung: Basiskontrolle automatisch (PDF-Kennung, Output Intent, Boxen,
  Schriften eingebettet), einmalig je Jahrgang der Acrobat-Preflight durch
  den Auftraggeber. Erst wenn der grün ist, gilt die Strasse als Druckweg.

## Etappen (je ein PR, je einzeln brauchbar)

1. **Gerüst und Inhalte – gebaut (11. 10. 2026).** `apps/lt-reader/` aus dem
   Starter, Jahrgangsdatei 2027 aus den Texten des IDML 2027 erzeugt
   (Platzhalter gesetzt), Inhalte-Werkstatt mit Ampeln, Vorschau aller
   20 Seiten (Textseiten atmen bis 14 % kleiner, dann Überlauf-Warnung),
   Arbeitsgruppen fliessen aus dem Stand der Webseite durch Spalten,
   Speicherung in `reader_jahrgang` mit Fassungen und Konflikt-Sperre,
   Vorschau-PDF über den Druckdialog (A5 + 3 mm, Schnittmarken), Motiv-Upload
   mit Farbvorschlag und Kontrast-Readouts. Danach kann die Sektion Texte
   pflegen.
2. **Motiv & Farben und Karte.** Palette aus dem Motiv, Rollen mit Kontrast,
   Kartentool eingebettet, Orte aus dem Programm, Legende automatisch.
3. **Programm-Seiten und IDML.** Workshop-, Führungs- und Open-Space-Seiten
   aus der Webseite, Seitenfluss, vollständiger IDML-Export mit eingesetzter
   Programm-Doppelseite. Danach ist der InDesign-Weg vollständig.
4. **Druckstrasse.** PDF/X-4 in GitHub Actions, Knopf im Werkzeug,
   Preflight-Abnahme. Danach braucht es InDesign nicht mehr zwingend.

Zeit: Tagung 3.–6. Februar 2027, Druck des Readers voraussichtlich Mitte
Januar. Etappen 1–3 bis Ende November, Etappe 4 im Dezember; so bleibt der
InDesign-Weg als Sicherheit, falls die Druckstrasse die Abnahme nicht
rechtzeitig besteht.

## Entscheide, die der Auftraggeber trifft

- **Druckweg 2027 (entschieden 11. 10. 2026):** IDML → InDesign → PDF/X als
  Pflicht (Etappe 3); die Druckstrasse (Etappe 4) folgt später, wenn mehr
  Erfahrung da ist.
- Output Intent: PSO Coated v3 (FOGRA51) angenommen; falls die Druckerei ein
  anderes Profil verlangt, ist es ein Parameter der Strasse.

## Ausblick: Plakat und Folder aus derselben Datei (Frage des Auftraggebers, 11. 10. 2026)

Ja, das geht und ist der natürliche nächste Schritt nach Etappe 4. Beide
Drucksachen brauchen nur, was die Jahrgangsdatei ohnehin trägt:

- **Plakat A1** = die Titelseite des Readers in Plakatgrösse: Motiv, Motto
  EN/DE, Tagungsname, Datum, QR, Logo. Ein weiteres Ausgabeformat des
  Seitentyps «titel», mit eigenem Satz der Plakatzeilen (Unterschneidung von
  Hand bleibt in InDesign).
- **Folder A5** = Titelseite (wie Plakat, Motiv und Motto) plus die
  Programm-Doppelseite, die das Tagungsprogramm heute schon aus der Vorlage
  exportiert. Der Folder wird damit ein Export des Readers, kein eigenes
  Werkzeug; die Vorlage `apps/lt-programm/vorlage/LT27.idml` bleibt die
  Rückseite.

Voraussetzung ist, dass Motiv und Farben (Werkstatt 1) stehen; dann sind
Plakat und Folder eine Etappe 5 mit zwei Exportknöpfen, kein neues Konzept.

## Was dieses Konzept bewusst nicht tut

- Kein Live-Mehrbenutzer-Editor, keine Rechteverwaltung: ein Jahrgang, ein
  Link, nacheinander arbeiten.
- Keine freie Gestaltung je Seite: der Seitenplan trägt die Formate, die
  Sektion trägt den Inhalt. Wer gestalten will, tut es in InDesign.
- Keine englische Programmseite lesen: die deutsche trägt beide Sprachen
  (Befund des Tagungsprogramms).
