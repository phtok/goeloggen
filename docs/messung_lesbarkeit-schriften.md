# Goetheanum Schrift und Source Sans 3, gemessen

Stand 31. 10. 2026. Anwendung des Skills `project-skills/lesbarkeit/` auf
beide Schriften. Gemessen, nicht geschätzt: Werte aus den Schriftdateien
(`tools/lesbarkeit-metrik.py`) und aus dem gerenderten Blatt (Chromium,
Playwright, Kafka-Texte aus `apps/lesetest/texte.js`). Keine Regel geändert.

**Das Wichtigste zuerst**

- **Gleich dunkel.** Mit dem `size-adjust` aus `tokens.css` haben Klar und
  Source Sans 3 bei gleichem Grad dieselbe x-Höhe und fast denselben Strich.
  Bei 14 px wird keine von beiden dunkler als die andere. Ein Grauwert-Grund
  für den Wechsel zu Source unter 18 px besteht **nicht**.
- **Der Unterschied ist die Form.** Klar läuft eng (o/x 0,79 gegen 0,93) und
  unterscheidet **0 und O nicht** (gleich breit, 0,98). Source zeichnet die
  Null schmal (0,75). I und l sind in **beiden** nur an der Höhe zu
  unterscheiden.
- **`ch` lügt.** 62ch fassen in Klar 87 Zeichen, in Source 71. Wer in `ch`
  setzt, setzt die Hausschrift ein Viertel zu breit (bestätigt
  `docs/schriften-verteilung.md`).
- **W8 geklärt:** 486 und 498 sind beide richtig, aber nicht dasselbe Mass.
  486 ist die flache x-Höhe (Oberkante x, OS/2), 498 die Oberkante des o mit
  Überhang. Fassung 3.052 in beiden Repos.

## 1. Aus der Datei (Tausendstel em)

`python3 tools/lesbarkeit-metrik.py` auf die Webfonts v2.8 und Source Sans 3
3.052 (statisch, `assets/fonts/goetheanum/Fallback/`).

| Schnitt | x flach | x rund | Strich | Strich/x | o/x | a–z | 0/O |
|---|--:|--:|--:|--:|--:|--:|--:|
| Goetheanum Ruhig 350 | 500 | 510 | 65 | 0,130 | 0,78 | 439 | 0,97 |
| Goetheanum Klar 440 | 500 | 510 | 81 | 0,162 | 0,79 | 443 | 0,98 |
| Goetheanum Deutlich 580 | 500 | 511 | 107 | 0,214 | 0,82 | 450 | 0,99 |
| Source Sans 3 Regular 400 | 486 | 498 | 82 | 0,169 | 0,93 | 475 | 0,75 |
| Source Sans 3 SemiBold 600 | 491 | 503 | 115 | 0,234 | 0,95 | 492 | 0,76 |

Lesart: **Strich/x** ist das Gewicht relativ zur Grösse der Kleinbuchstaben,
**o/x** die Breite der Rundung (offen, ruhig) relativ zur x-Höhe, **a–z** der
mittlere Vorschub (ohne die Laufweite von 0,02 em der Hausschrift),
**0/O** die Verwechselbarkeit von Null und O.

**W8 im Einzelnen.** `tokens.css` rechnet `size-adjust: 103%` aus 500/486,
flach gegen flach. Martha in `designs` (texter/SITZUNG-SCHRIFTEN.md) las 498,
die runde Oberkante. Rund gegen rund ergibt 510/498 = 102,4 %, also dieselbe
Angleichung im Rahmen eines halben Prozents. Der Wert in `tokens.css` steht.
Für Vergleiche gilt: flach gegen flach, und die Messweise dazuschreiben.

## 2. Im Grad (px, nach `size-adjust`)

Source Sans 3 mit 103 %, Hausschrift ohne Angleichung.

| Grad | x-Höhe beide | Strich Klar | Strich Source | Strich Deutlich |
|--:|--:|--:|--:|--:|
| 14 | 7,0 | 1,13 | 1,18 | 1,50 |
| 15 | 7,5 | 1,22 | 1,27 | 1,61 |
| 16 | 8,0 | 1,30 | 1,35 | 1,71 |
| 18 | 9,0 | 1,46 | 1,52 | 1,93 |
| 20 | 10,0 | 1,62 | 1,69 | 2,14 |

Klar und Source liegen bei 14 px knapp über 1,1 px Strich; Deutlich hat
bei 14 px den Strich, den Klar erst bei 18–19 px erreicht.

## 3. Am Blatt: wie dunkel wird der Strich

Zeile ‹Hamburgefonstiv Illegal 1l0O Wirkung›, schwarz auf weiss, Chromium,
Anteil der Schriftpixel, die mindestens 85 % Deckung erreichen (‹voll›).

| Grad | Klar 1× | Source 1× | Deutlich 1× | Klar 2× | Source 2× | Deutlich 2× |
|--:|--:|--:|--:|--:|--:|--:|
| 14 | 0,19 | 0,20 | 0,37 | 0,50 | 0,51 | 0,60 |
| 16 | 0,30 | 0,30 | 0,40 | 0,56 | 0,55 | 0,62 |
| 18 | 0,32 | 0,34 | 0,44 | 0,57 | 0,57 | 0,67 |
| 20 | 0,37 | 0,35 | 0,48 | 0,61 | 0,62 | 0,68 |

Klar und Source liegen bei jedem Grad innerhalb von 0,02. Deutlich bei 14 px
ist so dunkel wie Klar und Source bei 20 px. Der Sprung zur doppelten Dichte
(Telefon, Retina) ist grösser als jeder Schnitt- oder Schriftwechsel.

## 4. Zeichen je Zeile

Median der vollen Zeilen, Kafka-Prosa (4000 Zeichen), Zeilenhöhe 1,66.
Hausschrift mit 0,02 em Laufweite, wie `body`.

| Grad | Breite | Klar | Deutlich | Source |
|--:|---|--:|--:|--:|
| alle | 62ch | 87 | 85 | 71 |
| 14 | 600 px | 101 | 100 | 97 |
| 16 | 600 px | 88 | 87 | 85 |
| 18 | 600 px | 77 | 77 | 74 |
| 20 | 600 px | 70 | 68 | 67 |
| 14 | 358 px (Telefon) | 59 | 58 | 57 |
| 16 | 358 px | 51 | 51 | 49 |
| 18 | 358 px | 45 | 45 | 44 |
| 20 | 358 px | 40 | 40 | 39 |

Bei gleicher Breite fasst Klar 3–4 % mehr Zeichen als Source; das ist
wenig. Der grosse Unterschied entsteht allein durch `ch`: die Null der
Hausschrift ist 597 breit, die von Source 497.

Für 66 Zeichen (G10, Ziel) braucht Klar bei 18 px rund 515 px, Source rund
535 px. Auf dem Telefon (358 px Satzbreite) liegt jede der beiden Schriften
bei 16–20 px unter 45 Zeichen, also unter dem unteren Rand von G10.

## 5. Zeichen, die sich verwechseln

Gerendert bei 14–20 px, 1× und 2×.

- **0 und O:** in der Hausschrift gleich breit (597 zu 610), am Blatt nicht
  zu unterscheiden. In Source deutlich: Null schmal.
- **I und l:** in beiden Schriften ein senkrechter Strich; die Hausschrift
  unterscheidet nur an der Höhe (691 zu 716), Source ebenso.
- **1:** in beiden mit Fahne, unterscheidbar.

Folge für Daten (Codes, IBAN, Kennungen, Zahlen mit Buchstaben): die Grenze
in `base.css` (Werte in Source) hat damit einen gemessenen Grund. Für I/l
hilft keine der beiden Schriften; dort hilft nur der Zusammenhang.

## Vorschlag an den Inhaber (nicht entschieden)

Nicht im Regelwerk; der Inhaber entscheidet (CLAUDE.md § Wenn eine Regel
der Schrift widerspricht).

| | Hausschrift (Klar) | Source Sans 3 |
|---|---|---|
| **Länge** | bis ein Absatz am Stück (rund 100 Wörter) | ab dem zweiten Absatz Fliesstext |
| **Grad** | Lesetext ab 16 px; darunter nur einzeilig, dann Deutlich | mehrzeiliger Text unter 16 px |
| **Inhalt** | Sprache | Daten mit Ziffern und Buchstaben (0/O) |
| **Medium** | Bildschirm wie oben; Office und Druck vorläufig gleich | ebenso |

Begründung: Der Grauwert trennt die Schriften nicht (§ 3), die Form schon:
Klar ist eng und gleichförmig (o/x 0,79), das trägt Stimme und kurze Texte;
über viele Zeilen hinweg ist offenere Form der übliche Grund für eine
Lese-Grotesk. Die Längengrenze ist damit ein **Erfahrungswert**, kein
Messwert; nur ein Lesetest könnte sie belegen.

Folgen, falls angenommen: W1 entschieden (beides, nach Länge), W2 braucht
ein eigenes Mass für die Hausschrift in Zeichen, W6 entschieden (unter 16 px
einzeilig Deutlich).

## Was diese Messung nicht sagt

- Ob man in Klar langsamer oder ermüdeter liest als in Source. Das misst
  nur ein Lesetest mit Menschen (`apps/lesetest/`, liegt).
- Wie die Schriften in Office und im Druck (pt, andere Rasterung) wirken.
- Wie sie im Dunkeln wirken; gemessen wurde nur schwarz auf weiss.
- Wie Menschen mit Sehschwäche oder Legasthenie sie lesen.

## So wiederholen

```bash
python3 tools/lesbarkeit-metrik.py assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.8-Klar.woff2 assets/fonts/goetheanum/Fallback/SourceSans3-Regular.woff2
```

Zeichen je Zeile und Graustufe: Rezept in
`project-skills/lesbarkeit/SKILL.md` § Prüfschritte. Zum Anschauen:
https://werkzeuge.goetheanum.ch/apps/schriftgrenze/
