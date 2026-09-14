# Campusplan für Besucherinnen und Besucher — Szenarien, Relevanz, Machbarkeit

Stand: 13. September 2026 · Prüfung der Idee «Wer eine Reise ans Goetheanum
plant, stellt sich vorher einen Campusplan mit den Orten zusammen, die sie
besuchen will — als Druck-PDF oder als eigener Link mit Abhak-Liste.»
Grundlage: das laufende Kartentool
(https://werkzeuge.goetheanum.ch/apps/karten-generator/), sein Ortskatalog
(https://github.com/phtok/goeloggen/blob/main/apps/karten-generator/orte.js),
das Kurzlink-Backend des QR-Generators
(https://github.com/phtok/goeloggen/blob/main/services/qr-generator/README.md)
und die Besucherseiten von goetheanum.ch.

## 0 · Kurzurteil

**Relevant: ja. Machbar: ja, mit wenig neuer Technik. Die Hürde ist nicht
der Bau, sondern Inhalt und Heimat.** Das Kartentool besitzt heute schon
alles, was ein Besucherplan braucht: 71 Orte mit deutschen und englischen
Namen, Marker, Legende, Vektor-PDF. Ein Besucherplan ist datenmässig
nichts anderes als die Liste der angeschalteten Orte — die passt in zwölf
Zeichen hinter das `#` einer URL. Weder Konto noch Server sind nötig.

Was fehlt, ist nicht Code: ein für Gäste kuratierter Teil des Katalogs
(heute ist er auf Tagungen zugeschnitten; der Grosse Saal fehlt als
eigener Ort, Heizhaus und Verlagshaus fehlen ganz), vier bis fünf
vorgedachte Rundgänge — und ein Entscheid, wo die öffentliche Fassung
wohnt, weil werkzeuge.goetheanum.ch bewusst intern und `noindex` ist.

**Empfehlung:** nicht mit dem Abfrage-Assistenten beginnen, sondern mit
vordefinierten Highlights, die der Gast in drei Schritten zu seinem Plan
macht (Ablauf in § 9). Zielperson ist die Einzelne zuhause, am eigenen
Bildschirm — die Einfachheit der Handhabung entscheidet. Die Heimat der
öffentlichen Fassung wird sich finden, wenn das Werkzeug überzeugt
(Entscheid des Auftraggebers, 14. 9. 2026); bis dahin läuft es als
Laborseite mit teilbarem Link.

## 1 · Ausgangslage (gemessen, nicht geschätzt)

| Baustein | Stand heute | Quelle |
|---|---|---|
| Ortskatalog | 71 Orte in 8 Kategorien, DE/EN, Marker, Positionen in Blatt-mm | `orte.js` (generiert) |
| davon für Gäste tauglich | 44 (Eingänge 7 · Anreise 4 · Ausstellung 7 · Häuser 17 · Gärten 9); Säle 12, Sektionen 12 und Treppen 3 sind Tagungs- und Arbeitsorte | Kategorien im Katalog |
| Planzustand | `state.an` = Menge der Ort-IDs; Titel, Untertitel, Sprache; JSON-Sicherung vorhanden | `app.js`, `standAlsJson()` |
| Druck | Vektor-PDF A4/A3 quer, Schrift eingebettet, Beschnitt und Schnittmarken abschaltbar | `export.js` |
| Karte | Gelände-SVG 346 KB, Aquarellblatt 505 KB, PDF-Bibliotheken 450 KB | `assets/`, `vendor/` |
| Kurzlinks | RPC `qr_link_anlegen`, Brücke tools.goetheanum.ch/s/‹code›, anonyme Zählung; das Register ist **öffentlich** (Beschluss 10. 7. 2026) | `services/qr-generator/` |
| Oberfläche | Zwei-Spalten-Werkzeug für den Schreibtisch (Seitenleiste ab 300 px + Blattvorschau) — kein Telefon-Layout | `index.html` |
| goetheanum.ch | Besuchsseite nennt Führungen, Öffnungszeiten, Café, Buchhandlung, Gartenpark und Anreise — **keinen Plan zum Mitnehmen, keine App**; der Gartenpark (12 ha, immer offen) hat weder Karte noch Rundgang | https://goetheanum.ch/de/besuch |
| Leitsystem | Orientierungspläne je Etage gibt es **am Empfang**, gedruckt | https://github.com/phtok/goeloggen/blob/main/docs/leitsystem-befund.md |

Das Bild ist eindeutig: die Technik liegt bereit, das Angebot für Gäste
fehlt heute vollständig — auf der Website wie im Gelände.

## 2 · Wer plant einen Besuch? Relevanz je Gruppe

| Gruppe | Was sie braucht | Relevanz des Plans |
|---|---|---|
| **Tagesgäste, Architektur-Interessierte** (kommen wegen des Baus, oft aus Basel, halber Tag) | Wo ist was, was lohnt sich, wo ist der Eingang, wo das Café | **hoch** — heute nur die Führung oder Suchen |
| **Tagungsteilnehmende** | Säle, Verpflegung, Unterkunft, Anreise; die Karte bekommen sie vom Veranstalter (Kartentool) | mittel — der Plan ergänzt die Tagungskarte um die freie Zeit |
| **Gruppen, Schulklassen, Familien** | Rundgang mit Stationen, Aufgaben, Abhaken | **hoch** — Abhaken ist hier kein Gimmick, sondern das Format |
| **Mitglieder, Stammgäste** | Sektionshäuser, Bibliothek, Archiv | gering — kennen den Campus |
| **Empfang und Führungen** (intern) | Gästen schnell einen Plan mitgeben | **hoch** — ersetzt Zettel und Handzeichnung |

Das «Onliness»-Argument des Hauses (Strategieblatt, https://github.com/phtok/goeloggen/blob/main/docs/strategie.md)
trägt hier über die Mitarbeitenden hinaus: dieselbe Kartenmaschine, die
heute Tagungskarten setzt, würde Gästen ein markenkonformes, gedrucktes
und mobiles Stück Gastfreundschaft geben — «Gastfreundschaft beginnt vor
der Ankunft» (Werkzeuge-Mailplan, April).

## 3 · Drei Szenarien zur Auswahl

### Szenario A · «Drei Fragen» (Abfrage-Assistent)

Wie viel Zeit? (zwei Stunden · halber Tag · ganzer Tag) — Was interessiert?
(Architektur · Gärten · Ausstellungen und Bücher · Arbeit der Sektionen) —
Wie kommst du? (Bahn · Bus · Auto). Aus den Antworten entsteht ein
Vorschlag, der sich danach anpassen lässt.

Bewertung: fühlt sich modern an, ist bei 44 Orten aber **Aufwand ohne
Mehrwert**. Die drei Fragen ergeben faktisch dieselben vier bis fünf
Sets wie Szenario C, nur mit drei Klicks Umweg und einer Regel-Logik,
die gepflegt werden muss. G03 gilt auch für Interaktion: was sich
weglassen lässt, entfällt. **Nicht bauen.**

### Szenario B · «Aus der Liste» (freie Auswahl)

Die Gästeliste des Katalogs, nach Kategorien aufklappbar, jeder Ort mit
einer Zeile Text; die Karte zeigt live, was angeschaltet ist. Das ist die
heutige Orte-Liste des Kartentools, verschlankt auf die 44 Gäste-Orte
und ohne Backend-Regler.

Bewertung: notwendig als **Anpassungs-Ebene**, aber als Einstieg zu
offen — 44 Kästchen sind für jemanden, der den Campus nicht kennt, eine
Entscheidungswand.

### Szenario C · «Fertige Rundgänge» (kuratierte Sets)

Vier bis fünf Rundgänge, ein Klick, danach anpassen (Szenario B):

1. **Der Bau** — Haupteingang, Empfang, Grosser Saal, Wandelhalle,
   Nordgalerie, Haupttreppe, Buchhandlung, Café. Zwei Stunden.
2. **Die Perlen** — Glashaus, Heizhaus, Haus Duldeck, Haus de Jaager,
   Eurythmiehaus, Rudolf Steiner Halde, Schreinerei mit Atelier und
   Modell des Ersten Goetheanum. Halber Tag.
3. **Der Gartenpark** — Felsli, Wasserspiel, Gedenkhain, Heilkräuter-,
   Färberpflanzen-, Duftkräutergarten, Bienenskulptur, Präparatepavillon.
4. **Mit Kindern** — kurze Wege, Wasserspiel, Puppentheater Felicia,
   Backofen, Bienenskulptur, Speisehaus.
5. **Barrierefrei** — Zugang, Lifte, WC, kurze Wege; Reihenfolge nach
   Steigung.

Bewertung: **der richtige Einstieg.** Die Sets sind Inhalt, nicht Code —
sie leben als Liste von Ort-IDs neben dem Katalog und lassen sich vom
Empfang oder den Führungen ohne Entwicklerin pflegen.

**Entscheid, den dieses Papier vorschlägt: C als Einstieg, B als
Anpassung, A weglassen.**

## 4 · Von der Auswahl zur Ausgabe

### 4.1 Druck-PDF

Vorhanden. Die Besucher-Fassung braucht drei Abweichungen vom
Tagungs-Export: kein Beschnitt und keine Schnittmarken (Heimdrucker,
A4 randlos gibt es nicht), Titel «Mein Besuch» mit Datum statt
Tagungsname, und die Legende in Rundgang-Reihenfolge nummeriert statt
nach Katalognummer. Alles drei sind Schalter auf dem bestehenden Modell.

### 4.2 Der eigene Link

Der Plan **ist** die URL. 71 Orte als Bitmaske ergeben 9 Byte, als
`base64url` zwölf Zeichen; mit Sprache, Datum und Rundgang-Reihenfolge
bleibt ein Link unter 60 Zeichen:

```
https://‹heimat›/campusplan/#p=AAAABAAMAUgF&s=de&d=2026-10-04
```

Folgen: kein Konto, keine Datenbank, keine Personendaten, nichts läuft
ab, nichts muss gelöscht werden. Der Link lässt sich mailen, als QR
drucken (der QR-Generator des Hauses kann das heute) und auf dem PDF
selbst als QR mitdrucken — **das Blatt führt zum Telefon.**

Kurzlink: möglich über die bestehende RPC, aber **nicht empfohlen** —
das Register des QR-Generators ist per Beschluss öffentlich, und ein
Besuchsplan mit Datum ist eine private Sache. Entweder ohne Kurzlink
(der lange Link trägt alles) oder später ein eigenes, nicht gelistetes
Register. Kein Blocker.

### 4.3 Mobile Ansicht mit Abhaken

Neu, aber klein: eine Liste der Stationen in Rundgang-Reihenfolge, jede
mit Kästchen, einem Satz und einem Kartenausschnitt um den Marker
(dieselbe SVG, per `viewBox` gezoomt). ‹Nächste Station› springt weiter.
Der Haken lebt im `localStorage` des Telefons — privat, gerätegebunden,
ohne Übertragung; wer den Link auf einem zweiten Gerät öffnet, beginnt
bei null, was für einen Tagesbesuch richtig ist.

Kein Backend, kein Login, keine Standortabfrage (die Karte des Campus
ist klein genug, dass Orientierung an Gebäuden reicht — und GPS zwischen
den Bauten ist ohnehin unzuverlässig).

## 5 · Machbarkeit im Einzelnen

| Baustein | Vorhanden | Neu | Aufwand |
|---|---|---|---|
| Ortskatalog mit DE/EN | ja | Gäste-Flag, ein Satz je Ort (DE/EN), Grosser Saal als Ort, Heizhaus und Verlagshaus (Merkliste 16. 7.) | Inhalt, 1–2 Tage mit Empfang |
| Rundgänge | — | 5 Listen von Ort-IDs mit Reihenfolge, Titel, Dauer | Inhalt, halber Tag |
| Karte und Marker | ja | Zoom auf Station (`viewBox`) | Code, klein |
| Druck-PDF | ja | 3 Schalter (siehe 4.1) | Code, klein |
| Link-Kodierung | — | Bitmaske ↔ `state.an`, Reihenfolge | Code, klein |
| Auswahl-Oberfläche | teils (Orte-Liste) | eigene schlanke Seite `apps/campusplan/` aus dem Starter, Telefon zuerst; **nicht** das Backend-Werkzeug umbauen | Code, 2–3 Tage |
| Abhak-Ansicht | — | Liste + `localStorage`, 44-px-Ziele (B04), Kontraste aus den Tokens (B01/B02) | Code, 1–2 Tage |
| Zweisprachig | Katalog ja | Oberfläche DE/EN (Erika, `uebersetzerin`) | klein |
| Ladegewicht Telefon | — | Gelände-SVG 346 KB reicht; Aquarell (505 KB) und PDF-Bibliotheken (450 KB) nur auf Anforderung laden | Code, klein |
| Barrierefreiheit | Fundament ja | Messung mit `tools/barrierefreiheit.mjs --seite` | Pflicht, klein |
| **Heimat der öffentlichen Fassung** | — | werkzeuge.goetheanum.ch ist intern und `noindex`; öffentlich braucht Einbettung auf goetheanum.ch oder eine Adresse unter tools.goetheanum.ch | **Entscheid**, nicht Code |

Das Kartentool teilt Katalog und Karte mit der Besucher-Seite, bleibt
selbst aber unverändert das Werkzeug der Mitarbeitenden. Eine Quelle,
zwei Türen — dasselbe Muster wie QR-Code und Kurzlink im QR-Generator.

## 6 · Was dagegen spricht — und was daraus folgt

- **Zutritt.** Sektionshäuser, Wohnheim, Färberei sind Arbeits- und
  Wohnorte. Der Plan darf keine Erwartung wecken, dass man hinein darf.
  Folge: Gäste-Katalog nur mit Orten, die man **sehen** oder **betreten**
  darf, und je Ort das eine Wort dazu («von aussen»).
- **Öffnungszeiten veralten.** Nicht in den Plan aufnehmen, sondern den
  Link auf https://goetheanum.ch/de/besuch setzen. Der Plan sagt *wo*,
  die Website sagt *wann*.
- **Pflege.** Fünf Rundgänge sind fünf Listen, aber jemand muss sie
  besitzen. Folge: Eigentümerschaft beim Empfang oder den Führungen
  klären, bevor die öffentliche Fassung live geht (Etappe 4).
- **Doppelspur zu Führungen?** Nein — der Plan ist die Selbstführung für
  die Zeit ohne Führung und der Merkzettel danach. Er kann die Führung
  sogar verkaufen («Diesen Rundgang gibt es auch geführt»).
- **Datenschutz.** Durch den Link-Ansatz keiner. Sobald jemand Konten,
  Speichern oder Standort will, ändert sich das — deshalb ausdrücklich
  nicht bauen.

## 7 · Etappen (jede einzeln abschliessbar)

1. **Inhalt zuerst.** Gäste-Flag und Ein-Satz-Beschreibung im Katalog,
   Grosser Saal ergänzen, Perlen-Kategorie mit Heizhaus und Verlagshaus
   (schliesst Merkliste Punkte 3 und 4), fünf Rundgänge als Datei
   `apps/karten-generator/rundgaenge.js`. Prüfbar ohne eine Zeile
   Oberfläche.
2. **Heim-Fassung (Labor).** Seite `apps/campusplan/` aus dem
   Starter: Themen wählen → Zeit wählen → Plan anpassen → Druck-PDF und
   Link mit QR (Ablauf § 9). Läuft als Laborseite mit teilbarem Link,
   damit sie zuhause ausprobiert werden kann. Registrierung in
   `tools.json` als `cat: labor`.
3. **Telefon-Fassung.** Derselbe Link öffnet auf dem Telefon die
   Abhak-Liste mit Kartenausschnitt. Messung auf 390 px, Barrierefreiheit
   gemessen.
4. **Heimat entscheiden.** Mit der Erfahrung aus Etappe 2: öffentlich
   auf goetheanum.ch einbetten oder unter tools.goetheanum.ch anbieten;
   Eigentümerschaft der Rundgänge festlegen.

Nicht gebaut werden: Abfrage-Assistent (A), Konten, Server-Speicherung,
Öffnungszeiten-Logik, Standortverfolgung, Kurzlinks im öffentlichen
Register.

## 8 · Die eine offene Frage

Soll Etappe 1 und 2 gebaut werden — also die Empfangs-Fassung mit
fertigen Rundgängen, ohne den öffentlichen Auftritt schon zu
entscheiden? Empfohlen: ja, weil sie keinen Hosting-Entscheid braucht und
in einer Woche zeigt, ob Gäste den Plan nehmen.

## 9 · Der Ablauf: drei Bildschirme, je eine Frage, alles vorausgefüllt

Nachtrag 14. September 2026. Richtung des Auftraggebers: das Werkzeug
muss zuhause von einer Einzelperson bedienbar sein, die Einfachheit
entscheidet, und der Ablauf ist die Kernfrage — Themen wählen, dann
Details? Formular? Highlights vordefinieren?

**Antwort: kein Formular, sondern ein vorausgefüllter Plan, den der Gast
in drei Schritten zu seinem macht.** Ein Formular fragt, der Gast
antwortet und muss dem Ergebnis vertrauen. Hier steht das Ergebnis schon
beim dritten Schritt auf der Karte, und der Gast schiebt nur noch zurecht.
Sein Aufwand: zwei Tipps, ein Tipp, dann wahlweise Korrekturen.

### Schritt 1 · «Was zieht dich her?»

Fünf Themen als Kacheln mit Bild, Mehrfachwahl, keine Untermenüs:

| Thema | Was drin ist |
|---|---|
| **Der Bau** | Goetheanum innen: Grosser Saal, Treppenhäuser, Glasfenster, Wandelhalle, Menschheitsrepräsentant |
| **Architektursammlung** | die Nebenbauten 1913–1924 auf dem Hügel: Heizhaus, Glashaus, Transformatorenhaus, Haus Duldeck, Haus de Jaager, Eurythmiehäuser, Verlagshaus, Halde, Schreinerei |
| **Gartenpark** | Felsli, Wasserspiel, Gärten, Gedenkhain, Bienenskulptur, Präparatepavillon |
| **Bücher, Kunst, Ausstellungen** | Buchhandlung, Bibliothek, Nordgalerie, Rudolf-Steiner-Atelier, Modell des Ersten Goetheanum, Hochatelier |
| **Essen und Verweilen** | Café, Speisehaus, Vitalshop |

Darunter zwei **Umstände** als Schalter, keine Themen: *Mit Kindern* und
*Barrierefrei*. Sie ändern die Vorauswahl (Kinder-Orte hinein, steile
Wege heraus), nicht die Themen.

Heizhaus und Verlagshaus stehen nicht in einer Nebenkategorie, sondern
mitten in der Architektursammlung — sie sind Ikonen des Ensembles
(Beschluss 14. 9. 2026). Das Transformatorenhaus (1921) gehört dazu und
fehlt im Katalog ebenfalls.

### Schritt 2 · «Wie viel Zeit hast du?»

Drei grosse Knöpfe: **Zwei Stunden · Halber Tag · Ganzer Tag.**

Wirkung ohne Regelwerk: jeder Ort trägt in seinem Thema einen **Rang**
(1 = Highlight) und eine **Dauer** in Minuten. Das Zeitbudget schneidet
die nach Rang sortierte Liste — eine Sortierung und eine Summe, mehr
nicht. Immer dabei, unabhängig vom Budget: Haupteingang, Empfang, WC und
die drei Anreise-Marker (Bahnhof, Bus, Parkplatz). Die Anreise wird
darum **nicht** abgefragt; die Marker kosten auf der Karte nichts.

### Schritt 3 · «Dein Plan»

Karte oben, Liste unten in **Gehreihenfolge** (jeder Ort trägt einen
festen Rundweg-Index: Eingang → Bau → Kolonie im Süden → Gartenpark →
zurück). Jede Zeile: Nummer, Name, Einzeiler, Zugangswort, Dauer,
Kästchen. Abwählen ist ein Tipp; «Mehr Orte» klappt den Rest des Themas
auf. Darunter drei Knöpfe: **PDF · Link · QR.** Auf dem Telefon ist
dieser Bildschirm zugleich die Abhak-Liste.

**Highlights vordefinieren: ja — das ist das ganze Inhaltsmodell.** Der
Rang je Thema ersetzt jede Abfrage-Logik und lässt sich ohne Entwicklerin
pflegen.

## 10 · Inhaltsmodell: die Gäste-Zeile je Ort

Zu jedem Gäste-Ort kommen zum Katalog (`orte.js`) diese Felder — als
eigene Datei `gaeste.js`, damit der generierte Katalog unberührt bleibt:

| Feld | Werte | Wozu |
|---|---|---|
| `thema` | eines der fünf | Schritt 1 |
| `rang` | 1 … n innerhalb des Themas | Schritt 2, Highlight zuerst |
| `dauer` | Minuten | Schritt 2, Zeitbudget |
| `zugang` | betreten · von aussen · mit Führung · auf Anfrage | Zutritts-Erwartung steuern (§ 6) |
| `einzeiler` | DE/EN, ein Satz | Schritt 3, Legende, Abhak-Liste |
| `gehfolge` | Rundweg-Index | Reihenfolge in Liste und Legende |
| `kinder` · `barrierefrei` | ja/nein | die zwei Umstände |

## 11 · Wo es wirklich Inhalt braucht — und wo nicht

Grundsatz G03 für Text: **Was sich selbst erklärt, bekommt keinen
Einzeiler**, nur das Zugangswort. Einzeiler nur dort, wo der Name nichts
sagt oder täuscht («Heizhaus» klingt nach Technikraum, ist eine Ikone).

**Erklärt sich selbst (kein Einzeiler):** Haupteingang, Südeingang,
Empfang, Infotisch, barrierefreier Zugang, Toiletten, Bahnhof, Bus,
Parkplatz, Buchhandlung, Bibliothek, Café, Speisehaus, Vitalshop,
Wasserspiel, Heilkräuter-, Färberpflanzen-, Schnittblumen- und
Duftkräutergarten, Bienenskulptur.

**Gehört nicht in den Gästeplan (Arbeits- und Wohnorte, kein Sehwert
von aussen):** AfaP, Trigon, Holzhaus, Studierendenwohnheim,
Jugendsektionshaus, Gästehaus Friedwart, die zwölf Sektionen als eigene
Einträge, Säle ausser dem Grossen Saal, Treppenhäuser als eigene Orte.

**Braucht einen Einzeiler — Entwurf aus belegten Fakten** (Quellen:
Wikipedia-Artikel Goetheanum, https://www.architekturpfad.ch/, Liste der
Kulturgüter in Dornach; «zu prüfen» = Fakt noch nicht belegt):

| Ort | Einzeiler (Entwurf) | Zugang | Stand |
|---|---|---|---|
| Goetheanum · Grosser Saal *(fehlt als Ort)* | Knapp tausend Plätze unter einer Deckenmalerei in Pflanzenfarben, farbige Glasfenster von 1945. | betreten | belegt |
| Menschheitsrepräsentant *(fehlt als Ort; 5. OG, Südtreppe)* | Über acht Meter Holz: die Christusfigur zwischen Luzifer und Ahriman, von Rudolf Steiner und Edith Maryon ab 1914. | mit Führung? | Zugang zu prüfen |
| Heizhaus (1915) | Der erste Betonbau des Hügels: ein Heizwerk mit sphinxhafter Form, bis heute in Betrieb. | von aussen | belegt |
| Glashaus (1914) | Zwei Kuppeln unter Schiefer, gebaut zum Schleifen der Glasfenster des Ersten Goetheanum. | von aussen | belegt |
| Transformatorenhaus (1921) *(fehlt als Ort)* | Steiners Trafostation mit kubischen Auskragungen, bis heute am Netz. | von aussen | belegt |
| Haus Duldeck (1915) | Eisenbeton-Wohnhaus für den Stifter des Grundstücks, seit 2002 Rudolf-Steiner-Archiv. | von aussen | belegt |
| Haus de Jaager (1921) | Wohn- und Atelierhaus für einen Bildhauer, kantig und doch mit Anklang an die Doppelkuppel. | von aussen | belegt |
| Eurythmiehaus (1920) | Eines von drei Wohnhäusern nach Entwurf von Edith Maryon. | von aussen | belegt |
| Verlagshaus *(fehlt als Ort)* | Der letzte von Steiner entworfene Bau der Kolonie. | von aussen | Jahr und Fakt zu prüfen |
| Rudolf Steiner Halde (1905, Anbau 1923) | Der Betonanbau von 1923 war der Versuchsbau für das zweite Goetheanum, heute Tagungshaus. | betreten | belegt |
| Schreinerei (1913) | Die Bauhütte des Ersten Goetheanum, in der Steiner arbeitete und 1925 starb — heute Atelier und Modell. | betreten | belegt |
| Baugeschichte + Modell Erstes Goetheanum | Das Modell des 1922 abgebrannten Holzbaus, dazu seine Geschichte. | betreten | belegt |
| Rudolf-Steiner-Atelier | Steiners Arbeitsraum in der Schreinerei. | betreten? | zu prüfen |
| Hochatelier | Der hohe Raum, in dem die Holzplastik entstand. | ? | zu prüfen |
| Edith-Maryon-Zimmer | Erinnerungsraum an die Bildhauerin, Mitschöpferin der Holzplastik. | ? | zu prüfen |
| Nordgalerie | Ausstellungsraum im Goetheanum. | betreten | zu prüfen |
| Wandelhalle | Das Foyer unter dem Grossen Saal. | betreten | zu prüfen |
| Gedenkhain | Urnenhain, in dem Rudolf Steiner, Marie Steiner-von Sivers und Christian Morgenstern ruhen. | betreten | belegt |
| Felsli | Der Felsvorsprung am Westende des Hügels — der Aussichtspunkt. | betreten | belegt |
| Präparatepavillon | Hier entstehen die biodynamischen Präparate der Gärtnerei. | von aussen? | zu prüfen |
| Kepler-Sternwarte | Kleine Sternwarte der Mathematisch-Astronomischen Sektion. | von aussen | zu prüfen |
| Helene Finckh Häuschen | ? | ? | Inhalt fehlt |
| Kristallisationslabor | Labor für die Kupferchlorid-Kristallisation, ein Prüfverfahren der biodynamischen Forschung. | von aussen | zu prüfen |
| Haus Schuurman · Färberei | ? | ? | Inhalt fehlt |
| Puppentheater Felicia · Backofen | ? | ? | Inhalt fehlt (Kinder-Orte) |

**Befund am Rand:** Der *Architekturpfad Dornach-Arlesheim*
(https://www.architekturpfad.ch/) führt mit vier Routen durch die
Kolonie; sein gedruckter Führer von 2011 ist vergriffen. Das Ensemble
samt Heizhaus, Glashaus, Eurythmeum, Trafostation und Verlagshaus ist
Kulturgut von nationaler Bedeutung (Kategorie A). Beides stützt die
Relevanz — und der Pfad ist der natürliche Partner für die Einzeiler
der Architektursammlung.

### Bedienung des fertigen Plans auf dem Telefon (gebaut 14. 9. 2026)

Die Karte sitzt oben, die Stationen darunter; die Karte nimmt gut die
halbe Bildschirmhöhe. **Bewegen:** ein Finger zieht die Karte, die Seite
scrollt dabei nicht (`touch-action: none` auf der Karte). **Vergrössern:**
zwei Finger ziehen auf, dazu drei Knöpfe am Kartenrand (Plus, Minus,
ganzer Plan), Mausrad am Schreibtisch. **Springen:** der Knopf «Karte»
an jeder Station fährt die Karte auf diesen Ort; ein Tipp auf eine Nummer
in der Karte springt zur Station in der Liste und rahmt sie. **Abhaken:**
nur über das grosse Kästchen in der Liste (44 px Fingerziel), nie durch
einen Tipp auf die Karte — so passiert unterwegs nichts aus Versehen.
Abgehakte Nummern werden grün, oben zählt «3 von 9 besucht». Der Stand
bleibt im Speicher des Telefons, der Link selbst ändert sich nicht.

## 12 · Abfrage-Fahrplan (eine Frage je Runde)

Der Auftraggeber wird zu den offenen Punkten **einzeln** befragt, je
Runde eine Frage mit Empfehlung; Antworten landen hier im Papier:

1. Ablauf in drei Schritten (§ 9) — so bauen? *Ja, live testen (14. 9. 2026).
   Gebaut als Laborseite https://werkzeuge.goetheanum.ch/apps/campusplan/
   (Etappen 1 und 2, mit Telefon-Fassung aus Etappe 3): Karte zieht und
   zoomt per Finger, Kästchen 44 px, Abhaken bleibt auf dem Gerät.*
2. Die Themen und ihre Namen. *Rückmeldung 14. 9.: die Sektionen fehlen —
   sechstes Thema «Sektionen der Hochschule» ergänzt (zwölf Orte, Zugang
   auf Anfrage). Frage «Was zieht dich an?» statt «her?».*
3. Zugangswort je Bau: was darf der Gast betreten? *(offen)*
4. Einzeiler-Entwürfe (§ 11) freigeben oder korrigieren. *(offen)*
5. Dauer in Minuten je Ort — Schätzung des Auftraggebers oder des Empfangs. *(offen)*
6. **Öffnungszeiten** (Rückmeldung 14. 9.: mit angeben, Besuchstag abfragen).
   *Gebaut: Feld `zeiten` und `geschlossen` je Ort, Besuchstag als
   freiwilliges Datum in Schritt 2; ein am Besuchstag geschlossener Ort
   fällt aus der Vorauswahl und die Zeile sagt es. Belegt sind nur
   Goetheanum (täglich 9 bis 20 Uhr) und Empfang (Di bis So 9 bis 18 Uhr).
   **Offen: Zeiten für Buchhandlung, Bibliothek, Café, Speisehaus,
   Vitalshop, Archiv, Schreinerei-Ausstellung** — bitte liefern, ich trage
   sie ein.*
7. **Lagen visuell korrigieren.** *Heizhaus, Transformatorenhaus,
   Verlagshaus und Café stehen jetzt im Katalog des Kartentools (dazu
   Schreinerei, Grosser Saal, Menschheitsrepräsentant; Haus Duldeck, de
   Jaager und Eurythmiehaus mit Gebäude verknüpft). Korrigieren: Kartentool
   im Justage-Modus öffnen
   (https://werkzeuge.goetheanum.ch/apps/karten-generator/#justage), Ort
   anschalten, am ✥ ziehen, «Justierte Lagen exportieren» → die JSON-Datei
   im Chat einfügen; die Werte wandern in
   `tools/karten/extract-marker-positionen.py`, und der Katalog wird
   neu erzeugt.*
8. **Aquarell als Grundkarte** (Rückmeldung 14. 9.). *(offen — nächste Etappe:
   Schalter auf der Karte, im PDF wie im Kartentool als Datei-Verweis.)*

### Ausgabe als PDF (Rückmeldung 14. 9.: Druckansicht war Schrott)

Ersetzt: kein Drucken mehr, sondern ein Vektor-PDF wie im Kartentool
(jsPDF und svg2pdf, Schrift eingebettet, `apps/campusplan/pdf.js`).
Blatt 1: Karte auf den Plan zugeschnitten, rechts die nummerierte
Legende — bei mehr als 22 Stationen enger gesetzt, was nicht mehr passt,
verweist auf Blatt 2. Blatt 2 und folgende: alle Stationen mit Einzeiler,
Zugang, Dauer und Zeiten in zwei Spalten, unten Link und QR-Code fürs
Telefon. Kein Beschnitt, keine Marken: A4 quer für den Drucker zuhause.
