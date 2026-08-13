# Goetheanum Tools

Dieses Repository enthaelt nur noch Goetheanum-Projekte.

## Schnellueberblick

### Apps

Statische Onepager liegen unter `apps/`:

- `apps/logos/` - Logo-Generator (Slug `logo-generator`, kurze Adresse `/logo-generator/`)
- `apps/gtv-naming/` - GTV Naming – Renderings: Praesentationswerkzeug fuer die Umbenennung von Goetheanum TV mit umschaltbarer Wortmarke fuer alle Namenskandidaten
- `apps/visitenkarten-generator/`
- `apps/briefschaften/`
- `apps/karten-generator/`
- `apps/cover-generator/`
- `apps/signatur-generator/` - E-Mail-Signatur-Generator: erzeugt table-basiertes Signatur-HTML mit Inline-CSS nach gemeinsamer Vorlage

### Services

Nicht-statische Unterprojekte unter `services/`:

- `services/sommer-zaehler/` – Backend des Aktions-Cockpits
- `services/mailing-sommer2026/` – Mail-Fabrik der Sommer-Aktion 2026
- `services/mailing-grenzgaenger/` – Mail-Fabrik der Grenzgaenger-Wellen
- `services/lead-agent/` – Fang-Strecke des Grenzgaenger-Agenten
- `services/seelenkalender/` – Versand-Strecke des Wochenspruch-Abos
- `services/werkzeug-abo/` – Update-Abo der Werkzeuge
- `services/schmiede/` – Eingang der Wuensche aus der Werkzeug-Schmiede
- `services/qr-generator/` – Kurzlinks mit anonymer Scan-Zaehlung
- `services/kistenpflege/` – Sortierer der Werkzeugkiste
- `services/werkzeugpost/` – Textbestand der Werkzeugpost

### Collections

Materialsammlungen und Produktionsquellen liegen unter `collections/`:

- `collections/jahrgaenge/`

### Gemeinsam genutzt

- `assets/` - gemeinsame Schriften, Maps, SVGs und minimale Vendor-Dateien fuer die statischen Tools
- `workers/` - Cloudflare-Worker fuer Visitenkarten-Mailversand
- `docs/` - Spezifikationen und Projektdokumentation
- `reference/` - Referenzmaterial und Konzeptstaende
- `archive/` - archivierte Altversionen und alte Einstiegspunkte

## Root-Einstiege

Die Root-HTML-Dateien sind jetzt bewusst nur noch Launcher oder Rueckwaertskompatibilitaet:

- `index.html` -> Front door (Uebersicht der Werkzeuge; Wurzel umgelegt)
- `portal.html` -> `index.html` (Alias, alte Links bleiben stabil)
- `logo-generator.html` -> `apps/logos/`
- `visitenkarten.html` -> `visitenkarten-generator.html`
- `visitenkarten-generator.html` -> `apps/visitenkarten-generator/`
- `briefschaften.html` -> `apps/briefschaften/`
- `karten.html` -> `karten-generator.html`
- `karten-generator.html` -> `apps/karten-generator/`
- `cover-generator.html` -> `apps/cover-generator/`
- `index-cover-generator.html` -> `cover-generator.html`
- `signatur-generator.html` -> `apps/signatur-generator/`
- `index-goelogger-gci1.html` -> `logo-generator.html`

Damit bleiben alte Links stabil, waehrend die eigentlichen Apps klar in Ordnern liegen.

## Jahrgaenge

Die Sammlung der Zeichnungen und Texte aus den Jahrgaengen ist kein einzelnes Webtool.

Vorgesehener Ort:

- `collections/jahrgaenge/pdfs/`
- `collections/jahrgaenge/zeichnungen/`

Die zugehoerigen Verarbeitungsskripte und groesseren Datensammlungen folgen spaeter in separaten Merges.

## Was aktuell online bleibt

`deploy-pages.yml` baut ein kuratiertes Bundle (`_site`) und laedt es als
Pages-Artefakt hoch — aber **ausgeliefert wird es derzeit nicht**. Gemessen am
13. August 2026: `werkzeuge.goetheanum.ch` serviert den **Branch-Inhalt**, nicht
das Artefakt.

Beleg: `/CLAUDE.md`, `/SECRETS.md`, `/tools/ds-lint.py`, `/services/` und
`/reference/` antworten mit 200, obwohl der Workflow genau diese Ordner
aussen vor laesst. Umgekehrt fehlen die vom Workflow **erzeugten** Dateien —
die Kurz-Adressen `/‹slug›/` aus `tools/build_tool_aliases.py` waren live nie
erreichbar (404), obwohl sie in jedem Artefakt liegen. Genau daran starb der
Teilen-Link der Logoseite.

**Solange das so ist, gilt:** was live erreichbar sein soll, muss **im Branch
liegen**. Darum sind die Kurz-Adressen als Weiterleitungs-Stubs eingecheckt
(`logo-generator/`, `qr-generator/`, `kurzlink/`, `gtv-naming/` — neben den
laengst eingecheckten Abschnitts-Pfaden `logo/`, `signatur/`, `karten/` …).
Neu erzeugen laesst sich der Satz reproduzierbar mit:

    python3 tools/build_tool_aliases.py .

**Offen (Entscheidung des Auftraggebers):** Pages-Quelle in den
Repository-Einstellungen von ‹Deploy from a branch› auf ‹GitHub Actions›
umstellen. Dann gilt wieder, was der Workflow beschreibt — das kuratierte
Bundle — und `docs/`, `tools/`, `workers/`, `services/`, `reference/`,
`collections/` verschwinden aus dem Web. Bis dahin ist das Repository
oeffentlich lesbar.

## Noch bewusst nicht in diesem kleinen Merge

- grosse Script-Sammlungen
- Schriften-Downloads und lokale Output-Bestaende
- Service-Code fuer Brand Portrait und `gtv-subs`
- grosse Icon-Pakete jenseits der fuer Karten/Cover noetigen Minimalassets

## Repos daneben

- `goeloggen` - Goetheanum-Tools
- `publicsecrets` - eigenes Repo fuer Public Secrets
- `personal-finance` - eigenes Repo fuer Finance
