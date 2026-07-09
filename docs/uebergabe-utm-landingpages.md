# Übergabe-Brief: UTM-Durchreiche auf den Lovable-Landingpages (Sommer-Aktion 2026)

*Für eine neue Claude-Session (Chat oder Code). Dieser Brief ist selbsttragend —
er setzt kein Wissen aus früheren Sitzungen voraus. Stand: 6. Juli 2026.*

> **ERLEDIGT — Schlussstand 9. Juli 2026.** Die gesamte Kette ist bewiesen:
> Kurzlink → Landing (alle fünf: WoS DE/EN, TV DE/EN, Übersicht mit
> delegiertem Klick-Handler) → Paperform-Prefill bzw. Uscreen-Checkout-URL →
> Webhook → Zähler. Belege: echte Newsletter-Abos mit Attribution (WoS DE),
> Buchhalter-Tests über die EN-Landing (Felder tragen das volle Tupel),
> Sichtprüfungen der Checkout-URLs (TV DE/EN) und der Übersichts-Weiche.
> Test-Anmeldungen mit «hao.bu» in der Adresse filtert der Webhook
> automatisch (nur Roh-Protokoll, nie gezählt). Einzige Kür: die Pre-fill-Keys
> des Formulars sommer2026-eur-en umbenennen (Server-Fallback deckt es ab).
> Die Abschnitte unten bleiben als Anleitung für künftige Kampagnen stehen.

## Auftrag

Sicherstellen, dass die UTM-Parameter (`utm_source`, `utm_medium`,
`utm_campaign`, `utm_content`) auf **allen** Landingpages der Sommer-Aktion
(«3 Monate gratis», Ende 8. August 2026) vom Besuch bis zur Anmeldung
**durchgereicht** werden. Die Landingpages sind mit **Lovable** gebaut
(lovable.dev); die Anmeldung läuft je Angebot verschieden:

- **Wochenschrift (WoS):** Paperform-Formular als **Popup-Embed** auf der
  Landing (zwei Formulare: CH und INTL).
- **goetheanum.tv (GTV):** Knopf führt **auf eine andere Domain**
  (goetheanum.tv, Uscreen-Kasse). Uscreen liest UTMs beim Kontoanlegen selbst
  aus seiner Session — sie müssen also **auf der goetheanum.tv-URL ankommen**.
- **Übersichts-Landingpage** (`global-sommer2026.goetheanum.online`):
  verlinkt auf die beiden Angebots-Seiten — Outbound-Links müssen die UTMs
  **mitnehmen**, sonst reisst die Spur an der ersten Weiche.

## Die Kette (Soll-Zustand)

```
Kurzlink tools.goetheanum.ch/s/<tier>
  → 302 mit voller UTM-URL (funktioniert, live verifiziert)
  → Landingpage (Lovable)                     ← HIER wird durchgereicht
  → WoS: Paperform-Popup (prefill)  |  GTV: goetheanum.tv-URL mit ?utm_…
  → Webhook → Supabase sommer2026_signups (utm_* Spalten)
  → Team-Cockpit (Attribution «Nach Motiv», Soll/Ist je Link)
```

## Stand am 6. Juli 2026

**Erledigt:**
- **WoS-Landing** (`ws-sommer2026.dasgoetheanum.com`): Fix umgesetzt und
  publiziert. Lovable hat gebaut: `src/lib/utm.ts` (capture/read/ensure via
  sessionStorage + history.replaceState), Top-Level-Capture in
  `src/routes/__root.tsx`, `usePaperformEmbed.ts` übergibt
  `{ prefillInherit: true, prefill: { utm_source, … } }` an `Paperform.popup`.
  Gilt für beide Formulare (CH + INTL).
- Kurzlink-Kette, Webhooks (`ingest-paperform` v5+, `ingest-uscreen`),
  Attribution im Backend: alles live und getestet. Platzhalter-UTMs
  («none», leer) werden serverseitig zu `null` bereinigt.

**Offen (das ist die Arbeit):**
1. **Paperform-Blocker (kein Lovable-Thema):** Die vier versteckten Felder
   in beiden Formularen tragen zufällige Pre-fill-Keys (`75kij`, `eb0qb`,
   `qdmh`, `7c5la`), Paperform füllt aber **nur über den Key** vor, nie über
   den Titel. Fix von Hand im Formular-Editor: Feld anklicken → Konfiguration
   → ganz unten «Custom ID» → exakt `utm_source` / `utm_medium` /
   `utm_campaign` / `utm_content` eintragen (4 Felder × 2 Formulare), dann
   publishen.
2. **TV-Landingpages (Lovable, DE/EN):** Outbound-Links zur goetheanum.tv-
   Kasse müssen die gespeicherten UTMs **an die Ziel-URL anhängen**
   (Domainwechsel — sessionStorage hilft nicht hinüber). Prompt unten.
3. **Übersichts-Landingpage (Lovable):** dasselbe für ihre Links zu den
   beiden Angebots-Seiten. Prompt unten (identisch verwendbar).
4. **End-to-End-Test** nach 1.–3. (Rezept unten).

## Prompt für Lovable — Outbound-Links (TV-Landings UND Übersichts-Seite)

```
Visitors arrive on this page with UTM parameters (utm_source, utm_medium,
utm_campaign, utm_content) on the URL. The page links out to other domains
(e.g. goetheanum.tv) and/or to the offer pages. Currently those outbound
links drop the UTM parameters.

1. On first app load, read the four utm_* parameters from
   window.location.search and store them in sessionStorage (only overwrite a
   stored value if the URL actually carries that parameter).
2. On every outbound/offer link (including buttons that navigate), append the
   stored utm_* parameters to the target URL at click/render time — preserving
   any parameters the target URL already has, without duplicating keys.
3. Keys stay exactly utm_source, utm_medium, utm_campaign, utm_content.
4. Apply to all language variants in this project.

Ask me any questions before coding, then summarize which files you changed.
Publish after the change.
```

## Prompt für Lovable — Paperform-Popup (nur falls eine weitere Seite ein Paperform einbettet)

Bereits auf der WoS-Landing umgesetzt; für andere Seiten wiederverwendbar:
UTMs beim ersten Laden aus der URL in sessionStorage sichern, vor dem
Popup-Öffnen per `history.replaceState` zurück auf die URL schreiben und
`Paperform.popup(id, { prefillInherit: true, prefill: { utm_source, … } })`
übergeben (leere Schlüssel weglassen). Keys exakt `utm_source` usw.

## Verifikation (End-to-End, 5 Minuten)

1. Test-URL öffnen (privates Fenster):
   `https://ws-sommer2026.dasgoetheanum.com?utm_source=probe&utm_medium=test&utm_campaign=summer26_trial&utm_content=lovable_check`
   → Popup → Test-Anmeldung absenden.
2. In Supabase (Projekt `dagcsnfrlbpxcmdimnrw`) prüfen:
   `select created_at, utm_source, utm_medium, utm_content, landing_path from
   sommer2026_signups order by created_at desc limit 3;`
   **Erwartung:** `probe / test / lovable_check` und `landing_path` =
   Landing-Domain (nicht `…paperform.co` — das hiesse, der Test lief am
   Popup vorbei).
3. Für TV: Test-URL der TV-Landing öffnen, zum goetheanum.tv-Knopf, prüfen,
   dass die Ziel-URL im Browser die `?utm_…`-Parameter trägt (Anmeldung dort
   nur nötig, wenn man auch den Uscreen-Webhook prüfen will).
4. Testeinträge danach löschen (per `delete … where …` auf die Test-Zeile).

## Randbedingungen

- **Keine Personendaten** ins Repo oder in Screenshots; E-Mails liegen nur
  gehasht in der Datenbank. Secrets (Webhook-Secret) stehen **nicht** in diesem
  Brief — beim Auftraggeber erfragen.
- Lovable-Projekte gehören dem Auftraggeber (Zugang via lovable.dev).
  Königsweg für präzise Arbeit: **GitHub-Sync** des Lovable-Projekts
  aktivieren, dann kann eine Claude-Code-Session den Landing-Code direkt
  bearbeiten (Commits statt Prompts).
- Referenzen in diesem Repo (`phtok/goeloggen`):
  `services/sommer-zaehler/utm-ablauf.md` (Namensschema, Landingpages),
  `services/sommer-zaehler/schema.sql` (Datenmodell, RPCs),
  `services/sommer-zaehler/kurzlink-site/` (Kurzlink-Brücke, live in
  `phtok/goelinks` auf `tools.goetheanum.ch`),
  `apps/sommer-zaehler/` (Team-Cockpit), `apps/utm-generator/` (Generator,
  intern gelistet).

## Kontakt/Kontext

Auftraggeber: Philipp Tok. Die Attribution speist das Team-Cockpit
(`werkzeuge.goetheanum.ch/apps/sommer-zaehler/`, intern). Ziel des Ganzen:
Jede Massnahme der Aktion soll ihrer Wirkung zuordenbar sein — erst dann
sind Kurzlinks, Register und Cockpit eine geschlossene Schleife.
