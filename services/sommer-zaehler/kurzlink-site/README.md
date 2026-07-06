# Kurzlink-Brücke für tools.goetheanum.ch

> **Referenz-Kopie.** Live betrieben wird dieser statische Stand im eigenen
> GitHub-Pages-Repo `phtok/goelinks` (eine Pages-Site trägt genau eine Custom
> Domain; `goeloggen` hält bereits `werkzeuge.goetheanum.ch`). Diese Kopie liegt
> hier versioniert neben der `go`-Function, die sie auflöst. Änderungen hier
> zusätzlich nach `phtok/goelinks` übernehmen.

Statische GitHub-Pages-Seite, die kurze Adressen der Form

```
tools.goetheanum.ch/s/<tier>
```

auf die volle Kampagnen-URL (samt UTM-Parametern) weiterleitet. Die Auflösung
macht die Supabase-Function `go` gegen die Tabelle `sommer2026_links` — die
Datenbank ist die **einzige Quelle der Wahrheit**. Dieses Repo hält bewusst
keine Link-Liste; neue Kurzlinks entstehen im Generator und wirken sofort.

## Wie ein neuer Kurzlink entsteht

Nicht hier im Repo, sondern im **UTM-Generator**:
`werkzeuge.goetheanum.ch/apps/utm-generator/` → Ziel-URL + UTM-Merkmale
eintragen, Kurznamen wählen, ins Register schreiben. Der Kurzname wird zum
Pfad `/s/<kurzname>`.

**Slug-Stil:** kurz, klein, ein zweisilbiger Tiername mit Bild (`otter`,
`biber`, `reiher` …). Menschlich abtippbar aus Bio, Caption oder Papier.

## Wie die Weiterleitung läuft

1. Aufruf `tools.goetheanum.ch/s/otter` → GitHub Pages hat keine solche Datei
   und liefert `404.html` aus.
2. Ein kleines Skript in `404.html` liest den letzten Pfadteil (`otter`) und
   ruft `…/functions/v1/go/otter` auf.
3. Die `go`-Function schlägt `otter` in `sommer2026_links` nach und antwortet
   mit `302` auf die volle Ziel-URL. Unbekannte Kurznamen landen freundlich auf
   der Aktions-Landingpage.

## Inhalt

- `index.html` — Startseite (verweist auf Generator und Cockpit).
- `404.html` — die Weiterleitungs-Brücke.
- `CNAME` — `tools.goetheanum.ch` (von GitHub Pages gesetzt).

## Gestalt

Bindet Tokens und Basis des Goetheanum-Design-Systems absolut von
`werkzeuge.goetheanum.ch/design-system/` ein — keine eigenen Farb-, Schnitt-
oder Abstandswerte. Hausregeln: siehe `CLAUDE.md` in
[`phtok/goeloggen`](https://github.com/phtok/goeloggen).
