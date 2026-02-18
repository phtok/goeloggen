# Goetheanum Logo Generator

Ein interaktiver Web-Generator für Logos aller Goetheanum-Sektionen und -Organisationen.

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

## Verwendung

1. `index.html` in Browser öffnen
2. Organisation auswählen
3. Layout, Sprache und Farben anpassen
4. Größe einstellen
5. Als SVG/PNG/JPG exportieren

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

## GitHub Pages Deployment

Die Website kann direkt über GitHub Pages bereitgestellt werden.

### Was wird veröffentlicht

- `index.html` (Logo-Generator)
- `index-visitenkarten-onepager.html` (Visitenkarten-Tool)
- `assets/` (Schriften, Glyphen, Logos)

Der Deploy-Workflow liegt in:

- `.github/workflows/deploy-pages.yml`

### Einmalig im GitHub-Repo aktivieren

1. GitHub Repo öffnen: `Settings -> Pages`
2. Bei `Build and deployment` als Source `GitHub Actions` wählen
3. Auf `main` pushen (oder Workflow manuell via `Actions` starten)
