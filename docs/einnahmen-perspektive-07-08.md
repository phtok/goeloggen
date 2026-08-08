# Einnahmen-Perspektive der Sommer-Aktion — drei Szenarien, Stand 7. August 2026

Was die Aktion im **Folgejahr** einbringt, wenn die Gratis-Zeit vorbei ist.
Gerechnet auf dem Stand vom 7. August: **714 Anmeldungen, davon 693 aktiv**
(21 bereits gekündigt). Die Aktion läuft noch bis zum 11. August — die Zahlen
wachsen also weiter, die Verhältnisse voraussichtlich nicht.

Nachrechenbar: `node docs/einnahmen-perspektive-07-08.js` — dort stehen die
Segmente, die Preise und die Szenario-Annahmen als Code, damit die Tabellen
unten nicht von Hand gepflegt werden müssen.

Alle Beträge in CHF, EUR-Umsatz zum hinterlegten Kurs 0,93 umgerechnet.
Preise sind echt (Kampagnen-Formulare und Uscreen-Store, Stand 17. Juli),
nicht geschätzt. Die Szenarien selbst sind Annahmen — begründet, aber
Annahmen.

## Die Decke

Blieben **alle** 693 und zahlten die monatlichen zwölf volle Monate:

**CHF 101 904 im Folgejahr.**

Diese Zahl ist keine Erwartung, sondern die Obergrenze. Sie zu nennen lohnt
trotzdem: Sie sagt, worüber wir reden — die Aktion hat einen Gegenwert im
sechsstelligen Bereich aufgebaut, nicht im fünfstelligen Zehner.

## Die drei Szenarien

| | bleiben | **Folgejahr CHF** | davon goetheanum.tv | davon Wochenschrift | je bleibendem Abo |
|---|---:|---:|---:|---:|---:|
| **Vorsichtig** | 297 | **26 995** | 15 083 | 11 911 | 91 |
| **Erwartet** | 401 | **45 115** | 26 536 | 18 578 | 112 |
| **Gut** | 505 | **67 693** | 40 982 | 26 711 | 134 |

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
  **21 von 440** goetheanum.tv-Abos gekündigt (4,8 %) — bei der Wochenschrift
  **0 von 274**.

### 2 · Wie lange die monatlichen zahlen

**595 der 693 Abos zahlen monatlich, nur 98 jährlich.** Ein Folgejahr-Umsatz,
der bei jedem monatlichen Abo zwölf volle Monate ansetzt, rechnet mit einer
Treue, die niemand zugesagt hat. Darum trägt jedes Szenario einen
Monats-Faktor: **7 · 9 · 11** von zwölf Monaten. Jährliche Abos zählen voll —
sie haben das Jahr im Voraus bezahlt.

### Empfindlichkeit

Nur der Monats-Faktor bewegt, die Quoten bleiben auf «Erwartet»:

| Monate | Folgejahr CHF |
|---:|---:|
| 6 | 32 504 |
| 8 | 40 911 |
| 9 | **45 115** |
| 10 | 49 318 |
| 12 | 57 725 |

**Ein Monat durchschnittlicher Verweildauer ist rund CHF 4 200 wert.** Das
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
  Von den 274 WoS-Abos sind 87 Papier-Abos.

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
