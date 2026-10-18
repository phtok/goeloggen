# Seelenkalender — Versand-Strecke (Lead-Schleife 1B)

Backend des Wochenspruch-Abos ([`apps/seelenkalender/`](../../apps/seelenkalender/)).
Eine Edge Function (`seelenkalender`), vier Wege über `?aktion=`:

| Aktion | Weg | Wirkung |
|---|---|---|
| `anmelden` | POST (Formular der Seite) | Eintrag `angemeldet` + Bestätigungs-Brief (Double-Opt-in) |
| `bestaetigen` | GET `?t=<token>` (Link im Brief) | Status `aktiv`, Weiterleitung zur Seite |
| `ende` | GET `?t=<token>` (Link in jeder Mail) | Status `beendet` — ein Klick, ohne Rückfrage |
| `versand` | `?key=<versand_key>` (pg_cron) | Wochenspruch an alle Aktiven, eine Zeile ins Protokoll |

**Takt:** pg_cron, Montag 05.07 UTC. Doppel-Versand ist durch
`seelenkalender_versand (jahr, woche) unique` ausgeschlossen — der Cron darf
beliebig oft feuern. Woche 1 = Osterwoche (Gauss-Formel, identisch mit dem
Frontend; Referenzdaten 2024–2026 geprüft).

**Vertiefung im Wechsel:** gerade Woche → goetheanum.tv, ungerade →
Wochenschrift; UTM je Motiv `vers_NN` (`utm_campaign=evergreen`,
`utm_source=seelenkalender`). Damit ist jede Ausgabe im Cockpit attribuierbar.

## Datenhaltung (Zweckbindung statt Hash-Dogma)

Anders als beim Sommer-Zähler (reine Auswertung → nur Hashes) braucht ein
**Versand** die Adresse selbst — ohne sie gibt es keinen Brief. Darum gilt:

- `email` liegt **nur** für den Versand in `seelenkalender_abo` (RLS ohne
  Policies — kein anon-Zugriff); `email_hash` (gesalzen) dient der Entdopplung.
- **Auswertung nur über Summen:** `seelenkalender_stats()` gibt aktiv /
  angemeldet / beendet zurück, nie Zeilen.
- Double-Opt-in (bestätigt wird nur, wer den Brief öffnet), Ein-Klick-Abmeldung,
  `List-Unsubscribe`-Header (One-Click) in jeder Ausgabe.
- Löschung: `delete from seelenkalender_abo where status='beendet'` ist
  jederzeit zulässig — Beendete werden nicht angeschrieben und nicht gebraucht.

## Einrichtung (einmalig, zwei Handgriffe ausserhalb des Repos)

1. **Resend-Konto** (resend.com): eigene Domain verifizieren (z. B.
   `post.dasgoetheanum.com`; bis dahin sendet der Sandbox-Absender
   `onboarding@resend.dev` nur an die eigene Konto-Adresse — gut zum Testen).
2. **API-Key setzen** — im Supabase-SQL-Editor, nie im Repo/Chat:

   ```sql
   update seelenkalender_config set value = 're_…' where key = 'resend_api_key';
   update seelenkalender_config set value = 'Seelenkalender – Das Goetheanum <spruch@post.dasgoetheanum.com>'
     where key = 'absender';
   ```

`versand_key` und `hash_salt` wurden **serverseitig erzeugt**
(`gen_random_bytes`) und haben das Repo nie berührt.

## Prüfgriffe

```sql
select * from seelenkalender_stats();                  -- Summen
select jahr, woche, empfaenger, fehler from seelenkalender_versand order by id desc;
select jobname, schedule from cron.job where jobname = 'seelenkalender-versand';
```

Probelauf von Hand (statt auf Montag zu warten):
`select net.http_post(url := 'https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/seelenkalender?aktion=versand&key=' || (select value from seelenkalender_config where key='versand_key'));`
