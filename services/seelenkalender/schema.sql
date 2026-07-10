-- =============================================================================
-- Seelenkalender · Versand-Strecke (Lead-Schleife 1B) — Schema
-- Konzept: docs/marketing-maschine.md §6 · Spec: docs/specs/lead-maschine.md
-- Grundsätze: Double-Opt-in, Ein-Klick-Abmeldung, Zweckbindung. Die E-Mail-
-- Adresse wird NUR für den Versand gehalten (ohne sie gibt es keinen Brief);
-- Auswertung läuft ausschliesslich über Summen. Secrets entstehen serverseitig
-- (gen_random_bytes) und stehen nie im Repo. Resend-API-Key wird NACH dem
-- Einrichten des Resend-Kontos per SQL-Editor in seelenkalender_config gesetzt.
-- =============================================================================

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Konfiguration (nur Service-Role; RLS ohne Policies)
create table if not exists public.seelenkalender_config (
  key   text primary key,
  value text not null default ''
);
alter table public.seelenkalender_config enable row level security;

insert into public.seelenkalender_config (key, value) values
  ('versand_key',    encode(extensions.gen_random_bytes(24), 'hex')),
  ('hash_salt',      encode(extensions.gen_random_bytes(16), 'hex')),
  ('resend_api_key', ''),  -- per SQL-Editor setzen, nie ins Repo
  ('absender',       'Seelenkalender – Das Goetheanum <onboarding@resend.dev>'),
  ('seite_url',      'https://werkzeuge.goetheanum.ch/apps/seelenkalender/')
on conflict (key) do nothing;

-- Die 52 Wochensprüche (gemeinfrei; Quelle anthro.world, abgerufen 8.7.2026)
create table if not exists public.seelenkalender_sprueche (
  nr        int primary key check (nr between 1 and 52),
  vers      text not null,
  stimmung  text
);
alter table public.seelenkalender_sprueche enable row level security;
drop policy if exists "sprueche_lesen" on public.seelenkalender_sprueche;
create policy "sprueche_lesen" on public.seelenkalender_sprueche
  for select using (true);

insert into public.seelenkalender_sprueche (nr, vers, stimmung) values
(1, $vers$Wenn aus den Weltenweiten
Die Sonne spricht zum Menschensinn
Und Freude aus den Seelentiefen
Dem Licht sich eint im Schauen,
Dann ziehen aus der Selbstheit Hülle
Gedanken in die Raumesfernen
Und binden dumpf
Des Menschen Wesen an des Geistes Sein.$vers$, 'Oster-Stimmung'),
(2, $vers$Ins Äußere des Sinnesalls
Verliert Gedankenmacht ihr Eigensein;
Es finden Geisteswelten
Den Menschensprossen wieder,
Der seinen Keim in ihnen,
Doch seine Seelenfrucht
In sich muss finden.$vers$, null),
(3, $vers$Es spricht zum Weltenall,
Sich selbst vergessend
Und seines Urstands eingedenk,
Des Menschen wachsend Ich:
In dir, befreiend mich
Aus meiner Eigenheiten Fessel,
Ergründe ich mein echtes Wesen.$vers$, null),
(4, $vers$Ich fühle Wesen meines Wesens:
So spricht Empfindung,
Die in der sonnerhellten Welt
Mit Lichtesfluten sich vereint;
Sie will dem Denken
Zur Klarheit Wärme schenken
Und Mensch und Welt in Einheit fest verbinden.$vers$, null),
(5, $vers$Im Lichte das aus Geistestiefen
Im Raume fruchtbar webend
Der Götter Schaffen offenbart:
In ihm erscheint der Seele Wesen
Geweitet zu dem Weltensein
Und auferstanden
Aus enger Selbstheit Innenmacht.$vers$, null),
(6, $vers$Es ist erstanden aus der Eigenheit
Mein Selbst und findet sich
Als Weltenoffenbarung
In Zeit- und Raumeskräften;
Die Welt, sie zeigt mir überall
Als göttlich Urbild
Des eignen Abbilds Wahrheit.$vers$, null),
(7, $vers$Mein Selbst, es drohet zu entfliehen,
Vom Weltenlichte mächtig angezogen;
Nun trete du mein Ahnen
In deine Rechte kräftig ein,
Ersetze mir des Denkens Macht,
Das in der Sinne Schein
Sich selbst verlieren will.$vers$, null),
(8, $vers$Es wächst der Sinne Macht
Im Bunde mit der Götter Schaffen,
Sie drückt des Denkens Kraft
Zur Traumes Dumpfheit mir herab.
Wenn göttlich Wesen
Sich meiner Seele einen will,
Muss menschlich Denken
Im Traumessein sich still bescheiden.$vers$, null),
(9, $vers$Vergessend meine Willenseigenheit
Erfüllet Weltenwärme sommerkündend
Mir Geist und Seelenwesen;
Im Licht mich zu verlieren
Gebietet mir das Geistesschauen,
Und kraftvoll kündet Ahnung mir:
Verliere dich, um dich zu finden.$vers$, null),
(10, $vers$Zu sommerlichen Höhen
Erhebt der Sonne leuchtend Wesen sich,
Es nimmt mein menschlich Fühlen
In seine Raumesweiten mit,
Erahnend regt im Inneren sich
Empfindung, dumpf mir kündend,
Erkennen wirst du einst:
Dich fühlte jetzt ein Gotteswesen.$vers$, null),
(11, $vers$Es ist in dieser Sonnenstunde
An dir, die weise Kunde zu erkennen:
An Weltenschönheit hingegeben,
In dir dich fühlend zu durchleben:
Verlieren kann das Menschen-Ich
Und finden sich im Welten-Ich.$vers$, null),
(12, $vers$Der Welten Schönheitsglanz
Er zwinget mich aus Seelentiefen
Des Eigenlebens Götterkräfte
Zum Weltenfluge zu entbinden;
Mich selber zu verlassen,
Vertrauend nur mich suchend
In Weltenlicht und Weltenwärme.$vers$, 'Johanni-Stimmung'),
(13, $vers$Und bin ich in den Sinneshöhen,
So flammt in meinen Seelentiefen
Aus Geistes Feuerwelten
Der Götter Wahrheitswort:
In Geistesgründen suche ahnend
Dich geistverwandt zu finden.$vers$, null),
(14, $vers$An Sinnesoffenbarung hingegeben
Verlor ich Eigenwesens Trieb,
Gedankentraum, er schien
Betäubend mir das Selbst zu rauben,
Doch weckend nahet schon
Im Sinnenschein mir Weltendenken.$vers$, null),
(15, $vers$Ich fühle wie verzaubert
im Weltenschein des Geistes Weben,
Es hat in Sinnesdumpfheit
Gehüllt mein Eigenwesen,
Zu schenken mir die Kraft,
Die ohnmächtig sich selbst zu geben
Mein Ich in seinen Schranken ist.$vers$, null),
(16, $vers$Zu bergen Geistgeschenk im Innern
Gebietet Strenge mir mein Ahnen,
Dass reifend Gottesgaben
In Seelengründen fruchtend
Der Selbstheit Früchte bringen.$vers$, null),
(17, $vers$Es spricht das Weltenwort,
Das ich durch Sinnestore
In Seelengründe durfte führen:
Erfülle deine Geistestiefen
Mit meinen Weltenweiten
Zu finden einstens mich in dir.$vers$, null),
(18, $vers$Kann ich die Seele weiten,
Dass sie sich selbst verbindet
Empfangenem Welten-Keimesworte?
Ich ahne, dass ich Kraft muss finden
Die Seele würdig zu gestalten,
Zum Geisteskleide sich zu bilden.$vers$, null),
(19, $vers$Geheimnisvoll das Neu-Empfang’ne
Mit der Erinn’rung zu umschließen,
Sei meines Strebens weitrer Sinn:
Es soll erstarkend Eigenkräfte
In meinem Innern wecken
Und werdend mich mir selber geben.$vers$, null),
(20, $vers$So fühl’ ich erst mein Sein,
Das fern vom Welten-Dasein
In sich, sich selbst erlöschen
Und bauend nur auf eignem Grunde
In sich, sich selbst ertöten müsste.$vers$, null),
(21, $vers$Ich fühle fruchtend fremde Macht
Sich stärkend mir mich selbst verleihn,
Den Keim empfind ich reifend
Und Ahnung lichtvoll weben
Im Innern an der Selbstheit Macht.$vers$, null),
(22, $vers$Das Licht aus Weltenweiten,
Im Innern lebt es kräftig fort,
Es wird zum Seelenlichte
Und leuchtet in die Geistestiefen,
U m Früchte zu entbinden,
Die Menschenselbst aus Weltenselbst
Im Zeitenlaufe reifen lassen.$vers$, null),
(23, $vers$Es dämpfet herbstlich sich
Der Sinne Reizesstreben,
In Lichtesoffenbarung mischen
Der Nebel dumpfe Schleier sich,
Ich selber schau in Raumesweiten
Des Herbstes Weltenschlaf,
Der Sommer hat an mich
Sich selber hingegeben.$vers$, null),
(24, $vers$Sich selbst erschaffend stets
Wird Seelensein sich selbst gewahr;
Der Weltengeist, er strebet fort
In Selbsterkenntnis neu belebt
Und schafft aus Seelenfinsternis
Des Selbstsinns Willensfrucht.$vers$, null),
(25, $vers$Ich darf nun mir gehören
Und leuchtend breiten Innenlicht
In Raumes- und in Zeitenfinsternis.
Zum Schlafe drängt natürlich Wesen,
Der Seele Tiefen sollen wachen
Und wachend tragen Sonnengluten
In kalte Winterfluten.$vers$, null),
(26, $vers$Natur, dein mütterliches Sein,
Ich trage es in meinem Willenswesen;
Und meines Willens Feuermacht,
Sie stählet meines Geistes Triebe,
Dass sie gebären Selbstgefühl,
Zu tragen mich in mir.$vers$, 'Michaeli-Stimmung'),
(27, $vers$In meines Wesens Tiefen dringen
Erregt ein ahnungsvolles Sehnen,
Dass ich mich selbstbetrachtend finde
Als Sommersonnengabe, die als Keim
In Herbstesstimmung wärmend lebt
Als meiner Seele Kräftetrieb.$vers$, null),
(28, $vers$Ich kann im Innern neu belebt
Erfühlen eignen Wesens Weiten
Und krafterfüllt Gedankenstrahlen
Aus Seelensonnenmacht
Den Lebensrätseln lösend spenden,
Erfüllung manchem Wunsche leihen,
Dem Hoffnung schon die Schwingen lähmte.$vers$, null),
(29, $vers$Sich selbst des Denkens Leuchten
Im Innern kraftvoll zu entfachen,
Erlebtes sinnvoll deutend
Aus Weltengeistes Kräftequell,
Ist mir nun Sommererbe
Ist Herbstesruhe und auch Winterhoffnung.$vers$, null),
(30, $vers$Es sprießen mir im Seelensonnenlicht
Des Denkens reife Früchte,
In Selbstbewußtseins Sicherheit
Verwandelt alles Fühlen sich,
Empfinden kann ich freudevoll
Des Herbstes Geisterwachen,
Der Winter wird in mir
Den Seelensommer wecken.$vers$, null),
(31, $vers$Das Licht aus Geistestiefen,
Nach außen strebt es sonnenhaft,
Es wird zur Lebenswillenskraft
Und leuchtet in der Sinne Dumpfheit,
Um Kräfte zu entbinden,
Die Schaffensmächte aus Seelentrieben
Im Menschenwerke reifen lassen.$vers$, null),
(32, $vers$Ich fühle fruchtend eigne Kraft
Sich stärkend mich der Welt verleihn,
Mein Eigenwesen fühl ich kraftend
Zur Klarheit sich zu wenden
Im Lebens-Schicksalsweben.$vers$, null),
(33, $vers$So fühl’ ich erst die Welt,
Die außer meiner Seele Miterleben
An sich nur frostig leeres Leben
Und ohne Macht sich offenbarend
In Seelen sich von neuem schaffend
In sich den Tod nur finden könnte.$vers$, null),
(34, $vers$Geheimnisvoll das Alt-Bewahrte
Mit neu erstandnem Eigensein
Im Innern sich belebend fühlen:
Es soll erweckend Weltenkräfte
In meines Lebens Außenwerk ergießen
Und werdend mich ins Dasein prägen.$vers$, null),
(35, $vers$Kann ich das Sein erkennen,
Dass es sich wiederfindet
Im Seelen-Schaffens-Drange?
Ich fühle, dass mir Macht verlieh’n
Das eigne Selbst dem Weltenselbst
Als Glied bescheiden einzuleben.$vers$, null),
(36, $vers$In meines Wesens Tiefen spricht
Zur Offenbarung drängend
Geheimnisvoll das Weltenwort:
Erfülle deiner Arbeit Ziele
Mit meinem Geisteslichte
Zu opfern dich durch mich.$vers$, null),
(37, $vers$Zu tragen Geisteslicht in Weltenwinternacht
Erstrebet selig meines Herzens Trieb,
Dass leuchtend Seelenkeime
In Weltengründen wurzeln
Und Gotteswort im Sinnesdunkel
Verklärend alles Sein durchtönt.$vers$, null),
(38, $vers$Ich fühle wie entzaubert
Das Geisteskind im Seelenschoß,
Es hat in Herzenshelligkeit
Gezeugt das heil’ge Weltenwort
Der Hoffnung Himmelsfrucht,
Die jubelnd wächst in Weltenfernen
Aus meines Wesens Gottesgrund.$vers$, 'Weihnacht-Stimmung'),
(39, $vers$An Geistesoffenbarung hingegeben
Gewinne ich des Weltenwesens Licht,
Gedankenkraft, sie wächst
Sich klärend mir mich selbst zu geben
Und weckend löst sich mir
Aus Denkermacht das Selbstgefühl.$vers$, null),
(40, $vers$Und bin ich in den Geistestiefen,
Erfüllt in meinen Seelengründen
Aus Herzens Liebewelten
Der Eigenheiten leerer Wahn
Sich mit des Weltenwortes Feuerkraft.$vers$, null),
(41, $vers$Der Seele Schaffensmacht
Sie strebet aus dem Herzensgrunde
Im Menschenleben Götterkräfte
Zu rechtem Wirken zu entflammen,
Sich selber zu gestalten
In Menschenliebe und im Menschenwerke.$vers$, null),
(42, $vers$Es ist in diesem Winterdunkel
Die Offenbarung eigner Kraft
Der Seele starker Trieb,
In Finsternisse sie zu lenken
Und ahnend vorzufühlen
Durch Herzenswärme Sinnesoffenbarung.$vers$, null),
(43, $vers$In winterlichen Tiefen
Erwärmt des Geistes wahres Sein,
Es gibt dem Weltenscheine
Durch Herzenskräfte Daseinsmächte;
Der Weltenkälte trotzt erstarkend
Das Seelenfeuer im Menscheninnern.$vers$, null),
(44, $vers$Ergreifend neue Sinnesreize
Erfüllet Seelenklarheit,
Eingedenk vollzogner Geistgeburt,
Verwirrend sprossend Weltenwerden
Mit meines Denkens Schöpferwillen.$vers$, null),
(45, $vers$Es festigt sich Gedankenmacht
Im Bunde mit der Geistgeburt,
Sie hellt der Sinne dumpfe Reize
Zur vollen Klarheit auf.
Wenn Seelenfülle
Sich mit dem Weltenwerden einen will,
Muss Sinnesoffenbarung
Des Denkens Licht empfangen.$vers$, null),
(46, $vers$Die Welt, sie drohet zu betäuben
Der Seele eingeborne Kraft;
Nun trete du, Erinnerung,
Aus Geistestiefen leuchtend auf
Und stärke mir das Schauen,
Das nur durch Willenskräfte
Sich selbst erhalten kann.$vers$, null),
(47, $vers$Es will erstehen aus dem Weltenschoße,
Den Sinnenschein erquickend, Werdelust,
Sie finde meines Denkens Kraft
Gerüstet durch die Gotteskräfte
Die kräftig mir im Innern leben.$vers$, null),
(48, $vers$Im Lichte das aus Weltenhöhen
Der Seele machtvoll fließen will
Erscheine, lösend Seelenrätsel,
Des Weltendenkens Sicherheit
Versammelnd seiner Strahlen Macht
Im Menschenherzen Liebe weckend.$vers$, null),
(49, $vers$Ich fühle Kraft des Weltenseins:
So spricht Gedankenklarheit,
Gedenkend eignen Geistes Wachsen
In finstern Weltennächten
Und neigt dem nahen Weltentage
Des Innern Hoffnungsstrahlen.$vers$, null),
(50, $vers$Es spricht zum Menschen-Ich,
Sich machtvoll offenbarend
Und seines Wesens Kräfte lösend,
Des Weltendaseins Werdelust:
In dich mein Leben tragend
Aus seinem Zauberbanne
Erreiche ich mein wahres Ziel.$vers$, null),
(51, $vers$Ins Innre des Menschenwesens
Ergießt der Sinne Reichtum sich,
Es findet sich der Weltengeist
Im Spiegelbild des Menschenauges,
Das seine Kraft aus ihm
Sich neu erschaffen muss.$vers$, null),
(52, $vers$Wenn aus den Seelentiefen
Der Geist sich wendet zu dem Weltensein
Und Schönheit quillt aus Raumesweiten,
Dann zieht aus Himmelsfernen
Des Lebens Kraft in Menschenleiber
Und einet, machtvoll wirkend,
Des Geistes Wesen mit dem Menschensein.$vers$, null)
on conflict (nr) do update set vers=excluded.vers, stimmung=excluded.stimmung;

-- Abonnenten (nur Service-Role; RLS ohne Policies)
create table if not exists public.seelenkalender_abo (
  id            bigint generated always as identity primary key,
  email         text not null,
  email_hash    text not null unique,      -- sha256(salt+email), Entdopplung
  sprache       text not null default 'de',
  status        text not null default 'angemeldet'
                check (status in ('angemeldet','aktiv','beendet')),
  token         text not null unique,      -- Bestätigen/Abmelden
  herkunft      jsonb,                     -- UTM-Tupel der Anmeldung
  angemeldet_am timestamptz not null default now(),
  bestaetigt_am timestamptz,
  beendet_am    timestamptz
);
alter table public.seelenkalender_abo enable row level security;

-- Versand-Protokoll (eine Zeile je Woche; verhindert Doppel-Versand)
create table if not exists public.seelenkalender_versand (
  id           bigint generated always as identity primary key,
  jahr         int not null,
  woche        int not null check (woche between 1 and 52),
  empfaenger   int not null default 0,
  fehler       int not null default 0,
  gesendet_am  timestamptz not null default now(),
  unique (jahr, woche)
);
alter table public.seelenkalender_versand enable row level security;

-- Öffentliche Kennzahl (nur Summen verlassen die Datenbank)
create or replace function public.seelenkalender_stats()
returns table (aktiv bigint, angemeldet bigint, beendet bigint)
language sql security definer set search_path = public as $fn$
  select
    count(*) filter (where status = 'aktiv'),
    count(*) filter (where status = 'angemeldet'),
    count(*) filter (where status = 'beendet')
  from public.seelenkalender_abo
$fn$;
grant execute on function public.seelenkalender_stats() to anon;

-- Wöchentlicher Versand: Montag 05:07 UTC (bewusst neben der vollen Stunde).
-- Der Schlüssel wird erst zur Laufzeit aus der Config gelesen.
select cron.unschedule('seelenkalender-versand')
where exists (select 1 from cron.job where jobname = 'seelenkalender-versand');
select cron.schedule(
  'seelenkalender-versand',
  '7 5 * * 1',
  $cron$
  select net.http_post(
    url := 'https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/seelenkalender?aktion=versand&key='
           || (select value from public.seelenkalender_config where key = 'versand_key'),
    body := '{}'::jsonb
  )
  $cron$
);
