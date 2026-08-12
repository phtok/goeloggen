# Papier-Probeabos · Fulfillmentkosten

**Stand:** 12. August 2026  
**Kampagne:** Sommer-Aktion 2026  
**Kostenansatz:** CHF 0.77 Druck + CHF 0.93 Versand = **CHF 1.70 je physisch versandtem Heft**

## Warum nicht pauschal 13 Hefte?

‹Das Goetheanum› erscheint 2026 42-mal. Im Sommer liegen mehrere Doppelnummern; eine Doppelnummer ist physisch ein Heft und verursacht Druck und Versand nur einmal. Darum wird ein dreimonatiges Probeabo nicht als `3 Monate × 4,33 Wochen` gerechnet, sondern gegen den realen Erscheinungsplan.

Für die Kampagnenkohorte relevant sind folgende Erscheinungstage:

- 3. Juli · Nr. 27–28
- 17. Juli · Nr. 29–30
- 31. Juli · Nr. 31–32
- 14. August · Nr. 33–34
- 28. August · Nr. 35
- 4. September · Nr. 36
- 11. September · Nr. 37
- 18. September · Nr. 38
- 25. September · Nr. 39–40
- 9. Oktober · Nr. 41
- 16. Oktober · Nr. 42
- 23. Oktober · Nr. 43
- 30. Oktober · Nr. 44
- 6. November · Nr. 45
- 13. November · Nr. 46

Quelle des Erscheinungsplans: Mediadaten / Erscheinungsplan ‹Das Goetheanum› 2026.

## Rechenregel

Für jede Anmeldung `wos + papier + summer26_trial` wird gezählt, wie viele physische Erscheinungstage **nach dem Anmeldetag und vor Ablauf von drei Kalendermonaten** liegen.

Der Anmeldetag selbst wird nicht mitgerechnet. Das ist konservativ und verhindert, dass ein bereits produziertes/versandtes Heft automatisch als zusätzliche Kampagnenkosten angesetzt wird. Falls der Vertrieb bestätigt, dass Anmeldungen am Erscheinungstag noch genau diese Ausgabe erhalten, muss nur diese Grenzregel angepasst werden.

Die Kampagne wird auf den offiziellen Aktionszeitraum **3. Juli bis 11. August 2026** begrenzt. Spätere Datensätze zählen nicht rückwirkend zur Aktionsrechnung.

## Ergebnis

Im Kampagnenzeitraum liegen **113 Papier-Anmeldungen** vor.

Je nach Starttag fallen innerhalb der drei Monate an:

| physische Hefte | Papier-Abos | Versandvorgänge |
| ---: | ---: | ---: |
| 8 | 10 | 80 |
| 9 | 11 | 99 |
| 10 | 44 | 440 |
| 11 | 48 | 528 |
| **Summe** | **113** | **1 147** |

Damit:

- Druck: 1 147 × CHF 0.77 = **CHF 883.19**
- Versand: 1 147 × CHF 0.93 = **CHF 1 066.71**
- **Fulfillment gesamt: CHF 1 949.90**
- Durchschnitt: **10.15 Hefte je Papier-Probeabo**
- Durchschnittliche Fulfillmentkosten: **CHF 17.26 je Papier-Probeabo**

## Einbau in die Auswertung

Der Betrag **CHF 1 949.90** ist als Kostenposten `Probeabos Papier · 1 147 Hefte × CHF 1.70` in der Kategorie `Druck & Versand` erfasst. Damit fliesst er in die vorhandene Kostensumme ein, ohne die bestehende Kostenlogik umzubauen.

Zusätzlich gibt es im Backend den Aggregat-RPC `sommer2026_papier_tage()`. Er liefert nur `Tag + Anzahl Papier-Anmeldungen` und keine Personendaten. Damit lässt sich die Rechnung später reproduzieren oder bei bestätigter Versandregel neu berechnen.

## Noch zu klären

1. Erhält eine Anmeldung **am Erscheinungstag** bereits diese Ausgabe? Aktuell: nein.
2. Beginnt der physische Bezug immer mit der nächsten Ausgabe oder gibt es redaktionelle/vertriebliche Sonderregeln?
3. Sind CHF 0.77 + CHF 0.93 echte Grenzkosten je zusätzlichem Exemplar oder Durchschnittskosten? Für die Kampagnen-Wirtschaftlichkeit sollten Grenzkosten bevorzugt werden.

Bis diese Punkte anders bestätigt sind, ist CHF 1 949.90 die nachvollziehbare Arbeitszahl.