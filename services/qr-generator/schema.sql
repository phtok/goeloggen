-- =============================================================================
-- QR-Generator · Backend-Schema
-- Projekt: Supabase «Public Secrets App» (dagcsnfrlbpxcmdimnrw) – dasselbe
-- Werkzeug-Backend wie sommer2026_* / goeloggen_stats. Angewendet als
-- Migrationen «qr_links_und_scans» und «qr_stats_beide_register».
--
-- Prinzip wie statistik.html: Rohtabellen bleiben für anon geschlossen (RLS an,
-- keine Policy, Rechte entzogen). Nur die RPCs sind für anon offen – es
-- verlassen ausschliesslich Summen die Datenbank. Keine Personendaten: je Scan
-- werden nur Zeitpunkt und Code gespeichert (keine IP, kein User-Agent).
--
-- Gemeinsamer Namensraum mit sommer2026_links unter tools.goetheanum.ch/s/ —
-- Eindeutigkeit prüft qr_link_anlegen über BEIDE Register. Die Weiterleitung
-- (Edge Function go, services/sommer-zaehler/go/index.ts) löst über
-- kurzlink_aufloesen beide Register auf und zählt dabei in link_hits.
--
-- Bewusst KEINE Lösch-RPC in v1: ein offener Löschweg würde gedruckte Codes
-- gefährden. Geparkt für v2: Logo in der QR-Mitte (erzwingt Fehlerkorrektur H
-- + Gerätetests).
-- =============================================================================

create table if not exists public.qr_links (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  code       text not null,          -- Kurzname unter tools.goetheanum.ch/s/<code>
  url        text not null,          -- Ziel der Weiterleitung
  ersteller  text                    -- optionales Kürzel
);
create unique index if not exists qr_links_code_uk on public.qr_links (code);
alter table public.qr_links enable row level security;
revoke all on table public.qr_links from anon, authenticated;

comment on table public.qr_links is
  'QR-Generator: eine Zeile je angelegtem Kurzlink. Rohzeilen zu, Lesen nur über qr_stats_public (wer den Code kennt).';

create table if not exists public.link_hits (
  id   bigint generated always as identity primary key,
  ts   timestamptz not null default now(),
  code text not null                 -- zählt QR- UND Kampagnen-Kurzlinks
);
create index if not exists link_hits_code_ts_idx on public.link_hits (code, ts);
alter table public.link_hits enable row level security;
revoke all on table public.link_hits from anon, authenticated;

comment on table public.link_hits is
  'Scan-/Klick-Zählung der Kurzlinks (Function go): nur Zeitpunkt + Code, keine Personendaten.';

-- Anlegen: 'ok' | 'vergeben' | 'ungueltig' | 'unvollstaendig'.
-- Kollisionsprüfung über BEIDE Register (gemeinsamer Namensraum /s/).
create or replace function public.qr_link_anlegen(p_code text, p_url text, p_ersteller text default null)
returns text language plpgsql security definer set search_path to 'public' as $$
declare v_code text := lower(trim(coalesce(p_code,'')));
begin
  if coalesce(trim(p_url),'') = '' or v_code = '' then return 'unvollstaendig'; end if;
  if v_code !~ '^[a-z0-9][a-z0-9-]{2,31}$' or trim(p_url) !~ '^https?://' then return 'ungueltig'; end if;
  if exists (select 1 from public.sommer2026_links where code = v_code)
     or exists (select 1 from public.qr_links where code = v_code) then return 'vergeben'; end if;
  insert into public.qr_links (code, url, ersteller)
  values (v_code, trim(p_url), nullif(trim(coalesce(p_ersteller,'')),''));
  return 'ok';
exception when unique_violation then return 'vergeben';
end; $$;
grant execute on function public.qr_link_anlegen(text, text, text) to anon, authenticated;

-- Statistik je Code: Summe, letzter Scan, Ziel-URL (nur wer den Code kennt).
-- Liest BEIDE Register (Migration «qr_stats_beide_register»): auch
-- Kampagnen-Kurzlinks haben eine Zählung in link_hits; kein neues Datenleck,
-- die Kampagnen-URLs sind über sommer2026_links_public ohnehin öffentlich.
create or replace function public.qr_stats_public(p_code text)
returns table(code text, url text, created_at timestamptz, scans bigint, letzter_scan timestamptz)
language sql security definer set search_path to 'public' as $$
  with reg as (
    select l.code, l.url, l.created_at from public.qr_links l where l.code = lower(trim(p_code))
    union all
    select s.code, s.url, s.created_at from public.sommer2026_links s where s.code = lower(trim(p_code))
  )
  select r.code, r.url, r.created_at,
         count(h.id)::bigint as scans, max(h.ts) as letzter_scan
    from reg r left join public.link_hits h on h.code = r.code
   group by r.code, r.url, r.created_at
   limit 1;
$$;
grant execute on function public.qr_stats_public(text) to anon, authenticated;

-- Offenes Register (Migration «qr_links_offenes_register», Beschluss 10.7.2026,
-- wie UTM-Generator/Cockpit): alle angelegten Kurzlinks mit Ziel und Zählung
-- sind einsehbar – Transparenz vor Verschluss. Personendaten entstehen keine.
create or replace function public.qr_links_public()
returns table(code text, url text, created_at timestamptz, scans bigint, letzter_scan timestamptz)
language sql security definer set search_path to 'public' as $$
  select l.code, l.url, l.created_at,
         count(h.id)::bigint as scans, max(h.ts) as letzter_scan
    from public.qr_links l left join public.link_hits h on h.code = l.code
   group by l.id, l.code, l.url, l.created_at
   order by l.created_at desc;
$$;
grant execute on function public.qr_links_public() to anon, authenticated;

-- Scans je Tag (letzte 30 Tage) für die kleine Verlaufsgrafik.
create or replace function public.qr_stats_tage(p_code text)
returns table(tag date, n bigint)
language sql security definer set search_path to 'public' as $$
  select ts::date as tag, count(*)::bigint as n from public.link_hits
   where code = lower(trim(p_code)) and ts >= now() - interval '30 days'
   group by ts::date order by tag;
$$;
grant execute on function public.qr_stats_tage(text) to anon, authenticated;

-- Auflösen + Zählen in EINEM Rundgang – nur für die Edge Function (service_role).
create or replace function public.kurzlink_aufloesen(p_code text)
returns text language plpgsql security definer set search_path to 'public' as $$
declare v_code text := lower(trim(coalesce(p_code,''))); v_url text;
begin
  if v_code = '' then return null; end if;
  select url into v_url from public.sommer2026_links where code = v_code;
  if v_url is null then select url into v_url from public.qr_links where code = v_code; end if;
  if v_url is not null then insert into public.link_hits (code) values (v_code); end if;
  return v_url;
end; $$;
revoke execute on function public.kurzlink_aufloesen(text) from public, anon, authenticated;
