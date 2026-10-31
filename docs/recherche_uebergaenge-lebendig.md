# Recherche: lebendige Übergänge

Stand 31. 10. 2026. Recherche-Session (Sonnet 5.5) im Auftrag der Koordinatorin.
Grundlage ist das Leitbild des Auftraggebers
https://github.com/phtok/goeloggen/blob/spenden-befund/docs/memo-lebendige-gesten-2026-10-31.md
(Wiederholung, Polarität, Steigerung, Reduktion, Übergang; «wie die Bloom-Menüs»).
Zweck: Bewegungs-Vokabular im Fundament und neu gestaltetes Spendenformular.

**Methode.** Der Bestand ist am Stylesheet gemessen (Chromium/Playwright, Viewport
1440 px, `document.styleSheets` ausgelesen), nicht aus Bildfolgen. Die übrigen
Abschnitte stützen sich auf gelesene Seiten; drei Sonnet-Agenten haben je ein
Themenbündel gelesen. Jede Quelle ist mit URL genannt. Wo eine Seite sich nicht
lesen liess oder nur Zusammenfassungen vorlagen, steht es dabei. «Lesart» heisst:
Deutung, kein Beleg.

## § Bestand: das Bloom-Menü von goetheanum.ch

Quellen: https://goetheanum.ch und https://goetheanum.io (beide liefern dieselben
Menü-Regeln, gemessen am 31. 10. 2026).

### Klappmenü (`#navigation .sub-navigation`), die «Bloom»-Vorlage

| Merkmal | Wert |
|---|---|
| Übergang | `transition: 0.25s cubic-bezier(0.32, 0.08, 0.24, 1)` (Kurzform, also `all`) |
| Dauer auf und zu | gleich, 250 ms. Die Regel steht am Grundzustand, gilt darum in beide Richtungen |
| Zustand zu | `opacity: 0; visibility: hidden; transform: translate(-50%)` (waagrecht zentriert) |
| Zustand auf (`.main-navigation-item:hover .sub-navigation`) | `opacity: 1; visibility: visible; transform: translate(-50%, -1.5rem)` |
| Weg | 1,5 rem nach oben, auf den Auslöser zu. Das Menü sitzt bei `top: calc(100% + 1.5rem)` und steigt in seine Ruhelage |
| Höhe | wird nicht animiert (`height: auto`); es wachsen Deckkraft und Lage |
| Zeiger | `.arrow`: 1,6 rem grosses Quadrat, um 45° gedreht, `top: -0.6rem`, hängt am Menü und fährt mit |
| Fläche | weiss, `border-radius: 0.4rem`, `box-shadow: 0 0.2rem 1rem rgba(0,0,0,.3)`, `padding: 2rem` |

Die Kurve `cubic-bezier(.32,.08,.24,1)` ist ein Ease-out mit sehr langem Auslauf:
Der Start ist zügig (kleine Steigung am Anfang, dann schnell), das Ende bremst
fast bis zum Stillstand. Das Menü «blüht» nicht durch Skalierung, sondern durch
ruhiges Aufsteigen bei gleichzeitigem Einblenden.

### Weitere Bewegungen im selben Haus

| Element | Übergang |
|---|---|
| Unterstreichung der Hauptpunkte (`.main-navigation-item > a::after`) | `0.3s` (ease), `scaleX(0)` → 1: die Linie wächst von der Mitte |
| Unterstreichung im Klappmenü (`.sub-navigation > li a::after`) | `0.3s`, Breite 0 → voll |
| Kopfleiste (`#navigation`) | `0.15s`; Kopfleiste fixiert (`.headroom-fixed`): `0.5s` |
| Vollbild-Menü schmal (`.js-helm .helm-nav`) | `0.5s cubic-bezier(0.35, 0, 0.5, 1)` auf Hintergrund, Transform, Höhe, Deckkraft, Breite, Sichtbarkeit; Schiebeweg `translate3d(±100%, …)`, Blende `linear` mit `rgba(0,0,0,.5)` |
| Suchoverlay (`.search-overlay`) | zu: `0.2s`, auf (`.search--open`): `0.5s`, gleiche Kurve `cubic-bezier(0.35, 0, 0.5, 1)`. Hier ist der Eintritt länger als der Austritt |
| Filter-Auswahl Kalender (`.event-calendar__filter-dropdown`) | `0.25s ease-in-out` |
| Cookie-Schalter (iubenda) | `0.4s` |

Befunde:

1. Die Webfamilie kennt **zwei Kurven**: die weiche Bloom-Kurve (0.32,0.08,0.24,1)
   für kleine, schwebende Flächen und die ruhigere (0.35,0,0.5,1) für Flächen,
   die das ganze Blatt bewegen.
2. Das Klappmenü ist **symmetrisch** (250 ms hin, 250 ms zurück). Das Akkordeon im
   Haus (280 auf, 220 zu) ist bereits asymmetrischer als das Vorbild.
3. Es bewegt sich **nie nur eine Eigenschaft**: Deckkraft, Lage und Sichtbarkeit
   gehen zusammen, die Dauer ist dieselbe. Das ist der Kern von «eins geht aus dem
   anderen hervor»: ein Vorgang, mehrere Merkmale, eine Uhr.
4. Zeichen und Fläche gehören zusammen (Zeiger am Menü, Linie wächst unter dem
   Punkt): «jedes Teil enthält das Ganze» steht hier als dieselbe Bewegung im
   Kleinen (0,3 s) und im Grossen (0,25–0,5 s).

Was heisst das fürs Haus: Die Bloom-Kurve ist als Token zu behalten; zu ergänzen
sind die zweite Kurve für Vollflächen, die Eigenschaft «Lage» (kleiner Weg von
≈ 1,5 rem) neben «Höhe/Deckkraft» und die gleiche Uhr für alle Merkmale eines
Vorgangs. Der Bestand im Haus: `design-system/akkordeon.css` (`--acc-kurve`,
`--acc-dauer: .28s`, bei `prefers-reduced-motion` 0 s) und
`design-system/akkordeon.js` (Höhe und Deckkraft 0 → h, 280 ms auf, 220 ms zu,
dieselbe Kurve), Ledger 1.15.0 in
https://github.com/phtok/goeloggen/blob/main/design-system/CHANGELOG.md.

## § Systeme: Bewegungs-Token grosser Häuser

### Material Design 3

Quelle (Android-Doku, die Web-Spezifikation m3.material.io war nicht lesbar):
https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md

- Grundsatz: «duration should increase as the area/traversal of an animation increases».
- Easing: Standard `cubic-bezier(0.2, 0, 0, 1)`, Standard-Decelerate `(0, 0, 0, 1)`,
  Standard-Accelerate `(0.3, 0, 1, 1)`, Emphasized-Decelerate `(0.05, 0.7, 0.1, 1)`,
  Emphasized-Accelerate `(0.3, 0, 0.8, 0.15)`.
- Dauer-Stufen: short1–4 = 50/100/150/200 ms, medium1–4 = 250/300/350/400 ms,
  long1–4 = 450/500/550/600 ms, extraLong1–4 = 700/800/900/1000 ms.
- Asymmetrie: Container Transform ein 300, aus 250 ms; Fade ein 150, aus 75 ms.
  Eintritt bremst (Decelerate), Austritt beschleunigt (Accelerate).
- Struktur: Dauer (16 Stufen) × Kurve (Standard/Emphasized × Decelerate/Accelerate);
  die Richtung steckt in der Kurvenwahl.

Was heisst das fürs Haus: Die Asymmetrie ist dort Regel; 280/220 liegt zwischen
short4 und medium1. Das Haus hat nur eine Kurve für beide Richtungen.

### Apple Human Interface Guidelines

Quelle: https://developer.apple.com/design/human-interface-guidelines/motion

- «Add motion purposefully, supporting the experience without overshadowing it.»
  «Make motion optional.» «Let people cancel motion.» Bei häufigen Interaktionen
  keine Bewegung. Bewegung folgt der Geste (wer von oben einschiebt, erwartet kein
  seitliches Entlassen).
- Werte und Token: keine auf der Seite genannt.

Was heisst das fürs Haus: stützt das Weglassen (G03). Bewegung gehört dorthin, wo
Zustände selten und bedeutsam wechseln (Akkordeon, Dank), nicht auf jeden Hover.

### IBM Carbon

Quelle: https://carbondesignsystem.com/elements/motion/overview/

- Zwei Charaktere: productive («Effizienz») und expressive («enthusiastic, vibrant»).
- Kurven productive: standard `(0.2, 0, 0.38, 0.9)`, entrance `(0, 0, 0.38, 0.9)`,
  exit `(0.2, 0, 1, 0.9)`; expressive: standard `(0.4, 0.14, 0.3, 1)`, entrance
  `(0, 0, 0.3, 1)`, exit `(0.4, 0.14, 1, 1)`.
- Dauern: fast-01 70, fast-02 110, moderate-01 150, moderate-02 240, slow-01 400,
  slow-02 700 ms.
- Struktur: Dauer (6 Stufen) × Kurve (standard/entrance/exit) × Charakter. Die
  klarste Dreiteilung der gelesenen Systeme.

Was heisst das fürs Haus: Das Haus ist durchgehend «productive». Eine Rollen-Achse
(Ein/Aus/Standard) trennt Carbon sauber; Bloom entspräche «entrance».

### Atlassian

Quelle: https://atlassian.design/foundations/motion

- Interaktionen (Hover, Druck) 50–150 ms; Übergänge (ein, aus, bewegen) 150–400 ms;
  Beispiele: Listen-Hover 50, Dropdown-Eintritt 150, Modal-Eintritt 250 ms.
- Kurven: ease-out bold `(0, 0.4, 0, 1)`, ease-in-out bold `(0.4, 0, 0, 1)`,
  ease-in practical `(0.6, 0, 0.8, 0.6)` (Austritt), ease-out practical `(0.4, 1, 0.6, 1)`.
- Token bündeln Dauer, Kurve und Eigenschaft (belegt ist nur `motion.popup.enter`);
  Einführung hinter einem Flag.

Was heisst das fürs Haus: «Bold» (schneller Start, langer Auslauf) ist mit Bloom
verwandt; der Austritt hat dort eine eigene, kurze Kurve.

### GOV.UK Design System

Quellen: https://design-system.service.gov.uk/accessibility/ und
https://design-system.service.gov.uk/components/accordion/

- Beide Seiten erwähnen weder Animation noch Bewegung noch reduced motion; eine
  eigene Motion-Seite fand sich nicht. **Warum** GOV.UK so wenig Bewegung nutzt, ist
  **nicht belegt**; die Abwesenheit ist ein Indiz, kein Beleg.

Was heisst das fürs Haus: Verzicht ist eine anerkannte Haltung; unser Vokabular
sollte jede Bewegung rechtfertigen müssen.

### Salesforce Lightning

Quelle: https://app.unpkg.com/@salesforce-ux/design-system@2.3.0/files/design-tokens/force-base/duration.yml
(die Richtlinienseite lightningdesignsystem.com/guidelines/motion/ gab 404)

- Dauern als Adverbien: instantly 0, immediately 0,05, quickly 0,1, promptly 0,2,
  slowly 0,4 s; paused 3,2 s; Toasts 4,8 und 9,6 s. Kurven nicht belegt.

Was heisst das fürs Haus: Sprachliche Namen statt Zahlen passen zur Hausschrift
(Schnitte heissen Leise … Laut). Eine Anregung, kein Befund.

### Gesamtbild

Alle gelesenen Systeme setzen Ein- und Austritte zwischen 150 und 400 ms; 70–110 ms
sind Rückmeldung. Die Struktur ist überall Dauer (nach Grösse der Fläche) × Kurve
(nach Richtung), zum Teil × Charakter. Dem Haus fehlt bisher alles ausser einer
Kurve und zwei Dauern.

## § Grundlagen

### Disney-Prinzipien auf Oberflächen

- Val Head, «Designing Interface Animation» (2016):
  https://www.rosenfeldmedia.com/books/designing-interface-animation/ und
  https://www.creativebloq.com/web-design/beginners-guide-designing-interface-animations-61617793.
  Animation dient Rückmeldung, Orientierung, Aufmerksamkeitslenkung, Kausalität und
  Markencharakter; neu ist die «UI-Choreografie»: Bewegungen teilen Dauer, Kurve und
  Richtung. Feste Zahlen nennt sie nicht. Fürs Haus: Die eine Bloom-Kurve ist
  Choreografie im Kern; jede neue Bewegung erbt sie.
- Issara Willenskomer, «UI Animation Principles»:
  https://medium.com/ux-in-motion/ui-animation-principles-disney-is-dead-8bf6c66207f9
  (Seite gab 403, nur über Zusammenfassungen belegt). Disneys Prinzipien bilden 2D-Physik
  ab; er ersetzt sie durch zwölf eigene (Easing, Offset & Delay, Parenting,
  Transformation, Value Change, Masking, Overlay, Cloning, Obscuration, Parallax,
  Dimensionality, Dolly & Zoom). Fürs Haus: Zählen werden Easing, Offset (Stagger) und
  Parenting (Kinder folgen dem Eltern); Parallax, Dimensionality, Zoom nicht.
- Rachel Nabors, «Animation at Work» (2017): https://abookapart.com/products/animation-at-work
  (nur Klappentext und Rezensionen). Animation soll «Kontext in einer kontextarmen
  Umgebung» liefern; das Warum vor dem Wie. Fürs Haus: Bewegung zeigt, woher etwas
  kommt und wohin es geht, sonst entfällt sie (G03).

### Wahrnehmung von Dauer

- Nielsen Norman Group, Antwortzeiten: https://www.nngroup.com/articles/response-times-3-important-limits/.
  0,1 s = unmittelbar, 1,0 s = Gedankenfluss bleibt ungestört, 10 s = Aufmerksamkeit
  hält. Fürs Haus: Die Reaktion (Zeichen dreht, Fläche setzt ein) muss binnen
  100 ms sichtbar beginnen; Bloom beginnt sofort.
- NN/g, Animationsdauer: https://www.nngroup.com/articles/animation-duration/.
  Allgemein 100–500 ms; einfaches Feedback ≈ 100 ms; grosse Wechsel (Modal)
  200–300 ms; 400 ms nur bei weiten Wegen; ab 500 ms «zieht es sich». Die
  Schwellen 100/200/300 ms sind hier die belegte Fassung. Fürs Haus: 280/220 liegt
  mitten im Fenster; Hover, Pfeil und Farbwechsel gehören auf 100–150 ms.

### Eintritt länger als Austritt

- NN/g (siehe oben): «Entering animations need a slightly longer duration than
  exiting ones.» Beispiel Popup ≈ 300 ms ein, 200–250 ms aus.
- Material 1 (nur über Suchzusammenfassung):
  https://m1.material.io/motion/duration-easing.html: eintretend 225, austretend
  195 ms; was weggeht, braucht weniger Aufmerksamkeit.
- Material 3 und Carbon (siehe § Systeme): eigene Kurven je Richtung.
- Fürs Haus: 280/220 = Faktor 0,79, deckt sich mit NN/g. Wachsen darf also etwas
  länger dauern als Verwelken; das Verhältnis ist belegt, die absoluten Werte sind
  Setzung.

## § Technik heute (Stand Oktober 2026)

Sammelquelle: https://web-platform-dx.github.io/web-features-explorer/ (jeweils
Feature-Seite) und MDN. Die caniuse-Tabelle selbst liess sich nicht lesen.

| Feature | Unterstützung | Fallback | Craft ohne Framework? |
|---|---|---|---|
| View Transitions, same-document | Chrome 111, Safari 18, Firefox 144; Baseline «low» seit 14. 10. 2025 | `if (!document.startViewTransition) { update(); return; }` | ja, für Zustandswechsel mit Umbau (Filter, Ansicht); fürs Akkordeon unnötig |
| View Transitions, cross-document (`@view-transition { navigation: auto }`) | Chrome 126, Safari 18.2, Firefox nicht | At-Regel wird ignoriert, Seite lädt normal | ja, ein CSS-Block, null JS; nur ruhiges Überblenden (≈ 200 ms), kein Verschieben |
| `interpolate-size: allow-keywords` / `calc-size()` | Chrome/Edge 129; Safari und Firefox ohne Version, nicht Baseline | Höhe springt; `calc-size()` mit zuvor gesetztem Normalwert | optional, eine Zeile `:root`; Stand Safari/Firefox vor Gebrauch prüfen |
| `grid-template-rows: 0fr → 1fr` | überall (Allgemeinwissen, in dieser Recherche nicht getestet) | – | ja, trägt ohne JS-Messung als Basis für Höhe auto |
| `@starting-style` | Chrome 117, Firefox 129, Safari 17.5; Baseline «low» seit 6. 8. 2024 | Element erscheint ohne Eintritt | ja, risikolos |
| `transition-behavior: allow-discrete` | Chrome 117, Firefox 129, Safari 17.4; Baseline «low» | Kurzform doppelt setzen (erst ohne, dann mit) | ja; mit `@starting-style` für `[popover]`/`<dialog>` ohne JS |
| Scroll-driven Animations | Chrome 115, Safari 26, Firefox nicht (Flag/Nightly); nicht Baseline | `@supports (animation-timeline: scroll())`, Inhalt bleibt sichtbar | technisch ja, inhaltlich nein (siehe WCAG 2.3.3) |
| `prefers-reduced-motion` | Baseline «high» seit 15. 7. 2022 | – | Pflicht |

Quellen der Zeilen: die Feature-Seiten
https://web-platform-dx.github.io/web-features-explorer/features/view-transitions.json,
…/cross-document-view-transitions.json, …/interpolate-size.json,
…/calc-size.json, …/starting-style.json, …/transition-behavior.json,
…/scroll-driven-animations.json, …/prefers-reduced-motion.json sowie
https://developer.chrome.com/docs/css-ui/animate-to-height-auto und
https://developer.mozilla.org/en-US/docs/Web/CSS/interpolate-size. Zwei Widersprüche:
caniuse-Daten führen Firefox 144 bei Cross-Document als «teilweise (nur Level 1)»
(dann nur same-document), der Explorer sagt «nicht»; MDN nennt `allow-discrete` nicht
Baseline, der Explorer «low». Es gilt jeweils der Explorer.

### Barrierefreiheit der Bewegung

- WCAG 2.3.3 Animation from Interactions (AAA):
  https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html.
  Durch Interaktion ausgelöste Bewegungsanimation muss abschaltbar sein, ausser sie
  ist wesentlich. Farbe, Weichzeichnung und Deckkraft zählen nicht als Bewegung,
  solange Grösse, Form und Position gleich bleiben. Techniken C39, SCR40
  (`prefers-reduced-motion`). Fürs Haus: Die Höhenänderung ist Bewegung, bei
  `reduce` auf 0 ms oder reines Überblenden; das Haus ist bei AA, die Regel ist
  billig und steht ohnehin im Akkordeon.
- WCAG 2.2.2 Pause, Stop, Hide (A):
  https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html. Automatisch
  startende Bewegung über 5 s braucht Pause. Alle Übergänge des Hauses bleiben
  ≤ 0,5 s; erst Endlosschleifen (Karussell, Ladeanzeige) berührten die Regel.

Was heisst das fürs Haus: Nutzbar ohne Framework: `grid-template-rows` (Basis),
`@starting-style` + `allow-discrete` (Ein- und Ausblenden), `@view-transition`
(nur Überblenden) und `prefers-reduced-motion`. Beobachten, nicht einsetzen:
`interpolate-size`, Scroll-gebundene Animation.

## § Organisch

Ehrliche Vorrede: Belege gibt es für Goethes Begriffe und für Federphysik, nicht für
eine Brücke von Metamorphose zu Web-Bewegung. Die Übersetzung unten ist Lesart.

- Goethes Metamorphose als Ausdehnung und Zusammenziehung: Pitt Goethe Lexicon
  https://goethe-lexicon.pitt.edu/GL/article/download/22/26; Originaltext
  https://www.projekt-gutenberg.org/goethe/metamorp/metamorp.html. Das Lexikon
  beschreibt die Entwicklungsordnung als Folge von Ausdehnung und Zusammenziehung
  (sechs Stufen). Goethes Satz «die Pflanze ist immer nur Blatt» (1787), bei Harlan
  https://elementedernaturwissenschaft.org/de/download/1095/pre_pdf: Samenblatt, Kelch,
  Blütenblatt, Staubgefäss und Frucht sind Formen eines Organs. Einschränkung: Der
  Aufsatz von 1790 nennt die «Urpflanze» nicht; sie ist Denkmodell. **Polarität und
  Steigerung** als «zwei grosse Triebräder» (so das Memo) fanden sich in dieser
  Suche nicht in Fachquellen; vor dem Zitieren Goethes Text und das Lexikon
  (Eintrag «Steigerung») prüfen. Fürs Haus: «ein Organ, viele Gestalten» heisst, ein
  Baustein wandelt sich, statt dass ein anderer erscheint.
- Die beiden Goetheanum-Bauten: https://en.wikipedia.org/wiki/Second_Goetheanum. Erster Bau
  1913–1920 aus Holz und Beton, Brand 1922/23; zweiter Bau 1924–1928 ganz aus Gussbeton,
  weg vom rechten Winkel. Lesart: Die Form entsteht aus dem Material; im Web
  bewegt sich, was sich ändert (Höhe, Deckkraft), kein aufgesetzter Effekt. Ein Beleg,
  dass Steiner Zeitverläufe meinte, liegt nicht vor; auf der Seite nichts als
  «Steiners Prinzip» behaupten.
- Federn: https://developer.apple.com/videos/play/wwdc2023/10158/ (WWDC23 «Animate with
  springs»). Zwei Grössen genügen: Dauer und Bounce (z. B. 0,6 s, 0,2); Federn
  erhalten Kontinuität, auch bei Anfangsgeschwindigkeit; Bounce 0 ist sinnvoll. Fürs
  Haus: Bounce 0 oder sehr klein; in CSS als `linear()` oder Bezier mit weichem Auslauf.
  Bloom ist im Verlauf eine Feder ohne Überschwingen.
- Nicht belegt: Fibonacci/Goldener Schnitt als Zeitraster. Nicht behaupten.

Übersetzung der fünf Gesten in Dauer, Kurve und Reihenfolge (Lesart, nach
https://github.com/phtok/goeloggen/blob/spenden-befund/docs/memo-lebendige-gesten-2026-10-31.md):

| Geste | Mögliche Übersetzung |
|---|---|
| Wiederholung | gleiche Kurve und gleiche Dauer für gleiche Vorgänge |
| Polarität | auf und zu als Paar: dieselbe Kurve, der Austritt etwas kürzer (NN/g, belegt) |
| Steigerung | Reihenfolge von schwer nach leicht (Ledger 1.21.2); Stagger aufsteigend. Eine Studie zur Wirkung von Stagger fand sich nicht |
| Reduktion | eine Eigenschaft je Übergang, wo es genügt (G01/G03); Welken leiser und kürzer |
| Übergang | neuer Zustand beginnt dort, wo der alte aufhört; mehrere Merkmale, eine Uhr (wie Bloom, gemessen) |

## § Formular

### Betrag wählen (Kachel → freies Feld)

- Quellen (Anbieter und Blogs, schwach): https://capitalandgrowth.org/answers/Article/3600914/Blank-Box-or-Buttons-Which-Format-Increased-Online-Donations,
  https://commonslibrary.org/6-digital-fundraising-experiments-by-get-up/,
  https://help.actblue.com/hc/en-us/articles/16870088151191-Preset-Donation-Amounts.
  Voreingestellte Beträge schlugen in einem Test das leere Feld; immer ein freies
  Feld daneben; niedrig/mittel/hoch um den Durchschnitt; einen Betrag vorwählen. Im
  GetUp-Versuch war «Anderer Betrag» eng mit den Kacheln verbunden, aufsteigende
  Reihenfolge brachte die höchste Durchschnittsspende. Vorbehalt: Eigeninteresse der
  Anbieter, kleine Einzeltests.
- Fürs Haus: «Anderer Betrag» wird eine Kachel, die sich zum Feld weitet und den
  Platz der Kachel einnimmt (Ausdehnung statt zweitem Feld darunter); aufsteigende
  Folge entspricht der Steigerung; je Kachel ein Merkmal für die Wahl (G01).

### Felder erscheinen bei Bedarf

- GOV.UK, Conditional reveal: https://design-system.service.gov.uk/components/radios/.
  Die Frage erscheint, wenn die Option gewählt ist; einfach halten, bei mehrteiliger
  Frage lieber auf die nächste Seite; nicht bei nebeneinanderstehenden Ja/Nein-Radios;
  Fehler im aufgeklappten Feld müssen klar zur Ausgangsfrage gehören. Warnung: Nutzer
  werden nicht immer informiert, wenn die Frage erscheint (GOV.UK nennt das einen
  Fehler gegen WCAG 2.2, 4.1.2).
- NN/g, Progressive Disclosure: https://www.nngroup.com/articles/progressive-disclosure/.
  Zwei Ebenen sind das praktische Maximum; voneinander abhängige Schritte vertragen
  kein gestuftes Aufdecken; der Weg zu den Zusatzoptionen muss offensichtlich sein.
- Fürs Haus: «Adresse nur bei Spendenbescheinigung» ist der Normalfall, der trägt;
  eine mehrteilige Adresse ist an der Grenze. Betrag und Bescheinigung sind zwei
  Ebenen, das ist die Obergrenze. Der Dank ist ein Ende, keine dritte Ebene.

### Fehler erscheinen

- NN/g: https://www.nngroup.com/articles/errors-forms-design-guidelines/. Prüfen, sobald
  das Feld verlassen ist, nicht mittendrin; Meldung unter oder neben dem Feld; Farbe
  plus Icon, nie Farbe allein; der Fehlertext wird nie animiert, höchstens ein Icon
  dezent.
- GOV.UK Fehlerübersicht: https://design-system.service.gov.uk/components/error-summary/.
  Übersicht erhält beim Erscheinen den Fokus; Einträge verlinken aufs Feld; gleicher
  Wortlaut wie am Feld. Ob das bei einem kurzen Spendenformular das richtige Mass ist,
  ist Hausentscheid.
- Baymard (Spiegel): https://marketing-site-f2tmuig6e-baymard.vercel.app/blog/inline-form-validation:
  zu eifriges Prüfen während des Tippens wirkt tadelnd.
- Fürs Haus: Raum öffnet sich weich, der Text steht (nicht animiert eintreffend).

### Knopf wird zum Dank

- W3C SC 4.1.3 Statusmeldungen: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html.
  Erfolg: `role="status"`; Fehler: `role="alert"` oder Live-Region; `alert` für
  Unwichtiges unterbricht zu stark.
- Layoutsprünge: https://web.dev/articles/cls. Verschiebungen innerhalb 500 ms nach
  einer Eingabe zählen nicht als unerwartet; für Bewegung `transform` statt Höhe/Breite.
  Reduced-Motion heisst Sofort-Zustand, nicht «keine Änderung».
- Stripe: https://docs.stripe.com/elements/appearance-api nennt nur, dass Elements ein
  gleichbleibendes Layout halten; zu Fehlern oder Übergängen nichts gefunden. Eine
  unabhängige Studie zur Fokusführung nach dem Aufklappen fand sich nicht; selbst
  testen.
- Fürs Haus: Der Dank wächst am Ort des Knopfs (Lesart: Zusammenziehen zum ruhigen
  Punkt) und steht in einer Live-Region (`status`), die vor dem Inhalt im DOM liegt.
  Was nach der Eingabe wächst, wächst binnen 500 ms.

## Vorschlag: Bewegungs-Tokens fürs Fundament

Nur Vorschlag, nicht eingebaut. Namen im Muster von `design-system/tokens.css`
(`--s1`, `--w-klar`, `--r-card`), Dauern sprachlich wie die Schnitte. Die Werte der
ersten beiden Zeilen sind Bestand.

| Token | Wert | Rolle |
|---|---|---|
| `--kurve-bloom` | `cubic-bezier(.32,.08,.24,1)` | Standard für auf und zu kleiner Flächen (heute `--acc-kurve`) |
| `--kurve-flaeche` | `cubic-bezier(.35,0,.5,1)` | Vollflächen, Schiebeweg (goetheanum.ch Vollbild-Menü) |
| `--kurve-ein` | wie Bloom | Eintritt; eigene Kurve nur, falls Prüfung sie braucht |
| `--kurve-aus` | wie Bloom (oder `cubic-bezier(.4,0,1,1)`) | Austritt; Carbon/Atlassian/M3 führen eigene |
| `--dauer-hauch` | 120 ms | Hover, Fokus, Farbwechsel, Pfeil (NN/g ≈ 100) |
| `--dauer-kurz` | 220 ms | Austritt Akkordeon, Fehlerraum zu |
| `--dauer-mittel` | 280 ms | Eintritt Akkordeon, Betragsfeld, Adressfeld (heute `--acc-dauer`) |
| `--dauer-lang` | 400 ms | Dank, grosse Flächen; Obergrenze 500 ms |
| `--weg` | 1.5rem (≈ 24 px) | Lage-Weg beim Aufblühen, wie das Klappmenü |
| `--staffel` | 40 ms | Versatz je Glied in einer Folge (Steigerung); Wert ist Setzung, keine Quelle |
| Reduced Motion | alle `--dauer-*` auf 0 s | wie `--acc-dauer` heute; Raum öffnet sich ohne Bewegung (WCAG 2.3.3) |

Regeln für die Anwendung: eine Uhr für alle Merkmale eines Vorgangs (wie Bloom); ein
Zustand wechselt Höhe/Deckkraft/Lage zusammen, nie getrennt getaktet; Austritt
= `--dauer-kurz`, Eintritt = `--dauer-mittel`; Höhe auto über
`grid-template-rows` oder die Web Animations API wie im Akkordeon, `interpolate-size`
erst, wenn Safari und Firefox es tragen.

## Offene Fragen an den Auftraggeber

1. Eine Kurve für Ein und Aus (wie heute) oder je eine? M3, Carbon und Atlassian führen
   zwei; das Klappmenü auf goetheanum.ch nutzt eine.
2. Soll das Aufblühen den Lage-Weg (≈ 1,5 rem nach oben) des Klappmenüs übernehmen, auch
   im Akkordeon und im Formular, oder bleibt es bei Höhe und Deckkraft?
3. Bleibt es bei Bounce 0 (kein Überschwingen) oder soll «Wachsen» einmal sichtbar
   federn, z. B. beim Dank?
4. Fehlerübersicht mit Fokussprung (GOV.UK) auch bei kurzem Spendenformular, oder nur
   Meldung am Feld?
5. Darf «Adresse bei Bescheinigung» als aufklappendes Feld stehen (eine Ebene) oder
   gehört die mehrteilige Adresse auf einen eigenen Schritt?
