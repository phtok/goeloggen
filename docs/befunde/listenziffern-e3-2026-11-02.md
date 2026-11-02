# Befund: Listenzeichen in Kreis und Quadrat (Etappe E3)

Stand: 2. 11. 2026. Auftrag: Etappe E3 aus `docs/recherche_titillium-pro.md`
(Entscheid des Inhabers vom 31. 10. 2026). Anschauung:
https://werkzeuge.goetheanum.ch/listenzeichen.html · Bau:
`tools/goetheanum-fontfix/build_v29_listen.py` (liest v2.9 aus git, idempotent,
zweiter Lauf bitgleich geprüft).

![Listenzeichen: vier Formen, Flüstern bis Schreien](listenziffern-e3-2026-11-02.png) <!-- typo-ok -->

## Ergebnis

| Stilset | Form | Inhalt |
|---|---|---|
| `ss03` | Kreis, Kontur | A–Z, 0–9, 10–99 |
| `ss04` | Kreis, gefüllt | A–Z, 0–9, 10–99 |
| `ss05` | Quadrat, Kontur | A–Z, 0–9, 10–99 |
| `ss06` | Quadrat, gefüllt | A–Z, 0–9, 10–99 |

Je Stilset 56 Glyphen: 36 fertige Zeichen (wie die Pro) und 20 Bausteine für
10–99 (erste Ziffer mit linker, zweite mit rechter Hälfte). Dazu 52 fertige
Paare für Unicode. Zusammen 276 Glyphen, 98 Codepunkte (569 → 667):
`⓪ ①–⑳ ㉑–㊿ Ⓐ–Ⓩ` zeigen `ss03`, `⓿ ❶–❿ ⓫–⓴` zeigen `ss04`. Quadrate und
gefüllte Buchstaben gibt es in Unicode nur ausserhalb der BMP (`🄰 🅐 🅰`,
teils als Emoji gezeigt); sie bleiben Stilset.

## Formen

- **Kreis bleibt Kreis** (Entscheid des Inhabers am 2. 11. während der Arbeit):
  10–99 stehen im selben Kreis bzw. Quadrat wie ein Einzelzeichen. Eine
  erste Fassung setzte zwei Ziffern in eine Pille (Kreis in die Breite
  gezogen); verworfen. Die Paarziffern sind dafür gleichmässig kleiner
  (0,495 statt 0,66), nie gestaucht.
- **Grösse:** Kreis 860 Einheiten, Quadrat 800 (wirkt daneben gleich gross),
  Mitte auf halber Versalhöhe (345). Im Fliesstext mit Zeilenhöhe 1,66 bleibt
  der Kreis in der Zeile (−85 bis 775). Die Pro zeichnet ihre Stilset-Kreise
  mit 1208 Einheiten weit über die Zeile hinaus; das Haus nicht.
- **Inneres Zeichen:** das Hauszeichen selbst, auf 0,66 verkleinert, im
  gleichen Gewicht. Formgleich mit der Pro sind Versalien und Ziffern ohnehin
  (E2); die Upright-Formen betrifft es nicht. Ziffern lining.
- **Strich der Kontur** = Strich des verkleinerten Zeichens (0,66 × Stamm des
  I): 24 in Flüstern, 54 in Klar, 91 in Schreien. Er wächst mit dem Gewicht;
  die Pro hält ihn fest.
- **Gefüllt:** Fläche mit ausgespartem Zeichen. Die Tinte nimmt darum mit dem
  Gewicht ab; das Prüfmass verlangt für diese Glyphen jetzt fallende Fläche.
- **Luft:** mindestens 45 Einheiten zwischen Zeichen und Innenkante. Wo das
  nicht reicht, wird das Zeichen schmaler, ein Faktor für alle Gewichte:
  Kreis M × 0,87, Kreis W × 0,80 und 0,93 kleiner, Quadrat W × 0,96, Quadrat
  Q 0,94 kleiner. J und Q (Unterlänge) sind nach der Tinte gemittelt.
  Die Pro hat W, M, Q im Kreis neu gezeichnet und lässt sie den Rand berühren.
- **Naht** der Bausteine liegt in der Mitte, beide Hälften überlappen um 16
  Einheiten; bei 23 bis 200 px angesehen, keine Haarlinie.

## Technik

- Die Paarregel steht im Stilset selbst (nicht in `calt`), damit sie nur
  greift, wenn das Stilset an ist: Ziffer + Ziffer, ohne Ziffer davor und
  danach (zwei `ignore`-Regeln). `123` bleibt `①②③`. Eingaben sind alle
  Ziffernformen (`tnum`, `onum`, `zero` …). Mit HarfBuzz geprüft.
- Gebaut einmal an den sechs Mastern der Variable; die statischen Schnitte
  erhalten die Instanz der Variable an ihrem Gewicht (deckungsgleich).
- FeatureList jetzt nach Tag sortiert (auch das `ccmp` aus E2).
- Prüfmass `proof_variable_axis.py --alle`: 929 Glyphen, 0 Verstösse.

## Fassung statt neuer Version

Dateinamen bleiben **v2.9**, intern **Version 2.91** (`head.fontRevision`,
`name` 3/5). Gründe: nur Ergänzung, kein vorhandenes Zeichen und kein Mass
geändert, versandte Mails und rund 90 Einbindungen bleiben gültig. «2.10»
wäre als Zahl kleiner als 2.9 und würde von Betriebssystemen und Office als
ältere Datei gelesen; 2.91 wird als neuer erkannt. Webfonts gleichen Namens
können im Browser-Zwischenspeicher alt bleiben; die Anschauungsseite lädt
darum mit `?v=2.91`.

## Offen

- Paarziffern (0,495) sind kleiner als Einzelziffern (0,66), wie bei
  Unicode `⑨ ⑩`. Für eine Karte, auf der 1–99 gleich gross wirken sollen,
  liesse sich ein fünftes Stilset mit allen Ziffern in Paargrösse bauen –
  nur bei Bedarf.
- Office: Stilsets kann Word (Schriftart › Erweitert), PowerPoint nicht;
  dort helfen die Unicode-Zeichen `①–㊿`.
