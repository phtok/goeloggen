# Totaler Abgleich goetheanum.tv gegen Uscreen — 10. August 2026

Grundlage: Vollexport aller Uscreen-Konten (11 867 Zeilen, ohne Datumsfilter,
alle Status), zeilenweise gegen `sommer2026_signups` gejoint über
`ext_id` = Uscreen `User ID`. Der Export enthält Personendaten; ausgewertet
wurde ausschliesslich aggregiert, nichts davon steht in diesem Dokument oder
im Repository.

Dieses Dokument löst die aggregierte Vorprüfung vom 9. August ab.

## Das Ergebnis in einem Satz

Wir zählen für goetheanum.tv **665 Anmeldungen**, Uscreen kennt im
Kampagnenfenster **626 neue Abonnements**. Die Differenz ist erklärt, nicht
geschätzt: **40 unserer Zeilen sind gar keine neuen Abos**, dafür fehlen uns
**11 echte** aus den ersten Julitagen.

| | Zeilen |
|---|---:|
| unsere gtv-Anmeldungen | 665 |
| davon mit `ext_id` | 655 |
| **belegt: auch bei Uscreen ein neues Abo im Fenster** | **615** |
| bei uns, bei Uscreen aber kein neues Abo | 40 |
| ohne `ext_id`, nicht zuordenbar | 10 |
| bei Uscreen im Fenster, bei uns nicht | 11 |
| **Uscreen: neue Abos 3. Juli bis 10. August** | **626** |

## Woher die 40 kommen — Verlängerungen als Neuzugang gezählt

Die 40 Zeilen tragen bei Uscreen Abo-Daten aus 2022 bis 2025. Der Beweis
liegt in der Folgerechnung: Bei fast allen liegt `Next invoice date` **genau
einen Monat** (oder bei Jahresabos genau ein Jahr) nach dem Tag, an dem
unsere Datenbank sie als Anmeldung führt. Das ist kein Abschluss — das ist
die turnusmässige Rechnung eines laufenden Abos.

| Sorte | Zeilen |
|---|---:|
| reine Monatsrechnung eines Bestandsabos | 19 |
| reine Jahresrechnung eines Bestandsabos | 7 |
| Kündigung eines alten Abos, keine Folgerechnung | 11 |
| **Gratismonate auf ein bereits zahlendes Abo gebucht** | **2** |
| anderes | 1 |

**Ursache:** Der Uscreen-Webhook feuert auf Abo-Ereignisse allgemein, nicht
nur auf Neuabschlüsse. Wir haben Verlängerung und Neuabschluss nicht
unterschieden. Für die nächste Aktion gehört in die Ingest-Regel eine
Bedingung: nur zählen, wenn `Subscription Created at` im Kampagnenfenster
liegt.

**Die zwei mit Gratismonaten sind ein eigener Befund.** Zwei Menschen, die
bereits zahlten, haben über die Aktionsseite drei Monate geschenkt bekommen.
Klein in der Zahl, eindeutig in der Richtung: Das Angebot war nicht gegen
Bestandsabos gesperrt. Es kostet Geld, statt welches zu bringen.

## Die 11 fehlenden — Webhook-Lücke am Anfang

Alle 11 stammen vom **3. bis 6. Juli**, den ersten vier Kampagnentagen. Der
Webhook lief noch nicht sauber. Sie sind echte Abos und fehlen uns.

## Wer die Gratismonate nicht bekommt

Kaum jemand. Von 626 Abos im Fenster tragen **596** eine Folgerechnung
89 oder 90 Tage nach Abschluss — die drei Monate sind gebucht. Weitere 24
haben die Frist erhalten und **während** ihr gekündigt, darum steht bei ihnen
keine Folgerechnung mehr.

Wirklich ohne die drei Monate sind **sechs**:

| Fall | Zahl | Grund |
|---|---:|---|
| Institutionelles Abo über Team-Einladung | 2 | eigener Vertrag, wird separat verrechnet |
| App-Abo und ermässigtes Abo | 2 | anderer Plan, nur 6 Tage Probezeit |
| Herabstufung eines App-Abos | 1 | 42 Tage Restlaufzeit, kein Neuabschluss |
| Migration | 1 | Jahresabo, direkt verrechnet |

Die Aktion hat also **technisch getan, was sie sollte**. Die Unschärfe liegt
nicht bei der Frist, sondern beim Zählen und beim Bezahlen.

## Der eigentliche Verlust: die Kasse

Im Kampagnenfenster entstanden **874 neue Konten**. 460 davon haben ein Abo
abgeschlossen. **341 sind an der Kasse stehengeblieben** (Uscreen:
‹Abandoned checkout›), 227 davon mit Mailing-Spur. 73 sind später
zurückgekommen und haben doch abgeschlossen — **268 nicht**.

Das ist die grösste einzelne Zahl der ganzen Auswertung: 268 Menschen waren
entschlossen genug, bis zur Kasse zu gehen, und sind dort verloren gegangen.
Gemessen an 626 Abschlüssen wären sie **43 % mehr** gewesen. Für die nächste
Aktion ist der Kassenweg der Hebel, nicht die Reichweite.

## Ein Viertel kam aus dem eigenen Haus

Von den 626 Abos stammen **166 aus Konten, die es vorher schon gab** — 63
davon seit 2022. Sie tragen **keine** UTM-Spur, weil die beim Anlegen des
Kontos gesetzt wird und nicht beim Abschluss.

Das korrigiert die Dunkelfeld-Lesart an einer wichtigen Stelle: Ein guter
Teil des Dunkelfelds ist kein ungemessener Kanal, sondern **die Rückkehr
alter Konten**. Wer schon einmal da war, ist über die Aktion wiedergekommen.

Und diese Gruppe ist die bessere: Sie kündigt bisher mit **1,8 %** halb so
oft wie die Neukonten (**4,6 %**) und wählt etwas häufiger das Jahresabo
(15 % gegen 12 %). Ein erster, früher Hinweis für die Bleibe-Quote — mehr
noch nicht.

## Erste Kündigungen: 24 von 626

24 Abos sind bereits gekündigt oder ausgelaufen, gleichmässig über die
Laufzeit verteilt, mit leichter Häufung in den letzten Tagen. Das sind
**3,8 %** — die erste gemessene Zahl zur Bleibe-Quote überhaupt. Sie sagt
noch nichts über den Oktober, aber sie ist keine Schätzung.

## Tarifmischung im Fenster

547 monatlich, 79 jährlich (12,6 %). Die Einnahmen-Perspektive rechnet mit
dieser Mischung; sie ist damit belegt statt angenommen.

## Was zu tun ist

1. **Ingest-Regel schärfen:** Verlängerungen nicht als Neuzugang zählen
   (Bedingung auf `Subscription Created at`).
2. **Die 40 markieren, nicht löschen** — sie sind ein Beleg dafür, wie viele
   Bestandsabos in der Kampagnenzeit turnusmässig verlängert wurden.
3. **Die 11 aus dem Juli nachtragen.**
4. **Aktionsangebot gegen Bestandsabos sperren**, damit niemand geschenkt
   bekommt, wofür er schon zahlt.
5. **Angebote 84317 und 84322 am 12. August zurücksetzen** — steht
   unverändert offen.
