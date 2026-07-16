# werkzeug-abo — Update-Abo der Werkzeuge

Wer mag, abonniert auf [`abo.html`](../../abo.html) Neuerungen der Werkzeuge —
alle oder nur die persönlich relevanten (Auswahl nach `tools.json`-Slugs,
leere Auswahl = alles). Double-Opt-in, Ein-Klick-Abmeldung, Honeypot, kein
Nutzer-Enumerieren — dasselbe Muster wie der [Seelenkalender-Versand](../seelenkalender/).

Abgrenzung zur [Werkzeugpost](../werkzeugpost/): die Werkzeugpost ist die
redigierte Monats-Mail an alle Mitarbeitenden (Versand von Hand aus dem
Postfach); das Abo ist der freiwillige, feinkörnige Update-Kanal dazwischen
(«Schrift-Fassung neu — Neuinstallation lohnt sich»).

## Wege (`?aktion=`)

| Aktion | Methode | Eingabe | Wirkung |
|--------|---------|---------|---------|
| `anmelden` | POST | `{email, auswahl?: string[], website?}` | Double-Opt-in-Mail; Wieder-Anmelden aktualisiert nur die Auswahl |
| `bestaetigen` | GET | `?t=<token>` | Status `aktiv`, Umleitung auf die Seite |
| `ende` | GET | `?t=<token>` | Status `beendet` (1 Klick) |
| `versand` | POST | `?key=<versand_key>` + `{betreff, inhalt_html, werkzeuge?: string[]\|"alle", test?: email}` | Mail an alle Aktiven, deren Auswahl die Werkzeuge berührt; `test` schickt nur an diese Adresse |

Versand-Beispiel (Schlüssel steht in `werkzeugabo_config.versand_key`):

```bash
curl -X POST "https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/werkzeug-abo?aktion=versand&key=…" \
  -H "Content-Type: application/json" \
  -d '{"betreff":"Schriften 3.0 — Neuinstallation lohnt sich",
       "inhalt_html":"<p>…</p>",
       "werkzeuge":["schriften","powerpoint"],
       "test":"philipp.tok@goetheanum.ch"}'
```

## Speicher (Supabase, Projekt `dagcsnfrlbpxcmdimnrw`)

- `werkzeugabo_abo` — email, email_hash (Salt in Config), auswahl (jsonb),
  status `angemeldet|aktiv|beendet`, token, Zeitstempel
- `werkzeugabo_versand` — Protokoll je Aussendung
- `werkzeugabo_config` — `resend_api_key`, `absender`, `hash_salt`,
  `versand_key`, `seite_url`. RLS an, keine Policies → nur die Service-Role
  (Edge Function) kommt heran. **Schlüssel liegen nie im Repo.**

## Einmalige Handgriffe (Dashboard, nur der Auftraggeber)

1. **Verify JWT ausschalten** (Edge Functions → werkzeug-abo → Details):
   sonst weist das Funktions-Tor die Bestätigungs-/Abmelde-Links aus den
   Mails ab (nackte Browser-GETs ohne Header). Der Seelenkalender läuft
   genauso. Die Abo-Seite selbst schickt den Publishable Key mit und
   funktioniert in beiden Stellungen.
2. **Resend-Schlüssel setzen** — er fehlt derzeit auch beim Seelenkalender
   (Wert leer), Mails gehen also noch nicht hinaus:
   `update werkzeugabo_config set value='re_…' where key='resend_api_key';`
   Dazu den `absender` auf eine verifizierte Domain heben (derzeit
   Resend-Sandbox `onboarding@resend.dev`), z. B.
   `Werkzeuge – Das Goetheanum <post@werkzeuge.goetheanum.ch>`.

## Deploy

Quelle hier im Repo; deployt wird die Datei
[`werkzeug-abo/index.ts`](./werkzeug-abo/index.ts) als Edge Function
`werkzeug-abo` (per MCP oder `supabase functions deploy --no-verify-jwt werkzeug-abo`).
