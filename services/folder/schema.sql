-- =============================================================================
-- Goetheanum Folder · Archiv (apps/programmheft/live.html)
-- Projekt: dagcsnfrlbpxcmdimnrw (Werkzeug-Backend, wie schmiede_* / qr_links).
-- Jeder Folder, der im Editor entsteht, wird im Hintergrund als Stand (jsonb)
-- gesichert: laufend beim Bearbeiten und bei jedem Export (mit Art des Exports).
-- Rohzeilen zu; schreiben per anon-RPC, lesen nur mit dem Cockpit-Schlüssel
-- der Schmiede (schmiede_key_ok) – ein Schlüssel für die internen Eingänge.
-- Anwenden: einmal im Supabase-SQL-Editor ausführen (idempotent).
-- =============================================================================
create table if not exists public.folder_archiv (
  id          uuid primary key,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  titel       text not null default '',
  farbe       text not null default '',
  stand       jsonb not null default '{}'::jsonb,
  exporte     jsonb not null default '[]'::jsonb   -- [{art, am}]
);
create index if not exists folder_archiv_updated_idx on public.folder_archiv (updated_at desc);
alter table public.folder_archiv enable row level security;
revoke all on table public.folder_archiv from anon, authenticated;

-- Sichern (anon): legt an oder schreibt fort; p_export ('pdf-versand' | 'pdf-druck' | 'idml') vermerkt einen Export.
create or replace function public.folder_sichern(p_id uuid, p_stand jsonb, p_export text default null)
returns text language plpgsql security definer set search_path to 'public' as $$
begin
  if p_id is null or p_stand is null then return 'unvollstaendig'; end if;
  if octet_length(p_stand::text) > 15000000 then return 'zu_gross'; end if;
  insert into public.folder_archiv as f (id, titel, farbe, stand, exporte)
  values (p_id, left(coalesce(p_stand->>'titel',''),300), left(coalesce(p_stand->>'farbe',''),60), p_stand,
          case when p_export is null then '[]'::jsonb else jsonb_build_array(jsonb_build_object('art',p_export,'am',now())) end)
  on conflict (id) do update
     set stand = excluded.stand, titel = excluded.titel, farbe = excluded.farbe, updated_at = now(),
         exporte = f.exporte || excluded.exporte;
  return 'ok';
end; $$;
grant execute on function public.folder_sichern(uuid, jsonb, text) to anon, authenticated;

-- Liste (nur mit Schlüssel), ohne den schweren Stand.
create or replace function public.folder_liste(p_key text)
returns table(id uuid, created_at timestamptz, updated_at timestamptz, titel text, farbe text, exporte jsonb)
language plpgsql security definer set search_path to 'public' as $$
begin
  if not public.schmiede_key_ok(p_key) then return; end if;
  return query select f.id, f.created_at, f.updated_at, f.titel, f.farbe, f.exporte
                 from public.folder_archiv f order by f.updated_at desc;
end; $$;
grant execute on function public.folder_liste(text) to anon, authenticated;

-- Einen Stand holen (nur mit Schlüssel).
create or replace function public.folder_holen(p_key text, p_id uuid)
returns jsonb language plpgsql security definer set search_path to 'public' as $$
begin
  if not public.schmiede_key_ok(p_key) then return null; end if;
  return (select stand from public.folder_archiv where id = p_id);
end; $$;
grant execute on function public.folder_holen(text, uuid) to anon, authenticated;
