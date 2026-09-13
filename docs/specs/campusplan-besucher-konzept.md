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
fertigen Rundgängen zum Anpassen. Erste Etappe am Empfang statt im
Internet: die Person am Empfang baut den Plan mit dem Gast in einer
Minute, druckt ihn oder zeigt den QR-Code fürs Telefon. Das braucht
keinen Hosting-Entscheid und liefert sofort Erfahrung, welche Orte Gäste
wirklich wollen.

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
2. **Empfangs-Fassung (Labor).** Seite `apps/campusplan/` aus dem
   Starter: Rundgang wählen → anpassen → Druck-PDF und Link mit QR. Läuft
   im Backstage, der Empfang arbeitet damit. Registrierung in
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
