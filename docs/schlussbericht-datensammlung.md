# Schlussbericht Sommer-Aktion — was noch einzusammeln ist

Stand 9. August 2026. Diese Liste ist zum Abhaken: Was hier steht, kann die
Datenbank **nicht** selbst holen. Alles Übrige — Anmeldungen, Ströme, Tarife,
Währungen, Herkunftsland, Kurzlink-Klicks, Selbstauskünfte — liegt bereits
vollständig im Backend und fliesst ohne Zutun in den Bericht.

**Nichts davon braucht einen Commit.** Alles wird in den Formularen der
Kampagnen-App eingetragen und ist sofort im Cockpit wirksam:

- Reichweite und Klicks je Aktivität → **Aktivitäten** (`aktivitaeten.html`),
  Knopf «Bearbeiten» in der Zeile
- Beträge → **Kosten** (`kosten.html`)

## Erledigt am 9. August: ActiveCampaign

Die Zahlen sind über die AC-API gelesen und in den Aktivitäten eingetragen.
Die Wirkungskette des Mailings steht damit:

| Welle | zugestellt | geöffnet | Öffnungsrate | Klicker | Klick je Öffner |
|---|---:|---:|---:|---:|---:|
| w1 · 17. Juli | 33 709 | 16 959 | 50,3 % | 1 954 | 11,5 % |
| w2 · 30. Juli | 33 385 | 15 449 | 46,3 % | 1 559 | 10,1 % |
| w3 · 7. August | 33 006 | 12 080 | 36,6 % | 1 237 | 10,2 % |
| w3b · 8. August | 12 974 | 5 623 | 43,3 % | 683 | **12,1 %** |
| **Summe** | **113 074** | **50 111** | **44,3 %** | **5 433** | **10,8 %** |

Newsletter: Wochenschrift 17. Juli 16 690 zugestellt / 6 917 geöffnet ·
Weekly 17. Juli 13 292 / 5 688 / 519 Klicker · Wochenschrift 31. Juli
16 797 / 6 362 · Weekly 31. Juli 13 253 / 5 394 / 580 Klicker.

**Kette des Mailings:** 113 074 zugestellt → 50 111 geöffnet → 5 433 Klicker
→ 469 gemessene Abos, mit Dunkelfeld ≈641. Aus jedem neunten Klicker wurde
ein Abo (11,8 %); aus 1 000 zugestellten Mails knapp sechs.

### Vier Befunde aus dem Abholen

1. **Korrektur der Definition: Reichweite = zugestellte Mails, nicht
   geöffnete.** Der Sammel-Auftrag verlangte zuerst die Öffnungen; das war
   falsch. Reichweite ist im Trichter die Aussetzung, nicht schon eine
   Reaktion — und nur so passt sie zur Social-Reichweite aus Metricool. Die
   Öffnungen stehen in der Notiz jeder Zeile, die Lesart bleibt damit
   umkehrbar. **Offen:** Der Newsletter vom 4. Juli trägt noch Öffnungen als
   Reichweite (3 338, zugestellt laut Notiz ~7 000) und fällt aus der
   Systematik; bei Gelegenheit die echte Zustellzahl nachholen.
2. **w3b hängt zweimal, nicht einmal** — Öffner- und Nicht-Öffner-Zweig, wie
   w3. Die Aktion hatte 36 E-Mail-Schritte, nicht 30.
3. **Der englischen Gruppe «Lesen» fehlt die letzte Welle.** Für Lesen · EN
   gibt es keine w3b-Kampagne vom 8. August. Stattdessen tragen zwei
   w3b-EN-Kampagnen das Versanddatum **15. Juli** — drei Tage **vor** der
   ersten Welle, mit 197 zugestellten Mails, 90 Öffnern, 7 Klickern. Beides
   ist erklärungsbedürftig: Entweder haben 197 englische Leser am 15. Juli ein
   «heute läuft es aus» erhalten, als die Aktion noch gar nicht angekündigt
   war, oder es war ein Testlauf auf einer internen Liste. Die 197 sind in der
   w3b-Zeile **nicht** enthalten; mit ihnen wären es 13 171 / 5 713 / 690.
4. **Bei beiden Wochenschrift-Newslettern war das Link-Tracking aus**
   (`tracklinks:none`). Ihre Klicks sind darum nicht messbar — die Zeilen
   stehen leer und **nicht** auf null. Für die nächste Aktion: vor dem Versand
   prüfen, dass Link-Tracking an ist, sonst ist der Weg blind.

**Nicht gefunden: Newsletter AGiD (27. Juli).** Im ganzen Konto existiert für
Juli 2026 keine AGiD-Kampagne. Die Zeile im Protokoll trägt den Befund als
Notiz und zählt bis zur Klärung als geplant, nicht als ausgespielt.

## Erledigt am 10. August: Abgleich goetheanum.tv gegen Uscreen

Vollexport aller Konten, zeilenweise gejoint. Befund und Folgen stehen in
`docs/uscreen-abgleich-10-08.md`. Kurz: Uscreen kennt **626** neue Abos im
Fenster, wir zählen 665 — 40 unserer Zeilen sind Verlängerungen, 11 echte
Abos aus dem Juli fehlen uns. Die Gratismonate sind bei 620 von 626 gebucht;
der Verlust liegt nicht bei der Frist, sondern an der Kasse (268 Abbrüche
ohne Rückkehr).

## Noch einmal ActiveCampaign — zwei Sorten Zahlen, die nur dort liegen

Der erste Lauf hat Summen je Welle geholt. Für den Bericht fehlen zwei Dinge,
die keine andere Quelle hat. Beides sind **Summen, keine Listen** — es braucht
keine Kontaktdaten:

1. **Die Nenner je Gruppe.** Bisher haben wir jede Welle über alle sechs
   Automatisierungen zusammengezählt. Gebraucht wird die Aufschlüsselung
   **je Automatisierung** (`Lesen`, `Sehen`, `Beides` × DE/EN) mal **je Welle**
   — 24 Zeilen mit zugestellt, geöffnet, geklickt. Erst damit lässt sich
   rechnen, welche **Gruppe** wie gut konvertiert hat: Unsere Abschlüsse
   tragen die Gruppe im `utm_content` (`_noabo`, `_nurws`, `_nurtv`), aber
   ohne den Nenner ist das nur eine absolute Zahl. Die Quote je Gruppe ist die
   Zahl, mit der die nächste Aktion geplant wird.
2. **Abmeldungen und Bounces je Welle.** Vier Wellen auf rund 33 000 Adressen
   sind nicht gratis. Was die Aktion an Verteilerqualität gekostet hat, ist
   bisher nirgends verbucht — es gehört auf die Kostenseite, auch ohne
   Frankenbetrag.

**Nicht holen:** Kontaktlisten auf Personenebene. Sie liessen sich ohne
E-Mail-Adressen nicht gegen Uscreen legen, und die Frage ‹wer hat geklickt und
doch nicht abgeschlossen› ist über Uscreen bereits beantwortet (227 abgebrochene
Kassengänge mit Mailing-Spur).

## Traffic der Aktionsseiten — was wir haben und was fehlt (Frage vom 10. August)

**Die Aktionsseiten selbst zählen nicht mit.** Auf
`global-sommer2026.goetheanum.online`, `ws-sommer2026.dasgoetheanum.com` und
`tv-sommer2026.goetheanum.tv` läuft keine Reichweiten-Messung — es gibt also
keine Seitenaufrufe, keine Verweildauer, keine Absprungrate. Das ist die
grösste blinde Stelle der Auswertung.

**Der Weg dorthin ist trotzdem gemessen**, an der Quelle statt am Ziel:

| Was | Zahl | Woher |
|---|---:|---|
| Klicks auf Aktionslinks, alle Aktivitäten zusammen | 10 589 | Aktivitäten-Protokoll (AC, Meta, YouTube) |
| davon Klicker der vier Mail-Wellen | 5 433 | ActiveCampaign |
| Klicks auf die Kurzlinks (Print, QR, Social) | 2 333 | eigene Weiterleitung |
| neue Konten auf goetheanum.tv | 874 | Uscreen |
| abgeschlossene Abos goetheanum.tv | 626 | Uscreen |

Aus 10 589 Klicks wurden 874 Konten und 626 Abos. Die Kurzlink-Klicks je Ziel:
Übersicht 1 529 · goetheanum.tv 401 · Wochenschrift 363.

**Für die nächste Aktion:** ein leichtgewichtiger Zähler auf den Aktionsseiten
(dieselbe Weiterleitung, die die Kurzlinks zählt, kann das) — damit die Lücke
zwischen ‹Klick im Mail› und ‹Konto angelegt› sichtbar wird. Heute ist sie eine
Differenz, die wir ausrechnen, statt einer Zahl, die wir messen.

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

Stand 10. August: **CHF 769.70** erfasst — Druck 309.70, Meta-Anzeige 423,
YouTube-Anzeige 37. Damit ist der teuerste Weg endlich bewertbar. Was noch
fehlt, hält Kosten je Abo und Rückfluss weiterhin leer.

- ~~**Meta-Anzeige**~~ — **erledigt 10. August** (CHF 423). Reichweite und
  Klicks standen bereits (62 812 / 353 und 68 343 / 612).
- **Interne Stunden** — Kategorie **Stunden intern**, grobe Schätzung genügt.
  Ohne sie liest sich die Aktion billiger, als sie war. Die Maske fragt jetzt
  nach **Stunden und Ansatz** und rechnet die Franken selbst; eingetragen
  werden also 8 Stunden zu 60, nicht 480. **Der Hausansatz ist CHF 60 je
  Stunde** (festgelegt am 10. August 2026) und steht in der Maske
  voreingestellt — er ist damit über alle Posten hinweg derselbe, sonst
  vergleicht der Bericht Stunden, die verschieden viel wert sind.
- **Flyer und Stand** — Druck ist erfasst; fehlen noch Reichweite für «Auslage
  Flyer Empfang» und «Auslage Flyer Buchhandlung» (10. Juli). Wo nichts
  gemessen ist: verteilte Stückzahl eintragen und das in der Notiz sagen.

## Zwei Arten von Kosten — nicht vermischen (Hinweis 9. August)

Bisher kennt das Cockpit **eine** Sorte Kosten: einmalige Kampagnenkosten
(Druck, Anzeige, Stunden), verteilt über alle Abos. Das reicht nicht. Es kommt
eine zweite Sorte dazu — **Stückkosten je Abo und Jahr**, und die sind je Strom
verschieden:

| Strom | Stückkosten | Bemerkung |
|---|---|---|
| Wochenschrift **Papier** | Druck + Porto je Heft | grob rechenbar; **darf nicht auf alle Abos verteilt werden** |
| goetheanum.tv | Gebühr je Uscreen-Abo | folgt |
| Wochenschrift **Digital** | keine | durch die laufende Infrastruktur gedeckt |

Die Folge für den Bericht ist nicht kosmetisch: Aus dem Folgejahr-**Umsatz**
wird erst mit diesen Zahlen ein **Deckungsbeitrag**. Und weil die Stückkosten
am Papier hängen, verschiebt sich damit auch die Rangfolge der Ströme — ein
Papier-Abo bringt mehr Umsatz und kostet mehr; ob es netto mehr trägt als ein
digitales, ist heute unbeantwortet.

Zu sammeln sind darum **je Strom zwei Zahlen**: Herstellkosten je Ausgabe und
Portokosten je Ausgabe (Wochenschrift Papier, je Zone, wenn es sich unterscheidet)
sowie die Uscreen-Gebühr je Abo und Monat. Sobald sie vorliegen, bekommt das
Cockpit eine eigene Struktur dafür (`CONFIG.stueckkosten` je Strom) — vorher
nicht: Eine leere Struktur mit Nullen darin sähe aus wie «kostet nichts».

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

1. ~~Mail-Wellen (4 Einträge)~~ — **erledigt 9. August**
2. ~~Newsletter (4 von 5)~~ — **erledigt 9. August**, AGiD offen
3. **Meta-Kosten (1 Eintrag)** — jetzt der grösste Hebel: Er macht den
   teuersten Weg der Aktion bewertbar
4. Social (6 Einträge)
5. Stunden, Flyer, die zwei offenen Fragen, AGiD klären
