# Kampagnen-Drehbuch — Mailing-Kampagnen nach dem Muster Sommer 2026

Destillat der Sommer-Aktion 2026 (Juli 2026): Was sich bewährt hat, in der
Reihenfolge, in der es beim nächsten Mal geschehen soll. Die Fabrik
(`services/mailing-sommer2026/build_editor.py` + Editor) ist wiederverwendbar —
neue Kampagne = neue `heroes.json` + `config.json` + Motive; alle
Typografie-, Umbruch- und Versand-Beschlüsse stecken im Generator und werden
geerbt.

## Die eine Lehre über allen

**Es beginnt nicht mit Texten.** Es beginnt mit zwei Dingen, die wir 2026
erst unterwegs nachziehen mussten: der **Wahrheit des Angebots** und der
**Messkette**. Beides war teurer nachzurüsten als alles Redaktionelle.

## Phase 0 — Angebots-Wahrheit (bevor irgendjemand gestaltet)

1. **Mechanik schriftlich festzurren, in einem Satz:** Was genau bekommt man,
   was kostet es danach, endet es automatisch oder muss gekündigt werden,
   bis wann gilt es? 2026 sagten die Kleinzeilen dreierlei und die
   Landingpages widersprachen sich — die eine wahre Formel («Die ersten drei
   Monate kostenlos · jederzeit kündbar · Aktion bis …») muss VOR allem
   anderen stehen. Sie ist der Vertrag; kein Text darf mehr versprechen.
2. **Frist im System, nicht nur im Text:** Der Aktionsschluss existiert nur,
   wenn ihn eine Maschine durchsetzt — uscreen-Trial-Werte zurückstellen
   (Termin in den Kalender, Vor-Aktions-Wert notieren!), Paperform kennt
   geplantes Formular-Schliessen. 2026-Befund: «nur bis 8. August» stand
   ausschliesslich im Beschreibungstext der regulären Standard-Abos.
3. **Segmente und ihre AC-Tags benennen** (2026: nurtv/nurws/noabo über
   Abo-Tags; Doppel-Abonnenten ausgeschlossen) und die **Erfolgsdefinition**:
   Was zählt als Conversion, wer liest sie wo ab, welche Zielzahl?

## Phase 1 — Messkette (das Fundament, Ende-zu-Ende, VOR dem Inhalt)

1. **utm-Schema aus `links.py`** übernehmen: fix `utm_source/medium/campaign`,
   `utm_content = w{n}_{segment}` (ein Button je Mail — Entscheid 2026: die
   Wahl wandert aus der Mail in den Browser). Register in Supabase einspielen
   (`links.py` erzeugt die Zeilen; Cockpit matcht NUR über die vier Felder).
2. **Jeden Hop prüfen:** Landingpages müssen die Query weiterreichen —
   Zwischenseiten (Übersicht!) brauchen explizites Forwarding (Lovable:
   `location.search` an alle Ausgangs-Links, sessionStorage-Fallback);
   Paperform-Buttons `prefill-inherit` (leeres Attribut genügt); Formulare
   brauchen die vier Hidden Fields MIT URL-Prefill; Webhook → Cockpit
   (`sommer2026_signups`-Muster) muss die Felder speichern.
3. **uscreen-Wissen (eingefroren):** utm wird beim Klick im Session-Cookie
   gehalten und bei KONTOERSTELLUNG am Kunden gespeichert (first touch, nur
   Web-Checkout, In-App nie) — Wellen-Zählung nach Kampagnenende per
   People-CSV-Export. Der uscreen-Webhook trägt KEIN utm (wohl aber
   `offer_id`); Standard-Abos taugen nicht als Kampagnen-Zähler.
   Prüfen: Wie schnell setzt die Kette uscreen→(Make/Uncanny)→AC das
   Abo-Tag? Die Conversion-Ausstiege der Automationen hängen daran.
4. **Ende-zu-Ende-Beweis vor Inhalt:** Test-URL mit `utm_content=e2etest`
   durch die ganze Kette; im Backend nachsehen. 2026-Trick: echte
   Produktions-Anmeldungen mit utm sind der beste Beweis — kein Testeintrag
   mit Nebenwirkungen nötig, erst in den Daten nachschauen.

## Phase 2 — Gehalt und Inhalt (in DIESER Reihenfolge)

1. **Rohmaterial des Auftraggebers zuerst.** Die wirksamste Textrunde 2026
   war die letzte — sie hätte die erste sein sollen: Was ist der GEHALT, die
   Onlyness, die Essenz aus Empfängersicht? («Teilhabe am Erkenntnisringen
   reifer Persönlichkeiten», «laut denkende Menschen», «Befreiung aus dem
   eigenen Gesichtskreis».) Erst wenn diese Sätze stehen, lohnt Dramaturgie.
2. **Der Fünfer-Tisch** (wiederverwendbare Rollen-Prompts): lyrische Autorin
   (Bild, Verb, Rhythmus) · Direct-Response-Copywriter (ein Gedanke pro
   Zeile, Öffnungskraft, Mobile-35-Zeichen) · Hüterin der Haus-Stimme
   (Würde, kein Jargon, EN eigenständig) · Neumeier (Onlyness) · Geyrhalter
   (Empfänger-Essenz). Arbeitsweise: parallel, Durchfaller-Listen mit je
   einem Kandidaten, Redaktor synthetisiert. Prüf-Linsen, die 2026 trafen:
   «Wann geht es nur um uns?» · «Wo zählt Inventar statt Gewinn?» («800
   Videos warten») · «Verspricht der Betreff etwas Falsches?» («Ihr
   Gratis-Zugang endet» — es endete die Frist).
3. **Dramaturgie-Muster (bewährt):** w1 Brücke/Ankündigung (Cross-sell-Brücke
   in den Betreff: «Was Sie sehen, jetzt auch lesen»), w2 Erinnerung mit
   Datum, w3 echte Frist (Alt-Betreff für Nicht-Öffner = ANDERE Rahmung, am
   besten die Brücke — die haben sie nie gesehen), w3b Mini-Reminder nur an
   Klicker («Sie waren schon da»). Botschaft wiederholt NIE den Betreff.
   Preheader ergänzt den Betreff (Szene↔Angebot+Frist), 60–95 Zeichen,
   IMMER als eigenes Feld pflegen.
4. **Motive:** Geräte in Aktion im echten Set schlagen Cover/Titelkarten;
   die Aktionsseiten sind eine gute Bildquelle (l5e-Assets).
5. **Gegenlesen im Editor** (Kolleg:innen, Kommentar je Feld, ✎ liefert
   konkrete Fassungen) → Rücklauf in heroes.json → neu bauen.

## Phase 3 — Fabrik und Versandreife

- `heroes.json`/`config.json` füllen, `--publish`, nach dem Merge `--verify`
  (prüft Editor, Assets UND Mail-URLs live). Build bricht >100 KB ab
  (Gmail clippt bei ~102 KB; Bilder immer gehostet, nie Data-URI).
- **Typografie (beschlossen, im Generator eingefroren):** Headline =
  Hausschrift ‹Goetheanum Deutlich›, Body = ‹Source Sans 3› (beide OFL,
  selbst gehostete woff2 — nur Apple-Clients laden Webfonts, ~Hälfte der
  Öffnungen; Fallback -apple-system/Segoe). Kicker normal (G05). Titel ohne
  einzelnes Schlusswort (nbsp) + text-wrap:balance. Kleinzeile bricht an
  den Mittepunkten, eine Aussage je Zeile. Echte Apostrophe (G16).
- Testversand an echte Clients: iPhone/Apple Mail (Webfonts!), Gmail,
  Outlook — Links auf utm_content kontrollieren (Tabelle im AC-Prompt).

## Phase 4 — ActiveCampaign (Muster 2026)

- **Drei Automationen, eine je Segment**, Sprach-Split innen (If/Else auf
  Trigger-Liste DE/EN). **Eintritt über Bulk-Tag** («S26-Start») — die
  Listen-Trigger feuern nur bei NEUanmeldungen, nie für den Bestand!
- Je Automation: Hygiene-Filter (keine Öffnung >12 Monate → Ende) →
  Segment-Weiche (Tags, überschneidungsfrei) → Wellen-Drip mit «Warten bis
  Datum» → vor jeder Welle Conversion-Check (Ziel-Abo-Tag → Ende) → vor w3
  Öffner-Split (ODER via «match any»; Plan B: verschachtelte If/Else —
  UND und ODER nie in derselben Bedingungsgruppe!) → Goal am Ende.
- **Predictive Sending nur für frühe Wellen** — es streut bis 24 h; Frist-
  Mails (w3/w3b) fix senden. HTML als Custom-HTML von den Mail-URLs
  einfügen; %UNSUBSCRIBELINK% ersetzt AC; AC-Klick-Tracking ummantelt die
  URLs nur (utm bleibt intakt).
- Reihenfolge: Automationen bauen → Testversände → AKTIV schalten → dann
  erst Bulk-Tag setzen.

## Phase 5 — Betrieb während der Wellen

- **AC hält Kopien:** Text/Betreff-Änderung vor Versand der Welle = neu
  bauen + HTML im Schritt frisch einfügen. Bilder/Schrift laden zur
  Öffnungszeit von unseren URLs — Bildtausch wirkt ohne AC, auch
  rückwirkend. **⚠ Ab dem ersten Versand sind Asset-Dateinamen append-only**
  (`--publish` räumt das Verzeichnis — gelöschte Variationen reissen tote
  Bilder in versendete Mails).
- Cockpit beobachten (Reichweite → Klicks → Abschlüsse je utm_content).

## Phase 6 — Nach der Frist (der grösste Hebel liegt HIER)

1. Frist durchsetzen (Trial zurück, Formulare schliessen) — am Tag danach.
2. Zählung: Paperform/Backend direkt; TV per uscreen-People-CSV
   (`utm_campaign` × `utm_content`), App-Zugänge als bekannte Lücke.
3. **Onboarding-Strecke für die Gratis-Monate** (Willkommen mit
   Inhalts-Empfehlungen → Mid-Trial-Impuls → Erinnerung vor Ablauf): laut
   INMA/NZZ der grösste Trial→Paid-Hebel — 2026 als To-do notiert, nächstes
   Mal von Anfang an Teil des Plans (dieselbe Fabrik, eigene heroes.json).
4. Retro in dieses Drehbuch zurückschreiben.

## Eingefrorenes Detailwissen (Nachschlag)

- **Gmail:** clippt ~102 KB, blockt Data-URIs, kein @font-face.
- **Webfonts:** nur Apple-Clients (~50 % der Öffnungen, Litmus); dieselben
  Clients laden Headline- UND Body-Font → Paarung mischt nie falsch.
- **Resend an Nicht-Öffner:** andere RAHMUNG, nicht Variante; Konvertierte
  ausschliessen; zweite Welle performt immer schwächer (Deliverability im
  Blick behalten).
- **AC:** If/Else & Goals nutzen den Segment-Builder; «match any» = ODER;
  UND+ODER nur über getrennte Gruppen. Listen-Trigger ≠ Bestand.
- **Paperform:** `prefill-inherit` (auch ohne data-, leer = aktiv);
  Formulare je Währung/Sprache (Geo-Logik CH→chf, INTL→eur); Webhooks
  tragen den vollen Payload inkl. Hidden Fields.
- **Lovable-Seiten:** Query-Weitergabe gehört als Anforderung in jeden
  Seiten-Auftrag (alle Ausgangs-Links, beide Sprachfassungen, /en-Ziele
  auf -en-Domains prüfen).
- **Sicherheit/Ordnung:** keine Test-Endpunkte (webhook.site!) an
  Produktions-Webhooks; kommerzielle Fonts nie als offene Dateien hosten
  (eigene OFL-Schriften schon).
- **Sommer-Saisonalität:** Juli/August schwächste Öffnungsmonate — w2/w3
  sind wichtiger, nicht optional; Predictive hilft früh.
