---
name: lesbarkeit
description: Lesbarkeit von Schrift und Satz im Goetheanum prüfen – Grad, Schnitt, Zeilenmass, Zeilenhöhe, Kontrast, Medium, Verwechslungszeichen – und entscheiden, wo die Goetheanum Schrift trägt und wo Source Sans 3. Diesen Skill laden bei jeder Frage ‹ist das lesbar?›, bei jeder Seite oder Vorlage mit Fliesstext, bei Schriftwahl, Grad- oder Mass-Entscheiden, beim Vergleich zweier Schriften und bei Beschwerden über zu kleine oder zu feine Schrift. Jede Regel mit Quelle; Belegtes getrennt von Erfahrungswerten; offene Widersprüche gekennzeichnet; Prüfschritte am gerenderten Blatt.
---

# Lesbarkeit im Haus

Lesbar heisst: man liest, ohne an die Schrift zu denken. Dieser Skill sagt,
was dafür gilt, woher es kommt, und wie man es **misst statt schätzt**.
Jede Regel hat eine Quelle in Klammern: Hausregel-ID, Datei oder URL. Was
keine hat, steht in § 9. Offene Widersprüche heissen **W1–W8** und sind
**nicht entschieden**; der Inhaber entscheidet (CLAUDE.md § Wenn eine Regel
der Schrift widerspricht).

Grundlagen: Bestand `docs/recherche_lesbarkeit-bestand.md` (33 Fundstücke,
W1–W8, L1–L10), Messung `docs/messung_lesbarkeit-schriften.md`,
Blick-Werkzeug https://werkzeuge.goetheanum.ch/apps/schriftgrenze/

## 1. Die zwei Schriften, gemessen

Aus `docs/messung_lesbarkeit-schriften.md` (31. 10. 2026, Tausendstel em):

| | Klar 440 | Deutlich 580 | Source Sans 3 400 |
|---|--:|--:|--:|
| x-Höhe flach | 500 | 500 | 486 (×1,03 = 500) |
| Strich/x-Höhe | 0,16 | 0,21 | 0,17 |
| Breite o/x-Höhe | 0,79 | 0,82 | 0,93 |
| Zeichen in 62ch | 87 | 85 | 71 |
| 0 und O | gleich | gleich | unterscheidbar |

- Nach `size-adjust: 103%` sind Klar und Source **gleich gross und gleich
  dunkel** (Messung § 3). Wer Source ‹weil kleiner Grad› wählt, braucht einen
  anderen Grund als den Grauwert.
- Klar ist **eng** gezeichnet (o/x 0,79), Source offen (0,93).
- Klar unterscheidet **0/O nicht**. Codes, Kennungen, IBAN: Source
  (`base.css` § Schrift-Grenze; Messung § 5).

## 2. Wer trägt was (gilt heute)

- Hausschrift: alles, was als Sprache gelesen wird – Titel, Kicker, Lede,
  Fliesstext, Hinweise (CLAUDE.md § Grenzen der Hausschrift).
- Source Sans 3 (`--font-text`): Label, Wert, Meta, Legende, Badge, Chip,
  Formularfeld, Tabelle; dazu ‹echter Mengentext› in `.prose` (CLAUDE.md;
  `design-system/base.css`).
- Griechisch und Kyrillisch im Lesetext: Source Sans 3 (Hausschrift deckt sie
  nicht; `assets/fonts/goetheanum/Fallback/README.md`).
- **Offen W1:** Ob Fliesstext grundsätzlich Hausschrift oder Source ist,
  widerspricht sich im Bestand (CLAUDE.md und S01 gegen
  `typo-tokens` Mass, `Fallback/README.md`, `type-scale.json`
  ‹display-oder-source›). Bis zum Entscheid: CLAUDE.md folgen und den
  Widerspruch nennen.

## 3. Grad

- Fliesstext ≥16 px, Standard 18–20 (`--t-body`) (B03).
- Meta und Label ≥15 (`--t-small`); nichts Lesbares unter 14 (`--t-micro`) (B03).
- Eingabefelder ≥16 px, sonst zoomt iOS (B03; Skill `formular-ux`).
- Grösse bis 200 % ohne Verlust (WCAG 1.4.4,
  https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html).
- Kleine Hausschrift mindestens Klar, Titel Deutlich, nie Leise klein (CLAUDE.md).
- **Offen W4:** Mindestgrad 14 (CLAUDE.md, `tokens.css`) gegen 13/13.5
  (Kommentar `base.css`, Kicker in `type-scale.json`).
- **Offen W5:** Fliesstext 18–20 (CLAUDE.md, `tokens.css`) gegen 17–19
  (Kopfkommentar `base.css`).
- **Offen W6:** Hausschrift unter 18 px: Deutlich (TS1,
  `design-system/type-scale.json`) oder Klar (CLAUDE.md, S01)?
  Messung: Deutlich bei 14 px ist so dunkel wie Klar bei 20 px.

## 4. Zeilenmass

- In **Zeichen** zählen, nie in `ch`: `ch` misst die Null, und die ist in der
  Hausschrift breit (Messung § 4; `docs/schriften-verteilung.md`).
- 45–75 Zeichen, Ziel um 66 (G10, `assets/typografie/goetheanum-typo-tokens.json`).
- Auf dem Telefon fasst die Zeile bei 16–20 px 40–51 Zeichen; das ist unter
  G10 und unvermeidlich – nicht den Grad senken, um die Zahl zu erreichen
  (Messung § 4; B03 geht vor).
- **Offen W2:** `--measure: 62ch` ergibt in der Hausschrift 87 Zeichen, in
  Source 71. Dasselbe Token, zwei Masse. Nicht still ändern.

## 5. Zeilenhöhe, Laufweite, Umbruch

- Lesetext ≥1.5 (B04, WCAG 1.4.8 ist AAA, 1.4.12 fordert, dass 1.5 nichts
  zerstört: https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html).
- Hausschrift-Fliesstext ≥1.6, `--lh-body` 1.66 (CLAUDE.md).
- Container in `ch`/`%`/`em`, nie feste px-Höhen (B04, WCAG 1.4.12).
- Hausschrift 0,02 em Laufweite (`design-system/tokens.css`).
- Titel `text-wrap: balance`, Fliesstext `pretty`; feste Leerzeichen zwischen
  Zahl und Wort (CLAUDE.md § Umbrüche).
- **Offen W3:** 1.4–1.6 (G11) gegen ≥1.5 (B04) gegen ≥1.6/1.66 (CLAUDE.md).
  Entschieden ist nur: B04 geht vor G11 (18. 10.).

## 6. Kontrast und Grund

- Lesetext ≥4.5:1, grosse Schrift und Ränder ≥3:1 (B02; WCAG 1.4.3,
  https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- Auf Farbe Weiss, nie Schwarz (B01). Hell/Dunkel nur aus Tokens (B05).
- Im Dunkeln bleibt das Hell-Gewicht (B7 in `tokens.css`). **Offen W7:**
  B01–B05 (CLAUDE.md) und B1–B7 (`tokens.css`, `type-scale.json`) sind
  verschiedene Regeln mit fast gleichen Kürzeln; immer die Datei dazusagen.

## 7. Medium

- Pixeldichte wiegt mehr als die Schriftwahl: bei 2× wird jede Schrift
  dunkler als jede andere bei 1× (Messung § 3). Im Zweifel an 1× prüfen.
- Druck und Office: noch keine Messung (L4). Bekannt nur aus `designs`
  (Syntax 10/13 pt, Texter 10,5 pt/1.55); nicht auf die Hausschrift übertragen.

## 8. Prüfschritte am Blatt

Die Maschine prüft die Regel, das Auge das Gewicht (CLAUDE.md). Rezept:
`CLAUDE-REF.md` § Seite anschauen. Zwei Breiten, **1280** und **420**.

1. **Metrik der Schrift** (einmal je Schriftfassung):
   `python3 tools/lesbarkeit-metrik.py DATEI …` – x-Höhe flach und rund,
   Strich, o/x, Vorschub, 0/O. Flach gegen flach vergleichen; die Messweise
   immer mitschreiben (W8 war ein Messweisen-Unterschied, 486 flach, 498 rund).
2. **Grad und Schnitt messen:** `getComputedStyle(el).fontSize` und
   `.fontWeight` am Lesetext, an Meta, Label, Knopf. Gegen § 3.
3. **Zeichen je Zeile zählen** (nicht `ch`): je Absatz Zeichen mit
   `Range.getClientRects()` den Zeilen zuordnen, letzte Zeile weglassen,
   Median. Fertig in `apps/schriftgrenze/schriftgrenze.js`
   (`zeichenJeZeile`). Gegen § 4.
4. **Zeilenhöhe:** `lineHeight / fontSize` ≥ § 5.
5. **Kontrast und Barrierefreiheit:** `node tools/barrierefreiheit.mjs
   --seite PFAD` (DS08).
6. **Anschauen:** Screenshot beider Breiten, hell und dunkel; dazu bei
   kleinen Graden `deviceScaleFactor: 1` (Medium § 7). Gleich Wichtiges
   gleich gross? Einzelwort in der Schlusszeile?
7. **Verwechslung:** Kommen Codes, Zahlen mit Buchstaben, 0/O vor? Dann
   Source (§ 1).

Befund mit Regel-ID und `Datei:Zeile` melden, offene W nennen statt lösen.

## 9. Was wir nicht belegen können

Als **Erfahrungswert** führen, nie als Studie ausgeben:

- die Grenzen 18 px (TS1) und 22 px (TS2) ‹nach Beier›: kein Titel, kein
  Jahr, keine URL im Haus (L6);
- 45–75 Zeichen und das Ziel 66 (G10): Hausnorm ohne Quelle (L7);
- dass die Hausschrift bei langem Text ermüdet und Source nicht – kein
  Lesetest ausgewertet (L1, L3);
- ab wie vielen Wörtern ‹echter Mengentext› beginnt (L3);
- ‹Leichte und schwere Gewichte verschlechtern das Lesen›
  (`type-scale.json`, ohne Quelle);
- dass Source bei gleichem Grad ‹optisch grösser› wirkt (CHANGELOG,
  Auftraggeber-Urteil; gemessen ist die x-Höhe gleich);
- jede Aussage zu älteren Lesenden ausser der Persona Emil (fragenbank), zu
  Legasthenie, Kindern, Zweitsprache (L5);
- jede Pt-Grenze für Office und Druck (L4).

Belegt sind nur: WCAG-Kriterien (oben verlinkt), die eigenen Messungen
mit Datum (`docs/messung_lesbarkeit-schriften.md`,
`docs/schriften-verteilung.md`) und die drei Studien in
`designs/lesepult/docs/leseforschung.md` (Scrollen, Satzbilder,
Schriftpräferenz – keine zu Display gegen Lese-Grotesk).

Wer eine dieser Fragen klären will: messen, Ergebnis in `docs/` mit Datum.
