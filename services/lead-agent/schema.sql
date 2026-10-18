-- =============================================================================
-- Grenzgänger · Lead-Fang-Strecke — Schema (marketing_*)
-- Charta: docs/grenzgaenger/charta.md · Konzept: docs/marketing-maschine.md §6/§8
-- Vorbild: services/seelenkalender/schema.sql (ratifizierte Praxis).
-- Grundsätze: Double-Opt-in, Ein-Klick-Abmeldung, Zweckbindung. Die E-Mail-
-- Adresse wird NUR für den Versand gehalten; Auswertung läuft ausschliesslich
-- über Summen (marketing_stats). Secrets entstehen serverseitig
-- (gen_random_bytes) und stehen nie im Repo. Resend-API-Key wird per
-- SQL-Editor in marketing_config gesetzt.
-- =============================================================================

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Konfiguration (nur Service-Role; RLS ohne Policies)
create table if not exists public.marketing_config (
  key   text primary key,
  value text not null default ''
);
alter table public.marketing_config enable row level security;

insert into public.marketing_config (key, value) values
  ('versand_key',    encode(extensions.gen_random_bytes(24), 'hex')),
  ('hash_salt',      encode(extensions.gen_random_bytes(16), 'hex')),
  ('resend_api_key', ''),  -- per SQL-Editor setzen, nie ins Repo
  ('absender',       'Das Goetheanum <onboarding@resend.dev>'),
  ('mails_base_url', 'https://werkzeuge.goetheanum.ch/apps/grenzgaenger-mails/mails'),
  ('w2_nach_tagen',  '4'),
  ('w3_nach_tagen',  '5')
on conflict (key) do nothing;

-- Griffe-Allowlist + Mailkopf des Bestätigungs-Briefs. Nur AKTIVE Griffe
-- nehmen Anmeldungen an; die inhaltliche Wahrheit je Griff steht im Register
-- (docs/grenzgaenger/griffe.json), hier liegt nur, was der Versand braucht.
create table if not exists public.marketing_griffe (
  id                   text primary key,          -- 'g001' …
  titel                text not null,
  zielkreis            text not null,             -- Mail-Satz-Schlüssel, z. B. 'waldorf-eltern'
  landing_url          text not null,             -- Rücksprung nach bestaetigen/ende
  aktiv                boolean not null default false,
  bestaetigung_betreff jsonb not null,            -- {"de": "…", "en": "…"}
  bestaetigung_text    jsonb not null,            -- {"de": "…", "en": "…"} (ein Absatz, Klartext)
  wellen_betreff       jsonb not null default '{}'::jsonb
                       -- {"w1": {"de": "…", "en": "…"}, …} — beim Aktivieren aus
                       -- services/mailing-grenzgaenger/heroes.json übernommen
);
alter table public.marketing_griffe enable row level security;

-- Leads (nur Service-Role; RLS ohne Policies)
create table if not exists public.marketing_leads (
  id            bigint generated always as identity primary key,
  email         text not null,                    -- Klartext NUR für den Versand
  email_hash    text not null,                    -- sha256(salt+email), Entdopplung je Griff
  griff_id      text not null references public.marketing_griffe(id),
  sprache       text not null default 'de',
  milieu        text,
  produkt       text not null default 'beide'
                check (produkt in ('wos','gtv','beide')),
  status        text not null default 'angemeldet'
                check (status in ('angemeldet','aktiv','beendet')),
  token         text not null unique,             -- Bestätigen/Abmelden
  herkunft      jsonb,                            -- UTM-Tupel der Anmeldung
  angemeldet_am timestamptz not null default now(),
  bestaetigt_am timestamptz,
  beendet_am    timestamptz,
  w1_am         timestamptz,                      -- Wellen-Status: null = noch nicht gesendet
  w2_am         timestamptz,
  w3_am         timestamptz,
  unique (email_hash, griff_id)                   -- je Griff einmal; mehrere Griffe erlaubt
);
alter table public.marketing_leads enable row level security;

-- Versand-Protokoll (eine Zeile je Lauf × Griff × Welle mit Empfängern)
create table if not exists public.marketing_versand (
  id           bigint generated always as identity primary key,
  griff_id     text not null,
  welle        int not null check (welle between 1 and 3),
  empfaenger   int not null default 0,
  fehler       int not null default 0,
  gesendet_am  timestamptz not null default now()
);
alter table public.marketing_versand enable row level security;

-- Öffentliche Kennzahlen (nur Summen verlassen die Datenbank)
create or replace function public.marketing_stats()
returns table (
  griff_id text, aktiv bigint, angemeldet bigint, beendet bigint,
  w1 bigint, w2 bigint, w3 bigint
)
language sql security definer set search_path = public as $fn$
  select g.id,
    count(l.id) filter (where l.status = 'aktiv'),
    count(l.id) filter (where l.status = 'angemeldet'),
    count(l.id) filter (where l.status = 'beendet'),
    count(l.id) filter (where l.w1_am is not null),
    count(l.id) filter (where l.w2_am is not null),
    count(l.id) filter (where l.w3_am is not null)
  from public.marketing_griffe g
  left join public.marketing_leads l on l.griff_id = g.id
  group by g.id
  order by g.id
$fn$;
grant execute on function public.marketing_stats() to anon;

-- Erster Griff: g001 Waldorf-Eltern-Post (inaktiv angelegt; aktiviert wird
-- er beim Scharfstellen, wenn Landingpage und Wellen-Mails live sind).
insert into public.marketing_griffe
  (id, titel, zielkreis, landing_url, aktiv, bestaetigung_betreff, bestaetigung_text, wellen_betreff) values
  ('g001', 'Waldorf-Eltern-Post', 'eltern',
   'https://werkzeuge.goetheanum.ch/kampagne/g/g001.html', false,
   '{"de": "Bitte bestätigen: die Waldorf-Eltern-Post", "en": "Please confirm: the Waldorf Parents Letter"}',
   '{"de": "Damit die monatliche Auswahl zu Erziehung, Kindheit und Medienmündigkeit Sie erreicht, bestätigen Sie bitte Ihre Anmeldung.", "en": "To receive the monthly selection on education, childhood and media literacy, please confirm your sign-up."}',
   '{"w1": {"de": "Willkommen — Ihre erste Auswahl", "en": "Welcome — your first selection"},
     "w2": {"de": "Drei Stücke, die bleiben", "en": "Three pieces that stay with you"},
     "w3": {"de": "Wenn Sie weiterlesen möchten — das Abo im Klartext", "en": "If you want to keep reading — the subscription, plainly"}}')
on conflict (id) do nothing;

-- Täglicher Wellen-Lauf: 06:11 UTC (bewusst neben der vollen Stunde).
-- Der Schlüssel wird erst zur Laufzeit aus der Config gelesen. Fällige
-- Wellen bestimmt die Function (aktiv ∧ w1 null → w1; w1+4d → w2; w2+5d → w3);
-- doppeltes Feuern ist unschädlich, weil w{n}_am vor dem Senden gesetzt wird.
select cron.unschedule('marketing-wellen')
where exists (select 1 from cron.job where jobname = 'marketing-wellen');
select cron.schedule(
  'marketing-wellen',
  '11 6 * * *',
  $cron$
  select net.http_post(
    url := 'https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/lead-fang?aktion=wellen&key='
           || (select value from public.marketing_config where key = 'versand_key'),
    body := '{}'::jsonb
  )
  $cron$
);
