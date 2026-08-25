# Kalender-Befund: Was Apples Monatsansicht trägt — und was davon zu Tagwerk kommt

Stand: 25. August 2026 · Untersucht: zwei Bildschirmfotos vom selben Moment
(25.8.2026, 13:37) — iOS-Kalender in der Monatsansicht (dunkel) und Tagwerk in
der Monatsansicht (dunkel), beide 390 pt Breite bei dreifacher Auflösung.
Kappenhöhen, Farbwerte und Kontraste sind aus den Bilddateien **gerechnet**
(Pillow, Kontrastformel WCAG 2.1 § 1.4.3), nicht nach Augenmass behauptet.

## 1 · Der eine Satz

**Apple zeigt den Inhalt, wir zeigen den Behälter.** Bei Apple ist das Grösste
auf dem Blatt die Antwort — «August». Bei uns ist das Grösste die Frage —
«Monat». Alles Weitere in diesem Befund ist eine Folge davon.

## 2 · Was gemessen wurde

| Grösse | Tagwerk | iOS-Kalender | Lesart |
|---|---|---|---|
| Seitentitel, Kappenhöhe | «Monat» **14.0 px** | «August» **rund 22 px** (29.3 px inkl. Unterlänge) | der Titel ist bei uns halb so gross — und sagt nichts |
| Tageszahl, Kappenhöhe | **8.7 px** (≈ 12 px Schriftgrad) | **13.3 px** (≈ 19 px Schriftgrad) | Apples Tageszahl ist **53 % grösser** |
| Agenda-Eintrag, Kappenhöhe | 10.7 px | 12.3 px | |
| Vorspann bis zur Wochentagszeile | **33.5 %** der Bildhöhe | **18.7 %** | wir verbrauchen ein Drittel des Blatts, bevor ein Datum erscheint |
| Anteil der Tagesliste am Blatt | **rund 15 %** | **rund 37 %** | Apple gibt dem heutigen Tag zweieinhalbmal so viel Raum |
| Auswahlfläche Kupfer `#C9855F` mit Weiss | **3.0 : 1** | — | **verfehlt** B01/B02 (Soll ≥ 4.5 : 1) |
| Kupfer `#C9855F` auf Grund `#0D0E0F` | 6.4 : 1 | — | als Linie/Akzent tragfähig |
| Grau `#7C7B75` auf Grund | 4.55 : 1 | — | knapp bestanden, trägt aber drei verschiedene Rollen |
| Heute-Fläche `#CCCAC3` mit schwarzer Zahl | 12.8 : 1 | — | kontrastfest, aber der hellste Fleck des Blatts |

Die Tageszahl bei rund 12 px liegt unter unserer eigenen Untergrenze
(**B03**: nichts Lesbares unter 14 px). Der Kalender wäre auf unserem eigenen
Prüfstand ein DS03-Fehler — an der Stelle, die die ganze Ansicht trägt.

## 3 · Acht Befunde im Einzelnen

**B1 · Das Grösste sagt nichts.** «Monat» ist die Modus-Bezeichnung, nicht der
Inhalt. Der Nutzer weiss, welche Ansicht er geöffnet hat; er will wissen,
*welcher* Monat. Apple stellt den Monatsnamen gross, schiebt das Jahr in den
Zurück-Knopf («‹ 2026») und macht daraus zugleich die Navigation eine Ebene
höher. Zwei Aufgaben, ein Element.

**B2 · 42 Rahmen für 42 Zahlen.** Jeder Tag sitzt bei uns in einer gerundeten
Kachel mit eigener Fläche und Rand. Ein Kalender ist aber schon durch Zeile und
Spalte gruppiert — die Ausrichtung *ist* das Raster. Der Rahmen wiederholt eine
Information, die schon da ist, und zahlt sie mit Fläche, Kontrast und Ruhe.
Apple zeichnet nur eine dünne Linie je Woche und lässt sonst Schwarz stehen.

**B3 · Punkte zählen nicht.** Unsere zwei bis vier Punkte sagen «da ist etwas»,
aber nicht «wie viel». Ein Tag mit drei Terminen und ein Tag mit zwölf sehen
gleich aus. Apples Marke ist ein **segmentierter Balken**, dessen *Länge* die
Belegung trägt und dessen Segmentfarben die Kalender zeigen: am 27. ein Punkt,
am 28. ein voller Balken. Man liest die Monatslast, ohne einen Tag zu öffnen.
Das ist eine Sparkline, kein Schmuck.

**B4 · Der Vorspann frisst den Kalender.** Kupferstreifen, Kopfzeile «Monat»,
vier Navigationsknöpfe gleichen Gewichts, fünf Filterpillen — 33.5 % des Blatts,
bevor das erste Datum kommt. Die Filterleiste ist Bedienung *vor* dem Inhalt:
Sie kostet jeden Nutzer bei jedem Öffnen Aufmerksamkeit, obwohl sie selten
gebraucht wird.

**B5 · Die Agenda ist abgeschnitten.** Die Liste des heutigen Tages ist der
eigentliche Nutzen der Ansicht — der Monat ist nur die Karte dazu. Bei uns
bleiben zwei Zeilen übrig, bei Apple ein gutes Drittel des Blatts, mit
Ganztägig zuoberst, farbigem Randstrich je Kalender, Ort in zweiter Zeile und
Anfang/Ende rechtsbündig in einer eigenen Spalte.

**B6 · Drei Füllzustände ohne erkennbare Regel.** Heute ist eine helle Fläche,
zwei Samstage tragen eine braune Fläche, der Rest ist dunkel. Drei Bedeutungen
auf demselben Merkmal (Fläche), und die hellste — «heute» — sieht aus wie eine
Auswahl. Apple markiert genau einen Zustand und genau mit einem Merkmal: ein
gefüllter Kreis um die Zahl, in der einen Akzentfarbe. Das ist der Geist von
**G01/G03** auf der Strukturebene: ein Merkmal, und was entbehrlich ist, entfällt.

**B7 · Kupfer auf Weiss hält nur 3.0 : 1.** Gerechnet, nicht geschätzt: die
aktive Reiter-Pille (`#C9855F` mit weisser Schrift) verfehlt die 4.5 : 1 aus
**B01/B02** deutlich. Für das Plus im Aktionsknopf (Grafik, Soll 3 : 1) reicht
es gerade eben. Unser Fundament hat die Lösung längst: `--gold-deep #94702E`
trägt Weiss mit 4.55 : 1. Kupfer bleibt als *Linie und Akzent* auf dunklem
Grund richtig (6.4 : 1) — nur nicht als Textgrund.

**B8 · Inhalt unter der Navigation.** Unterhalb der Reiterleiste steht noch ein
Eintrag («Haiku»). Die Leiste ist der Boden des Blatts; was darunter erscheint,
wirkt wie ein Fehler und wird nicht gelesen.

## 4 · Auf welchen Prinzipien Apple hier steht

1. **Zurücknahme** (*deference*, Apple HIG seit iOS 7): Die Oberfläche tritt
   hinter den Inhalt zurück. Keine Kacheln, keine Ränder, keine Verläufe — die
   Zahlen und Balken **sind** die Oberfläche.
2. **Hierarchie durch Grad, nicht durch Rahmen.** Jahr klein, Monat gross,
   Wochentag winzig, Tageszahl mittel. Wer nur den Schriftgrad ändert, kann
   nichts unstimmig machen; wer Flächen einführt, sofort.
3. **Ein Akzent, für Zustand reserviert.** Rot bedeutet «jetzt» — heutiger Tag,
   Kalenderwochen-Ziffern, aktuelle Termine. Alles andere ist Grau plus
   Kalenderfarbe. Die Kalenderfarben sind **Daten**, nicht Dekor.
4. **Die Marke am Tag ist ein Mass.** Länge = Belegung. Ein Datenbild statt
   eines Symbols (Tuftes *data-ink*: jedes Pixel trägt Information).
5. **Voreinstellung statt Bedienung.** Kein Filter auf der Fläche. Wer filtern
   will, öffnet das Kalenderblatt; die Ansicht zeigt die Antwort, nicht die
   Regler (Hicks Gesetz: jede sichtbare Wahl kostet vor dem Nutzen).
6. **Karte und Ausschnitt gleichzeitig.** Monat oben, heutiger Tag unten —
   Wiedererkennen statt Erinnern; man muss nicht wechseln, um zu wissen, was
   ansteht.
7. **Daumenzone.** «Heute», Ansichtswechsel und Posteingang sitzen als
   schwebende Pillen am unteren Rand, nicht in der Kopfzeile (Fitts' Gesetz).
8. **Der Rand navigiert.** Der Zurück-Knopf trägt zugleich das Jahr; die
   Monatsnavigation läuft über Wischen statt über zwei Pfeilknöpfe.
9. **Ausrichtung als Ordnung.** Titel links, Zeiten rechts in einer Spalte,
   tabellarische Ziffern — genau das, was **G25** bei uns ohnehin verlangt.

## 5 · Woraus wir sonst schöpfen können

- **Dieter Rams, «Weniger, aber besser».** Gute Gestaltung ist so wenig
  Gestaltung wie möglich. Deckt sich wörtlich mit unserer Kardinalregel
  **G03 Weglassen** — wer eine Auszeichnung weglassen kann, lässt sie weg.
- **Edward Tufte, *data-ink ratio* und Sparklines.** Der Tagesbalken ist eine
  Sparkline. Der Monat ist ein *small multiple* aus 30 Sparklines.
- **Gestaltgesetze: Nähe und Ausrichtung schlagen die gemeinsame Region.**
  Kacheln sind das schwerste Gruppierungsmittel überhaupt — für etwas, das
  schon durch das Raster gruppiert ist, das falsche.
- **Josef Müller-Brockmann.** Das Raster wird gefühlt, nicht gezeichnet.
- **Jakobs Gesetz.** Nutzer verbringen ihre Zeit in anderen Apps: Kreis =
  heute, grosser Monatsname, Wischen für den Monatswechsel sind gelernte
  Konventionen. Abweichen kostet, ohne zu gewinnen.
- **Unser eigenes Regelwerk ist die kürzeste Fassung von alledem** —
  **G03** (Weglassen), **G05** (betont wird mit Laut, nicht mit Beiwerk),
  **G25** (tabellarische Ziffern), **B01/B02** (Weiss auf Farbe, gerechnet),
  **B03/B04** (Mindestgrössen, 44 px Fingerziele). Wir müssen dafür nichts
  Neues erfinden, sondern das Vorhandene auf den Kalender anwenden.

## 6 · Massnahmen, nach Wirkung geordnet

| # | Massnahme | Wirkung | Aufwand |
|---|---|---|---|
| 1 | «Monat» streichen, **«August»** gross als Seitentitel, **2026** klein als Zurück-Kontext | gross | klein |
| 2 | **Kachelrahmen entfernen** — nur Zahlen auf Grund, dünne Linie je Woche | gross | klein |
| 3 | **Tageszahl auf ≥ 16 px** heben (B03), Wochenende gedämpft, Fremdmonate sehr leise | gross | klein |
| 4 | **Filterpillen ins Kalenderblatt** verlagern; auf der Fläche höchstens eine Zeile, wenn ein Filter aktiv ist | gross | mittel |
| 5 | **Punkte → segmentierter Lastbalken** (Länge = Belegung, Segmentfarbe = Kalender) | gross | mittel |
| 6 | **Tagesliste auf ein Drittel des Blatts**: Ganztägig zuoberst, Randstrich je Kalender, Zeiten rechtsbündig tabellarisch (G25) | gross | mittel |
| 7 | **Heute = gefüllter Kreis um die Zahl** in einer Akzentfarbe — ein Merkmal, ein Zustand; die zweite Flächenmarkierung auflösen | mittel | klein |
| 8 | **Kupfer als Textgrund ersetzen** durch `--gold-deep #94702E` (4.55 : 1); Kupfer bleibt Linie und Akzent | mittel | klein |
| 9 | **Kupferstreifen und zweite Kopfzeile** zusammenlegen | mittel | klein |
| 10 | **Inhalt unterhalb der Reiterleiste** auflösen | klein | klein |
| 11 | Monatswechsel per **Wischen**; die zwei Pfeilknöpfe entfallen | klein | mittel |

## 7 · Wenn nur eine Sache passiert

Die **Rahmen weg und die Tageszahl gross** (Nr. 2 und 3). Das kostet ein paar
Zeilen CSS, gibt sofort Ruhe und Platz, hebt zugleich einen B03-Verstoss auf —
und macht den Rest der Liste erst sichtbar.
