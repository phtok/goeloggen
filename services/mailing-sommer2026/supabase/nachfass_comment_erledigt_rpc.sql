-- Erledigt-Haken im Nachfass-Editor: anon darf NICHT breit updaten, nur diese
-- eine Spalte über die RPC kippen (security definer, fester search_path).
-- Angewendet auf dagcsnfrlbpxcmdimnrw (Migration create_nachfass_mail_comments).
create or replace function public.nachfass_comment_erledigt(kommentar_id bigint, wert boolean default true)
returns void
language sql
security definer
set search_path = public
as $$
  update public.nachfass_mail_comments set erledigt = wert where id = kommentar_id;
$$;

revoke all on function public.nachfass_comment_erledigt(bigint, boolean) from public;
grant execute on function public.nachfass_comment_erledigt(bigint, boolean) to anon, authenticated;
