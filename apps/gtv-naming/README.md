# GTV Naming – interaktive Renderings

Präsentationswerkzeug für die Umbenennung von Goetheanum TV. Eine einzige
selbsttragende HTML-Datei: realistischer Nachbau der goetheanum.tv-Startseite
(Stand Juni 2026) mit umschaltbarer Wortmarke für alle Namenskandidaten.

## Integration in goeloggen

Zielpfad: `apps/gtv-naming/index.html`
→ URL: https://phtok.github.io/goeloggen/apps/gtv-naming/

Optional in der goeloggen-Übersicht/Startseite verlinken (neben Logo-Generator).

## Bedienung (Presenter-Leiste oben)

- **Pillen** = Namenskandidaten; Klick wechselt, **×** scheidet aus, **↺** holt alle zurück.
  Der letzte verbliebene Kandidat ist nicht entfernbar.
- **„+ Vorschlag"-Feld**: neuen Namen eintippen, Enter → wird als Kandidat
  ergänzt und sofort gerendert. Die vollständige IANA-TLD-Liste ist
  eingebettet (`const TLDS`, tlds-alpha-by-domain.txt, Version 2026-06-12,
  1286 ASCII-Einträge) – jeder Vorschlag wird sofort korrekt als „eigene TLD
  möglich" oder „Subdomain" eingestuft, und die Punkt-Sonderform schaltet
  sich bei echter TLD frei (z. B. io, study, stream, video, live).
  Hinweis: „TLD existiert" heisst nicht automatisch „frei registrierbar" –
  einzelne TLDs sind marken- oder branchengebunden.
- **Pfeil-Knöpfe ‹ ›** (und Pfeiltasten der Tastatur): schnell durch die
  verbliebenen Kandidaten blättern.
- **Sonderform mit Punkt**: Kreis-Icon + „.name" (nur bei Kandidaten mit echter
  TLD wirksam, z. B. tv, studio, online, media).
- **Icon (offene Form)**: schaltet den Zweizeiler vom Kreis-Icon (Default)
  auf das offene Icon um.
- **Kurzform**: zeigt nur den Zusatznamen neben dem Icon, ohne die
  „Goetheanum"-Zeile (z. B. Icon + „Studio"). Hat Vorrang vor Zweizeiler
  und Punkt-Sonderform; das gewählte Icon (Kreis/offen) gilt auch hier.
- **iPhone**: schwebende Mobilvorschau unten rechts, synchron zum Hauptzustand,
  mit drei Modi: **Web** (iframe derselben Datei mit `#embed`, Sync via
  postMessage), **Splash** (App-Startbildschirm: Kreis-Icon + Kandidat auf
  Schwarz) und **App** (Home-Screen-Nachbau der GTV-iOS-App mit vollem Namen
  im Header, Pillen, Skeleton-Inhalten und Tabbar).
- **▾-Knopf** (links in der Leiste): klappt die Presenter-Leiste auf eine
  schmale Zeile zusammen – nützlich auf dem iPhone, wo die volle Leiste
  sonst die halbe Sicht nimmt.
- **PNG**: speichert das aktuell gezeigte Logo (Zweizeiler, Sonderform, tv
  oder Kurzform – inkl. gewählter Icon-Form) als transparentes PNG, hochauflösend
  und ohne externe Bibliothek (Standalone-SVG → Canvas). Die Sonderform/tv wird
  dabei in den Goetheanum-Glyphen gesetzt – konsistent zum Zweizeiler-Zusatz,
  nicht in der Bildschirm-Näherung Titillium Web. Auf dem iPhone öffnet Safari
  das Bild ggf. in einem neuen Tab; dort per Tippen-und-Halten sichern.
- **Speichern**: eigene Vorschläge, ausgeschiedene Kandidaten, Auswahl und
  Toggle-Zustände werden automatisch in `localStorage` gesichert und beim
  Neuladen wiederhergestellt (pro Browser/Gerät). Einen eigenen Vorschlag
  dauerhaft löschen: mit **×** ausscheiden und neu laden – ausgeschiedene
  Vorschläge werden nicht mitgespeichert. **↺** holt nur die
  Standard-Kandidaten der laufenden Sitzung zurück.

## Architektur-Notizen

- Logosystem (SIGNET-, POINT-Pfade, GL-Glyphensatz mit 130 Zeichen, Satzlogik
  `logoZweizeiler`/`logoSonderform`) ist aus
  `apps/logo-generator/` **dupliziert** (Stand Juni 2026).
  Sinnvoller Refactor: gemeinsame Konstanten nach `assets/` auslagern und in
  beiden Apps importieren, damit Glyphen-/Pfadänderungen nur einmal gepflegt
  werden.
- Kandidatenliste: `const CANDIDATES` im Script (label, word, l2, tld,
  dom, sub, name). tld: true = echte TLD existiert, false = nur Subdomain,
  null = ungeprüft.
- Farben: TV-Blaugrau `#23323F` (Primärfarbe aus den GTV-Site-Settings),
  Zeile 1 des Zweizeilers `#575756`. Schrift: Titillium Web (Google Fonts),
  Hausschrift der GTV-Plattform.
- Hero-Slides: echte Screenshots der Live-Site (Juni 2026), als JPEG-Base64
  eingebettet → Datei ist offline lauffähig bis auf:
  - 4 Reihen-Cover (live von alpha.uscreencdn.com)
  - Titillium Web (Google Fonts)
  Für volle Offline-Fähigkeit: Cover lokal ablegen, Font self-hosten.

## Nutzungsstatistik

Die Live-Site (nur `phtok.github.io`, nicht das Embed-iframe und nicht
lokal) sendet anonyme Events an Supabase (Projekt „Public Secrets App",
Tabelle `gtv_naming_events`, Insert-only per Publishable Key, RLS ohne
Lese-Recht für Besucher):

- `visit` (Referrer, Sprache, Bildschirm, mobil ja/nein),
  `heartbeat` alle 30 s bei sichtbarem Tab, `leave` mit aktiver Gesamtzeit
  → Besucherzahl und Verweildauer
- `suggestion` (eingegebenes Wort + TLD-Einstufung) → was Nutzer vorschlagen
- `interaction` (Kandidatenwahl, ×/↺, Toggles, iPhone-Modi) → womit gespielt wird

Keine Cookies, keine personenbezogenen Daten; Session-ID ist zufällig und
lebt nur im `sessionStorage`. Auswertung über die Views `gtv_naming_tage`,
`gtv_naming_verweildauer` und `gtv_naming_vorschlaege` im
Supabase-Dashboard (SQL-Editor).

## Offene Aufgaben (Vorschläge)

1. Refactor: Logo-Konstanten mit logo-generator teilen (s.o.).
2. TLD-Liste (`const TLDS`) gelegentlich gegen
   https://data.iana.org/TLD/tlds-alpha-by-domain.txt aktualisieren.
