-- =============================================================================
-- Umkehrbar statt abgeschlossen (Beschluss des Inhabers, 5. 11. 2026)
-- Migration «werkzeuge_umkehrbar»
--
-- Die Werkzeuge bleiben ohne Schlüssel zugänglich. Wer etwas kaputt macht,
-- richtet keinen bleibenden Schaden an:
--   · Folder:      jede Sicherung hält die überschriebene Fassung fest.
--   · Kurzlinks:   Gelöschtes landet im Archiv (samt Zählung), ein Link auf
--                  eine noch nie verwendete Domain meldet sich per Mail.
--   · Sommer-Zähler: Ändern und Löschen landet im Protokoll.
-- Alle Archive: RLS an, keine Rechte für anon/authenticated. Zurückholen per
-- SQL (Rezepte in CLAUDE-REF.md § Werkzeug-Schutz).
-- =============================================================================

-- ---------- Folder: Fassungen -------------------------------------------------
create table if not exists public.folder_fassung (
  id        bigint generated always as identity primary key,
  folder_id uuid not null,
  am        timestamptz not null default now(),
  titel     text,
  stand     jsonb not null
);
create index if not exists folder_fassung_folder on public.folder_fassung (folder_id, am desc);
alter table public.folder_fassung enable row level security;
revoke all on public.folder_fassung from anon, authenticated;

-- Hält den Stand fest, BEVOR er überschrieben wird: höchstens alle zehn
-- Minuten eine Fassung (das Auto-Archiv speichert alle paar Sekunden), bei
-- jedem Export immer. Je Folder bleiben die letzten 60 Fassungen.
create or replace function public.folder_fassung_halten()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  if old.stand is distinct from new.stand and (
       jsonb_array_length(coalesce(new.exporte,'[]')) > jsonb_array_length(coalesce(old.exporte,'[]'))
       or not exists (select 1 from public.folder_fassung f
                       where f.folder_id = old.id and f.am > now() - interval '10 minutes')) then
    insert into public.folder_fassung (folder_id, titel, stand) values (old.id, old.titel, old.stand);
    delete from public.folder_fassung f
     where f.folder_id = old.id
       and f.id not in (select f2.id from public.folder_fassung f2 where f2.folder_id = old.id order by f2.am desc limit 60);
  end if;
  return new;
end;
$$;
drop trigger if exists folder_fassung_halten on public.folder_archiv;
create trigger folder_fassung_halten before update on public.folder_archiv
for each row execute function public.folder_fassung_halten();

-- ---------- Kurzlinks: Archiv der gelöschten ----------------------------------
create table if not exists public.kurzlink_geloescht (
  id           bigint generated always as identity primary key,
  geloescht_am timestamptz not null default now(),
  quelle       text not null,          -- qr_links | sommer2026_links
  code         text,
  url          text,
  zeile        jsonb not null,         -- die ganze gelöschte Zeile
  hits         jsonb                   -- die Zählung (link_hits), falls mitgelöscht
);
alter table public.kurzlink_geloescht enable row level security;
revoke all on public.kurzlink_geloescht from anon, authenticated;

create or replace function public.kurzlink_archivieren()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.kurzlink_geloescht (quelle, code, url, zeile, hits)
  values (tg_table_name, old.code, old.url, to_jsonb(old),
          case when old.code is null then null else
            (select jsonb_agg(to_jsonb(h)) from public.link_hits h where h.code = old.code) end);
  return old;
end;
$$;
drop trigger if exists kurzlink_archivieren on public.qr_links;
create trigger kurzlink_archivieren before delete on public.qr_links
for each row execute function public.kurzlink_archivieren();
drop trigger if exists kurzlink_archivieren on public.sommer2026_links;
create trigger kurzlink_archivieren before delete on public.sommer2026_links
for each row execute function public.kurzlink_archivieren();

-- ---------- Kurzlinks: Meldung bei neuer Domain -------------------------------
-- Konfiguration (Werte nie im Repo):
--   melde_url  : https://<projekt>.supabase.co/functions/v1/kurzlink-melden
--   melde_key  : gemeinsames Geheimnis DB ⇄ Function
--   empfaenger : Mailadresse
create table if not exists public.kurzlink_config (key text primary key, value text not null);
alter table public.kurzlink_config enable row level security;
revoke all on public.kurzlink_config from anon, authenticated;

create or replace function public.kurzlink_host(p_url text)
returns text language sql immutable set search_path = ''
as $$ select regexp_replace(lower(substring(coalesce(p_url,'') from '^[a-zA-Z]+://([^/:?#]+)')), '^www\.', '') $$;

create or replace function public.kurzlink_neue_domain()
returns trigger language plpgsql security definer set search_path = ''
as $$
declare h text := public.kurzlink_host(new.url); v_url text; v_key text;
begin
  if h is null or h = '' then return new; end if;
  -- Nach dem Insert steht der neue Link schon in seiner Tabelle: neu ist die
  -- Domain, wenn sie insgesamt genau einmal vorkommt (auch nicht im Archiv).
  if (select count(*) from public.qr_links q where public.kurzlink_host(q.url) = h)
     + (select count(*) from public.sommer2026_links s where public.kurzlink_host(s.url) = h) > 1
     or exists (select 1 from public.kurzlink_geloescht g where public.kurzlink_host(g.url) = h) then
    return new;
  end if;
  begin
    select value into v_url from public.kurzlink_config where key = 'melde_url';
    select value into v_key from public.kurzlink_config where key = 'melde_key';
    if coalesce(v_url,'') <> '' then
      perform net.http_post(
        url := v_url,
        headers := jsonb_build_object('Content-Type','application/json'),
        body := jsonb_build_object('code', new.code, 'url', new.url, 'domain', h,
                                   'quelle', tg_table_name, 'key', coalesce(v_key,'')));
    end if;
  exception when others then null;   -- Netz weg: egal, der Link ist gespeichert
  end;
  return new;
end;
$$;
drop trigger if exists kurzlink_neue_domain on public.qr_links;
create trigger kurzlink_neue_domain after insert on public.qr_links
for each row execute function public.kurzlink_neue_domain();
drop trigger if exists kurzlink_neue_domain on public.sommer2026_links;
create trigger kurzlink_neue_domain after insert on public.sommer2026_links
for each row execute function public.kurzlink_neue_domain();

-- ---------- Sommer-Zähler: Protokoll ------------------------------------------
create table if not exists public.sommer2026_protokoll (
  id      bigint generated always as identity primary key,
  am      timestamptz not null default now(),
  tabelle text not null,
  aktion  text not null,             -- UPDATE | DELETE
  alt     jsonb not null             -- die Zeile vor der Änderung
);
alter table public.sommer2026_protokoll enable row level security;
revoke all on public.sommer2026_protokoll from anon, authenticated;

create or replace function public.sommer2026_protokollieren()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.sommer2026_protokoll (tabelle, aktion, alt) values (tg_table_name, tg_op, to_jsonb(old));
  return null;
end;
$$;
do $$
declare t text;
begin
  foreach t in array array['sommer2026_kosten','sommer2026_massnahmen','sommer2026_multiplikatoren','sommer2026_multi_kontakte'] loop
    execute format('drop trigger if exists sommer2026_protokoll on public.%I', t);
    execute format('create trigger sommer2026_protokoll after update or delete on public.%I
                    for each row execute function public.sommer2026_protokollieren()', t);
  end loop;
end
$$;

-- Trigger-Funktionen sind nicht zum Aufrufen da
revoke execute on function public.folder_fassung_halten(), public.kurzlink_archivieren(),
  public.kurzlink_neue_domain(), public.sommer2026_protokollieren() from public, anon, authenticated;
