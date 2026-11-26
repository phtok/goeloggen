# Befund E4: Goetheanum Serif Probe, Grenzen des Einsatzes (31. 10. 2026)

Etappe E4 aus `docs/recherche_titillium-pro.md`. Auftrag des Inhabers:
«die Serifschrift unbedingt testen und Grenzen des Einsatzes klären; ein
tolles Spielzeug für manche Sektion und Anwendung».

- Specimen (Treibhaus): https://werkzeuge.goetheanum.ch/schrift-serif-probe.html
- Probe-Font: https://github.com/phtok/goeloggen/tree/main/assets/fonts/proben/goetheanum-serif-probe
- Bauskript: https://github.com/phtok/goeloggen/blob/main/tools/goetheanum-fontfix/build_serif_probe.py

## Entscheidvorlage (das Wichtigste zuerst)

**Empfehlung: B, die Serif als Stimme für Zitat, Lede und Titel, nicht für
Mengentext.** Vorher eine kleine Ausbau-Etappe (S1, unten). Die Probe trägt
Display und Zitat ab 24 px schon jetzt schön; für Mengentext fehlen Fett,
Kerning und Akzente, und Source Sans 3 macht diese Arbeit heute besser.

| Option | Was | Aufwand | Empfehlung |
|---|---|---|---|
| A Spielzeug | bleibt im Treibhaus, kein Einsatz | keiner | nein: verschenkt, was schon trägt |
| **B Stimme** | Zitat, Spruch, Lede, Titel ab 24 px; zuerst Sektion für Schöne Wissenschaften, Wochenspruch im Seelenkalender | Etappe S1 (Akzente, Zeichen, Kerning aus der Sans Pro) | **ja** |
| C Lesefamilie | Mengentext statt Source Sans 3 | Fett, Kursive auf Upright-Logik, 600 Zeichen, Kerning, Ziffern: ein Schriftentwurf | nein, jetzt nicht; Chialabs zweite Serif abwarten |

**Zu entscheiden, je eine Frage:**

1. Option B freigeben? (Ja: S1 als nächste Etappe, danach Aufnahme der Rolle
   ‹Stimme Serif› ins Regelwerk; Nein: Probe bleibt im Treibhaus.)
2. Einstöckiges a als Grundform der Serif (wie in der Hausschrift)?
   Empfehlung ja: es liest sich als a, nicht als u, und bindet die Serif an
   die Upright-Logik.
3. Erste Sektion: Schöne Wissenschaften (Literatur, Sprache, Übersetzen)?
   Zweite Kandidatin: Redende und Musizierende Künste (Sprachgestaltung).

Die Hausregeln kennen heute zwei Schriften: Goetheanum als Stimme, Source
Sans 3 für Funktion und Daten (CLAUDE.md § Grenzen der Hausschrift). Eine
dritte Rolle ist eine Regeländerung; das Regelwerk ist nicht angefasst.

## Was gebaut wurde

`tools/goetheanum-fontfix/build_serif_probe.py`, aus der Quelle im Repo
(`tools/goetheanum-fontfix/sources/titillium-pro-serif-beta/`, Commit 65ca153
von https://github.com/chialab/titillium_pro/tree/serif), idempotent, zwei
Läufe bytegleich. Ausgabe nach `assets/fonts/proben/goetheanum-serif-probe/`,
**nicht** ins Paket.

- **Name:** «Goetheanum Serif Probe», Version 0.1 Probe. Titillium führt
  «Titillium» als Reserved Font Name (OFL § 3); die Probe trägt ihn nicht.
- **Umlaute:** Die Quelle hat 15 kombinierende Akzente, gezeichnet ist nur
  der Punkt (U+0307). Das Trema ist aus zwei Punkten gebaut: Mittenabstand
  210 (Hausschrift 190 bei schmalerem Punkt), 110 über der x-Höhe, über
  Versalien 110 über 700. Komponiert: ä ö ü ë ï ÿ Ä Ö Ü Ë Ï.
- **ß:** Form der Hausschrift (Klar; Stamm 81 zu 82 Einheiten, also gleich
  kräftig) mit dem Fuss-Serif des Serif-h. In der Kursiven um 16° geneigt.
- **Einstöckiges a (ss01):** Hausschrift-Logik, a = d ohne Oberlänge: Stamm
  des Serif-d flach auf 514 gekappt. Ein erster Versuch mit der Kopf-Fahne
  des u las sich im Bild als u («Huus») und ist verworfen.
- **Ligaturen:** nicht nötig. f-Bogen und i-Punkt berühren sich nicht; eine
  fi-Ligatur aus f und punktlosem i nahm dem i den Punkt und ist verworfen.
- **Leere Akzente aus der cmap:** Chrome zerlegt é in e + Akzent und fand die
  leere Akzent-Glyphe der Quelle: «Café» stand als «Cafe» da, ohne Warnung.
  Jetzt fallen é, è, à, ñ … als Ganzes in die Fallback-Schrift (sichtbar
  fremd, aber richtig). Gilt für jeden künftigen Ausbau: nie leere Akzente
  in der cmap lassen.
- **Leerzeichen:** U+00A0, U+202F, U+2009 und weiches Trennzeichen, damit
  ` ` und Trennung nicht in die Fallback-Schrift springen.
- Guillemets « » ‹ › und deutsche Anführung „ “ ‚ ‘ sind in der Quelle da <!-- typo-ok -->
  und stimmen.

## Gemessen und angeschaut

Seite in Chromium auf 1280 und 420 px, hell und dunkel, Schriftgrad mit
`getComputedStyle` gemessen (Mengentext 20 px, Lede 23,2, Titel 39,2,
Karte 16). `typo-check` und `ds-lint` grün (100 %), `barrierefreiheit.mjs`
ohne Verstoss (2 Messungen).

- **Masse:** x-Höhe 500, Versalhöhe 700 wie Hausschrift und Source. Stamm
  82 Einheiten = Klar. Serif-Platte 45 Einheiten.
- **Laufweite:** im Schnitt 0,458 em je Zeichen; Klar 0,409, Source 0,447
  (mit size-adjust 103 %). Die Serif läuft 12 % breiter als Klar.
  Weil `ch` an der Null der eigenen Schrift hängt und die Null der Serif breit ist (0,599 em, Source 0,512), passen in 62 ch 81 Zeichen (Source 71): für die Serif gilt **54 ch**
  als Lesemass, auf der Specimen-Seite so gesetzt.
- **Kontrast:** Farben unverändert aus den Tokens; Tinte auf Papier 15,0:1,
  `--muted` 4,9:1, dunkel 14,4:1 und 6,8:1, Weiss auf
  `--sek-ssw-dunkel` 7,5:1. Der Stamm ist so kräftig wie Klar; heikel ist
  nur die Platte: 45 Einheiten sind bei 16 px 0,72 px, bei 14 px
  0,63 px, also unter einem Bildpunkt.
- **Bild:** Ab 18 px ruhig und gut lesbar, hell wie dunkel; 16 px
  trägt einen Absatz; 14 und 15 px lesbar, aber die Serifen flimmern,
  auf dunklem Grund mehr. Titel und Zitat sind der stärkste Eindruck der
  Seite: die Serif klingt wärmer und älter als Deutlich, ohne fremd zu
  wirken, weil Masse und Breiten aus derselben Familie kommen.
- **Kursive:** schön im Zitat, aber Text-Form, nur 117 Zeichen, eigener
  Rhythmus. Die Hausregel «Leise statt Kursive» gilt weiter; die Kursive
  bleibt Probe.

## Grenzen des Einsatzes

**Grade (B02, B03).** Lesetext in der Serif ab 18 px (`--t-body`),
Lede ab 20, Zitat und Titel ab 24. Unter 16 px nie; Meta, Label,
Legende, Karte-Kleintext bleiben Source Sans 3, wie das Fundament es
schon verdrahtet. Auf farbigem Grund (B01) nur ab 24 px. Der Kurztext der Karte steht auf der
Specimen-Seite bewusst in 15–16 px Serif, als Gegenprobe unter der Grenze.

**Rollen.**
- Ja: Zitat und Spruch, Lede, Titel und Kopf einer Sektionsseite, Plakat-
  und Programmheft-Titel, Wochenspruch.
- Nein: Mengentext (kein Fett für Betonung nach G05, kein Kerning, keine
  Akzente; Source ist dafür da), UI, Formulare, Tabellen, Zahlen (keine
  tabellarischen Ziffern, G25).
- Nie gemischt im selben Absatz mit der Hausschrift (G01: zwei Merkmale).

**Sektionen und Anwendungen (Vorschlag, abgeglichen mit
https://werkzeuge.goetheanum.ch/sektionsfarben-goethe.html).**
Die Serif gehört dorthin, wo Sprache der Gegenstand ist: Sektion für Schöne
Wissenschaften (Literatur, Übersetzen; Kopf auf `--sek-ssw-dunkel`
gemessen), Sektion für Redende und Musizierende Künste (Sprachgestaltung,
Rezitation), der Wochenspruch im Seelenkalender
(https://werkzeuge.goetheanum.ch/apps/seelenkalender/), Zitate im
Newsletter. Nicht für Naturwissenschaft, Landwirtschaft, Medizin oder die
Werkzeuge selbst: dort spricht die Hausschrift.

**Was bis zur Nutzbarkeit fehlt.**

| Lücke | Wirkung heute | Weg | Etappe |
|---|---|---|---|
| Akzente é è à ç â ê î ô û ñ und Versal-Gegenstücke | Fallback-Glyphe im Wort («Café») | Akzente zeichnen (5 Formen), komponieren wie das Trema | S1 |
| & % € § @ + = × ° © ẞ | Fallback | aus der Hausschrift mit Serifen oder neu, rund 12 Zeichen | S1 |
| Kerning | «Ta», «Wa», «Te» klaffen ab 32 px | Breiten sind gleich wie in der Sans Pro: deren iKern-Paare für formgleiche Paare prüfen (E2 baut den Abgleich ohnehin) | S1 |
| Fett (Laut) | keine Betonung möglich, G05 nicht erfüllbar | zweiter Master; bei Chialab angekündigt, nicht geliefert | C |
| Kursive auf Upright-Logik | Text-Form | nach E1 entscheiden | C |
| Ziffern tnum, case, Brüche | keine Tabellen | Features ergänzen | C |
| Akzente in der Kursiven | fehlen ganz | wie S1 | S1 |

S1 ist eine überschaubare Etappe (Glyphen aus vorhandenen Teilen, Kerning
übernehmen), C ist ein Schriftentwurf.

## Offen

- [ ] Entscheid Inhaber zu den drei Fragen oben.
- [ ] Bei B: Etappe S1 (Akzente, Zeichen, Kerning), danach Rolle ins
      Regelwerk (`goetheanum-typo-tokens.json`, CLAUDE.md § Grenzen).
- [ ] Chialab beobachten: zweite Serif und Gewichte (mit der halbjährlichen
      Beobachtung aus der Recherche).

## Mischung und Lesbarkeit im Mengentext, gemessen (25. 11. 2026)

Rückmeldung des Inhabers (25. 11.): ‹In der Probe fehlt die Mischung:
grotesker Titel und Serifen im Mengentext sowie umgekehrt. Wie lesbar
schätzt du diese Serif-Variante ein?› Neuer Abschnitt ‹Mischung› auf
https://werkzeuge.goetheanum.ch/schrift-serif-probe.html#mischung: Sektionsseite,
Artikel, Zitat im Text, je in drei Wegen (Titel Hausschrift + Text Serif ·
Titel Serif + Text Hausschrift · Titel Serif + Text Source). Lesemass der
Serif jetzt **30em** (66 Zeichen bei 0,458 em je Zeichen) statt 54ch – nie
in `ch` (Skill `lesbarkeit` § 4).

### Messung

Metrik aus der Datei (`tools/lesbarkeit-metrik.py`, x-Höhe flach):

| | Klar 440 | Serif Probe | Source Sans 3 |
|---|--:|--:|--:|
| x-Höhe flach | 500 | 500 | 486 (×1,03) |
| Strich | 81 | 82 | 82 |
| Strich/x-Höhe | 0,162 | 0,164 | 0,169 |
| o/x (Offenheit) | 0,792 | 0,908 | 0,926 |
| a–z im Mittel | 443 | 509 | 475 |
| 0/O (1 = gleich) | 0,979 | 0,837 | 0,748 |
| Kerning (`kern`) | ja | **nein** | ja |
| Zeichen in der cmap | 677 | **118** | – |

Am gerenderten Blatt (Chromium, deviceScaleFactor 1, Mengentext aus
‹Mischung› und ‹Mengentext›; Zeichen je Zeile = Median, letzte Zeile mit):

| | Grad | Zeilenhöhe | Zeichen/Zeile 375 px | 1280 px | Grauwert 1280 |
|---|--:|--:|--:|--:|--:|
| Serif Probe | 18,1 / 20 px | 1,66 | 35 | 60 | 0,081 · 0,076 |
| Hausschrift Klar | 18,1 / 20 px | 1,66 | 40 | 63 | 0,081 · 0,077 |
| Source Sans 3 | 18,1 / 20 px | 1,66 | 36 | 61 | 0,081 · 0,075 |

Grauwert = Tintenanteil im Absatzrechteck (Bildschirmfoto, Graustufen),
je Absatz. Barrierefreiheit (`barrierefreiheit.mjs --seite`): kein Verstoss.

### Einschätzung (belegt, wo Zahl; Erfahrungswert, wo keine)

1. **Die Buchstaben tragen Mengentext.** Gleiche x-Höhe, gleicher Strich,
   gleicher Grauwert wie Klar und Source; offen gezeichnet wie Source
   (o/x 0,91), viel offener als Klar (0,79). Klars Schwäche im langen Text
   ist ihre Enge (Entscheid 5. 11.); diese Schwäche hat die Serif nicht.
2. **Die Ausstattung trägt ihn nicht.** Kein Kerning, 118 Zeichen, keine
   Akzente (é, à, ñ fallen aus der Schrift), kein Fett (Betonung nach G05
   unmöglich). Das ist kein Lesbarkeits-, sondern ein Satzproblem, aber es
   verhindert jeden echten Mengentext.
3. **Breit.** 15 % breiter als Klar, 7 % breiter als Source: am Telefon 35
   Zeichen je Zeile (Klar 40, Source 36) – unter G10, wie alle drei.
4. **Platte unter einem Bildpunkt.** 45 Einheiten = 0,81 px bei 18 px,
   0,90 px bei 20 px: bei 1× werden die Serifen als Graustufen gemalt; bei
   2× (Telefon, Retina) 1,6–1,8 px und sauber (Medium, Skill § 7).
5. **Mischung, angeschaut:** ‹Titel Serif + Text Source› ist der stimmigste
   Weg – Gegensatz in der Form, beide offen, Source bringt mit, was der Serif
   fehlt. ‹Titel Hausschrift + Text Serif› kehrt die Rollen um (die laute
   Stimme klein, die warme gross) und wirkt wie zwei Häuser. ‹Text
   Hausschrift + Zitat Serif› trägt: das Zitat bekommt eine zweite Stimme
   ohne zweites Merkmal im Absatz (G01 betrifft nur Auszeichnung im
   Fliesstext; das abgesetzte Zitat ist eigene Ebene).

**Urteil:** Lesbar ja, setzbar nein. Für Mengentext auf dem Bildschirm
schätze ich sie nach S1 (Kerning, Akzente) ab 20 px und auf 2×-Schirmen so
lesbar wie Source; ungemessen bleibt die Lesegeschwindigkeit (kein Lesetest,
Skill `lesbarkeit` § 9). Empfehlung unverändert **B (Stimme)**, mit dem
Mischweg ‹Titel und Zitat Serif, Text Source›.

## Entscheid des Inhabers (25. 11. 2026)

‹Die Serif überzeugt mich im Bild gar nicht. Ich würde sie funktional nicht
integrieren, nur als Ergänzung anbieten. Goetheanum Serif Beta.›

- Umbenannt in **Goetheanum Serif Beta** (Familie, Dateien, Ordner
  `assets/fonts/proben/goetheanum-serif-beta/`, Skript
  `build_serif_beta.py`), dazu ein ZIP (zwei OTF, OFL, README), bytegleich
  gebaut.
- Angeboten auf https://werkzeuge.goetheanum.ch/schriften.html#download als
  Karte ‹Ergänzung› und auf der Treibhaus-Seite.
- **Keine Rolle im Regelwerk** (Option B entfällt), nicht im Paket. Die
  Fragen 1–3 der Entscheidvorlage oben sind damit erledigt; S1 nur, wenn die
  Beta später gebraucht wird.

## Display-Ausbau, Fassung 0.2 (26. 11. 2026)

Entscheid des Inhabers (26. 11.): ‹als Möglichkeit im Display anbieten.
Entsprechend optimieren.› Display heisst Titel und grosse Grade, nicht
Lesetext. Gebaut ist S1, auf Titel zugeschnitten
(`build_serif_beta.py PFAD/titillium_pro`, zwei Läufe bytegleich):

| | 0.1 | 0.2 |
|---|--:|--:|
| Zeichen | 118 | 300 |
| Kerning-Paare aufrecht | 0 | 9 316 |
| Kerning-Paare kursiv | 0 | 10 900 |

- **Akzente:** Marken der Titillium Sans Pro, gesetzt über deren Anker,
  umgerechnet auf die Mitte des Serif-Buchstabens im selben Höhenband
  (Ogonek: rechte Kante). Punkt und Trema bleiben die der Serif. Lettische
  Cedille als Komma unten. Ohne: ď ľ ť ģ (Hakenform), Ł Ø Æ Œ Đ.
- **Zeichen:** & % ‰ € $ £ ¢ ¥ § ¶ @ © ® + = × ÷ ± ° · • † ‡ aus der Pro
  (Strich 78 zu 82). In der Kursiven um die halbe x-Höhe geneigt, sonst
  rutscht der Mittelpunkt aus der Mitte. ẞ: Pro-Form mit Fuss- und
  Kopf-Serife des Serif-B.
- **Kerning:** Die Breiten der Serif sind andere als in der Pro (Befund
  oben, ‹Breiten gleich›, stimmt nicht: 0 von 117 gleich). Darum gelten die
  Pro-Werte nur als Formkorrektur, und nur die schliessenden (≤ −10).
  **Kollisionswache:** je Höhenband von 25 Einheiten bleiben mindestens 40
  Einheiten Luft; 344 Paare aufrecht, 877 kursiv zurückgenommen. Gemessen
  (HarfBuzz): Ta −91, LT −112, P. −107, AV −42, «Y −48.
- **Angeschaut** bei 110 px: ‹Ta›, ‹P.›, ‹«Y›, ‹AVA› schliessen; ‹Tú› hält
  105 Einheiten Luft zwischen Arm und Akzent (wie in der Pro).

**Offen, zu entscheiden:** ein zweites Gewicht für Titel neben Deutlich (die
Quelle hat nur eines; ein eigener Master wäre ein Schriftentwurf), und ob
`ss01` (einstöckiges a) in der Beta Standard wird.
