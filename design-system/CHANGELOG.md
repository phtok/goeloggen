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

## [Unveröffentlicht]

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
