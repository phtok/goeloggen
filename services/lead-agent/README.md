# Lead-Agent — Grenzgänger-Fang-Strecke

Backend des Grenzgänger-Agenten (`docs/grenzgaenger/charta.md`). Eine Edge
Function (`lead-fang`), vier Wege über `?aktion=`, je Griff parametrisiert:

| Aktion | Weg | Wirkung |
|---|---|---|
| `anmelden` | POST `{email, griff, sprache?, milieu?, produkt?, utm?, website?}` | nur für aktive Griffe: Eintrag `angemeldet` + Bestätigungs-Brief (Double-Opt-in) |
| `bestaetigen` | GET `?t=<token>` (Link im Brief) | Status `aktiv`, Rücksprung zur Landingpage des Griffs |
| `ende` | GET `?t=<token>` (Link in jeder Mail) | Status `beendet` — ein Klick, ohne Rückfrage |
| `wellen` | `?key=<versand_key>` (pg_cron) | fällige Wellen senden, Protokoll je Lauf |

**Takt:** pg_cron, täglich 06.11 UTC. Fällig ist: `aktiv ∧ w1 leer → w1`,
`w1 älter als 4 Tage → w2`, `w2 älter als 5 Tage → w3` (Abstände in
`marketing_config`). Höchstens drei Wellen je Lead — danach Ruhe (Charta
§2.2). Doppel-Versand ist ausgeschlossen, weil `w{n}_am` **vor** dem Senden
gestempelt wird; der Cron darf beliebig oft feuern.

**Wellen-Inhalte:** die Versand-Artefakte der Mail-Fabrik
(`services/mailing-grenzgaenger/` → `apps/grenzgaenger-mails/mails/` auf
GitHub Pages, Basis-URL in `marketing_config.mails_base_url`;
Dateischema `mail_{zielkreis}_w{n}_{sprache}.html`). `%UNSUBSCRIBELINK%`
wird je Lead durch den `ende`-Link ersetzt. Die Betreffzeilen stehen in
`marketing_griffe.wellen_betreff` — beim Aktivieren eines Griffs aus
`heroes.json` übernehmen.

## Datenhaltung (Zweckbindung, wie Seelenkalender)

- `email` liegt **nur** für den Versand in `marketing_leads` (RLS ohne
  Policies — kein anon-Zugriff); `email_hash` (gesalzen) dient der
  Entdopplung je Griff.
- **Auswertung nur über Summen:** `marketing_stats()` liefert je Griff
  aktiv / angemeldet / beendet / Wellen-Fortschritt, nie Zeilen.
- Double-Opt-in, Ein-Klick-Abmeldung, `List-Unsubscribe`-Header (One-Click)
  in jeder Welle.
- Löschung: `delete from marketing_leads where status='beendet'` ist
  jederzeit zulässig.
- Die **Konversion** je Griff läuft nicht über Adressen, sondern über die
  UTM-Messkette: Wellen-Links tragen `utm_content=g0NN_w{n}`, die
  bestehenden Ingest-Funktionen des Sommer-Zählers schreiben das mit.

## Einrichtung (einmalig, zwei Handgriffe ausserhalb des Repos)

1. **Resend-Konto:** eigene Domain verifizieren (z. B.
   `post.dasgoetheanum.com`; bis dahin sendet der Sandbox-Absender
   `onboarding@resend.dev` nur an die eigene Konto-Adresse — gut zum Testen).
2. **API-Key setzen** — im Supabase-SQL-Editor, nie im Repo/Chat:

   ```sql
   update marketing_config set value = 're_…' where key = 'resend_api_key';
   update marketing_config set value = 'Das Goetheanum <post@post.dasgoetheanum.com>'
     where key = 'absender';
   ```

`versand_key` und `hash_salt` entstehen **serverseitig**
(`gen_random_bytes`) und berühren das Repo nie.

## Griff aktivieren (je Griff, macht der Agent beim Schritt `bereit → live`)

```sql
-- Betreffzeilen aus services/mailing-grenzgaenger/heroes.json übernehmen,
-- dann freischalten:
update marketing_griffe set aktiv = true where id = 'g001';
```

Voraussetzung: Landingpage live (`kampagne/g/g0NN.html`), Wellen-Mails
gebaut und gemergt (`apps/grenzgaenger-mails/mails/`), Registerzeilen im
UTM-Generator angelegt.

## Prüfgriffe

```sql
select * from marketing_stats();                       -- Summen je Griff
select griff_id, welle, empfaenger, fehler, gesendet_am
  from marketing_versand order by id desc limit 20;
select jobname, schedule from cron.job where jobname = 'marketing-wellen';
```

Probelauf von Hand (statt auf den Cron zu warten):

```sql
select net.http_post(url :=
  'https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/lead-fang?aktion=wellen&key='
  || (select value from marketing_config where key = 'versand_key'));
```

Fang-Strecke Ende-zu-Ende: auf der Landingpage mit einer Testadresse
anmelden → Zeile `angemeldet` → Bestätigungs-Link im Brief → `aktiv` →
`ende`-Link → `beendet`. Ein POST mit gefülltem Honigtopf-Feld `website`
muss still verpuffen (Antwort `ok`, keine Zeile).
