# Schlussbericht Sommer-Aktion — was noch einzusammeln ist

Stand 13. August 2026 (Aktion endete am 11. August). Diese Liste ist zum Abhaken: Was hier steht, kann die
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

## Erledigt am 10. August: die Nenner je Gruppe

Zweiter AC-Lauf ausgeführt. Auswertung in `docs/mailing-gruppen-10-08.md`.
Kurz: Die Gruppe **Lesen** (Wochenschrift-Leser, 922 angeschrieben) wandelte
**11,2 %** der Angeschriebenen und **53,4 % der Klicker** in ein TV-Abo — die
Gruppe **Sehen** (TV-Abonnenten, Wochenschrift angeboten) trotz der besten
Klickrate nur **0,91 %** beziehungsweise 3,8 %. Dazu: **549 Abmeldungen** als
bisher unverbuchte Kostenseite, und zwei Fehler in der Mail-Strecke.

**Offen bleibt allein die AC-Monatsgebühr** — die Abrechnung liegt beim
Konto-Inhaber in einem eigenen Portal und war nicht einsehbar. Der
Verteilschlüssel steht: Die vier Wellen verbrauchten 9,4 % des Sendekontingents.

## Erledigt am 10. August: Einnahmen-Perspektive und Cockpit nachgezogen

Die Zählregel hat die Basis verschoben, darum ist beides neu gerechnet und
neu geschrieben:

- **`docs/einnahmen-perspektive-10-08.md`** löst die Fassung vom 8. August ab.
  Basis jetzt **1 042 Anmeldungen, 1 019 aktiv** (vorher 902). Erwartet
  **CHF 65 877** statt 58 497, Decke 149 306, ein Monat Verweildauer rund
  CHF 6 200 statt 5 500. **Quoten und Monats-Faktoren sind unverändert** — es
  hat sich allein die Menge geändert. `CONFIG.szenarien.doc` zeigt auf die
  neue Fassung.
- **Die Nenner je Gruppe stehen im Cockpit** (`CONFIG.mailingGruppen`).
  Abschnitt «Wer sind die Neuen» sortiert die drei Gruppen jetzt nach der
  Quote je Klicker statt nach der Menge und zeigt je Gruppe angeschrieben,
  Klicker, Abo je Angeschriebenem, Abo je Klicker sowie die Sprachzeilen.
- **Was der Versand den Verteiler gekostet hat** (`CONFIG.verteiler`) steht
  im Abschnitt «Was hat funktioniert» beim Gebiet Mailing: 549 Abmeldungen,
  46 harte und 118 weiche Rückläufer, 9,4 % des Sendekontingents.
- **Abschnitt «Schlüsse und Perspektiven» neu geschrieben.** Vier neue
  Absätze aus der Gruppen-Auswertung; die Aussage «Quer-Angebot rund
  dreimal so oft» ist korrigiert — gemessen ist es das **Zwölffache**
  (11,2 % gegen 0,91 % je Angeschriebenem).

## Erledigt am 13. August: Kosten vollständig, Sehen-Ursache geklärt

Vier Entscheide des Auftraggebers, alle umgesetzt:

1. **Interne Stunden sind eingetragen** — 40 Stunden Landing Pages und
   technische Klärungen, 60 Stunden Kampagnenmonitor, Mailings, Entwürfe und
   Zuarbeiten, macht **CHF 6 000** zum Hausansatz CHF 60. Zusammen mit den
   bereits erfassten Beträgen (Druck, Meta, YouTube) und dem separat
   hergeleiteten Papier-Fulfillment der Probeabos (`docs/probeabo-kosten-12-08.md`,
   CHF 1 949.90) stehen jetzt **CHF 9 014.60** in der Datenbank.
2. **`CONFIG.kostenVollstaendig` steht auf `true`.** Kosten je Abo und
   Rückfluss zeigen ab jetzt echte Zahlen statt eines Platzhalters: **CHF 8.65
   je Anmeldung, Rückfluss 7,3-fach** (gegen die Szenario-Mitte «Erwartet»,
   CHF 65 877 — siehe unten, «Nicht vollständig» weiterhin zutreffend für
   Metricool/Flyer/Papier-Stückkosten, siehe «Zwei Arten von Kosten»).
3. **Die AC-Monatsgebühr ist als Schätzung eingetragen**, nicht weiter
   nachgefragt: CHF 95 (9,4 % Versandanteil auf angenommene CHF 1 000/Monat
   Grundgebühr, ungeprüft — Herleitung in `docs/mailing-gruppen-10-08.md`).
   Als Kostenposten «ActiveCampaign-Anteil …» in der Kategorie
   Infrastruktur, mit dem Wort «Schätzung» im Posten-Text selbst markiert.
4. **Die Sehen-Ursache ist geklärt — durch Widerlegung, nicht Bestätigung.**
   Die Mail-Betreffzeilen standen bereits im Repo
   (`services/mailing-sommer2026/AC-AUTOMATION.md`); der Vergleich gegen die
   Lesen-Automation widerlegt die Hypothese vom letzten Eintrag («Betreff
   verwechselbar mit dem eigenen Abo»). Es gibt keinen Textfehler zu beheben.
   Die wahrscheinlichste Erklärung ist strukturell: Ein Leseabo zu beginnen
   ist ein grösserer Schritt als ein Video anzuklicken — eine Erkenntnis für
   die nächste Aktion, keine Korrektur an dieser. Herleitung in
   `docs/mailing-gruppen-10-08.md`.

**Bewusst nicht getan:** Die 268 Kassenabbrecher bei goetheanum.tv
anzuschreiben. Der Auftraggeber hat sich dagegen entschieden — die Analyse
bleibt im Dokument stehen, damit sie nicht als vergessener Punkt wiederkehrt.

**Auf später verschoben, nicht mehr in der Bearbeitungsreihenfolge:**
Metricool-Zahlen, Flyer-Reichweite, der fehlende AGiD-Newsletter, die
Inserate VaG/RSV und der Zoho-Abgleich der Wochenschrift. Der Auftraggeber
hat sie ausdrücklich als verzichtbare Ergänzung eingestuft — der Bericht
ist ohne sie fertig, sie verbessern ihn, wenn sie einmal anfallen. Details
weiterhin unten, jetzt unter «Spätere Ergänzung».

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

Dazu die AC-Kosten selbst (Tarif, Kontingent, Gebühr) — sie sind bisher
nirgends verbucht. Fertiger Auftrag: `services/mailing-sommer2026/AC-NENNER.md`.

**Nicht holen: Kontaktlisten auf Personenebene.** Sie *würden* etwas sagen —
mit den Adressen liesse sich Klick gegen Abschluss legen, und das Dunkelfeld
wäre gemessen statt geschätzt. Dagegen stehen zwei Dinge: Personendaten aus
zwei Systemen zusammenzuführen ist ein eigener Vorgang mit eigener
Rechtsgrundlage, und die Frage ‹wer hat geklickt und doch nicht abgeschlossen›
ist über Uscreen bereits beantwortet (227 abgebrochene Kassengänge mit
Mailing-Spur). Die Nenner je Gruppe bringen fast dieselbe Erkenntnis ohne eine
einzige Adresse.

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

## Geld (Meta Ads Manager und eigene Aufzeichnung)

**Stand 13. August: CHF 9 014.60, vollständig erfasst.** Druck & Versand
2 259.60 (davon 1 949.90 Papier-Fulfillment der Probeabos, siehe unten),
Social 460 (Meta 423, YouTube 37), Stunden intern 6 000 (100 Stunden ×
CHF 60), Infrastruktur 295 (Lovable 200, AC-Anteil geschätzt 95).
`CONFIG.kostenVollstaendig` steht auf `true` — Kosten je Abo (CHF 8.65) und
Rückfluss (7,3-fach) zeigen im Cockpit echte Zahlen.

Was in dieser Summe **absichtlich fehlt** und keine allgemeine Kampagnenkosten
sind, sondern eine andere Rechnung (siehe «Zwei Arten von Kosten» unten): die
laufende, jährlich wiederkehrende Uscreen-Gebühr je zahlendem Abo.

## Zwei Arten von Kosten — nicht vermischen (Hinweis 9. August)

Das Cockpit rechnet **eine** Sorte Kosten in der Summe oben: einmalige
Kampagnenkosten (Druck, Anzeige, Stunden), verteilt über alle Abos. Das reicht
für «was hat die Aktion gekostet» — nicht für «was bleibt vom Folgejahr-Umsatz
übrig». Dafür braucht es eine zweite Sorte, **Stückkosten je Abo und Jahr**, je
Strom verschieden:

| Strom | Stückkosten | Bemerkung |
|---|---|---|
| Wochenschrift **Papier**, Trial-Zeit | Druck + Porto je Heft | **erledigt** — CHF 1 949.90 für 1 147 Hefte, `docs/probeabo-kosten-12-08.md`, bereits in der Summe oben |
| Wochenschrift **Papier**, Folgejahr | Druck + Porto je Heft und Jahr | offen — dieselbe Rechnung, für die Jahre **nach** der Gratiszeit, **nicht** in der Kostensumme, sondern gegen den Folgejahr-Umsatz zu stellen |
| goetheanum.tv | Gebühr je Uscreen-Abo und Monat | offen |
| Wochenschrift **Digital** | keine | durch die laufende Infrastruktur gedeckt |

Die Trial-Fulfillmentkosten (erste Zeile) sind eine **einmalige** Ausgabe der
Kampagne — sie gehören zur Kostensumme oben und sind dort drin. Die zweite und
dritte Zeile sind etwas anderes: eine **wiederkehrende** Ausgabe für jedes Jahr,
in dem ein Abo bezahlt weiterläuft. Erst mit ihr wird aus dem Folgejahr-Umsatz
(`docs/einnahmen-perspektive-10-08.md`) ein Deckungsbeitrag. Diese Zahlen fehlen
weiterhin und stehen als «Spätere Ergänzung» unten.

## Spätere Ergänzung — verzichtbar, auf Wunsch des Auftraggebers zurückgestellt (13. August)

Fünf Punkte, keiner davon hält den Bericht auf. Sie verbessern ihn, sobald sie
anfallen — niemand muss sie aktiv beschaffen:

- **Social (Metricool), 6 Einträge ohne vollständige Zahlen** — Kampagnen-
  Auswertung im geschützten Dashboard, Link im Cockpit unter «Methode und
  Quellen»: Reel WS Wolfgang (10.7., fehlt Klicks), Reel GTV Thijs (12.7.,
  fehlt Klicks, Reichweite 3 wirkt wie ein Tippfehler), Karussell GTV (16.7.),
  Karussell WS (19.7.), Reel letzte Erinnerung WS (31.7.), Reel letzte
  Erinnerung GTV (2.8.) — bei den letzten vier fehlen Reichweite und Klicks.
- **Flyer- und Stand-Reichweite** — Druck ist erfasst (CHF 82.50 + 55, oben);
  es fehlt, wie viele Flyer «Auslage Empfang» und «Auslage Buchhandlung»
  (10. Juli) tatsächlich mitgenommen wurden.
- **Inserate VaG und RSV** (13. Juli, Notiz «Bei Bruno Zweifel angefragt») —
  ob sie überhaupt erschienen sind, ist unbestätigt.
- **Abgleich Wochenschrift gegen Zoho** — 359 WoS-Anmeldungen sind Paperform-
  Einreichungen; Zoho ist der Wahrheitsstand für Abonnements. Ohne Abgleich
  bleibt offen, wie viele Dubletten oder Fehleinträge die 406 WoS-Anmeldungen
  enthalten. (goetheanum.tv braucht das nicht — dort schreibt der Webhook
  direkt.)
- **Uscreen-Gebühr je Abo und Monat, Papier-Stückkosten fürs Folgejahr** — die
  zweite Kostensorte oben; ohne sie bleibt der Folgejahr-Umsatz ein Umsatz,
  kein Deckungsbeitrag.

## Bewusst nicht getan (13. August)

**Die 268 Kassenabbrecher bei goetheanum.tv anschreiben.** Sie sind bei
Uscreen samt Abbruchzeitpunkt bekannt, die Abandoned-Checkout-Mail bringt
Uscreen serienmässig mit, war aber nicht scharf geschaltet. Der Auftraggeber
hat sich gegen ein Nachfassen entschieden. Herleitung und Zahl bleiben in
`docs/mailing-gruppen-10-08.md` stehen, damit die Analyse nicht als offener
Punkt zurückkommt — die Entscheidung ist gefallen, nicht das Wissen fehlt.

## Was NICHT jetzt eingesammelt wird

Die **Bleibe-Quote**. Die Aktion ist «3 Monate gratis»; die erste Kohorte
entscheidet frühestens Anfang Oktober. Bis dahin bleibt der Folgejahr-Umsatz
eine Rechnung in drei Szenarien
(`docs/einnahmen-perspektive-10-08.md`) — der Schlussbericht sollte das so
sagen und die Zahl nicht härter machen, als sie ist.

## Reihenfolge

Alles hier Genannte ist entweder erledigt oder bewusst zurückgestellt — es
gibt aktuell **keinen offenen Blocker** für den Schlussbericht.

1. ~~Mail-Wellen (4 Einträge)~~ — **erledigt 9. August**
2. ~~Newsletter (4 von 5)~~ — **erledigt 9. August**, AGiD auf später verschoben
3. ~~Meta- und YouTube-Kosten~~ — **erledigt 10. August**
4. ~~Uscreen-Vollabgleich und Zählregel~~ — **erledigt 10. August**
5. ~~Nenner je Gruppe (zweiter AC-Lauf)~~ — **erledigt 10. August**
6. ~~Einnahmen-Perspektive neu rechnen, Erkenntnisse ins Cockpit~~ —
   **erledigt 10. August**
7. ~~Interne Stunden, `CONFIG.kostenVollstaendig`~~ — **erledigt 13. August**
8. ~~AC-Monatsgebühr~~ — **erledigt 13. August** (als Schätzung, CHF 95)
9. ~~Sehen-Gruppe: Ursache prüfen~~ — **erledigt 13. August** (widerlegt,
   nicht bestätigt — Herleitung in `docs/mailing-gruppen-10-08.md`)
10. ~~Kassenabbrecher anschreiben~~ — **entschieden: nicht** (13. August)
11. Was übrig bleibt, steht unter «Spätere Ergänzung» — freiwillig, nicht
    Teil der Berichtspflicht.
