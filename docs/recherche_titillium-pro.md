# Recherche: Titillium Pro und Verwandte — was die Hausschrift davon lernen kann

Stand: 31. 10. 2026. Anlass: Chialab (Bologna) pflegt seit 2023 eine
«Titillium Pro» samt Serif-Prototyp. Frage des Inhabers: Was lernen oder
übernehmen wir, wie sehen die Serif-Experimente aus, ist die
Upright-Variante einbezogen?

Die Hausschrift Goetheanum ist aus **Titillium Upright** abgeleitet
(`assets/fonts/goetheanum/AUDIT.md`, `tools/goetheanum-fontfix/sources/`).
«Upright» heisst bei Titillium die ruhige Buchstabenfamilie: einstöckiges a,
gerader y-Schwanz, aufrechter g-Abstrich, schlichtes t. Die verbreitete
«Text»-Form (Titillium Web auf Google Fonts) hat zweistöckiges a und
gebogenes y.

## Befund Titillium Pro (Chialab)

Repo: https://github.com/chialab/titillium_pro — Branch `main` = Sans Pro,
Branch `serif` = Serif-Prototyp. Lizenz OFL. Letzter Commit 4. 2. 2026.
Redesign und Mastering Antonio D'Elisiis, Kerning Igino Marini (iKern),
mit Segen der Accademia di Belle Arti di Urbino (April 2023).

- **Titillium Sans Pro:** 12 Schnitte Thin–Black samt Kursiven, 607 Zeichen
  (Quelle Upright: 454). Features: calt, case, dlig, frac, liga, locl,
  pnum/tnum, sinf/sups, zero, ss01–ss06.
  ss01 = einstöckiges a, ss02 = gerades l, ss03–ss06 = Listenziffern in
  Kreis und Quadrat (Kontur/gefüllt).
- **Titillium Pro Serif «version_00»:** nur Regular und Italic (Neigung
  16°), 117 Zeichen, Beta. Studienarbeit von Lorenzo Volpe (ISIA Faenza),
  betreut von D'Elisiis. Übernimmt die Vertikalmasse der Sans exakt
  (x-Höhe 500, Versalhöhe 700 auf 1000) und die Breiten; Serifen flach,
  ohne Kehlung, Slab-nah. Keine Umlaute, keine Ligaturen, kein Kerning.
  Geplant: eine zweite Serif, die sich von der Sans löst.

**Upright einbezogen? Nein.** Sans Pro und Serif bauen auf der Text-Form.
Die Sans Pro bietet nur a (ss01) und l (ss02) als Upright-Formen; g, y, t
bleiben Text-Form. Die Serif hat durchweg Text-Formen.

Vergleichsbilder (Hausschrift Klar, Titillium Upright, Web, Sans Pro,
Serif BETA; Serif über Sans gelegt) wurden am 31. 10. in der Session
gerendert und angeschaut; der Serif-Prototyp passt deckungsgleich auf die
Sans.

## Was wir lernen oder übernehmen können

1. **Kerning und Metriken.** Die Pro hat professionelles Kerning (iKern),
   unsere Quelle fast keines. Gleiche Vertikalmasse: Paare für gleiche
   Formen (Versalien, Ziffern, Satzzeichen) prüfen und übernehmen (OFL).
2. **Glyphen-Reparaturen.** Chialab führt eine Liste korrupter Glyphen aus
   der Interpolation; mit unserem Audit abgleichen.
3. **Listenziffern in Kreis und Quadrat** (ss03–ss06): passt zu unserem
   Icon-Set, brauchbar für Werkzeugseiten und Beipackzettel.
4. **Serif als Idee, nicht als Datei.** Die Vertikalmasse-Strategie ist der
   Weg zu einer Lesevariante der Hausschrift; sie müsste auf Upright-Formen
   umgezeichnet werden. Beobachten, nicht übernehmen.
5. **Black-Gewicht.** Die Pro geht bis Black; unser Laut (680) ist das Ende.
   Ein Schnitt darüber wäre interpolierbar, falls Plakate es brauchen.

## Weitere Projekte (Sichtung)

Acht Adressen vom Inhaber (31. 10.), gesichtet; wo Dateien vorlagen, in
der Session geladen, gemessen und gerendert. Keines der Projekte führt die
Upright-Formen durchgehend; alle stehen auf der Text-Form. Einstöckiges a
gibt es in Titillio und Multa Pecunia als ss01, sonst nichts.

| Projekt | Wer, Stand | Was | Relevanz für uns |
|---|---|---|---|
| **Titillium Web variabel** https://v-fonts.com/fonts/titillium-web → https://github.com/eliheuer/titillium-web-vf | Eli Heuer, 2018–2020, OFL | Roman und Italic als getrennte VF, wght 200–900, Latein + Arabisch (Cairo) + Vietnamesisch, 700 Zeichen | Vorlage für den VF-Build mit einer Gewichtsachse; Stand vor Pro, Text-Form |
| **Pass A38** https://forum.italia.it/t/suggerimento-per-estensione-di-titillium-web/39784 → https://codeberg.org/m-casanova/PassA38 | Michele Casanova, Vorschlag im Forum Italia 22. 7. 2024 (ohne Antwort), letzter Stand 28. 12. 2025, OFL | VF aus Titillium Web, Roman **und** Italic in einer Datei (wght + ital), kompatible Metriken, Listenzeichen, dazu **variable Icons** aus dem UI Kit Italia (Strichstärke folgt dem Text). Repo hält nur die FontLab-Quelle (.vfj, 7 MB), Fonts unter Releases | Idee «Icons im Font mit mitlaufender Strichstärke» ist genau unser Fall (Goetheanum-Icons, Pfeile): prüfen, ob unsere Icon-Fonts eine Gewichtsachse bekommen sollen |
| **Titillio** («Titillium Pro Display») https://forum.italia.it/t/titillium-pro-display-di-pagopa/42943 → https://github.com/pagopa/titillium-pro-display | pagoPA mit Alessio D'Ellena, auf Basis Titillium Pro (Chialab), Stand 19. 5. 2025, OFL | 14 statische OTF Light–**Extrablack** samt Kursiven, 608 Zeichen, gleiche Features wie Sans Pro (ss01 a, ss02 l, ss03–06 Listenziffern). Für Bildschirm nachgezeichnet: breiter, offener, grössere Umlautpunkte, Kreis-Ziffern kleiner | Bestes Beispiel für «eine Titillium-Tochter für den Schirm»; Extrablack zeigt, wie weit die Gewichtsachse geht. Anlass war Lesbarkeit und Barrierefreiheit in der App IO, derselbe Beweggrund wie unser B02/B03 |
| **Multa Pecunia** https://fontesk.com/multa-pecunia-typeface/ → https://codeberg.org/m-casanova/MultaPecunia | Casanova, ab 9. 11. 2024, v1.545 am 28. 12. 2025, OFL | **Eine** VF-Datei mit wght 100–1000 und ital-Achse, 20 Instanzen, aus Titillio abgeleitet, Metriken wie Pass A38; ss01 a, ss02 l, ss10 | Technisches Muster für unsere Variable: eine Datei, zwei Achsen, CSS `font-weight: 100 1000` |
| **Panefresco** https://www.wfonts.com/font/panefresco | Chank Co, 2011, OFL (Reserved Font Name «Titillium») | 8 Gewichte 1wt–999wt, je Regular und Italic, 16 statische Schnitte, kein VF | Nur Vergleich: früher Fork mit sehr breiter Gewichtsachse; zeigt die OFL-Namensklausel (Umbenennen Pflicht, wie wir es mit «Goetheanum» getan haben) |
| **Elbonium** https://dribbble.com/shots/73639-Elbonium-Regular-Shot | Dribbble-Shot, nicht abrufbar (Seite liefert keinen Inhalt) | — | Nicht gesichtet; vom Inhaber ggf. als Bild liefern |
| **Pass-A38 auf GitHub** https://github.com/m-casanova/Pass-A38 | Casanova | Leer, nur Verweis auf Codeberg (siehe oben) | — |
| **Titillium Pro, Branch serif** https://github.com/chialab/titillium_pro/tree/serif | Chialab | siehe Befund oben | siehe oben |

Lehren aus der Sichtung, zusätzlich zu den fünf Punkten oben:

6. **Variable mit ital-Achse in einer Datei** (Pass A38, Multa Pecunia):
   wir liefern nur Gewicht. Ob eine Kursive je kommt, ist offen; die
   Technik stünde bereit.
7. **Variable Icons:** Strichstärke der Icons folgt dem Textgewicht
   (Pass A38). Für Goetheanum-Icons und Pfeile neben Leise bis Laut prüfen.
8. **Alle Projekte bleiben bei der Text-Form.** Die Upright-Formen trägt
   derzeit nur unsere Hausschrift. Das ist ein Alleinstellungsmerkmal, kein
   Rückstand; es heisst aber auch: Glyphen (a, g, y, t, l) lassen sich von
   keinem dieser Projekte direkt borgen, nur Versalien, Ziffern, Zeichen.

## Entscheid des Inhabers (31. 10. 2026) und Etappen

Der Inhaber hat entschieden: Kursive prüfen und einbauen, alle Lehren zu
Glyphen, Kerning und Metriken übernehmen, Listenziffern aufnehmen, Serif
testen und Grenzen klären, Black nur als Probewort. Jede Etappe läuft als
eigene Session (Opus, Effort medium), Branch je Etappe, PR, Squash-Merge.

**Faktenfrage zu den Listenziffern, geklärt:** Titillium Pro liefert je
Stilset nur 36 Einzelglyphen (A–Z, 0–9), eingesetzt per einfacher
Substitution. 10 bis 99 gibt es dort **nicht**. Für die Hausschrift sind
1–99 machbar: zweistellige Zahlen werden per `calt`/`liga` aus
Halbkreis- bzw. Halbquadrat-Bausteinen und schmalen Ziffern zusammengesetzt
(linke Hälfte + Ziffer + Ziffer + rechte Hälfte); das sind rund 20 Bausteine
pro Form statt 90 fertige Glyphen. Technik im Fontfix-Build mit fontTools.

| Etappe | Inhalt | Ergebnis |
|---|---|---|
| **E1 Kursive** | Titillium Sans Pro Italic (Thin–Black) auf die Hausschrift abbilden: Vertikalmasse passen (500/700), Neigung messen, Upright-Formen (a, g, y, t, l) in der Kursiven nachziehen oder bewusst Text-Form lassen. Probe-Schnitt «Goetheanum Kursiv Klar» bauen, Specimen neben Klar. Prüfen: Variable mit ital-Achse (Muster Multa Pecunia) oder getrennte Datei | Probe-Font, Specimen-Seite, Befund mit Empfehlung; noch kein Paket |
| **E2 Glyphen, Kerning, Metriken** | Abgleich Hausschrift v2.8 ↔ Sans Pro: fehlende Zeichen (607 vs. 454), Kerning-Paare für formgleiche Glyphen (Versalien, Ziffern, Zeichen) übernehmen, Chialabs Liste korrupter Glyphen gegen `AUDIT.md`, Vertikalmetriken (hhea/OS2) vergleichen. Skript in `tools/goetheanum-fontfix/`, idempotent | v2.9-Kandidat, Diff-Bericht, Webfonts und ZIP neu gepackt |
| **E3 Listenziffern** | Kreis und Quadrat, Kontur und gefüllt, A–Z und 1–99, als ss03–ss06 in die Hausschrift; Bausteinlösung wie oben. Anwendung: Campus-Karte, Leitsystem, Beipackzettel | Glyphen im Font, Anschauungsseite, Doku im Beipackzettel |
| **E4 Serif** | Titillium Pro Serif BETA als «Goetheanum Serif Probe»: Umlaute und Ligaturen ergänzen, auf Upright-a prüfen, Specimen in echten Anwendungen (Sektionsseite, Zitat, Lede, Mengentext, Karte). Grenzen klären: ab welchem Grad, welche Sektion, welche Anwendung; was fehlt bis zur Nutzbarkeit | Specimen-Seite (Treibhaus), Befund mit Einsatzgrenzen, Entscheidvorlage |
| **E5 Black-Probewort** (klein, in E1 oder E2 mit) | Ein Probewort über Laut (680) hinaus extrapolieren (Richtung Titillio Extrablack), rendern, anschauen. Kein Schnitt, nur ein Bild | ein Bild, ein Satz Befund |

Reihenfolge: E2 zuerst (liefert die Basis), E1 und E3 und E4 parallel
danach; E5 hängt sich an E1. Jede Session liest diese Notiz und
`CLAUDE-REF.md` § Schnitt-System, baut aus sauberem Stand, schreibt ihren
Befund als `docs/befunde/…` und trägt Beschlüsse in
`design-system/CHANGELOG.md` ein.

## Offen

- [ ] Titillium Pro beobachten (Serif-Fortschritt, Variable), halbjährlich.
- [ ] Elbonium (Dribbble) nicht gesichtet; Bild vom Inhaber.
