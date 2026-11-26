# Recherche: Kyrillisch, Arabisch, Griechisch und die Variable

Stand: 26. 11. 2026. Nur gelesen und gemessen, nichts im Repo an Schriften
geändert. Gemessen = mit fontTools an den Dateien im Repo oder an frisch
geladenen Fremdquellen; Vermutung ist als solche gekennzeichnet.

## Befund in fünf Zeilen

1. **Kyrillisch:** Die Quelle (Titillium Web [RUS], 4 Gewichte, 74 kyrillische
   Zeichen) passt in Höhen und Strichstärke zur Hausschrift, ist aber **nicht
   interpolationskompatibel** (40 von 74 kyrillischen Glyphen mit abweichender
   Punktstruktur) und hat zweistöckiges а. Nur **23 von 74** sind formgleich
   mit Latein; **51** müssten neu oder abgeleitet gebaut werden.
2. **Arabisch:** Cairo ist variabel (wght 200–1000, slnt), hat dieselbe
   x-Höhe (500) und Strichstärken, die sich sauber auf die Hausschnitte
   abbilden lassen (Tabelle unten). Das Hindernis ist die **Vertikalmetrik**:
   Cairo 1303/−571, Haus 750/−250.
3. **Griechisch:** Keine Titillium-nahe OFL-Quelle gefunden; Lücke bleibt.
4. **Eine gemeinsame Variable** ist technisch möglich (Kyrillisch klein,
   Arabisch gross), aber Arabisch fügt sich nur mit zweiter Outline-Technik
   (Cairo TrueType, Haus CFF2) und eigener Zeilenhöhe in Office; **Office
   kann nur die Named Instances nutzen, keine stufenlose Achse**.
5. Die Präzedenz (Titillium Web VF von Eli Heuer) ist **kein Muster für
   Arabisch**: Ihre Datei enthält 297 arabische Zeichen, aber **keine
   GSUB-Tabelle** und im GPOS nur `DFLT` (gemessen).

## 1. Hausschrift (Fassung 2.94)

Quelle: `assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf`
(intern Version 2.94). Bau: `tools/goetheanum-fontfix/build_v294.py`, davor
`build_v293.py`, `build_v29_pro.py`, `repair_variable_v28.py`
(Kette in `tools/goetheanum-fontfix/README.md`).

| Messwert | Variable | Static Klar (Office-TTF) |
|---|---:|---:|
| unitsPerEm | 1000 | 1000 |
| Glyphen | 1141 | 1141 |
| cmap-Zeichen | 677 | 677 |
| hhea ascent / descent / lineGap | 750 / −250 / 0 | 750 / −250 / 0 |
| OS/2 typo asc / desc / gap | 750 / −250 / 0 | 750 / −250 / 0 |
| OS/2 win asc / desc | 1114 / 306 | 1114 / 306 |
| USE_TYPO_METRICS | ja | ja |
| x-Höhe | 500 | 500 |
| Versalhöhe | 690 | 690 |
| fsType | 8 | 0 |
| Dateigrösse OTF / TTF in Byte | 522 856 | 169 152 |
| Variable als woff2 in Byte | 98 884 | – |

- **Achse:** nur `wght`, 190 bis 725, Default 440 (Klar). Sieben Named
  Instances: Flüstern 190, Leise 265, Ruhig 350, Klar 440, Deutlich 580,
  Laut 680, Schreien 725. Keine `avar`-Tabelle.
- **Outlines:** CFF2 (PostScript-Kurven). Tabellen: CFF2, GDEF, GPOS, GSUB,
  HVAR, STAT, fvar.
- **Master (gemessen an den Regionen im VarStore, Peaks auf wght
  zurückgerechnet):** Default 440 plus fünf Regionen mit Peak bei etwa 190,
  335, 420, 600 und 725. Das heisst sechs Quellorte; die Stützpunkte stammen
  aus den Titillium-Uprights (Thin, Light, Regular, Semibold, Bold in
  `tools/goetheanum-fontfix/sources/`, Interpolation in `fontfix.py`). Die
  Zuordnung der Peaks zu einzelnen Quelldateien ist Vermutung.
- **GSUB-Scripts:** `DFLT`, `latn`. Features: c2sc, calt, case, ccmp, frac,
  liga, lnum, locl, onum, pnum, smcp, ss03–ss06, tnum, zero.
- **GPOS-Scripts:** `DFLT`, `latn`. Features: cpsp, kern.
- Lizenzzeile der Hausschrift: «Based on Titillium … with Reserved Font Name
  Titillium» (nameID 0).

## 2. Kyrillisch

### Quelle und Messung

Dateien im Repo: `assets/fonts/goetheanum/Fallback/TitilliumRUS-{Light,
Regular,SemiBold,Bold}.ttf`, Version 1.002 (September 2018), «Cyrillization by
Daymarius». Das Original-Repo dieser Erweiterung ist nicht auffindbar (Suche
ergab nur Verzeichnisse wie https://online-fonts.com/fonts/titillium-webrus-daymarius,
keine Quelldateien). Es liegen **nur kompilierte TTF vor, keine Master**.

| Messwert | Light | Regular | SemiBold | Bold | Haus Klar |
|---|---:|---:|---:|---:|---:|
| usWeightClass | 300 | 400 | 600 | 700 | 440 |
| Stammbreite I | 62 | 77 | 111 | 138 | 82 |
| x-Höhe | 500 | 500 | 500 | 500 | 500 |
| Versalhöhe | 695 | 692 | 685 | 680 | 690 |
| UPM | 1000 | 1000 | 1000 | 1000 | 1000 |
| hhea asc / desc | 1133 / −388 | 1133 / −388 | 1133 / −388 | 1133 / −388 | 750 / −250 |
| win asc / desc | 1133 / 388 | 1133 / 388 | 1133 / 388 | 1133 / 388 | 1114 / 306 |
| Glyphen | 530 | 530 | 530 | 530 | 1141 |
| cmap-Zeichen | 472 | 472 | 472 | 472 | 677 |

- **Kyrillisch:** 74 Zeichen (U+0400–052F). Inhalt: Ё Є І Ї Ґ, А–Я, а–я und
  ё є і ї ґ. Kein Serbisch/Makedonisch/Bulgarisch-Locl über die Grundmenge,
  kein Ѕ Ј Ђ Ћ Љ Њ Џ.
- **Features:** GSUB `case`, `frac`, `locl`; GPOS `cpsp`, `kern`; Scripts
  `DFLT`, `cyrl`, `latn`.
- **Lizenz:** OFL, kein Reserved Font Name in nameID 0 (Copyright 2009–2011
  Accademia di Belle Arti di Urbino), fsType 0.
- **Gewichte:** nur diese vier; Thin, ExtraLight und Black fehlen.

### Interpolationskompatibilität (gemessen)

Verglichen wurde je Codepunkt die Konturstruktur (Endpunkte und
Punkt-Typen aus `glyf`) über die Gewichte.

| Gewichtspaar | kompatibel (von 472) | unverträglich Kyrillisch (von 74) | unverträglich Übrige |
|---|---:|---:|---:|
| alle vier | 216 | 40 | 216 |
| Regular / Bold | 231 | 38 | 203 |
| Light / Regular | 295 | 32 | 145 |
| Regular / SemiBold | 271 | 26 | 175 |
| SemiBold / Bold | 231 | 38 | 203 |

Beispiele: Б hat 20/18/20/20 Punkte, Д 23/22/22/22. Ursache ist der Weg der
Quelle (einzeln gezeichnet und gehintet, wie schon bei den Titillium-Web-
Statics), nicht ein Datenfehler. **Heisst:** Die vier TTF lassen sich nicht
direkt zu einer Variable verbinden; Punkte müssten je Glyphe angeglichen
werden (Handarbeit oder Zuordnung der Konturen, Vermutung: 40 Glyphen
Handarbeit, der Rest automatisch).

### Formgleich mit Latein (gemessen, RUS Regular und Bold identisch)

Die Koordinaten der kyrillischen Glyphe sind gleich denen der lateinischen
im selben Font.

| Gruppe | Zeichen | Anzahl |
|---|---|---:|
| Versalien | А В Е К М Н О Р С Т Х | 11 |
| Versalien mit Trema | Ё Ї | 2 |
| Versale | І | 1 |
| Gemeine | а е о р с х | 6 |
| Gemeine mit Trema | ё ї | 2 |
| Gemeine | і | 1 |
| **Summe** | | **23** |

Davon sind in der **Hausschrift** nicht formgleich, sondern müssten neu
aufgesetzt werden: **а** (die Hausschrift hat einstöckiges ɑ, die Quelle
zweistöckiges а, gerendert und angesehen). Alle übrigen 22 sind in der
Hausschrift Latein-Entsprechungen (А → A usw.) und lassen sich als
Komponente oder Kopie aus dem Hausbuchstaben setzen. Ё, Ї, ё, ї brauchen
das Trema der Hausschrift (vorhanden, `build_v29_pro.py` setzt ë/ï ebenso
aus Teilen).

**Nicht formgleich, eigene Zeichnung nötig (51 von 74):**

| Gruppe | Zeichen | Anzahl |
|---|---|---:|
| Versalien Grundformen | Б Г Д Ж З И Л П У Ф Ц Ч Ш Щ Ъ Ы Ь Э Ю Я | 20 |
| Versalien abgeleitet | Й (И + Breve), Є (aus С/Э), Ґ (aus Г) | 3 |
| Gemeine Grundformen | б в г д ж з и к л м н п т у ф ц ч ш щ ъ ы ь э ю я | 25 |
| Gemeine abgeleitet | й, є, ґ | 3 |
| **Summe** | | **51** |

(20 + 3 + 25 + 3 = 51, dazu 23 formgleiche = 74; У und у gelten als eigene
Form, die Quelle zeichnet у mit gebogenem Schwanz, die Hausschrift hat
geraden y-Schwanz.)

**Mögliche Abkürzung (Vermutung, nicht gemessen):** Die Hausschrift hat
Kapitälchen (`smcp`). к м н т в entsprechen in vielen serifenlosen
Kyrillisch-Schnitten Kapitälchenformen von К М Н Т В; das würde bis zu fünf
Gemeine ersparen. Nicht geprüft.

### Text-Form gegen Upright-Logik

- Gerendert verglichen (Hausschrift Klar gegen Titillium RUS Regular): Die
  Hausschrift hat einstöckiges a, die Quelle zweistöckiges a. Das
  kyrillische а der Quelle ist glyphengleich mit diesem zweistöckigen a.
  Zusammen im Satz stünde einstöckiges lateinisches a neben zweistöckigem
  kyrillischem а.
- Die Quelle folgt überall der Text-Form, nicht der Upright-Form: Das
  gilt für а, у und die Latein-Glyphen im Font (g, y, t).
- Breiten: Quelle ist breiter gezeichnet. Beispiel Latein a: Vorschub 501
  (Quelle) zu 495 (Haus Klar), g 514 zu 471, y 483 zu 449. Das
  Verhältnis liegt bei etwa 0,92 bis 0,95 (Haus enger). Dasselbe
  Verhältnis hat `build_v29_pro.py` schon für Chialabs Kerning gesetzt
  (≈ 0,92).

### Weitere Quellen mit kyrillischer Titillium-Form

| Quelle | Befund | Beleg |
|---|---|---|
| Titillium Sans Pro (Chialab) | **kein Kyrillisch**; 607 Zeichen, griechisch nur Δ Ω μ π (4); UFO-Master Thin, Regular, Bold (je Roman/Italic) | gemessen an `Sans/WEB/TitilliumSansPro-Regular.woff2`, Repo https://github.com/chialab/titillium_pro (Stand 4. 2. 2026) |
| Titillio / Titillium Pro Display (pagoPA) | Kyrillisch nicht erwähnt; Zeichenzahl laut `docs/recherche_titillium-pro.md` 608 (also kein Kyrillisch zu erwarten, nicht gemessen) | https://github.com/pagopa/titillium-pro-display |
| Multa Pecunia (Casanova) | Schriftsysteme auf der Repo-Seite nicht genannt; Ableitung aus Titillio, daher vermutlich Latein | https://codeberg.org/m-casanova/MultaPecunia |
| Titillium Web VF (Heuer) | kein Kyrillisch (0 kyrillische Zeichen, gemessen) | https://github.com/eliheuer/titillium-web-vf |
| Google Fonts Titillium Web | 22 statische TTF, Zeichensatz nicht gemessen (Fontsource nennt Latein) | https://github.com/google/fonts/tree/main/ofl/titilliumweb |

**Ergebnis:** Titillium Web [RUS] ist die einzige gefundene Titillium-Quelle
mit Kyrillisch.

### Aufwand je Weg (grobe Schätzung)

| Weg | Glyphen | Master | Anmerkung |
|---|---:|---:|---|
| A. Kyrillisch bleibt Begleitschrift | 0 | 0 | Stand heute |
| B. Kyrillisch aus Hausformen ableiten, Rest aus RUS interpoliert | 51 (davon 6 abgeleitet) | RUS-Gewichte auf Hausmaster (6 Orte) umrechnen | Quelle muss je Glyphe auf gleiche Punktzahl gebracht werden |
| C. Alles neu zeichnen in Upright-Form | 51 + а | 6 Master (190/335/420/440/600/725), gesamt rund 300 Zeichnungen | Vermutung, sauberster Weg |

## 3. Arabisch

### Quelle und Messung

`assets/fonts/goetheanum/Fallback/Cairo-Variable.ttf`, Version 3.130
(gftools 0.9.24), im Repo vorhanden.

| Messwert | Cairo VF | Haus (Variable) |
|---|---:|---:|
| Achsen | wght 200/400/1000, slnt −11/0/11 | wght 190/440/725 |
| unitsPerEm | 1000 | 1000 |
| hhea asc / desc | 1303 / −571 | 750 / −250 |
| typo asc / desc | 1303 / −571 | 750 / −250 |
| win asc / desc | 1312 / 571 | 1114 / 306 |
| USE_TYPO_METRICS | ja | ja |
| x-Höhe | 500 | 500 |
| Versalhöhe | 700 | 690 |
| Glyphen | 1956 | 1141 |
| cmap-Zeichen gesamt | 699 | 677 |
| davon Arabisch (U+0600–06FF, 0750–077F, FB50–FDFF, FE70–FEFF) | 297 | 0 |
| Datei in Byte | 599 548 | 522 856 |
| Outline-Technik | TrueType (glyf, gvar) | CFF2 |
| Variationstabellen | avar, gvar, HVAR, MVAR, STAT | HVAR, STAT, ohne avar |

- **GSUB-Scripts:** `DFLT`, `arab` (Langsys `URD `), `latn` (`MOL `, `ROM `).
  Features: aalt, ccmp, dlig, dnom, fina, frac, init, locl, medi, numr,
  ordn, rlig, rvrn, sinf, subs, sups. **Kein `calt`, `liga`, `isol`
  (nicht nötig, Standardform).**
- **GPOS:** kern, mark, mkmk. **Kein `curs`.**
- **Lizenz:** OFL, Copyright «The Cairo Project Authors» (Mohamed Gaber),
  kein Reserved Font Name in nameID 0, fsType 0.

### Vertikale Ausdehnung (gemessen, in Einheiten)

| | Cairo 400 | Cairo 700 | Haus Rahmen |
|---|---:|---:|---:|
| Arabisch Grundbuchstaben yMax | 807 | 847 | 750 (asc) |
| Arabisch Grundbuchstaben yMin | −430 | −462 | −250 (desc) |
| Arabisch mit Marken yMax | 963 | 997 | 750 |
| Arabisch mit Marken yMin | −430 | −462 | −250 |
| Latein yMax | 749 | 751 | – |
| Latein yMin | −235 | −229 | – |

Der Arabisch-Bedarf (Grundbuchstaben bis −462 und 847, mit Marken bis 997) liegt
deutlich über dem Hausrahmen 750/−250. Wer die Hausmetrik (1000 Einheiten
Zeilenhöhe) behält, klemmt Arabisch in Office oder überlappt es auf der Zeile
darüber (Vermutung, nicht in Office geprüft). Wer Cairos Metrik übernimmt
(1874 Einheiten), bekommt für Latein 1,87 em Zeilenhöhe, mehr als das Doppelte
der Hausschrift.

### Gewichtsabgleich (gemessen, Stamm des Alif gegen Stamm von l)

Cairos Alif-Stamm als Breite der Glyphenbegrenzung, auf ein Raster von
25 wght-Schritten abgetastet; Hausstamm als Breite von l.

| Hausschnitt | wght | Stamm Haus | Cairo-wght mit gleichem Stamm |
|---|---:|---:|---:|
| Flüstern | 190 | 35 | 200 |
| Leise | 265 | 49 | 302 |
| Ruhig | 350 | 65 | 358 |
| Klar | 440 | 81 | 452 |
| Deutlich | 580 | 107 | 636 |
| Laut | 680 | 126 | 683 |
| Schreien | 725 | 134 | 705 |

Cairo-Stämme zur Probe: 200 → 35, 300 → 48, 400 → 77, 500 → 85, 600 → 92,
700 → 133, 800 → 152, 1000 → 224. Der Sprung zwischen 600 und 700 (92 → 133)
ist ein Merkmal von Cairos `avar`-Abbildung. **Heisst:** Bei gleichem wght
wäre das Arabisch in Deutlich (580) zu dünn (Stamm Cairo 580 ≈ 90 statt 107).
Ein Mapping Hausachse → Cairo-Achse über `avar` gleicht das aus, ist aber
eine Eigenbau-Tabelle.

### Cairo und Titillium

Cairo ist von Mohamed Gaber, laut Repo-Beschreibung «extended the famous
Latin typeface family Titillium Web to support the Arabic script»:
https://github.com/Gue3bara/Cairo (die Arabisch-Zeichnung folgt der
Kufi-Kalligrafie). Die Namenstabelle nennt zusätzlich «Accademia di Belle
Arti di Urbino» als Hersteller.

### Präzedenz: Titillium Web VF (Eli Heuer)

Repo https://github.com/eliheuer/titillium-web-vf (letzter Commit 5. 3. 2020),
OFL.

- **Quellen:** `sources/TitilliumWeb-Roman.glyphs` und `Cairo-Roman.glyphs`
  (gleiche 833 Glyphen), je drei Master (Gewichtswerte 36, 138 oder 80, 232).
  Bau mit fontmake (`scripts/build.sh`), Variable `wght` 200–900,
  Default 200.
- **Gemessen an `fonts/TitilliumWeb-Roman-VF.ttf`:** 833 Glyphen, 700
  cmap-Zeichen, **297 davon Arabisch, aber keine GSUB-Tabelle**, GPOS nur
  `DFLT` mit mark/mkmk. Ohne `init/medi/fina` verbinden sich arabische
  Buchstaben nicht. Die Datei zeigt, dass Arabisch nur als Zeichensatz
  mitkam, nicht als funktionierendes Shaping.
- **Metriken:** hhea 1303/−571, win 1312/571, also **Cairos Metrik auf
  einer lateinischen Titillium-Web** (gemessen). Das verdoppelt die
  Zeilenhöhe von reinem Latein; ob das die Absicht war, ist nicht belegt.
- **Issues** (24 offen, https://github.com/eliheuer/titillium-web-vf/issues):
  keine zu Vertikalmetrik, Arabisch oder Kyrillisch; #29 «Regular Weight looks
  like bold, it's not same as Titillium» und #30 betreffen das Gewicht, #24
  Cairo (Test gegen Google-Fonts-Stand). Rest sind Fontbakery-Meldungen.
- Google Fonts führt Titillium Web weiter als 22 statische TTF
  (https://github.com/google/fonts/tree/main/ofl/titilliumweb), Cairo als
  `Cairo[slnt,wght].ttf` (https://github.com/google/fonts/tree/main/ofl/cairo).
  Die Variable von Heuer wurde also dort nicht zum Standard (Beleg:
  Dateiliste).

### Aufwand je Weg (grobe Schätzung)

| Weg | Glyphen | Master | Anmerkung |
|---|---:|---:|---|
| A. Arabisch bleibt Begleitschrift (statisch 400/700) | 0 | 0 | Stand heute |
| B. Cairo als zweite Variable-Datei neben der Hausschrift, `unicode-range` im CSS, `avar` Hausachse → Cairo | 0 | 0 | rein im CSS und Mapping; Office: Named Instances je Hausschnitt |
| C. Arabisch in eine Datei mit der Hausschrift einbauen | 297 arabische Zeichen; im Arabisch-Subset 388 Glyphen samt Formen aus GSUB/GPOS | Cairo hat 3 Master, Haus 6: Cairo muss auf die 6 Orte gebracht werden | Outlines TrueType gegen CFF2 umwandeln (cu2qu/qu2cu); `avar` neu |
| D. Arabisch neu zeichnen | nicht abschätzbar | – | nicht erwogen |

## 4. Griechisch

- Hausschrift (Variable, gemessen): **4 griechische Zeichen** (Δ Ω μ π, also
  Mathematik- und Einheitenzeichen; `docs/schriften-verteilung.md` nennt 1 von 57
  für den Block, Zählweise dort abweichend), kein Kyrillisch, kein Arabisch.
  Chialabs Pro hat dieselben vier.
- **Keine Titillium-nahe OFL-Griechisch-Quelle gefunden.** Chialab Pro: 4
  Zeichen. Titillio, Multa Pecunia, Heuer VF: Griechisch nicht belegt. Die
  Websuche («Titillium Greek extension») fand nur Cairo als Skript-Fork.
- Titillium-fremde Kandidaten stehen schon in
  `assets/fonts/schriftsysteme/LIZENZEN.md` und `docs/schriften-verteilung.md`
  (Fira Sans, Commissioner, IBM Plex Sans, Source Sans 3), alle OFL.
- **Lücke:** Wer Griechisch in der Hausschrift will, zeichnet es: das
  griechische Alphabet (24 Buchstaben, Gross und Klein) plus Tonos-Formen,
  Grössenordnung 60–70 Glyphen (Vermutung).

## 5. Gemeinsame Variable: technische Risiken

### Grösse

| Datei | woff2 in Byte | Quelle der Zahl |
|---|---:|---|
| Hausschrift Variable v2.9 | 98 884 | gemessen |
| Cairo VF, nur Arabisch (388 Glyphen) | 58 920 | gemessen (fontTools-Subset) |
| Cairo VF, ganz (822 Glyphen) | 137 404 | gemessen |
| Cairo-Regular woff2 vorhanden | 49 376 | gemessen |
| Titillium RUS Regular, nur Kyrillisch (77 Glyphen) | 6 744 | gemessen |
| Titillium RUS Bold, nur Kyrillisch | 6 520 | gemessen |
| **Haus + Kyrillisch + Arabisch (eine Datei)** | **rund 160 000 bis 200 000** | Schätzung: 99 000 + 59 000 + 10 000 bis 40 000 (Kyrillisch variabel statt statisch, Arabisch auf sechs Master) |

Getrennte Dateien mit `unicode-range` im CSS laden nur, was die Seite braucht
(Vermutung zur Laufzeit: Latein 99 KB, Arabisch erst bei arabischem Text).
Das ändert nichts an Office, wo Installation zählt.

### Shaping und Office

- **Variable Fonts in Office (Beleg lückenhaft):** Microsoft nennt Windows 10
  Version 1709 als Einstieg (https://learn.microsoft.com/en-us/typography/develop/font-variations),
  Named Instances erscheinen wie statische Schriften. Dalton Maag meldet für
  PowerPoint: vordefinierte Instanzen ja, **weitere Achsen nein**, PDF-Erzeugung
  und manche Druckertreiber unzuverlässig
  (https://daltonmaag.com/help/using-variable-fonts.html). Ein Nutzerbericht
  bestätigt: in Word und PowerPoint sind statische Instanzen nutzbar, die
  Achse nicht (https://learn.microsoft.com/en-au/answers/questions/2110791/does-excel-support-variable-fonts).
  Das Haus hat das schon entschieden: Office bekommt statische TTF (Trio), die
  Variable ist nur Zusatz (`docs/schriften-verteilung.md`). Eine gemeinsame
  Variable ändert für Office daher nichts; dort müssten Kyrillisch und
  Arabisch ohnehin als statische Schnitte (ab 5 Schnitten wären es 10 weitere
  Dateien) nachgebaut werden.
- **Einbettung:** Office-Einbettung ist laut Microsoft auf die Windows-Desktop-
  Versionen von Word, PowerPoint und Publisher beschränkt, Mac und Web
  ausgenommen (Blogbeitrag ohne Datum, aus dem Suchtreffer; Stand heute
  nicht neu geprüft). Ob variable Instanzen einbettbar sind, ist offen.
- **RTL in Office:** nicht gemessen. Bekannt ist, dass Word/PowerPoint
  Arabisch über Uniscribe/DirectWrite formen; `init/medi/fina/rlig` müssen im
  `arab`-Script stehen (Cairo: ja, Heuers VF: nein).

### Vertikalmetrik-Konflikt

Siehe Tabelle in Abschnitt 3. Vier Wege, gemessen als Zahlen:

| Weg | Zeilenhöhe Latein | Wirkung (Vermutung) |
|---|---:|---|
| Hausmetrik 750/−250 behalten | 1000 | Arabisch klemmt unter −250 und über 750 |
| Cairo-Metrik 1303/−571 übernehmen | 1874 | Latein bekommt fast doppelte Zeilenhöhe |
| Mittelweg (Messungen): asc 850, desc −460 | 1310 | Grundbuchstaben passen, Marken brauchen Platz |
| `win` gross (wie heute 1114/306), typo klein | – | Windows klemmt nicht, Zeilenabstand folgt typo |

Der Eintrag in `OS/2` ist eine Datei-Eigenschaft: Eine gemeinsame Datei hat
**eine** Zeilenhöhe. Zwei Dateien (Haus, Arabisch) haben zwei, Office wählt je
Schrift die ihre. Das ist der stärkste technische Grund für getrennte Dateien.

### Lizenz

- **Hausschrift:** OFL 1.1 mit Reserved Font Name «Titillium» in nameID 0;
  daher der Name «Goetheanum». Variable fsType 8 (bearbeitbare Einbettung),
  Statics fsType 0 (gemessen; Unterschied ist nicht erklärt).
- **Titillium Web [RUS]:** OFL, kein Reserved Font Name (nameID 0
  gemessen), fsType 0. **Cairo:** OFL, kein Reserved Font Name (gemessen),
  fsType 0.
- OFL 1.1 erlaubt, Fassungen zu verändern und zu verbinden, sofern Lizenz und
  Copyright der Quellen erhalten bleiben und kein Reserved Font Name
  verwendet wird. Das passt zum heutigen Weg
  (`build_begleitschriften.py` bricht bei Reserved Font Name ab). Eine
  rechtliche Prüfung ist das nicht; der Volltext liegt in
  `assets/fonts/goetheanum/OFL.txt`.

## Quellen

- Chialab Titillium Pro: https://github.com/chialab/titillium_pro
- Heuer Titillium Web VF: https://github.com/eliheuer/titillium-web-vf
- Cairo: https://github.com/Gue3bara/Cairo
- Google Fonts Titillium Web: https://github.com/google/fonts/tree/main/ofl/titilliumweb
- Google Fonts Cairo: https://github.com/google/fonts/tree/main/ofl/cairo
- pagoPA Titillio: https://github.com/pagopa/titillium-pro-display
- Multa Pecunia: https://codeberg.org/m-casanova/MultaPecunia
- Titillium Web RUS (nur Verzeichnis): https://online-fonts.com/fonts/titillium-webrus-daymarius
- Microsoft, Font Variations: https://learn.microsoft.com/en-us/typography/develop/font-variations
- Dalton Maag, Using Variable Fonts: https://daltonmaag.com/help/using-variable-fonts.html
- Microsoft Q&A zu Variable Fonts in Office: https://learn.microsoft.com/en-au/answers/questions/2110791/does-excel-support-variable-fonts
- Im Repo: `CLAUDE-REF.md` § Schnitt-System, `docs/schriften-verteilung.md`,
  `docs/recherche_titillium-pro.md`, `tools/goetheanum-fontfix/README.md`,
  `tools/goetheanum-fontfix/build_begleitschriften.py`
