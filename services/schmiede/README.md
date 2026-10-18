# Werkzeug-Schmiede — Backend

Der Eingang der Wünsche aus der [Werkzeug-Schmiede](../../apps/schmiede/): eine
insert-only Tabelle, gelesen und getaggt nur im key-geschützten
[Cockpit](../../apps/schmiede-eingang/). Muster wie `qr-generator` (Rohzeilen zu,
security-definer-RPCs) und `lead-agent` (Resend + Config-Tabelle).

Warum kein GitHub-Issue: ein Auftrag trägt **Kontaktdaten**. Die sollen nicht
öffentlich werden — deshalb private Tabelle statt Issue, und Lesen nur mit
Schlüssel.

## Teile

| Datei | Rolle |
|---|---|
| `schema.sql` | Tabelle `schmiede_auftraege` + Config, Insert-RPC (anon), key-geschützte RPCs `schmiede_liste` / `schmiede_setzen`, Info-Ping über `net.http_post`. |
| `schmiede-melden/index.ts` | Edge Function: schickt bei neuem Wunsch **eine** Info-Mail via Resend (Inhalt bleibt im Cockpit). |

## Einrichten (im Supabase-SQL-Editor, nie im Repo/Chat)

1. **Schema anwenden** — `schema.sql` im SQL-Editor ausführen (Projekt
   `dagcsnfrlbpxcmdimnrw`, wie die anderen Werkzeuge).

2. **Cockpit-Schlüssel festlegen** — Klartext nur hier eingeben, gespeichert wird
   nur der Hash:

   ```sql
   insert into schmiede_config(key, value)
   values ('cockpit_key_hash',
           encode(extensions.digest('goe-schmiede:' || lower(trim('DEIN-SCHLUESSEL')), 'sha256'), 'hex'))
   on conflict (key) do update set value = excluded.value;
   ```

3. **Info-Mail einrichten** (optional, aber gewünscht):

   ```sql
   insert into schmiede_config(key, value) values
     ('empfaenger', 'DEINE-MAIL@…'),
     ('melde_url',  'https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/schmiede-melden'),
     ('melde_key',  encode(gen_random_bytes(24), 'hex'))
   on conflict (key) do update set value = excluded.value;
   ```

   Absender und Resend-Key liegen bereits in `marketing_config` (vom Lead-Agent) —
   die Info-Mail nutzt sie mit. Ohne `melde_url` unterbleibt der Ping still; der
   Wunsch wird trotzdem gespeichert.

4. **Edge Function deployen:**

   ```sh
   supabase functions deploy schmiede-melden
   ```

   `SUPABASE_URL` und `SUPABASE_SERVICE_ROLE_KEY` stehen der Function automatisch
   zur Verfügung.

## Öffnen

Cockpit über den Geheim-Link (Schlüssel aus Schritt 2):

```
https://werkzeuge.goetheanum.ch/apps/schmiede-eingang/?key=DEIN-SCHLUESSEL
```

## Wie sich die Schleife schliesst

1. Person füllt die Schmiede aus → **Absenden** → Zeile in `schmiede_auftraege`.
2. Info-Mail: <q>Ein neuer Wunsch ist da</q> (nur Titel, Link ins Cockpit).
3. Im Cockpit: sichten, taggen, Status setzen; von dort in die Bau-Schleife.

## Datensparsamkeit

- Rohzeilen zu (RLS an, keine anon-Policy). Kein anon-Leseweg auf Kontaktdaten.
- Lesen/Taggen nur mit Schlüssel (Hash-Vergleich in der RPC).
- Die Info-Mail trägt **keinen** Inhalt, nur den Titel und den Cockpit-Link.
- Löschen ist jederzeit zulässig: `delete from schmiede_auftraege where …`.

## Wachstumspfad

Das Cockpit ist als Board angelegt: die Wünsche sind die erste Quelle. Später
können hier **alle laufenden Projekte** sichtbar und taggbar werden (zweite
Quelle, z. B. aus `tools.json` oder einer eigenen Projekt-Tabelle).
