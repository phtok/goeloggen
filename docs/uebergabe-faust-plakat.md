# Übergabe: Plakat «Faust 2027 im Goetheanum» (13. 10. 2026)

Richtungssuche mit dem Theater. Die Bildrechte sind noch nicht geklärt; die
Entwürfe bleiben intern und gehen nicht live.

## Auftrag

Alle Motive durchprobieren, für jedes passende Anordnungen von Schriftzug und
Infos finden. Am Ende wieder **ein IDML**. Die zwei rohen Entwürfe bleiben
unverändert als Basis in der Datei; die neuen Varianten kommen als weitere
Spreads dazu.

## Was der Auftraggeber in die neue Sitzung mitbringt

Die Dateien der alten Sitzung sind weg. Nötig ist **eine** Datei:

`faust-plakat-paket.zip` (9,7 MB): `Plakate-2026_mini.idml` (Schriftzug, Logo,
Daten, zwei Rohentwürfe), 12 Bühnenfavoriten und 5 Porträts von Ludowika Held
(`faust-bilder-klein/`), dazu 31 weitere Favoriten aus «Allbilde»
(`faust-bilder-klein/allbilde-auswahl/`). Alle Bilder sind auf höchstens
2000 px verkleinert; die Originale für den Druck stehen im Drive-Ordner
(siehe «Bilder neu holen»).

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

**Bewertung der Allbilde-Auswahl durch den Auftraggeber** (13. 10.; Sichtung
von rund 3400 verkleinerten Fotos, dunkle Bilder und Serien-Dubletten
vorab aussortiert; Präfix `F1_` = Faust 1, `F2_` = Faust 2):

- **Ja:** `F1_SA707865` (blaue Schleier-Geister um Faust, dunkel, quer),
  `F1_SA707899` (Mephisto hell mit Brief vor der Bibliothek, hoch)
- **Vielleicht:** `F2_SA701066`, `F2_SA701075` (Figur mit Armen zum Mond),
  `F2_SA701266`, `F2_SA701270` (Wassergeist mit Krone neben dem Mond),
  `F2_SA701110` (grosser Mond, kaum Figur), `F1_SA708170` (Faust hält sich
  die Ohren zu, zwei Mephisto, quer), `F2_SA701388` (Frau in Weiss mit langem
  Tuch, hoch)
- **Nein:** alle 22 übrigen der 31, darunter Arme zum Himmel
  (`F2_SA701562`, `F2_SA701565`), Gretchen mit Mimosen, Handstand, Fahrrad,
  Student mit Büchern, Homunculus, Engel, Pudel, Mantelwurf, Laser

Lesart: gefragt sind dunkle, geheimnisvolle Stimmungen mit Figuren, Mond und
Schleiern; helle, heitere oder sehr szenische Bilder und das reine Blau
kommen nicht an. Die Bilder liegen alle 31 im Paket
(`faust-bilder-klein/allbilde-auswahl/`), gebraucht werden die Ja- und
Vielleicht-Bilder. Die früheren Favoriten (Mond-Serie `SA701200`, `SA701211`,
`SA701216`, Silhouette `SA701700`, Ast und Säule `SA701664` usw.) sind
nicht bewertet.

Ungesichtet: Die Originale von «Faust 2» (2065 Dateien) kennt die Sichtung nur
über die 896 verkleinerten («Faust 2 Klein»); der Ordner «Faust 1» (301
Dateien) liegt daneben.

**Ludowika Held** (5 Bilder von filmmakers.eu, 1440 × 2160 px, © Lev
Gonopolsky): https://www.filmmakers.eu/de/actors/ludowika-held. Ihr
Instagram `ludowikaheld` ist nur mit Anmeldung sichtbar; der Auftraggeber
liefert die Porträts von dort selbst. Bessere Porträts über die Agentur
(Reiter «Agency» auf der Filmmakers-Seite).

## Bilder neu holen (falls nötig)

Den Freigabe-Link gibt der Auftraggeber in der Sitzung mit; er steht bewusst
nicht im Repo. Der Drive-Ordner ist eine Synology-Drive-Freigabe: Die Seite lädt per
JavaScript, die Dateien lassen sich nur im Browser (Playwright/Chromium) mit
dem Sitzungs-Token über `SYNO.SynologyDrive.Files` (`list`, `download`)
abholen. Struktur: `Allbilde/Faust 1/Faust1_JPEG` (2470 Originale),
`Allbilde/Faust 1 Klein` (2470), `Allbilde/Faust 2/Faust 2` (2065),
`Allbilde/Faust 2 Klein` (896). Die `list`-Antwort ist auf 1000 Einträge
begrenzt (`offset` weiterzählen). Die Dateinamen der Favoriten gelten in den
Original- und Klein-Ordnern gleich. Die Filmmakers-Bilder stehen als `imgproxy.filmmakers.eu/…rt:fit/w:3840…jpg`
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
