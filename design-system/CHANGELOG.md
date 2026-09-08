# Design-System — Beschluss-Ledger (das Gedächtnis)

Hier atmet das System: jede Verbesserung, die aus einer Seite ins **Fundament**
aufgenommen wird, steht hier mit Datum, Grund und Wirkung. Der Ledger ist die
Erinnerung des Systems an sein eigenes Wachstum — und die Quelle der
Versionsnummer (`design-system/contract.json` → `version`, SemVer).

**Der Atem (Aufnahme-Schleife).** Eine neue Lösung taucht auf einer Seite auf →
`tools/ds-lint.py` erkennt die Abweichung (DS04) → Entscheid: **aufnehmen**
(in `tokens.css`/`base.css` + `contract.json`, Eintrag hier) oder **auflösen**
(`tools/ds-fix.py` hebt sie auf die Token-Schicht zurück). Aufgenommenes gilt ab
dann überall und wird vom Checker erwartet. So wird aus einer Rand-Verbesserung
Fundament — nie lokal belassen.

Schema je Eintrag: *was · warum · Wirkung (welche Regel/Token/Komponente)*.

---

## 8. September 2026 — eine Reihe, die alle gleich macht, macht alle gleich (1.24.0)

**Was.** Das Rezept kennt jetzt eine **Spanne**: Die Helligkeit der Basisfarbe
wirkt auf die abgeleitete mit (`spanne: 0.14` bei Fläche und Tinte, `0.10` im
Dunkelmodus). Dazu tragen die dunklen Flächen **vier Fünftel** der Buntheit
ihrer Basis statt eines absoluten Deckels von 0.085 («halb satt», Beschluss).
Betroffen sind `--sek-*-dunkel`, `--sek-*-ink` und die Dunkelmodus-Tinte; der
helle Hauch bleibt, wie er ist.

**Warum.** Der Auftraggeber: «Mathe und Redende brauchen Differenzierung.» Das
Nachmessen zeigte, dass es kein Einzelfall war, sondern die Regel selbst:
Zwischen **Redende und Musizierende Künste** und der **Mathematisch-Astro-
nomischen Sektion** lagen in der Basis 18 Einheiten Abstand – in der dunklen
Variante noch **0.6**. Bei Pädagogik und Redende waren es 22.7 gegen 2.7.
Insgesamt lagen **sieben von 78 Paaren** praktisch übereinander.

Die Ursache war die Gleichmacherei: Alle dreizehn standen auf **derselben**
Helligkeit mit gedeckelter Buntheit. Sechs der dreizehn Sektionen sind blau und
unterscheiden sich vor allem darin, **wie hell** sie sind – zwingt man sie auf
eine Helligkeit, sind sie dieselbe Farbe. **Eine Reihe, die alle gleich macht,
macht alle gleich.** Gleichmass ist ein Mittel, keine Tugend: Es soll die
Sektionen als eine Familie zeigen, nicht ihre Identität einziehen.

**Wirkung.** Kleinster Abstand jetzt 2.6 statt 0.6, **kein Paar mehr unter 2**;
Redende und Mathe stehen bei 7.7. Weiss hält überall zwischen 5.3 und 9.4:1,
alle 165 Kontraste ≥ 4.5:1 in beiden Themes. Die zwei Ausnahmen (Kürbis,
Korallenrot) bleiben und nehmen keine Spanne: Ihr Wert ist am Muster
beschlossen, nicht gerechnet.

**Offen.** Der helle Hauch trägt weiterhin fast keine Identität – 27 der 78
Paare liegen unter 2, zwei sind sogar gleich. Das ist die Kehrseite des
Beschlusses «zart, nicht leuchtend»: Bei dieser Helligkeit ist der Farbraum so
eng, dass dreizehn Töne kaum Platz haben. Solange die Identität von Basis und
Tinte getragen wird, ist das vertretbar; wenn Chips einmal ohne Tinte
auskommen müssen, ist es neu zu entscheiden.

## 8. September 2026 — die Jugendsektion bekommt ihr Rot zurück (1.23.0)

**Was.** **`--sek-js-dunkel` #BD2525** statt #844741 (Weiss 6.08:1) und
**`--sek-js-ink` #AB0815** als Schrift (6.8 bis 7.6:1). Die Ausnahme steht im
selben Block wie die der Heilpädagogik, mit demselben Abstand zwischen Fläche
und Schrift: fünf Hundertstel Helligkeit.

**Warum.** Dieselbe Wand, von der anderen Seite. Bei der Heilpädagogik war der
**Farbkörper** eng – Orange kann bei dieser Helligkeit gar nicht bunt genug
sein. Beim Korallenrot der Jugendsektion ist er weit: C 0.191 wären bei L 0.47
möglich, der Deckel liess 0.085 zu und nahm ihr damit **56 Prozent** ihrer
Buntheit. Übrig blieb ein stumpfes Rostbraun, das in der Reihe neben der
Sozialwissenschaft fast verschwand – zwei Nachbarn, die gleich aussahen.

**Wirkung.** Ein Deckel, der für alle gilt, trifft jede Farbe anders: Orange
lag bei 70 Prozent des Möglichen, Rot bei 44, Blau bei 28. **Ein absoluter
Deckel ist keine gleiche Behandlung.** Vorerst bleibt er, weil er die blassen
Sektionen ruhig hält; wo er eine Identität frisst, hebt ihn eine Ausnahme –
mit Muster und Beschluss, wie der Block es verlangt. Alle 165 Kontraste halten
weiterhin ≥ 4.5:1 in beiden Themes.

## 8. September 2026 — Orange darf nicht braun werden (1.22.0)

**Was.** Die dunkle Fläche der Heilpädagogik steht heller und schöpft ihre
Buntheit aus: **`--sek-hpise-dunkel` #AF5400** statt #804C2B (Weiss 5.13:1).
Ihre Schrift bleibt eine Stufe dunkler, **`--sek-hpise-ink` #9A4900**
(5.7 bis 6.3:1 auf Papier, Hauch und Karte) – damit die Tinte Reserve behält,
wo die Fläche heller werden durfte. Dafür wird **`ink` eine eigene Rolle** im
Rezept statt ein Zweitname der Fläche, und `tools/sek-varianten.py` bekommt
einen **Ausnahmen-Block** mit Begründungspflicht. Nebenbei trifft
`from_oklch()` den Gamut-Rand jetzt per Bisektion statt in 6-%-Schritten –
bisher blieb eine Farbe je nach Zufall bis zu 6 % unter ihrer möglichen
Buntheit, genau dort, wo sie diese am nötigsten braucht.

**Warum.** Der Auftraggeber: «Das Orange wird unangenehm braun.» Er hat recht,
und es liegt nicht am Rezept, sondern am Farbkörper: **Orange ist die einzige
Sektionsfarbe, deren dunkle Form einen eigenen, abwertenden Namen trägt.**
Dunkles Blau heisst Dunkelblau, dunkles Grün Dunkelgrün – dunkles Orange heisst
Braun. Bei L 0.47 kann Orange höchstens C 0.121 tragen (gemessen, sRGB); satt
oder nicht, es bleibt ein Braun. Eine Regel für alle hält die Reihe zusammen,
aber der Farbkörper ist nicht rund: Wo die Regel die Identität frisst, braucht
sie eine begründete Ausnahme. Entschieden wurde am Muster, nicht an der Zahl –
sechs Kandidaten am Kopfband und die ganze Reihe je Kandidat.

**Wirkung.** Die Heilpädagogik ist in der Reihe nun etwas heller als ihre
Nachbarn. Das ist gewollt: Es gleicht aus, dass Orange bei gleicher Helligkeit
dunkler und schmutziger wirkt als Blau oder Grün. Regel für neue Ausnahmen:
**nur mit Muster und Beschluss** – der Block in `sek-varianten.py` sagt das.
Alle 165 Kontraste halten weiterhin ≥ 4.5:1 in beiden Themes.
## 8. September 2026 — der Text der Kapsel liegt auf einem halben Hauch (1.21.4)

**Was.** Die geöffnete Kapsel steht nicht mehr auf blankem Papier, sondern auf
**55 % von `--ton-hell` über Papier** – einem halben Hauch. Geschlossen bleibt
die volle Fläche; der offene Grund ist damit immer der ruhigere von beiden.

**Warum.** Der Auftraggeber: «Ich fände es schon gut, wenn der Text ganz ganz
leicht hinterlegt wäre.» Papier war eine Stufe zu weit – die Antwort verlor
ihre Zugehörigkeit zur Karte und stand einfach auf der Seite. Ein halber Hauch
gibt ihr wieder ein Feld, ohne dass der Satz trägt, was er nicht muss.

**Wirkung.** `akkordeon.css`, Kleid Kapsel. Die Reihe der Gründe von schwer nach
leicht: Band (`--ton-dunkel`) → geschlossene Kapsel (`--ton-hell`) → offener
Lesegrund (halber Hauch) → Papier. **Je mehr Text, desto leiser der Grund.**

## 8. September 2026 — die Schritt-Kugel sitzt auf der Versalmitte (1.21.3)

**Was.** `.step-num` wird um **0.26em ihrer eigenen Grösse angehoben** (rein
optisch, `position:relative`, damit die Zeilenbox des Titels unverändert
bleibt).

**Warum.** Der Auftraggeber sah es am Blatt: «Die Kugel sitzt zu tief.» Die
Messung gab ihm recht — als Inline-Box hing die Kugel an der **Grundlinie**,
ihre Mitte lag damit **5.4 px unter der Versalmitte** des Titels (28.8 px Grad,
Versalhöhe 20, x-Höhe 14; Tinte auf Canvas vermessen, nicht geschätzt). Eine
Marke neben einem Titel gehört auf die Mitte der Versalhöhe: die Grundlinie ist
die Kante, auf der der Text steht, nicht seine Mitte. Nachgemessen sitzt die
Kugel jetzt auf −10 px, exakt auf der Versalmitte.

**Wirkung.** `base.css`. Betrifft beide Seiten, die die Kugel führen
(`akkordeon.html`, `apps/logos/`) — beide nachgesehen. Regel für runde Marken
neben Text: **auf die Versalmitte heben, nicht auf der Grundlinie hängen
lassen** — und die Korrektur optisch setzen, damit der Durchschuss nicht
springt.

## 8. September 2026 — die Kapsel lernt von der Blüte: Text auf Papier (1.21.2)

**Was.** Die geöffnete Kapsel wechselt ihren Grund: die Antwort steht auf
**Papier** (mit der Haarlinie der Blüte), nicht mehr auf dem Farbhauch. Der
Hauch bleibt der Grund der **geschlossenen** Kapsel; offen trägt nur noch das
Band die Farbe. Einzug und Innenabstand übernehmen die Masse der Blüte
(`--s6` links, `--s4` oben und unten am Band).

**Warum.** Der Auftraggeber: «Die Blüte ist ein gutes Vorbild.» Ihre Leichtigkeit
kommt nicht vom Radius, sondern vom **Grund**: eine gefüllte Fläche wiegt
schwerer als eine umrissene, und Mengentext braucht den ruhigsten Grund, den es
gibt. Damit behält die Kapsel ihr Merkmal – die farbige Fläche –, gibt es aber
dort auf, wo gelesen wird.

**Wirkung.** `akkordeon.css`, Kleid Kapsel. Regel dahinter: **die Farbe zeigt
den Zustand, das Papier trägt den Text.** Geschlossen = Hauch, offen = Band auf
Papier.

## 8. September 2026 — die Kapsel wird ruhig: dezenter Radius, mehr Luft (1.21.1)

**Was.** Das Kleid Kapsel verliert seine Kapselform: der Radius fällt von einer
halben Zeilenhöhe (rund 46 px) auf **`--r-card`, 14 px**. Dafür mehr
Innenabstand — Kopfzeile und Antwort tragen `--s5` (schmal `--s4`), Frage und
Antwort stehen links auf **derselben Kante** (gemessen 139 px breit, 28 px
schmal). Offen wird die Frage zu einem **Band**: oben gerundet, unten bündig in
die Karte laufend; die Karte selbst bleibt rund. Der Abstand zwischen den Karten
wächst von `--s3` auf `--s4`.

**Warum.** Der Auftraggeber: die Kapsel hat bisher keinen Fürsprecher gefunden,
und der Text wirkte **eingequetscht**. Zu Recht — eine starke Rundung frisst
Satzspiegel: an den Ecken bleibt vom Innenabstand nichts übrig, der Text
rückt in die Mitte und die Fläche drückt von zwei Seiten. Dazu kam ein
Fehler aus dem Wegfall der Nummer: die Antwort behielt ihren Einzug von
`--s3 + 2.2em + --s4` und stand damit rund 50 px weiter innen als die Frage.

**Wirkung.** `akkordeon.css`, Kleid Kapsel. Regel dahinter: **Rundung und
Innenabstand hängen zusammen** — wer den Radius erhöht, muss den Innenabstand
mitziehen, sonst verliert der Satz an den Ecken, was er in der Mitte hat.

## 8. September 2026 — das Akkordeon lässt los: unabhängig, zeigbar, aus dem Fundament gefärbt (1.21.0)

**Was.** Vier Änderungen am Modul Akkordeon, dazu das Aufgehen im Fundament:

1. **Antworten öffnen unabhängig.** Eine neu geöffnete schliesst die anderen
   nicht mehr; beliebige Kombinationen bleiben stehen. «Alle aufklappen» bleibt
   und spiegelt jetzt den Stand der Liste, egal wie er zustande kam.
2. **Die Nummer ist optional und entfällt.** Fehlt `span.nr`, wird die Zeile
   einreihig (`summary:not(:has(.nr))`). Die Schau-Seite zeigt alle drei Kleider
   ohne Zahlen.
3. **Der Faden zeigt seine Bedienbarkeit.** Bei Hover legt sich ein Hauch Ton
   (7 % auf Papier) unter die ganze Zeile – Winkel, Text und Fläche sind
   dieselbe Aktion. Der Fokusring bleibt unverändert.
4. **Jede Antwort ist teilbar.** Wer eine öffnet, bekommt ihre Adresse in die
   Adresszeile (`replaceState`, kein Sprung, kein Eintrag in der
   Zurück-Geschichte); am Fuss der Antwort steht ‹Link kopieren›.
5. **Die Farbrollen kommen aus dem Fundament.** Die dreizehn eigenen
   `[data-sek]`-Regeln des Moduls sind weg; es liest `--ton`, `--ton-dunkel`,
   `--ton-hell`, `--ton-ink` (1.20.0) mit Gold als Fallback. Damit färbt auch ein
   `data-sek` weiter oben im Dokument das Akkordeon mit, und Bühne und
   Bau-Administration kommen gratis dazu.

**Warum.** Der Auftraggeber, mit Belegen: **GOV.UK** setzt sein Akkordeon
mehrfach offen, weil zusammengehörige Fragen sich vergleichen lassen müssen –
Teilnahme und Mitgliedschaft liest man nebeneinander, nicht nacheinander. Das
Einfach-offen war eine Annahme, keine Anforderung. **NN/g** stützt, Text und
Zeichen dieselbe Aktion auslösen zu lassen; die Hover-Fläche macht sichtbar,
was schon galt. Und Direktlinks, die nur beim Ankommen funktionieren, aber beim
Öffnen keine Adresse hinterlassen, sind für den Leser nicht auffindbar.

**Wirkung.** `akkordeon.css` verliert 13 Regeln an das Fundament (Atem);
`akkordeon.js` verliert die Einfach-offen-Mechanik samt Sprungausgleich – der
wurde nur gebraucht, weil sich etwas darüber schloss. Für Craft: der Anker
kommt aus der **ID der Zeile**, nicht aus `loop.index`, damit ein geteilter Link
gültig bleibt, wenn Fragen umsortiert werden.

## 8. September 2026 — ein Attribut färbt einen Abschnitt (1.20.0)

**Was.** `data-sek` ist jetzt Fundament: `<div data-sek="nws">` setzt vier
Farbrollen für alles darin — **`--ton`** (Linie, Marke), **`--ton-dunkel`**
(Fläche für Weiss), **`--ton-hell`** (Hauch für dunklen Text), **`--ton-ink`**
(die Farbe als Schrift). Hausfall ist Gold, die Zuordnung erzeugt
`tools/sek-varianten.py` mit. Dazu drei Bausteine in `base.css`, die diese
Rollen abgreifen: **`.band`** (Kopfband, Weiss auf der dunklen Fläche),
**`.kasten`** (Hinweis auf dem Hauch, Kante im dunklen Ton), **`.btn.ton`**
(Knopf) sowie `.card.ton` (Kante) — und `.chip.ton` liest die Rollen jetzt
ebenfalls, im Hausfall unverändert golden.

**Warum.** Das Akkordeon (1.15.0) brauchte die Varianten und schrieb dafür
**dreizehn Zeilen** Zuordnung in sein eigenes Modul; die Sektionsfarben-Seite
tat dasselbe mit fünf Variablen im Skript. Jedes weitere Modul hätte
abgeschrieben — und die Abschriften wären mit der nächsten Sektion
auseinandergelaufen. **Eine Zuordnung, die jede Komponente wiederholt, gehört
in die Schicht darunter.** Ebenso die Bausteine: Kopfband und Hinweiskasten
standen lokal auf der Sektionsfarben-Seite, obwohl sie der eigentliche Grund
für die hellen und dunklen Varianten sind.

**Wirkung.** Das Akkordeon verliert seine dreizehn Zeilen und liest nur noch
ab (`--ak: var(--ton, …)`, Modul-API unverändert); die Sektionsfarben-Seite
verliert ihre gesamte lokale Farblogik und setzt ein Attribut. Neue Werkzeuge
färben einen Abschnitt mit **einem** `data-sek` und bauen mit `.band`,
`.kasten`, `.chip.ton`, `.btn.ton`. Der Knopf nimmt dabei immer `--ton-dunkel`
mit Weiss, nie die Basisfarbe — die hält bei sechs Sektionen kein Weiss (B01).
Beim Messen fiel nebenbei ein alter Fehler auf der Sektionsfarben-Seite auf:
die Kontrastzeile auf der Basisfläche trug `opacity:.92`. Bei den sechs
Sektionen, deren Vordergrund ein knapp gerechneter dunkler Ton ist (4.6:1),
drückte die Deckkraft ihn **unter** die 4.5:1 — gefunden von
`tools/barrierefreiheit.mjs`, nicht vom Auge. **Deckkraft ist eine
Kontraständerung**: auf einem Wert, der ohne Reserve gerechnet ist, hat sie
nichts zu suchen.

Nebenbei: Die Code-zum-Kopieren-Blöcke auf `akkordeon.html` waren Abschriften
der Modul-Dateien und wären mit dieser Änderung falsch geworden; sie laden den
Text jetzt aus der Quelle (Rückfall bleibt der statische Block).
## 8. September 2026 — der Rückstand ist abgetragen, das Tor ist zu (1.19.0)

**Was.** Die acht Funde der Erstmessung sind entschieden und behoben, und
`verlinktes_css.stand` steht auf **‹tor›** — Verstösse in verlinktem CSS
blockieren ab jetzt wie die der Seite selbst. Im Einzelnen: der **Kicker**
(`.kicker`/`.kick`) und der **Code-Block** stehen auf `--t-micro` statt auf
13.5 und 13 px; in der Kopfzeile tragen «← Übersicht», Tooltip, Toast und der
Schubladenfuss dasselbe Token statt 12 und 13.5 px. Die Wortmarke nimmt
`--muted` statt des harten `#8a9097`. Und der Schleier hinter der Schublade
bekommt ein eigenes Token, **`--scrim`** — hell `rgba(20,24,28,.32)` wie
bisher, dunkel `rgba(0,0,0,.52)`, weil er dort tiefer greifen muss.

**Warum.** Beschluss des Auftraggebers, 8. September: «Kicker hoch.» Der
Boden von 14 px gilt seit dem 10. Juli; base.css und nav.css liefen nur
darunter, weil der Prüfer sie nie las. Die Wortmarke war nebenbei ein
gerechneter Grenzfall: `#8a9097` hält auf getönter Fläche 3.04:1 — knapp über
der 3:1 für grosse Schrift und ohne Reserve; `--muted` trägt 4.94:1.

**Wirkung.** Score bleibt 100 % (63/63), jetzt aber mit geschlossenem Tor
statt mit einem Rückstand daneben. Der Kicker steht auf 54 Seiten und wächst
um einen halben Pixel — am gerenderten Blatt geprüft, das Bild bleibt.

## 8. September 2026 — der Schweber wird leise (1.19.0)

**Was.** Das Familien-Signet ist nicht mehr eine gefüllte blaue Scheibe mit
ausgespartem Zeichen, sondern eine **Papierfläche mit Ring und Zeichen** in
`--blue`. Die Geometrie bleibt die des Kreis-Layouts aus dem Logo-Generator.
Dazu weicht die Rückmelde-Pille der Kopfzeile dem Schweber aus, sobald
`familie.js` die Klasse `goe-hat-schweber` setzt.

**Warum.** Befund des Auftraggebers: «auf mobil sehr laut, vielleicht ist das
Blau zu viel.» Am schmalen Blatt stimmt das — 44 px volles Markenblau sind
dort ein Drittel der Zeilenhöhe. Und gemessen überlappten Schweber und
Rückmelde-Pille ab 360 px abwärts, eine gängige Telefonbreite.

**Wirkung.** Die Farbe kommt aus dem Token, nicht aus dem Druck: festes
Markenblau hält auf dunklem Papier nur **2.76:1** und reisst unter die 3:1 für
Grafik (B02); `--blue` trägt 6.69:1 und im Ruhezustand noch 3.57:1. Der
Schweber ist ein Bedienelement, das die Markenform trägt — kein gedrucktes
Logo. Gemessen auf 320, 360, 390 und 420 px: keine Überlappung mehr.

## 8. September 2026 — der blinde Fleck: verlinktes CSS kommt unter die Lupe (1.18.0)

**Was.** `tools/ds-lint.py` prüfte DS02 (Farben nur über Tokens), DS03
(Grössen), DS04 (kanonische Rollen), DS05 (Hervorhebung) und DS07
(Theme/harte Flächen) bisher **nur** in den `<style>`-Blöcken und
`style="…"`-Attributen der HTML-Datei selbst — verlinkte `*.css`-Dateien
blieben aussen vor (nur DS10/`check_tokens` löste sie schon auf). Eine Seite,
deren ganze Gestalt in einer eigenen CSS-Datei steckt, meldete darum «0
Fehler», ohne dass dort je geprüft wurde. `tools/ds-lint.py` löst jetzt jeden
`<link href="…css">` einer Seite über denselben Weg wie DS10 auf (repo-eigene
Pfade, externe/absolute URLs aussen vor) und prüft die fünf Regeln auch dort —
jede CSS-Datei genau **einmal** pro Lauf (nicht 60-mal für 60 einbindende
Seiten), mit der Zeile in der CSS-Datei selbst und einer Liste, welche
Seite(n) sie einbinden. `design-system/*.css` definiert die kanonischen
Rollen selbst und ist darum von DS04 (‹lokal redefiniert›) ausgenommen — DS02/
03/05/07 gelten dort unverändert. Nebenbei behoben, weil das Mitlesen von
`tokens.css` es sofort sichtbar machte: CSS-Kommentare wurden vor dieser
Änderung nicht aus den Regel-Körpern entfernt. Zwei Folgen, beide gefixt: (1)
ein Kommentar direkt hinter einer Custom-Property-Definition
(`--blue-solid:#0061a9; /* … */`) verklebte mit der nächsten Deklaration und
liess DS02 diese Fundament-Farben fälschlich als harte Werte melden; (2) ein
mehrzeiliger Kommentar vor einer Regel landete im erfassten Selektor und sein
Leerraum liess die Nachfahren-Ausnahme («`.download .btn` ist Verortung, keine
Neudefinition») fälschlich auch auf **bare** Selektoren wie `.lede{…}`
zuschlagen — DS04 hat dadurch **fünf** echte, bisher unsichtbare
Rollen-Redefinitionen in eigenen `<style>`-Blöcken übersehen (siehe Wirkung).
Dieselbe Verwechslung liess DS05 `.hint a:hover{text-decoration:underline}`
(Link-Hover, keine Betonung) fälschlich als Verstoss zählen; DS05 prüft
`underline` jetzt wie DS04 nur auf bare/compound-Selektoren, Nachfahren-
Selektoren (`.hint a`) sind Link-Konvention und ausdrücklich erlaubt.

**Warum.** Befund Konrads (Korrektor), 8. September 2026, am neuen
Familienmenü: `design-system/familie.css` (127 Zeilen, komplette Gestalt der
Schublade) lief unsichtbar am Checker vorbei — der Score war eine Behauptung,
keine Messung. Jede künftige Seite mit eigener CSS-Datei hätte denselben
blinden Fleck genutzt, ob absichtlich oder aus Versehen.

**Berichtend, noch kein Tor.** Sofort blockierend gestellt fiele der Score von
100 % (63/63) auf **5 % (3/63)** — und niemand im Haus könnte mehr committen,
weil `base.css` und `nav.css` in 60 bzw. 52 der 63 Seiten stecken. Darum
dasselbe Vorgehen wie bei **DS08** (Barrierefreiheit, 8. August): die
Erstmessung **berichtet**, sie sperrt nicht. Der Prüfer weist die Funde in
verlinktem CSS getrennt aus (‹dazu berichtend›), das Gate bleibt grün, und der
Stand steht im Vertrag unter `verlinktes_css.stand`. Ist der Rückstand
entschieden und behoben, wird dort ‹berichtend› auf ‹tor› gedreht — eine
Zeile, wie bei DS08 das `continue-on-error`. Ein Tor, das vom ersten Tag an
rot steht, hütet nichts.

**Der Rückstand.** `design-system/base.css` und `design-system/nav.css`
(Fundament) tragen acht echte, bisher unsichtbare Verstösse, die jede Seite
erbt, die sie einbindet. Sie liefen seit der Anhebung des Grössen-Bodens
(10. Juli, 13 → 14 px) unbemerkt mit, weil der Prüfer nur ins HTML sah:
- `base.css:305` `.kicker,.kick{…font-size:13.5px…}` — DS03 fehler, 0.5px
  unter dem 14px-Floor (B03). Die kanonische Kicker-Rolle selbst.
- `base.css:336` `.code.block,pre.code{…font-size:13px}` — DS03 fehler.
- `nav.css:52` `.dsnav .brand .wm{…color:#8a9097…}` — DS02 fehler, hartes Hex
  statt Token.
- `nav.css:55` `.dsnav .back{…font-size:13.5px…}` — DS03 fehler.
- `nav.css:95` `.dsnav [data-tip]::after{…font-size:12px…}` (Tooltip) — DS03
  fehler.
- `nav.css:115` `.dsnav-backdrop{…background:rgba(20,24,28,.32)…}` — DS02
  fehler, rgba() ohne Token.
- `nav.css:184` `.dsnav-toast{…font-size:13px…}` — DS03 fehler.
- `nav.css:214` `.dsnav-drawer .foot{…font-size:12px…}` — DS03 fehler.

Dazu ein echter Treffer in Seiten-CSS: `apps/sommer-zaehler/campaign.css:11`
`.lead-title{…font-size:clamp(32px,7vw,58px);…}` — DS04 hinweis, redefiniert
die kanonische Rolle lokal (legitim gemeldet, wie base.css/nav.css NICHT
ausgenommen, weil es keine Fundament-Quelle ist). Und fünf durch den
Kommentar-Fix neu sichtbare DS04-Treffer in eigenen `<style>`-Blöcken:
`design-system/index.html:79` (`pre.code`), `schrift-vergleich.html:27` und
`werkzeug.html:22` (je `.lede`), `sektionsfarben.html:71` und `:82`
(`.chip.sek`, `.btn.sek`).

**Bewusst nicht getan.** `base.css`/`nav.css` selbst NICHT angefasst — die
Floor-Unterschreitungen (Kicker, Tooltip, Toast, Fusszeile) und die zwei
harten Farbwerte betreffen 50+ Seiten auf einen Schlag und brauchen eine
Design-Entscheidung (grösser setzen? andere Rolle? neues `--scrim`-Token für
die Backdrop-Rgba?), keine mechanische Korrektur — `tools/ds-fix.py` kennt
für Grössen ohnehin keine automatische Anhebung. Ebenso nicht angefasst:
`apps/sommer-zaehler/campaign.css:11` und die fünf frisch sichtbaren
`<style>`-Redefinitionen — alle sechs sind `hinweis`, blockieren das Gate
nicht, verdienen aber denselben Blick vor der nächsten Anfassung dieser
Seiten. `tools/ds-fix.py` prüft nach wie vor nur die HTML-Datei selbst — auf
verlinkte CSS-Dateien nicht erweitert (nicht beauftragt, siehe Auftrag). ⚑
Alle acht Fehler + sechs Hinweise liegen zur Entscheidung bei Philipp.

## 8. September 2026 — das Familienmenü kommt ins Fundament (1.17.0)

**Was.** Drei neue Dateien im Fundament: `familie.json` (die Goetheanum-Familie
als eine Quelle — vier Gruppen, 32 Einträge, vier Sprachen), `familie.css` und
`familie.js`. Sie erzeugen ein Menü, das von **jeder** Seite der Familie zurück
ins Ganze führt — auch von fremden CMS aus, mit einer Zeile im Seitenfuss.
Zwei Öffner auf dieselbe Schublade: der **Schweber**, eine runde Marke unten
links, die bei Hover und Fokus zur Pille «Goetheanum» aufblüht (Hauptform, auf
dem Schreibtisch wie am Telefon), und die **Familienzeile** über dem Seitenkopf.
Die Schublade zeigt vier Gruppen — Goetheanum, Sektionen, Bereiche, Medien und
Dienste — als **blosse Titel** (G03); Sektionen und farbtragende Bereiche
führen einen Punkt in ihrer Identitätsfarbe (`--sek-*`, `--bereich-*`), der
Standort trägt `aria-current` und Deutlich. Schauseite und Einbau-Rezept:
`design-system/familie.html`.

**Warum.** Die Familie läuft auf vier Unterbauten (Craft, WordPress, Uscreen,
Squarespace — `docs/webfamilie-befund.md`); eine gemeinsame Kopfzeile liesse
sich dort nirgends gleich einbauen, und ein zweiter Header griffe zu stark in
gewachsene Layouts ein (Einwand des Auftraggebers, 8. September). Der Schweber
braucht **kein** Layout: er liegt über der Seite, kostet zwei Zeilen und ist am
Telefon im Daumenbereich. Radial aufblühende Icons («Bloom») wurden verworfen —
sie tragen vier bis sechs Einträge, nicht dreissig, und Icons ohne Wort sind
nicht lesbar (`docs/megamenu-konzept.md`, Abschnitt 6).

**Wirkung.** Die Titel kommen aus `assets/goe-orgs.js`, die Reihenfolge und die
Ziele von `goetheanum.ch/de/sektionen`; eine neue Sektion ist eine Zeile in
`familie.json` und gilt überall am selben Tag. Der Schweber weicht aus, wenn
der Tastaturfokus unter ihm liegt (WCAG 2.2, 2.4.11), verschwindet im Druck und
hält sich an `prefers-reduced-motion`. Gemessen: ds-lint 0 Fehler,
`barrierefreiheit.mjs` ohne Verstoss auf 390 und 1440 px.

## 8. September 2026 — die Zahl folgt dem Rahmen (1.16.3)

**Was.** In der Blüte nimmt die Nummer die Sektionsfarbe an, sobald der Rahmen
sie annimmt – bei Hover und im offenen Zustand; geschlossen bleibt sie grau.

**Warum.** Auf Frage des Auftraggebers. Vorher wechselte nur der Ring die
Farbe, die Zahl blieb stumm; jetzt bewegen sich beide zusammen und der offene
Eintrag liest sich als ein Zeichen statt als zwei. Die Zahl trägt die **Tinte**
(`--ak-ink`), nicht die Basisfarbe: die ist Linie, nicht Schrift (B02).
Gemessen am gerenderten Blatt: 7.04:1 hell, 9.86:1 dunkel.

**Wirkung.** `akkordeon.css`, Kleid Blüte. Faden und Kapsel tragen die Farbe an
der Zahl schon; damit ist die Regel in allen drei Kleidern dieselbe: **das
farbige Zeichen der Anwahl trägt die Zahl mit.**

## 7. September 2026 — die Nummer als Marke, in der Hausschrift (1.16.2)

**Was.** Der Griff aus dem Faden gilt jetzt auch für die **Blüte**: die Nummer
steht als eigene Zeile über der Frage, Frage und Antwort laufen bündig (die
Antwort verliert ihren Einzug von `2ch + s4`). Dazu in **allen drei Kleidern**:
die Ziffer läuft in der **Hausschrift** (Klar, in der Kapsel Deutlich) statt in
der Lese-Grotesk, und nach der Zahl steht mehr Luft (`row-gap` von 2 px auf
`--s2`). Im Kreis der Kapsel sitzt sie mit dem vermessenen 8%-Versatz aus
`.step-num`.

**Warum.** Der Auftraggeber wollte den Faden-Griff auch in der Blüte und die
Zahlen «aus der Goeschrift». Die Schrift-Grenze schickt Zahlen in die
Lese-Grotesk, wo sie **Daten** sind – Tabelle, Wert, Formular. Diese Ziffer ist
aber keine Angabe, sondern eine **Marke**: sie zählt die Frage, wie die
Schritt-Nummer `.step-num` einen Schritt zählt, und die trägt in `base.css`
längst die Hausschrift. Gleiche Rolle, gleiche Schrift.

**Wirkung.** `akkordeon.css`: `.acc .nr` in `--font-display`, Gewicht Klar
(kleine Hausschrift nie Leise), Ziffern weiterhin dicktengleich (G25). Regel
für neue Bausteine: **zählende Marken tragen die Hausschrift, messende Werte
die Lese-Grotesk.** Nur die Blüte behält ihre Zahl in Grau – dort trägt der
Ring die Farbe, im Faden die Zahl.

## 7. September 2026 — Faden: die Nummer über der Frage (1.16.1)

**Was.** Im Kleid Faden steht die Nummer als eigene, leise Zeile über der
Frage (Sektionstinte, `--t-small`); Frage und Antwort laufen bündig in
derselben Einrückung. Vorher stand die Zahl in einer eigenen Spalte links.

**Warum.** Der Auftraggeber: die eingerückte Zahl «schafft eine typografische
Kluft» – auf dem Handy stand die Antwort links bündig, die Frage aber hinter
der Zahl eingerückt. Die Zahl über der Frage schliesst die Kluft und bleibt
mit 15 px in der Tinte unauffällig; am Blatt geprüft bei 420 und 1280 px.

**Wirkung.** `akkordeon.css`, Kleid Faden: `summary` als Raster mit den
Bereichen `nr` / `frage` / `knopf`; Blüte und Kapsel behalten ihre Zahl in
Spalte bzw. Kreis.

## 7. September 2026 — zwei Bereiche mit eigener Farbe bekommen ihre Flächen (1.16.0)

**Was.** Bühne (`--bereich-buehne`) und Bau-Administration (`--bereich-bauadmin`)
kommen als Tokens ins Fundament, mit `--on-bereich-*` und denselben drei
Varianten wie die Sektionen (`-dunkel`, `-hell`, `-ink`), erzeugt vom selben
Rezept. Die Sektionsfarben-Seite zeigt sie als zwei Karten im Abschnitt
«Bereiche»; der Wähler der Anwendungsbeispiele kennt sie.

**Warum.** Von allen Bereichen und Teilbereichen tragen nur diese zwei eine
eigene Farbe (die Gärtnerei teilt das Landwirtschaftsgrün, alle anderen
Markenblau). Die alte Bereiche-Liste wiederholte darum Markenblau und
erklärte nichts. Beschluss des Auftraggebers: eigene Karten mit Varianten.
Bühnengold ist ein Mittelton: Weiss hält nur 3.75:1, darum steht darauf ein
sehr dunkles Braun (4.82:1), wie bei den hellen Sektionen.

**Wirkung.** Generator und Prüfer kennen zwei Familien (`sek`, `bereich`);
`--bereich` ohne Schlüssel bleibt der Standard (= Markenblau) ohne Varianten.
## 7. September 2026 — Frage und Antwort, eine Stimme (1.15.1)

**Was.** Die Antwort im Akkordeon läuft wieder in der Hausschrift (Klar,
`--t-body`), nicht mehr in der Lese-Grotesk. Mass `min(48ch,100%)` – gemessen
63 Zeichen je Zeile auf breitem Blatt – und Durchschuss 1.6 breit, 1.5 schmal.
Der Lesemodus der Kopfzeile schaltet weiterhin auf die Grotesk um.

**Warum.** Der Auftraggeber: Frage und Antwort «erscheinen wie zwei völlig
verschiedene Welten», und die Grotesk wirkte zu gross – sie ist per
`size-adjust` auf die x-Höhe der Hausschrift gehoben und steht bei gleichem
Grad optisch grösser. Zwei Wege wurden gemessen und angeschaut: Grotesk auf
17–18 px angeglichen, oder eine Stimme. Die eine Stimme löst die Disharmonie
ganz und entspricht der Hausregel (Fliesstext in der Hausschrift, Lesbarkeit
aus den Faktoren). Auf dem Handy bleibt die Zeile mit rund 39 Zeichen unter
dem Mass von G10 – darum der knappere Durchschuss nach G11.

**Wirkung.** `akkordeon.css`: `.acc-inner` ohne `.prose`, eigenes Mass und
eigener Durchschuss; Markup-Vertrag `.acc-body > .acc-inner`. Befund fürs
Regelwerk (nicht geändert): G10 nennt `min(39ch,100%)` für die Hausschrift,
das Token `--measure` steht auf 62ch für die Grotesk – beide meinen ~66
Zeichen, der Regeltext ist älter als die Schrift-Grenze.

## 7. September 2026 — das Akkordeon wird ein Modul (1.15.0)

**Was.** Das Akkordeon aus der Schau-Seite `akkordeon.html` zieht als Modul
ins Fundament: **`akkordeon.css`** und **`akkordeon.js`** neben `nav.css`/`nav.js`.
Drei Kleider auf einer Mechanik – `.bluete`, `.faden`, `.kapsel` als Klasse an
`.acc-liste` – mit vier Farbrollen (`--ak` Linie, `--ak-ink` Text, `--ak-dunkel`
Fläche für Weiss, `--ak-hell` Hauch), im Hausfall Gold, per `data-sek` in jeder
Sektionsfarbe (1.14.0). Das Skript macht natives `details`/`summary` weich
(Bloom-Kurve des goetheanum.ch-Menüs), hält je Liste eines offen, ohne dass die
Seite springt, bietet «Alle aufklappen», öffnet beim Drucken alles und stellt
den Stand danach wieder her.

**Warum.** Der Auftraggeber will das Modul in Craft übernehmen und dafür den
Code samt CSS kopieren – das geht nur, wenn er als Datei existiert und nicht im
`<style>` einer Seite steckt. Ein Modul, das in der Seite wohnt, muss für jede
zweite Seite abgeschrieben werden; ein Modul im Fundament wird eingebunden.
Die Schau-Seite bindet die Dateien jetzt selbst ein (Konformität durch
Identität) und bietet Twig-Partial, CSS, JS und einen aus `tokens.css`
gerechneten Token-Auszug zum Kopieren an.

**Wirkung.** Neue Dateien `design-system/akkordeon.css` und
`design-system/akkordeon.js`; Markup-Vertrag `.acc-liste > .acc-kopf + details.acc
> summary(.nr .frage .knopf) + .acc-body > .acc-inner`. Welches Kleid die
Website trägt, ist noch nicht entschieden – das Modul trägt alle drei, die
Wahl ist eine Klasse.

**Mechanik (hier statt auf der Seite, Beschluss 1.14.1).** Bewegung mit der
Bloom-Kurve `cubic-bezier(.32,.08,.24,1)`, 280 ms auf, 220 ms zu, bei
`prefers-reduced-motion` keine. Eines aufs Mal: schliesst sich darüber eine
Antwort, geht sie ohne Bewegung zu und der Versatz wird ausgeglichen – die
angetippte Frage bleibt an ihrem Platz (gemessen 401→401 px); liegt sie danach
unter einer klebenden Leiste, zieht die Seite nach. «Alle aufklappen» hebt das
auf; `beforeprint` öffnet alles, `afterprint` stellt den Stand her. Jede Frage
ist per `#id` verlinkbar. Fingerziel = ganze Zeile ≥44 px (B04), der Winkel ist
nur das Zeichen (das gelernte der Webfamilie: Hauptmenü, Kalender-Filter,
Klappliste). Frage in der Hausschrift Deutlich mit Durchschuss 1.25, schmal
18 px; Antwort als Mengentext in `.prose` (Schrift-Grenze, Lesemass 62ch);
Nummer tabellarisch (G25). Farben: Basis als Linie/Ring, Tinte für Nummer und
Winkel, dunkle Fläche + Weiss für die Anwahl (B01), Hauch als Grund.

## 7. September 2026 — Werkzeuge zeigen, das Repo erklärt (1.14.1)

**Was.** Die Sektionsfarben-Seite verliert den Abschnitt «Vorschläge und
Beschluss», die Bereiche-Liste, die Kontrast-Belege und alle Token- und
Skript-Hinweise in den Bildunterschriften. Das Prinzip steht jetzt in
`CLAUDE.md`: eine Werkzeugseite trägt nur, was der Anwender zum Arbeiten
braucht – Dokumentation gehört in diesen Ledger, den PR oder `CLAUDE-REF.md`.

**Warum.** Der Auftraggeber: «Dokumentation ist nicht relevant für die
Anwender.» Die Vergleichsreihen waren für die Entscheidung gebaut und blieben
nach dem Beschluss als Ballast stehen; die Bereiche-Liste wiederholte zu
achtzig Prozent Markenblau. Beides erklärte, statt zu zeigen.

**Wirkung.** Regel für alle Werkzeuge (Ausnahme: Labor- und Strategieseiten
im Backstage). Die Bereiche bleiben in der ersten Karte «Goetheanum und
Bereiche» (Markenblau); ob Bühne und Bau-Administration eigene Karten mit
Varianten bekommen, ist offen.

## 7. September 2026 — eine Sektionsfarbe braucht drei Gestalten (1.14.0)

**Was.** Jede Sektionsfarbe bekommt zwei abgeleitete Flächen und eine Tinte:
**`--sek-*-dunkel`** (matte, tiefe Fläche – Weiss drauf, 6.6 bis 7.2:1,
markenfest), **`--sek-*-hell`** (ein Farbhauch, kaum mehr als Papier – `--ink`
oder die Sektionstinte drauf; kippt im Dunkelmodus zu einem stillen, tiefen
Ton knapp über `--paper`) und
**`--sek-*-ink`** (die Sektion als Text – hell gleich dem dunklen Ton, dunkel
ein heller Hauch). Erzeugt werden sie aus einem Rezept in OKLCH
(`tools/sek-varianten.py`, idempotent, `--apply`), geprüft von
`tools/check-on-sek.py` (jetzt CI-Tor in `pruefmaschinen.yml`): 143 Kontraste,
beide Themes, alle ≥ 4.5:1. Die Seite `sektionsfarben.html` zeigt Karten statt
Tabelle (mobil-first), misst die Kontraste am gerenderten Blatt, führt sechs
Anwendungsbausteine je Sektion vor und stellt drei Stärken je Rolle
nebeneinander. Beschluss des Auftraggebers am selben Tag: Dunkel matt
(Stufe B), Hell zarter als jeder Vorschlag – ein Hauch (L 0.965), nicht
leuchtend.

**Warum.** Sechs der zwölf Basisfarben tragen kein Weiss (B01 – Landwirtschaft
2.66:1, Heilpädagogik 2.41:1), und als Fläche sind alle zu laut für ein
Kopfband oder einen Hinweiskasten. Wer eine Sektion sichtbar machen wollte,
griff bisher zu Hand-Mischungen oder liess es. Gold und Grün hatten längst
beide Gestalten (`--gold-deep`/`--gold-ink`, `--ok`/`--ok-ink`) – die
Sektionen nicht. Und weil zwölf Farben zwölfmal von Hand gemischt zwölf
Meinungen ergeben, rechnet ein Rezept: gleiche Helligkeit je Rolle, Buntheit
gedeckelt, Farbton der Sektion. Damit wirken die Sektionen als **eine Reihe**.

**Wirkung.** Regel für Werkzeuge: Kopfband/Titelfläche = `-dunkel` +
`--on-accent`; Chip/Kasten/Zeile = `-hell` + `--ink` oder `-ink`; Kicker/Link =
`-ink`; die Basis bleibt Linie, Marke und Knopf (mit `--on-sek-*`). Basisfarbe
korrigieren = `goe-orgs.js` und `tokens.css` ändern, dann
`python3 tools/sek-varianten.py --apply`. Eine andere Stärke wählen = eine Zahl
im `REZEPT` des Skripts.

## 25. August 2026 — was über allem schwebt, muss undurchsichtig sein (1.13.1)

**Was.** Die globale Feedback-Pille (`.dsnav-invite`, `nav.css`) liegt nicht
mehr auf `--bar-bg`, sondern **opak** auf `--paper`.

**Warum.** `--bar-bg` ist 90% Weiss — richtig für eine klebende Leiste, die
über dem **eigenen** Papier liegt und ein wenig durchscheinen darf. Die
Feedback-Pille aber schwebt über **beliebigem** Inhalt. Über der dunklen Bühne
des Kalender-Entwurfs mischte sich ihr Grund auf `#e8e8e8`, und der Aufruf in
`--gold-ink` fiel damit von 5.18:1 auf **4.23:1** — unter die 4.5:1 aus B02.
Gefunden hat es nicht das Auge, sondern `tools/barrierefreiheit.mjs`: dieselbe
Seite war bei ds-lint sauber, weil kein Token verletzt war. **Ein Kontrast
entscheidet sich erst am gerenderten Blatt** — und eine Fläche, die sich ihren
Grund vom Zufall borgt, hat gar keinen.

**Wirkung.** B02 hält jetzt auf jedem Grund, auf dem die Pille landen kann.
Regel für neue schwebende Elemente: **`--bar-bg` nur für Leisten, die zum
eigenen Blatt gehören; alles frei Schwebende trägt `--paper`.**

## 10. August 2026 — eine Maske, die sagt, was sie will (1.13.0)

**Was.** Vier Grundformen für Eingabemasken kommen ins Fundament:
**`.formgrid`** (drei Spalten, auf schmalem Blatt eine, mit `.span2`/`.span3`),
**`.said`** als Rückmelde-Zeile mit `.gut`/`.schlecht`, **`.field>.hint`** als
Beisatz direkt am Feld — und **`.btn[disabled]`**, damit ein Knopf keinen
zweiten Klick annimmt, solange der erste noch schreibt. Dazu eine Zeile, die
lange gefehlt hat: **`[hidden]{display:none !important}`**.

**Warum.** Das Team hat die Kosten-Maske benutzt und drei Dinge gemeldet, die
alle dasselbe Muster haben — *die Maske erklärt sich nicht*:

1. «Wo sollen die internen Stunden eingetragen sein? Was machen wir unter
   Betrag in CHF?» Die Maske fragte bei der Kostenart «Stunden intern» nach
   einem Franken-Betrag und liess den Menschen die Umrechnung machen. **Eine
   Maske, die nach dem Ergebnis fragt statt nach dem, was man weiss, ist eine
   Rechenaufgabe.** Jetzt fragt sie nach Stunden und Ansatz und schreibt das
   Ergebnis hin, bevor geklickt wird.
2. Ein Doppelklick auf «Eintragen» hat den Posten **zweimal** angelegt — die
   Zeile musste von Hand aus der Datenbank geholt werden. Der Knopf war nie
   gesperrt; keine Maske im Haus hatte dafür eine Form.
3. Es gab **keinen Weg zurück**. Wer sich vertippt, muss jemanden bitten. Ein
   offener Schreibweg ohne offenen Löschweg macht aus jedem Tippfehler eine
   Anfrage.

**`[hidden]` war die stille Falle.** Das Franken-Feld sollte im Stunden-Modus
verschwinden, blieb aber stehen: `.field{display:grid}` schlägt das schwache
`[hidden]` des Browsers. Derselbe Fehlertyp wie die Löcher in der Skala vom
Vortag — das Fundament setzt `display` auf Klassen und muss darum auch sagen,
wie Verstecken gewinnt. **Gefunden beim Anschauen der Seite, nicht beim
Rechnen**; im selben Blick fiel auf, dass die Kosten-Seite seit dem Cockpit-Umbau
noch `.tile` benutzte — eine Klasse, die es nicht mehr gab. Ihre drei Zahlen
standen seither unformatiert untereinander, und keine Maschine hat es gesehen.

**Wirkung.** `base.css` (`.formgrid`, `.said`, `.field>.hint`,
`.btn[disabled]`, `[hidden]`), `contract.json` (Version). Die Kosten-Seite
nutzt die Grundformen und die Hausrolle `.kennzahl`; die Aktivitäten-Maske
bekam dieselbe Klick-Sperre. Backend: Stunden bleiben als Stunden erhalten
(`stunden`, `ansatz`), eine Zwei-Minuten-Sperre gegen den doppelten Klick und
ein Löschweg, der so offen ist wie der Schreibweg.

## 9. August 2026 — die Skala hatte Löcher, und CSS schwieg darüber (1.12.0)

**Was.** Die Abstands-Skala ist lückenlos geworden (`--s5:20px`, `--s7:28px`),
die fünf Schnitte tragen jetzt ihre Hausnamen als Token (`--w-klar`, `--w-laut`,
`--w-ruhig`; die alten `--w-text`/`--w-strong` bleiben als Zweitnamen gültig),
und zwei Grundformen kamen dazu: **`.kennzahl`/`.kennzahlen`** (eine Fläche, die
EINE Zahl trägt: Label, Wert, Notiz — mit grosszügigem Innenabstand) und
**`.chip.ton`** (ein Chip, der einen ganzen Satz tragen kann). Neue Regel
**DS10**: jedes `var(--x)` muss ein definiertes Token treffen.

**Warum.** Im Sommer-Bericht klebte die Schrift auf den Kartenkanten. Der Grund
war kein Gestaltungsfehler, sondern ein Systemfehler: `--s5` existierte nicht.
Die Skala ging 4 · 8 · 12 · 16 · — · 24 · — · 32, und **CSS löst ein unbekanntes
Token still zu nichts auf** — aus `padding:var(--s5)` wurde `padding:0`, ohne
Fehler, ohne Warnung. **13 Dateien im Repo** griffen nach genau diesen beiden
fehlenden Sprossen. Wer eine Skala mit Löchern baut, baut eine Falle: Die
fehlende Sprosse ist die, nach der gegriffen wird.

Derselbe Fehlertyp eine Ebene höher: Das Haus spricht von «Klar» und «Laut», die
Token hiessen `--w-text` und `--w-strong`. Wer das Hauswort benutzte, griff ins
Leere — DS10 fand es sofort an drei Stellen in der Werkzeugpost, wo seit je die
falsche Strichstärke stand. **Ein Design-System, dessen Vokabular vom
Sprachgebrauch des Hauses abweicht, erzeugt genau solche Fehler.**

**Und die Pillen.** Dieselbe Frage, nächste Ebene: Die pillenförmigen Rollen
trugen zwischen **0,14 und 0,67 em** senkrechter Luft — also gar keine Regel.
Die engsten (`.zeichen`, `.ev-kanal`: 2 px bei 14 px Schrift) klebten sichtbar
an der Rundung. Neu gibt es dafür ein Grundmass, **in em statt in Pixeln**, damit
die Luft mit dem Schriftgrad wächst: `--pille-y:0.4em`, `--pille-x:0.95em`.
Waagrecht knapp ein Geviert, weil eine volle Rundung die Ecken frisst — was beim
Rechteck noch Abstand ist, berührt im Oval schon die Kurve. Alle Pillen sitzen
jetzt auf diesem Mass; die Marke behält ihre ratifizierte optische Verschiebung
nach oben, nur proportional statt absolut.

**Und eine fehlende Zweitfarbe.** Beim Nachmessen fiel das grüne Merkzeichen
«trägt die Aktion» mit **4,14:1** durch. Grund: Gold hatte seit je zwei
Gestalten — `--gold` als Fläche, `--gold-ink` als Schrift —, Grün nur eine.
`--ok` ist als Fläche definiert («Weiss drauf»); wer es als Schrift nahm, fiel
unter AA. Neu: **`--ok-ink`** (hell `#39703f`, dunkel `#6bac76`), gerechnet
gegen den grünen Ton auf Papier und auf Karte. *Eine Signalfarbe braucht beide
Gestalten, sonst wird die Fläche als Schrift missbraucht.* Die getönten Marken
mischen jetzt zudem über `--paper` statt über `transparent` — sonst nehmen sie
die Farbe der Fläche an, auf der sie zufällig liegen.

**Wirkung.** `tokens.css` (Skala geschlossen, Schnitt-Namen, Pillen-Luft,
`--ok-ink`), `base.css`
(`.kennzahl`, `.kennzahlen`, `.chip.ton`), `contract.json` (DS10),
`tools/ds-lint.py` (`check_tokens`). Das Cockpit gab seine zwei lokalen
Karten-Kopien und die eigene `.pill` ab und nutzt die Grundformen. Score
zurück auf 100 Prozent — mit einer Wache mehr.

## [1.10.0] – 2026-08-04

### Der Seitentitel wird eine Rolle des Fundaments
- **Was:** Neue kanonische Rolle `.hero h1, .lead-title` in `base.css` — sie
  setzt Schrift, Schnitt, **Durchschuss (`--lh-tight` 1.15)** und **Laufweite
  (0)**. Aus 16 Seiten wurden die lokalen `line-height`- und
  `letter-spacing`-Angaben am Titel entfernt; `font-size` und `max-width`
  bleiben bei der Seite. `lead-title` steht jetzt im Vertrag unter
  `rollen.kanonische_klassen`, damit DS04 künftige Alleingänge meldet.
- **Warum:** Jede Seite hatte ihren Titel selbst gesetzt — Durchschuss zwischen
  **1.02 und 1.08**, durchweg mit negativer Laufweite (`-.01em`). Zweizeilige
  Titel stiessen dadurch zusammen, Umlaute berührten die Zeile darüber. Auch
  `design-system/starter.html` trug die enge Fassung, hat sie also an jede neue
  Seite weitergegeben — die Abweichung pflanzte sich fort, statt aufzufallen.
  Aufgefallen am Sommer-Cockpit auf dem Handy (Rückmeldung 4.8.2026).
- **Wirkung:** Titel atmen überall gleich; der Grad bleibt eine Satzentscheidung
  der Seite, der Durchschuss ist Hausregel. Wer künftig `.lead-title` lokal
  redefiniert, wird von `ds-lint` (DS04) darauf hingewiesen.

## [1.9.5] – 2026-07-17

### Gedämpfter Text auf Blau bekommt ein Token: `--on-accent-muted`
- **Was:** Neues Token `--on-accent-muted:#ccdff1` — gedämpfter Sekundärtext
  (Fusszeile, Meta, Kontaktzeile) auf Blau-Flächen. **4.7:1 auf `--blue`**
  (WCAG AA); `--on-accent` bleibt Weiss für die Haupt-Beschriftung. Dunkel
  erbt (on-accent-Flächen bleiben dunkel genug, Beschluss 1.9-Serie).
- **Warum:** Die PowerPoint-Vorlage setzte die Fusszeile/Kontaktzeile auf den
  blauen Folien in `#9CC3EC` = **3.47:1** (13pt, kleiner Text → unter 4.5:1,
  B02-Verstoss). Statt lokal einen Wert zu erfinden ins Fundament genommen —
  der Atem: die Rand-Verbesserung gilt ab jetzt überall.
- **Wirkung:** `tokens.css` (`--on-accent-muted`); genutzt in der PP-Vorlage
  (Folien 1/5/15, Layouts 2/3). Keine neue Regel — B02 endlich auch für
  gedämpften Text auf Akzent erfüllbar, ohne Weiss zu erzwingen.


### Menü: Strukturtitel von Laut auf Deutlich
- **Was:** Schubladen-Titel, Bereichs-Titel und aktiver Eintrag laufen jetzt in
  **Deutlich (580)** statt Laut (680). Die Laute ist die Inline-Fettung —
  Strukturtitel tragen laut Hausregel Deutlich; bei 15–17px rendert 680
  zudem klumpig (Befund Auftraggeber, iPhone-Screenshot 11. Juli 2026).
- **Wirkung:** nav.css (`.dhead .t`, `.dsnav-group>summary`,
  `.dsnav-link.is-active .tt`); keine neue Regel — eine Regel angewandt.

## [1.9.3] – 2026-07-10

### Status-Marker in der Intern-Schublade
- **Was:** Im Intern-Modus zeigt jeder Menü-Eintrag rechts leise seinen
  Manifest-Status (Beta · Entwurf · intern · geparkt) — Meta-Rolle in der
  Lese-Grotesk, `--t-micro`, gedeckt. **Live bleibt unmarkiert** (G03: der
  Normalfall trägt kein Zeichen — was live ist, erkennt man am reinen Titel).
  Das öffentliche Menü bleibt wortlos («koordiniert, erklärt nicht»).
- **Warum:** In der Pflege-Ansicht war nicht unterscheidbar, was draussen
  sichtbar ist und was noch Werkstatt ist.

## [1.9.2] – 2026-07-10

### Engine geschärft: Vertrags-Ausnahmen greifen auch für Wurzel-Ordner
- **Was:** `ds-lint` prüfte Dateien unter `assets/` trotz Ausnahme im Vertrag –
  die Staged-Pfade kommen relativ (`assets/…`), die Substring-Ausnahme stand
  absolut (`/assets/`). Der Checker normalisiert Pfade jetzt vor dem Abgleich;
  auch die neuen Versand-Ausnahmen (`mails/`, `export/`) greifen damit in
  beiden Pfadformen.
- **Warum:** Aufgefallen an der neuen Druckquelle
  `assets/merkblaetter/src/warum-ohne-bilder.html` (Druck-Artefakt: Papier ist
  immer weiss, gehört nicht in den Theme-Geltungsbereich).
- **Wirkung:** Geltungsbereich verhält sich wie beschlossen; keine neue Regel.

## [1.9.1] – 2026-07-10

### Die Maschinen bekommen Zähne: CI-Gate + blockierender Hook + Export-Konvention
- **Was:** (1) **CI-Gate** `.github/workflows/pruefmaschinen.yml` — typo-check
  (`--all`) und ds-lint laufen auf jedem PR und auf `main`; Schwere ‹fehler›
  macht den Lauf rot. (2) Der Commit-Hook führt `ds-lint --staged` jetzt
  **blockierend** (das vorgesehene `|| true` ist entfernt — der Score stand
  bei 100 %). (3) **Export-Konvention:** erzeugte Versand-/Export-Artefakte
  wohnen in Ordnern namens `mails/` oder `export/`; diese sind generell vom
  Vertrag ausgenommen (ersetzt die Einzel-Ausnahme für den Mail-Editor).
- **Warum:** Beschluss Auftraggeber, 10. Juli 2026, nach dem Score-Einbruch
  durch die publizierten Versand-Mails: <q>automatisch mergen, wenn die
  Prüfmaschinen grün sind</q> ist erst durchsetzbar, wenn die Maschinen
  unabhängig vom lokalen Hook auf jedem PR laufen.

## [1.9.0] – 2026-07-10

### Spielraum & Welten + warme Stilprobe + Geltungsbereich Versand-Artefakte
- **Was:** (1) Neuer Schaufenster-Abschnitt <q>Spielraum &amp; Welten</q> —
  Dramaturgie-Leitsatz (ein Hero, eine Primärhandlung je Blick, eine
  Akzentfläche je Bildschirmhöhe) und die Fest/Frei-Tabelle je Rolle
  (Varianz-Entwurf, Ansätze 1–3, Beschluss 10. Juli 2026). (2) Welten-Mechanik
  in `tokens.css`: `data-welt` schaltet Stimmungs-Tokens, nie Regeln; erste
  Welt **warm** als Stilprobe (`stilprobe-warm.html`, Experiment): warmes
  Papier #fbf7ee/#f3edde mit nachgedunkelten Tinten (muted 5.0:1, gold-ink
  5.1:1 auf der Karte — ohne Nachdunkeln fielen beide unter 4.5:1).
  (3) `geltungsbereich`: `apps/mail-editor/mails/` sind Versand-Artefakte
  (E-Mail-HTML kann keine Includes tragen) — ausgenommen wie /assets/.
  (4) `ds-lint` meldet ds-ok-Marker im falschen Format (DS00-Hinweis);
  Signatur-Generator-Marker korrigiert, `btn-mini` auf ≥14px.
- **Warum:** Score-Einbruch auf 67 % durch 20 publizierte Versand-Mails
  (PR #341) + Marker-Wiederholungsfehler — der Vertrag kannte die
  Artefakt-Klasse ‹Versand-HTML› nicht. Warme Flächen: Auftraggeber-Wunsch
  nach einer Stimmungs-Variante aus dem My-Goetheanum-Entwurf.
- **Ausserdem:** Die Perspektive `my-goetheanum.html` und das Lockup
  `goetheanum-my.svg` sind entfernt (Entscheid: noch zu intern); die
  App-Schale-Rollen bleiben im Fundament.

## [1.8.0] – 2026-07-10

### App-Schale (aus dem My-Goetheanum-Entwurf aufgenommen)
- **Was:** Neue Rollen in `base.css` — `app` (Seitenleiste + Inhaltsfläche,
  mobil als Band), `sidenav` (Bereichs-Navigation; Auswahl = dunkles Gold +
  Weiss, B01; Gruppen-Etikett als Kicker, G05), `cardgrid`, `card .cfoot`,
  `leer` (Leerzustand). Neues Lockup `assets/logos/goetheanum-my.svg` aus der
  Logo-Engine (DS08).
- **Warum:** Der Entwicklerentwurf des Mitglieder-Portals ‹My Goetheanum›
  zeigt einen echten Bedarf, den das Fundament nicht deckte — und riet darum
  die Gestalt: Versal-Zwischentitel (G05), Gold-Etiketten bei ≈2:1 (B02),
  Weiss auf Hellgrün ≈2:1 (B01/B02), erfundenes Marken-Lockup (DS08).
- **Wirkung:** `perspektiven/my-goetheanum.html` setzt denselben Schirm aus
  den Fundament-Rollen — regelkonform durch Konstruktion. Dazu
  `docs/gestaltungsspielraum-entwurf.md` (Foto-Richtlinie in drei Richtungen,
  vier Varianz-Ansätze — Entwurf, zu ratifizieren). `contract.json` →
  Version 1.8.0, Rollen ergänzt.

## [1.7.2] – 2026-07-09

### Badge-Sitz + leisere Modi-Reihe (Rückfluss aus der Kopfzeile)
- **Was:** Das `.badge`-Rezept in `base.css` setzt die Tinte jetzt optisch
  mittig ins Oval: `line-height:1` plus ein Hauch mehr Luft oben — Statuswörter
  haben meist keine Unterlängen, zentriert man das Geviert, hängt die Tinte
  oben (nachgemessen: vorher 26/36, jetzt 30/32 Gerätepixel bei 4×). Die
  Beta-Pille der Kopfzeile baut nun auf diesem Rezept auf und läuft in der
  Lese-Grotesk statt der Display-Schrift (Badge/Chip-Regel des Fundaments);
  eigen bleibt nur die Gold-Färbung (ein Merkmal, G01).
- **Ausserdem:** Die Modi-Reihe in der Schublade ist leiser und luftiger —
  Konturen auf Papier statt Füllflächen, aktiver Zustand = Gold-Kontur +
  Gold-Tinte statt Doppel-Ring (G03), mehr Abstand (`--s3`/`--s4`). Die
  Theme-Taste heisst kurz «Dunkel»/«Hell» (im Gruppenkontext ‹Anzeige-Modi›
  eindeutig), Zeichen sind vor Flex-Schwund geschützt — so trägt die Reihe
  auch 320px-Schirme ohne Überlauf.

## [1.7.1] – 2026-07-09

### Mobil-Kopfzeile entlastet: Modi-Schalter ziehen in die Schublade
- **Was:** Auf ≤720px verlassen die drei Modi-Schalter (Lesemodus ·
  Hell/Dunkel · Teilen) die Leiste und stehen als eigene Reihe `.dmodes`
  ganz oben in der Schublade — mit Wort **und** Zeichen beschriftet,
  Ziele ≥44px (B04), Beschriftung `--t-small` (B03). Die Leiste trägt
  mobil nur noch Marke + Menü. `nav.js` hält beide Button-Sätze
  (Leiste/Schublade) im selben Zustand; Desktop unverändert.
- **Warum:** Nach dem Zuwachs auf drei Schalter blieb zwischen Marke und
  Menüknopf kein Platz mehr zum Dreifachtipp (Feedback-Geste); die
  reinen Zeichen-Knöpfe waren mobil zudem schwer deutbar.

## [1.7.0] – 2026-07-09

### DS09: Fundament relativ einbinden – Wächter gegen den Custom-Domain-Bruch
- **Was:** `starter.html` und `starter-artikel.html` binden das Fundament jetzt
  RELATIV ein (Root-Beispiel, Pfadtiefen dokumentiert); der irreführende
  Kommentar («funktioniert von JEDEM Ort») ist korrigiert. Neuer Vertrags-Punkt
  **DS09** (fehler): absolute `phtok.github.io/goeloggen/(design-system|assets)`-
  URLs und absolute `data-root` meldet der Checker.
- **Warum:** Vorfall Signatur-Generator (PR #291) – die aus dem Starter
  übernommenen Absolut-URLs laufen auf der Custom-Domain ins Leere
  (Auslieferung im Root, kein /goeloggen/-Präfix) → Seite komplett ungestylt.
  Übergabe-Papier: `docs/learnings-starter-pfade.md`.
- **Nebenbefund:** Die Artefakt-Marker der Signatur-Vorschaubühne standen im
  falschen Format (`/* ds-ok: … */` statt `# ds-ok`) – der Checker sah die
  Ratifizierung nicht. Format korrigiert; Audit wieder 100 % über 40 Seiten.

## [1.6.0] – 2026-07-08

### Werkzeugwissen + Druck-Tinte (Rückfluss aus dem Kartentool)
- **Was:** Neues Dokument `design-system/werkzeugwissen.md` — Konstruktions-
  regeln für Werkzeuge, die drucken und zeichnen: kein `text-anchor="middle"`
  in Export-SVGs (Breiten selbst messen: TTF-Vorschubtabellen, Canvas nur als
  Rückfall), Icons auf die Tintenbox statt die viewBox zentrieren,
  Kontur-Zwillinge entfernen + Fugendichtung (`stroke` = `fill`) für
  Flächengrafik, `.step-num`-Masse im Kartenmassstab (Grad 0.5 × ⌀,
  Piktos 1.26 × r), Token-Treue auch für Abstände (erfundene `var(--…)`
  fallen still auf 0). Dazu neues Token **`--ink-print-leise:#6e6f6a`** —
  leises Strukturbeiwerk auf Papierweiss, gerechnet 5.07:1 (B02-fest).
- **Warum:** 18 Rückmelderunden Kartentool haben Bauwissen erzeugt, das
  sonst in der Session verloren ginge (Entscheid Auftraggeber, 8. Juli 2026:
  ‹direkt einarbeiten›). Der `--s5`-Vorfall (nicht existierendes
  Abstands-Token, still auf 0 zurückgefallen) zeigt eine DS02-Lücke —
  Kandidat für `ds-lint`: unbekannte `var(--…)`-Namen melden.
- **Wirkung:** Werkzeugwissen ist Fundament (gilt für jedes künftige
  Druck-/Grafik-Werkzeug); `--ink-print-leise` ersetzt den bisher nur im
  Kartentool notierten Hex-Wert. `contract.json` → Version 1.6.0.
## [1.5.0] – 2026-07-06

### Bild-Ebene + Logo-Disziplin (DS08)
- **Was:** Neue Rollen für Fotografie in `base.css` — `hero-bild` (Bild-Hero,
  Text nur auf dem theme-festen dunklen Schleier, Kontrast gerechnet),
  Bild-Träger in `teaser .thumb`, `event .thumb` und `poster` (object-fit,
  Fläche `--soft` als Rückfall). Dazu `brand .lockup` (erzeugtes Logo) und
  zwei neue Marken-Assets aus der Logo-Engine: `assets/logos/goetheanum-logo.svg`
  (das offizielle Logo) und `goetheanum-marke.svg` (blanke Marke). Neue Regel
  **DS08**: Die Marke kommt aus dem Logo-Generator — das Favicon
  (`goetheanum-mark-blue.svg`, Kachel) steht nie als `<img>`; `ds-lint` prüft das.
- **Warum:** Auftraggeber-Befund — die Nachbauten waren bildlos und ohne Heros
  (<q>zu viel System-Indiz, wenig Gestaltung</q>), und Seitenköpfe erfanden
  Marken-Lockups (Favicon-Kachel + Text) statt den Logo-Generator zu nutzen.
- **Wirkung:** Die vier Perspektivseiten tragen die echten Motive ihrer
  Startseiten (site-eigene CDNs: Hero, Veranstaltungs-, Artikel- und
  Poster-Bilder, Heft-Cover); goetheanum.ch-Nachbau und interner Hub führen
  das erzeugte Logo/Lockup. `contract.json` → Version 1.5.0, Rolle
  `hero-bild` + Regel DS08 ergänzt.

## [1.4.0] – 2026-07-06

### Perspektiven als Vollnachbauten + schwebende Leiste
- **Was:** Neue Rolle `fab` in `base.css` — schwebende Leiste unten rechts
  (zurück ins System · Original in neuem Fenster, Fingerziele ≥44px).
  Die vier Perspektivseiten sind jetzt **vollständige Nachbauten der echten
  Startseiten** (Inhalte von goetheanum.ch, dasgoetheanum.com, goetheanum.tv,
  anthroposophie.org, Stand 6. Juli 2026): ganze Webseite mit Kopfzeile,
  Aufmacher, Rubriken/Kalender/Katalog und Fusszeile — ausschliesslich aus
  Fundament-Rollen gesetzt.
- **Warum:** Auftraggeber-Entscheid — keine Beispiele, keine Reduktionen,
  keine erfundenen Inhalte: ein Erlebnis-Eindruck, wie die Seite mit dem
  System durchgearbeitet aussähe; das Original ist einen Klick daneben.
- **Wirkung:** `perspektiven/*.html` sind Erlebnis-Seiten ohne Hub-Rahmen
  (Nachbau-Kopfzeile je Seite mit `# ds-ok` ratifiziert). Die
  Gegenüberstellungs-Rollen `mockpair`/`mock` (1.3.0) bleiben im Fundament
  verfügbar. `contract.json` → Version 1.4.0, Rolle `fab` ergänzt.

## [1.3.0] – 2026-07-06

### Gegenüberstellung «heute ↔ mit dem System» (aus den Perspektivseiten aufgenommen)
- **Was:** Neue Rollen `mockpair`/`mock` (+ `.ist`/`.soll`, `figcaption`, `.screen`)
  in `base.css` — zwei Fenster auf dieselbe Startseite, links der heutige Zustand
  als Artefakt (fremde Schriften/Farben mit `# ds-ok` ratifiziert), rechts derselbe
  Inhalt aus den Fundament-Rollen.
- **Warum:** Die Perspektivseiten waren einseitig Befund und Analyse. Ihre Aufgabe
  ist zu **zeigen**, wie die Seiten aussähen, wenn sie mit dem Design-System
  durchgearbeitet würden — der direkte Ist↔Könnte-Vergleich je Startseite leistet
  das; die Befund-Zahlen bleiben als Beleg darunter.
- **Wirkung:** Alle vier `perspektiven/*.html` beginnen mit der Gegenüberstellung
  ihrer Startseite. Der Bau-Workflow («So baust du ein neues Werkzeug») zog von der
  Schauseite in den internen Hub (`start/#bauen`) — die Schauseite zeigt das System,
  die Werkstatt zeigt das Bauen. `contract.json` → Version 1.3.0, Rollen ergänzt.

## [1.2.0] – 2026-07-06

### Webfamilie-Komponenten + Bühne (aus dem Vier-Seiten-Befund aufgenommen)
- **Was:** Neue kanonische Rollen in `base.css` — Artikel-Anatomie (`crumbs`,
  `byline`, `lit`, `bio`, `related` + `starter-artikel.html`), `teaser` (+ `.stack`),
  `event` + `filterbar`, `stage`/`mrow`/`mtile`/`live` (Medienkatalog),
  `person`, `subscribe`, `.ds-footer .fcols`. Neue theme-feste Tokens
  `--stage-bg/-bg2/-ink/-muted/-veil` (Kontraste gerechnet: ink 15.3:1,
  muted 8.2:1).
- **Warum:** Analyse der vier grossen Goetheanum-Webseiten
  (`docs/webfamilie-befund.md`): ihre Inhaltsmuster (Artikel, Kalender,
  Medienkacheln, Newsletter) fehlten dem Fundament; ihre wiederkehrenden
  Fehler (Versal-Bylines, <14px, Kontrast-Fails, lh 1.4) zeigen, welche
  Regeln die Rollen einbauen müssen.
- **Wirkung:** Vier Testseiten unter `perspektiven/` zeigen je Original den
  Nachbau, den gerechneten Vorher-nachher-Befund und den Einbau-Weg
  (Craft/WordPress/Uscreen). Schaufenster-Abschnitt «Perspektiven des
  Design-Systems». `contract.json` → Version 1.2.0, Rollen ergänzt.

## [Unveröffentlicht]

### Kartentool-Learnings aufgenommen (Werkzeugwissen + belegte Werte)
- **Was:** Nachschlagewerk Werkzeugwissen (SVG-/Druck-Export-/
  UI-Bauwissen); Quelle `docs/learnings-kartentool.md` (14 verifizierte
  Testrunden). Kernregeln: Icons auf die **Tintenbox** zentrieren (Einzeldateien
  tragen keine einheitliche viewBox — nachgeprüft: nur 46 von 81 Dateien haben
  die Standardbox); in Export-SVGs **kein `text-anchor="middle"`** und **keine
  OpenType-Feature-Abhängigkeit** (PDF-Renderer ignorieren beides — Breiten und
  Ziffern-Slots selbst setzen); Kontur-Zwillinge entfernen, Fugen mit
  Eigenkontur in Füllfarbe dichten.
- **Belegte Werte:** Druck-Tinten auf Papierweiss gerechnet — `#4e4f4a` 8.26:1,
  `#6e6f6a` 5.07:1 (Token-Kandidat `--ink-print-leise`, aufgenommen sobald ein
  zweites Druckwerkzeug ihn braucht), `#767771` 4.52:1. Die Hausschrift führt
  `tnum`/`lnum` als GSUB-Features — G25 über `font-variant-numeric` greift auch
  in der Hausschrift (nur nicht im PDF-Export).
- **Bestätigt:** Die `.step-num`-Sitzkorrektur (translateY 8 %) wurde im
  Kartentool unabhängig pixelverifiziert; Vermerk am Kommentar in `base.css`.
- **Ratifiziert und umgesetzt (9. Juli 2026):** Icon-Einzeldateien per
  `normalize_icon_svgs.py` aus dem Font regeneriert — einheitliche Em-Box
  `-2 -1002 1004 1004` (Ausnahme Wortmarke, proportional), ‹mit Text›-Waisen
  entfernt (nur Webfont), PNG/PDF/ZIP neu, idempotent (Hash-verifiziert).
  Sichtprüfung: Rollstuhl jetzt font-wahr statt eigenbox-vergrössert.
  Die parallel entstandenen zwei Werkzeugwissen-Papiere (docs/ und
  design-system/) sind zu EINEM konsolidiert: design-system/werkzeugwissen.md.

### Neuer Font «Goetheanum Pfeile» – Pfeile & Kompass ohne PUA-Umweg
- Die Pfeile/Kompass lagen im Icon-Font im **Zeichen-Privatbereich (PUA)** und waren
  nur über Option/Alt oder die Glyphenpalette erreichbar; eine installierbare
  Tastaturbelegung dafür existierte nie (sie stand nur im Beipackzettel). Statt eine
  fehleranfällige, hier nicht testbare `.keylayout`/`.klc` zu erfinden: **ein eigener,
  schlanker Font**, der dieselben 20 Zeichen auf **normale Tasten** legt (Belegung ‹A›,
  Beipackzettel-treu; Umschalt = fett). Schrift wählen, Taste tippen – kein Option,
  kein PUA, keine Belegungsdatei. Die PUA-Codepoints bleiben zusätzlich erhalten.
- **Reproduzierbar über die Font-Skripte**: `tools/goetheanum-fontfix/build_pfeile.py`
  leitet «Goetheanum Pfeile» aus dem Icon-OTF ab (Subset auf 20 Glyphen, Grundtasten +
  PUA belegt, Metadaten/Lizenz/Version aus dem Icon-Font geerbt), baut otf · woff ·
  woff2 · Office-TTF und legt alle vier Dateien ins Office-ZIP und ins Komplett-Bündel
  `Goetheanum-Schriften-v2.7.zip`. `build_office_ttf.py` kennt den Font jetzt (JOBS).
- **Web** (`icons.html`): der zweite Tastatur-Reiter heisst statt ‹Option/Alt› nun
  **‹Pfeile & Kompass›** und rendert die Zeichen aus dem neuen Webfont auf ihren
  Grundtasten (Klick kopiert weiterhin). Eigene Download-Karte (woff2/OTF).
- Verifiziert: Font lädt im Browser, `6 t u h` → ↑ ← → ↓, `T` kopiert U+E267; Office-TTF
  (glyf) und beide ZIPs enthalten den Font; Score 100 %.

### Icon-Font: fehlende Glyphe «Goetheanum Badge invers» repariert
- Ein Font-Audit (alle Schriftdateien, nicht nur die eine) zeigte: 44 von 45
  benannten Icons waren korrekt belegt, aber **«Goetheanum Badge invers» hatte in
  keiner Datei einen eigenen Glyph** — U+0031 (`1`, die im Beipackzettel S.2
  dokumentierte Taste) fiel auf den generischen Füll-Glyph zurück; der Fehler
  steckte schon im Quell-Master `v0.3.35.otf`. `icons.json` wies das Zeichen zudem
  falsch auf U+0022 aus (Widerspruch zu Beipackzettel und `build.py`).
- **Repariert über die Font-Skripte** (nicht freihändig): `fontfix.add_badge_invers`
  (CFF) und `add_badge_invers_ttf` (glyf/cu2qu) holen die Kontur aus der Einzeldatei
  `goetheanum-badge-invers.svg` (deren `d` liegt in y-oben-Fontraum, importiert also
  mit Identität wie der positive Badge auf `2`). `apply_badge_invers.py` setzt sie
  idempotent in **otf · woff · woff2 · Office-TTF** und packt **Office-TTF.zip** und
  **Schriften-v2.7.zip** neu; `build_icons()` ruft die Reparatur mit, damit ein
  Voll-Rebuild korrekt bleibt. `icons.json` auf U+0031 berichtigt.
- Verifiziert: alle 8 Font-Artefakte 45/45, U+0031 belegt; im Web zeigt Taste `1`
  jetzt den Kreis-Badge (invers), `2` den Quadrat-Badge — Beipackzettel-treu.

### Aufgeräumt: interne Vergleichsstudie entfernt
- `apps/logos/preview-hinweise.html` gelöscht — eine nirgends verlinkte Studie
  (‹Aktuell · Vorschlag›), die als einzige Seite den ds-lint-Score auf 97 % zog
  (var()-Fallbacks, Artefaktfarben, ein 6.5px-Text). Score wieder **100 %**.

### Icons-Tastatur: Option/Alt-Ebene wiederhergestellt (Pfeile & Kompass)
- Die Web-Tastatur zeigte nur die **Grundebene** (Buchstaben → Piktogramme) und
  liess die 20 Pfeil-/Kompass-Zeichen fallen: ihre Codepoints liegen im Privat-
  bereich (PUA), passen also auf keine Buchstabentaste – und ihre **dokumentierte
  Tastenlage (Beipackzettel Seite 3: Option/Alt) war nie in Daten kodiert**, nur
  im PDF. Jetzt ein **Ebenen-Umschalter** (Grundebene ⇄ Option/Alt): die zweite
  Ebene setzt Pfeile und Kompass auf ihre belegten Tasten (⌥6=↑, ⌥T=←, ⌥U=→,
  ⌥H=↓, ⌥2/0/Q/E/O/Ü/S/Ö=gebogen, ⌥Y/X/C/V=Kompass). Jede Zeichen-Taste ist ein
  Knopf – **ein Klick kopiert das Zeichen** (fürs Web), Rückmeldung per Toast.
  Ersetzt die vorige Behelfs-Palette; das Verlorene ist zurück auf der Tastatur.

### Neues Werkzeug: Goetheanum Editor (v1) – die Typografie-Engine läuft im Browser
- **`assets/typografie/goe-typo.js`** (neu, wiederverwendbar): führt
  `typo-regeln.yaml` clientseitig aus – lädt und parst die Regeln (derselbe
  Mini-Parser wie `tools/typo-check.py`, eine Quelle der Wahrheit), behebt
  ‹fehler›-Regeln automatisch und findet ‹empfehlung›-Regeln als offene Fragen
  mit Kontext-Ausschnitt fürs Verständnis. Kein Rendering/DOM – reine Engine,
  gedacht als Baustein fürs Backend weiterer Goe-Webseiten (v3-Ziel).
- **`apps/editor/`**: Text einfügen, ‹Prüfen› klicken – Eindeutiges (Anführung,
  Striche, Auslassung, Ziffern-Gruppierung, Leerzeichen) wird sofort gesetzt und
  im Protokoll ‹Angewandt› nachvollziehbar; offene Fragen (Abkürzungs-Spatium,
  Prozent/Einheiten-Spatium, Uhrzeit, Minus) erscheinen als Marginal-Karten mit
  Übernehmen/Lassen und Sammel-Übernahme. Die 10 Urteils-Regeln (`pruefung: lm`
  – Schriftwahl, Auszeichnung, Zeilenmass, Kontrast …) sind ausgewiesen, aber
  noch nicht automatisiert (kein LLM in v1) – folgt als Lektorat-Pass (v2).
- Eintrag in `tools.json`/Startseite/Menü (Kategorie Werkzeuge, Priorität nach
  Signatur). Score bleibt 100 % (konform).

### Icons-Tastatur: das Piktogramm wird zum Held der Taste
- Die Icons standen mit 26px verloren in 48px-Tasten, der Buchstabe konkurrierte
  darunter. Jetzt: ruhigere Tasten (62px), Icon mittig bei 40px, Buchstabe als
  kleine Legende in der unteren rechten Ecke (wie das Zweitzeichen echter Tasten),
  leere Tasten treten zurück (`opacity`). *Wirkung:* die Piktogramme führen den
  Blick statt zu verschwimmen; hell/dunkel bleibt tokengetrieben (`--ink`).

### `.step-num` optisch nachjustiert · Links im Fliesstext sichtbar
- **`.step-num` neu vermessen** (`base.css`): der erste Fix (line-height:1 +
  Flex-Zentrierung) zentrierte die *Line Box*, nicht die Zeichen-Tinte – Nutzer-
  Feedback bestätigte, dass Ziffern sichtbar zu hoch sassen. Per Pixel-Analyse
  (Screenshot der echten Schrift, Tinten-Bounding-Box vs. geometrische Kreismitte)
  UND Font-Metriken (hhea ascent 750/descent −250 vs. Ziffern-Tintenmitte ≈ 330/1000)
  übereinstimmend auf **8 % `translateY`** des inneren Zahl-Elements bestimmt –
  zwei unabhängige Methoden, ein Ergebnis. *Wirkung:* Ziffer sitzt jetzt tatsächlich
  mittig, nicht nur nach CSS-Theorie.
- **`.step-num` Gold als Hausfarbe**, `.blue` als benannte Ausnahme (vorher
  umgekehrt). *Warum:* Gold ist bereits die Auswahl-/Markierungsfarbe im System
  (Auswahl-Pille, `.seg button[aria-pressed]`) – zwei blaue Kugeln neben einer
  goldenen wirkten wie ein Fehler, nicht wie Absicht. *Wirkung:* Schritt-Marken
  sind einheitlich Gold; Blau bleibt für Vergleichsseiten verfügbar, die Alt/Neu
  bewusst farblich trennen wollen.
- **Links im Fliesstext sichtbar** (`base.css`): der globale Reset (`a{color:
  inherit;text-decoration:none}`) machte Links in Absätzen/Listen/Hinweisen
  farblich und optisch identisch mit umgebendem Text – ein Link in den
  Logo-Hinweisen wurde dadurch für nicht vorhanden gehalten. *Wirkung:* `p a`,
  `li a`, `.note a` etc. bekommen Gold + dezente Unterstreichung (DS05 nimmt
  Links vom Unterstreich-Verbot ausdrücklich aus – das ist Link-Konvention,
  keine Betonung).

### Feinschliff: Karussell zentriert · Such-Synonyme · PowerPoint-Bild
- **Karussell-Inhalt zentriert** (Thumb + Text als Gruppe mittig) statt linksbündig.
- **Suche mit Synonymen**: pro Werkzeug `such`-Begriffe in `tools.json`; die Menü-Suche
  matcht Titel **und** Synonyme. So findet ‹Farben› jetzt Sektionsfarben **und**
  Design-System (wo Marken-/Neutralfarben wohnen).
- **PowerPoint** bekommt ein eindeutiges Bild (Mini-Folie mit Titelzeile) statt des
  mehrdeutigen ‹P›.

### Burger flach (Modell B) – keine Kategorien öffentlich
- Das Menü zeigt öffentlich **eine priorisierte Liste** (wie die Startseite), mit
  ‹Startseite› oben – keine aufklappbaren Welten mehr. Die Suche übernimmt das Finden.
- **Backstage** bleibt unverändert nach Welten gruppiert hinter dem geheimen
  Dreifach-Klick. Reihenfolge in `FLAT_ORDER` (deckungsgleich mit der Startseite).

### Beta-Einblender + Suche im Menü; Karten-Pillen abgelöst
- **Beta-Einblender** (`nav.js`/`nav.css`): ein dezenter, schwebender Hinweis unten –
  ‹Beta – die Werkzeuge wachsen noch. Feedback geben ✕›, wegklickbar (merkt sich
  ‹gesehen› in localStorage). Löst die per-Karte-Pillen ab; ein Ort statt zwölf Marker.
- **Suche im Menü**: Tippfeld oben in der Schublade filtert die Werkzeugliste live;
  leere Bereiche blenden aus, Treffer-Bereiche klappen auf.
- Startseite: ‹Schon entdeckt?› klein/fein über das Karussell gehoben; Karussell-Inhalt
  Wallpaper · Schriften · PowerPoint · Icons · Logos; Karten ohne Pillen, eine Fläche.
- Konsolidiert: Webfont in Schriften (Abschnitt + Sprunglink), Zeichen in Logos (Link) –
  keine eigenen Karten mehr.

### Startseite: Entdecker-Karussell + Karten flach nach Priorität
- **Karussell** oben (rotierend, pausiert bei Hover/Fokus, respektiert
  `prefers-reduced-motion`, Pfeile · Punkte · Wisch): ein **Hinweis auf weniger
  Bekanntes** (Sektionsfarben, Zeichen, Übersetzungen, Wallpaper, Typografie,
  Design-System) – ‹Schon entdeckt?›.
- **Karten flach nach Priorität** statt nach Kategorien gruppiert (Logos · Signatur
  · Visitenkarten · Icons · Schriften · …). Backstage-Welten bleiben draussen
  (öffentliche Kategorien-Schranke beibehalten).
- Die Mini-Visuals der Karten von `.tile .x` auf `.thumb .x` generalisiert, damit
  das Karussell dieselben Erkennungszeichen nutzt – eine Quelle, kein Duplikat.

### Schliff: Sektionsfarben-Seite · Design-System-Bild · Theme-Icon ohne Emoji
- **Farben → Sektionsfarben**: die Sonderseite trägt jetzt **nur Sektions- und Bereichsfarben**
  (datengetrieben aus `goe-orgs.js`: 12 Sektionen + 6 Bereiche). Marken- und Neutralfarben wohnen
  im **Design-System** (Schaufenster `#swatches`) – keine Doppelpflege. Datei, Karte und Slug heissen
  jetzt `sektionsfarben`. Pantone war schon raus.
- **Startkarte Design-System** bekommt ein **eigenes Bild**: ein Mini-Bauplan (Leiste + Textzeilen +
  Farb-Chips = Struktur **und** Farbe) statt der Farbfelder – klar unterscheidbar von den Sektionsfarben.
- **Theme-Schalter ohne Emoji**: Sonne/Mond sind jetzt **Inline-SVG** (currentColor) statt der
  Unicode-Glyphen ☀/☾, die iOS zu Emoji umfärbte. Deterministisch in Hell wie Dunkel.

### Weitere Lücken vom alten Auftritt geschlossen: Zeichen · Wallpaper · PowerPoint · Feedback
- **Zeichen** (`zeichen.html`) – die Zeichen von Rudolf Steiner (Hochschule, Gesellschaft,
  Bau-Administration) als Vorschau + Anwendungshinweis + Zugang zu den vollständigen Paketen.
  Die Marken stehen auf weissem Feld (`# ds-ok`: Briefpapier-Artefakt, in Hell wie Dunkel sichtbar).
  Assets von grafik.goetheanum.ch gezogen, als echte PNG abgelegt (`assets/zeichen/`).
- **Wallpaper** (`wallpaper.html`) – elf Desktop-Hintergründe (2500×1406) zum Herunterladen.
  Von der CDN gezogen, als JPG q88 abgelegt (`assets/wallpaper/`, ~0,5 MB gesamt).
- **PowerPoint** (`powerpoint.html`) – Platzhalterseite (Vorlage wird überarbeitet, Datei folgt).
- **Neue Welt ‹Anwendungen›** (cat `anwendung`) in `nav.js`/`tools.json`/Startseite – für fertige
  Vorlagen (Wallpaper, PowerPoint); **Pantone aus der Farbseite entfernt** (wird nicht mehr verwendet).
- **Globaler Feedback-Link** im Menü (Schubladen-Fuss, `nav.js`) – mailto an die Goetheanum Grafik, auf jeder
  Seite erreichbar. Bewusst NICHT in der Kopfzeile: dort frass ein Icon die leere Fläche an, über die
  der (geheime) Dreifach-Klick die Intern-Ansicht schaltet. Anfrage-/Druckformular bleibt getrennt (Todo).

### Neue Publikumsseite: Farben (Lücke vom alten Auftritt geschlossen)
- **`farben.html`** – die Identitätsfarben auf einen Blick (Marke · Neutrale ·
  Sektionen). **Hex/RGB/HSB** werden im Browser exakt aus dem Token-Hex errechnet
  (eine Quelle: `tokens.css`; Sektionen aus `goe-orgs.js`), jede Zelle klick-kopierbar.
- **Ehrlich statt erfunden** (Hausregel): **CMYK** steht als **rechnerischer Richtwert**
  (sRGB→CMYK, geräteabhängig) klar markiert; **Pantone** und die offiziellen Druck-CMYK-/
  Sonderfarben sind ‹—› (noch aus dem Marken-Handbuch zu erfassen). Damit ist der im
  Schaufenster offene Punkt ‹CMYK-/Sonderfarben› sichtbar adressiert, ohne falsche Werte.
- Registriert in `tools.json` (cat `system`, erscheint in der Welt **Elemente**) + Startkarte.
- Aus dem Vergleich mit grafik.goetheanum.ch als ‹jetzt bauen› gewählt; Zeichen, PowerPoint,
  Wallpaper und ein globaler Kontakt-/Feedback-Button sind als nächste Schritte vorgemerkt.

### Generatorpass: die letzten vier Werkzeuge theme-aware – 100 %
- Die vier Generatoren folgten eigenen, fest verdrahteten Dunkel-Paletten und
  ignorierten Hell/Dunkel. Jetzt **theme-aware reskinnt**: ihre lokalen Variablen
  sind nur noch **Aliase auf die DS-Tokens** (`--bg→--paper`, `--panel→--soft`,
  `--text→--ink`, `--accent→--gold` …) – eine Kante, das ganze Chrome kippt mit.
  - **karten-generator** · **cover-generator** · **briefschaften**: Chrome auf
    Tokens, Aktion = volles Blau + Weiss (B01), Auswahl = dunkles Gold + Weiss,
    Felder/Knöpfe/Pillen aus dem Fundament; base.css ergänzt wo es fehlte (DS01).
  - **gtv-naming** ist zu grossen Teilen ein **Artefakt**: ein Marken-Muster einer
    hypothetischen ‹Goetheanum TV›-Plattform samt **Telefon-Mockup** (eigene
    Bildsprache: Titillium, Navy). Laut Hausregel kein Theme-Grund – darum
    **ratifiziert** (`# ds-ok`, eigene `--gtv-*`-Palette). Theme-aware ist allein
    das Werkzeug-Chrome, die Präsentations-Leiste `#presenter`.
- **Gedruckte Artefakte bleiben fest**: das A4-Blatt (karten/briefschaften) und die
  Cover-Leinwand bleiben weiss bzw. tragen die echten Druckfarben (`# ds-ok`),
  kippen NICHT mit dem Theme.
- **`start/index.html`** (alte Übersicht) mit auf den Floor gehoben (sub-14 → Tokens,
  Versal-Kicker entfernt G05, Rest tokenisiert).
- **Vertrag geschärft (v1.1.0)**: `reference/` zum Geltungsbereich-Ausschluss
  ergänzt – eingefrorene Referenz-Schnappschüsse sind keine Live-Flächen (ds-fix
  schloss sie längst aus; jetzt deckungsgleich). Score wird dadurch ehrlich.

> Score-Verlauf (Fortsetzung): **76 %** → **92 %** (vier Generatoren auf 0 Fehler)
> → **100 %** (`start/` + Vertrag-Geltungsbereich). **24/24 Seiten konform, 0
> Fehler.** Verbleibend nur Hinweise (DS04 additive Eigenrollen, DS05/DS06 in den
> bewusst eigenständigen Mockup-/Übersichtsköpfen).

### Aufgenommen
- **`.step-num`** (`base.css`, `contract.json` DS04) — runde Schritt-Nummer vor
  nummerierten Zwischentiteln (fixe Höhe *und* Breite statt nur `min-width`,
  `line-height:1`, tabular-nums). *Warum:* eine Seite (Logo-Hinweise) erfand
  Kreis-Badges lokal; die Ziffer sass optisch nicht mittig, weil `min-width`
  allein plus `align-items:baseline` im Elternflex die Kreisgeometrie und die
  Zentrierung dem Zufall überliess. *Wirkung:* eine Quelle für nummerierte
  Schritte, verlässlich rund und mittig, ab jetzt überall (`step-num` in DS04).
- **Textrollen als gemessene Grundlage** (`base.css`) — Kicker · Lede · Hinweis
  (`.note`/`.hint`/`.help`/`.desc`) · Meta (`.cap`/`.caption`/`.legend`/`.byline`) ·
  Label (`.lab`/`.role`) · Wert (`.readout`) · Code (`.code`/`.mono`).
  *Warum:* jede Seite erfand eigene Grade (11–15px) und Farben für denselben
  Zweck — uneinheitlich und teils unter der Leseschwelle. *Wirkung:* eine Quelle,
  B03-sicher, löst die Eigenlösungen ab (DS04).
- **Mobil-Baseline** (`base.css`) — Fingerziele ≥44px, Felder ≥16px, kein
  Überlauf, umbrechende Köpfe. *Wirkung:* B03/B04 als Konstruktion, nicht als
  Nachkontrolle.
- **Sektionsfarben als Tokens** (`tokens.css`/`tokens.json`) — `--sek-*` aus
  `assets/goe-orgs.js`. *Warum:* die Sektions-Identitätsfarben lebten nur in der
  Logo-Engine. *Wirkung:* überall gleich benannt, markenfest (kippen nicht mit
  Hell/Dunkel).
- **`--ok` (Erfolgsgrün)** (`tokens.css`/`tokens.json`). *Warum:* die Engine fand
  das Grün `#3f7d46` hartverdrahtet in `base.css .btn.ok` und im Schaufenster –
  ein fehlendes Token. *Wirkung:* erste echte Atem-Aufnahme: aus einer entdeckten
  Abweichung wurde Fundament; `.btn.ok` und die Status-Punkte ziehen jetzt `--ok`.

### Engine (neu)
- **`design-system/contract.json`** — maschinenlesbarer Struktur-Vertrag (DS01–DS07).
- **`tools/ds-lint.py`** — prüft Gestalt-Konformität, meldet je Regel + Score.
- **`tools/ds-fix.py`** — hebt die Hauspalette deterministisch auf Tokens (Codemod).
- **Hook** — `ds-lint --staged` läuft mit (vorerst berichtend, nicht blockierend).

> Score-Verlauf (die Messlatte): **9 %** (Engine-Einführung) → **17 %** (Fundament
> + Schaufenster) → **35 %** (öffentliche Live-Seiten) → **46 %** (Generatoren +
> Icons). 11/24 Seiten konform. Jeder Schritt bewegt diese Zahl.

### Schaufenster bildet ab, was bereitliegt (Doku + Präsentation in einem)
- Neue Abschnitte, live aus der Quelle gerendert: **Textrollen** (Kicker/Lede/
  Hinweis/Meta/Label/Wert/Code/Badge), **Sektionen & Bereiche** (volle Tabelle
  aus `goe-orgs.js` + `--sek-*`-Swatches), **Konformitäts-Engine** (Vertrag
  DS01–07 aus `contract.json`, die Schleife, der Score).
- `goe-orgs.js` ist damit im Design-System **sichtbar** und über die Quelle
  korrigierbar. Befund dabei: die Visitenkarten-App trägt eine **abgewichene
  Kopie** der Tabelle – Konsolidierung (einbinden statt kopieren) steht an.

### Lesbarkeit & Inklusivität fest verankert (recherchiert, Stand 2026)
- **Typo-Skala einen Schritt grösser**: Floor 13→**14px**, Meta/Label 14→**15–16**
  (`--t-small`), Fliesstext 17→**18–20** (`--t-body`), Lede 19→**20–23**. Grund:
  16px ist die Norm-Untergrenze, Best Practice ‹bei 16 beginnen, hochskalieren›
  (WCAG resize 1.4.4; rem-basiert). Contract-Floor (DS03) 13→14 nachgezogen; die
  literalen 13px der öffentlichen Seiten auf `--t-small` gehoben.
- **B04**: Bezug auf WCAG 2.2 SC 2.5.8 (Ziel ≥24px, wir geben 44) und 1.4.12
  (Layout übersteht erhöhte Laufweiten) in den Hausregeln verankert.
- **Icons im Dunkelmodus**: schwarze Strich-Icons als `<img>` wurden verschluckt.
  Utility `.ico-invert` (Filter im Dunkelmodus) ins Fundament; auf die Schriften-
  Icons angewandt. Besser noch: Icons als Webfont/Inline-SVG mit currentColor.

### Die Schrift-Grenze gezogen – Source Sans 3 endlich im Einsatz
- Die zweite Groteske (Source Sans 3) war geladen, aber ungenutzt. Jetzt verdrahtet:
  **Funktion & Daten** tragen sie (Label, Wert/Readout, Meta/Legende, Badge/Chip,
  Formularfelder, Tabellen) – klein & konventionell deutlich lesbarer.
- **Identität bleibt Hausschrift**: Titel, Kicker, Lede, **Fliesstext und erklärende
  Hinweise** (Sprache). Lesbarkeit dort aus den **Faktoren**: --lh-body 1.6 → **1.66**,
  Mass ~62ch, Schnitt Klar, Betonung Laut. Die Grenze ‹wo Lesbarkeit über Identität
  geht› in CLAUDE.md verankert.

### Backstage/Beta auf den 14px-Floor + Org-Farbe angeglichen
- Acht Specimen-/Backstage-Seiten (Typografie, Tester, Grotesk+, Vorschau,
  Mischsatz, Ligaturen ×3) auf den neuen Floor gehoben: literale <14px → --t-small;
  Reste tokenisiert (Bar-Hintergrund → --bar-bg, Gold-Tint → color-mix, Code-Chip
  → --code-*). Alle 0 Fehler. Gesamt-Score **42 % → 72 %** (18/25 konform).
- **Track 1**: `--bereich` von #005eb8 auf **#0061a9 = Markenblau** angeglichen
  (so rendern es die Logo-Daten/goe-orgs.js schon). Sektionsnamen-Korrekturen aus
  #164 (Team) übernommen; spanische Gesellschaft bleibt `prüfen`.

### Einbinden statt kopieren – eine Org-Quelle (Drift dauerhaft behoben)
- Es gab DREI Org-Datensätze: `assets/goe-orgs.js` (36, Schaufenster), `assets/
  data/goetheanum-orgs.js` (38 inkl. it/subscriptions, live: Logos+Signatur) und
  eine **inline-Kopie** in Visitenkarten (abgewichen). Befund bei der Prüfung:
  die *live*-Daten treffen goetheanum.ch besser (es ‹Bellas Artes›, ‹Jóvenes›).
- **`assets/goe-orgs.js` ist jetzt die EINE Quelle** (38 Orgs der Live-Daten +
  vollständige API: bare `ORGS`/`CATS` für die Logo-Engine & Signatur UND
  `GCI_ORGS`/`window.GOE_*` fürs Schaufenster). Logos, Signatur, Visitenkarten,
  Briefschaften, Schaufenster und Übersetzungen binden dieselbe Datei ein; die
  Inline-Kopie ist raus, `assets/data/goetheanum-orgs.js` gelöscht. Verifiziert:
  alle Dropdowns/Tabellen 38 Einträge, Logo rendert. Drift ist nicht mehr möglich.

### Neue Quelle & Werkzeug
- **`assets/goe-terms.js`** (Begriffe & Übersetzungen) – auf goetheanum.ch
  geprüft: fr/es korrigiert (Hochschule = ‹Université libre de science de
  l’esprit›, Gesellschaft = ‹Société anthroposophique générale›), verifizierte
  Zeilen auf `fest`. Neue Seite **uebersetzungen.html** (durchsuchbar, klick-
  kopierbar, für die Sekretariate) + Eintrag in `tools.json` (Startkarte).

### Behoben (Mobil & Lesbarkeit – aus echtem Geräte-Befund)
- **Seitenrand am Handy** war weg: `.hero{padding:X 0 Y}` setzte den seitlichen
  Rand auf 0 und überschrieb `.wrap` – Text klebte am Glas. Fundament-Fix:
  `.hero` nutzt nur noch `padding-block` (Seitenrand kommt aus `.wrap`); die 9
  Seiten mit lokalem `.hero`-Override nachgezogen. Mobiler `.wrap`-Rand bleibt
  grosszügig (`max(22px, safe-area)`), nicht verkleinert.
- **Lede unlesbar** (in „G Leise" 265 + muted gesetzt) → auf den Lese-Schnitt
  Klar gehoben (schriften, icons, statistik). Regelbezug: Leise verschwimmt klein,
  Minimum ist Klar.

### Engine geschärft (Lernen am Bestand)
- **DS04** meldet nur noch Schlüssel-Selektoren, nicht kontextuelle Überschreibungen
  (`.download .btn` ist Verortung). **Zeilen-Treffer** liegen jetzt korrekt auf der
  Property-Zeile (Mehrzeilen-CSS) – damit greift `# ds-ok` auch in den Generatoren.
- **Artefakt-Kategorien** ratifiziert (`# ds-ok`): gedrucktes Blatt/Karte, Schnitt-
  marken, E-Mail-Leinwand, „Logo auf Dunkel"-Vorschau, Owner-Mode-Signal, Modal-Scrim.
  Die Maschine schlägt vor, der Mensch ratifiziert – die Ausnahme wird Teil des Codes.

---

## Wie eine Verbesserung aufgenommen wird (Kurz-Rezept)
1. Lösung an *einer* Seite bewährt? `ds-lint` zeigt sie als DS04-Abweichung.
2. In `tokens.css`/`base.css` heben (Token oder Rolle/Komponente). Bei neuer
   Pflicht: `contract.json` ergänzen (Regel/Klasse) **und** `version` erhöhen.
3. Eintrag hier (was · warum · Wirkung).
4. `ds-fix` über die Seiten laufen lassen, `ds-lint --score` prüfen, shippen.
