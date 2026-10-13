# Übergabe: Plakat «Faust 2027 im Goetheanum» (13. 10. 2026)

Richtungssuche mit dem Theater. Die Bildrechte sind noch nicht geklärt; die
Entwürfe bleiben intern und gehen nicht live.

## Auftrag

Alle Motive durchprobieren, für jedes passende Anordnungen von Schriftzug und
Infos finden. Am Ende wieder **ein IDML**. Die zwei rohen Entwürfe bleiben
unverändert als Basis in der Datei; die neuen Varianten kommen als weitere
Spreads dazu.

## Was der Auftraggeber in die neue Sitzung mitbringt

Die Dateien der alten Sitzung sind weg. Nötig sind:

1. `Plakate-2026_mini.idml` (Schriftzug, Logo, Daten, zwei Rohentwürfe)
2. die vier ZIPs `entwurf-faust-bilder-teil1…4.zip` (12 Bühnenfavoriten im
   Original, 5 Porträts von Ludowika Held)

Fehlen die ZIPs, lassen sie sich neu holen (siehe unten).

## Das IDML (Befund)

- Zwei Spreads mit je einer Seite, **A2**: 1190,55 × 1683,78 pt. Die
  Dokumentvoreinstellung nennt 2383,94 × 3370,39 pt (A0); die Seitengrenzen
  gelten.
- Je Entwurf: Hintergrund-Blob (Polygon, Faustrot, leicht gedreht), Bildrahmen
  mit verknüpftem PSD (`Figur_GenAIImage_…psd`, liegt nur auf dem Mac des
  Auftraggebers), ein Textrahmen, eine Logo-Gruppe in Schwarz 80 %. Die
  GraphicLine liegt weit ausserhalb der Seite (y ≈ −203 000) und kann
  bleiben.
- Farbe: **Faustrot** = CMYK 0/100/80/10 (`Color/Faustrot`); Text und Logo in
  `Tint/[Schwarz] 80%`.
- Schrift: «Goetheanum Variabel», Schnitt **Deutlich**, 91,4 pt im Rahmen,
  Zeilenabstand 110, Zahlen tabellarisch (`OTFFigureStyle="TabularLining"`).
  Der Rahmen skaliert mit 0,4976; die wirksame Grösse ist darum kleiner.
- Die Elemente tragen verschachtelte `ItemTransform`-Matrizen. Zur Position
  auf der Seite: Spread-Matrix × Item-Matrix × Punkt; die Seite sitzt mittig
  auf dem Spread-Ursprung.
- Neue Spreads: einen Spread-XML samt Stories kopieren, neue `Self`-IDs
  vergeben, in `designmap.xml` eintragen. Bilder als Verknüpfung auf
  relative Pfade.

## Texte

- Titel (zwei Fassungen im IDML): «Faust 2027 im Goetheanum» und «Den ganzen
  Faust erleben im Goetheanum 2027»
- Daten: «9.–11. · 16.–18. · 24.–25. Juli»
- «Tickets: www.faust.jetzt»

## Motive

**Bühne** (Drive-Ordner «Faust2026_Probe», Fotos XueLi), Rangfolge:

1. Mond über Wasser: `SA701200`, `SA701211`, `SA701216` (Faust 2)
2. Silhouette vor Rot: `SA701700`
3. Ast und Säule vor Blau: `SA701664`
4. Läufer vor Blau: `SA701680`
5. Glaskugel mit Nebel (quer): `SA700510`
6. Kronleuchter (quer): `SA700470`
7. Faust in der Bibliothek (quer): `SA707378` (Faust 1)
8. Hexenkessel (quer): `SA708490` (Faust 1)
9. Gretchen und Faust: `SA709062` (Faust 1)
10. Mantelwurf: `SA707753` (Faust 1)

Hochformate sind 3000 × 4500 px, bei A2 knapp 190 dpi: für Entwürfe genug,
für den Druck die Originale aus dem Drive-Ordner nehmen.

**Ludowika Held** (5 Bilder von filmmakers.eu, 1440 × 2160 px, © Lev
Gonopolsky): https://www.filmmakers.eu/de/actors/ludowika-held. Ihr
Instagram `ludowikaheld` ist nur mit Anmeldung sichtbar; der Auftraggeber
liefert die Porträts von dort selbst. Bessere Porträts über die Agentur
(Reiter «Agency» auf der Filmmakers-Seite).

## Bilder neu holen (falls nötig)

Der Drive-Ordner ist eine Synology-Drive-Freigabe: Die Seite lädt per
JavaScript, die Dateien lassen sich nur im Browser (Playwright/Chromium) mit
dem Sitzungs-Token über `SYNO.SynologyDrive.Files` (`list`, `download`)
abholen. Die Filmmakers-Bilder stehen als `imgproxy.filmmakers.eu/…rt:fit/w:3840…jpg`
direkt im HTML.

## Regeln für die Gestaltung

Hausregeln aus `CLAUDE.md` und `assets/typografie/typo-regeln.yaml`
beachten, betroffene Regel-IDs nennen. Besonders: G01 Einfachauszeichnung,
G03 Weglassen, G05 Betonung nur mit Laut (nie Versalien, Sperren,
Unterstreichen), G23 Versalien nur per Laufweite sperren, G25 tabellarische
Ziffern. Keine Initialen, kein Schmuck. Das Auge prüft das Gewicht: die
Entwürfe als Bild ansehen, nicht nur rechnen.

## Offene Punkte

- Bildrechte (Fotografie XueLi, Lev Gonopolsky) vor jeder Veröffentlichung klären.
- Instagram-Porträts von Ludowika Held liefert der Auftraggeber.
- Empfohlen für diese Aufgabe: das grosse Modell (Gestaltungsurteil und
  IDML-Feinarbeit).
