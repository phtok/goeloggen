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
- **iPhone**: schwebende Mobilvorschau unten rechts, synchron zum Hauptzustand
  (iframe derselben Datei mit `#embed`, Sync via postMessage).

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

## Offene Aufgaben (Vorschläge)

1. Refactor: Logo-Konstanten mit logo-generator teilen (s.o.).
2. TLD-Liste (`const TLDS`) gelegentlich gegen
   https://data.iana.org/TLD/tlds-alpha-by-domain.txt aktualisieren.
3. Optional: Zustand (ausgeschiedene Kandidaten, neue Vorschläge) in
   localStorage persistieren, damit eine Sitzung wiederaufgenommen werden kann.
4. Optional: Export-Knopf „aktuelle Ansicht als PNG" (html2canvas o.ä.).
