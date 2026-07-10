# Webfamilie-Befund: Was das Design-System von den vier grossen Goetheanum-Seiten lernt — und sie von ihm

Stand: 6. Juli 2026 · Untersucht: goetheanum.ch · dasgoetheanum.com · goetheanum.tv ·
anthroposophie.org (Roh-HTML/CSS ausgewertet, Kontraste gerechnet, nicht geschätzt).

## 1 · Kurzbild je Seite

| Seite | Unterbau | Stimme (Schrift) | Zustand |
|---|---|---|---|
| goetheanum.ch | Craft CMS, 4 Sprachen, Bild-CDN `static.goetheanum.ch` | Titillium (Titel) + Source Sans Pro (Text), 11 statische Einzeldateien | reifster Betrieb, null Token-Disziplin |
| dasgoetheanum.com | WordPress + Zeen, Leaky Paywall, WPML (DE/EN) | Fazeta Sans, nur 2 Schnitte → Faux-Bold/-Kursiv | reifste Artikelseite, schwächste Typo-Basis |
| goetheanum.tv | Uscreen (gemietet), Tailwind | Titillium per `!important` über Inter geflickt | kompletter Medienkatalog, keine Marke in der Palette |
| anthroposophie.org | Craft CMS auf ~12 Jahre altem Gratis-Template | Titillium + Yrsa; 2 deklarierte Schriften laden nie | 4 Sprachausgaben — und `noindex` auf der Startseite |

Überraschungen: anthroposophie.org ist keine Wissensseite, sondern die Online-Ausgabe von
«Anthroposophie Weltweit» (Schwester der Wochenschrift, Assets von `static.goetheanum.ch`).
Beide Craft-Seiten teilen bereits Infrastruktur (`static.goetheanum.ch`, `login.goetheanum.ch`)
— die Familie hat gemeinsame Leitungen, nur keine gemeinsame Gestalt.

## 2 · Querschnittsbefund

Die Familie spricht mit vier Stimmen — und tastet dabei längst nach derselben: drei der vier
Seiten greifen zu Titillium. Die Hausschrift «Goetheanum» ist die zu Ende gebaute Titillium
(Urbino-Basis, v2.7, echte Schnitte 190–725). Die Familie sucht die Stimme, die fertig im
Regal liegt.

Dasselbe beim Gold: `#ebb565` (.ch), `#B19F7C` (.org), `#ac9f84` (Wochenschrift, marginal),
unser `#d7ab68`/`#94702e`. Das Gold existiert überall als Instinkt, nirgends als Token.
Verwandte Tinten: `#37404c` (.ch), `#23323F` (.tv), unser `#23272b`.

Alle vier scheitern an identischen Stellen — exakt dort, wo unser System per Konstruktion prüft:

| Systemfehler | .ch | Wochenschrift | .tv | .org | bei uns |
|---|---|---|---|---|---|
| Fokus unterdrückt | 15× `outline:none` | `outline:0!important` | kein `:focus-visible` | global | Fokus-Defaults |
| Text unter 14 px | 12.5–13 (Kalender) | 12er-Versal-Bylines | 12–14 | 11–12 | B03-Floor |
| Kontrast-Fails | Gold+Weiss 1.85:1 | Grenzfälle | Grau 3.67:1 | Weiss/Gelb 1.6:1 | B01/B02 gerechnet |
| Zeilenhöhe Lesetext | 1.4 | 1.4 | — | ~1.43 | 1.6/1.66 |
| Tokens | ~0 | 0 | Anbieter-Tokens, überflickt | 1 | eine Quelle |
| Dark Mode | nein | toter Restcode | ja (Plattform) | nein | `data-theme` |
| Prüfung/Score | — | — | — | `noindex`! | ds-lint |

## 3 · Was UNS fehlt (Komponenten-Lücken)

Die Schwäche liegt spiegelverkehrt: die anderen haben Inhaltsarchitektur ohne System, wir
haben System ohne Inhaltsarchitektur.

1. **Artikel-Anatomie** (Breadcrumb → Kicker → Titel → Byline → Lede → Langtext →
   Literatur → Autoren-Bio → Verwandtes) — wir haben `.prose`, keine kanonische Artikelseite.
2. **Teaser-Hierarchie** (Bild + Kicker + Titel + Vorspann + Meta, 2–3 Gewichtsstufen).
3. **Veranstaltungs-Karte + Filterleiste** (Vorbild .ch: Freitext/Zeitraum/Typ/Veranstalter, ICS).
4. **Medien-Kachel + Reihen-Karussell** (Poster, Titel, Dauer; Dunkel-Katalogfläche) — auch
   für die geplanten Videoreihen.
5. **Formularstrecken**: Newsletter, Mitglied/Spenden-Funnel, Such-Overlay.
6. **Personen-/Kontaktkarten**, **Footer-Architektur** (7-Block-Footer von .ch als Vorbild),
   Pagination/Load-More.
7. **Mehrsprachigkeit als Muster**: `lang`/`hreflang`, Umschalter, `/de|en|fr|es/`-Schema.
8. **Lese-Betriebsdaten**: Lesezeit, Fortschritt, Weiter/Zurück (Wochenschrift).

## 4 · Übernehmen — je Quelle

- **Wochenschrift:** die Artikel-Kette als `starter-artikel.html` — mit unseren Faktoren
  (lh 1.66 statt 1.4, ~62ch statt ~78, echte Schnitte statt Faux-Bold, Byline normal statt
  12px-Versal). Ausgabe-Tags als Print↔Web-Brücke.
- **goetheanum.ch:** Event-Karten-Muster samt Filtergrammatik und ICS; Bild-Transform-Disziplin.
- **goetheanum.tv:** Medien-Kachel, Reihen-Karussell, `hero-theme`-Attribut je Banner;
  Idee «abgeleitete Töne per Formel» (muted/subtle aus Grundfarbe errechnet) für tokens.css.
- **anthroposophie.org:** designseitig nichts; das 4-Sprachen-URL-Schema als Anforderung —
  und als Mahnbild: ohne Maschine prüft niemand (`noindex`, Phantom-Schriften, 574× `alt="Image"`).

## 5 · Wo unsere Lösungen deutlich brauchbarer sind (belegt)

(a) Barrierefreiheit als Konstruktion — jede der vier Seiten würde bei `ds-lint` Dutzende
Treffer mit Regel-ID + Zeile ernten. (b) Variable Font mit echten Graden gegen Faux-Bold auf
drei von vier Seiten. (c) Token-Schicht mit Hell/Dunkel — existiert sonst nirgends.
(d) Selbst-Hosting — .tv/.org laden Google Fonts extern (Datenschutz). (e) Die
Konformitäts-Engine selbst — im ganzen Feld kein einziges Prüfinstrument. (f) Der
Icon-Font-Ansatz ist extern validiert (Wochenschrift nutzt dasselbe Muster «tipi», nur
unsystematisch).

## 6 · Alle ausstatten? Ja — geschichtet

Das Fundament ist CMS-agnostisches CSS + woff2:

- **Craft** (.ch, .org): Template-Partial bindet tokens.css/base.css ein; Verteilung über das
  bereits gemeinsame `static.goetheanum.ch`.
- **WordPress** (Wochenschrift): Child-Theme existiert (`zeen-child`) — ein Enqueue.
- **Uscreen** (gtv): Betreiber injiziert heute schon Custom-CSS — derselbe Kanal trägt Tokens.

Grenzen: Wir ersetzen nicht CMS, Paywall oder OTT-Plattform — wir statten aus. Die Hausschrift
auf goetheanum.ch ist eine Markenentscheidung, kein CSS-Patch.

## 7 · Die Sichthöhe: Fundamentschicht der Goetheanum-Webfamilie

Vier Stufen, jede einzeln wertvoll:

1. **Stimme** — die Schriften als Paket (woff2 + fertige `@font-face`-Schnipsel existieren).
   Niedrigste Schwelle, grösste Markenwirkung; die Titillium-Affinität macht den Übergang weich.
2. **Fundament** — tokens.css/base.css als versioniertes, gehostetes Artefakt mit drei
   Adaptern (Craft-Partial, WP-Enqueue, Uscreen-CSS). Der Beschluss-Ledger wird zum
   Gedächtnis der Familie.
3. **Komponenten** — die Lücken aus Abschnitt 3 schliessen, entlang der real existierenden
   Bedürfnisse der vier Seiten.
4. **Vertrag** — die Engine nach aussen wenden: `ds-lint` je Site als Konformitätsbericht
   mit Score. «Wie weit weg ist goetheanum.ch?» wird eine Zahl.

## 8 · Nächste Schritte

1. `starter-artikel.html` — Artikel-Anatomie mit unseren Regeln (grösste eigene Lücke).
2. Komponenten-Lücken in base.css + Showroom (Teaser, Event, Medienkachel, Formular,
   Person, Footer).
3. «Fundament-Paket v1»: versioniertes tokens+base+fonts-Bündel mit den drei
   Adapter-Schnipseln.
4. Vier-Seiten-Konformitätsbericht (`ds-lint` extern) als Gesprächsgrundlage mit den
   Betreibern.
