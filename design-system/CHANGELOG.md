# Design-System — Beschluss-Ledger (das Gedächtnis)

Hier atmet das System: jede Verbesserung, die aus einer Seite ins **Fundament**
aufgenommen wird, steht hier mit Datum, Grund und Wirkung. Der Ledger ist die
Erinnerung des Systems an sein eigenes Wachstum — und die Quelle der
Versionsnummer (`design-system/contract.json` → `version`, SemVer).

**Der Atem (Aufnahme-Schleife).** Eine neue Lösung taucht auf einer Seite auf →
`tools/ds-lint.py` erkennt die Abweichung (DS04) → Entscheid: **aufnehmen**
(in `tokens.css`/`base.css` + `contract.json`, Eintrag hier) oder **auflösen**
(`tools/ds-fix.py` hebt sie auf die Token-Schicht zurück). Aufgenommenes gilt ab
dann überall und wird vom Checker erwartet. So wird aus einer Rand-Verbesserung
Fundament — nie lokal belassen.

Schema je Eintrag: *was · warum · Wirkung (welche Regel/Token/Komponente)*.

---

## [1.7.1] – 2026-07-09

### Mobil-Kopfzeile entlastet: Modi-Schalter ziehen in die Schublade
- **Was:** Auf ≤720px verlassen die drei Modi-Schalter (Lesemodus ·
  Hell/Dunkel · Teilen) die Leiste und stehen als eigene Reihe `.dmodes`
  ganz oben in der Schublade — mit Wort **und** Zeichen beschriftet,
  Ziele ≥44px (B04), Beschriftung `--t-small` (B03). Die Leiste trägt
  mobil nur noch Marke + Menü. `nav.js` hält beide Button-Sätze
  (Leiste/Schublade) im selben Zustand; Desktop unverändert.
- **Warum:** Nach dem Zuwachs auf drei Schalter blieb zwischen Marke und
  Menüknopf kein Platz mehr zum Dreifachtipp (Feedback-Geste); die
  reinen Zeichen-Knöpfe waren mobil zudem schwer deutbar.

## [1.7.0] – 2026-07-09

### DS09: Fundament relativ einbinden – Wächter gegen den Custom-Domain-Bruch
- **Was:** `starter.html` und `starter-artikel.html` binden das Fundament jetzt
  RELATIV ein (Root-Beispiel, Pfadtiefen dokumentiert); der irreführende
  Kommentar («funktioniert von JEDEM Ort») ist korrigiert. Neuer Vertrags-Punkt
  **DS09** (fehler): absolute `phtok.github.io/goeloggen/(design-system|assets)`-
  URLs und absolute `data-root` meldet der Checker.
- **Warum:** Vorfall Signatur-Generator (PR #291) – die aus dem Starter
  übernommenen Absolut-URLs laufen auf der Custom-Domain ins Leere
  (Auslieferung im Root, kein /goeloggen/-Präfix) → Seite komplett ungestylt.
  Übergabe-Papier: `docs/learnings-starter-pfade.md`.
- **Nebenbefund:** Die Artefakt-Marker der Signatur-Vorschaubühne standen im
  falschen Format (`/* ds-ok: … */` statt `# ds-ok`) – der Checker sah die
  Ratifizierung nicht. Format korrigiert; Audit wieder 100 % über 40 Seiten.

## [1.6.0] – 2026-07-08

### Werkzeugwissen + Druck-Tinte (Rückfluss aus dem Kartentool)
- **Was:** Neues Dokument `design-system/werkzeugwissen.md` — Konstruktions-
  regeln für Werkzeuge, die drucken und zeichnen: kein `text-anchor="middle"`
  in Export-SVGs (Breiten selbst messen: TTF-Vorschubtabellen, Canvas nur als
  Rückfall), Icons auf die Tintenbox statt die viewBox zentrieren,
  Kontur-Zwillinge entfernen + Fugendichtung (`stroke` = `fill`) für
  Flächengrafik, `.step-num`-Masse im Kartenmassstab (Grad 0.5 × ⌀,
  Piktos 1.26 × r), Token-Treue auch für Abstände (erfundene `var(--…)`
  fallen still auf 0). Dazu neues Token **`--ink-print-leise:#6e6f6a`** —
  leises Strukturbeiwerk auf Papierweiss, gerechnet 5.07:1 (B02-fest).
- **Warum:** 18 Rückmelderunden Kartentool haben Bauwissen erzeugt, das
  sonst in der Session verloren ginge (Entscheid Auftraggeber, 8. Juli 2026:
  ‹direkt einarbeiten›). Der `--s5`-Vorfall (nicht existierendes
  Abstands-Token, still auf 0 zurückgefallen) zeigt eine DS02-Lücke —
  Kandidat für `ds-lint`: unbekannte `var(--…)`-Namen melden.
- **Wirkung:** Werkzeugwissen ist Fundament (gilt für jedes künftige
  Druck-/Grafik-Werkzeug); `--ink-print-leise` ersetzt den bisher nur im
  Kartentool notierten Hex-Wert. `contract.json` → Version 1.6.0.

## [1.5.0] – 2026-07-06

### Bild-Ebene + Logo-Disziplin (DS08)
- **Was:** Neue Rollen für Fotografie in `base.css` — `hero-bild` (Bild-Hero,
  Text nur auf dem theme-festen dunklen Schleier, Kontrast gerechnet),
  Bild-Träger in `teaser .thumb`, `event .thumb` und `poster` (object-fit,
  Fläche `--soft` als Rückfall). Dazu `brand .lockup` (erzeugtes Logo) und
  zwei neue Marken-Assets aus der Logo-Engine: `assets/logos/goetheanum-logo.svg`
  (das offizielle Logo) und `goetheanum-marke.svg` (blanke Marke). Neue Regel
  **DS08**: Die Marke kommt aus dem Logo-Generator — das Favicon
  (`goetheanum-mark-blue.svg`, Kachel) steht nie als `<img>`; `ds-lint` prüft das.
- **Warum:** Auftraggeber-Befund — die Nachbauten waren bildlos und ohne Heros
  (<q>zu viel System-Indiz, wenig Gestaltung</q>), und Seitenköpfe erfanden
  Marken-Lockups (Favicon-Kachel + Text) statt den Logo-Generator zu nutzen.
- **Wirkung:** Die vier Perspektivseiten tragen die echten Motive ihrer
  Startseiten (site-eigene CDNs: Hero, Veranstaltungs-, Artikel- und
  Poster-Bilder, Heft-Cover); goetheanum.ch-Nachbau und interner Hub führen
  das erzeugte Logo/Lockup. `contract.json` → Version 1.5.0, Rolle
  `hero-bild` + Regel DS08 ergänzt.

## [1.4.0] – 2026-07-06

### Perspektiven als Vollnachbauten + schwebende Leiste
- **Was:** Neue Rolle `fab` in `base.css` — schwebende Leiste unten rechts
  (zurück ins System · Original in neuem Fenster, Fingerziele ≥44px).
  Die vier Perspektivseiten sind jetzt **vollständige Nachbauten der echten
  Startseiten** (Inhalte von goetheanum.ch, dasgoetheanum.com, goetheanum.tv,
  anthroposophie.org, Stand 6. Juli 2026): ganze Webseite mit Kopfzeile,
  Aufmacher, Rubriken/Kalender/Katalog und Fusszeile — ausschliesslich aus
  Fundament-Rollen gesetzt.
- **Warum:** Auftraggeber-Entscheid — keine Beispiele, keine Reduktionen,
  keine erfundenen Inhalte: ein Erlebnis-Eindruck, wie die Seite mit dem
  System durchgearbeitet aussähe; das Original ist einen Klick daneben.
- **Wirkung:** `perspektiven/*.html` sind Erlebnis-Seiten ohne Hub-Rahmen
  (Nachbau-Kopfzeile je Seite mit `# ds-ok` ratifiziert). Die
  Gegenüberstellungs-Rollen `mockpair`/`mock` (1.3.0) bleiben im Fundament
  verfügbar. `contract.json` → Version 1.4.0, Rolle `fab` ergänzt.

## [1.3.0] – 2026-07-06

### Gegenüberstellung «heute ↔ mit dem System» (aus den Perspektivseiten aufgenommen)
- **Was:** Neue Rollen `mockpair`/`mock` (+ `.ist`/`.soll`, `figcaption`, `.screen`)
  in `base.css` — zwei Fenster auf dieselbe Startseite, links der heutige Zustand
  als Artefakt (fremde Schriften/Farben mit `# ds-ok` ratifiziert), rechts derselbe
  Inhalt aus den Fundament-Rollen.
- **Warum:** Die Perspektivseiten waren einseitig Befund und Analyse. Ihre Aufgabe
  ist zu **zeigen**, wie die Seiten aussähen, wenn sie mit dem Design-System
  durchgearbeitet würden — der direkte Ist↔Könnte-Vergleich je Startseite leistet
  das; die Befund-Zahlen bleiben als Beleg darunter.
- **Wirkung:** Alle vier `perspektiven/*.html` beginnen mit der Gegenüberstellung
  ihrer Startseite. Der Bau-Workflow («So baust du ein neues Werkzeug») zog von der
  Schauseite in den internen Hub (`start/#bauen`) — die Schauseite zeigt das System,
  die Werkstatt zeigt das Bauen. `contract.json` → Version 1.3.0, Rollen ergänzt.

## [1.2.0] – 2026-07-06

### Webfamilie-Komponenten + Bühne (aus dem Vier-Seiten-Befund aufgenommen)
- **Was:** Neue kanonische Rollen in `base.css` — Artikel-Anatomie (`crumbs`,
  `byline`, `lit`, `bio`, `related` + `starter-artikel.html`), `teaser` (+ `.stack`),
  `event` + `filterbar`, `stage`/`mrow`/`mtile`/`live` (Medienkatalog),
  `person`, `subscribe`, `.ds-footer .fcols`. Neue theme-feste Tokens
  `--stage-bg/-bg2/-ink/-muted/-veil` (Kontraste gerechnet: ink 15.3:1,
  muted 8.2:1).
- **Warum:** Analyse der vier grossen Goetheanum-Webseiten
  (`docs/webfamilie-befund.md`): ihre Inhaltsmuster (Artikel, Kalender,
  Medienkacheln, Newsletter) fehlten dem Fundament; ihre wiederkehrenden
  Fehler (Versal-Bylines, <14px, Kontrast-Fails, lh 1.4) zeigen, welche
  Regeln die Rollen einbauen müssen.
- **Wirkung:** Vier Testseiten unter `perspektiven/` zeigen je Original den
  Nachbau, den gerechneten Vorher-nachher-Befund und den Einbau-Weg
  (Craft/WordPress/Uscreen). Schaufenster-Abschnitt «Perspektiven des
  Design-Systems». `contract.json` → Version 1.2.0, Rollen ergänzt.

## [Unveröffentlicht]

### Kartentool-Learnings aufgenommen (Werkzeugwissen + belegte Werte)
- **Was:** Nachschlagewerk Werkzeugwissen (SVG-/Druck-Export-/
  UI-Bauwissen); Quelle `docs/learnings-kartentool.md` (14 verifizierte
  Testrunden). Kernregeln: Icons auf die **Tintenbox** zentrieren (Einzeldateien
  tragen keine einheitliche viewBox — nachgeprüft: nur 46 von 81 Dateien haben
  die Standardbox); in Export-SVGs **kein `text-anchor="middle"`** und **keine
  OpenType-Feature-Abhängigkeit** (PDF-Renderer ignorieren beides — Breiten und
  Ziffern-Slots selbst setzen); Kontur-Zwillinge entfernen, Fugen mit
  Eigenkontur in Füllfarbe dichten.
- **Belegte Werte:** Druck-Tinten auf Papierweiss gerechnet — `#4e4f4a` 8.26:1,
  `#6e6f6a` 5.07:1 (Token-Kandidat `--ink-print-leise`, aufgenommen sobald ein
  zweites Druckwerkzeug ihn braucht), `#767771` 4.52:1. Die Hausschrift führt
  `tnum`/`lnum` als GSUB-Features — G25 über `font-variant-numeric` greift auch
  in der Hausschrift (nur nicht im PDF-Export).
- **Bestätigt:** Die `.step-num`-Sitzkorrektur (translateY 8 %) wurde im
  Kartentool unabhängig pixelverifiziert; Vermerk am Kommentar in `base.css`.
- **Ratifiziert und umgesetzt (9. Juli 2026):** Icon-Einzeldateien per
  `normalize_icon_svgs.py` aus dem Font regeneriert — einheitliche Em-Box
  `-2 -1002 1004 1004` (Ausnahme Wortmarke, proportional), ‹mit Text›-Waisen
  entfernt (nur Webfont), PNG/PDF/ZIP neu, idempotent (Hash-verifiziert).
  Sichtprüfung: Rollstuhl jetzt font-wahr statt eigenbox-vergrössert.
  Die parallel entstandenen zwei Werkzeugwissen-Papiere (docs/ und
  design-system/) sind zu EINEM konsolidiert: design-system/werkzeugwissen.md.

### Neuer Font «Goetheanum Pfeile» – Pfeile & Kompass ohne PUA-Umweg
- Die Pfeile/Kompass lagen im Icon-Font im **Zeichen-Privatbereich (PUA)** und waren
  nur über Option/Alt oder die Glyphenpalette erreichbar; eine installierbare
  Tastaturbelegung dafür existierte nie (sie stand nur im Beipackzettel). Statt eine
  fehleranfällige, hier nicht testbare `.keylayout`/`.klc` zu erfinden: **ein eigener,
  schlanker Font**, der dieselben 20 Zeichen auf **normale Tasten** legt (Belegung ‹A›,
  Beipackzettel-treu; Umschalt = fett). Schrift wählen, Taste tippen – kein Option,
  kein PUA, keine Belegungsdatei. Die PUA-Codepoints bleiben zusätzlich erhalten.
- **Reproduzierbar über die Font-Skripte**: `tools/goetheanum-fontfix/build_pfeile.py`
  leitet «Goetheanum Pfeile» aus dem Icon-OTF ab (Subset auf 20 Glyphen, Grundtasten +
  PUA belegt, Metadaten/Lizenz/Version aus dem Icon-Font geerbt), baut otf · woff ·
  woff2 · Office-TTF und legt alle vier Dateien ins Office-ZIP und ins Komplett-Bündel
  `Goetheanum-Schriften-v2.7.zip`. `build_office_ttf.py` kennt den Font jetzt (JOBS).
- **Web** (`icons.html`): der zweite Tastatur-Reiter heisst statt ‹Option/Alt› nun
  **‹Pfeile & Kompass›** und rendert die Zeichen aus dem neuen Webfont auf ihren
  Grundtasten (Klick kopiert weiterhin). Eigene Download-Karte (woff2/OTF).
- Verifiziert: Font lädt im Browser, `6 t u h` → ↑ ← → ↓, `T` kopiert U+E267; Office-TTF
  (glyf) und beide ZIPs enthalten den Font; Score 100 %.

### Icon-Font: fehlende Glyphe «Goetheanum Badge invers» repariert
- Ein Font-Audit (alle Schriftdateien, nicht nur die eine) zeigte: 44 von 45
  benannten Icons waren korrekt belegt, aber **«Goetheanum Badge invers» hatte in
  keiner Datei einen eigenen Glyph** — U+0031 (`1`, die im Beipackzettel S.2
  dokumentierte Taste) fiel auf den generischen Füll-Glyph zurück; der Fehler
  steckte schon im Quell-Master `v0.3.35.otf`. `icons.json` wies das Zeichen zudem
  falsch auf U+0022 aus (Widerspruch zu Beipackzettel und `build.py`).
- **Repariert über die Font-Skripte** (nicht freihändig): `fontfix.add_badge_invers`
  (CFF) und `add_badge_invers_ttf` (glyf/cu2qu) holen die Kontur aus der Einzeldatei
  `goetheanum-badge-invers.svg` (deren `d` liegt in y-oben-Fontraum, importiert also
  mit Identität wie der positive Badge auf `2`). `apply_badge_invers.py` setzt sie
  idempotent in **otf · woff · woff2 · Office-TTF** und packt **Office-TTF.zip** und
  **Schriften-v2.7.zip** neu; `build_icons()` ruft die Reparatur mit, damit ein
  Voll-Rebuild korrekt bleibt. `icons.json` auf U+0031 berichtigt.
- Verifiziert: alle 8 Font-Artefakte 45/45, U+0031 belegt; im Web zeigt Taste `1`
  jetzt den Kreis-Badge (invers), `2` den Quadrat-Badge — Beipackzettel-treu.

### Aufgeräumt: interne Vergleichsstudie entfernt
- `apps/logos/preview-hinweise.html` gelöscht — eine nirgends verlinkte Studie
  (‹Aktuell · Vorschlag›), die als einzige Seite den ds-lint-Score auf 97 % zog
  (var()-Fallbacks, Artefaktfarben, ein 6.5px-Text). Score wieder **100 %**.

### Icons-Tastatur: Option/Alt-Ebene wiederhergestellt (Pfeile & Kompass)
- Die Web-Tastatur zeigte nur die **Grundebene** (Buchstaben → Piktogramme) und
  liess die 20 Pfeil-/Kompass-Zeichen fallen: ihre Codepoints liegen im Privat-
  bereich (PUA), passen also auf keine Buchstabentaste – und ihre **dokumentierte
  Tastenlage (Beipackzettel Seite 3: Option/Alt) war nie in Daten kodiert**, nur
  im PDF. Jetzt ein **Ebenen-Umschalter** (Grundebene ⇄ Option/Alt): die zweite
  Ebene setzt Pfeile und Kompass auf ihre belegten Tasten (⌥6=↑, ⌥T=←, ⌥U=→,
  ⌥H=↓, ⌥2/0/Q/E/O/Ü/S/Ö=gebogen, ⌥Y/X/C/V=Kompass). Jede Zeichen-Taste ist ein
  Knopf – **ein Klick kopiert das Zeichen** (fürs Web), Rückmeldung per Toast.
  Ersetzt die vorige Behelfs-Palette; das Verlorene ist zurück auf der Tastatur.

### Neues Werkzeug: Goetheanum Editor (v1) – die Typografie-Engine läuft im Browser
- **`assets/typografie/goe-typo.js`** (neu, wiederverwendbar): führt
  `typo-regeln.yaml` clientseitig aus – lädt und parst die Regeln (derselbe
  Mini-Parser wie `tools/typo-check.py`, eine Quelle der Wahrheit), behebt
  ‹fehler›-Regeln automatisch und findet ‹empfehlung›-Regeln als offene Fragen
  mit Kontext-Ausschnitt fürs Verständnis. Kein Rendering/DOM – reine Engine,
  gedacht als Baustein fürs Backend weiterer Goe-Webseiten (v3-Ziel).
- **`apps/editor/`**: Text einfügen, ‹Prüfen› klicken – Eindeutiges (Anführung,
  Striche, Auslassung, Ziffern-Gruppierung, Leerzeichen) wird sofort gesetzt und
  im Protokoll ‹Angewandt› nachvollziehbar; offene Fragen (Abkürzungs-Spatium,
  Prozent/Einheiten-Spatium, Uhrzeit, Minus) erscheinen als Marginal-Karten mit
  Übernehmen/Lassen und Sammel-Übernahme. Die 10 Urteils-Regeln (`pruefung: lm`
  – Schriftwahl, Auszeichnung, Zeilenmass, Kontrast …) sind ausgewiesen, aber
  noch nicht automatisiert (kein LLM in v1) – folgt als Lektorat-Pass (v2).
- Eintrag in `tools.json`/Startseite/Menü (Kategorie Werkzeuge, Priorität nach
  Signatur). Score bleibt 100 % (konform).

### Icons-Tastatur: das Piktogramm wird zum Held der Taste
- Die Icons standen mit 26px verloren in 48px-Tasten, der Buchstabe konkurrierte
  darunter. Jetzt: ruhigere Tasten (62px), Icon mittig bei 40px, Buchstabe als
  kleine Legende in der unteren rechten Ecke (wie das Zweitzeichen echter Tasten),
  leere Tasten treten zurück (`opacity`). *Wirkung:* die Piktogramme führen den
  Blick statt zu verschwimmen; hell/dunkel bleibt tokengetrieben (`--ink`).

### `.step-num` optisch nachjustiert · Links im Fliesstext sichtbar
- **`.step-num` neu vermessen** (`base.css`): der erste Fix (line-height:1 +
  Flex-Zentrierung) zentrierte die *Line Box*, nicht die Zeichen-Tinte – Nutzer-
  Feedback bestätigte, dass Ziffern sichtbar zu hoch sassen. Per Pixel-Analyse
  (Screenshot der echten Schrift, Tinten-Bounding-Box vs. geometrische Kreismitte)
  UND Font-Metriken (hhea ascent 750/descent −250 vs. Ziffern-Tintenmitte ≈ 330/1000)
  übereinstimmend auf **8 % `translateY`** des inneren Zahl-Elements bestimmt –
  zwei unabhängige Methoden, ein Ergebnis. *Wirkung:* Ziffer sitzt jetzt tatsächlich
  mittig, nicht nur nach CSS-Theorie.
- **`.step-num` Gold als Hausfarbe**, `.blue` als benannte Ausnahme (vorher
  umgekehrt). *Warum:* Gold ist bereits die Auswahl-/Markierungsfarbe im System
  (Auswahl-Pille, `.seg button[aria-pressed]`) – zwei blaue Kugeln neben einer
  goldenen wirkten wie ein Fehler, nicht wie Absicht. *Wirkung:* Schritt-Marken
  sind einheitlich Gold; Blau bleibt für Vergleichsseiten verfügbar, die Alt/Neu
  bewusst farblich trennen wollen.
- **Links im Fliesstext sichtbar** (`base.css`): der globale Reset (`a{color:
  inherit;text-decoration:none}`) machte Links in Absätzen/Listen/Hinweisen
  farblich und optisch identisch mit umgebendem Text – ein Link in den
  Logo-Hinweisen wurde dadurch für nicht vorhanden gehalten. *Wirkung:* `p a`,
  `li a`, `.note a` etc. bekommen Gold + dezente Unterstreichung (DS05 nimmt
  Links vom Unterstreich-Verbot ausdrücklich aus – das ist Link-Konvention,
  keine Betonung).

### Feinschliff: Karussell zentriert · Such-Synonyme · PowerPoint-Bild
- **Karussell-Inhalt zentriert** (Thumb + Text als Gruppe mittig) statt linksbündig.
- **Suche mit Synonymen**: pro Werkzeug `such`-Begriffe in `tools.json`; die Menü-Suche
  matcht Titel **und** Synonyme. So findet ‹Farben› jetzt Sektionsfarben **und**
  Design-System (wo Marken-/Neutralfarben wohnen).
- **PowerPoint** bekommt ein eindeutiges Bild (Mini-Folie mit Titelzeile) statt des
  mehrdeutigen ‹P›.

### Burger flach (Modell B) – keine Kategorien öffentlich
- Das Menü zeigt öffentlich **eine priorisierte Liste** (wie die Startseite), mit
  ‹Startseite› oben – keine aufklappbaren Welten mehr. Die Suche übernimmt das Finden.
- **Backstage** bleibt unverändert nach Welten gruppiert hinter dem geheimen
  Dreifach-Klick. Reihenfolge in `FLAT_ORDER` (deckungsgleich mit der Startseite).

### Beta-Einblender + Suche im Menü; Karten-Pillen abgelöst
- **Beta-Einblender** (`nav.js`/`nav.css`): ein dezenter, schwebender Hinweis unten –
  ‹Beta – die Werkzeuge wachsen noch. Feedback geben ✕›, wegklickbar (merkt sich
  ‹gesehen› in localStorage). Löst die per-Karte-Pillen ab; ein Ort statt zwölf Marker.
- **Suche im Menü**: Tippfeld oben in der Schublade filtert die Werkzeugliste live;
  leere Bereiche blenden aus, Treffer-Bereiche klappen auf.
- Startseite: ‹Schon entdeckt?› klein/fein über das Karussell gehoben; Karussell-Inhalt
  Wallpaper · Schriften · PowerPoint · Icons · Logos; Karten ohne Pillen, eine Fläche.
- Konsolidiert: Webfont in Schriften (Abschnitt + Sprunglink), Zeichen in Logos (Link) –
  keine eigenen Karten mehr.

### Startseite: Entdecker-Karussell + Karten flach nach Priorität
- **Karussell** oben (rotierend, pausiert bei Hover/Fokus, respektiert
  `prefers-reduced-motion`, Pfeile · Punkte · Wisch): ein **Hinweis auf weniger
  Bekanntes** (Sektionsfarben, Zeichen, Übersetzungen, Wallpaper, Typografie,
  Design-System) – ‹Schon entdeckt?›.
- **Karten flach nach Priorität** statt nach Kategorien gruppiert (Logos · Signatur
  · Visitenkarten · Icons · Schriften · …). Backstage-Welten bleiben draussen
  (öffentliche Kategorien-Schranke beibehalten).
- Die Mini-Visuals der Karten von `.tile .x` auf `.thumb .x` generalisiert, damit
  das Karussell dieselben Erkennungszeichen nutzt – eine Quelle, kein Duplikat.

### Schliff: Sektionsfarben-Seite · Design-System-Bild · Theme-Icon ohne Emoji
- **Farben → Sektionsfarben**: die Sonderseite trägt jetzt **nur Sektions- und Bereichsfarben**
  (datengetrieben aus `goe-orgs.js`: 12 Sektionen + 6 Bereiche). Marken- und Neutralfarben wohnen
  im **Design-System** (Schaufenster `#swatches`) – keine Doppelpflege. Datei, Karte und Slug heissen
  jetzt `sektionsfarben`. Pantone war schon raus.
- **Startkarte Design-System** bekommt ein **eigenes Bild**: ein Mini-Bauplan (Leiste + Textzeilen +
  Farb-Chips = Struktur **und** Farbe) statt der Farbfelder – klar unterscheidbar von den Sektionsfarben.
- **Theme-Schalter ohne Emoji**: Sonne/Mond sind jetzt **Inline-SVG** (currentColor) statt der
  Unicode-Glyphen ☀/☾, die iOS zu Emoji umfärbte. Deterministisch in Hell wie Dunkel.

### Weitere Lücken vom alten Auftritt geschlossen: Zeichen · Wallpaper · PowerPoint · Feedback
- **Zeichen** (`zeichen.html`) – die Zeichen von Rudolf Steiner (Hochschule, Gesellschaft,
  Bau-Administration) als Vorschau + Anwendungshinweis + Zugang zu den vollständigen Paketen.
  Die Marken stehen auf weissem Feld (`# ds-ok`: Briefpapier-Artefakt, in Hell wie Dunkel sichtbar).
  Assets von grafik.goetheanum.ch gezogen, als echte PNG abgelegt (`assets/zeichen/`).
- **Wallpaper** (`wallpaper.html`) – elf Desktop-Hintergründe (2500×1406) zum Herunterladen.
  Von der CDN gezogen, als JPG q88 abgelegt (`assets/wallpaper/`, ~0,5 MB gesamt).
- **PowerPoint** (`powerpoint.html`) – Platzhalterseite (Vorlage wird überarbeitet, Datei folgt).
- **Neue Welt ‹Anwendungen›** (cat `anwendung`) in `nav.js`/`tools.json`/Startseite – für fertige
  Vorlagen (Wallpaper, PowerPoint); **Pantone aus der Farbseite entfernt** (wird nicht mehr verwendet).
- **Globaler Feedback-Link** im Menü (Schubladen-Fuss, `nav.js`) – mailto an die Hausgrafik, auf jeder
  Seite erreichbar. Bewusst NICHT in der Kopfzeile: dort frass ein Icon die leere Fläche an, über die
  der (geheime) Dreifach-Klick die Intern-Ansicht schaltet. Anfrage-/Druckformular bleibt getrennt (Todo).

### Neue Publikumsseite: Farben (Lücke vom alten Auftritt geschlossen)
- **`farben.html`** – die Identitätsfarben auf einen Blick (Marke · Neutrale ·
  Sektionen). **Hex/RGB/HSB** werden im Browser exakt aus dem Token-Hex errechnet
  (eine Quelle: `tokens.css`; Sektionen aus `goe-orgs.js`), jede Zelle klick-kopierbar.
- **Ehrlich statt erfunden** (Hausregel): **CMYK** steht als **rechnerischer Richtwert**
  (sRGB→CMYK, geräteabhängig) klar markiert; **Pantone** und die offiziellen Druck-CMYK-/
  Sonderfarben sind ‹—› (noch aus dem Marken-Handbuch zu erfassen). Damit ist der im
  Schaufenster offene Punkt ‹CMYK-/Sonderfarben› sichtbar adressiert, ohne falsche Werte.
- Registriert in `tools.json` (cat `system`, erscheint in der Welt **Elemente**) + Startkarte.
- Aus dem Vergleich mit grafik.goetheanum.ch als ‹jetzt bauen› gewählt; Zeichen, PowerPoint,
  Wallpaper und ein globaler Kontakt-/Feedback-Button sind als nächste Schritte vorgemerkt.

### Generatorpass: die letzten vier Werkzeuge theme-aware – 100 %
- Die vier Generatoren folgten eigenen, fest verdrahteten Dunkel-Paletten und
  ignorierten Hell/Dunkel. Jetzt **theme-aware reskinnt**: ihre lokalen Variablen
  sind nur noch **Aliase auf die DS-Tokens** (`--bg→--paper`, `--panel→--soft`,
  `--text→--ink`, `--accent→--gold` …) – eine Kante, das ganze Chrome kippt mit.
  - **karten-generator** · **cover-generator** · **briefschaften**: Chrome auf
    Tokens, Aktion = volles Blau + Weiss (B01), Auswahl = dunkles Gold + Weiss,
    Felder/Knöpfe/Pillen aus dem Fundament; base.css ergänzt wo es fehlte (DS01).
  - **gtv-naming** ist zu grossen Teilen ein **Artefakt**: ein Marken-Muster einer
    hypothetischen ‹Goetheanum TV›-Plattform samt **Telefon-Mockup** (eigene
    Bildsprache: Titillium, Navy). Laut Hausregel kein Theme-Grund – darum
    **ratifiziert** (`# ds-ok`, eigene `--gtv-*`-Palette). Theme-aware ist allein
    das Werkzeug-Chrome, die Präsentations-Leiste `#presenter`.
- **Gedruckte Artefakte bleiben fest**: das A4-Blatt (karten/briefschaften) und die
  Cover-Leinwand bleiben weiss bzw. tragen die echten Druckfarben (`# ds-ok`),
  kippen NICHT mit dem Theme.
- **`start/index.html`** (alte Übersicht) mit auf den Floor gehoben (sub-14 → Tokens,
  Versal-Kicker entfernt G05, Rest tokenisiert).
- **Vertrag geschärft (v1.1.0)**: `reference/` zum Geltungsbereich-Ausschluss
  ergänzt – eingefrorene Referenz-Schnappschüsse sind keine Live-Flächen (ds-fix
  schloss sie längst aus; jetzt deckungsgleich). Score wird dadurch ehrlich.

> Score-Verlauf (Fortsetzung): **76 %** → **92 %** (vier Generatoren auf 0 Fehler)
> → **100 %** (`start/` + Vertrag-Geltungsbereich). **24/24 Seiten konform, 0
> Fehler.** Verbleibend nur Hinweise (DS04 additive Eigenrollen, DS05/DS06 in den
> bewusst eigenständigen Mockup-/Übersichtsköpfen).

### Aufgenommen
- **`.step-num`** (`base.css`, `contract.json` DS04) — runde Schritt-Nummer vor
  nummerierten Zwischentiteln (fixe Höhe *und* Breite statt nur `min-width`,
  `line-height:1`, tabular-nums). *Warum:* eine Seite (Logo-Hinweise) erfand
  Kreis-Badges lokal; die Ziffer sass optisch nicht mittig, weil `min-width`
  allein plus `align-items:baseline` im Elternflex die Kreisgeometrie und die
  Zentrierung dem Zufall überliess. *Wirkung:* eine Quelle für nummerierte
  Schritte, verlässlich rund und mittig, ab jetzt überall (`step-num` in DS04).
- **Textrollen als gemessene Grundlage** (`base.css`) — Kicker · Lede · Hinweis
  (`.note`/`.hint`/`.help`/`.desc`) · Meta (`.cap`/`.caption`/`.legend`/`.byline`) ·
  Label (`.lab`/`.role`) · Wert (`.readout`) · Code (`.code`/`.mono`).
  *Warum:* jede Seite erfand eigene Grade (11–15px) und Farben für denselben
  Zweck — uneinheitlich und teils unter der Leseschwelle. *Wirkung:* eine Quelle,
  B03-sicher, löst die Eigenlösungen ab (DS04).
- **Mobil-Baseline** (`base.css`) — Fingerziele ≥44px, Felder ≥16px, kein
  Überlauf, umbrechende Köpfe. *Wirkung:* B03/B04 als Konstruktion, nicht als
  Nachkontrolle.
- **Sektionsfarben als Tokens** (`tokens.css`/`tokens.json`) — `--sek-*` aus
  `assets/goe-orgs.js`. *Warum:* die Sektions-Identitätsfarben lebten nur in der
  Logo-Engine. *Wirkung:* überall gleich benannt, markenfest (kippen nicht mit
  Hell/Dunkel).
- **`--ok` (Erfolgsgrün)** (`tokens.css`/`tokens.json`). *Warum:* die Engine fand
  das Grün `#3f7d46` hartverdrahtet in `base.css .btn.ok` und im Schaufenster –
  ein fehlendes Token. *Wirkung:* erste echte Atem-Aufnahme: aus einer entdeckten
  Abweichung wurde Fundament; `.btn.ok` und die Status-Punkte ziehen jetzt `--ok`.

### Engine (neu)
- **`design-system/contract.json`** — maschinenlesbarer Struktur-Vertrag (DS01–DS07).
- **`tools/ds-lint.py`** — prüft Gestalt-Konformität, meldet je Regel + Score.
- **`tools/ds-fix.py`** — hebt die Hauspalette deterministisch auf Tokens (Codemod).
- **Hook** — `ds-lint --staged` läuft mit (vorerst berichtend, nicht blockierend).

> Score-Verlauf (die Messlatte): **9 %** (Engine-Einführung) → **17 %** (Fundament
> + Schaufenster) → **35 %** (öffentliche Live-Seiten) → **46 %** (Generatoren +
> Icons). 11/24 Seiten konform. Jeder Schritt bewegt diese Zahl.

### Schaufenster bildet ab, was bereitliegt (Doku + Präsentation in einem)
- Neue Abschnitte, live aus der Quelle gerendert: **Textrollen** (Kicker/Lede/
  Hinweis/Meta/Label/Wert/Code/Badge), **Sektionen & Bereiche** (volle Tabelle
  aus `goe-orgs.js` + `--sek-*`-Swatches), **Konformitäts-Engine** (Vertrag
  DS01–07 aus `contract.json`, die Schleife, der Score).
- `goe-orgs.js` ist damit im Design-System **sichtbar** und über die Quelle
  korrigierbar. Befund dabei: die Visitenkarten-App trägt eine **abgewichene
  Kopie** der Tabelle – Konsolidierung (einbinden statt kopieren) steht an.

### Lesbarkeit & Inklusivität fest verankert (recherchiert, Stand 2026)
- **Typo-Skala einen Schritt grösser**: Floor 13→**14px**, Meta/Label 14→**15–16**
  (`--t-small`), Fliesstext 17→**18–20** (`--t-body`), Lede 19→**20–23**. Grund:
  16px ist die Norm-Untergrenze, Best Practice ‹bei 16 beginnen, hochskalieren›
  (WCAG resize 1.4.4; rem-basiert). Contract-Floor (DS03) 13→14 nachgezogen; die
  literalen 13px der öffentlichen Seiten auf `--t-small` gehoben.
- **B04**: Bezug auf WCAG 2.2 SC 2.5.8 (Ziel ≥24px, wir geben 44) und 1.4.12
  (Layout übersteht erhöhte Laufweiten) in den Hausregeln verankert.
- **Icons im Dunkelmodus**: schwarze Strich-Icons als `<img>` wurden verschluckt.
  Utility `.ico-invert` (Filter im Dunkelmodus) ins Fundament; auf die Schriften-
  Icons angewandt. Besser noch: Icons als Webfont/Inline-SVG mit currentColor.

### Die Schrift-Grenze gezogen – Source Sans 3 endlich im Einsatz
- Die zweite Groteske (Source Sans 3) war geladen, aber ungenutzt. Jetzt verdrahtet:
  **Funktion & Daten** tragen sie (Label, Wert/Readout, Meta/Legende, Badge/Chip,
  Formularfelder, Tabellen) – klein & konventionell deutlich lesbarer.
- **Identität bleibt Hausschrift**: Titel, Kicker, Lede, **Fliesstext und erklärende
  Hinweise** (Sprache). Lesbarkeit dort aus den **Faktoren**: --lh-body 1.6 → **1.66**,
  Mass ~62ch, Schnitt Klar, Betonung Laut. Die Grenze ‹wo Lesbarkeit über Identität
  geht› in CLAUDE.md verankert.

### Backstage/Beta auf den 14px-Floor + Org-Farbe angeglichen
- Acht Specimen-/Backstage-Seiten (Typografie, Tester, Grotesk+, Vorschau,
  Mischsatz, Ligaturen ×3) auf den neuen Floor gehoben: literale <14px → --t-small;
  Reste tokenisiert (Bar-Hintergrund → --bar-bg, Gold-Tint → color-mix, Code-Chip
  → --code-*). Alle 0 Fehler. Gesamt-Score **42 % → 72 %** (18/25 konform).
- **Track 1**: `--bereich` von #005eb8 auf **#0061a9 = Markenblau** angeglichen
  (so rendern es die Logo-Daten/goe-orgs.js schon). Sektionsnamen-Korrekturen aus
  #164 (Team) übernommen; spanische Gesellschaft bleibt `prüfen`.

### Einbinden statt kopieren – eine Org-Quelle (Drift dauerhaft behoben)
- Es gab DREI Org-Datensätze: `assets/goe-orgs.js` (36, Schaufenster), `assets/
  data/goetheanum-orgs.js` (38 inkl. it/subscriptions, live: Logos+Signatur) und
  eine **inline-Kopie** in Visitenkarten (abgewichen). Befund bei der Prüfung:
  die *live*-Daten treffen goetheanum.ch besser (es ‹Bellas Artes›, ‹Jóvenes›).
- **`assets/goe-orgs.js` ist jetzt die EINE Quelle** (38 Orgs der Live-Daten +
  vollständige API: bare `ORGS`/`CATS` für die Logo-Engine & Signatur UND
  `GCI_ORGS`/`window.GOE_*` fürs Schaufenster). Logos, Signatur, Visitenkarten,
  Briefschaften, Schaufenster und Übersetzungen binden dieselbe Datei ein; die
  Inline-Kopie ist raus, `assets/data/goetheanum-orgs.js` gelöscht. Verifiziert:
  alle Dropdowns/Tabellen 38 Einträge, Logo rendert. Drift ist nicht mehr möglich.

### Neue Quelle & Werkzeug
- **`assets/goe-terms.js`** (Begriffe & Übersetzungen) – auf goetheanum.ch
  geprüft: fr/es korrigiert (Hochschule = ‹Université libre de science de
  l’esprit›, Gesellschaft = ‹Société anthroposophique générale›), verifizierte
  Zeilen auf `fest`. Neue Seite **uebersetzungen.html** (durchsuchbar, klick-
  kopierbar, für die Sekretariate) + Eintrag in `tools.json` (Startkarte).

### Behoben (Mobil & Lesbarkeit – aus echtem Geräte-Befund)
- **Seitenrand am Handy** war weg: `.hero{padding:X 0 Y}` setzte den seitlichen
  Rand auf 0 und überschrieb `.wrap` – Text klebte am Glas. Fundament-Fix:
  `.hero` nutzt nur noch `padding-block` (Seitenrand kommt aus `.wrap`); die 9
  Seiten mit lokalem `.hero`-Override nachgezogen. Mobiler `.wrap`-Rand bleibt
  grosszügig (`max(22px, safe-area)`), nicht verkleinert.
- **Lede unlesbar** (in „G Leise" 265 + muted gesetzt) → auf den Lese-Schnitt
  Klar gehoben (schriften, icons, statistik). Regelbezug: Leise verschwimmt klein,
  Minimum ist Klar.

### Engine geschärft (Lernen am Bestand)
- **DS04** meldet nur noch Schlüssel-Selektoren, nicht kontextuelle Überschreibungen
  (`.download .btn` ist Verortung). **Zeilen-Treffer** liegen jetzt korrekt auf der
  Property-Zeile (Mehrzeilen-CSS) – damit greift `# ds-ok` auch in den Generatoren.
- **Artefakt-Kategorien** ratifiziert (`# ds-ok`): gedrucktes Blatt/Karte, Schnitt-
  marken, E-Mail-Leinwand, „Logo auf Dunkel"-Vorschau, Owner-Mode-Signal, Modal-Scrim.
  Die Maschine schlägt vor, der Mensch ratifiziert – die Ausnahme wird Teil des Codes.

---

## Wie eine Verbesserung aufgenommen wird (Kurz-Rezept)
1. Lösung an *einer* Seite bewährt? `ds-lint` zeigt sie als DS04-Abweichung.
2. In `tokens.css`/`base.css` heben (Token oder Rolle/Komponente). Bei neuer
   Pflicht: `contract.json` ergänzen (Regel/Klasse) **und** `version` erhöhen.
3. Eintrag hier (was · warum · Wirkung).
4. `ds-fix` über die Seiten laufen lassen, `ds-lint --score` prüfen, shippen.
