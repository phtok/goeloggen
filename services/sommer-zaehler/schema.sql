-- =============================================================================
-- Sommer-Zähler 2026 · Backend-Schema
-- Projekt: Supabase «Public Secrets App» (dagcsnfrlbpxcmdimnrw) – dasselbe
-- Werkzeug-Backend, das schon landing_events / gtv_naming_events / signatur_events
-- trägt. Angewendet als Migration «sommer2026_signups».
--
-- Prinzip wie statistik.html: Rohtabelle bleibt für anon geschlossen (RLS an,
-- keine Policy, Rechte entzogen). Nur die Aggregat-RPCs sind für anon offen –
-- es verlassen ausschliesslich Summen die Datenbank, keine Personendaten.
-- =============================================================================

create table if not exists public.sommer2026_signups (
  id            bigint generated always as identity primary key,
  created_at    timestamptz not null default now(),
  signed_up_at  timestamptz not null,                 -- Zeitpunkt der Anmeldung (Momentum, Kohorten)
  produkt       text not null check (produkt in ('wos','gtv')),
  sprache       text not null check (sprache in ('de','en')),
  format        text not null check (format  in ('papier','digital','stream')),   -- WoS: papier/digital · GTV: stream
  tarif         text not null check (tarif   in ('standard','ermaessigt')),
  intervall     text not null check (intervall in ('monatlich','jaehrlich')),
  waehrung      text check (waehrung in ('eur','chf')),  -- Zahlungswährung (für Umsatz)
  status        text not null default 'neu'    check (status in ('neu','bleibt','gekuendigt','laeuft-aus')),
  kanal         text not null default 'andere' check (kanal in ('newsletter','mailer','social','popup','website','empfehlung','andere')),  -- Herkunftsweg (Attribution)
  source        text not null default 'manual' check (source in ('uscreen','zoho','paperform','manual')),
  ext_id        text,                                 -- Fremd-ID der Quelle (z. B. user_id/submission_id)
  dedup_key     text,                                 -- Entdopplung: <produkt>:<E-Mail-Hash> bzw. <source>:<ext_id>
  -- Attribution (Wirkungskette): volles UTM-Tupel + Landingpage + offene Selbstauskunft.
  kampagne      text default 'summer26_trial',        -- Kampagnen-ID (eine Aktion, eine Kennung)
  utm_source    text,                                 -- z. B. instagram / newsletter / google
  utm_medium    text,                                 -- z. B. social / email / organic
  utm_campaign  text,                                 -- i. d. R. = kampagne
  utm_content   text,                                 -- konkretes Motiv (z. B. reel_ernst_zuercher)
  landing_path  text,                                 -- Pfad der genutzten Landingpage
  selbstauskunft text                                 -- «Wie aufmerksam geworden?», E-Mail-redigiert (O-Ton)
);
-- Entdopplung strikt über dedup_key (Person je Produkt, auch über Quellen hinweg)
create unique index if not exists sommer2026_signups_dedup_uk on public.sommer2026_signups (dedup_key);

comment on table public.sommer2026_signups is
  'Sommer-Aktion 2026: eine Zeile je Anmeldung im Gratis-Zeitraum. status = Bleibe-Zustand nach 3 Monaten. Nur Aggregate verlassen die DB (RPCs).';

create index if not exists sommer2026_signups_day_idx on public.sommer2026_signups (signed_up_at);

alter table public.sommer2026_signups enable row level security;
-- Bewusst KEINE anon-Policy: RLS an + keine Policy = Rohzeilen zu.
revoke all on table public.sommer2026_signups from anon, authenticated;

-- 1) Breakdown je Dimension (Ströme, Tarife, Bleibe-Zustand, Zahlungswährung)
-- (Migration «sommer2026_stats_waehrung»: waehrung ergänzt, damit der
-- Folgejahr-Umsatz je Zahlungswährung zum echten Preis rechnet; gtv-Zeilen
-- ohne Angabe wurden auf 'eur' nachgezogen – der Uscreen-Store rechnet in EUR.)
create or replace function public.sommer2026_stats()
returns table(produkt text, sprache text, format text, tarif text, intervall text, status text, waehrung text, n bigint)
language sql security definer set search_path to 'public' as $$
  select produkt, sprache, format, tarif, intervall, status, waehrung, count(*)::bigint as n
    from public.sommer2026_signups
   group by produkt, sprache, format, tarif, intervall, status, waehrung;
$$;

-- 2) Momentum: Anmeldungen je Tag und Produkt
create or replace function public.sommer2026_timeline()
returns table(day date, produkt text, n bigint)
language sql security definer set search_path to 'public' as $$
  select signed_up_at::date as day, produkt, count(*)::bigint as n
    from public.sommer2026_signups
   group by signed_up_at::date, produkt
   order by day;
$$;

-- 3) Der 3-Monats-Moment: Kohorten und ihr Entscheidungsdatum
create or replace function public.sommer2026_kohorten()
returns table(kohorte date, neu bigint, bleibt bigint, gekuendigt bigint, offen bigint, entscheidung_ab date)
language sql security definer set search_path to 'public' as $$
  select date_trunc('month', signed_up_at)::date                        as kohorte,
         count(*)::bigint                                                as neu,
         count(*) filter (where status = 'bleibt')::bigint              as bleibt,
         count(*) filter (where status = 'gekuendigt')::bigint          as gekuendigt,
         count(*) filter (where status in ('neu','laeuft-aus'))::bigint  as offen,
         (date_trunc('month', signed_up_at) + interval '3 months')::date as entscheidung_ab
    from public.sommer2026_signups
   group by date_trunc('month', signed_up_at)
   order by kohorte;
$$;

-- 4) Attribution: Anmeldungen je Herkunftsweg
create or replace function public.sommer2026_kanaele()
returns table(kanal text, n bigint)
language sql security definer set search_path to 'public' as $$
  select kanal, count(*)::bigint as n
    from public.sommer2026_signups
   group by kanal
   order by n desc;
$$;

grant execute on function public.sommer2026_stats()    to anon, authenticated;
grant execute on function public.sommer2026_timeline() to anon, authenticated;
grant execute on function public.sommer2026_kohorten() to anon, authenticated;
grant execute on function public.sommer2026_kanaele()  to anon, authenticated;

-- =============================================================================
-- Wirkungskette: Massnahmen-Protokoll + feinere Attribution + Trichter
-- (Migration «sommer2026_attribution_und_massnahmen»)
-- =============================================================================

-- Massnahmen-Protokoll: eine Zeile je Kampagnen-Massnahme (Newsletter, Inserat, Post …).
-- Freitext (beobachtung/entscheidung) bleibt INTERN – nicht im öffentlichen RPC.
create table if not exists public.sommer2026_massnahmen (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  tag         date not null,                              -- Datum der Massnahme
  massnahme   text not null,                              -- z. B. «Auftaktnewsletter»
  kanal       text not null default 'andere' check (kanal in ('newsletter','mailer','flyer','social','popup','website','empfehlung','andere')),
  rolle       text not null default 'wirkung' check (rolle in ('sichtbarkeit','aktivierung','wirkung','bindung')),  -- Hauptaufgabe
  zielgruppe  text,
  botschaft   text,
  code        text,                                       -- Link/UTM/QR-Code der Massnahme
  kosten      numeric,                                    -- Aufwand
  reichweite  bigint,                                     -- Sichtbarkeit (Impressionen)
  klicks      bigint,                                     -- Aktivierung
  ersteller   text,                                       -- Kürzel: wer steht dahinter
  notiz       text,                                        -- ÖFFENTLICH: klärende Präzisierung (z. B. «nur geöffnete Mails»)
  beobachtung text,                                       -- INTERN (nicht im RPC)
  entscheidung text                                       -- INTERN (nicht im RPC)
);
alter table public.sommer2026_massnahmen enable row level security;
revoke all on table public.sommer2026_massnahmen from anon, authenticated;

-- Feinere Attribution (unter dem kanal-Bucket): welches Motiv brachte Anmeldungen?
create or replace function public.sommer2026_attribution()
returns table(kanal text, utm_source text, utm_medium text, utm_campaign text, utm_content text, n bigint)
language sql security definer set search_path to 'public' as $$
  select kanal, utm_source, utm_medium, utm_campaign, utm_content, count(*)::bigint as n
    from public.sommer2026_signups
   group by kanal, utm_source, utm_medium, utm_campaign, utm_content
   order by n desc;
$$;

-- Massnahmen-Protokoll, kuratiert (ohne interne Freitext-Spalten; notiz ist die
-- öffentliche, klärende Präzisierung und darf mit)
drop function if exists public.sommer2026_massnahmen_public();
create or replace function public.sommer2026_massnahmen_public()
returns table(id bigint, tag date, massnahme text, kanal text, rolle text, ersteller text, kosten numeric, reichweite bigint, klicks bigint, notiz text)
language sql security definer set search_path to 'public' as $$
  select id, tag, massnahme, kanal, rolle, ersteller, kosten, reichweite, klicks, notiz
    from public.sommer2026_massnahmen
   order by tag, id;
$$;

-- Massnahme eintragen (Migration «sommer2026_massnahme_eintragen»): offener
-- Schreibweg fürs Team (Muster Link-Register) – nur kuratierte Felder, die
-- internen Freitext-Spalten bleiben der Redaktion. Speist Zeitband, Protokoll
-- und Wirkungskette im Cockpit.
drop function if exists public.sommer2026_massnahme_eintragen(date, text, text, text, text, numeric, bigint, bigint, text);
create or replace function public.sommer2026_massnahme_eintragen(
  p_tag date, p_massnahme text, p_kanal text, p_rolle text,
  p_zielgruppe text, p_kosten numeric, p_reichweite bigint, p_klicks bigint,
  p_ersteller text default null, p_notiz text default null)
returns text language plpgsql security definer set search_path to 'public' as $$
declare
  v_kanal text; v_rolle text;
begin
  if p_tag is null or coalesce(trim(p_massnahme), '') = '' then
    return 'unvollstaendig';
  end if;
  v_kanal := lower(coalesce(p_kanal, ''));
  if v_kanal not in ('newsletter','mailer','flyer','social','popup','website','empfehlung','andere') then v_kanal := 'andere'; end if;
  v_rolle := lower(coalesce(p_rolle, ''));
  if v_rolle not in ('sichtbarkeit','aktivierung','wirkung','bindung') then v_rolle := 'wirkung'; end if;
  insert into public.sommer2026_massnahmen (tag, massnahme, kanal, rolle, zielgruppe, kosten, reichweite, klicks, ersteller, notiz)
  values (p_tag, trim(p_massnahme), v_kanal, v_rolle, nullif(trim(coalesce(p_zielgruppe,'')), ''), p_kosten, p_reichweite, p_klicks,
          nullif(trim(coalesce(p_ersteller,'')), ''), nullif(trim(coalesce(p_notiz,'')), ''));
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_massnahme_eintragen(date, text, text, text, text, numeric, bigint, bigint, text, text) to anon, authenticated;

-- Bearbeiten (Migration «sommer2026_massnahmen_kuerzel_flyer_bearbeiten»):
-- nur übergebene Werte ändern, vorhandene Zahlen bleiben erhalten.
drop function if exists public.sommer2026_massnahme_aendern(bigint, date, text, text, text, text, numeric, bigint, bigint);
create or replace function public.sommer2026_massnahme_aendern(
  p_id bigint, p_tag date, p_massnahme text, p_kanal text, p_rolle text,
  p_ersteller text, p_kosten numeric, p_reichweite bigint, p_klicks bigint,
  p_notiz text default null)
returns text language plpgsql security definer set search_path to 'public' as $$
declare
  v_kanal text; v_rolle text; n int;
begin
  v_kanal := lower(coalesce(p_kanal, ''));
  if v_kanal not in ('newsletter','mailer','flyer','social','popup','website','empfehlung','andere') then v_kanal := null; end if;
  v_rolle := lower(coalesce(p_rolle, ''));
  if v_rolle not in ('sichtbarkeit','aktivierung','wirkung','bindung') then v_rolle := null; end if;
  update public.sommer2026_massnahmen set
    tag        = coalesce(p_tag, tag),
    massnahme  = coalesce(nullif(trim(coalesce(p_massnahme,'')), ''), massnahme),
    kanal      = coalesce(v_kanal, kanal),
    rolle      = coalesce(v_rolle, rolle),
    ersteller  = coalesce(nullif(trim(coalesce(p_ersteller,'')), ''), ersteller),
    kosten     = coalesce(p_kosten, kosten),
    reichweite = coalesce(p_reichweite, reichweite),
    klicks     = coalesce(p_klicks, klicks),
    notiz      = coalesce(nullif(trim(coalesce(p_notiz,'')), ''), notiz)
  where id = p_id;
  get diagnostics n = row_count;
  return case when n > 0 then 'ok' else 'unbekannt' end;
end;
$$;
grant execute on function public.sommer2026_massnahme_aendern(bigint, date, text, text, text, text, numeric, bigint, bigint, text) to anon, authenticated;

-- Kosten-Einzelposten (Migration «sommer2026_kosten_posten»): das Team traegt
-- Posten mit Kuerzel ein, das Cockpit summiert je Kostenart (Uebersicht bleibt,
-- Details klappen auf). Muster wie Massnahmen: Tabelle zu, RPCs offen.
create table if not exists public.sommer2026_kosten (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  tag        date not null,
  posten     text not null,
  kategorie  text not null default 'andere' check (kategorie in ('stunden','social','druck','infrastruktur','andere')),
  betrag     numeric not null check (betrag >= 0),
  ersteller  text
);
alter table public.sommer2026_kosten enable row level security;
revoke all on table public.sommer2026_kosten from anon, authenticated;

create or replace function public.sommer2026_kosten_public()
returns table(id bigint, tag date, posten text, kategorie text, betrag numeric, ersteller text)
language sql security definer set search_path to 'public' as $$
  select id, tag, posten, kategorie, betrag, ersteller
    from public.sommer2026_kosten
   order by tag, id;
$$;
grant execute on function public.sommer2026_kosten_public() to anon, authenticated;

create or replace function public.sommer2026_kosten_eintragen(
  p_tag date, p_posten text, p_kategorie text, p_betrag numeric, p_ersteller text)
returns text language plpgsql security definer set search_path to 'public' as $$
declare v_kat text;
begin
  if p_tag is null or coalesce(trim(p_posten), '') = '' or p_betrag is null or p_betrag < 0 then
    return 'unvollstaendig';
  end if;
  v_kat := lower(coalesce(p_kategorie, ''));
  if v_kat not in ('stunden','social','druck','infrastruktur','andere') then v_kat := 'andere'; end if;
  insert into public.sommer2026_kosten (tag, posten, kategorie, betrag, ersteller)
  values (p_tag, trim(p_posten), v_kat, p_betrag, nullif(trim(coalesce(p_ersteller,'')), ''));
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_kosten_eintragen(date, text, text, numeric, text) to anon, authenticated;

-- Multiplikatoren-Kontaktprotokoll (Migration «sommer2026_multiplikatoren»):
-- wer hat wen wann kontaktiert, mit welchem Ergebnis. Klarnamen liegen in der
-- geschlossenen Tabelle und verlassen die DB NUR über sommer2026_multi_namen
-- (Passwort-Hash «multiplikatoren_pw_hash» in sommer2026_config, Präfix
-- 'goe-multi:'). Rolle, Verlauf und Status sind offen (Beschluss 9.7.2026);
-- darum gilt: keine Klarnamen in rolle_funktion/ergebnis notieren.
create table if not exists public.sommer2026_multiplikatoren (
  id             bigint generated always as identity primary key,
  created_at     timestamptz not null default now(),
  name           text not null,          -- Klarname: nur via Passwort-RPC
  rolle_funktion text,                   -- Rolle/Funktion/Organisation (offen)
  ersteller      text                    -- Kürzel: wer hat angelegt
);
alter table public.sommer2026_multiplikatoren enable row level security;
revoke all on table public.sommer2026_multiplikatoren from anon, authenticated;

create table if not exists public.sommer2026_multi_kontakte (
  id               bigint generated always as identity primary key,
  created_at       timestamptz not null default now(),
  multiplikator_id bigint not null references public.sommer2026_multiplikatoren(id) on delete cascade,
  tag              date not null,
  wer              text not null,        -- Team-Kürzel
  art              text not null default 'andere' check (art in ('anruf','mail','treffen','andere')),
  ergebnis         text,                 -- Freitext, KEINE Klarnamen (offen)
  status           text not null default 'offen' check (status in ('offen','erreicht','zugesagt','abgesagt','spaeter'))
);
alter table public.sommer2026_multi_kontakte enable row level security;
revoke all on table public.sommer2026_multi_kontakte from anon, authenticated;

-- Passwort-Prüfung ist gross/klein- und leerzeichen-unabhängig
-- (Migration «sommer2026_multi_pw_case_insensitive»: lower(trim(...)) vor
-- dem Hash-Vergleich – Handy-Autokorrektur macht sonst aus «pw» ein «Pw»).
-- RPCs: multi_liste() (Alias statt Name), multi_protokoll() (alle Kontakte),
-- multi_namen(p_passwort) (Klarnamen nur bei korrektem Hash),
-- multi_anlegen(name, rolle, ersteller), multi_kontakt_anlegen(...).
-- Volltext siehe Migration «sommer2026_multiplikatoren».

-- Wirkungstrichter: Sichtbarkeit → Aktivierung → Wirkung → Bindung
-- (Migration «sommer2026_trichter_kurzlink_klicks»: die Stufe «Klicks» =
-- von Hand erfasste Aktivitäts-Klicks PLUS die automatisch gezählten
-- Kurzlink-Klicks der Kampagnen-Links aus link_hits. Doppelzählung möglich,
-- wenn dieselben Klicks zusätzlich von Hand erfasst werden – die Fussnote
-- im Cockpit weist die Zusammensetzung aus.)
create or replace function public.sommer2026_trichter()
returns table(stufe text, wert bigint, ord int)
language sql security definer set search_path to 'public' as $$
  select * from (
    select 'sichtbarkeit'::text as stufe, coalesce(sum(reichweite),0)::bigint as wert, 1 as ord from public.sommer2026_massnahmen
    union all
    select 'aktivierung',
           (select coalesce(sum(klicks),0) from public.sommer2026_massnahmen)::bigint
         + (select count(*) from public.link_hits h join public.sommer2026_links l on l.code = h.code)::bigint,
           2
    union all
    select 'wirkung', count(*)::bigint, 3 from public.sommer2026_signups
    union all
    select 'bindung', count(*) filter (where status = 'bleibt')::bigint, 4 from public.sommer2026_signups
  ) t
  order by t.ord;
$$;

grant execute on function public.sommer2026_attribution()       to anon, authenticated;
grant execute on function public.sommer2026_massnahmen_public() to anon, authenticated;
grant execute on function public.sommer2026_trichter()          to anon, authenticated;

-- Ereignis-Protokoll (Migration «sommer2026_ereignisse», erweitert um
-- «sommer2026_ereignisse_vermutung»): die einzelnen Anmeldungen der letzten
-- 14 Tage fürs Cockpit («Was ist heute passiert?») – stundengenau gerundet
-- (keine Minuten-Fingerprints), ohne jede Personenspalte. Für Anmeldungen
-- OHNE UTM-Spur wird zusätzlich die «vermutete Herkunft» mitgeliefert: der
-- zeitlich nächste Kurzlink-Klick auf einen zum Produkt passenden Link
-- innerhalb von 90 Minuten davor. Indiz, keine Messung – die harte
-- Attribution (kanal/utm_*) bleibt unberührt.
create or replace function public.sommer2026_ereignisse()
returns table(stunde timestamptz, produkt text, sprache text, format text, tarif text, intervall text,
              kanal text, utm_source text, utm_medium text, utm_content text, landing_path text, source text,
              vermutet_source text, vermutet_content text, vermutet_code text, vermutet_min int)
language sql security definer set search_path to 'public' as $$
  select date_trunc('hour', s.signed_up_at) as stunde, s.produkt, s.sprache, s.format, s.tarif, s.intervall,
         s.kanal, s.utm_source, s.utm_medium, s.utm_content, s.landing_path, s.source,
         v.utm_source, v.utm_content, v.code, v.minuten
    from public.sommer2026_signups s
    left join lateral (
      select l.utm_source, l.utm_content, l.code,
             (extract(epoch from (s.signed_up_at - h.ts)) / 60)::int as minuten
        from public.link_hits h
        join public.sommer2026_links l on l.code = h.code
       where s.utm_source is null and s.utm_content is null
         and h.ts between s.signed_up_at - interval '90 minutes' and s.signed_up_at
         and ((s.produkt = 'gtv' and l.landing in ('tv','gtv','uebersicht'))
           or (s.produkt = 'wos' and l.landing in ('wos','uebersicht')))
       order by h.ts desc
       limit 1
    ) v on true
   where s.signed_up_at >= now() - interval '14 days'
   order by s.signed_up_at desc
   limit 400;
$$;
grant execute on function public.sommer2026_ereignisse() to anon, authenticated;

-- =============================================================================
-- Link-Register (Migration «sommer2026_links_register»)
-- Erzeugte UTM-Links (aus apps/utm-generator/) sammeln → Soll/Ist im Cockpit.
-- Anon darf nur anlegen (Generator, Publishable-Key), Lesen nur über RPC.
-- =============================================================================
create table if not exists public.sommer2026_links (
  id           bigint generated always as identity primary key,
  created_at   timestamptz not null default now(),
  kampagne     text not null default 'summer26_trial',
  utm_source   text not null,
  utm_medium   text not null,
  utm_campaign text not null default 'summer26_trial',
  utm_content  text,
  landing      text,          -- Angebot der Landingpage (uebersicht/wos/tv)
  sprache      text,          -- Sprache der Landingpage (de/en)
  url          text not null, -- fertiger Link
  code         text,          -- Kurzcode für die Weiterleitung (Function go)
  rolle        text,          -- Hauptaufgabe (sichtbarkeit/aktivierung/wirkung/bindung)
  ersteller    text           -- optionales Kürzel, kein Pflichtfeld
);
create unique index if not exists sommer2026_links_url_uk  on public.sommer2026_links (url);
create unique index if not exists sommer2026_links_code_uk on public.sommer2026_links (code);
alter table public.sommer2026_links enable row level security;
revoke all on table public.sommer2026_links from anon, authenticated;
-- Schreiben über die RPCs unten (kein direktes anon-INSERT auf die Tabelle).

-- Soll/Ist: je registriertem Link die Zahl der Anmeldungen über genau dieses
-- UTM-Tupel – plus die Kurzlink-Klicks (Migration «sommer2026_links_klicks_sichtbar»:
-- die Function go zählt jeden /s/<code>-Aufruf in link_hits; hier wird die Zählung
-- je Link sichtbar). Nur Links MIT Kurzcode haben eine Klick-Zählung.
create or replace function public.sommer2026_links_public()
returns table(created_at timestamptz, utm_source text, utm_medium text, utm_content text,
              landing text, sprache text, url text, code text, rolle text, ersteller text,
              abschluesse bigint, klicks bigint, letzter_klick timestamptz)
language sql security definer set search_path to 'public' as $$
  select l.created_at, l.utm_source, l.utm_medium, l.utm_content, l.landing, l.sprache, l.url, l.code, l.rolle, l.ersteller,
         count(distinct s.id)::bigint as abschluesse,
         count(distinct h.id)::bigint as klicks,
         max(h.ts) as letzter_klick
    from public.sommer2026_links l
    left join public.sommer2026_signups s
      on  s.utm_campaign is not distinct from l.utm_campaign
      and s.utm_source   is not distinct from l.utm_source
      and s.utm_medium   is not distinct from l.utm_medium
      and s.utm_content  is not distinct from l.utm_content
    left join public.link_hits h on l.code is not null and h.code = l.code
   group by l.id, l.created_at, l.utm_source, l.utm_medium, l.utm_content, l.landing, l.sprache, l.url, l.code, l.rolle, l.ersteller
   order by abschluesse desc, l.created_at desc;
$$;
grant execute on function public.sommer2026_links_public() to anon, authenticated;

-- Sprache fürs Produkt gtv aus dem Link-Register (Migration
-- «sommer2026_sprache_aus_register_trigger», Beschluss 18.7.2026): die
-- Uscreen-Plan-Titel sind durchweg deutsch, der Titel-Rat der Ingestion ergäbe
-- immer 'de'. Trägt das UTM-Tupel im Register eindeutig EINE Sprache, setzt
-- der Trigger sie beim Schreiben; mehrdeutige Tupel und Anmeldungen ohne Spur
-- bleiben unangetastet. Netz und doppelter Boden zur gleichen Logik in
-- ingest-uscreen (spracheAusRegister) - beide setzen denselben Wert.
create or replace function public.sommer2026_sprache_aus_register()
returns trigger language plpgsql security definer set search_path to 'public' as $$
declare
  v_sprache text;
begin
  if new.produkt = 'gtv' and (new.utm_source is not null or new.utm_content is not null) then
    select min(l.sprache) into v_sprache
      from public.sommer2026_links l
     where l.utm_campaign is not distinct from new.utm_campaign
       and l.utm_source   is not distinct from new.utm_source
       and l.utm_medium   is not distinct from new.utm_medium
       and l.utm_content  is not distinct from new.utm_content
       and l.sprache is not null
    having count(distinct l.sprache) = 1;
    if v_sprache is not null then
      new.sprache := v_sprache;
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists sommer2026_signups_sprache on public.sommer2026_signups;
create trigger sommer2026_signups_sprache
before insert or update of utm_source, utm_medium, utm_campaign, utm_content
on public.sommer2026_signups
for each row execute function public.sommer2026_sprache_aus_register();

-- Kurzlink-Weiterleitung: Edge Function `go` liest sommer2026_links.code (Service-Role)
-- und leitet per 302 auf die volle UTM-URL. Siehe go/index.ts.

-- Anlegen per RPC: meldet 'ok' | 'vergeben' (unique) | 'unvollstaendig'
-- als Text an den Generator. Der einst eingeführte Team-Schlüssel wurde am
-- 6.7.2026 wieder entfernt (Migration «sommer2026_links_schluessel_entfernen»);
-- p_schluessel bleibt aus Kompatibilität in der Signatur und wird ignoriert.
create or replace function public.sommer2026_link_anlegen(
  p_schluessel text, p_source text, p_medium text, p_content text,
  p_landing text, p_sprache text, p_url text, p_code text,
  p_rolle text, p_ersteller text)
returns text language plpgsql security definer set search_path to 'public' as $$
begin
  if coalesce(p_source, '') = '' or coalesce(p_medium, '') = '' or coalesce(p_url, '') = '' then
    return 'unvollstaendig';
  end if;
  begin
    insert into public.sommer2026_links
      (kampagne, utm_source, utm_medium, utm_campaign, utm_content,
       landing, sprache, url, code, rolle, ersteller)
    values
      ('summer26_trial', p_source, p_medium, 'summer26_trial', nullif(p_content, ''),
       nullif(p_landing, ''), nullif(p_sprache, ''), p_url, nullif(p_code, ''),
       nullif(p_rolle, ''), nullif(p_ersteller, ''));
  exception when unique_violation then
    return 'vergeben';
  end;
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_link_anlegen(text, text, text, text, text, text, text, text, text, text) to anon, authenticated;

-- Kontrolliertes Löschen (per URL, nur RPC – p_schluessel wird ignoriert).
create or replace function public.sommer2026_link_loeschen(p_url text, p_schluessel text)
returns text language plpgsql security definer set search_path to 'public' as $$
begin
  delete from public.sommer2026_links where url = p_url and kampagne = 'summer26_trial';
  return 'ok';
end;
$$;
grant execute on function public.sommer2026_link_loeschen(text, text) to anon, authenticated;

-- =============================================================================
-- Ingestion (Webhooks) – siehe ingest-uscreen/index.ts
-- =============================================================================

-- Roh-Log jedes eingehenden Webhooks (PII-redigiert), nur Service-Role liest ihn
create table if not exists public.sommer2026_ingest_raw (
  id          bigint generated always as identity primary key,
  received_at timestamptz not null default now(),
  source      text not null default 'uscreen',
  event       text,
  ok          boolean not null default true,
  note        text,
  payload     jsonb
);
alter table public.sommer2026_ingest_raw enable row level security;
revoke all on table public.sommer2026_ingest_raw from anon, authenticated;

-- Konfig-Speicher (u. a. webhook_secret) – nur Service-Role
create table if not exists public.sommer2026_config (
  key   text primary key,
  value text not null
);
alter table public.sommer2026_config enable row level security;
revoke all on table public.sommer2026_config from anon, authenticated;
-- Schlüssel in sommer2026_config:
--   webhook_secret : Secret für ?key= der Ingestion-Functions
--   hash_salt      : Salt für den E-Mail-Hash (Entdopplung)
--   aktion_aktiv   : 'true' = zählen, sonst nur loggen
--   aktion_start   : Zeitgrenze (Anmeldungen davor zählen nicht), z. B.
--                    '2026-07-03T12:00:00+02:00'
--   aktion_coupon  : optional – Aktions-Coupon-Code (statt Trial-Heuristik)
--   aktion_plan    : optional – Aktions-Plan-Titel (statt Trial-Heuristik)
