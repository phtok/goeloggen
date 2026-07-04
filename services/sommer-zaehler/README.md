# Sommer-Zähler 2026 — Backend

Backend des Aktions-Cockpits [`apps/sommer-zaehler/`](../../apps/sommer-zaehler/).
Zieht live aus dem Werkzeug-Supabase (`dagcsnfrlbpxcmdimnrw`) über drei
Aggregat-RPCs. Es verlassen **nur Summen** die Datenbank, keine Personendaten.

## Datenmodell

Eine Zeile in `public.sommer2026_signups` = eine Anmeldung im Gratis-Zeitraum.
Dimensionen: `produkt` (wos/gtv) · `sprache` (de/en) · `format`
(papier/digital/stream) · `tarif` (standard/ermaessigt) · `intervall`
(monatlich/jaehrlich) · `status` (neu/bleibt/gekuendigt/laeuft-aus) · `source` ·
`ext_id` (Dedup). Schema und RPCs: [`schema.sql`](./schema.sql).

RPCs (für `anon` per Publishable-Key aufrufbar, wie in `statistik.html`):
`sommer2026_stats` (Breakdown), `sommer2026_timeline` (Momentum je Tag),
`sommer2026_kohorten` (der 3-Monats-Moment).

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

## Fest im Cockpit hinterlegt (bis echte Werte vorliegen)

In `apps/sommer-zaehler/index.html` im `CONFIG`-Block: Zielmarken je Strom,
Preise je Tarif/Intervall, angenommene Bleibe-Quote, Aktionsstart/-ende,
Meilensteine. Diese Werte sind vorläufig markiert — nur diese ersetzen, sobald
die echten Zahlen da sind; die Aggregation rechnet unverändert weiter.
