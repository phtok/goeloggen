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
- `apps/schriften/`

### Services

Nicht-statische Unterprojekte liegen unter `services/`:

- `services/brand-portrait/`
- `services/gtv-subs/`

### Collections

Materialsammlungen und Produktionsquellen liegen unter `collections/`:

- `collections/jahrgaenge/`

### Gemeinsam genutzt

- `assets/` - gemeinsame Schriften, Icons, Maps, SVGs und Vendor-Dateien
- `scripts/` - Build-, Release- und Produktionsskripte
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
- `schriften.html` -> `apps/schriften/`
- `index-cover-generator.html` -> `cover-generator.html`
- `index-goelogger-gci1.html` -> `logo-generator.html`

Damit bleiben alte Links stabil, waehrend die eigentlichen Apps klar in Ordnern liegen.

## Jahrgaenge

Die Sammlung der Zeichnungen und Texte aus den Jahrgaengen ist kein einzelnes Webtool.

Vorgesehener Ort:

- `collections/jahrgaenge/pdfs/`
- `collections/jahrgaenge/zeichnungen/`

Die zugehoerigen Verarbeitungsskripte bleiben unter `scripts/`.

## Was aktuell online bleibt

Der GitHub-Pages-Workflow publiziert weiter nur den stabilen oeffentlichen Satz:

- Logo-Generator
- Visitenkarten-Generator
- gemeinsame `assets/`

Das reduziert Risiko fuer laufende Veroeffentlichungen, obwohl die Repo-Struktur intern bereits aufgeraeumt ist.

## Repos daneben

- `goeloggen` - Goetheanum-Tools
- `publicsecrets` - eigenes Repo fuer Public Secrets
- `personal-finance` - eigenes Repo fuer Finance
