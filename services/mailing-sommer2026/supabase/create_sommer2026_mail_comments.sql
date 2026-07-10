-- Bereits auf dagcsnfrlbpxcmdimnrw angewendet (Migration create_sommer2026_mail_comments).
create table if not exists public.sommer2026_mail_comments (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  mail_key   text not null,
  sprache    text,
  autor      text,
  kommentar  text not null,
  erledigt   boolean not null default false
);
alter table public.sommer2026_mail_comments enable row level security;
create policy "anon insert kommentar" on public.sommer2026_mail_comments for insert to anon with check (true);
create policy "anon select kommentar" on public.sommer2026_mail_comments for select to anon using (true);
