# Goetheanum Tools

Dieses Repository enthaelt nur noch Goetheanum-Projekte.

## Schnellueberblick

### Apps

Statische Onepager liegen unter `apps/`:

- `apps/logo-generator/`
- `apps/visitenkarten-generator/`
- `apps/briefschaften/`
- `apps/karten-generator/`
- `apps/cover-generator/`

### Services

Nicht-statische Unterprojekte sind unter `services/` bereits vorgesehen:

- `services/brand-portrait/`
- `services/gtv-subs/`

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

- `index.html` -> `logo-generator.html`
- `logo-generator.html` -> `apps/logo-generator/`
- `visitenkarten.html` -> `visitenkarten-generator.html`
- `visitenkarten-generator.html` -> `apps/visitenkarten-generator/`
- `briefschaften.html` -> `apps/briefschaften/`
- `karten.html` -> `karten-generator.html`
- `karten-generator.html` -> `apps/karten-generator/`
- `cover-generator.html` -> `apps/cover-generator/`
- `index-cover-generator.html` -> `cover-generator.html`
- `index-goelogger-gci1.html` -> `logo-generator.html`

Damit bleiben alte Links stabil, waehrend die eigentlichen Apps klar in Ordnern liegen.

## Jahrgaenge

Die Sammlung der Zeichnungen und Texte aus den Jahrgaengen ist kein einzelnes Webtool.

Vorgesehener Ort:

- `collections/jahrgaenge/pdfs/`
- `collections/jahrgaenge/zeichnungen/`

Die zugehoerigen Verarbeitungsskripte und groesseren Datensammlungen folgen spaeter in separaten Merges.

## Was aktuell online bleibt

Der GitHub-Pages-Workflow publiziert weiter nur den stabilen oeffentlichen Satz:

- Logo-Generator
- Visitenkarten-Generator
- gemeinsame `assets/`

Das reduziert Risiko fuer laufende Veroeffentlichungen, obwohl die Repo-Struktur intern bereits aufgeraeumt ist.

## Noch bewusst nicht in diesem kleinen Merge

- grosse Script-Sammlungen
- Schriften-Downloads und lokale Output-Bestaende
- Service-Code fuer Brand Portrait und `gtv-subs`
- grosse Icon-Pakete jenseits der fuer Karten/Cover noetigen Minimalassets

## Repos daneben

- `goeloggen` - Goetheanum-Tools
- `publicsecrets` - eigenes Repo fuer Public Secrets
- `personal-finance` - eigenes Repo fuer Finance
