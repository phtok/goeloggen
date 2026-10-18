-- Nachfass-Editor (apps/nachfass-editor/): eigene Kommentar-Tabelle, damit
-- Onboarding-Kommentare NICHT in der laufenden Kampagnen-To-do-Liste
-- (sommer2026_mail_comments) auftauchen. Spiegelt jene Tabelle 1:1.
-- Angewendet auf dagcsnfrlbpxcmdimnrw (Migration create_nachfass_mail_comments).
create table if not exists public.nachfass_mail_comments (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  mail_key   text not null,
  sprache    text,
  autor      text,
  kommentar  text not null,
  erledigt   boolean not null default false
);
alter table public.nachfass_mail_comments enable row level security;
create policy "anon insert kommentar" on public.nachfass_mail_comments for insert to anon with check (true);
create policy "anon select kommentar" on public.nachfass_mail_comments for select to anon using (true);
