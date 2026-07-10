# CLAUDE.md — Sommer-Aktion 2026 · Mailing

Kontext-Speicher für Claude Code. Wer hier arbeitet, liest zuerst diese Datei.

## Ziel
Drei-Wellen-Mailing, 3 Monate gratis (Wochenschrift und/oder goetheanum.tv), Frist **8. August 2026**.
Drei Zielgruppen × Wellen × zwei Sprachen. Optik = Landingpage-DNA: Rosé (#A95278) auf Mist-Weiss,
FazetaSans, echte Sommer-Lifestyle-Motive. Die Mail ist **Artefakt** (Kampagnen-DNA), das
Editor-Chrome läuft auf dem Haus-Design-System.

## Eine Quelle
`heroes.json` trägt alles Redaktionelle: die Wellen-Texte (`wellen`, je Welle × Sprache, optional
`preheader`), die Motive mit CTA-Labels und Bildvariationen, den Wellenplan, Kleinzeile/Proof/Badge.
`config.json` trägt alles Strukturelle: Landing-URLs, UTM-Fix, **CTA-Ziele je Welle**
(`segmente.*.wellen_ctas` — Attribution!), Theme-Farben/Schriften, `asset_base_url`.
Nächste dreistufige Kampagne = neue `heroes.json` + `config.json` + Motive; `build_editor.py`
bleibt unangetastet.

```
heroes.json ─┐
config.json ─┼─► build_editor.py ─► dist/mail_{motiv}_{welle}_{sprache}.html (20, versandfähig)
links.py    ─┘        --publish  ─► ../../apps/mail-editor/ (Editor + Assets + mails/ = Versand-HTML
                                    per URL, für die AC-Bestückung; GitHub Pages)
                      --verify   ─► Live-Check nach dem Merge: Editor, Assets und Mail-URLs erreichbar?
```
Bauen: `pip install -r requirements.txt` · `npm i -g mjml` · `python3 build_editor.py --publish`
Wortmarke = offizielles Logo (`assets/logos/goetheanum-logo.svg` → PNG via cairosvg), Badge =
HTML-Text in der Mail-Grundschrift — beide so beschlossen im Gegenlesen (Kommentare 9.7.).

## Segmente ↔ Motive ↔ Wellenplan
- **lesen** → Segment `nurtv` (Cross-sell WS): w1 garten · w2 abendlicht · w3 see
- **sehen** → Segment `nurws` (Cross-sell TV): w1 pergola · w2 licht · w3 feuer
- **beides** → Segment `noabo` (kein Abo): w1 abendlicht · w2 vor-dem-bau · w3 picknick · w3b picknick
Auswahl (bestätigt): lesen=garten · sehen=pergola · beides=abendlicht. Motive in `assets/motive/` (8 JPGs).
Betreff-Alternativen (`wellen.*.alt`) = Munition für AC-Split (Nicht-Öffner).

## Versandfähigkeit (gelöst, nicht wieder brechen)
- `asset_base_url` gesetzt → Bilder als gehostete URLs, jede Mail ~15–17 KB (Gmail clippt bei
  ~102 KB und blockt Data-URIs). `asset_base_url` leer = nur Vorschau. Der Build bricht ab,
  wenn eine Versand-Mail über 100 KB liegt.
- Assets liegen nach `--publish` unter `apps/mail-editor/assets/` → GitHub Pages liefert sie
  unter `https://werkzeuge.goetheanum.ch/apps/mail-editor/assets/` aus. **Erst mergen/deployen,
  dann versenden** — vorher sind die Bild-URLs tot.
- Headline/Botschaft ist **HTML-Text** (Font-Stack, @font-face für Clients, die es können) —
  bei Bildblockung bleibt die Kernaussage lesbar. Nur Wortmarke + Badge sind PNG (mit Alt-Text).
- Alles Redaktionelle wird XML-escaped — ein `&` im Betreff bricht den Build nicht mehr.

## Attribution / Links (verifiziert 9.7. gegen das Live-Register)
Cockpit `sommer2026_links_public()` matcht nur über utm_campaign+utm_source+utm_medium+utm_content.
Fix: utm_source=mailing, utm_medium=email, utm_campaign=summer26_trial. `links.py` erzeugt sie aus
(segment, welle, ziel, sprache); `python3 links.py` leitet die 20 aktiven Registerzeilen ab.
**Ein-Button-Entscheid (10.7.):** noabo führt in ALLEN Wellen genau einen Button zur Übersicht
(`w{n}_noabo`); das Register wurde um `w1_noabo`/`w3_noabo` erweitert, die alten Zwei-Button-Zeilen
(`w{n}_noabo_ws|tv`) bleiben als Altbestand stehen. **make-or-break vor Versand:** (1) Die WS-Seite
reicht utm_* via Paperform `prefill-inherit` weiter (verifiziert 10.7.). (2) Die **Übersichts-Seite
muss utm_* an ihre zwei Ausgangs-Links anhängen** — ohne diesen Fix ist die gesamte NoAbo-Attribution
blind (Snippet siehe To-do). (3) GTV-Anmeldedialog: utm-Durchreichung unverifiziert.

## Der Editor (Gegenlesen)
`apps/mail-editor/` (Hub-Kategorie «Kampagne», intern): DE/EN-Umschalter, oben **Sammelansicht
«Offene Kommentare»** (To-do-Liste; anklicken springt zum Feld, schaltet ggf. die Sprache um und
öffnet das Panel), dann gemeinsame Elemente, darunter je Segment die Wellen als Mail-Vorschau,
je Feld kommentierbar (Motiv, Betreff, Botschaft, Text, CTA, Alt-Betreff, Link, ganze Mail).
Der ✎-Knopf im Kommentarfeld übernimmt den aktuellen Feldtext — Gegenleser schreiben direkt die
gewünschte Fassung statt vager Kritik. Kopfzeile zeigt Build-Stand (Datum + Git-Rev) gegen
Stale-Reviews. Die Vorschauen sind **exakt die Versand-Mails** (gehostete Bilder — kein
Doppel-Rendering, Seite ~0.5 MB statt 4 MB); offline-einbettbar nur mit leerer `asset_base_url`.
Kommentare → Supabase `sommer2026_mail_comments`, key = element-id (`shared#x` oder
`{motiv}_{welle}_{lang}#feld`), Sprache wird mitgeschrieben. **Erledigt-Haken direkt im Editor**
(RPC `sommer2026_comment_erledigt`, security definer; `supabase/comment_erledigt_rpc.sql`,
angewendet). Rücklauf: offene Kommentare lesen → in heroes.json korrigieren → neu bauen
(`--publish`) → nach dem Merge `--verify`.

## ActiveCampaign (via Cowork)
Automation einmal im UI bauen: If/Else-Split auf Abo-Tags (nurtv/nurws/noabo; beides ausgeschlossen),
Conversion-Goal, Verhaltens-Split vor w3 (Nicht-Öffner → Alt-Betreff). Generiertes HTML aus dist/ in die Schritte.
Versand ab Engagement-Segment, gestaffelt; Nicht-Öffner >12 Mt. weglassen.
Merge-Tags/Abmeldelink in AC ersetzen `%UNSUBSCRIBELINK%`.

## Offen
- [x] **Übersicht gefixt (Lovable, 10.7., publiziert):** Query-Weitergabe an alle
      Angebots-Links (`src/lib/utm.ts` — komplette location.search, Delegation vor
      Hydration, sessionStorage-Fallback für interne Navigation), Kündigungsmodell-Satz
      DE/EN korrigiert, /en verlinkt die -en-Zielseiten. Statisch live verifiziert 10.7.
      (Sätze + /en-Ziele im HTML, Weitergabe-Logik samt Host-Präfixen im App-Bundle
      `assets/index-*.js`).
- [ ] **Klick-Test im echten Browser** (Rest der Voraussetzung): Übersicht mit utm-Test-URL
      öffnen, beide Angebots-Links müssen die vier Parameter tragen (Schritt 5 des
      Paperform-Prüfauftrags deckt das mit ab). Erst danach Bulk-Tag «S26-Start».
- [ ] **Attribution GTV — halb verifiziert (10.7.):** Der Anmelde-Dialog führt in den
      uscreen-Checkout (goetheanum.tv/checkout/new?o=84317 monatlich CHF 14 / o=84322
      jährlich CHF 140) und die utm_* werden in die Checkout-URL übernommen. OFFEN: ob
      uscreen die Parameter beim Abschluss speichert/weitergibt (uscreen↔AC-Integration) —
      beim Betreiber der Integration klären, sonst bleiben gtv-Registerzeilen ohne Abschlüsse.
- [ ] **Paperform verifizieren:** Hidden Fields utm_* + URL-Prefill + Integrations-Mapping
      in sommer2026-eur-de/-en prüfen, Ende-zu-Ende-Testeintrag (Prompt liegt bereit).
- [x] GTV-FAQ bestätigt Kündigungsmodell («läuft Ihr Abo regulär weiter … Kündigung vor
      Ablauf der Testphase») — deckungsgleich mit WS-Seite und den Mail-Kleinzeilen.
- [ ] **Onboarding-Strecke nach dem 8. August** (Trial→Paid, August–November): Willkommen
      mit Inhalts-Empfehlungen → Mid-Trial-Impuls → Erinnerung vor Ablauf. Grösster
      Conversion-Hebel laut INMA/NZZ-Learnings; als neue heroes.json/config.json auf
      derselben Fabrik bauen.
- [ ] Wellen-Copy w2/w3/w3b feinschleifen (Kolleg:innen via Editor).
- [ ] Segment `beides` = geparkte Empfehlungsmail für Doppelabonnenten (später).
- [ ] Nach Merge: `python3 build_editor.py --verify` (prüft Editor + alle Bild-URLs live),
      dann AC bestücken.
- [ ] Offener Kommentar zu `lesen_w1_de#Betreff` («macht vielleicht mehr Sinn», 9.7.) —
      unklar, was gemeint ist; im Editor nachfassen (✎ liefert künftig konkrete Fassungen).
