# Einnahmen-Perspektive der Sommer-Aktion — drei Szenarien, Stand 8. August 2026

> **Überholt.** Die geltende Fassung ist
> `docs/einnahmen-perspektive-10-08.md` (Schlussstand 1 042 Anmeldungen /
> 1 019 aktive Abos nach der neuen Zählregel). Dieses Dokument rechnet noch
> auf 902 aktive Abos und bleibt als Beleg des Zwischenstands stehen.

Was die Aktion im **Folgejahr** einbringt, wenn die Gratis-Zeit vorbei ist.
Gerechnet auf dem Stand vom 8. August, dem letzten Fristtag: **926
Anmeldungen, davon 902 aktiv** (24 bereits gekündigt). Die Aktion läuft still
bis zum 11. August weiter — die Zahlen wachsen also noch, die Verhältnisse
voraussichtlich nicht mehr.

Diese Fassung löst den Stand vom 7. August ab (693 aktive Abos, erwartet
CHF 45 115). Geändert haben sich allein die Mengen: Die beiden Fristtage
brachten 380 Anmeldungen. Quoten, Monats-Faktoren und Methode sind unverändert.

Nachrechenbar: `node docs/einnahmen-perspektive-08-08.js` — dort stehen die
Segmente, die Preise und die Szenario-Annahmen als Code, damit die Tabellen
unten nicht von Hand gepflegt werden müssen.

Alle Beträge in CHF, EUR-Umsatz zum hinterlegten Kurs 0,93 umgerechnet.
Preise sind echt (Kampagnen-Formulare und Uscreen-Store, Stand 17. Juli),
nicht geschätzt. Die Szenarien selbst sind Annahmen — begründet, aber
Annahmen.

## Die Decke

Blieben **alle** 902 und zahlten die monatlichen zwölf volle Monate:

**CHF 132 710 im Folgejahr.**

Diese Zahl ist keine Erwartung, sondern die Obergrenze. Sie zu nennen lohnt
trotzdem: Sie sagt, worüber wir reden — die Aktion hat einen Gegenwert im
sechsstelligen Bereich aufgebaut, nicht im fünfstelligen Zehner.

## Die drei Szenarien

| | bleiben | **Folgejahr CHF** | davon goetheanum.tv | davon Wochenschrift | je bleibendem Abo |
|---|---:|---:|---:|---:|---:|
| **Vorsichtig** | 386 | **34 877** | 19 715 | 15 162 | 90 |
| **Erwartet** | 522 | **58 497** | 34 746 | 23 750 | 112 |
| **Gut** | 657 | **87 974** | 53 727 | 34 247 | 134 |

Die Spanne ist gross — Faktor 2,5 zwischen vorsichtig und gut. Das ist keine
Rechenschwäche, sondern der ehrliche Zustand: **Noch keine einzige Kohorte
hat entschieden.** Die erste (Juli-Anmeldungen) entscheidet ab Anfang Oktober.

## Woraus die Szenarien gebaut sind

Zwei Stellschrauben, nicht eine. Die zweite fehlt im Cockpit bisher und ist
die wirksamere.

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
  **24 von 573** goetheanum.tv-Abos gekündigt (4,2 %) — bei der Wochenschrift
  **0 von 353**.

**Neu am 8. August und gegen alle drei Szenarien:** 380 der 926 Anmeldungen —
gut 40 Prozent — kamen an den beiden Fristtagen herein, unter Zeitdruck und
grösstenteils aus einer Erinnerungs-Mail. Wer unter einer ablaufenden Frist
zusagt, hat kürzer überlegt als wer im Juli aus eigenem Antrieb zugesagt hat;
für die Bleibe-Entscheidung im Herbst ist das eher ein Nach- als ein Vorteil.
Die Quoten sind hier **nicht** gesenkt worden — dafür fehlt jede Messung —,
aber es ist der stärkste vorliegende Grund, «Vorsichtig» einzuplanen und nicht
«Erwartet».

### 2 · Wie lange die monatlichen zahlen

**782 der 902 Abos zahlen monatlich, nur 120 jährlich.** Ein Folgejahr-Umsatz,
der bei jedem monatlichen Abo zwölf volle Monate ansetzt, rechnet mit einer
Treue, die niemand zugesagt hat. Darum trägt jedes Szenario einen
Monats-Faktor: **7 · 9 · 11** von zwölf Monaten. Jährliche Abos zählen voll —
sie haben das Jahr im Voraus bezahlt.

### Empfindlichkeit

Nur der Monats-Faktor bewegt, die Quoten bleiben auf «Erwartet»:

| Monate | Folgejahr CHF |
|---:|---:|
| 6 | 41 944 |
| 8 | 52 979 |
| 9 | **58 497** |
| 10 | 64 014 |
| 12 | 75 049 |

**Ein Monat durchschnittlicher Verweildauer ist rund CHF 5 500 wert.** Das
ist der grösste einzelne Hebel in dieser Rechnung — grösser als jede
plausible Verschiebung der Bleibe-Quote allein.

## Was diese Rechnung nicht ist

- **Keine Prognose.** Kein Wert stützt sich auf eine beobachtete
  Bleibe-Entscheidung, weil es noch keine gibt. Wer die Zahlen weitergibt,
  gibt Annahmen weiter.
- **Kein Deckungsbeitrag.** Gegengerechnet sind nur die Einnahmen. Die Kosten
  der Aktion stehen mit CHF 309.70 (Druck) in der Datenbank; **der Betrag der
  Meta-Anzeige fehlt dort noch**. Solange er fehlt, ist jede Aussage über den
  Rückfluss zu günstig — besonders auf der Kosten-Seite, wo Kosten je Abo und
  Rückfluss direkt daraus gerechnet werden. Die Zahlen werden in der Woche ab
  dem 10. August eingetragen (Auskunft Auftraggeber, 8. August); sie fliessen
  ohne weiteres Zutun ein, sobald sie im Kosten-Formular stehen.
- **Keine Aussage über Papier.** Die Wochenschrift auf Papier trägt
  Herstellungs- und Versandkosten je Exemplar, die hier nicht abgezogen sind.
  Von den 353 WoS-Abos sind 106 Papier-Abos.

## Was den Rat durch Messung ersetzt

Zwei Termine, in dieser Reihenfolge:

1. **Anfang Oktober** entscheidet die erste Kohorte (Juli-Anmeldungen). Dann
   steht die Bleibe-Quote je Produkt zum ersten Mal als Zahl da und ersetzt
   die Annahme in `CONFIG.bleibeQuote`.
2. **Ab November** wird der Monats-Faktor sichtbar: Die Uscreen-Zahlungen
   (`order_paid`, `success_recurring`) laufen ohnehin ins Roh-Log; wie viele
   Monate ein Abo im Schnitt trägt, lässt sich daraus ablesen, sobald zwei
   Zyklen durch sind.

Bis dahin gilt: **«Erwartet» nennen, «Vorsichtig» einplanen.**
