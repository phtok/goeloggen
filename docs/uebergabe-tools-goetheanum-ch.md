# Übergabe-Brief: UTM-Link-Kürzer auf tools.goetheanum.ch

*Für eine neue Claude-Code-Session auf einem eigenen Repo. Dieser Brief ist
selbsttragend — er setzt kein Wissen aus früheren Sitzungen voraus.*

## Auftrag

Baue einen **Link-Kürzer für UTM-Links** als neues Werkzeug der Goetheanum-
Werkzeugfamilie. Kurzadresse: `tools.goetheanum.ch/<slug>` → leitet auf die
lange Ziel-URL samt UTM-Parametern weiter. Dazu eine kleine Oberfläche zum
**Komponieren** (Ziel-URL + utm_source/medium/campaign eintragen → Kurzlink
entsteht) und eine **Übersicht** der bestehenden Kurzlinks.

## Domain — Stand und Inbetriebnahme

- DNS ist **fertig**: `tools.goetheanum.ch` zeigt bereits per CNAME auf
  `phtok.github.io`. Es beansprucht sie nur noch kein Repo (darum 404).
- Inbetriebnahme: neues Repo **unter dem Account `phtok`** anlegen (Vorschlag:
  `phtok/goelinks`), GitHub Pages aktivieren, dann Settings → Pages →
  **Custom domain: `tools.goetheanum.ch`** eintragen (erzeugt die
  `CNAME`-Datei) und nach Zertifikat **Enforce HTTPS** setzen. Läuft in Minuten.
- Wichtig, falls ein Deploy-Workflow gebaut wird: die `CNAME`-Datei muss im
  veröffentlichten Artefakt liegen (Vorbild: `deploy-pages.yml` in
  `phtok/goeloggen` kopiert sie mit).

## Architektur (statisch, GitHub Pages — kein Server)

Empfohlenes Muster, zweistufig:

1. **`links.json` als Quelle der Wahrheit** im Repo:
   `{ "slug": { "url": "https://…", "label": "…", "angelegt": "2026-07-06" } }`.
2. **Weiterleitung über `404.html`**: GitHub Pages liefert für unbekannte Pfade
   die `404.html` aus. Dort liest ein kleines Skript den Slug aus
   `location.pathname`, schlägt in `links.json` nach und leitet per
   `location.replace()` weiter. Vorteil: **neue Links brauchen nur einen
   Eintrag in links.json**, keine Seitengenerierung.
   - Optionale Härtung für die wichtigsten Links: zusätzlich statische
     `/<slug>/index.html` mit `<meta http-equiv="refresh" content="0;url=…">`
     + `rel="canonical"` (funktioniert ohne JavaScript). Ein kleines
     Generator-Skript (`tools/build_links.py`) kann diese aus links.json
     erzeugen — idempotent.
3. **Klickzählung** nach dem Hausmuster von werkzeuge.goetheanum.ch: eigener
   Supabase-Endpoint, **keine Cookies, keine IP-/Personendaten**, nur
   `bump(kind, label)` mit dem Slug (Vorbild: der `schriften_bump`-Block am
   Ende von `icons.html` im Repo `phtok/goeloggen`).
4. **Komponier-Oberfläche** (`index.html`): Formular Ziel-URL + UTM-Felder,
   erzeugt den langen Link, schlägt einen Slug vor, zeigt den fertigen
   `links.json`-Eintrag zum Übernehmen (v1: Eintrag wird per Commit/PR
   gepflegt — bewusst ohne Schreib-Backend). QR-Code des Kurzlinks als
   Bonus (client-seitig generierbar).

## Gestalt — verbindlich (Goetheanum-Design-System)

Das Werkzeug gehört zur Familie von `werkzeuge.goetheanum.ch`
(Repo `phtok/goeloggen`, öffentlich). Es gilt:

- **Vom Starter ausgehen:** `design-system/starter.html` aus `phtok/goeloggen`
  als Ausgangspunkt kopieren.
- **Einbinden statt kopieren:** `tokens.css`, `base.css` (und bei Bedarf
  `nav.css`/`nav.js`) per `<link>` **absolut** von
  `https://werkzeuge.goetheanum.ch/design-system/…` einbinden (GitHub Pages
  sendet `Access-Control-Allow-Origin: *`, Webfonts laden also auch
  cross-origin). Keine eigenen Farb-, Schnitt- oder Abstandswerte erfinden —
  nur Tokens (`var(--gold)`, `var(--s6)`, `var(--w-deutlich)` …).
- **Hausregeln lesen und befolgen:** `CLAUDE.md` im Repo `phtok/goeloggen`
  (Typografie G01/G03/G05/G23/G25, Barrierefreiheit B01–B05, Struktur
  DS01–DS07). Beim Gestalten die betroffenen Regel-IDs nennen. Kernpunkte:
  Fließtext ≥16 px, nichts Lesbares unter 14 px, Kontraste rechnen (≥4.5:1),
  Fingerziele ≥44 px, kein Versal/Sperren/Unterstreichen als Betonung,
  Hell/Dunkel nur über die Tokens.
- **Schrift-Grenze:** Titel/Kicker/Lede in der Hausschrift «Goetheanum»;
  Label, Werte, Formularfelder, Tabellen in Source Sans 3 (`--font-text`) —
  das erledigt `base.css` bereits.

## Anschluss an die Familie

- Nach dem Livegang einen Eintrag in `tools.json` von `phtok/goeloggen`
  ergänzen (Kategorie `generatoren`, externes `href`
  `https://tools.goetheanum.ch/`), damit das Werkzeug im Hub und im Menü
  erscheint. Das kann diese Session per PR im goeloggen-Repo tun, sofern es
  in ihrem Zugriff liegt — sonst als Hinweis an den Auftraggeber zurückgeben.

## Abnahmekriterien

1. `tools.goetheanum.ch` liefert die Komponier-Oberfläche im Hausbild
   (Tokens, Hausschrift, Hell/Dunkel funktioniert).
2. Ein Testeintrag in `links.json` leitet unter
   `tools.goetheanum.ch/<slug>` korrekt weiter (mit UTM-Parametern intakt).
3. Klicks werden gezählt (ohne Cookies/Personendaten); ein Zähler ist in der
   Übersicht sichtbar oder abrufbar.
4. Kontraste gerechnet, keine Schrift unter 14 px, Fokus sichtbar,
   `lang="de"` gesetzt.
5. Kurzer README-Abschnitt: wie ein neuer Kurzlink angelegt wird
   (links.json-Eintrag), wie der Slug-Stil lautet (klein, bindestrich, kurz).

## Kontakt/Kontext

Auftraggeber: Philipp Tok. Referenz-Repo mit Design-System, Hausregeln und
allen Mustern: `github.com/phtok/goeloggen` (live:
`werkzeuge.goetheanum.ch`). Der Webfamilie-Befund
(`docs/webfamilie-befund.md` dort) erklärt die größere Strategie, in die
dieses Werkzeug sich einfügt.
