# Baustelle: Goetheanum-Grafik neu zusammengesetzt

Hier entsteht die einheitliche Umgebung für alle Grafik-Werkzeuge. Ziel ist,
die **Corporate Identity des Goetheanum zu definieren und durch einfache
Werkzeuge durchzusetzen** – die laufenden Tools (Logo, Signatur, Schriften …)
bleiben währenddessen unter ihren bisherigen Adressen in Betrieb.

## Bausteine

- **`design-system/tokens.css`** – eine Quelle für Farben, Typo, Abstände,
  Radien und die Hausschrift. Jedes Tool bindet sie ein und ist allein durch
  Wiederverwendung im Hausbild.
- **`design-system/tokens.json`** – dieselben Werte maschinenlesbar (DTCG),
  für Dokumentation und spätere Prüfwerkzeuge.
- **`design-system/base.css`** – gemeinsame Komponenten (Kopf-/Fusszeile,
  Abschnitte, Karten, Knöpfe, Formularfelder), extrahiert aus dem reifsten
  Tool (Signatur-Generator).
- **`tools.json`** (im Repo-Root) – das **Manifest aller Werkzeuge**. Einzige
  Liste; die Übersicht rendert sich daraus selbst.
- **`start/index.html`** – die neue Übersicht. Während der Baustellenzeit
  erreichbar unter `…/goeloggen/start/`. Die Wurzel (`index.html`) bleibt
  vorerst die Weiterleitung zum Logo-Generator.

## Ein Werkzeug hinzufügen

Einen Eintrag in `tools.json` ergänzen:

```json
{ "slug": "mein-tool", "cat": "generatoren", "status": "entwurf",
  "tag": "Kategorie", "title": "Mein Tool", "href": "../mein-tool.html",
  "desc": "Kurzbeschreibung." }
```

`status`: `live` (im Einsatz), `beta` (nutzbar, in Arbeit) oder `entwurf`.
Pfade sind relativ zu `start/`. Mehr Code ist für die Übersicht nicht nötig.

## Ein bestehendes Tool ins Design-System heben

Im `<head>` des Tools einbinden – statt eigener `:root`-Variablen:

```html
<link rel="stylesheet" href="../design-system/tokens.css" />
<link rel="stylesheet" href="../design-system/base.css" />
```

Danach das tool-spezifische CSS auf die Tokens (`var(--blue)`, `var(--s4)` …)
umstellen. Solange ein Tool nicht migriert ist, läuft es unverändert weiter.

## Migrationsplan

1. **Deploy vereinheitlicht** – nur noch ein Pages-Workflow (erledigt).
2. **Design-System + Übersicht** als Baustelle (dieser Stand).
3. Tool für Tool aufs Design-System heben; alte URL bleibt bis zum Ersatz.
4. Wenn alles steht: Wurzel-Weiterleitung auf die Übersicht umlegen, alte
   Links als Aliasse behalten.

## Stack

GitHub Pages (Hosting) · Supabase (anonyme Statistik) · Cloudflare Worker +
Resend (nur Visitenkarten-Mailversand). Vercel ist derzeit nicht im Einsatz.
