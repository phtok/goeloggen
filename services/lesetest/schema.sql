-- =============================================================================
-- Lesetest Hausschrift / Source Sans 3 (apps/lesetest/)
-- Projekt: dagcsnfrlbpxcmdimnrw (Werkzeug-Backend, wie reader_jahrgang).
-- Ein Datensatz je Durchgang. Anonym: gespeichert werden die Altersgruppe,
-- das Medium (Bildschirm/Papier), die Fensterbreite und je Text Lesezeit,
-- Antworten und Einschätzungen. Kein Name, keine Mail, keine IP.
-- Freigabe des Inhabers für Tabelle und Funktionen: 31. 10. 2026.
-- Rohzeilen zu; schreiben und lesen nur über die RPCs.
-- Anwenden: der Workflow .github/workflows/lesetest-schema.yml tut es bei
-- Änderung (idempotent), oder einmal im Supabase-SQL-Editor.
-- =============================================================================
create table if not exists public.lesetest_durchgang (
  id          bigint generated always as identity primary key,
  schluessel  uuid not null default gen_random_uuid(),
  begonnen    timestamptz not null default now(),
  abgegeben   timestamptz,
  gruppe      smallint not null check (gruppe between 0 and 7),
  medium      text not null default 'bildschirm' check (medium in ('bildschirm', 'papier')),
  alter_gruppe text not null default '',
  fenster     integer,
  daten       jsonb
);
create index if not exists lesetest_durchgang_gruppe_idx on public.lesetest_durchgang (gruppe);
alter table public.lesetest_durchgang enable row level security;
revoke all on table public.lesetest_durchgang from anon, authenticated;

-- Beginnen: legt den Durchgang an und teilt die Gruppe zu (Zuteilung der Texte
-- und Schriften). Bildschirm: die Gruppe mit den wenigsten Durchgängen, die
-- abgegeben oder in der letzten Stunde begonnen wurden. Papier: die Gruppe
-- steht auf dem Bogen (1–8) und kommt mit. Ebenso, wenn der Browser beim
-- Start keine Verbindung hatte und die Gruppe selbst gewählt hat.
create or replace function public.lesetest_beginnen(p_medium text, p_alter text default '',
                                                    p_fenster integer default null, p_bogen integer default null)
returns jsonb language plpgsql security definer set search_path to 'public' as $$
declare
  v_gruppe smallint;
  neu record;
begin
  if p_medium not in ('bildschirm', 'papier') then return jsonb_build_object('status', 'medium'); end if;
  if p_bogen is not null then
    if p_bogen not between 1 and 8 then return jsonb_build_object('status', 'bogen'); end if;
    v_gruppe := p_bogen - 1;
  elsif p_medium = 'papier' then
    return jsonb_build_object('status', 'bogen');
  else
    select s.nr into v_gruppe
      from generate_series(0, 7) as s(nr)
      left join public.lesetest_durchgang d
        on d.gruppe = s.nr and (d.abgegeben is not null or d.begonnen > now() - interval '1 hour')
     group by s.nr
     order by count(d.id), random()
     limit 1;
  end if;
  insert into public.lesetest_durchgang (gruppe, medium, alter_gruppe, fenster)
  values (v_gruppe, p_medium, left(coalesce(p_alter, ''), 20), p_fenster)
  returning id, schluessel into neu;
  return jsonb_build_object('status', 'ok', 'id', neu.id, 'schluessel', neu.schluessel, 'gruppe', v_gruppe);
end; $$;
grant execute on function public.lesetest_beginnen(text, text, integer, integer) to anon, authenticated;

-- Abgeben: schreibt die Messungen; nur mit dem Schlüssel des Durchgangs und
-- nur einmal.
create or replace function public.lesetest_abgeben(p_id bigint, p_schluessel uuid, p_daten jsonb)
returns jsonb language plpgsql security definer set search_path to 'public' as $$
begin
  if p_daten is null or octet_length(p_daten::text) > 50000 then return jsonb_build_object('status', 'ungueltig'); end if;
  update public.lesetest_durchgang
     set daten = p_daten, abgegeben = now()
   where id = p_id and schluessel = p_schluessel and abgegeben is null;
  if not found then return jsonb_build_object('status', 'unbekannt'); end if;
  return jsonb_build_object('status', 'ok');
end; $$;
grant execute on function public.lesetest_abgeben(bigint, uuid, jsonb) to anon, authenticated;

-- Auswertung: alle abgegebenen Durchgänge, ohne Schlüssel. Die Daten sind
-- anonym; die Auswertungsseite rechnet im Browser.
create or replace function public.lesetest_ergebnisse()
returns table(id bigint, abgegeben timestamptz, gruppe smallint, medium text,
              alter_gruppe text, fenster integer, daten jsonb)
language sql security definer set search_path to 'public' as $$
  select d.id, d.abgegeben, d.gruppe, d.medium, d.alter_gruppe, d.fenster, d.daten
    from public.lesetest_durchgang d
   where d.abgegeben is not null
   order by d.abgegeben;
$$;
grant execute on function public.lesetest_ergebnisse() to anon, authenticated;
