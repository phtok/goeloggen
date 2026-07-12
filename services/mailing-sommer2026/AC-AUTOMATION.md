# Prompt für Claude-Chrome: ActiveCampaign-Struktur «Sommer-Aktion 2026» (S26)

> **Dies ist der fertige Prompt für den Automation-Aufbau.** Alles ab der
> Trennlinie unten Claude-Chrome (Cowork) geben. Die Mail-Tabelle wird aus
> `heroes.json` erzeugt — nach einer Copy-Änderung: `python3 build_editor.py
> --publish` und `python3 ac_prompt.py --write`, dann ist dieser Prompt wieder
> aktuell. Betreffe/URLs unten nicht von Hand ändern.

---

Baue in ActiveCampaign die Automatisierungen für unser Drei-Wellen-Mailing
«Sommer-Aktion 2026» (3 Monate gratis: Wochenschrift und/oder goetheanum.tv,
Frist Samstag, 8. August 2026). Es gibt 20 fertige, versandfähige Mails —
je Segment die Wellen × DE/EN: NurTV 6, NurWS 6, NoAbo 8 (dort kommt der
Mini-Reminder w3b dazu); der HTML-Quelltext jeder Mail liegt unter einer
festen URL (Tabelle unten). Orientiere dich am Stil der bestehenden
Automatisierungen GTV26 (DE /builder/104, EN /builder/107) — aber baue neu
nach dieser Struktur. Ändere nichts an den bestehenden Automatisierungen.

## Deine zwei Fragen, beantwortet

- **(a) Sprache** erkennst du an der Trigger-Liste: «Sonderangebote» = DE,
  «Special Offers» = EN. Beide Listen als Eintritt, danach If/Else auf die
  Listen-Mitgliedschaft.
- **(b) Die drei Gruppen** unterscheiden sich über die Abo-Tags:
  - **NurTV** = hat das GTV-Abonnent-Tag, aber kein Wochenschrift-Abo-Tag → bekommt das Wochenschrift-Angebot (Cross-sell)
  - **NurWS** = hat das Wochenschrift-Abo-Tag, aber kein GTV-Tag → bekommt das goetheanum.tv-Angebot (Cross-sell)
  - **NoAbo** = keines von beiden → bekommt beide Angebote
  - **Beide Tags** (Doppel-Abonnenten) sind überall ausgeschlossen (bekommen später separat eine Empfehlungsmail).

  **Wichtig:** Schlag die exakten Tag-Namen im Konto nach (GTV heisst
  vermutlich «GTV Abonnent»; wie das Wochenschrift-Pendant heisst, weiss ich
  nicht sicher). Notiere mir am Ende, welche Tags du verwendet hast.

## Struktur: drei Automatisierungen (nicht eine)

Eine je Segment — **S26 · NurTV→WS**, **S26 · NurWS→TV**, **S26 · NoAbo** —
mit dem Sprach-Split jeweils innen. Gründe: jedes Segment hat ein eigenes
Conversion-Ziel (anderes Abo-Tag), NoAbo hat eine Welle mehr (w3b), und das
Reporting bleibt je Segment lesbar.

### Aufbau jeder Automatisierung

1. **Start-Trigger:** Tag **«S26-Start»** wird hinzugefügt (einmaliger Lauf).
   Der Bestand tritt NICHT über die Listen-Anmeldung ein (die feuert nur bei
   Neuanmeldungen!), sondern indem wir das Tag per Bulk auf den Adressstamm
   setzen — erst wenn alle drei Automatisierungen aktiv sind.
2. **Hygiene-Filter** direkt nach dem Start: Wer in den letzten 12 Monaten
   keine Kampagne geöffnet hat → Automatisierung beenden (Zustellbarkeit).
3. **Segment-Weiche** (macht die drei Automatisierungen überschneidungsfrei):
   - NurTV→WS: If/Else «hat GTV-Tag UND hat NICHT WS-Tag» — No → Ende
   - NurWS→TV: If/Else «hat WS-Tag UND hat NICHT GTV-Tag» — No → Ende
   - NoAbo: If/Else «hat WEDER GTV- NOCH WS-Tag» — No → Ende
4. **Sprach-Split:** If/Else «ist in Liste ‹Special Offers›» → EN-Zweig,
   sonst DE-Zweig. Beide Zweige sind strukturell identisch, nur mit den
   jeweiligen Mails.
5. **Wellen-Drip je Sprach-Zweig** (Zeiten = Schweizer Zeit):
   - **Warten bis Di 14.07.2026, 9.30 Uhr** → Mail **w1** senden
     (Predictive Sending: ja, wie bei GTV26).
   - **Warten bis Do 23.07.2026, 9.30 Uhr** → **Conversion-Check**: hat der
     Kontakt inzwischen das Ziel-Abo-Tag? Ja → Ende. Nein → Mail **w2**
     (Predictive: ja).
   - **Warten bis Do 06.08.2026, 9.30 Uhr** → Conversion-Check (wie oben) →
     **Öffner-Split**: «hat w1 ODER w2 dieser Automatisierung geöffnet?»
     - Ja → Mail **w3** mit dem **Standard-Betreff**
     - Nein → Mail **w3** mit dem **Alt-Betreff** (identisches HTML, nur die
       Betreffzeile anders — zwei separate E-Mail-Schritte mit derselben
       HTML-Quelle)
     - *Bauweg:* If/Else nutzt den Segment-Builder; das ODER geht dort als
       «match any» über zwei «hat geöffnet»-Bedingungen (Kategorie Actions).
       **Plan B**, falls das ODER über zwei konkrete Automation-Mails nicht
       sauber wählbar ist: zwei verschachtelte If/Else — «hat w1 geöffnet?»
       Ja → Standard; Nein → «hat w2 geöffnet?» Ja → Standard; Nein →
       Alt-Betreff. Gleiches Ergebnis, ganz ohne ODER.
     - **Predictive Sending hier AUS** (fixer Versand): Predictive streut bis
       24 h — die letzte Erinnerung darf nicht in den Mini-Reminder- oder
       Frist-Tag hineinrutschen.
   - **Nur S26 · NoAbo:** **Warten bis Fr 07.08.2026, 9.30 Uhr** → Bedingung:
     «hat in w1–w3 geklickt UND hat kein Abo-Tag» → Mail **w3b**
     (Mini-Reminder, nur an unentschlossene Klicker; Predictive AUS).
     Alle anderen → Ende.
     - *Bauweg:* Bedingungsgruppe (match any) mit drei «hat Link
       geklickt»-Bedingungen, per UND verknüpft mit «hat kein Abo-Tag»
       (UND und ODER nie in derselben Gruppe — zweite Gruppe verwenden).
       **Plan B:** eine kleine Hilfs-Automatisierung mit Start-Trigger
       «klickt einen Link in einer E-Mail» (beschränkt auf die
       S26-NoAbo-Mails), die nur das Tag **«S26-geklickt»** setzt und endet;
       die w3b-Bedingung wird dann schlicht «hat Tag S26-geklickt UND hat
       kein Abo-Tag».
6. **Conversion-Ziel je Automatisierung** (als Goal-Schritt ans Ende, «Ende
   der Automatisierung», damit Konvertierte sofort aussteigen und AC die
   Conversion zählt):
   - S26 · NurTV→WS: WS-Abo-Tag gesetzt
   - S26 · NurWS→TV: GTV-Abo-Tag gesetzt
   - S26 · NoAbo: eines der beiden Abo-Tags gesetzt — Goals nutzen denselben
     Segment-Builder, das ODER ist also eine Bedingungsgruppe mit
     «match any» über die zwei Tag-Bedingungen.

## Die Mails (HTML per URL abholen)

Öffne je Mail die URL aus der Tabelle, übernimm den kompletten HTML-Quelltext
als **Custom-HTML** (nicht im Drag-and-drop-Designer nachbauen, nichts
«verbessern»). Der Preheader steckt bereits im HTML; `%UNSUBSCRIBELINK%`
ersetzt AC beim Versand automatisch. Absender/Reply-To wie bei GTV26
(104/107) übernehmen. **Die Links in den Mails nicht anfassen** — die
`utm_*`-Parameter sind unsere Conversion-Attribution (Cockpit),
Link-Tracking von AC darf die Ziel-URLs nicht umschreiben, nur ummanteln
(Standard-Klick-Tracking ist okay). Jede Mail hat genau EINEN Button; die Spalte «utm_content» sagt dir, was
in dessen Link stehen muss — das ist deine Kontrolle beim Testversand.
Alle Links tragen zudem
`utm_source=mailing`, `utm_medium=email`, `utm_campaign=summer26_trial`.

<!-- TABELLEN:START -->
*Mail-Tabelle automatisch erzeugt aus heroes.json — nicht von Hand pflegen; neu erzeugen mit `python3 ac_prompt.py --write`.*

### S26 · NurTV→WS (Angebot: Wochenschrift lesen)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Was Sie sehen, jetzt auch lesen — 3 Monate gratis | — | `w1_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w1_de.html |
| w1 | EN | What you watch, now also read — 3 months free | — | `w1_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w1_en.html |
| w2 | DE | Drei Monate Lesestoff, geschenkt zu Ihrem Abo | — | `w2_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w2_de.html |
| w2 | EN | Three months of reading, free with your subscription | — | `w2_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w2_en.html |
| w3 | DE | Bis Samstag: drei Monate mitlesen, geschenkt | Was Sie sehen, jetzt auch lesen — bis Samstag | `w3_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3_de.html |
| w3 | EN | Until Saturday: three months of reading, as a gift | What you watch, now also read — until Saturday | `w3_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3_en.html |

### S26 · NurWS→TV (Angebot: goetheanum.tv sehen)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Was Sie lesen, jetzt auch sehen — 3 Monate gratis | — | `w1_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w1_de.html |
| w1 | EN | What you read, now also watch — 3 months free | — | `w1_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w1_en.html |
| w2 | DE | Ihr Sommer hat noch Abende frei | — | `w2_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w2_de.html |
| w2 | EN | Your summer still has evenings free | — | `w2_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w2_en.html |
| w3 | DE | Nur noch bis Samstag: drei Monate gratis | Was Sie lesen, jetzt auch sehen — bis Samstag | `w3_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3_de.html |
| w3 | EN | Only until Saturday: three months free | What you read, now also watch — until Saturday | `w3_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3_en.html |

### S26 · NoAbo (beide Angebote; jede Mail führt mit einem Button zur Übersicht)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Ein Sommer mit dem Goetheanum — 3 Monate gratis | — | `w1_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w1_de.html |
| w1 | EN | A summer with the Goetheanum — 3 months free | — | `w1_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w1_en.html |
| w2 | DE | Lesen, sehen — oder gleich beides | — | `w2_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w2_de.html |
| w2 | EN | Read, watch — or simply both | — | `w2_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w2_en.html |
| w3 | DE | Am Samstag endet die Sommer-Aktion | Drei Monate Goetheanum — lesen, sehen oder beides | `w3_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3_de.html |
| w3 | EN | The summer offer ends on Saturday | Three months of Goetheanum — read, watch or both | `w3_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3_en.html |
| w3b | DE | Morgen ist Schluss | — | `w3b_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3b_de.html |
| w3b | EN | It ends tomorrow | — | `w3b_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3b_en.html |

Macht **26 E-Mail-Schritte** insgesamt: 20 Mails, wobei die 6 w3-Mails je zweimal eingehängt werden (Standard- und Alt-Betreff, gleiches HTML).
<!-- TABELLEN:END -->

## Bevor etwas live geht — Checkliste

1. Exakte Tag-Namen (GTV-Abo, WS-Abo) und Listen-Namen verifizieren und mir
   nennen.
2. Von jeder Mail-Vorlage einen **Testversand an philipp@saetzerei.com**:
   Bilder laden, Betreff/Preheader stimmen, Abmeldelink funktioniert, die
   Button-Links tragen `utm_campaign=summer26_trial` und exakt das
   `utm_content` aus der Tabelle.
3. Alle drei Automatisierungen **aktiv schalten, BEVOR** das Tag «S26-Start»
   per Bulk gesetzt wird. Das Bulk-Setzen selbst NICHT ausführen — nur
   vorbereiten und mir Bescheid geben. Zweite Voraussetzung vor dem Start:
   der utm-Weitergabe-Fix auf der Übersichts-Landingpage muss live sein
   (separater Zusatz-Auftrag) — vorher wäre die NoAbo-Attribution blind.
4. Zum Insight «12,5 % Abmelderate bei GTV26 Mail 3»: Unsere w3 ist ebenfalls
   eine Frist-Mail. Die Entschärfung ist eingebaut (w3b geht nur an Klicker,
   Nicht-Öffner bekommen w3 nur mit anderem Betreff) — bitte keine
   zusätzliche Dringlichkeit hineintexten und nichts am Mail-Inhalt ändern.
5. Falls etwas nicht wie beschrieben machbar ist, nicht improvisieren — kurz
   melden, was der Builder anbietet, dann entscheiden wir. Für die drei
   bekannten Verifikationspunkte (Öffner-ODER vor w3, w3b-Klick-Bedingung,
   NoAbo-OR-Goal) stehen die Bauwege und Plan-B-Varianten direkt bei den
   jeweiligen Schritten in der Struktur oben. Melde mir am Ende kurz,
   welcher Weg es jeweils geworden ist (Plan A oder B).
