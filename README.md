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

**Zwei Auslieferungen konkurrieren — das ist der Stand, nicht die Absicht.**
Auf jeden Push nach `main` laufen zwei Pages-Deployments:

1. `deploy-pages.yml` (unser Workflow) laedt das kuratierte Bundle `_site` hoch.
2. `pages-build-deployment` — der von GitHub selbst erzeugte Lauf, weil die
   **Pages-Quelle auf ‹Deploy from a branch› steht**. Er veroeffentlicht den
   **rohen Branch**, durch Jekyll gereicht.

**Der spaeter fertige Lauf gewinnt.** Beim Merge von #549 etwa war der
Branch-Lauf um 17:37:57 fertig, der Bundle-Lauf um 17:37:32 — also stand der
Branch online. An anderen Tagesstunden war es umgekehrt. Die Seite wechselt
darum ihr Gesicht, ohne dass jemand etwas aendert.

Woran man erkennt, welcher Lauf gerade oben ist (gemessen 13. August 2026):

- **Branch-Lauf oben:** `/CLAUDE.md` **und** `/CLAUDE.html` antworten mit 200
  (Jekyll wandelt Markdown mit um); alles nur im Build Erzeugte ist **404**.
- **Bundle-Lauf oben:** die Quellordner sind 404, die erzeugten Pfade 200.

**Daraus die Arbeitsregel, solange das so ist:** was live gelten soll, muss
**im Branch liegen** — dann traegt es unter beiden Laeufen. Die Abschnitts-Pfade
aus `sektionen.json` und die Kurz-Adressen `/‹slug›/` je Werkzeug sind deshalb
**eingecheckt**, nicht nur erzeugt. Neu erzeugen, wenn `sektionen.json` oder
`tools.json` sich aendern:

    python3 tools/build_sections.py .
    python3 tools/build_tool_aliases.py .

**Offen (nur der Auftraggeber kann das):** unter Settings → Pages die Quelle auf
‹GitHub Actions› stellen. Dann faellt der Branch-Lauf weg, das kuratierte Bundle
gilt allein, die Quellordner sind zuverlaessig draussen — und die eingecheckten
Weiterleitungen werden zur blossen Redundanz statt zur Notwendigkeit.

**Altlinks bleiben stehen.** Wer eine Adresse auswaerts hinterlegt hat, soll
nicht ins Leere laufen, wenn wir intern umbenennen. `apps/logo-generator/` ist
darum kein Werkzeug mehr, sondern eine Weiterleitung auf `apps/logos/` — siehe
`apps/README.md`. Umbenennen heisst hier: **die alte Adresse behalten**, nicht
ersetzen.

**Zur Vorgeschichte (13. August 2026):** dieser Abschnitt behauptete an einem Tag
zweierlei Gegenteiliges — erst ‹der Branch wird ausgeliefert›, dann ‹das Bundle
wird ausgeliefert›. Beide Messungen waren fuer sich richtig und trotzdem
irrefuehrend: es haengt davon ab, welcher der zwei Laeufe zuletzt fertig wurde.
**Lehre fuer kuenftige Messungen:** eine einzelne Abfrage beweist hier nichts.
Mehrfach messen, den Zeitpunkt notieren und gegen beide Deployment-Laeufe
halten. Und den Statuscode an der echten HTTP-Statuszeile ablesen — hinter einem
Proxy steht davor eine `200 Connection Established`, die leicht mitgezaehlt wird
und 404er als Erfolg erscheinen laesst.

## Noch bewusst nicht in diesem kleinen Merge

- grosse Script-Sammlungen
- Schriften-Downloads und lokale Output-Bestaende
- Service-Code fuer Brand Portrait und `gtv-subs`
- grosse Icon-Pakete jenseits der fuer Karten/Cover noetigen Minimalassets

## Repos daneben

- `goeloggen` - Goetheanum-Tools
- `publicsecrets` - eigenes Repo fuer Public Secrets
- `personal-finance` - eigenes Repo fuer Finance
