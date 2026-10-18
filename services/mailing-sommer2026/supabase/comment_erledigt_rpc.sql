-- Erledigt-Haken im Mail-Editor: anon darf NICHT breit updaten, nur diese eine
-- Spalte über die RPC kippen (security definer, fester search_path).
-- Angewendet auf dagcsnfrlbpxcmdimnrw (Migration comment_erledigt_rpc).
create or replace function public.sommer2026_comment_erledigt(kommentar_id bigint, wert boolean default true)
returns void
language sql
security definer
set search_path = public
as $$
  update public.sommer2026_mail_comments set erledigt = wert where id = kommentar_id;
$$;

revoke all on function public.sommer2026_comment_erledigt(bigint, boolean) from public;
grant execute on function public.sommer2026_comment_erledigt(bigint, boolean) to anon, authenticated;
