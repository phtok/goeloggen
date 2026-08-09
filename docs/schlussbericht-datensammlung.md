# Schlussbericht Sommer-Aktion — was noch einzusammeln ist

Stand 8. August 2026. Diese Liste ist zum Abhaken: Was hier steht, kann die
Datenbank **nicht** selbst holen. Alles Übrige — Anmeldungen, Ströme, Tarife,
Währungen, Herkunftsland, Kurzlink-Klicks, Selbstauskünfte — liegt bereits
vollständig im Backend und fliesst ohne Zutun in den Bericht.

**Nichts davon braucht einen Commit.** Alles wird in den Formularen der
Kampagnen-App eingetragen und ist sofort im Cockpit wirksam:

- Reichweite und Klicks je Aktivität → **Aktivitäten** (`aktivitaeten.html`),
  Knopf «Bearbeiten» in der Zeile
- Beträge → **Kosten** (`kosten.html`)

## Zuerst: die vier Mail-Wellen (ActiveCampaign)

Der wichtigste Posten. Das Mailing trägt rund 69 Prozent der Aktion, und
genau dort ist die Wirkungskette leer: keine Reichweite, keine Klicks. Ohne
diese acht Zahlen lässt sich für den stärksten Kanal weder eine Klickquote
noch ein Preis je Abo rechnen.

| Aktivität | Datum | fehlt |
|---|---|---|
| Mail-Welle 1 «Ankündigung» | 17. Juli | Reichweite, Klicks |
| Mail-Welle 2 «Erinnerung» | 30. Juli | Reichweite, Klicks |
| Mail-Welle 3 «morgen läuft es aus» | 7. August | Reichweite, Klicks |
| Mail-Welle 3b «heute läuft es aus» | 8. August | Reichweite, Klicks |

**Zwei Definitionen, damit die Zahlen vergleichbar bleiben** — so ist der
Newsletter vom 4. Juli erfasst, und so sollten es alle sein:

- **Reichweite = geöffnete Mails**, nicht versendete.
- **Klicks = eindeutige Klicker (Personen)**, nicht Klick-Ereignisse.

Weicht eine Zahl davon ab, gehört das in die öffentliche **Notiz** der Zeile —
sonst rechnet der Bericht Äpfel gegen Birnen. Jede Welle bestand aus sechs
Mails (Lesen/Sehen/Beides × DE/EN); für die Wirkungskette zählt die **Summe**
über alle sechs.

## Dann: die Newsletter (ActiveCampaign)

| Aktivität | Datum |
|---|---|
| Newsletter Wochenschrift | 17. Juli · 31. Juli |
| Newsletter Weekly | 17. Juli · 31. Juli |
| Newsletter AGiD | 27. Juli |

Gleiche zwei Definitionen. Die Newsletter tragen laut Lesart rund 12 Prozent
der Aktion — nach dem Mailing der zweitgrösste Posten ohne Zahlen.

## Social (Metricool)

Sechs Einträge, alle ohne vollständige Zahlen. Die Kampagnen-Auswertung liegt
im geschützten Metricool-Dashboard; der Link steht im Cockpit unter «Methode
und Quellen».

| Aktivität | Datum | fehlt |
|---|---|---|
| Reel WS: Wolfgang | 10. Juli | Klicks |
| Reel GTV: Thijs | 12. Juli | Klicks (Reichweite 3 prüfen — wirkt wie ein Tippfehler) |
| Karussell GTV | 16. Juli | Reichweite, Klicks |
| Karussell WS | 19. Juli | Reichweite, Klicks |
| Reel: letzte Erinnerung WS | 31. Juli | Reichweite, Klicks |
| Reel: Letzte Erinnerung GTV | 2. August | Reichweite, Klicks |

## Geld (Meta Ads Manager und eigene Aufzeichnung)

In der Datenbank stehen bisher **nur CHF 309.70 Druck**. Damit sind Kosten je
Abo und Rückfluss auf der Kosten-Seite zu günstig — und ausgerechnet der
teuerste Weg fehlt.

- **Meta-Anzeige** — Betrag aus dem Ads Manager (Rechnung Juli), Kategorie
  **Social Media**. DE und EN dürfen zusammengefasst werden. Reichweite und
  Klicks der Anzeige stehen bereits (62 812 / 353 und 68 343 / 612). Ist die
  Zahl da, steht neben dem Befund «≈9 Abos» endlich ein Preis.
- **Interne Stunden** — Kategorie **Stunden intern**, grobe Schätzung genügt.
  Ohne sie liest sich die Aktion billiger, als sie war.
- **Flyer und Stand** — Druck ist erfasst; fehlen noch Reichweite für «Auslage
  Flyer Empfang» und «Auslage Flyer Buchhandlung» (10. Juli). Wo nichts
  gemessen ist: verteilte Stückzahl eintragen und das in der Notiz sagen.

## Zwei offene Fragen, keine Zahlen

- **Inserate VaG und RSV** (13. Juli, Notiz «Bei Bruno Zweifel angefragt») —
  sind sie überhaupt erschienen? Wenn nein, gehören die Zeilen als
  «nicht erschienen» in die Notiz, sonst zählen sie als stumme Wege gegen die
  Kampagne. Wenn ja: Reichweite beim Betreiber erfragen.
- **Abgleich Wochenschrift gegen Zoho** — die 359 WoS-Anmeldungen sind
  Paperform-Einreichungen. Wahrheitsstand für Abonnements ist Zoho. Für den
  Bericht zählt, wie viele davon dort als Abo angelegt sind; die Differenz sind
  Dubletten oder Fehleinträge und gehören benannt, nicht stillschweigend
  mitgezählt. (goetheanum.tv braucht diesen Abgleich nicht — dort schreibt der
  Uscreen-Webhook direkt.)

## Was NICHT jetzt eingesammelt wird

Die **Bleibe-Quote**. Die Aktion ist «3 Monate gratis»; die erste Kohorte
entscheidet frühestens Anfang Oktober. Bis dahin bleibt der Folgejahr-Umsatz
eine Rechnung in drei Szenarien
(`docs/einnahmen-perspektive-08-08.md`) — der Schlussbericht sollte das so
sagen und die Zahl nicht härter machen, als sie ist.

## Reihenfolge

1. Mail-Wellen (4 Einträge) — der grösste Hebel
2. Meta-Kosten (1 Eintrag) — macht den teuersten Weg bewertbar
3. Newsletter (5 Einträge)
4. Social (6 Einträge)
5. Stunden, Flyer, die zwei offenen Fragen

Nach Punkt 1 und 2 ist der Bericht schon erzählbar; alles Weitere schärft ihn.
