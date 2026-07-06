-- =============================================================================
-- Sommer-Zähler 2026 · Backend-Schema
-- Projekt: Supabase «Public Secrets App» (dagcsnfrlbpxcmdimnrw) – dasselbe
-- Werkzeug-Backend, das schon landing_events / gtv_naming_events / signatur_events
-- trägt. Angewendet als Migration «sommer2026_signups».
--
-- Prinzip wie statistik.html: Rohtabelle bleibt für anon geschlossen (RLS an,
-- keine Policy, Rechte entzogen). Nur die Aggregat-RPCs sind für anon offen –
-- es verlassen ausschliesslich Summen die Datenbank, keine Personendaten.
-- =============================================================================

create table if not exists public.sommer2026_signups (
  id            bigint generated always as identity primary key,
  created_at    timestamptz not null default now(),
  signed_up_at  timestamptz not null,                 -- Zeitpunkt der Anmeldung (Momentum, Kohorten)
  produkt       text not null check (produkt in ('wos','gtv')),
  sprache       text not null check (sprache in ('de','en')),
  format        text not null check (format  in ('papier','digital','stream')),   -- WoS: papier/digital · GTV: stream
  tarif         text not null check (tarif   in ('standard','ermaessigt')),
  intervall     text not null check (intervall in ('monatlich','jaehrlich')),
  waehrung      text check (waehrung in ('eur','chf')),  -- Zahlungswährung (für Umsatz)
  status        text not null default 'neu'    check (status in ('neu','bleibt','gekuendigt','laeuft-aus')),
  kanal         text not null default 'andere' check (kanal in ('newsletter','mailer','social','popup','website','empfehlung','andere')),  -- Herkunftsweg (Attribution)
  source        text not null default 'manual' check (source in ('uscreen','zoho','paperform','manual')),
  ext_id        text,                                 -- Fremd-ID der Quelle (z. B. user_id/submission_id)
  dedup_key     text,                                 -- Entdopplung: <produkt>:<E-Mail-Hash> bzw. <source>:<ext_id>
  -- Attribution (Wirkungskette): volles UTM-Tupel + Landingpage + offene Selbstauskunft.
  kampagne      text default 'summer26_trial',        -- Kampagnen-ID (eine Aktion, eine Kennung)
  utm_source    text,                                 -- z. B. instagram / newsletter / google
  utm_medium    text,                                 -- z. B. social / email / organic
  utm_campaign  text,                                 -- i. d. R. = kampagne
  utm_content   text,                                 -- konkretes Motiv (z. B. reel_ernst_zuercher)
  landing_path  text,                                 -- Pfad der genutzten Landingpage
  selbstauskunft text                                 -- «Wie aufmerksam geworden?», E-Mail-redigiert (O-Ton)
);
-- Entdopplung strikt über dedup_key (Person je Produkt, auch über Quellen hinweg)
create unique index if not exists sommer2026_signups_dedup_uk on public.sommer2026_signups (dedup_key);

comment on table public.sommer2026_signups is
  'Sommer-Aktion 2026: eine Zeile je Anmeldung im Gratis-Zeitraum. status = Bleibe-Zustand nach 3 Monaten. Nur Aggregate verlassen die DB (RPCs).';

create index if not exists sommer2026_signups_day_idx on public.sommer2026_signups (signed_up_at);

alter table public.sommer2026_signups enable row level security;
-- Bewusst KEINE anon-Policy: RLS an + keine Policy = Rohzeilen zu.
revoke all on table public.sommer2026_signups from anon, authenticated;

-- 1) Breakdown je Dimension (Ströme, Tarife, Bleibe-Zustand)
create or replace function public.sommer2026_stats()
returns table(produkt text, sprache text, format text, tarif text, intervall text, status text, n bigint)
language sql security definer set search_path to 'public' as $$
  select produkt, sprache, format, tarif, intervall, status, count(*)::bigint as n
    from public.sommer2026_signups
   group by produkt, sprache, format, tarif, intervall, status;
$$;

-- 2) Momentum: Anmeldungen je Tag und Produkt
create or replace function public.sommer2026_timeline()
returns table(day date, produkt text, n bigint)
language sql security definer set search_path to 'public' as $$
  select signed_up_at::date as day, produkt, count(*)::bigint as n
    from public.sommer2026_signups
   group by signed_up_at::date, produkt
   order by day;
$$;

-- 3) Der 3-Monats-Moment: Kohorten und ihr Entscheidungsdatum
create or replace function public.sommer2026_kohorten()
returns table(kohorte date, neu bigint, bleibt bigint, gekuendigt bigint, offen bigint, entscheidung_ab date)
language sql security definer set search_path to 'public' as $$
  select date_trunc('month', signed_up_at)::date                        as kohorte,
         count(*)::bigint                                                as neu,
         count(*) filter (where status = 'bleibt')::bigint              as bleibt,
         count(*) filter (where status = 'gekuendigt')::bigint          as gekuendigt,
         count(*) filter (where status in ('neu','laeuft-aus'))::bigint  as offen,
         (date_trunc('month', signed_up_at) + interval '3 months')::date as entscheidung_ab
    from public.sommer2026_signups
   group by date_trunc('month', signed_up_at)
   order by kohorte;
$$;

-- 4) Attribution: Anmeldungen je Herkunftsweg
create or replace function public.sommer2026_kanaele()
returns table(kanal text, n bigint)
language sql security definer set search_path to 'public' as $$
  select kanal, count(*)::bigint as n
    from public.sommer2026_signups
   group by kanal
   order by n desc;
$$;

grant execute on function public.sommer2026_stats()    to anon, authenticated;
grant execute on function public.sommer2026_timeline() to anon, authenticated;
grant execute on function public.sommer2026_kohorten() to anon, authenticated;
grant execute on function public.sommer2026_kanaele()  to anon, authenticated;

-- =============================================================================
-- Wirkungskette: Massnahmen-Protokoll + feinere Attribution + Trichter
-- (Migration «sommer2026_attribution_und_massnahmen»)
-- =============================================================================

-- Massnahmen-Protokoll: eine Zeile je Kampagnen-Massnahme (Newsletter, Inserat, Post …).
-- Freitext (beobachtung/entscheidung) bleibt INTERN – nicht im öffentlichen RPC.
create table if not exists public.sommer2026_massnahmen (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  tag         date not null,                              -- Datum der Massnahme
  massnahme   text not null,                              -- z. B. «Auftaktnewsletter»
  kanal       text not null default 'andere' check (kanal in ('newsletter','mailer','social','popup','website','empfehlung','andere')),
  rolle       text not null default 'wirkung' check (rolle in ('sichtbarkeit','aktivierung','wirkung','bindung')),  -- Hauptaufgabe
  zielgruppe  text,
  botschaft   text,
  code        text,                                       -- Link/UTM/QR-Code der Massnahme
  kosten      numeric,                                    -- Aufwand
  reichweite  bigint,                                     -- Sichtbarkeit (Impressionen)
  klicks      bigint,                                     -- Aktivierung
  beobachtung text,                                       -- INTERN (nicht im RPC)
  entscheidung text                                       -- INTERN (nicht im RPC)
);
alter table public.sommer2026_massnahmen enable row level security;
revoke all on table public.sommer2026_massnahmen from anon, authenticated;

-- Feinere Attribution (unter dem kanal-Bucket): welches Motiv brachte Anmeldungen?
create or replace function public.sommer2026_attribution()
returns table(kanal text, utm_source text, utm_medium text, utm_campaign text, utm_content text, n bigint)
language sql security definer set search_path to 'public' as $$
  select kanal, utm_source, utm_medium, utm_campaign, utm_content, count(*)::bigint as n
    from public.sommer2026_signups
   group by kanal, utm_source, utm_medium, utm_campaign, utm_content
   order by n desc;
$$;

-- Massnahmen-Protokoll, kuratiert (ohne interne Freitext-Spalten)
create or replace function public.sommer2026_massnahmen_public()
returns table(tag date, massnahme text, kanal text, rolle text, kosten numeric, reichweite bigint, klicks bigint)
language sql security definer set search_path to 'public' as $$
  select tag, massnahme, kanal, rolle, kosten, reichweite, klicks
    from public.sommer2026_massnahmen
   order by tag, id;
$$;

-- Wirkungstrichter: Sichtbarkeit → Aktivierung → Wirkung → Bindung
create or replace function public.sommer2026_trichter()
returns table(stufe text, wert bigint, ord int)
language sql security definer set search_path to 'public' as $$
  select * from (
    select 'sichtbarkeit'::text as stufe, coalesce(sum(reichweite),0)::bigint as wert, 1 as ord from public.sommer2026_massnahmen
    union all
    select 'aktivierung', coalesce(sum(klicks),0)::bigint, 2 from public.sommer2026_massnahmen
    union all
    select 'wirkung', count(*)::bigint, 3 from public.sommer2026_signups
    union all
    select 'bindung', count(*) filter (where status = 'bleibt')::bigint, 4 from public.sommer2026_signups
  ) t
  order by t.ord;
$$;

grant execute on function public.sommer2026_attribution()       to anon, authenticated;
grant execute on function public.sommer2026_massnahmen_public() to anon, authenticated;
grant execute on function public.sommer2026_trichter()          to anon, authenticated;

-- =============================================================================
-- Link-Register (Migration «sommer2026_links_register»)
-- Erzeugte UTM-Links (aus apps/utm-generator/) sammeln → Soll/Ist im Cockpit.
-- Anon darf nur anlegen (Generator, Publishable-Key), Lesen nur über RPC.
-- =============================================================================
create table if not exists public.sommer2026_links (
  id           bigint generated always as identity primary key,
  created_at   timestamptz not null default now(),
  kampagne     text not null default 'summer26_trial',
  utm_source   text not null,
  utm_medium   text not null,
  utm_campaign text not null default 'summer26_trial',
  utm_content  text,
  landing      text,          -- Angebot der Landingpage (uebersicht/wos/tv)
  sprache      text,          -- Sprache der Landingpage (de/en)
  url          text not null, -- fertiger Link
  code         text,          -- Kurzcode für die Weiterleitung (Function go)
  rolle        text,          -- Hauptaufgabe (sichtbarkeit/aktivierung/wirkung/bindung)
  ersteller    text           -- optionales Kürzel, kein Pflichtfeld
);
create unique index if not exists sommer2026_links_url_uk  on public.sommer2026_links (url);
create unique index if not exists sommer2026_links_code_uk on public.sommer2026_links (code);
alter table public.sommer2026_links enable row level security;
revoke all on table public.sommer2026_links from anon, authenticated;
-- Schreiben NUR über die Schlüssel-RPCs unten (Migration
-- «sommer2026_links_schreibschutz») – kein offenes anon-INSERT mehr.

-- Soll/Ist: je registriertem Link die Zahl der Anmeldungen über genau dieses UTM-Tupel
create or replace function public.sommer2026_links_public()
returns table(created_at timestamptz, utm_source text, utm_medium text, utm_content text,
              landing text, sprache text, url text, code text, rolle text, ersteller text, abschluesse bigint)
language sql security definer set search_path to 'public' as $$
  select l.created_at, l.utm_source, l.utm_medium, l.utm_content, l.landing, l.sprache, l.url, l.code, l.rolle, l.ersteller,
         count(s.id)::bigint as abschluesse
    from public.sommer2026_links l
    left join public.sommer2026_signups s
      on  s.utm_campaign is not distinct from l.utm_campaign
      and s.utm_source   is not distinct from l.utm_source
      and s.utm_medium   is not distinct from l.utm_medium
      and s.utm_content  is not distinct from l.utm_content
   group by l.id, l.created_at, l.utm_source, l.utm_medium, l.utm_content, l.landing, l.sprache, l.url, l.code, l.rolle, l.ersteller
   order by abschluesse desc, l.created_at desc;
$$;
grant execute on function public.sommer2026_links_public() to anon, authenticated;

-- Kurzlink-Weiterleitung: Edge Function `go` liest sommer2026_links.code (Service-Role)
-- und leitet per 302 auf die volle UTM-URL. Siehe go/index.ts.

-- Schreibschutz (Migration «sommer2026_links_schreibschutz»): Anlegen und
-- Löschen verlangen den Team-Schlüssel. Sein SHA-256-Hash liegt in
-- sommer2026_config unter «links_schluessel_hash» (Präfix 'goe-links:');
-- Schlüsselwechsel = diese eine Config-Zeile neu setzen.
create or replace function public.sommer2026_links_schluessel_ok(p_schluessel text)
returns boolean language sql security definer set search_path to 'public' as $$
  select exists (
    select 1 from public.sommer2026_config
     where key = 'links_schluessel_hash'
       and value = encode(extensions.digest('goe-links:' || coalesce(p_schluessel, ''), 'sha256'), 'hex')
  );
$$;
revoke execute on function public.sommer2026_links_schluessel_ok(text) from public, anon, authenticated;

-- Anlegen nur per RPC: prüft Schlüssel, meldet 'ok' | 'schluessel' |
-- 'vergeben' (unique) | 'unvollstaendig' als Text an den Generator.
create or replace function public.sommer2026_link_anlegen(
  p_schluessel text, p_source text, p_medium text, p_content text,
  p_landing text, p_sprache text, p_url text, p_code text,
  p_rolle text, p_ersteller text)
returns text language plpgsql security definer set search_path to 'public' as $$
begin
  if not public.sommer2026_links_schluessel_ok(p_schluessel) then
    return 'schluessel';
  end if;
  if coalesce(p_source, '') = '' or coalesce(p_medium, '') = '' or coalesce(p_url, '') = '' then
    return 'unvollstaendig';
  end if;
  begin
    insert into public.sommer2026_links
      (kampagne, utm_source, utm_medium, utm_campaign, utm_content,
       landing, sprache, url, code, rolle, ersteller)
    values
      ('summer26_trial', p_source, p_medium, 'summer26_trial', nullif(p_content, ''),
       nullif(p_landing, ''), nullif(p_sprache, ''), p_url, nullif(p_code, ''),
       nullif(p_rolle, ''), nullif(p_ersteller, ''));
  exception when unique_violation then
    return 'vergeben';
  end;
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_link_anlegen(text, text, text, text, text, text, text, text, text, text) to anon, authenticated;

-- Kontrolliertes Löschen (per URL), ebenfalls nur mit Schlüssel.
create or replace function public.sommer2026_link_loeschen(p_url text, p_schluessel text)
returns text language plpgsql security definer set search_path to 'public' as $$
begin
  if not public.sommer2026_links_schluessel_ok(p_schluessel) then
    return 'schluessel';
  end if;
  delete from public.sommer2026_links where url = p_url and kampagne = 'summer26_trial';
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_link_loeschen(text, text) to anon, authenticated;

-- =============================================================================
-- Ingestion (Webhooks) – siehe ingest-uscreen/index.ts
-- =============================================================================

-- Roh-Log jedes eingehenden Webhooks (PII-redigiert), nur Service-Role liest ihn
create table if not exists public.sommer2026_ingest_raw (
  id          bigint generated always as identity primary key,
  received_at timestamptz not null default now(),
  source      text not null default 'uscreen',
  event       text,
  ok          boolean not null default true,
  note        text,
  payload     jsonb
);
alter table public.sommer2026_ingest_raw enable row level security;
revoke all on table public.sommer2026_ingest_raw from anon, authenticated;

-- Konfig-Speicher (u. a. webhook_secret) – nur Service-Role
create table if not exists public.sommer2026_config (
  key   text primary key,
  value text not null
);
alter table public.sommer2026_config enable row level security;
revoke all on table public.sommer2026_config from anon, authenticated;
-- Schlüssel in sommer2026_config:
--   webhook_secret : Secret für ?key= der Ingestion-Functions
--   hash_salt      : Salt für den E-Mail-Hash (Entdopplung)
--   links_schluessel_hash : SHA-256 des Team-Schlüssels (Präfix 'goe-links:')
--                    fürs Link-Register (Anlegen/Löschen)
--   aktion_aktiv   : 'true' = zählen, sonst nur loggen
--   aktion_start   : Zeitgrenze (Anmeldungen davor zählen nicht), z. B.
--                    '2026-07-03T12:00:00+02:00'
--   aktion_coupon  : optional – Aktions-Coupon-Code (statt Trial-Heuristik)
--   aktion_plan    : optional – Aktions-Plan-Titel (statt Trial-Heuristik)
