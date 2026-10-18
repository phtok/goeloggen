# Prompt für Claude-Chrome: ActiveCampaign-Struktur «Sommer-Aktion 2026» (S26)

> **Dies ist der fertige Prompt für den Automation-Aufbau.** Alles ab der
> Trennlinie unten Claude-Chrome (Cowork) geben. Die Mail-Tabelle wird aus
> `heroes.json` erzeugt — nach einer Copy-Änderung: `python3 build_editor.py
> --publish` und `python3 ac_prompt.py --write`, dann ist dieser Prompt wieder
> aktuell. Betreffe/URLs unten nicht von Hand ändern.

---

Baue bzw. aktualisiere in ActiveCampaign die Automatisierungen für unser
**Vier-Wellen-Mailing** «Sommer-Aktion 2026» (3 Monate gratis: Wochenschrift
und/oder goetheanum.tv, Frist Samstag, 8. August 2026). Es gibt **24 fertige,
versandfähige Mails** — je Gruppe die vier Wellen × DE/EN (**w1** Ankündigung,
**w2** Erinnerung, **w3** Vorabend-Frist «morgen», **w3b** Frist-Tag «heute»):
Lesen 8, Sehen 8, Beides 8. Der HTML-Quelltext jeder Mail liegt unter einer
festen URL (Tabelle unten). Orientiere dich am Stil der bestehenden
GTV26-Automatisierungen (DE /builder/104, EN /builder/107) — je Sprache eine
eigene Automatisierung. Ändere nichts an GTV26.

**Zwei Aufträge in einem — die Reihenfolge ist Absicht:**
1. **Gruppe Lesen (DE + EN) aktualisieren:** die Automatisierungen bestehen
   bereits → die neuen Versanddaten (unten) eintragen, jede Mail frisch aus
   ihrer URL neu einfügen (die Copy hat sich geändert), und die **neue vierte
   Welle w3b (Samstag)** als Schritt anhängen (Conversion-Check und Öffner-Gate
   davor, siehe unten). Erst wenn Lesen DE und EN vollständig der Soll-Struktur
   unten entsprechen, weiter zu Schritt 2 — sie sind die Kopiervorlage.
2. **Gruppen Sehen und Beides (DE + EN) durch Duplizieren bauen:** die frisch
   aktualisierten Lesen-Automatisierungen **duplizieren** (Lesen DE → Sehen DE
   und Beides DE; Lesen EN → Sehen EN und Beides EN) und je Kopie die
   **Duplikat-Checkliste** unten abarbeiten. Struktur, Trigger, Warte-Schritte
   und Weichen sind in allen Gruppen identisch — nur Gruppen-Weiche, Ziel-Tag
   und die fünf E-Mail-Schritte unterscheiden sich. Falls der Builder das
   Duplizieren nicht sauber anbietet oder die Kopie mehr Nacharbeit kostet als
   ein Neubau: nicht erzwingen — dann nach der Struktur unten neu aufbauen und
   mir kurz melden, warum.

Macht **sechs Automatisierungen** (drei Gruppen × zwei Sprachen).

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

## Struktur: sechs Automatisierungen (je Gruppe × Sprache)

Je Gruppe und Sprache eine eigene Automatisierung — **S26 · Lesen · DE/EN**,
**S26 · Sehen · DE/EN**, **S26 · Beides · DE/EN** — wie bei GTV26 (getrennte
DE/EN-Builder). Gründe: jede Gruppe hat ein eigenes Conversion-Ziel, das
Reporting bleibt je Gruppe/Sprache lesbar, und Testversand/Go-Live lassen sich
je Automatisierung einzeln freigeben. **Lesen DE/EN** existieren schon → zuerst
aktualisieren; **Sehen/Beides DE/EN** entstehen danach als angepasste Duplikate
davon (Checkliste unten).

### Aufbau jeder Automatisierung

1. **Start-Trigger:** Tag **«S26-Start»** (einmaliger Lauf; per Bulk auf den
   Adressstamm, erst wenn **alle sechs** aktiv sind — die Listen-Anmeldung feuert
   nur bei Neuanmeldungen, deshalb Bulk-Tag als Eintritt).
2. **Hygiene-Filter:** keine Kampagne in den letzten 12 Monaten geöffnet → Ende.
3. **Sprach-Weiche:** ist in Liste «Sonderangebote» (DE) bzw. «Special Offers»
   (EN)? Nein → Ende. (Jede Automatisierung trägt nur EINE Sprache.)
4. **Gruppen-Weiche** (macht die Automatisierungen überschneidungsfrei):
   - Lesen: «hat GTV-Tag UND NICHT WS-Tag» — Nein → Ende
   - Sehen: «hat WS-Tag UND NICHT GTV-Tag» — Nein → Ende
   - Beides: «hat WEDER GTV- NOCH WS-Tag» — Nein → Ende
5. **Wellen-Drip** (Zeiten = Schweizer Zeit):
   - **Warten bis Do 16.07.2026, 12.00 Uhr** → Mail **w1** (Predictive Sending: ja).
     *(Start am 16.7. von 9.30 auf 12 Uhr verschoben — der Aufbau läuft am
     Versandtag selbst; die Wartezeit muss beim Aktivschalten in der Zukunft liegen.)*
   - **Warten bis Do 30.07.2026, 9.30 Uhr** → **Conversion-Check** (hat der
     Kontakt das Ziel-Abo-Tag? Ja → Ende) → Mail **w2** (Predictive: ja).
   - **Warten bis Fr 07.08.2026, 18.00 Uhr** → Conversion-Check → **Öffner-Split**:
     «hat w1 ODER w2 geöffnet?»
     - Ja → **w3** mit **Standard-Betreff**
     - Nein → **w3** mit **Alt-Betreff** (identisches HTML, nur die Betreffzeile —
       zwei E-Mail-Schritte mit derselben HTML-Quelle)
     - *Bauweg:* «match any» über zwei «hat geöffnet»-Bedingungen. **Plan B:**
       zwei verschachtelte If/Else («w1 geöffnet?» → sonst «w2 geöffnet?» → sonst
       Alt-Betreff).
     - **Predictive AUS** (fixer Freitagabend-Versand — der Rahmen «morgen läuft
       es aus» darf nicht in den Frist-Tag verrutschen).
   - **Warten bis Sa 08.08.2026, 10.00 Uhr** → Conversion-Check → **Öffner-Gate**:
     «hat w1 ODER w2 ODER w3 dieser Kampagne geöffnet?» **Ja** → Mail **w3b**
     (Standard-Betreff, Rahmen «heute läuft es aus»); **Nein** → Ende. Die
     Samstag-Mail geht also **nur an Kontakte, die diese Kampagne schon geöffnet
     haben** — kein vierter Anlauf bei Desinteressierten. **Predictive AUS.**
     *(Bauweg wie beim Öffner-Split vor w3: «match any» über die drei
     «hat geöffnet»-Bedingungen, bzw. verschachtelte If/Else als Plan B.)*
6. **Conversion-Ziel** (Goal am Ende, «Ende der Automatisierung», damit
   Konvertierte sofort aussteigen und AC zählt):
   - Lesen: WS-Abo-Tag gesetzt · Sehen: GTV-Abo-Tag gesetzt · Beides: eines der
     beiden Abo-Tags (Bedingungsgruppe «match any» über die zwei Tag-Bedingungen).

**Neu gegenüber der alten Struktur:** w3b (Samstag) gibt es jetzt in **jeder**
Gruppe (nicht mehr nur NoAbo), geht aber **nur an Öffner** dieser Kampagne
(w1/w2/w3) — die letzte Mail landet nicht bei Desinteressierten. GF-Prinzip:
keine Nacht zwischen letztem Ruf (Fr abend) und Frist (Sa). Damit bekommt ein
Nicht-Öffner höchstens **drei** Mails (w1, w2, w3-Alt), ein Öffner die volle
Frist-Staffel inkl. w3b. Die frühere Klick-Bedingung/Hilfsautomatisierung
**entfällt**.

### Duplikat-Checkliste (je Kopie vollständig abarbeiten)

Beim Duplizieren übernimmt AC **alle** Inhalte der Vorlage — jede Kopie trägt
also zunächst noch Lesen-Inhalte. Je Duplikat sind genau diese Punkte zu
ändern, alles andere bleibt stehen:

1. **Name:** «S26 · Sehen · DE/EN» bzw. «S26 · Beides · DE/EN».
2. **Gruppen-Weiche** (Schritt 4 oben): Tag-Bedingung der neuen Gruppe setzen —
   Sehen: «hat WS-Tag UND NICHT GTV-Tag» · Beides: «WEDER GTV- noch WS-Tag».
3. **Alle fünf E-Mail-Schritte** (w1, w2, w3 Standard, w3 Alt, w3b): HTML
   frisch aus der Gruppen-URL (Tabelle unten) einfügen, Betreff aus der
   Tabelle setzen, den E-Mail-Schritt nach Gruppe und Welle umbenennen
   (z. B. «S26 Sehen w1 DE»). Nichts von der Lesen-Vorlage stehen lassen.
4. **Conversion-Checks** (vor w2, w3, w3b): auf das Ziel-Tag der neuen Gruppe
   umstellen — Sehen: GTV-Abo-Tag · Beides: eines der beiden Abo-Tags
   («match any»).
5. **Conversion-Ziel (Goal)** am Ende: gleiches Ziel-Tag wie in Punkt 4.
6. **Kontrolle gegen Kopier-Restbestand:** einmal alle Schritte der Kopie
   durchgehen — nirgends darf mehr ein Lesen-Betreff, eine `mail_lesen_…`-URL
   oder (bei Sehen) ein WS-Ziel-Tag stehen. Duplikate bleiben **inaktiv**, bis
   alle sechs fertig gebaut und getestet sind.

Unverändert aus der Vorlage übernehmen (genau das spart die Zeit):
Start-Trigger «S26-Start», Hygiene-Filter, Sprach-Weiche, die vier
Warte-Schritte mit ihren Zeiten, Öffner-Split vor w3, Öffner-Gate vor w3b,
Absender/Reply-To.

## Die Mails (HTML per URL abholen)

Öffne je Mail die URL aus der Tabelle, übernimm den kompletten HTML-Quelltext
als **Custom-HTML** (nicht im Drag-and-drop-Designer nachbauen, nichts
«verbessern»). Der Preheader steckt bereits im HTML; `%UNSUBSCRIBELINK%`
ersetzt AC beim Versand automatisch. Absender/Reply-To wie bei GTV26
(104/107) übernehmen. **Die Links in den Mails nicht anfassen** — die
`utm_*`-Parameter sind unsere Conversion-Attribution (Cockpit),
Link-Tracking von AC darf die Ziel-URLs nicht umschreiben, nur ummanteln
(Standard-Klick-Tracking ist okay). Jede Mail hat genau EINEN Button; die frühen Wellen
(w1/w2) tragen unter der Feinschrift zusätzlich einen leisen Teilen-Link im PS (führt aufs
selbe Angebot, eigenes `utm_content` `…_share`) — die Frist-Mails (w3/w3b) nicht. Beide
Links nicht anfassen. Die Spalte «utm_content» unten meint den **Button** — das ist deine
Kontrolle beim Testversand.
Alle Links tragen zudem
`utm_source=mailing`, `utm_medium=email`, `utm_campaign=summer26_trial`.

<!-- TABELLEN:START -->
*Mail-Tabelle automatisch erzeugt aus heroes.json — nicht von Hand pflegen; neu erzeugen mit `python3 ac_prompt.py --write`.*

### S26 · NurTV→WS (Angebot: Wochenschrift lesen)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Ihr freier Zugang zur Wochenschrift Das Goetheanum | — | `w1_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w1_de.html |
| w1 | EN | Your free access to the weekly Das Goetheanum | — | `w1_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w1_en.html |
| w2 | DE | Ihr kostenloser Zugang – noch bis zum 8. August | — | `w2_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w2_de.html |
| w2 | EN | Your free access — still open until 8 August | — | `w2_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w2_en.html |
| w3 | DE | Nur noch bis morgen, Samstag: drei Monate gratis lesen | Bis morgen: drei Monate gratis lesen — jetzt starten | `w3_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3_de.html |
| w3 | EN | Only until tomorrow, Saturday: three months free | Until tomorrow: three months of free reading — start now | `w3_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3_en.html |
| w3b | DE | Heute läuft das Angebot aus — drei Monate gratis lesen | — | `w3b_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3b_de.html |
| w3b | EN | The offer closes today — three months of free reading | — | `w3b_nurtv` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_lesen_w3b_en.html |

### S26 · NurWS→TV (Angebot: goetheanum.tv sehen)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Ihr freier Zugang zu goetheanum.tv | — | `w1_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w1_de.html |
| w1 | EN | Your free access to goetheanum.tv | — | `w1_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w1_en.html |
| w2 | DE | Ihr kostenloser Zugang – noch bis zum 8. August | — | `w2_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w2_de.html |
| w2 | EN | Your free access — still open until 8 August | — | `w2_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w2_en.html |
| w3 | DE | Nur noch bis morgen, Samstag: drei Monate goetheanum.tv gratis | Bis morgen: drei Monate goetheanum.tv gratis — jetzt starten | `w3_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3_de.html |
| w3 | EN | Only until tomorrow, Saturday: three months of goetheanum.tv | Until tomorrow: three months of goetheanum.tv free — start now | `w3_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3_en.html |
| w3b | DE | Heute läuft das Angebot aus — drei Monate goetheanum.tv gratis | — | `w3b_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3b_de.html |
| w3b | EN | The offer closes today — three months of goetheanum.tv | — | `w3b_nurws` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_sehen_w3b_en.html |

### S26 · NoAbo (beide Angebote; jede Mail führt mit einem Button zur Übersicht)

| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |
|---|---|---|---|---|---|
| w1 | DE | Ihr freier Zugang zum Goetheanum – lesen und sehen | — | `w1_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w1_de.html |
| w1 | EN | Your free access to the Goetheanum – read and watch | — | `w1_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w1_en.html |
| w2 | DE | Ihr kostenloser Zugang – noch bis zum 8. August | — | `w2_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w2_de.html |
| w2 | EN | Your free access — still open until 8 August | — | `w2_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w2_en.html |
| w3 | DE | Nur noch bis morgen, Samstag: drei Monate gratis | Bis morgen: drei Monate gratis lesen oder sehen — jetzt starten | `w3_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3_de.html |
| w3 | EN | Only until tomorrow, Saturday: three months free | Until tomorrow: three months free to read or watch — start now | `w3_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3_en.html |
| w3b | DE | Heute läuft das Angebot aus — drei Monate gratis | — | `w3b_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3b_de.html |
| w3b | EN | The offer closes today — three months free | — | `w3b_noabo` | https://werkzeuge.goetheanum.ch/apps/mail-editor/mails/mail_beides_w3b_en.html |

Macht **30 E-Mail-Schritte** insgesamt: 24 Mails, wobei die 6 w3-Mails je zweimal eingehängt werden (Standard- und Alt-Betreff, gleiches HTML).
<!-- TABELLEN:END -->

## Bevor etwas live geht — Checkliste

1. Exakte Tag-Namen (GTV-Abo, WS-Abo) und Listen-Namen verifizieren und mir
   nennen.
2. **Testversand ALLER 24 Mails — sobald alle sechs Automatisierungen fertig
   gebaut sind** (vor dem Aktivschalten). Schicke jede der 24 Vorlagen **je
   einmal** an diese vier Adressen:
   - `francisca.devries@dasgoetheanum.com`
   - `louis.defeche@goetheanum.ch`
   - `nicolas.prestifilippo@goetheanum.ch`
   - `philipp@saetzerei.com`

   Prüfe je Mail: Bilder laden, Betreff/Preheader stimmen, **genau EIN Footer**
   (der AC-eigene — die HTML tragen keinen), Abmeldelink funktioniert, der
   Button trägt `utm_campaign=summer26_trial` und exakt das `utm_content` aus
   der Tabelle. Sind alle drei Gruppen × zwei Sprachen × vier Wellen (= 24)
   raus, melde mir kurz «alle 24 getestet».
3. Alle sechs Automatisierungen **aktiv schalten, BEVOR** «S26-Start» per Bulk
   gesetzt wird. Das Bulk-Setzen selbst NICHT ausführen — nur vorbereiten und
   mir Bescheid geben. Zweite Voraussetzung: der utm-Weitergabe-Fix auf der
   Übersichts-Landingpage muss live sein — vorher wäre die NoAbo-Attribution
   blind.
4. Zum Insight «12,5 % Abmelderate bei GTV26 Mail 3»: w3 und w3b sind Frist-
   Mails. Die Entschärfung sitzt im Text (kein Drohton, aufs Datum geankert),
   im Öffner-Split vor w3 (Nicht-Öffner nur anderer Betreff) und im **Öffner-Gate
   vor w3b** (die vierte Mail nur an Kampagnen-Öffner) — bitte keine zusätzliche
   Dringlichkeit hineintexten, nichts am Inhalt ändern.
5. Falls etwas nicht wie beschrieben machbar ist, nicht improvisieren — kurz
   melden, was der Builder anbietet, dann entscheiden wir. Für die
   Verifikationspunkte (Öffner-ODER vor w3, «match any»-Goal bei Beides) stehen
   die Bauwege und Plan-B-Varianten oben. Melde am Ende, welcher Weg es jeweils
   wurde (Plan A oder B).
