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
- Guillemets « » ‹ › und deutsche Anführung „ “ ‚ ‘ sind in der Quelle da
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
