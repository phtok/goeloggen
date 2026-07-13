-- =============================================================================
-- Werkzeug-Schmiede · Backend-Schema
-- Projekt: Supabase «Public Secrets App» (dagcsnfrlbpxcmdimnrw) – dasselbe
-- Werkzeug-Backend wie sommer2026_* / qr_links / goeloggen_stats.
-- Angewendet als Migration «schmiede_auftraege».
--
-- Unterschied zur Statistik (WICHTIG): die anonyme Zählung darf offen sein, weil
-- nur SUMMEN die DB verlassen. Ein Auftrag trägt aber KONTAKTDATEN – die dürfen
-- NICHT anon lesbar sein. Deshalb:
--   · Rohtabelle zu (RLS an, keine Policy, Rechte entzogen).
--   · Schreiben: eine security-definer-RPC (anon) – nur rein, nie raus.
--   · Lesen/Taggen: NUR über einen Geheim-Schlüssel (Cockpit), Hash in der
--     Config verglichen – ohne Schlüssel kommt nichts zurück (Muster wie
--     qr_link_loeschen). Kein anon-Leseweg auf die Zeilen.
--   · Info-Ping per Resend über die Edge Function schmiede-melden (net.http_post),
--     Absender/Key wie beim Lead-Agent in einer Config-Zeile – nie im Repo.
-- =============================================================================

-- --- Eingang der Wünsche --------------------------------------------------------
create table if not exists public.schmiede_auftraege (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  titel       text not null,
  daten       jsonb not null default '{}'::jsonb,   -- alle Formularfelder (zweck, kontakt, quellen …)
  auftrag_md  text,                                 -- der zusammengestellte Auftrag als Text
  status      text not null default 'neu' check (status in ('neu','gesehen','in_arbeit','erledigt')),
  tags        text[] not null default '{}',         -- frei taggbar im Cockpit
  notiz       text                                  -- interne Triage-Notiz
);
create index if not exists schmiede_auftraege_status_idx on public.schmiede_auftraege (status, created_at desc);
alter table public.schmiede_auftraege enable row level security;
-- Bewusst KEINE anon-Policy: RLS an + keine Policy = Rohzeilen zu (Kontaktdaten!).
revoke all on table public.schmiede_auftraege from anon, authenticated;

comment on table public.schmiede_auftraege is
  'Werkzeug-Schmiede: eine Zeile je eingegangenem Wunsch. Rohzeilen zu (Kontaktdaten); Lesen/Taggen nur über den Cockpit-Schlüssel.';

-- --- Versiegelte Config (Schlüssel-Hash, Ping-Ziel) -----------------------------
create table if not exists public.schmiede_config (
  key   text primary key,
  value text not null
);
alter table public.schmiede_config enable row level security;
revoke all on table public.schmiede_config from anon, authenticated;
-- Schlüssel in schmiede_config:
--   cockpit_key_hash : encode(digest('goe-schmiede:' || lower(trim(schluessel)), 'sha256'), 'hex')
--   melde_url        : https://<projekt>.supabase.co/functions/v1/schmiede-melden   (optional; ohne = kein Ping)
--   melde_key        : gemeinsames Geheimnis Edge Function ⇄ DB (gen_random_bytes)  (optional)

-- Prüft den Cockpit-Schlüssel gegen den Hash (gross/klein- und leerraum-tolerant).
create or replace function public.schmiede_key_ok(p_key text)
returns boolean language sql security definer set search_path to 'public','extensions' as $$
  select exists (
    select 1 from public.schmiede_config c
     where c.key = 'cockpit_key_hash'
       and c.value = encode(extensions.digest('goe-schmiede:' || lower(trim(coalesce(p_key,''))), 'sha256'), 'hex')
  );
$$;
revoke execute on function public.schmiede_key_ok(text) from public, anon, authenticated;

-- --- Schreiben (anon): 'ok' | 'unvollstaendig' -----------------------------------
-- Honigtopf p_honeypot: ist es gefüllt, tun wir so als ob (kein Eintrag, 'ok'),
-- damit ein Bot keinen Unterschied merkt (Muster lead-fang «website»).
create or replace function public.schmiede_auftrag_anlegen(
  p_titel text, p_daten jsonb, p_md text default null, p_honeypot text default ''
) returns text language plpgsql security definer set search_path to 'public' as $$
declare v_titel text := nullif(trim(coalesce(p_titel,'')), '');
        v_url text; v_key text;
begin
  if coalesce(trim(p_honeypot),'') <> '' then return 'ok'; end if;   -- Bot: still schlucken
  if v_titel is null and coalesce(trim(p_md),'') = '' then return 'unvollstaendig'; end if;

  insert into public.schmiede_auftraege (titel, daten, auftrag_md)
  values (coalesce(v_titel,'ohne Namen'), coalesce(p_daten,'{}'::jsonb), nullif(trim(coalesce(p_md,'')),''));

  -- Info-Ping (fire-and-forget; darf den Eintrag NIE gefährden).
  begin
    select value into v_url from public.schmiede_config where key = 'melde_url';
    select value into v_key from public.schmiede_config where key = 'melde_key';
    if coalesce(v_url,'') <> '' then
      perform net.http_post(
        url := v_url,
        headers := jsonb_build_object('Content-Type','application/json'),
        body := jsonb_build_object('titel', coalesce(v_titel,'ohne Namen'), 'key', coalesce(v_key,''))
      );
    end if;
  exception when others then null;   -- pg_net fehlt/Netz weg: egal, der Wunsch ist gespeichert
  end;

  return 'ok';
end; $$;
grant execute on function public.schmiede_auftrag_anlegen(text, jsonb, text, text) to anon, authenticated;

-- --- Lesen (Cockpit, nur mit Schlüssel) -----------------------------------------
-- Ohne gültigen Schlüssel: leere Menge. Kein Enumerieren, kein Leck.
create or replace function public.schmiede_liste(p_key text)
returns table(id bigint, created_at timestamptz, titel text, daten jsonb,
              auftrag_md text, status text, tags text[], notiz text)
language plpgsql security definer set search_path to 'public' as $$
begin
  if not public.schmiede_key_ok(p_key) then return; end if;
  return query
    select a.id, a.created_at, a.titel, a.daten, a.auftrag_md, a.status, a.tags, a.notiz
      from public.schmiede_auftraege a
     order by (a.status = 'erledigt'), a.created_at desc;
end; $$;
grant execute on function public.schmiede_liste(text) to anon, authenticated;

-- --- Taggen / Status / Notiz (Cockpit, nur mit Schlüssel) -----------------------
-- 'ok' | 'schluessel' | 'unbekannt' | 'ungueltig'
create or replace function public.schmiede_setzen(
  p_key text, p_id bigint, p_status text default null, p_tags text[] default null, p_notiz text default null
) returns text language plpgsql security definer set search_path to 'public' as $$
declare n int;
begin
  if not public.schmiede_key_ok(p_key) then return 'schluessel'; end if;
  if p_status is not null and p_status not in ('neu','gesehen','in_arbeit','erledigt') then return 'ungueltig'; end if;
  update public.schmiede_auftraege
     set status = coalesce(p_status, status),
         tags   = coalesce(p_tags, tags),
         notiz  = coalesce(p_notiz, notiz)
   where id = p_id;
  get diagnostics n = row_count;
  if n = 0 then return 'unbekannt'; end if;
  return 'ok';
end; $$;
grant execute on function public.schmiede_setzen(text, bigint, text, text[], text) to anon, authenticated;
