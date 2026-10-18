# Auftrag für Claude im Chrome: Uscreen-Attribution einrichten (goetheanum.tv)

> **SCHLUSSSTAND 18.7.2026 — erledigt und übertroffen.** Das Event
> «User Created» ist aktiv und liefert `utm_params` (volles UTM-Tupel aus
> Uscreens Session-Erfassung) plus die Custom-Field-Antwort; die Ingestion
> (ab v16) heftet beides automatisch an die Anmeldungen. Der Altbestand
> 3.–18.7. wurde über den People-CSV-Export rekonstruiert (People → Filter
> «Created on date» → Export; enthält UTM-Spalten + Referrer + User Field 1):
> 18 Alt-Abos bekamen ihr UTM-Tupel, 23 ihren Kanal (mailer/social/website)
> nachträglich. Ein Admin-API-Zugang existiert in diesem Konto nicht und
> wird nicht gebraucht. Die Abschnitte unten bleiben als Verlauf stehen.

Dieser Prompt ist für **Claude in Chrome** gedacht, eingeloggt im
**Uscreen-Admin von goetheanum.tv**. Er stammt aus der Attributions-Analyse vom
17.7.2026: Der Uscreen-Webhook liefert nur `event`, `subscription_id`,
`subscription_title`, `transaction_id` und User-Felder — **keine UTM-Parameter,
keinen Referrer, keine Custom-Field-Antworten**. Darum landen alle
goetheanum.tv-Abos im Cockpit unter «ohne UTM».

Den folgenden Block vollständig kopieren und Claude im Chrome geben:

---

Du bist im Uscreen-Admin-Backend von goetheanum.tv eingeloggt und hilfst mir,
die Herkunfts-Attribution unserer Abo-Anmeldungen einzurichten. Kontext: Wir
fahren die Sommer-Aktion «3 Monate gratis» (bis 8. August) und messen die
Anmeldungen in einem eigenen Cockpit. Unser Webhook-Empfänger bekommt von
Uscreen aktuell nur `event`, `subscription_id`, `subscription_title`,
`transaction_id` und die User-Felder — keine UTM-Parameter, keinen Referrer
und keine Antworten aus Custom-Feldern. Dadurch ist bei allen
goetheanum.tv-Abos unsichtbar, welche Massnahme sie ausgelöst hat.

Regeln für diesen Auftrag:
- Nichts löschen und keine bestehenden Einstellungen abschalten. Nur
  hinzufügen, prüfen und dokumentieren.
- Keine Aktionen, die Mails an Kundinnen oder Kunden auslösen.
- Geheimnisse (Webhook-URLs mit `?key=…`, API-Tokens) nie in den Chat
  schreiben und nicht in Screenshots zeigen — nur bestätigen, DASS sie
  existieren, und den Fundort nennen.
- Wenn eine Einstellung nicht existiert oder anders heisst als unten
  beschrieben, nicht improvisieren: notieren, wie der Bereich wirklich heisst,
  und im Abschlussbericht melden.

Arbeite diese fünf Schritte der Reihe nach ab:

**Schritt 1 — Custom-Feld «Wie sind Sie auf uns aufmerksam geworden?»**
Öffne die Einstellungen für Nutzerfelder (Settings → Custom Fields bzw.
User Fields, je nach Oberfläche). Prüfe, ob ein Feld wie «Wie sind Sie auf
uns aufmerksam geworden?» existiert. Falls nein: lege es an, als bei der
Registrierung sichtbares, optionales Textfeld (kein Pflichtfeld — es darf
keine Anmeldung verhindern). Notiere den exakten internen Feld-Key/Namen,
den Uscreen dem Feld gibt — wir brauchen ihn wortgenau für unser Mapping.

**Schritt 2 — Webhook-Konfiguration prüfen**
Öffne Settings → Webhooks (bzw. Integrations → Webhooks). Dokumentiere,
welche Webhook-Endpunkte eingetragen sind (nur Host nennen, den `?key=`-Teil
weglassen) und welche Events aktiviert sind. Wir erwarten mindestens:
Subscription created/assigned, Subscription canceled und ein Zahlungs-Event
(order paid / payment succeeded). Prüfe ausserdem, ob es irgendwo eine Option
gibt, den Payload zu erweitern (Custom Fields, UTM/Referrer, Marketing-Daten
mitsenden). Falls ja: aktiviere sie und dokumentiere genau, welche Felder
dazukommen. Falls nein: ausdrücklich notieren, dass der Payload nicht
erweiterbar ist.

**Schritt 3 — Admin-API-Zugang für die Anreicherung**
Öffne Settings → API (Uscreen-API). Prüfe, ob ein API-Token existiert oder
erzeugt werden kann — wenn wählbar, mit Nur-Lese-Rechten. Erzeuge das Token,
schreibe es aber NICHT in den Chat: sag mir nur, wo es liegt, damit ich es
selbst kopieren und sicher hinterlegen kann. Hintergrund: Wenn der Webhook
keine Custom-Field-Antworten mitliefert, kann unser Backend sie nach jeder
Anmeldung per API nachschlagen (User → Custom Fields) — dafür brauchen wir
dieses Token. Notiere auch, ob die API pro User die Custom-Field-Antworten
und Marketing-/Herkunftsdaten hergibt (in der API-Doku nachsehen, die im
Admin verlinkt ist).

**Schritt 4 — Tracking-Möglichkeiten des Storefronts**
Sieh in Settings → Tracking (bzw. Marketing/Integrations) nach: Gibt es
Felder für Google Analytics 4, Meta Pixel oder eigene Tracking-Snippets im
Checkout? Dokumentiere, was vorhanden und was davon bereits ausgefüllt ist
(IDs nur mit den letzten 4 Zeichen). Das ist unser Weg B: Wenn Uscreen die
UTMs nie an den Webhook gibt, können wir die Konversion clientseitig im
Checkout messen.

**Schritt 5 — Abschlussbericht**
Gib mir am Ende einen kompakten Bericht in genau dieser Gliederung:
1. Custom-Feld: existierte schon? / neu angelegt? — exakter Feld-Key
2. Webhooks: Endpunkte (ohne Key) + aktivierte Events + erweiterbar ja/nein
3. API: Token vorhanden/erzeugt (Fundort, nicht der Wert) + was die API je
   User an Herkunftsdaten hergibt
4. Tracking: welche Snippet-/Analytics-Felder es gibt und was belegt ist
5. Auffälligkeiten oder Abweichungen von den Beschreibungen oben

---

## Ergebnis des ersten Durchlaufs (17.7.2026, Claude im Chrome)

- **Custom-Feld angelegt:** Slot «User Field 1» trägt jetzt «Wie sind Sie auf
  uns aufmerksam geworden?» (Key im Datenmodell: `custom_field_1` /
  `user_field_1`; Uscreen kennt nur drei feste, immer optionale Text-Slots).
- **Webhook-Payload nicht erweiterbar** (nur URL + ein Event je Endpunkt).
  Unser Endpunkt hört auf: Recurring Payment Successful, Order Paid, Access
  canceled, Subscription Assigned. **Es fehlt «User Created»** – laut
  Uscreen-Doku das einzige Event, das die Custom-Field-Antworten
  (`custom_fields`) mitliefert. → Follow-up unten.
- **API:** Unter «Developers» gibt es nur den Publishable-Key (Headless,
  «no scopes») – für Server-Lookups ungeeignet. Der eigentliche Admin-Key
  (`X-Store-Token`) liegt laut Doku auf der **API-Keys-Seite unter Admin
  Users** und ist teils Plus-Plan-gebunden. Mit dem User-Created-Event wird
  die API für die Selbstauskunft aber voraussichtlich gar nicht gebraucht.
- **Tracking (Weg B):** Kein GA4/Meta verbunden; der **Post-purchase-Slot**
  (Settings → Snippets, läuft ~10 s nach Checkout) ist frei bis auf ein
  X/Twitter-Event – dort könnte clientseitiges Konversions-Tracking ergänzt
  werden, falls nötig.

### Follow-up-Auftrag für Claude im Chrome (kurz)

> Im Uscreen-Admin von goetheanum.tv: Öffne Settings → Webhooks. Lege einen
> zusätzlichen Webhook auf **dieselbe URL wie der bestehende
> `…supabase.co/functions/v1/ingest-uscreen`-Endpunkt** an (URL inklusive des
> `?key=…`-Teils vom bestehenden Eintrag übernehmen, nicht in den Chat
> schreiben), mit Event **«User Created»**. Nichts löschen, bestehende
> Einträge unverändert lassen. Danach: Sieh unter Settings → Admin Users
> nach, ob es dort eine API-Keys-Seite gibt (Admin-API, `X-Store-Token`) und
> berichte nur, ob sie existiert und ob ein Key angelegt werden kann – keinen
> Key-Wert in den Chat.

Die Ingestion verarbeitet «User Created» bereits: Sie legt daraus **kein**
Abo an, sondern heftet die Selbstauskunft an die Anmeldung derselben Person
(nur wo noch leer) und zieht den Kanal nach, wenn er noch «andere» ist;
kommt die Anmeldung später, greift der Roh-Log-Fallback.

## Was danach bei uns passiert (Backend-Seite)

- Die Ingestion (`ingest-uscreen/index.ts`) liest die Custom-Field-Antwort
  bereits aus mehreren möglichen Payload-Pfaden (`custom_fields.…`,
  `user_fields.0.value` …) und schreibt sie als `selbstauskunft` mit — sobald
  Uscreen sie liefert, greift das Mapping ohne weiteres Zutun.
- Kommt sie nur per API: Anreicherungs-Schritt bauen (API-Token in
  `sommer2026_config`, Nachschlag je neuer Anmeldung).
- Test-Anmeldungen mit einer `hao.bu`-Adresse zählen nie als Abo, werden aber
  roh geloggt — damit lässt sich die Kette gefahrlos verifizieren.
