# Megamenü für die Goetheanum-Familie: Konzept

Stand: 7. September 2026 · Frage des Auftraggebers: Von jeder Sektionsseite
und jedem Bereich zurück ins Ganze – wo platziert, was drin, wie universal?

## 1 · Empfehlung in drei Sätzen

Das Menü ist **keine Navigation der jeweiligen Seite**, sondern die **Karte
des Ganzen** – darum sitzt es **über** dem eigenen Kopf jeder Seite, als
schmale, überall gleiche **Familienzeile** (links «Goetheanum», rechts der
Öffner «Alle Bereiche»). Es zeigt **nur Titel** (Sektionen in ihrer
Sektionsfarbe, Bereiche, Medien, Dienste) und markiert, **wo man gerade
ist**. Es wird universal, weil es **eine Quelle** hat (`familie.json`) und
**ein Einbinde-Snippet** – dieselbe Mechanik wie `tools.json` → `nav.js` heute.

## 2 · Wo: die Familienzeile über dem Seitenkopf

- **Position:** ganz oben, vor dem `<header>` der Gastseite. Höhe eine
  Zeile (44 px, `--tap`), Fläche `--bar-bg`, Linie `--line`. Nicht sticky:
  die Gastseite behält ihren eigenen klebenden Kopf.
- **Warum nicht im Hauptmenü von goetheanum.ch?** Die Familie läuft auf
  vier Unterbauten (Craft, WordPress, Uscreen, Squarespace; siehe
  `webfamilie-befund.md`). Nur eine Ebene **oberhalb** aller Kopfzeilen kann
  auf jeder Seite gleich sein, ohne ein einziges CMS umzubauen.
- **Handy:** links die Wortmarke, rechts nur der Öffner. Das Menü öffnet
  als ganze Fläche (Schublade), nicht als Hover-Dropdown.
- **Auf goetheanum.ch selbst** ist die Zeile dieselbe. Der Punkt «Sektionen»
  im Hauptmenü darf dann darauf zeigen, statt eine zweite Liste zu pflegen.

## 3 · Was drin ist – nur Titel, kein Beiwerk (G03)

Das Menü koordiniert, es erklärt nicht. Vier Spalten auf breit, vier
aufklappbare Gruppen auf schmal (native `details`/`summary` wie `nav.css`):

| Gruppe | Einträge | Quelle |
|---|---|---|
| **Goetheanum** | Startseite · Veranstaltungen · Besuchen · Hochschule · Gesellschaft · Mitglied werden · Spenden | goetheanum.ch |
| **Sektionen** | die elf Sektionen der Freien Hochschule, je mit Farbpunkt in ihrer Sektionsfarbe (`--sek-*`) | `tokens.json` → `color.sektion` |
| **Bereiche** | Bühne · Bibliothek · Verlag · Archiv · Gartenpark · Empfang und weitere Bereiche (Markenblau) | `assets/goe-orgs.js` |
| **Medien & Dienste** | Wochenschrift · Goetheanum.tv · Anthroposophie Weltweit · Suche · Sprache DE/EN/FR/ES · Login | Familie |

- **Standort:** der Eintrag der aktuellen Seite trägt `aria-current="page"`
  und steht in Deutlich (`--w-deutlich`) – **eine** Auszeichnung (G01).
- **Sektionsfarbe** nur als Punkt vor dem Titel, nie als Textfarbe kleiner
  Schrift (B02) und nie als Fläche mit dunklem Text (B01).
- **Reihenfolge:** Sektionen in der Hausordnung, nicht alphabetisch; sie
  kommt aus `goe-orgs.js`, nicht aus dem Menü.
- **Kein** Beschreibungstext, keine Bilder, keine Teaser. Wer mehr will,
  klickt.

## 4 · Wie es universal wird – und ein Gewinn für alle

**Eine Quelle, ein Snippet.** `familie.json` (analog `tools.json`) hält
alle Einträge in vier Sprachen. Ein Skript `familie.js` rendert Zeile und
Menü aus dieser Datei; jede Seite bindet zwei Zeilen ein:

```html
<link rel="stylesheet" href="https://phtok.github.io/goeloggen/design-system/familie.css">
<script src="https://phtok.github.io/goeloggen/design-system/familie.js" data-lang="de" data-here="ms"></script>
```

`data-here` nennt den Schlüssel der eigenen Sektion (z. B. `ms` für die
Medizinische Sektion); daraus entsteht die Standortmarke. Ohne Skript
bleibt ein einfacher Link «Goetheanum» stehen – nichts bricht.

**Was jede Seite davon hat:**

- **Die Sektion** bekommt einen festen, sichtbaren Platz im Ganzen und
  behält ihre Identität (Farbe, eigener Kopf, eigenes CMS). Einbau kostet
  zwei Zeilen, nicht ein Redesign.
- **Das Dach** wird von jeder Unterseite aus erreichbar; Veranstaltungen,
  Spenden und Mitgliedschaft stehen überall gleich weit weg.
- **Besucherinnen und Besucher** verlieren das Ganze nie – gleich, ob sie
  über eine Suchmaschine in einer Sektion oder auf goetheanum.tv gelandet
  sind.
- **Die Pflege** ist zentral: ein Eintrag in `familie.json`, ein PR, und
  die Änderung gilt überall am selben Tag. Sektionen tragen ihre
  Einträge selbst ein (Weg über die Werkzeug-Schmiede).

**Barrierefreiheit ist eingebaut, nicht nachgeprüft:** Sprunglink,
sichtbarer Fokus, Fingerziele 44 px, Schrift ≥ 16 px, Kontraste aus den
Tokens, Hell/Dunkel über `data-theme` (B01–B05). Das ist auf allen vier
Familienseiten heute die grösste Lücke (`webfamilie-konformitaet.md`); die
Familienzeile ist das erste Stück Fundament, das dort ankommt.

## 5 · Etappen

1. **Prototyp** `design-system/familie.html` aus dem Starter, gespeist aus
   einer ersten `familie.json` (Sektionen aus `tokens.json`); zwei Breiten
   ansehen (1280 und 420), ds-lint und Barrierefreiheit messen.
2. **Ledger-Eintrag** in `design-system/CHANGELOG.md`, Eintrag in
   `tools.json` (Kategorie System).
3. **Pilot** auf einer Sektionsseite mit dem Zwei-Zeilen-Snippet, dann
   goetheanum.ch.

## 6 · Variante: schwebender Öffner unten links (Frage vom 7. 9.)

**Als Öffner ja, als Bloom-Menü nein.** Die G-Marke als schwebende Taste
unten links ist der universalste Einbau überhaupt: sie braucht keine
Kopfzeile, kein CMS, kein Layout – ein Skript, fertig. Auf dem Handy liegt
sie im Daumenbereich. Was sich aber **radial aufblühen** lässt, sind vier
bis sechs Icons – nicht elf Sektionen, ein Dutzend Bereiche und die
Medien. Icons ohne Wort sind für dieses Publikum nicht lesbar und
widersprechen dem Grundsatz «nur Titel». Darum: die Marke **öffnet**, und
was aufgeht, ist dieselbe Schublade mit Titeln wie in Abschnitt 3.

Was die schwebende Form leisten muss:

- **Beschriftet, nicht nur Icon.** Ruhend eine runde Taste (48 px,
  Markenblau, weisse Marke – B01); bei Hover und Fokus blüht sie zur Pille
  «Goetheanum» auf. So versteht man, was sie tut.
- **Fokus nie verdecken** (WCAG 2.2, SC 2.4.11): die Taste bleibt klein und
  weicht am unteren Rand aus, wenn ein fokussiertes Element darunter liegt.
- **Platz teilen:** Cookie-Banner und Chat-Widgets liegen meist unten
  rechts oder ganz unten; links unten ist frei, aber die Taste muss über
  Bannern liegen und im Druck verschwinden.
- **Bewegung nur mit Erlaubnis** (`prefers-reduced-motion`).
- **Auf dem Desktop** ist die Zeile oben die bekanntere Form; die
  schwebende Marke ist die stärkere Form für Handy und Fremdseiten.

**Entscheid für den Prototyp:** beide Öffner in einer Datei, per Schalter
umschaltbar – dieselbe `familie.json`, dieselbe Schublade. Der Auftraggeber
sieht beides und entscheidet am Blatt, nicht am Papier.

Offen für den Auftraggeber: ob die Zeile auf goetheanum.ch selbst
erscheint (Empfehlung: ja, überall gleich) oder dort im Hauptmenü aufgeht.
