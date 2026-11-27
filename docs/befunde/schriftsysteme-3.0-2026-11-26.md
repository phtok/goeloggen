# Entscheidvorlage: Kyrillisch, Arabisch, Griechisch und die Hausschrift 3.0

Stand 26. 11. 2026. Frage des Inhabers: ‹Was ist aus den anderen
Schriftsystemen geworden? Arabisch, Kyrillisch … die gehören doch auch zu
3.0? Könnten die sogar Teil der Variable werden?› Messungen und Quellen:
`docs/recherche_schriftsysteme-variable.md`. Kein Bau ohne Entscheid.

## Stand heute

- **Goetheanum Kyrillisch** (aus Titillium Web [RUS], Regular und Bold) und
  **Goetheanum Arabisch** (aus Cairo, statisch 400 und 700) sind
  Begleitschriften, nur im Installer (`docs/schriften-verteilung.md`).
- **Griechisch** hat keine Titillium-Quelle; auf Webseiten springt Source
  Sans 3 ein.
- Ein Plan ‹3.0› stand bisher nirgends im Repo. Diese Vorlage ist der erste.

## Empfehlung (das Wichtigste zuerst)

| System | Empfehlung | Warum | Aufwand |
|---|---|---|---|
| **Kyrillisch** | **in die Hausschrift, als Kern von 3.0** | gleiche Höhen (x 500, Versal 690), Strich passt, 23 von 74 Zeichen sind Hausbuchstaben | 51 Zeichen neu, in Upright-Form, je 6 Master: ein Schriftentwurf |
| **Arabisch** | **eigene Datei, gleiche Achse**: ‹Goetheanum Arabisch› variabel, Schnitte wie die Hausschrift | eine Datei hat nur eine Zeilenhöhe: Arabisch braucht 847/−462, die Hausschrift 750/−250 | klein: Cairo umbenennen, Achse auf Leise … Laut abbilden, fünf statische Schnitte für Office |
| **Griechisch** | **Lücke lassen**, Source Sans 3 bzw. Fira Sans wie bisher | keine Titillium-nahe Quelle; nur bei echtem Bedarf zeichnen | 60–70 Zeichen neu |

## Begründung

**Kyrillisch gehört in die Variable.** Kyrillisch und Latein teilen Bauweise
und Masse; in einem russischen oder ukrainischen Text stehen beide im selben
Satz (Namen, Abkürzungen). Gemessen: x-Höhe 500 wie das Haus, Stamm der
Quelle 77 zu Klar 82. Aber:
- Die Quelle ist **nicht interpolationsfähig** (40 von 74 kyrillischen
  Zeichen mit anderer Punktzahl je Gewicht) und hat nur kompilierte Dateien.
- Sie folgt der Text-Form (zweistöckiges а, gebogenes у); die Hausschrift
  hat die Upright-Form. Aus der Quelle übernommen, stünde einstöckiges a
  neben zweistöckigem а.
- **Halb geht nicht:** Fehlt ein Zeichen, setzt der Browser nur dieses aus
  der Ersatzschrift, mitten im Wort. Kyrillisch kommt ganz oder gar nicht.

Darum ein eigener Entwurf: 22 Zeichen als Komponenten aus den
Hausbuchstaben (А В Е К М Н О Р С Т Х, е о р с х, І і, Ё Ї ё ї), 51 neu
gezeichnet in den sechs Mastern der Variable, die Quelle als Vorlage für
die Formen. Mit Kerning, `locl` für Bulgarisch erst später.

**Arabisch gehört neben die Variable, nicht hinein.** Drei Gründe, alle
gemessen:
1. **Zeilenhöhe:** Arabische Grundbuchstaben reichen bis −462 und 847, mit
   Vokalzeichen bis 997. Die Hausschrift rechnet mit 750/−250. Eine
   gemeinsame Datei hätte eine Zeilenhöhe: entweder klemmt Arabisch, oder
   Latein bekommt fast die doppelte Zeilenhöhe (Cairo-Metrik 1874).
2. **Technik:** Cairo ist TrueType, die Variable CFF2; Cairo hat 3 Master,
   das Haus 6. Zusammenführen heisst umrechnen, nicht verbinden.
3. **Präzedenz misslungen:** Die Titillium-Web-Variable von Eli Heuer hat
   297 arabische Zeichen, aber keine GSUB-Tabelle: die Buchstaben verbinden
   sich nicht. Sie trägt ausserdem Cairos Zeilenhöhe auf reinem Latein.

Was dennoch zusammenwächst: die **Achse**. Cairo ist variabel (wght
200–1000). Abgebildet über den Stamm (Klar 440 ↔ Cairo 452, Deutlich 580 ↔
636, Laut 680 ↔ 683) bekommt ‹Goetheanum Arabisch› dieselben Schnittnamen
Leise bis Laut. Im Web lädt sie per `unicode-range` nur, wo Arabisch steht;
in Office ist sie eine eigene Schrift mit eigener Zeilenhöhe, wie heute.

**Office ändert sich durch eine Variable nicht.** Word und PowerPoint zeigen
von einer Variable nur die benannten Schnitte; das Haus liefert Office
darum statische TTF. Auch Kyrillisch in 3.0 käme als statische Schnitte ins
Office-Paket.

## Was ‹3.0› dann heisst (Vorschlag)

- Hausschrift mit **Kyrillisch**, in allen Schnitten und in der Variable.
- **Goetheanum Arabisch** als Schwesterdatei mit denselben Schnittnamen.
- Die **Kursive** (läuft in eigener Session), sobald sie steht.
- Griechisch nicht.

## Zu entscheiden, je eine Frage

1. **Kyrillisch als Entwurf in die Hausschrift (Kern von 3.0)?**
   Empfehlung ja, wenn es Texte gibt, die es brauchen (Übersetzungen,
   Tagungen auf Russisch oder Ukrainisch). Sonst bleibt die Begleitschrift.
2. **Arabisch als variable Schwesterdatei mit den Hausschnitten?**
   Empfehlung ja; das ist die kleine Etappe und kann zuerst laufen.
3. **Griechisch offen lassen?** Empfehlung ja.

## Entscheid des Inhabers (26. 11. 2026)

‹Kyrillisch in die Hausschrift. Wie weit in die Variable integrierbar?
Arabisch extra ist sehr gut. Griechisch in Source Sans reicht aus.›

- **Kyrillisch:** ja, in die Hausschrift. In die Variable ganz: Jedes neue
  Zeichen wird in allen sechs Mastern gezeichnet (wie die lateinischen), dann
  läuft es stufenlos von Flüstern bis Schreien mit, und die fünf statischen
  Schnitte und Office-TTF entstehen daraus wie heute. Grenze nur dort, wo
  ein Zeichen nicht in allen Mastern gleich gebaut ist; das prüft
  `proof_variable_axis.py --alle`.
- **Arabisch:** als variable Schwesterdatei (Etappe A1).
- **Griechisch:** Source Sans 3 reicht; keine eigene Zeichnung.

## Etappen nach Entscheid

| Etappe | Inhalt | Ergebnis |
|---|---|---|
| A1 | Cairo variabel umbenennen, `avar` auf die Hausachse, fünf statische Schnitte, Installer, `unicode-range` in `tokens.css` | Goetheanum Arabisch variabel, Probe-Seite |
| | **A1 erledigt (27. 11.)**, ausser `tokens.css`: wartet auf Freigabe des Inhabers. Bau `tools/goetheanum-fontfix/build_arabisch.py`; Probe https://werkzeuge.goetheanum.ch/schrift-arabisch-probe.html | |
| K1 | 22 Komponenten-Zeichen und Plan der 51 Formen (Upright-Logik für а у), Probe in Klar | Probe-Bild, Entscheid zu den Formen |
| K2 | 51 Zeichen in sechs Mastern, Kerning, Prüfer (`proof_variable_axis.py --alle`) | Hausschrift 3.0-Kandidat |
