# Lesbarkeit: der Bestand aus allen Repos

Stand 31. 10. 2026. Auftrag des Inhabers: alle Repos auf Skills und
Recherchen zur Lesbarkeit durchsehen, als Grundlage für ein
Lesbarkeits-Skillset und eine klare Grenze zwischen der Goetheanum Schrift
und Source Sans 3. Diese Etappe sammelt nur. Nichts ist neu erfunden, keine
Regel geändert.

**Das Wichtigste zuerst**

- **Es gibt keinen Lesbarkeits-Skill.** Der einzige Skill im Haus, der als
  Muster taugt, ist `formular-ux`.
- **Es gibt keine gemessene Grenze.** Alle Zahlen zur Schriftwahl nach Grad
  und Länge sind Hausentscheide oder Erfahrungswerte. Der Lesetest, der sie
  messen soll, ist gebaut, aber nicht ausgewertet.
- **Die Regeln widersprechen einander** an acht Stellen (§ Widersprüche).
  Am schwersten wiegt: Ist der Fliesstext in der Hausschrift oder in
  Source Sans 3?
- Gesichtet: 11 Repos, 33 Fundstücke (Nr. 1–33, dazu ein Sammeleintrag für Repos ohne Fund). Funde nur in `goeloggen`, `designs`,
  `fragenbank` und den beiden Kopien `rsa-web`/`rsa-prototyp`.

## Wie gelesen wurde

Durchsucht wurden alle elf Repos (flach geklont) nach Skills
(`SKILL.md`, `project-skills/`, `.claude/skills/`, `.agents/skills/`),
Recherchen (`recherche_*.md`, `docs/`, `befunde/`), Regelwerken
(Typo-Tokens, `contract.json`, `typo-regeln.yaml`) und den Stichworten des
Auftrags. Die Art je Fundstück: **Regel** (verbindlich oder entschieden),
**Recherche** (Quellen gelesen), **Skill**, **Befund** (am Ding gemessen
oder beobachtet), **Prüfer** (Maschine).

**Belegt** heisst hier: die Zahl hat eine Quelle, die man öffnen kann (URL,
Messung mit Datum, Entscheid mit Datum). **Erfahrungswert** heisst: im Repo
steht die Zahl ohne Quelle.

## Fundstücke

### goeloggen (angehängt)

Basis aller URLs: https://github.com/phtok/goeloggen/blob/main/

**1. `CLAUDE.md` § Barrierefreiheit B01–B05 und § Grenzen der Hausschrift** (Regel)
https://github.com/phtok/goeloggen/blob/main/CLAUDE.md
Die Hausschrift trägt alles, was als Sprache gelesen wird, auch den
Fliesstext; Source Sans 3 trägt Funktion und Daten (Label, Wert, Meta,
Badge, Formularfelder, Tabellen). Lesbarkeit kommt im Lesetext aus den
Faktoren, nicht aus einem Schriftwechsel.
Zahlen: Fliesstext ≥16 px, Standard 18–20 px; Meta ≥15; nichts Lesbares unter
14; Eingabefelder ≥16 px; Fingerziele ≥44 px; Zeilenhöhe Lesetext ≥1.5
(Hausschrift ≥1.6, `--lh-body` 1.66); Lesemass ~62ch; Kontrast 4.5:1 und 3:1.
Quelle der Zahlen: Hausentscheid; WCAG 2.2 SC 2.5.8 (24 px) und 1.4.12 sind
genannt, ohne URL. Kontrastwerte sind WCAG 1.4.3/1.4.11.

**2. `assets/typografie/goetheanum-typo-tokens.json`** (Regel)
https://github.com/phtok/goeloggen/blob/main/assets/typografie/goetheanum-typo-tokens.json
G09 ‹magisches Viereck› (Schriftwahl, Zeilenlänge, Zeilenabstand, Umraum
hängen zusammen), G10 Zeilenlänge 45–75 Zeichen, Ziel ~66 (neun Wörter),
G11 Zeilenabstand 1.4–1.6 wächst mit dem Mass, G25 Ziffern, G27 drei
Lesesituationen (Lese, Konsultation, Schau). S01 Schriftwahl: Lesetext in
Klar 440, Source Sans 3 nur für ‹langen immersiven Mengensatz›.
Zahlen: 45–75 und ~66 Zeichen ohne Quelle (Erfahrungswert); `ch` gegen
Zeichen ‹empirisch gezählt› (39ch = 66 Zeichen in der Hausschrift).

**3. `assets/typografie/typo-regeln.yaml`** (Regel, ausführbar)
https://github.com/phtok/goeloggen/blob/main/assets/typografie/typo-regeln.yaml
Dieselben Regeln G09–G11, G25, G27 als Erkennen/Korrektur. Keine zusätzlichen
Zahlen.

**4. `design-system/type-scale.json` und `tools/check-type-scale.py`** (Regel und Prüfer)
https://github.com/phtok/goeloggen/blob/main/design-system/type-scale.json
https://github.com/phtok/goeloggen/blob/main/tools/check-type-scale.py
Die einzige Stelle, die die Schriftwahl nach Grad festlegt. TS1: Hausschrift
unter 18 px braucht Gewicht ≥580 (Deutlich). TS2: Leise (265) als Lesetext
erst ab 22 px. Rollen mit Mindestgrad: Fliesstext 18 (Schrift
‹display-oder-source›), Lede 18, Meta/Label/Readout 15 (Source), Beiwerk 14,
Kicker 13.5, Knopf 14.5, Titel 22. Leitsatz: ‹Leichte und schwere Gewichte
verschlechtern das Lesen, die Mitte ist optimal.›
Zahlen: 18/22 px ‹nach Beier›, aber ohne Titel, Jahr oder URL einer
Beier-Arbeit im Repo. Als Erfahrungswert behandeln.

**5. `design-system/tokens.css` und `design-system/base.css`** (Regel, Umsetzung)
https://github.com/phtok/goeloggen/blob/main/design-system/tokens.css
https://github.com/phtok/goeloggen/blob/main/design-system/base.css
Skala: `--t-micro` 14, `--t-small` 15–16, `--t-body` 18–20, Lede 20–23;
`--lh-body` 1.66, `--lh-min` 1.5, `--measure` 62ch. Source Sans 3 mit
`size-adjust: 103%` (‹500/486›) auf die x-Höhe der Hausschrift gehoben.
Hausschrift hat 0.02em Laufweite (‹hilft Lese-/Kleingraden, Beier›). Im
Dunkeln bleibt das Hell-Gewicht (‹B7›). Der Kommentarblock ‹Die Schrift-Grenze›
wiederholt CLAUDE.md. Quelle der Zahlen: Hausentscheid und Messung der
x-Höhe (500 gegen 486).

**6. `design-system/CHANGELOG.md`** (Befund, Ledger)
https://github.com/phtok/goeloggen/blob/main/design-system/CHANGELOG.md
Entscheide mit Begründung: Floor von 13 auf 14 px angehoben, Eingabefelder
16 px (iOS-Zoom), Kartenzeile 15–16 px bei Zeilenhöhe 1.5 und 4.9:1, ein
Frage/Antwort-Block ‹in einer Stimme› statt Hausschrift plus Grotesk (Mass
`min(48ch,100%)` = 63 Zeichen gemessen, Durchschuss 1.6 breit / 1.5 schmal),
die Grotesk erscheine bei gleichem Grad ‹optisch grösser›. Das ist die
einzige Stelle, an der eine Hausschrift-Source-Mischung am gerenderten Blatt
beurteilt wurde. Quelle: Auftraggeber-Urteil, Messung in Chromium.

**7. `typografie.html`** (Regel, gesetztes Referenzdokument)
https://github.com/phtok/goeloggen/blob/main/typografie.html
Die Hausschrift sei ‹Werk- und Auszeichnungs-Grotesk, kein Buchsatz›, ohne
echte Kursive. Lesbarkeit als Gleichgewicht der vier Ecken. 45–75 Zeichen,
Zeilenabstand 1.5–1.6, ‹nie unter 1.5 (B04)›. Spalte 39ch ≈ 66 Zeichen.

**8. `assets/fonts/goetheanum/Fallback/README.md`** (Regel, Entscheid)
https://github.com/phtok/goeloggen/blob/main/assets/fonts/goetheanum/Fallback/README.md
Source Sans 3 ist als ‹Lese-/Begleitschrift für langen Mengentext›
entschieden. Griechischer und kyrillischer Mengentext läuft in Source Sans 3
selbst. Begründung: Praxis auf goetheanum.ch (Titillium plus Source).
Keine Messung.

**9. `schrift-vergleich.html`** (Recherche, Kandidatenvergleich)
https://github.com/phtok/goeloggen/blob/main/schrift-vergleich.html
Vier Lese-Groteske live im Kontext: Source Sans 3, IBM Plex Sans, Atkinson
Hyperlegible (‹auf maximale Lesbarkeit gezeichnet›), Inter. Der Vergleich ist
visuell, ohne Messwerte.

**10. `docs/schriften-verteilung.md`** (Befund, Stand der Etappe)
https://github.com/phtok/goeloggen/blob/main/docs/schriften-verteilung.md
Offene Office-Regel (Hausschrift für Titel, Lede, Fliesstext; Source für
Tabellen, Felder, Legenden, Fussnoten), deren Fliesstext-Grenze der
Lesetest liefern soll. Messbefund: 62ch ergeben in der Hausschrift **89
Zeichen** je Zeile (die Null ist breit, `ch` misst sie), in Source 70.
`--measure` sei für Hausschrift-Fliesstext ‹rund ein Viertel zu breit›, nicht
geändert. Telefon: Klar etwa 50, Source etwa 46 Zeichen je Zeile. Stamm bei
400 px: Klar 33, Source 34 px. Quelle: eigene Messung, 31. 10. 2026.

**11. Lesetest `apps/lesetest/` und `services/lesetest/schema.sql`** (Werkzeug, nicht ausgewertet)
https://github.com/phtok/goeloggen/tree/main/apps/lesetest
https://github.com/phtok/goeloggen/blob/main/services/lesetest/schema.sql
Hausschrift gegen Source Sans 3 je Textlänge (≈80/250/500/1000 Wörter),
acht Kafka-Texte mit LIX 33–49, drei Fragen je Text, Ausschluss unter 40 oder
über 800 Wörtern je Minute. Es liegt kein Ergebnis vor; im Repo steht als
Plan ‹nach 20–30 Durchgängen auswerten›. Der Inhaber hat den Test als zu
aufwendig zur Seite gelegt.

**12. `project-skills/formular-ux/SKILL.md`** (Skill, Muster für den Aufbau)
https://github.com/phtok/goeloggen/blob/main/project-skills/formular-ux/SKILL.md
Aufbau: je Regel eine Quelle in Klammern (Hausregel-ID oder URL), am Ende
‹Was wir nicht belegen können›. Streift die Lesbarkeit nur an den Rändern:
Felder in Source 16 px, Containerhöhen gegen WCAG 1.4.12
(https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html), Fingerziel
(https://www.nngroup.com/articles/touch-target-size/), Eingabezoom
(https://docs.squirrelscan.com/rules/mobile/input-zoom). Dazu die Recherche
`docs/recherche_spendenformular-ux.md`, aber ohne Schriftbezug.

**13. `docs/recherche_titillium-pro.md`** (Recherche, Schriftfamilie)
https://github.com/phtok/goeloggen/blob/main/docs/recherche_titillium-pro.md
Familienvergleich von Titillium-Ableitungen (Titillio u. a.), Lizenzen,
Features. Nennt x-Höhe 500 und Versalhöhe 700 auf 1000. Keine
Lesbarkeitsmessung.

**14. `assets/fonts/goetheanum/AUDIT.md` und `README.md`** (Befund, Technik)
https://github.com/phtok/goeloggen/blob/main/assets/fonts/goetheanum/AUDIT.md
https://github.com/phtok/goeloggen/blob/main/assets/fonts/goetheanum/README.md
Metrikfehler (Zeilenhöhe in Apps aufgebläht auf 2.17×, jetzt behoben),
Ziffernsätze (`pnum`, `tnum`, `onum`, echte Mediävalziffern fehlen), keine
echte Kursive. Wirkt auf die Lesbarkeit im Satz, ist aber keine
Lesbarkeitsregel.

**15. Prüfmaschinen** (Prüfer)
https://github.com/phtok/goeloggen/blob/main/tools/barrierefreiheit.mjs
https://github.com/phtok/goeloggen/blob/main/tools/ds-lint.py
https://github.com/phtok/goeloggen/blob/main/design-system/contract.json
DS03 (Grössen-Untergrenze), DS08 (axe-core auf 390 und 1440 px, WCAG 2.2 AA).
Messen Kontrast, Zielgrösse, Umbruch; sie messen **nicht**, ob ein Satz
leicht gelesen wird.

### designs (Haus RSA, Texter, Lesepult)

Basis: https://github.com/phtok/designs/blob/main/. Hier ist die Hausschrift
**Inclusive Sans** (‹nach Beier & Ford-Williams›), nicht die Goetheanum
Schrift. Was dort gemessen wurde, gilt für das Verfahren, nicht für die
Zahlen.

**16. `lesepult/docs/leseforschung.md`** (Recherche, mit Quellen)
https://github.com/phtok/designs/blob/main/lesepult/docs/leseforschung.md
Die einzige Stelle mit zitierten Studien. (a) Clinton-Lisell & Litzinger
2026, Netzwerk-Metaanalyse, 56 Stichproben, 79 Effektgrössen: Papier besser
als Bildschirm, **aber der Unterschied hängt am Scrollen**, paginiert am
besten (https://link.springer.com/article/10.1007/s10639-025-13843-8).
(b) THERIF, Cai et al. 2023: Grad, Zeilenfall und Breite hängen
voneinander ab, drei zusammenhängende Satzbilder statt freier Regler
(https://arxiv.org/abs/2303.04221). (c) Wallace et al. 2022, ACM TOCHI:
die **bevorzugte** Schrift ist nicht verlässlicher die schnellste, ‹Geschmack
ist kein Messwert› (https://dl.acm.org/doi/10.1145/3502222). Umgesetzt:
Satzbreite endet beim Hausmass 52 ch.

**17. `rsa/design-system/syntax-am-schirm.md`** (Recherche und Befund, gemessen)
https://github.com/phtok/designs/blob/main/rsa/design-system/syntax-am-schirm.md
Massgebend ist die x-Höhe je Geviert (aus `OS/2`, auf 1000 normiert):
Inclusive 500, Syntax Sans 512, Syntax Serif 498. Serif-Fliesstext bei
einfacher Pixeldichte: 16 px trägt, 14 px knapp, **12 px wird grau und
brüchig**; bei doppelter Dichte trägt alles. Folge: ‹Die Serif trägt den
Lesetext, die Grotesk trägt alles Kleine.› Kapitälchen: ohne Minuskeln fehlt
das Wortbild. Quelle: eigene Messung und Rendering, 15./16. 9. 2026. Die einzige
Messung im Haus, die Grad und Medium (Pixeldichte) verbindet.

**18. `texter/SITZUNG-SCHRIFTEN.md` und `texter/pruefung/fremde-schriften.html`** (Befund, gemessen)
https://github.com/phtok/designs/blob/main/texter/SITZUNG-SCHRIFTEN.md
https://github.com/phtok/designs/blob/main/texter/pruefung/fremde-schriften.html
Angleich von Ergänzungsschriften über die x-Höhe: `size-adjust: 93.3%` für
Noto an Inclusive. Tabelle, Tausendstel em, Schnitt 400: x-Höhe Inclusive
500, Noto 536, **Source Sans 3 498**, Ubuntu Sans 518; Strich zu x-Höhe
0,168 / 0,164 / 0,165 / 0,145; Breite ο zu x-Höhe 1,16 / 1,13 / 1,07 / 1,13.
Source Sans 3 ‹läuft schmaler›. Das ist das Verfahren, mit dem sich die
Goetheanum Schrift und Source Sans 3 vergleichen liessen.

**19. `rsa/contract.json` (K4, K10) und `rsa/design-system/erklaert.md`** (Regel und Prüfer)
https://github.com/phtok/designs/blob/main/rsa/contract.json
https://github.com/phtok/designs/blob/main/rsa/design-system/erklaert.md
K4 Mindestgrad 0.75 rem / 12 px (‹vgl. Goetheanum-DS: min. 14px›). K10
Zeilenmass 45–75 Zeichen, Optimum um 66, **im Browser gemessen** auf 390, 844
und 1440 px mit `tools/zeilenmass.mjs`. K3 Flattersatz. Quelle: System B
R08 (Satzspiegel), selbst ohne URL.

**20. `MARKE.md`, `rsa/marke.json`, `rsa/system-b/index.html`** (Regel, R05 und R10/R11)
https://github.com/phtok/designs/blob/main/MARKE.md
https://github.com/phtok/designs/blob/main/rsa/marke.json
https://github.com/phtok/designs/blob/main/rsa/system-b/index.html
R05: Inclusive Sans ‹nach Beier & Ford-Williams' Lesbarkeitskriterien›: keine
spiegelnden Formen, weite Öffnungen, grosszügige Laufweite, ‹für Mengentext
gemacht›, hohe x-Höhe. Mass 52 ch. Die Berufung auf Beier und Ford-Williams
steht ohne Titel und Jahr.

**21. `schreibpult/KONZEPT.md`** (Regel)
https://github.com/phtok/designs/blob/main/schreibpult/KONZEPT.md
R10/R11 ‹Das Mass ist eine harte Grenze: 60–65 Zeichen, überall›; man
schreibt in der Zeilenlänge, in der gelesen wird. Zahl ohne Quelle.

**22. `rsa/design-system/barrierefreiheit.md` und `barrierefreiheit-systeme.md`** (Befund, gemessen)
https://github.com/phtok/designs/blob/main/rsa/design-system/barrierefreiheit.md
https://github.com/phtok/designs/blob/main/rsa/design-system/barrierefreiheit-systeme.md
Erstmessung K11 mit axe-core: nur zwei Kriterien hängen an der Fensterbreite.
Rundumlauf 3 Systeme × 2 Klimata × 2 Breiten × 15 Schirme = 180 Messungen,
24 Funde, alle `color-contrast` (z. B. 1.84:1, 2.52:1, 3.33:1). Lehren:
Scroll-Einblendungen, Tageszeit und verdeckte Flächen verfälschen die
Messung. Grenze: etwa ein Drittel der WCAG-Kriterien ist maschinell prüfbar.

**23. `rsa/vision/BEFUNDE.md`** (Befund, Inhaberurteil)
https://github.com/phtok/designs/blob/main/rsa/vision/BEFUNDE.md
15. 9. 2026, Inhaber: Alle Entwürfe gingen ‹an die Grenzen der Lesbarkeit,
sehr kleine und sehr feine Typo-Elemente in der Mobilansicht›. Gemessen:
**3024 Stellen unter 14 px**, hängen an einem Wert; `--grad-fein` und
`--grad-klein` fallen mobil auf 0,94 rem (15 px) zusammen. Zwei Ausreisser mit
12,5 px behoben. Dazu 20. 9.: verlorene Worte auf letzten Zeilen,
schlecht ausgeglichene Absätze, Zwischentitel zu klein.

**24. `rsa/design-system/silbentrennung.md`** (Regel, Lehre)
https://github.com/phtok/designs/blob/main/rsa/design-system/silbentrennung.md
Wann getrennt wird und wann nicht: Titel, Namen, kurze Zeilen nie;
höchstens zwei getrennte Zeilen übereinander. Verweist auf das Typolexikon,
ohne URL. Gilt für das Haus RSA.

**25. `TEXTER.md`, `texter/README.md`, `texter/ETAPPEN.md`** (Befund, Umsetzung)
https://github.com/phtok/designs/blob/main/TEXTER.md
https://github.com/phtok/designs/blob/main/texter/README.md
Druck und Office: Satzspiegel im Lesemass 112 mm, ‹rund 64 Zeichen›; ein
Zeilenabstand 1.55 auf 10,5 pt (16,275 pt) wechselte beim Umsetzen in Word
und RTF. Das ist die einzige Messung im Haus zum Satz in **pt**, nicht in px.

**26. `rsa/design-system/system-a-bestand.md`** (Befund, Druck)
https://github.com/phtok/designs/blob/main/rsa/design-system/system-a-bestand.md
Jahresbericht in Syntax: 10/13 pt, Zeilenabstand durchgehend 13,0 pt, ‹Faktor
1,30›. Druckwert als Gegenstück zu den Bildschirm-Zeilenhöhen 1.5–1.66.

**27. `sks/entwuerfe/schriftkabinett.html`** (Recherche, Kandidatenvergleich)
https://github.com/phtok/designs/blob/main/sks/entwuerfe/schriftkabinett.html
Tabelle von Textschriften mit Urteil. Inclusive Sans: ‹auf Lesbarkeit
gezeichnet, I, l und 1 klar unterschieden, offene Formen›, aber geneigte
statt echter Kursive und fehlende Ziffernvarianten (Urteil ‹raus› für diesen
Zweck, 14. 10. 2026). Space Grotesk ‹niedrigste x-Höhe im Feld›.

**28. `luzifer/assets/lesepult.css`, `luzifer/assets/leser.js`** (Umsetzung)
https://github.com/phtok/designs/blob/main/luzifer/assets/lesepult.css
`--lesemass: 52ch`, einstellbar im Leser. Umsetzung des Hausmasses, keine
eigene Quelle.

**29. `strategieraum/wissen/quellen.json` und `referenzen/17-recherche-kreation-und-werkzeugwahl.md`** (Recherche, Randfund)
https://github.com/phtok/designs/blob/main/strategieraum/wissen/referenzen/17-recherche-kreation-und-werkzeugwahl.md
Hemingway-Hilfe (https://hemingwayapp.com/help/docs/readability): englische
Lesestufen sind **keine** validierte Bewertung für Deutsch; für deutsche
Texte eine eigene redaktionelle Prüfroutine. Betrifft Textverständlichkeit,
nicht Schrift.

**30. `testteam/berichte/2026-08-05-vision-testcouch.md`** (Befund, Randfund)
https://github.com/phtok/designs/blob/main/testteam/berichte/2026-08-05-vision-testcouch.md
Satz: ‹Wir haben ein Mass für Lesbarkeit und keines für Wirkung.› Bestätigt,
dass nur Zeilenlänge, Mindestgrad und Kontrast gemessen werden.

### fragenbank

**31. `docs/usability-test-2026-08/emil.md` und `MASSNAHMEN.md`** (Befund, einzige Lesergruppe)
https://github.com/phtok/fragenbank/blob/main/docs/usability-test-2026-08/emil.md
https://github.com/phtok/fragenbank/blob/main/docs/usability-test-2026-08/MASSNAHMEN.md
Persona Emil, 74, altersbedingte Sehschwäche. Gemessene Grössen: «anonym?»
11.2 px, Rechtstext 12 px, Hinweise 12.48 px, Meta 13.6 px; Kontrast 2.4:1,
2.54:1, 3.89:1 gegen die geforderten 4.5:1. Fragetexte 33–57.6 px bei etwa
15:1 bestehen. Zoom 200 % bestanden. Folgerung der Test-Session: Meta und
Erklärtexte mindestens ~14 px und 4.5:1. Hinweis: der Tester ist eine
**Persona** des Testteams, keine Person.

### rsa-web, rsa-prototyp

**32. `contract.json`, `design-system/barrierefreiheit.md`, `CONTRIBUTING.md`** (Kopien von Nr. 19 und 22)
https://github.com/phtok/rsa-web/blob/main/design-system/barrierefreiheit.md
https://github.com/phtok/rsa-prototyp/blob/main/design-system/barrierefreiheit.md
Kopien der `designs`-Regeln (K4, K10, K11). Kein eigener Befund.

### ifaep

**33. `src/app/globals.css`** (Erfahrungswert)
https://github.com/phtok/ifaep/blob/main/src/app/globals.css
Zeilenhöhe 1.6 im Fliesstext, 1.7 an anderer Stelle, 1.2 für Titel. Ohne
Regel und Quelle.

### Ohne Fund

**34. `ohr`, `faustweb-deploy`, `mantren`, `vodojo`, `goelinks`**
Kein Lesbarkeitsmaterial. `ohr` trifft nur das Wort ‹Zeilenlänge› im Sinn von
Satzlänge (`vestimenta/gegenlese-3-auswertung.md`). `mantren`, `vodojo`,
`goelinks` und `faustweb-deploy` tragen nur den Skill `i-have-adhd`, der die
Antwortform regelt, nicht die Schrift. `fragenbank` führt zusätzlich nur
Supabase-Skills.

## Widersprüche

Die Reihenfolge folgt dem Gewicht. Jeder Widerspruch nennt beide Seiten mit
Fundstück. Entscheiden muss der Inhaber (CLAUDE.md § Wenn eine Regel der
Schrift widerspricht).

**W1. Wer setzt den Fliesstext: die Hausschrift oder Source Sans 3?**
- Hausschrift: `CLAUDE.md` § Grenzen (Nr. 1), Kommentarblock in `base.css`
  (Nr. 5), CHANGELOG-Entscheid ‹Fliesstext in der Hausschrift› (Nr. 6),
  `typo-tokens` S01 ‹Lesetext in Klar› (Nr. 2).
- Source Sans 3: `typo-tokens` Mass `zeilenlaenge` (‹Lesetext läuft jetzt in
  Source statt in der schmalen Display-Grotesk›; Nr. 2), `Fallback/README.md`
  (‹Lese-/Begleitschrift für langen Mengentext›; Nr. 8), `.prose` in
  `base.css` und `prinzipien.html` (‹echter Mengentext darf in Source›).
- Unentschieden: `type-scale.json` Rolle Fliesstext = ‹display-oder-source›
  (Nr. 4).
- Dazu: Die Hausschrift ist laut `typografie.html` (Nr. 7) ‹kein Buchsatz›,
  laut CLAUDE.md aber die Schrift des Fliesstextes. Die Berufung auf Beier
  (‹auf Lesbarkeit gezüchtet›, Nr. 20) gilt dem **Haus RSA und Inclusive
  Sans**, nicht der Goetheanum Schrift.

**W2. Das Zeilenmass in der Hausschrift.**
`--measure: 62ch` (‹~66 Zeichen in Source›, Nr. 5), G10 `min(39ch)` = 66
Zeichen (Nr. 2, 7), CHANGELOG `min(48ch)` = 63 Zeichen (Nr. 6), CLAUDE.md
‹~62ch› für die Hausschrift (Nr. 1). Gemessen 31. 10.: **62ch = 89 Zeichen
in der Hausschrift**, 70 in Source (Nr. 10). Dasselbe Wort ‹62ch› bedeutet
je nach Schrift 70 oder 89 Zeichen; die Einheit sollte Zeichen sein, nicht
`ch`.

**W3. Die Zeilenhöhe im Lesetext.**
CLAUDE.md: Hausschrift-Fliesstext ≥1.6, `--lh-body` 1.66 (Nr. 1). G11/Token:
1.4–1.6, Wert 1.5 (Nr. 2). B04: ≥1.5 (Nr. 1). `typografie.html`: 1.5–1.6,
‹nie unter 1.5›. Der Entscheid vom 18. 10. ‹B04 geht vor G11› ist notiert,
löst aber nur die Untergrenze. Offen bleibt, ob 1.6 oder 1.66 Pflicht ist
und ob 1.4 (G11 unten) noch erlaubt ist.

**W4. Der Mindestgrad.**
CLAUDE.md: nichts Lesbares unter 14 (B03). `base.css` Kommentar: ‹nichts
Lesbares unter 13 (B03)›, Kicker 13.5. `type-scale.json`: Kicker 13.5, Knopf
14.5, Beiwerk 14. `tokens.css`: `--t-micro` 14. Das Schwesterhaus `designs`
K4: 12 px, ‹vgl. Goetheanum-DS: min. 14px›. Die Tabelle in `base.css` führt
noch 13.5 und 17–19 im Kopfkommentar; der Code steht auf 14 und 18–20.

**W5. Der Fliesstextgrad.**
CLAUDE.md B03 Standard 18–20 px (Nr. 1), `tokens.css` 18–20 (Nr. 5), `base.css`
Kommentar und Rollentabelle ‹17–19› (Nr. 5), `type-scale.json` Minimum 18
(Nr. 4), `schrift-vergleich.html` 19. Der Lesetest stellt `--t-body` ein.

**W6. Wie klein darf welcher Schnitt der Hausschrift sein?**
CLAUDE.md: kleine UI-Schrift mindestens Klar, Titel Deutlich, kleine Labels
nie Leise (Nr. 1). `type-scale.json` TS1: unter 18 px **Deutlich (≥580)**,
nicht Klar (Nr. 4). `typo-tokens` S01: Klar ist ‹das Minimum für kleine
Marginalien›, Legenden und Zitate in Leise, ‹nie kleiner als der Lesetext›
(Nr. 2). TS2: Leise erst ab 22 px. Drei Mindestwerte für dasselbe Objekt.

**W7. Gleiche Kürzel, andere Regeln.**
B01–B05 in CLAUDE.md (Kontrast, Grösse, Fingerziele) gegen B1–B7 in
`base.css`, `tokens.css` und `type-scale.json` (Typo-Leiter nach Beier: B2
Deutlich unter 18 px, B3 Laufweite, B4 `size-adjust`, B6 Leiter, B7
Dunkelgewicht). ‹B04› heisst in CLAUDE.md Fingerziel und Zeilenhöhe, in
`tokens.css` daneben ‹B4› die x-Höhen-Angleichung. Wer ‹nach B3› schreibt,
meint je nach Datei etwas anderes.

**W8. Die x-Höhe von Source Sans 3.**
`tokens.css`: `size-adjust: 103%` aus ‹500/486›, also x-Höhe Source **486**
(Nr. 5). `designs` Martha: Source Sans 3 **498** bei Schnitt 400 (Nr. 18). Die
Versionen oder Messweisen unterscheiden sich; welche Zahl für die
Vergleichsseite gilt, ist offen.

## Lücken

Was für eine klare Schriftgrenze fehlt. Gesucht in dieser Reihenfolge: das,
was das Skillset zuerst braucht.

**L1. Eine gemessene Grenze. Es gibt nur Entscheide.**
Alle Grenzen (18 px, 22 px, ‹langer Mengentext›) sind Hausentscheide oder
Erfahrungswerte. Der Lesetest (Nr. 11) wäre die Messung, hat aber kein
Ergebnis. Vergleichsseite und Messung am Blatt fehlen noch.

**L2. Grad.**
Es fehlt die Antwort: Ab welchem Grad trägt die Hausschrift noch Text, und
ab welchem Grad muss Source übernehmen? Vorhanden: TS1 (<18 px Deutlich),
Floor 14 px, Mindestgrade je Rolle. Nicht vorhanden: eine Messung der
Hausschrift bei 14–17 px, Klar gegen Deutlich, 1× gegen 2× Pixeldichte
(die einzige vergleichbare Messung betrifft Syntax Serif, Nr. 17).

**L3. Textlänge.**
Fehlt: ab wie vielen Wörtern am Stück die Hausschrift ermüdet. Vorhanden:
‹ein paar Zeilen sind kein Problem, echter Mengentext darf in Source›
(CLAUDE.md), ohne Zahl. Lesetest sieht 80/250/500/1000 Wörter vor.

**L4. Medium.**
Bildschirm Desktop, Telefon, Papier/Druck, Office-Dokument (Punktgrad), E-Mail,
Folie, Plakat. Vorhanden: Zeilenmass im Browser auf drei Achsen (K10),
Druck-Satz des Jahresberichts (10/13 pt, Nr. 26), Texter 10,5 pt/1.55 (Nr. 25).
Fehlt: eine Pt-Grenze für die Hausschrift in Office, eine Dunkelmodus-Messung,
Mails (nur Schriftstapel in `tools/mail_fontstack.py`, keine Lesbarkeit).

**L5. Lesergruppe.**
Alter, Sehschwäche, Legasthenie, Lesen in der Zweitsprache, Kinder, müde
Leser. Vorhanden: eine **Persona** (Emil, 74, Nr. 31), WCAG 1.4.12 als
Textabstand-Probe, Zoom 200 %. Fehlt: jede Messung mit echten Lesenden;
**zu Legasthenie/Dyslexie findet sich in keinem Repo etwas**; zu Kindern
nichts; zu älteren Lesenden nur Nr. 31.

**L6. Quellenlage zu Beier.**
TS1/TS2, B2, B3 und R05 berufen sich auf Beier und Ford-Williams, aber kein
Repo nennt Titel, Jahr oder URL. Die Grenzwerte 18 und 22 px sind damit
nicht überprüfbar. Zu klären, welche Arbeit gemeint ist, bevor die Zahlen in
einen Skill gehen.

**L7. Studienlage.**
Die einzigen zitierten Studien (Nr. 16) betreffen Scrollen, Satzbilder und
Schriftpräferenz, nicht Display- gegen Lese-Grotesk. Fehlt: Literatur zu
x-Höhe, Laufweite und Strichstärke bei kleinen Graden; zu Zeilenabstand und
Zeilenlänge (die Hausnorm 45–75 / 66 ist ohne Quelle); zu Kursive, Versalien
und Betonung durch Gewicht (G01/G05 sind Hausregeln).

**L8. Die Hausschrift selbst.**
Es fehlt eine Zeichenprüfung für Verwechslungen (I/l/1, 0/O) in der
Hausschrift (Inclusive Sans hat sie, Nr. 27), die Prüfung der Ziffernsätze im
Fliesstext, die Laufweite bei erhöhtem Textabstand (WCAG 1.4.12) auf
gerenderten Seiten und die Wirkung von Klar (440) gegen Laut (680) als
Betonung im Lesetext.

**L9. Fremde Schriftsysteme.**
Mengentext in Griechisch/Kyrillisch läuft in Source Sans 3 (Nr. 8); für
Hebräisch, Georgisch, Armenisch, CJK sind Kandidaten gesammelt (docs
`schriften-verteilung.md`), nicht auf Lesbarkeit gemessen.

**L10. Das Gerüst des Skills.**
Vorlage `formular-ux` hat Quelle je Regel und Abschnitt ‹nicht belegbar›. Für
ein Lesbarkeits-Skillset fehlen Prüfschritte am gerenderten Blatt
(Playwright-Rezept steht in `CLAUDE-REF.md` § Seite anschauen) und ein
Messverfahren für x-Höhe und Zeichen je Zeile; das Verfahren aus Nr. 18
(x-Höhe, Strich, Breite in Tausendstel em) und Nr. 10 (Zeichen je Zeile
zählen statt `ch`) wäre die Grundlage.
