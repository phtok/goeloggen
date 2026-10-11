-- =============================================================================
-- Tagungs-Reader · Jahrgänge (apps/lt-reader/)
-- Projekt: dagcsnfrlbpxcmdimnrw (Werkzeug-Backend, wie folder_archiv / qr_links).
-- Ein Datensatz je Jahrgang (jahr = Schlüssel). Das Werkzeug sichert beim
-- Tippen im Hintergrund; jede Sicherung, die älter als zehn Minuten nach der
-- letzten Fassung liegt, legt zusätzlich eine Fassung ab (Verlauf).
-- Kein Login (wie der Folder, Beschluss 24. 9. 2026): versteckter Link reicht.
-- Rohzeilen zu; schreiben und lesen nur über die RPCs.
-- Anwenden: einmal im Supabase-SQL-Editor ausführen (idempotent) – oder der
-- Workflow .github/workflows/lt-reader-schema.yml tut es bei Änderung.
-- =============================================================================
create table if not exists public.reader_jahrgang (
  jahr        integer primary key,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  von         text not null default '',
  stand       jsonb not null default '{}'::jsonb
);
alter table public.reader_jahrgang enable row level security;
revoke all on table public.reader_jahrgang from anon, authenticated;

create table if not exists public.reader_fassung (
  id          bigint generated always as identity primary key,
  jahr        integer not null references public.reader_jahrgang (jahr) on delete cascade,
  am          timestamptz not null default now(),
  von         text not null default '',
  anlass      text not null default '',       -- '' (laufend) | 'export-idml' | 'export-pdf' | 'einfrieren'
  stand       jsonb not null
);
create index if not exists reader_fassung_jahr_idx on public.reader_fassung (jahr, am desc);
alter table public.reader_fassung enable row level security;
revoke all on table public.reader_fassung from anon, authenticated;

-- Sichern (anon). p_seit = updated_at, das der Browser zuletzt gesehen hat:
-- liegt auf dem Server ein jüngerer Stand von jemand anderem, kommt 'ueberholt'
-- zurück und nichts wird geschrieben (der Browser lädt dann neu).
create or replace function public.reader_sichern(p_jahr integer, p_stand jsonb, p_von text default '',
                                                 p_seit timestamptz default null, p_anlass text default '')
returns jsonb language plpgsql security definer set search_path to 'public' as $$
declare
  alt record;
  letzte timestamptz;
  jetzt timestamptz := now();
begin
  if p_jahr is null or p_stand is null then return jsonb_build_object('status', 'unvollstaendig'); end if;
  if octet_length(p_stand::text) > 15000000 then return jsonb_build_object('status', 'zu_gross'); end if;
  select * into alt from public.reader_jahrgang where jahr = p_jahr;
  if found and p_seit is not null and alt.updated_at > p_seit + interval '1 second'
     and coalesce(alt.von, '') <> coalesce(p_von, '') then
    return jsonb_build_object('status', 'ueberholt', 'updated_at', alt.updated_at, 'von', alt.von);
  end if;
  insert into public.reader_jahrgang as j (jahr, von, stand, updated_at)
  values (p_jahr, left(coalesce(p_von, ''), 80), p_stand, jetzt)
  on conflict (jahr) do update
     set stand = excluded.stand, von = excluded.von, updated_at = jetzt;
  select max(am) into letzte from public.reader_fassung where jahr = p_jahr;
  if p_anlass <> '' or letzte is null or letzte < jetzt - interval '10 minutes' then
    insert into public.reader_fassung (jahr, von, anlass, stand)
    values (p_jahr, left(coalesce(p_von, ''), 80), left(coalesce(p_anlass, ''), 40), p_stand);
  end if;
  return jsonb_build_object('status', 'ok', 'updated_at', jetzt);
end; $$;
grant execute on function public.reader_sichern(integer, jsonb, text, timestamptz, text) to anon, authenticated;

-- Den aktuellen Stand eines Jahrgangs holen (null, wenn es ihn noch nicht gibt).
create or replace function public.reader_holen(p_jahr integer)
returns jsonb language sql security definer set search_path to 'public' as $$
  select jsonb_build_object('stand', stand, 'updated_at', updated_at, 'von', von)
    from public.reader_jahrgang where jahr = p_jahr;
$$;
grant execute on function public.reader_holen(integer) to anon, authenticated;

-- Welche Jahrgänge gibt es (ohne den schweren Stand).
create or replace function public.reader_jahrgaenge()
returns table(jahr integer, updated_at timestamptz, von text)
language sql security definer set search_path to 'public' as $$
  select j.jahr, j.updated_at, j.von from public.reader_jahrgang j order by j.jahr desc;
$$;
grant execute on function public.reader_jahrgaenge() to anon, authenticated;

-- Fassungen eines Jahrgangs (Verlauf), neueste zuerst.
create or replace function public.reader_fassungen(p_jahr integer)
returns table(id bigint, am timestamptz, von text, anlass text)
language sql security definer set search_path to 'public' as $$
  select f.id, f.am, f.von, f.anlass from public.reader_fassung f
   where f.jahr = p_jahr order by f.am desc limit 200;
$$;
grant execute on function public.reader_fassungen(integer) to anon, authenticated;

-- Eine Fassung holen.
create or replace function public.reader_fassung_holen(p_id bigint)
returns jsonb language sql security definer set search_path to 'public' as $$
  select stand from public.reader_fassung where id = p_id;
$$;
grant execute on function public.reader_fassung_holen(bigint) to anon, authenticated;
