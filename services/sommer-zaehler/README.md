# Sommer-Zähler 2026 — Backend

Backend des Aktions-Cockpits [`apps/sommer-zaehler/`](../../apps/sommer-zaehler/).
Zieht live aus dem Werkzeug-Supabase (`dagcsnfrlbpxcmdimnrw`) über drei
Aggregat-RPCs. Es verlassen **nur Summen** die Datenbank, keine Personendaten.

## Aufbau der App (mehrseitig)

Die Kampagne ist eine mehrseitige App in `apps/sommer-zaehler/`, geklammert
durch die gemeinsame Unter-Leiste (`data-onpage` von `nav.js`):
**Cockpit** (`index.html`) · **Aktivitäten** (`aktivitaeten.html`, Zeitband +
Protokoll) · **Kosten** (`kosten.html`) · **Multiplikatoren**
(`multiplikatoren.html`) — dazu verlinkt **Links** (`../utm-generator/`) und
**Mail** (`../mail-editor/`). (Im Backend heisst die Tabelle weiterhin
`sommer2026_massnahmen`; „Aktivität" ist nur die Oberflächen-Benennung.)
Geteiltes CSS/JS liegt in `campaign.css` und `campaign.js`; jede Seite bindet
beide ein und rendert per Element-Guards nur ihre eigenen Abschnitte, so bleibt
der Code einfach (eine Datei, aus dem Cache). Der Hub-Eintrag `sommer-zaehler`
bleibt die Startseite; die Unterseiten sind nur über die Leiste erreichbar.

## Datenmodell

Eine Zeile in `public.sommer2026_signups` = eine Anmeldung im Gratis-Zeitraum.
Dimensionen: `produkt` (wos/gtv) · `sprache` (de/en) · `format`
(papier/digital/stream) · `tarif` (standard/ermaessigt) · `intervall`
(monatlich/jaehrlich) · `status` (neu/bleibt/gekuendigt/laeuft-aus) · `source` ·
`ext_id` (Dedup). Schema und RPCs: [`schema.sql`](./schema.sql).

RPCs (für `anon` per Publishable-Key aufrufbar, wie in `statistik.html`):
`sommer2026_stats` (Breakdown), `sommer2026_timeline` (Momentum je Tag),
`sommer2026_kohorten` (der 3-Monats-Moment), `sommer2026_kanaele` (Attribution
je Herkunftsweg), `sommer2026_attribution` (feiner: je UTM-Motiv),
`sommer2026_trichter` (Wirkungskette Sichtbarkeit→Bindung),
`sommer2026_massnahmen_public` (Massnahmen-Protokoll, kuratiert),
`sommer2026_ereignisse` (Einzel-Anmeldungen der letzten 14 Tage für «Was ist
passiert?» – stundengenau gerundet, ohne jede Personenspalte).

## Attribution (Woher) und Kosten

`kanal` (newsletter / mailer / social / popup / website / empfehlung / andere)
hält den **Herkunftsweg** je Anmeldung als groben Bucket. Darunter wird das
**volle UTM-Tupel** roh gespeichert (`utm_source` / `utm_medium` / `utm_campaign`
/ `utm_content`) plus `landing_path` und die offene `selbstauskunft` («Wie sind
Sie aufmerksam geworden?», E-Mail-redigiert). So bleibt sichtbar, welches
**Motiv** (z. B. `reel_ernst_zuercher` vs. `footer_link`) getragen hat, nicht nur
welcher Kanal. Die Ingestion (Paperform / Uscreen) schreibt das mit; der
`kanal`-Bucket wird daraus abgeleitet. Die **Kosten** liegen (wie Preise und
Zielmarken) im `CONFIG`-Block der Seite; daraus rechnet das Cockpit Kosten je Abo
(CPA) und den Rückfluss je eingesetztem Franken. Alle Geldbeträge zeigt das
Cockpit in **einer** Anzeige-Währung (`CONFIG.waehrung`, aktuell CHF); gezahlt
wird real in EUR und CHF (`waehrung` je Anmeldung) – echte Preise je Währung
stehen noch aus.

## Wirkungskette und Aktivitäten-Protokoll

Das Cockpit liest die Aktion als **Kette gemessener Zahlen**, nicht als
Einzelwerte: **Reichweite → Klicks → Abschlüsse → Geblieben**
(`sommer2026_trichter`). Alle vier Stufen sind gemessen, **nicht** eine im
Eintrag gewählte Kategorie: Reichweite = Summe der `reichweite`, Klicks = Summe
der `klicks` (beide aus den Aktivitäten); Abschlüsse = Anzahl Anmeldungen,
Geblieben = Anmeldungen mit Status `bleibt` (beide live aus `sommer2026_signups`).
Darum zeigt der Trichter zusätzlich die **Reichweite je Kanal** (Social,
Newsletter, Popup …), client-seitig aus den Aktivitäten summiert. Reichweite und
Klicks werden direkt beim Eintrag der Aktivität erfasst (oder später über
Bearbeiten). Das frühere Feld „Aufgabe der Aktivität" (`rolle`) ist aus der
Oberfläche entfernt, weil es dieselben vier Wörter trug wie die Trichterstufen
und so den Eindruck erweckte, es steuere die Zählung – die Spalte bleibt in der
DB, wird aber nicht mehr gepflegt.

Quelle ist das **Aktivitäten-Protokoll** `sommer2026_massnahmen` – eine Zeile je
Aktivität (Newsletter, Inserat, Post) mit Datum, Kanal, Kosten, Reichweite,
Klicks, einer öffentlichen **`notiz`** (klärende Präzisierung, z. B. „Reichweite =
geöffnete Mails, nicht versendete") und **internen** Notizen (`beobachtung` /
`entscheidung`). Die internen Freitext-Spalten verlassen die DB **nie**: der
öffentliche RPC `sommer2026_massnahmen_public` gibt nur die kuratierten Zahlen
plus `notiz` zurück. So wird CPA je **Aktivität** rechenbar (nicht nur je Bucket),
und aus der Aktion wird eine lesbare Geschichte statt eines Datenhaufens.

**Eintragen und Bearbeiten** über die RPCs `sommer2026_massnahme_eintragen` und
`…_aendern` (offener Schreibweg fürs Team, Muster Link-Register; `notiz` ist
Bestandteil beider). Im Cockpit lässt sich jede Aktivität **direkt im Zeitband
anklicken** – der Chip lädt die Zeile in die Bearbeiten-Maske. Chips mit Notiz
tragen sie als Zeile im Chip und einen goldenen Rand.

## Ströme und Tarife

Sechs Ströme: Wochenschrift DE Papier · DE Digital · EN Papier · EN Digital,
goetheanum.tv DE · EN — je mit Tarifstufe (Standard/Ermässigt) und Zahlungsweise
(Monatlich/Jährlich). Die Aktion ist «3 Monate gratis, jederzeit kündbar»; nach
drei Monaten fällt je Kohorte die Bleibe-Entscheidung (`status` → bleibt /
gekuendigt / laeuft-aus).

## Betrieb: gepflegte Backend-Tabelle

Zahlen werden in `sommer2026_signups` gepflegt (CSV-Import / kleiner Upsert),
die Seite zieht live daraus — kein Commit je Aktualisierung nötig. `ext_id`
verhindert Doppelzählung beim erneuten Import.

## Live-Anbindung (je Quelle, sobald Zugang vorliegt)

Geplant je Quelle eine Ingestion (Supabase Edge Function + `pg_cron`), die nach
`sommer2026_signups` upsertet. Benötigt wird:

- **Uscreen (goetheanum.tv):** Admin-API-Token **oder** täglicher Subscriber-CSV.
  Felder: Anmeldedatum, Plan-Name (→ Sprache, Tarif, Intervall), Status
  (trialing/active/cancelled), **Trial-Ende** (= 3-Monats-Moment). Offen: DE/EN
  getrennte Stores oder ein Store mit Plan-Tags? «3 Monate gratis» als Trial
  oder Coupon?
- **Zoho (Wochenschrift):** Zoho Subscriptions (Billing) **oder** CRM — OAuth-
  Client (Client-ID/-Secret + Refresh-Token, Read-Scope) **oder** planbarer
  Export. Felder: Start-/Erstelldatum, Plan-Code (→ Papier/Digital, Tarif,
  Intervall, Sprache), Status, Erst-Abbuchungsdatum. Plus die Zuordnung
  Plan-Code → Dimension. Zoho = Wahrheitsstand für WoS.
- **Paperform:** API-Key **oder** Webhook je Formular (DE/EN) — nur als
  Echtzeitpuls «gerade angemeldet»; entprellt gegen Zoho.

## Uscreen-Webhook (aktiv)

Edge Function [`ingest-uscreen/index.ts`](./ingest-uscreen/index.ts) nimmt
Uscreen-Webhooks entgegen (kein API-Key nötig) und upsertet nach
`sommer2026_signups` (`source='uscreen'`, Dedup über `ext_id` =
`subscription_id`). Jeder Payload wird PII-redigiert (E-Mail/Name → `***`) in
`sommer2026_ingest_raw` geloggt, um das Mapping am ersten echten Event zu
verfeinern.

- **URL:** `…/functions/v1/ingest-uscreen?key=<webhook_secret>`
  (Secret liegt in `sommer2026_config`, nicht im Code/Repo).
- **In Uscreen:** Settings → Webhooks → obige URL; Events *subscription
  created / canceled* (und *payment/charge* für die Umwandlung `bleibt`).
- **Attribution:** Settings → Custom user fields → «Wie sind Sie auf uns
  aufmerksam geworden?»; die Function mappt die Antwort auf `kanal`.
- **Aktions-Isolierung:** jede Neuanmeldung (`subscription_assigned` u. ä.) im
  Aktionszeitraum zählt als `neu`. Trials hinterlegen eine Kreditkarte, darum ist
  `transaction_id` **kein** Unterscheidungsmerkmal. Verlängerungen legen nichts an
  (nur Neuanmeldungen). Kündigung → `gekuendigt`. **Zahlungen setzen vorerst kein
  `bleibt`** – die Umwandlung wird erst nach der 3-Monats-Frist bestimmt. Zeitlich
  begrenzt durch `aktion_start`; schärfer stellbar über `aktion_coupon` / `aktion_plan`.
- **Scharf/Log:** zählt nur wenn `sommer2026_config.aktion_aktiv = 'true'`,
  sonst reiner Log-Modus.

## Paperform-Webhook (Wochenschrift, aktiv)

Edge Function [`ingest-paperform/index.ts`](./ingest-paperform/index.ts) nimmt die
Formular-Einreichungen entgegen (Paperform → After submission → Webhook, **kein
API-Key nötig**). Das Formular ist die Aktion – jede Einreichung zählt als `neu`
(`produkt='wos'`). Es gibt **vier Formulare** (Währung EUR/CHF × Sprache DE/EN);
Sprache, Währung und Format je Formular über die URL:
`…/ingest-paperform?key=<secret>&sprache=de&waehrung=eur` (bzw. `&sprache=en`,
`&waehrung=chf`, optional `&format=papier|digital`). Tarif/Intervall werden aus
den Feldern erraten und am ersten echten Payload verfeinert (Roh-Log).

## Entdopplung (Dupletten filtern)

Strikt über `dedup_key`:
- Innerhalb einer Quelle: eine Zeile je Abonnent (mehrere Events derselben
  Person – Anmeldung, Zahlung, Verlängerung, Kündigung – aktualisieren dieselbe
  Zeile, statt neue anzulegen).
- Über Quellen hinweg (Paperform **und** Zoho für dieselbe WoS-Person):
  `dedup_key = <produkt>:<gesalzener E-Mail-Hash>` – E-Mail wird **nur gehasht**
  gespeichert (Salt in `sommer2026_config.hash_salt`), nie im Klartext.

## Fest im Cockpit hinterlegt (bis echte Werte vorliegen)

In `apps/sommer-zaehler/index.html` im `CONFIG`-Block: Zielmarken je Strom,
Preise je Tarif/Intervall, angenommene Bleibe-Quote, Aktionsstart/-ende,
Meilensteine. Diese Werte sind vorläufig markiert — nur diese ersetzen, sobald
die echten Zahlen da sind; die Aggregation rechnet unverändert weiter.
