# Goetheanum Tools

Sammlung von Goetheanum-Grafiktools, Produktionshilfen und Referenzmaterial.

## Features

- **34 Organisationen** aus 3 Kategorien
- **2 Layout-Varianten** (Desktop & Mobile)
- **4 Sprachen** (DE, EN, FR, IT)
- **5 Farbvarianten** + Custom Colors
- **Live-Preview** mit Größenregler
- **Export** als SVG, PNG, JPG

## Technische Details

- Pure HTML/CSS/JavaScript (keine Dependencies)
- Embedded Font (Titillium Upright)
- Text-to-Path Konvertierung für konsistente SVG-Exports
- Responsive Design (Desktop & Mobile)
- Alle Glyphen für deutsche und englische Texte

## Aktive Tools

- `index.html` - Logo-Generator
- `visitenkarten.html` - Visitenkarten-Generator
- `briefschaften.html` - Briefschaften
- `karten.html` - Karten-Generator
- `cover-generator.html` - TV Cover Generator
- `tools/brand-portrait/` - Brand-Portrait-Generator

## Repo-Struktur

- `assets/` - gemeinsame Schriften, Glyphen, Logos, Vendor-Dateien und Cutouts
- `workers/` - Cloudflare-Worker und Deploy-Helfer
- `scripts/` - Build-, Release- und Produktionsskripte
- `tools/` - eigenständige Unterprojekte wie Brand-Portrait und `gtv-subs`
- `reference/` - Referenzstände, Altfassungen, Pflichtenhefte und Konzeptmaterial
- `docs/specs/` - Spezifikationen, die zu aktiven Goetheanum-Tools gehören
- `archive/` - archivierte Altversionen und Experimente
- `hefte_pdf/`, `ausgabe_zeichnungen/` - Jahrgangs-PDFs und extrahierte Zeichnungsdaten

## Organisationen

### Freie Hochschule für Geisteswissenschaft
- Allgemeine Anthroposophische Sektion
- Jugendsektion
- Medizinische Sektion
- Naturwissenschaftliche Sektion
- Pädagogische Sektion
- Sektion für Redende und Musizierende Künste
- Sektion für Schöne Wissenschaften
- Sozialwissenschaftliche Sektion

### Anthroposophische Gesellschaft
- [21 weitere Organisationen]

### Sonstige
- [5 weitere Organisationen]

## Lizenz

© 2024 Goetheanum

## Entwicklung

Entwickelt für die digitale Markenführung des Goetheanum.

## Zeichnungen und Jahrgaenge

Die Sammlung der Zeichnungen und Texte aus den Jahrgaengen ist kein einzelnes Webtool, sondern eine Produktionspipeline:

- Rohdaten: `hefte_pdf/`
- extrahierte Zeichnungen und HTML-Ausgaben: `ausgabe_zeichnungen/`
- Pipeline-Skripte: `scripts/`

## Spezifikationen

- Pflichtenheft Campus-Kartentool: `docs/specs/campus-kartentool-pflichtenheft.md`

## GitHub Pages Deployment

Die Website kann direkt über GitHub Pages bereitgestellt werden.

### Was aktuell ueber GitHub Pages veroeffentlicht wird

- `index.html` (Logo-Generator)
- `visitenkarten.html` (Visitenkarten-Tool)
- `assets/` (Schriften, Glyphen, Logos)

Weitere Tools liegen im Repo, sind aber im aktuellen Workflow noch nicht im Pages-Bundle:

- `cover-generator.html`
- `briefschaften.html`
- `karten.html`

Rueckwaertskompatibilitaet:

- `index-cover-generator.html` leitet auf `cover-generator.html` weiter
- `index-goelogger-gci1.html` leitet auf `index.html` weiter

Alte Einstiegsdateien liegen unter:

- `archive/legacy-entrypoints_2026-03-10/`

Optional für E-Mail-gesteuerte Visitenkarten-Downloads:

- `assets/vk-email-config.js` (Endpoint-Konfiguration)
- `workers/visitenkarten-email-worker.js` (Cloudflare Worker)

Der Deploy-Workflow liegt in:

- `.github/workflows/deploy-pages.yml`

### Einmalig im GitHub-Repo aktivieren

1. GitHub Repo öffnen: `Settings -> Pages`
2. Bei `Build and deployment` als Source `GitHub Actions` wählen
3. Auf `main` pushen (oder Workflow manuell via `Actions` starten)
