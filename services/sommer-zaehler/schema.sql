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
  status        text not null default 'neu'    check (status in ('neu','bleibt','gekuendigt','laeuft-aus')),
  kanal         text not null default 'andere' check (kanal in ('newsletter','mailer','social','popup','website','empfehlung','andere')),  -- Herkunftsweg (Attribution), aus UTM
  source        text not null default 'manual' check (source in ('uscreen','zoho','paperform','manual')),
  ext_id        text,                                 -- Dedup-Schlüssel je Quelle (verhindert Doppelzählung)
  unique (source, ext_id)
);

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
-- insert into public.sommer2026_config(key,value) values ('webhook_secret','<zufälliger-wert>');
