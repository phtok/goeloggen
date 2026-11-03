-- =============================================================================
-- Werkzeug-Schlüssel: schreibende und heikle lesende RPCs nur noch mit Schlüssel
-- (Sicherheits-Review vom 3. 11. 2026, Migration «werkzeug_schluessel_a»)
--
-- Bauart: Die bisherige Funktion zieht unverändert ins Schema werkzeug_intern
-- (für anon/authenticated unerreichbar). An ihrer Stelle steht in public eine
-- Hülle mit derselben Signatur plus `p_key text default null`, die erst
-- public.werkzeug_tor() fragt und dann durchreicht. Die Rümpfe bleiben so,
-- wie sie waren – nachzulesen in den Schema-Dateien der Dienste.
--
-- Drei Phasen (damit live nichts bricht):
--   A  pflicht = false: ohne Schlüssel geht es noch, ein falscher wird abgewiesen.
--   B  Aufrufer schicken den Schlüssel mit (Browser merkt ihn sich).
--   C  update public.werkzeug_schluessel set pflicht = true where werkzeug = '…';
--
-- Geheimnisse stehen hier NICHT. Die Hashes werden in DERSELBEN Transaktion
-- gesetzt (sonst ist jedes Werkzeug zu, denn ein unbekanntes Werkzeug ist zu):
--   insert into public.werkzeug_schluessel (werkzeug, hash) values ('<werkzeug>',
--     encode(extensions.digest('goe-werkzeug:<werkzeug>:' || '<normalisierter Schlüssel>', 'sha256'), 'hex'));
-- Normalisiert = klein geschrieben, alles ausser a–z/0–9 entfernt
-- (Bindestriche und Leerzeichen beim Eintippen sind also egal).
-- =============================================================================

create schema if not exists werkzeug_intern;
revoke all on schema werkzeug_intern from public, anon, authenticated;

create table if not exists public.werkzeug_schluessel (
  werkzeug  text primary key,
  hash      text not null,
  pflicht   boolean not null default false,
  geaendert timestamptz not null default now()
);
alter table public.werkzeug_schluessel enable row level security;
revoke all on public.werkzeug_schluessel from anon, authenticated;

-- Normalform eines eingetippten Schlüssels
create or replace function public.werkzeug_key_norm(p_key text)
returns text language sql immutable set search_path = ''
as $$ select lower(regexp_replace(coalesce(p_key, ''), '[^A-Za-z0-9]', '', 'g')) $$;

-- Stimmt der Schlüssel? (öffentlich – für die Rückmeldung beim Eintippen)
create or replace function public.werkzeug_key_ok(p_werkzeug text, p_key text)
returns boolean language sql stable security definer set search_path = ''
as $$
  select public.werkzeug_key_norm(p_key) <> '' and exists (
    select 1 from public.werkzeug_schluessel w
     where w.werkzeug = p_werkzeug
       and w.hash = encode(extensions.digest('goe-werkzeug:' || p_werkzeug || ':' || public.werkzeug_key_norm(p_key), 'sha256'), 'hex'));
$$;
revoke execute on function public.werkzeug_key_ok(text, text) from public;
grant execute on function public.werkzeug_key_ok(text, text) to anon, authenticated, service_role;

-- Das Tor: interne Aufrufe (keine Anfrage-Rolle) und service_role gehen durch;
-- unbekanntes Werkzeug = zu; leerer Schlüssel nur, solange pflicht = false.
create or replace function public.werkzeug_tor(p_werkzeug text, p_key text)
returns boolean language plpgsql stable security definer set search_path = ''
as $$
declare r public.werkzeug_schluessel;
begin
  if auth.role() is null or auth.role() = 'service_role' then return true; end if;
  select * into r from public.werkzeug_schluessel where werkzeug = p_werkzeug;
  if not found then return false; end if;
  if public.werkzeug_key_norm(p_key) = '' then return not r.pflicht; end if;
  return public.werkzeug_key_ok(p_werkzeug, p_key);
end;
$$;
revoke execute on function public.werkzeug_tor(text, text) from public, anon, authenticated;

-- Hüllen bauen (idempotent: was schon in werkzeug_intern liegt, wird übersprungen)
do $do$
declare
  z record; f record;
  callargs text; sig text; body text;
begin
  for z in select * from (values
    ('qr_link_anlegen','kurzlinks','p_key'), ('qr_link_loeschen','kurzlinks','p_key'),
    ('sommer2026_link_anlegen','kurzlinks','p_schluessel'), ('sommer2026_link_loeschen','kurzlinks','p_schluessel'),
    ('folder_liste','folder','p_key'), ('folder_holen','folder','p_key'), ('folder_sichern','folder','p_key'),
    ('reader_jahrgaenge','reader','p_key'), ('reader_holen','reader','p_key'), ('reader_sichern','reader','p_key'),
    ('reader_fassungen','reader','p_key'), ('reader_fassung_holen','reader','p_key'),
    ('sommer2026_kosten_eintragen','zaehler','p_key'), ('sommer2026_kosten_loeschen','zaehler','p_key'),
    ('sommer2026_kosten_produkt_setzen','zaehler','p_key'), ('sommer2026_kosten_public','zaehler','p_key'),
    ('sommer2026_einnahmen','zaehler','p_key'),
    ('sommer2026_massnahme_eintragen','zaehler','p_key'), ('sommer2026_massnahme_aendern','zaehler','p_key'),
    ('sommer2026_multi_anlegen','zaehler','p_key'), ('sommer2026_multi_kontakt_anlegen','zaehler','p_key'),
    ('sommer2026_multi_protokoll','zaehler','p_key'),
    ('lesetest_ergebnisse','lesetest','p_key')
  ) as t(fn, werkzeug, keyparam)
  loop
    if exists (select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace
                where n.nspname = 'werkzeug_intern' and p.proname = z.fn) then
      continue;
    end if;
    select p.oid, p.proretset,
           pg_get_function_arguments(p.oid) args,
           pg_get_function_identity_arguments(p.oid) ident,
           pg_get_function_result(p.oid) res,
           coalesce((select string_agg(format('%1$I => %1$I', a.name), ', ' order by a.ord)
                       from unnest(p.proargnames, coalesce(p.proargmodes, array_fill('i'::"char", array[coalesce(cardinality(p.proargnames), 0)])))
                            with ordinality as a(name, mode, ord)
                      where a.mode in ('i','b')), '') callargs
      into f
      from pg_proc p join pg_namespace n on n.oid = p.pronamespace
     where n.nspname = 'public' and p.proname = z.fn;
    if not found then raise exception 'Funktion % fehlt', z.fn; end if;

    execute format('alter function public.%I(%s) set schema werkzeug_intern', z.fn, f.ident);
    execute format('revoke all on function werkzeug_intern.%I(%s) from public, anon, authenticated', z.fn, f.ident);

    sig := case when z.keyparam <> 'p_key' then f.args
                when f.args = '' then 'p_key text default null'
                else f.args || ', p_key text default null' end;
    body := case when f.proretset
                 then format('return query select * from werkzeug_intern.%I(%s);', z.fn, f.callargs)
                 else format('return werkzeug_intern.%I(%s);', z.fn, f.callargs) end;

    execute format($f$
      create function public.%I(%s) returns %s
      language plpgsql security definer set search_path = ''
      as $w$
      begin
        if not public.werkzeug_tor(%L, %I) then
          raise exception 'schluessel_falsch' using errcode = '28000',
            hint = 'Werkzeug-Schlüssel fehlt oder stimmt nicht.';
        end if;
        %s
      end
      $w$$f$, z.fn, sig, f.res, z.werkzeug, z.keyparam, body);
    execute format('revoke execute on function public.%I from public', z.fn);
    execute format('grant execute on function public.%I to anon, authenticated, service_role', z.fn);
  end loop;
end
$do$;

-- succow26_*: Klartext-Token im Rumpf durch Hash ersetzen (Token bleibt gleich,
-- Aufrufer merken nichts; pflicht von Anfang an). Liest den Token aus dem alten
-- Rumpf, damit er in keiner Datei steht.
do $do$
declare tok text; d text; fn text;
begin
  select substring(p.prosrc from 'is distinct from ''([^'']+)''') into tok
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public' and p.proname = 'succow26_list';
  if tok is null then return; end if;   -- schon umgebaut
  insert into public.werkzeug_schluessel (werkzeug, hash, pflicht)
  values ('succow26', encode(extensions.digest('goe-werkzeug:succow26:' || public.werkzeug_key_norm(tok), 'sha256'), 'hex'), true)
  on conflict (werkzeug) do nothing;
  foreach fn in array array['succow26_list','succow26_upsert'] loop
    select pg_get_functiondef(p.oid) into d
      from pg_proc p join pg_namespace n on n.oid = p.pronamespace
     where n.nspname = 'public' and p.proname = fn;
    d := regexp_replace(d, 'token is distinct from ''[^'']+''', 'not public.werkzeug_tor(''succow26'', token)');
    if position(tok in d) > 0 then raise exception 'Token noch im Rumpf von %', fn; end if;
    execute d;
  end loop;
end
$do$;

notify pgrst, 'reload schema';
