# Befund E1: Kursive der Hausschrift aus Titillium Sans Pro Italic

Stand: 31. 10. 2026. Etappe E1 aus `docs/recherche_titillium-pro.md`,
Entscheid des Inhabers vom 31. 10.: «die Italics sind interessant, Einbau ins
Haussystem erwägen, voll kompatibel». Dazu E5 (Black-Probewort), die sich an
E1 hängt.

- Probe-Schnitt: `assets/fonts/goetheanum/Probe/Goetheanum-Kursiv-Probe-Klar.otf`
  und `.woff2` (Familie «Goetheanum Kursiv Probe», Version 0.100, **nicht im
  Paket**; `pack_release_zip.py` erfasst den Ordner nicht)
- Bau: `tools/goetheanum-fontfix/build_kursiv_probe.py` (idempotent, zweimal
  gebaut, gleiche Prüfsumme)
- Specimen: https://werkzeuge.goetheanum.ch/kursive-probe.html (Treibhaus)
- Quelle: https://github.com/chialab/titillium_pro, Commit `65ca1530`
  (4. 2. 2026), OFL

## Ergebnis in drei Sätzen

Die Pro-Kursive passt auf die Hausschrift: gleiche x-Höhe, gleiche Einheiten,
und die Gewichte bilden sich fast eins zu eins ab. Die Upright-Formen sind in
der Kursiven schon da – g, y, t entsprechen der Hausform, das einstöckige a
und das gerade l hat Chialab als ss01/ss02 gezeichnet; die Probe macht sie zur
Grundform. Offen sind eine Regelfrage (S01: «keine echte Kursive») und die
Office-Familie, in der Leise heute den Kursiv-Platz hält.

## 1 Messung

**Neigung** 12° (alle Kursiv-Master und -Schnitte).

**Vertikalmasse** (Einheiten auf 1000):

| | x-Höhe | Versalhöhe | typo asc/desc |
|---|---:|---:|---:|
| Hausschrift Klar | 500 | 690 | 750 / −250 |
| Pro Italic (Regular) | 500 | 700 | 950 / −250 (woff2) |
| Probe Kursiv Klar | 500 | 700 | 750 / −250 |

Die x-Höhe ist gleich; die Versalhöhe liegt 10 Einheiten höher (1,4 %, bei
18 px 0,2 px). Die Probe übernimmt typo, hhea und win der Hausschnitte
(lineGap 0, USE_TYPO_METRICS): gleiche Zeilenhöhe im Satz, geprüft im Specimen.

**Gewicht.** Gemessen am Stamm des I (Fläche durch Höhe, scherungsfest).
Ziel ist dieselbe Strichdicke quer zur Strichrichtung, darum der aufrechte
Stamm geteilt durch cos 12°. Die Master stehen bei Thin 35, Regular 78,
Bold 137 (waagrecht); dazwischen linear, wie im Audit.

| Hausschnitt | Stamm | Ziel geneigt | entspricht Pro |
|---|---:|---:|---:|
| Leise 265 | 50 | 51,1 | 212 |
| Ruhig 350 | 67 | 68,5 | 334 |
| Klar 440 | 82 | 83,8 | 430 |
| Deutlich 580 | 110 | 112,5 | 575 |
| Laut 680 | 129 | 131,9 | 674 |

Ausser bei Leise decken sich die Hauszahlen mit der Pro-Gewichtsskala auf
±10. Gebaut ist nur Klar (I-Stamm 83,5).

**Breite** gegen Klar: n 508 / 503, o 504 / 486, H 668 / 619, Gemeine im
Mittel 456,5 / 443. Ein Satz läuft in der Kursiven 2,7 % länger
(737,6 gegen 718,2 px bei 22 px); die Versalien sind 8 % breiter. Klassisch
läuft eine Kursive eher schmaler als ihre Aufrechte. Die Probe lässt die
Breiten, wie Chialab sie gezeichnet hat; ein Stauchen auf 97 % wäre ein
Schalter im Skript, verschiebt aber das Verhältnis von Stamm zu Haarstrich.

**Zeichenvorrat.** 869 Glyphen, 608 Zeichen (Klar: 411). Von den Zeichen der
Hausschrift fehlen 8: `Ǻ ǻ`, die Bindestrich-Varianten U+2010–2012, der
Wortverbinder U+2060 und zwei Altlasten im Privatbereich. Features: `kern`,
`liga`, `frac`, `tnum`/`pnum`, `case`, `zero`, `sups`/`subs`, ss03–ss06
(Listenzeichen) – aber **keine Kapitälchen** (`smcp`/`c2sc`) und keine
Mediävalziffern (`onum`), die die Hausschrift führt.

## 2 Upright-Formen: nachziehen oder Text-Form lassen

Angeschaut im Specimen (Abschnitt «Formen») und gross gerendert:

- **g, y, t** der Pro-Kursiven entsprechen schon der Hausform: gerader
  y-Schwanz, aufrechter g-Abstrich, schlichtes t. Nichts nachzuziehen. (Die
  Recherche nannte g, y, t als Text-Form; das gilt für die aufrechte Pro, nicht
  für ihre Kursive.)
- **a** und **l** hat Chialab in der Kursiven doppelt gezeichnet: Grundform
  a mit Abschwung und l mit Bogen (Text-Form), ss01 einstöckiges ɑ und ss02
  gerades l (Upright-Form).

Die Probe tauscht Grund- und Alternativform (24 Glyphen: a, l und ihre
Akzente, `fl`, `l·l` katalanisch). Die Text-Formen bleiben über ss01/ss02
erreichbar. Es ist nichts geschert oder von Hand umgezeichnet; beide Formen
sind Chialabs Zeichnung.

**Empfehlung: Upright-Formen als Grundform.** Die Kursive gehört dann
sichtbar zur Familie, das ɑ ist das Erkennungszeichen der Hausschrift
(Recherche, Lehre 8). Die Neigung allein unterscheidet genug. Die Text-Formen
wirken schreibschriftlicher und heben sich stärker ab; als Stilset bleiben sie
für Plakat und Titel verfügbar.

Nachzuarbeiten, falls eingebaut: Die Kerning-Klassen der Pro sind auf die
Text-Formen eingestellt; für ɑ und l nachziehen (gehört zu E2).

## 3 Mangel der Quelle

Im Bold-Italic-UFO (Commit `65ca1530`) fehlen 152 Glyphendateien (Versalien
A–N samt Akzenten und Listenzeichen), dazu `fontinfo.plist`; die
`layercontents.plist` verweist auf eine fehlende Hintergrundebene. Das Skript
füllt auf: 130 Glyphen aus der mitgelieferten `BoldItalic.woff2` (dort
punktgleich zum Master, geprüft an den vorhandenen Glyphen) oder als
Komponenten vom Regular; 21 Glyphen (B, D, G und ihre Akzente u. a.), bei
denen die woff2 beim Kompilieren Überlappungen entfernt hat, werden aus Thin
und Regular fortgeschrieben – für Klar 13 % über Regular hinaus, unsichtbar.
Für Deutlich und Laut braucht es die echten Master. Es lohnt sich, Chialab
darauf hinzuweisen (Issue im Repo); das ist eine Handlung nach aussen und
bleibt dem Inhaber überlassen.

## 4 Technik: eine Datei mit ital-Achse oder getrennte Datei

**Eine Variable mit wght und ital** (Muster Multa Pecunia): verlangt, dass
jede Glyphe in allen Mastern, aufrecht wie kursiv, punktgleich ist. Multa
Pecunia hat das, weil Aufrechte und Kursive aus derselben Linie gezeichnet
sind. Unsere Aufrechte stammt aus Titillium Upright, die Kursive aus der Pro –
andere Konturen. Ginge nur mit einer diskreten ital-Achse, die per
FeatureVariations ganze Glyphensätze tauscht: doppelte Dateigrösse, und
Browser wenden `font-style: italic` auf eine ital-Achse uneinheitlich an.

**Getrennte Dateien** (wie Google Fonts, Source Sans, Titillium Web VF): eine
Kursiv-Variable mit wght-Achse aus den drei Pro-Mastern (die Master sind
kompatibel; der Probe-Bau interpoliert schon daraus) plus die bestehende
aufrechte Variable. Im Web zwei `@font-face` mit derselben Familie und
`font-style: normal | italic`; der Browser wählt selbst. STAT verknüpft die
beiden für Grafikprogramme.

**Empfehlung: getrennte Datei.** Folgen:

- **Webfonts:** eine Datei dazu (Kursiv-Variable, woff2 ≈ 90 KB geschätzt,
  oder statisch Kursiv Klar ≈ 48 KB). `tokens.css` bekäme ein zweites
  `@font-face` «Goetheanum» mit `font-style: italic`.
- **Office-TTF (Trio):** heute ‹Goetheanum Schrift› = Klar (Regular) + Laut
  (Fett, ⌘B) + **Leise (Kursiv, ⌘I)**. Zwei Wege:
  a) Kursive als eigene Familie ‹Goetheanum Kursiv› neben Ruhig und Deutlich;
     ⌘I bleibt Leise. Kein Eingriff ins Trio, aber in Word keine Kursive auf
     Tastendruck.
  b) Quartett: Kursiv Klar auf ⌘I, Kursiv Laut auf ⌘B⌘I, Leise wird eigene
     Familie. Natürlicher in Office, ändert aber die Hausregel und jede Vorlage,
     die ⌘I als Leise nutzt.
- **Statische Schnitte:** mindestens Kursiv Klar; Kursiv Laut nur, wenn
  Weg b) gewählt wird (G01 erlaubt Laut-kursiv im Fliesstext ohnehin nicht).
- **Beschreibungen:** bei Einbau alle Stellen mitziehen (schriften.html,
  schrift-webfont.html, README, tools.json, Beipackzettel, Installer).

## 5 Regel, die widerspricht (melden, nicht umschreiben)

`$regeln` S01 und `typo-regeln.yaml`: «Die Goetheanum Schrift … führt keine
echte Kursive (Leise ist aufrechter Gegenton) … nicht vortäuschen.» Und
«Zitate in Leise». `base.css` setzt `em`/`i` auf Laut, nicht kursiv. Wird die
Kursive eingebaut, muss S01 neu gefasst werden; das entscheidet der Inhaber.

## 6 E5: Black-Probewort

Bild: `docs/befunde/black-probewort-e5-2026-10-31.svg` (Laut 680, Schreien
725, Fortschreibung auf Stamm 180 ≈ Gewicht 945; Skript
`tools/goetheanum-fontfix/proof_black_probewort.py`). Bis etwa Stamm 180 trägt
die lineare Fortschreibung; darüber laufen die Punzen von a und e zu – ein
Black müsste dort gezeichnet, nicht gerechnet werden.

## Entscheidvorlage für den Inhaber

1. **Einbauen?** Empfehlung: **ja**, als Kursiv-Variable in eigener Datei.
   Die Messung trägt «voll kompatibel» bei x-Höhe, Zeilenhöhe und Gewicht.
2. **Form:** Empfehlung: **Upright-Formen** (ɑ, gerades l) als Grundform,
   Text-Formen als ss01/ss02.
3. **Rollen:** Empfehlung: **Werktitel** und **Fremdwort** (dort ist heute
   nichts oder die Anführung, die mit Zitaten kollidiert). **Zitat** als Wahl
   zwischen Leise und Kursiv – im Specimen nebeneinander. **Lede: nein** – eine
   ganze Lede kursiv ist zu viel Stimme. Nie Betonung (G05 bleibt Laut).
4. **Office:** Empfehlung: zuerst **Weg a)**, eigene Familie, Trio unverändert;
   Weg b) erst, wenn die Kursive sich im Web bewährt hat.
5. **Regel S01** neu fassen, wenn 1 ja.

Bei ja folgt: Kursiv-Variable aus den drei Mastern (sobald der Bold-Master
vollständig ist), Kerning für ɑ/l, die 8 fehlenden Zeichen, Kapitälchen
entscheiden, Paket und Beschreibungen.
