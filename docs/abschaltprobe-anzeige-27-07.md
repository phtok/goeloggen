# Abschalt-Probe der bezahlten Anzeige — Ergebnis, 27. Juli 2026

Die Lesart vom 24. Juli (`wirkungs-lesart-24-07.md`) empfahl als ersten Zug,
die bezahlte Meta-Anzeige auszusetzen und die Anmeldungen zu vergleichen —
«das beantwortet ‹5 oder 60› endgültig, und zwar in Abos, nicht in
Zuordnungswahrscheinlichkeiten». Die Anzeige ist inzwischen gestoppt. Hier
das Ergebnis.

**Kurz: Die Anzeige hat nicht nichts gebracht, aber sehr wenig — rund ein
Abo pro Tag, im Zweifel weniger. Die ≈44 der Lesart vom 22. Juli sind
endgültig widerlegt; die ≈9 der Lesart vom 24. Juli halten stand.**

## Wann die Anzeige aufhörte

Aus den Kurzlink-Zählern (`sommer2026_links_public`, Codes `dachs-4` DE und
`elster-2` EN), gemessen an drei Zeitpunkten:

| Stichtag | Klicks der Anzeige | Zuwachs |
|---|---:|---|
| 22. Juli | 597 | — |
| 24. Juli | 713 | +116 in 2 Tagen (~58/Tag) |
| 27. Juli | 716 | **+3 in 3 Tagen (~1/Tag)** |

Die Anzeige lief also bis zum 24. Juli und ist seither aus; der letzte
Einzelklick fiel am 26. Juli.

## Der Vergleich

Verglichen werden die goetheanum.tv-Anmeldungen je Tag — das Ziel der
Anzeige — in zwei Fenstern, beide nach dem Abklingen der Mailing-Welle.
Die Klick-Mengen je Weg stammen aus der Differenz derselben Zähler.

| | Anzeige AN (22.–24.) | Anzeige AUS (24.–27.) |
|---|---:|---:|
| Klicks der Anzeige | **58/Tag** | **1/Tag** |
| Klicks Newsletter | 40/Tag | 40/Tag |
| Klicks Social | 8/Tag | 16/Tag |
| Klicks Mailing | 0/Tag | 9/Tag |
| **goetheanum.tv-Anmeldungen** | **8,5/Tag** | **7,7/Tag** |

Der bezahlte Weg verliert **57 Klicks am Tag** — über die Hälfte des
gesamten Klick-Aufkommens. Die Anmeldungen fallen um **0,8 am Tag**.

Zwei Einschränkungen, beide gegen die Anzeige:

- Im Abschalt-Fenster laufen Social und Mailing **stärker** als vorher
  (+8 bzw. +9 Klicks/Tag). Sie fangen einen Teil des Rückgangs auf; der
  Anteil der Anzeige an den 0,8 ist damit eher kleiner als grösser.
- Das Fenster ist mit drei Tagen kurz. Eine einzelne gute Tageskurve
  (25. Juli mit 12 Anmeldungen) hebt den Schnitt spürbar.

Hochgerechnet auf die ganze Laufzeit der Anzeige (~10 Tage, 716 Klicks)
ergibt das eine Grössenordnung von **rund 8–12 Abos** — genau das Band, das
die Lesart vom 24. Juli aus Placebo-Probe, Tageskurve und Selbstauskunft
angesetzt hatte (≈9, Band 4–18). Die Anteile in `CONFIG.dunkel` bleiben
darum unverändert; sie sind jetzt zusätzlich empirisch gestützt.

## Der zweite, unabhängige Beleg

Die «vermutete Herkunft» im Ereignis-Protokoll zeigt das Artefakt der alten
Lesart in Reinform. Zahl der dunklen Anmeldungen, denen der zeitlich
nächste Klick auf die Anzeige zugeordnet wurde:

| Tag | 17. | 18. | 19. | 20. | 21. | 22. | 23. | **24.** | **25.** | **26.** | **27.** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| «vermutet: meta-anzeige» | 8 | 16 | 9 | 5 | 4 | 3 | 3 | **0** | **0** | **0** | **0** |

Der Anker verschwindet mit dem letzten Klick vollständig — **die dunklen
Anmeldungen aber bleiben** (dunkle goetheanum.tv-Abschlüsse: 5,7/Tag mit
Anzeige, 4,7/Tag ohne). Sie werden jetzt einfach dem zugeordnet, was
stattdessen klickt: Newsletter, Facebook, Mailing. Genau so verhält sich
ein Zufallstreffer, nicht eine Ursache.

## Hart gemessen bleibt es bei eins

Über die ganze Laufzeit trägt genau **eine** Anmeldung die UTM-Spur der
Anzeige (`meta-anzeige / story_statisch`), bei 716 Klicks. Die Kette ist
geprüft und intakt (siehe `utm-ablauf.md`) — die Klicks gehen also nicht
verloren, sie werden kaum zu Abos.

## Was daraus folgt

1. **Nicht wieder einschalten**, solange kein eigenes Uscreen-Angebot je
   bezahltem Weg eingerichtet ist (`uscreen-angebot-attribution-auftrag.md`).
   Erst dann ist der Ertrag serverseitig zählbar statt schätzbar.
2. **Die Kosten der Anzeige fehlen im Cockpit.** Erfasst sind nur Flyer und
   Roll-Ups (CHF 310). Ohne den Anzeigen-Betrag lässt sich der teuerste
   Posten der Aktion nicht gegen ~10 Abos rechnen — eine Zeile unter Kosten
   schliesst die letzte offene Frage.
3. **Der frei gewordene Aufwand gehört in die Mail-Wellen.** Welle 1 trug
   87 gemessene Abschlüsse; Welle 2 (30. Juli) und 3 sind vorbereitet und
   tragen seit kurzem Kurzcodes — ihre Klicks werden damit erstmals sichtbar.

## Prüfweg (wiederholbar)

Klick-Differenzen je Weg aus zwei Abrufen von `sommer2026_links_public` zu
verschiedenen Zeitpunkten; Anmeldungen je Tag aus `sommer2026_timeline`;
die Verteilung der vermuteten Herkunft aus `sommer2026_ereignisse`. Alle
drei sind offene Aggregat-RPCs — die Probe braucht keinen Datenbankzugriff
und lässt sich jederzeit wiederholen.
