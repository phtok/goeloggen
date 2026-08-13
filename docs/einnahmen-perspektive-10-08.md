# Einnahmen-Perspektive der Sommer-Aktion — drei Szenarien, Stand 10. August 2026

Was die Aktion im **Folgejahr** einbringt, wenn die Gratis-Zeit vorbei ist.
Gerechnet auf dem Schlussstand: **1 042 Anmeldungen, davon 1 019 aktiv**
(23 bereits gekündigt, alle bei goetheanum.tv). Die Aktion endete am
11. August; die Mengen stehen damit fest.

Diese Fassung löst den Stand vom 8. August ab (902 aktive Abos, erwartet
CHF 58 497). **Geändert hat sich allein die Menge** — und zwar in beide
Richtungen:

| | 8. August | jetzt | |
|---|---:|---:|---|
| goetheanum.tv | 573 | **636** | −40 Verlängerungen, +11 nachgetragen, + Schlusstage |
| Wochenschrift | 353 | **406** | Schlusstage |
| **Anmeldungen** | **926** | **1 042** | |
| davon aktiv | 902 | **1 019** | |

Die neue Zählregel (Spalte `art`, View `sommer2026_neuabos`,
`docs/uscreen-abgleich-10-08.md`) nimmt bei goetheanum.tv 40 Zeilen als
Verlängerungen heraus und trägt 11 echte Juli-Abos nach. Netto steht
goetheanum.tv trotzdem höher als am 8. August: Die Schlusstage haben mehr
gebracht, als die Korrektur weggenommen hat.

Quoten, Monats-Faktoren und Methode sind **unverändert**. Nachrechenbar:
`node docs/einnahmen-perspektive-10-08.js`.

Alle Beträge in CHF, EUR-Umsatz zum hinterlegten Kurs 0,93 umgerechnet.
Preise sind echt (Kampagnen-Formulare und Uscreen-Store, Stand 17. Juli),
nicht geschätzt. Die Szenarien selbst sind Annahmen — begründet, aber
Annahmen.

## Die Decke

Blieben **alle** 1 019 und zahlten die monatlichen zwölf volle Monate:

**CHF 149 306 im Folgejahr.**

Diese Zahl ist keine Erwartung, sondern die Obergrenze. Sie zu nennen lohnt
trotzdem: Sie sagt, worüber wir reden.

## Die drei Szenarien

| | bleiben | **Folgejahr CHF** | davon goetheanum.tv | davon Wochenschrift | je bleibendem Abo |
|---|---:|---:|---:|---:|---:|
| **Vorsichtig** | 438 | **39 272** | 21 990 | 17 283 | 90 |
| **Erwartet** | 591 | **65 877** | 38 786 | 27 091 | 112 |
| **Gut** | 744 | **99 087** | 60 005 | 39 082 | 133 |

Die Spanne ist gross — Faktor 2,5 zwischen vorsichtig und gut. Das ist keine
Rechenschwäche, sondern der ehrliche Zustand: **Noch keine einzige Kohorte
hat entschieden.** Die erste (Juli-Anmeldungen) entscheidet ab Anfang Oktober.

Gegenüber dem 8. August liegt jedes Szenario rund **12 Prozent höher** — das
ist die gewachsene Menge, nicht eine bessere Erwartung. Der Betrag je
bleibendem Abo ist mit CHF 112 praktisch unverändert.

## Woraus die Szenarien gebaut sind

Zwei Stellschrauben, nicht eine. Die zweite ist die wirksamere.

### 1 · Wer bleibt (Bleibe-Quote)

| | goetheanum.tv | Wochenschrift |
|---|---:|---:|
| Vorsichtig | 35 % | 55 % |
| Erwartet | 50 % | 70 % |
| Gut | 65 % | 85 % |

Warum die Wochenschrift höher steht als goetheanum.tv — drei Gründe, alle
aus den eigenen Daten und Texten:

- **Beide Angebote sind Opt-out.** «Danach läuft das Abo regulär weiter,
  jederzeit kündbar» steht so in den Kampagnentexten. Es braucht kein Ja, nur
  ein ausbleibendes Nein.
- **Das Nein ist bei goetheanum.tv einen Klick weit weg** («ein Klick im
  Konto», eigene Formulierung), bei der Wochenschrift nicht. Und die
  monatliche Kartenbelastung erinnert dort jeden Monat an die Entscheidung.
- **Der Frühindikator zeigt genau das:** Schon im Gratis-Zeitraum haben
  **23 von 636** goetheanum.tv-Abos gekündigt (3,6 %) — bei der Wochenschrift
  **0 von 406**.

**Zwei Befunde vom 10. August, die gegeneinander stehen** und darum beide
keine Quote verschieben:

- **Dagegen:** 380 der Anmeldungen — gut ein Drittel — kamen an den beiden
  Fristtagen herein, unter Zeitdruck und grösstenteils aus einer
  Erinnerungs-Mail. Wer unter einer ablaufenden Frist zusagt, hat kürzer
  überlegt.
- **Dafür:** **166 der 626 belegten goetheanum.tv-Abos stammen aus Konten,
  die es vorher schon gab** (`docs/uscreen-abgleich-10-08.md`). Diese Gruppe
  kündigt bisher mit 1,8 % halb so oft wie die Neukonten (4,6 %) und wählt
  etwas häufiger das Jahresabo. Ein Viertel der Kohorte ist also treuer als
  angenommen.

Die Quoten sind darum **nicht** bewegt worden — dafür fehlt weiterhin jede
Messung. Es bleibt beim Rat vom 8. August: «Erwartet» nennen, «Vorsichtig»
einplanen.

### 2 · Wie lange die monatlichen zahlen

**886 der 1 019 Abos zahlen monatlich, nur 133 jährlich** (13,1 % — die
Tarifmischung ist inzwischen gegen Uscreen belegt, nicht mehr angenommen).
Ein Folgejahr-Umsatz, der bei jedem monatlichen Abo zwölf volle Monate
ansetzt, rechnet mit einer Treue, die niemand zugesagt hat. Darum trägt jedes
Szenario einen Monats-Faktor: **7 · 9 · 11** von zwölf Monaten. Jährliche
Abos zählen voll — sie haben das Jahr im Voraus bezahlt.

### Empfindlichkeit

Nur der Monats-Faktor bewegt, die Quoten bleiben auf «Erwartet»:

| Monate | Folgejahr CHF |
|---:|---:|
| 6 | 47 177 |
| 8 | 59 643 |
| 9 | **65 877** |
| 10 | 72 110 |
| 12 | 84 577 |

**Ein Monat durchschnittlicher Verweildauer ist rund CHF 6 200 wert** (am
8. August waren es 5 500 — die Menge ist gewachsen). Das ist der grösste
einzelne Hebel in dieser Rechnung, grösser als jede plausible Verschiebung
der Bleibe-Quote allein.

## Was diese Rechnung nicht ist

- **Keine Prognose.** Kein Wert stützt sich auf eine beobachtete
  Bleibe-Entscheidung, weil es noch keine gibt. Wer die Zahlen weitergibt,
  gibt Annahmen weiter.
- **Noch kein Deckungsbeitrag — aber die Kampagnenkosten stehen.** Seit
  13. August: **CHF 9 014.60** vollständig erfasst (Druck & Versand 2 259.60,
  davon 1 949.90 Papier-Fulfillment der Probeabos — `docs/probeabo-kosten-12-08.md`;
  Social 460; Stunden intern 6 000; Infrastruktur 295, davon CHF 95 eine
  Schätzung für die ActiveCampaign-Gebühr). Das Cockpit rechnet damit live:
  **CHF 8.65 Kosten je Anmeldung, Rückfluss 7,3-fach** gegen das Szenario
  «Erwartet». Was weiterhin fehlt, ist die **laufende** Uscreen-Gebühr je Abo
  und Monat sowie die Papier-Stückkosten für die Jahre **nach** der Gratiszeit
  — ohne sie bleibt der Folgejahr-Umsatz oben ein Umsatz, kein
  Deckungsbeitrag (`docs/schlussbericht-datensammlung.md`, «Zwei Arten von
  Kosten»).
- **Keine Aussage über Papier.** Die Wochenschrift auf Papier trägt
  Herstellungs- und Versandkosten je Exemplar, die hier nicht abgezogen sind.
  Von den 406 WoS-Abos sind **114 Papier-Abos**. Was dafür zu sammeln ist,
  steht in `docs/schlussbericht-datensammlung.md`.

## Was den Rat durch Messung ersetzt

Zwei Termine, in dieser Reihenfolge:

1. **Anfang Oktober** entscheidet die erste Kohorte (Juli-Anmeldungen). Dann
   steht die Bleibe-Quote je Produkt zum ersten Mal als Zahl da und ersetzt
   die Annahme in `CONFIG.szenarien`.
2. **Ab November** wird der Monats-Faktor sichtbar: Die Uscreen-Zahlungen
   (`order_paid`, `success_recurring`) laufen ohnehin ins Roh-Log; wie viele
   Monate ein Abo im Schnitt trägt, lässt sich daraus ablesen, sobald zwei
   Zyklen durch sind.

Bis dahin gilt: **«Erwartet» nennen, «Vorsichtig» einplanen.**
