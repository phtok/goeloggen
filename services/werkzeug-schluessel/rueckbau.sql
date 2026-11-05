-- =============================================================================
-- Rückbau der Werkzeug-Schlüssel (Beschluss des Inhabers, 5. 11. 2026)
-- Migration «werkzeug_schluessel_rueckbau»
--
-- Die Hüllen aus schema.sql (Migration «werkzeug_schluessel_a») fallen weg,
-- die ursprünglichen Funktionen kehren unverändert nach public zurück.
-- Schutz entsteht stattdessen durch Umkehrbarkeit (umkehrbar.sql).
-- Bleibt: werkzeug_tor/werkzeug_key_ok/werkzeug_schluessel – nur noch für
-- succow26_* (dessen Token nun als Hash statt im Klartext im Rumpf steht).
-- =============================================================================
do $do$
declare f record;
begin
  for f in
    select p.proname, pg_get_function_identity_arguments(p.oid) ident
      from pg_proc p join pg_namespace n on n.oid = p.pronamespace
     where n.nspname = 'werkzeug_intern'
  loop
    -- die Hülle in public (gleicher Name; ggf. mit p_key)
    execute (select string_agg(format('drop function public.%I(%s)', p.proname, pg_get_function_identity_arguments(p.oid)), '; ')
               from pg_proc p join pg_namespace n on n.oid = p.pronamespace
              where n.nspname = 'public' and p.proname = f.proname);
    execute format('alter function werkzeug_intern.%I(%s) set schema public', f.proname, f.ident);
    execute format('grant execute on function public.%I(%s) to anon, authenticated, service_role', f.proname, f.ident);
  end loop;
end
$do$;
drop schema if exists werkzeug_intern;
delete from public.werkzeug_schluessel where werkzeug <> 'succow26';
-- Ohne Werkzeug-Dialog braucht niemand mehr die öffentliche Prüfung.
revoke execute on function public.werkzeug_key_ok(text, text) from anon, authenticated;
notify pgrst, 'reload schema';
