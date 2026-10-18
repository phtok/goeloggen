# Leitsystem-Befund: Was grafik.goetheanum.ch zum Leitsystem enthält — und was davon zu uns kommt

Stand: 10. Juli 2026 · Untersucht: grafik.goetheanum.ch (Squarespace-Portal),
Rubrik «Leitsystem» samt Etagen-Katalog und Nachbarrubriken (Kartierung,
Werkstatt, Icons) — abgeglichen mit dem Stand im Repo (Schilder-App,
Icon-Satz v2.7, Typo-Regelwerk, Strategieblatt).

## 1 · Fundstellen auf grafik.goetheanum.ch

| Seite | Inhalt | Zustand |
|---|---|---|
| `/leitsystem-grundsaetze` | die Gestaltungsprinzipien des gebauten Leitsystems im Goetheanum-Bau — Sprache, Raum, Material, Schrift, Beschriftungsarten, Icons, offene Fragen, Ausführung, Rollen | **die Hauptquelle**, vollständig, nur hier |
| `/erdgeschoss` | Katalog der ausgeführten Beschilderung im Erdgeschoss: 15 Einträge (Empfang, Grosser Saal, Buchhandlung, Lifte, WCs, Wegweiser …) mit Beschriftungsart je Element (Opak · Glimmer · Schablone) | Foto-Dokumentation, Bilder auf Squarespace-CDN |
| `/galerieetage` · `/westtreppenhaus` · `/suedtreppenhaus` · `/nordtreppenhaus` | weitere Etagen-Kataloge, primär Fotos, kaum Text | Foto-Dokumentation |
| `/kartierung` | Geländekarte (Illustrator, Stand Dez. 2021) + Anwendungsbeispiele | bereits abgelöst: Kartentool ist live, Pflichtenheft liegt in `docs/specs/` |
| `/werkstatt` | neun Artikel (Logo, Wortmarke, Schrift-Geschichte) | **kein** Leitsystem-Artikel — die Grundsätze-Seite ist die einzige Quelle |

## 2 · Inventar der Grundsätze (vollständig, weil nur dort dokumentiert)

**Zweck.** Das Leitsystem weist Besucher mit Beschriftungen und Icons durch
den Bau; je Etage gibt es einen Orientierungsplan (am Empfang erhältlich).

**Sprache.** Alle Elemente zweisprachig Deutsch/Englisch, Standard
untereinander. Ausnahmen: in beiden Sprachen identische Begriffe und
festgelegte Raumnamen («Grundsteinsaal»); in Sonderfällen (Lift) einzeilig.

**Raum.** Signaletik greift in die architektonische Substanz ein — die
Beschriftung hält sich deshalb bewusst zurück. Raumnamen ändern sich; die
Flexibilität steckt in der Materialwahl (Folie statt Gravur und Bohrung).

**Material — der Untergrund bestimmt die Ausführung:**

| Untergrund | Ausführung |
|---|---|
| Putz | farbig bedruckte matte Folie **oder** Schablone mit mineralischen KEIM-Farben; Farbton aus der Untergrundfarbe entwickelt, dunkler und kontrastreich |
| Beton | **nur** dunkelgrau bedruckte Klebefolie (Denkmalschutz); weisse Folie stört, Bohrungen vermeiden |
| Glas(-türen) | halbtransparente Crystalfolie («Glimmer»); auf Aussentüren gespiegelt von innen geklebt |
| Holz | auf unruhigen oder dunklen Flächen weisse matte Folie; Fräsung denkbar |

**Schrift (Stand der alten Seite).** Titillium, eigens um einen
Medium-Schnitt erweitert; Deutsch läuft in Medium, Englisch in Light
(als Fonts «Goetheanum Text Deutsch» und «Goetheanum Titel Englisch»).
Grössenstufen: auf Glastüren fest 160 pt (Raumname) · 80 pt (Zusatz) ·
60 pt (Information/Uhrzeit); auf Beton, Putz und Holz situativ aus der
Reihe 280 · 240 · 200 · 160 · 120 · 80 · 60 pt.

**Zwei Beschriftungsarten.**
- *Bezeichnend* (auf und über Türen, benennt den Raum dahinter):
  Ausrichtung folgt der **Wandkante** — nahe rechter Kante rechtsbündig,
  nahe linker Kante linksbündig, über Türen zentriert. Nicht der
  Bewegungsrichtung, der Kante.
- *Weisend* (auf Wänden, deren Neigung bereits Richtung gestikuliert):
  gleiche Kantenregel, Pfeile stützen die Richtung.

**Icons.** Set von Severin Geissler: Toiletten, Hundeplatz, WLAN,
Garderobe, Schliessfächer, Handy aus, keine Fotos. Duktus an den
Titillium-Buchstaben orientiert: geradlinig, dynamisch gebogen, simpel;
harte Ecken abgekantet, Konturlinien zum Ende hin dünner.

**Offene Fragen (auf der Seite ehrlich festgehalten):**
1. Drücken/Ziehen-Beschilderung auf Türen funktionierte nicht ausreichend — Überarbeitung nötig.
2. Messingschilder auf Holztürrahmen (gegen Spiegelung) — ungelöst.
3. Adhäsive Folie auf Glas: leicht entfernbar, in der Praxis unpraktisch.

**Ausführung und Rollen (Betriebswissen, nirgends sonst notiert).**
Foliendruck, -schnitt und Anbringung: Scheller (scheller.ch) ·
Schablonen-Malerei: Georg Müller (Hausmaler) mit KEIM-Mineralfarben ·
Positionierung im Gebäude: Susanne Mandl und Severin Geissler ·
Betrieb: Rebekka Frischknecht · Weiterentwicklung: Philipp Tok.
Dazu eine DIY-Anleitung für kleine Korrekturen: Untergrund staubfrei,
Folie mit Heissluftföhn weich machen (haftet in der Wandstruktur),
Glas mit Reinigungsbenzin reinigen, mit Rakel andrücken.

## 3 · Abgleich: was bei uns schon lebt

- **Icons:** Der alte Sieben-Zeichen-Satz lebt im Haus-Icon-Font v2.7
  weiter und ist auf **81 Zeichen** gewachsen (Piktogramme, Text-Varianten,
  Pfeile, Kompass, gebogene Pfeile) — als Webfont, SVG, PNG, PDF
  (`icons.html`, live). Der Duktus-Grundsatz (aus der Schrift entwickelt,
  Linienenden dünner) ist dort eingelöst.
- **Schrift:** Die Hausschrift v2.7 ist die zu Ende gebaute Titillium.
  Für Signaletik ist heute **Laut (680)** der benannte Schnitt
  (Font-README, Tokens, Beipackzettel); die Schau ist als eigene
  Lesesituation im Regelwerk verankert (G27), Versalsatz ist nur dort
  zulässig (G23).
- **Werkzeug:** `apps/schilder/` (Entwurf) setzt Orientierungsschilder
  A5 quer — Zeilen, Haus-Icons und -Pfeile, mm-genaue Vorschau, Druck.
  Die Türschild-Vorlagen warten laut Quelltext darauf, dass «die genauen
  Masse vorliegen».
- **Strategie:** `docs/strategie.md` führt Leitsystem als ❌ mit To-do
  «Schilder-Generator»; das alte Portal wird mittelfristig abgelöst.
- **Kartierung:** durch das Kartentool abgelöst; das Pflichtenheft
  schliesst Leitsystem-Sonderformate aus v1 bewusst aus.

## 4 · Was wir brauchen — und in welcher Form

1. **Die Grundsätze als Regelwerk ins Repo.** Material-Matrix,
   Zweisprachigkeits-Regel, Kantenregel, bezeichnend/weisend und die
   Grössenstufen sind das fehlende Fundament des Schilder-Generators —
   sie gehören als Regeln zu uns (analog Typo-Regeln), nicht auf
   Squarespace. Dieser Befund ist der erste Schritt.
2. **Die Grössenstufen sind die ‹genauen Masse›.** Worauf die
   Schilder-App wartet, steht zum Teil längst auf der alten Seite:
   Glastür 160/80/60 pt, Wandreihe 280–60 pt. Daraus lassen sich die
   Türschild-Vorlagen (Name/Funktion) und die Grössen-Presets ableiten —
   offen bleiben nur die physischen Schildformate in mm.
3. **Den Etagen-Katalog sichern, bevor das Portal fällt.** Die Fotos der
   ausgeführten Beschilderung (mit Beschriftungsart je Element) liegen auf
   dem Squarespace-CDN und verschwinden mit der Ablösung. Sie sind die
   einzige Bestandsdokumentation des gebauten Systems.
4. **Betriebswissen übernehmen.** Lieferanten (Scheller, KEIM),
   Zuständigkeiten und die DIY-Korrektur-Anleitung sind Betriebswissen
   des Hauses — gehört in die Übergabe-/Betriebsdokumentation, nicht in
   den Papierkorb.

## 5 · Was weiterleben kann (schriftunabhängig gültig)

- Zurückhaltung vor der architektonischen Substanz, Denkmalschutz als
  harte Grenze (Beton: nur dunkelgraue Folie, keine Bohrung).
- Der Untergrund bestimmt Verfahren und Farbigkeit (Material-Matrix).
- Zweisprachigkeit als Standardfall mit klaren, benannten Ausnahmen.
- Die Kantenregel der Ausrichtung und die Unterscheidung
  bezeichnend/weisend.
- Flexibilität durch Folie: Raumnamen ändern sich, das System rechnet
  damit.
- Der Icon-Duktus — bereits in v2.7 aufgenommen und ausgebaut.

## 6 · Was übersetzt werden muss — Entscheid des Auftraggebers nötig

**Die Schnitt-Zuordnung widerspricht dem heutigen Stand.** Alt:
Deutsch = Medium, Englisch = Light (zwei Gewichte trennen die Sprachen).
Heute sagen Font-README und Tokens: Signaletik = **Laut**. Beides
zugleich geht nicht — entweder trägt ein Schnitt beide Sprachen und die
Trennung kommt aus Grösse/Stellung, oder die Zwei-Gewichte-Logik wird in
die neuen Schnitte übersetzt (etwa Deutsch Laut/Deutlich, Englisch
Klar/Ruhig — **nie** Leise in kleiner Signaletik). Das ist der Fall aus
den Arbeitsregeln: Widerspruch zwischen Regelwerk und Schrift **melden,
nicht eigenmächtig entscheiden** — hiermit gemeldet.

Kleiner: die pt-Stufen der alten Seite sind Druck-/Plotmasse, keine
Bildschirmgrössen (B03 gilt der Bedienung, nicht dem Artefakt — wie in
der Schilder-App bereits kommentiert).

## 7 · Learnings, die unbedingt mitkommen

1. **Die drei dokumentierten Fehlschläge** (Drücken/Ziehen wirkungslos,
   Folie auf Glas unpraktisch, Messingfrage offen) sind teuer erkauftes
   Wissen. Wer Türschilder als Vorlage baut, plant Drücken/Ziehen nicht
   einfach nach altem Muster.
2. **Wechselbarkeit ist das Konstruktionsprinzip.** Das alte System wählte
   Folie, weil Raumnamen wandern. Für uns heisst das: der eigentliche
   Fortschritt ist die **Selbstbedienung** — ein Generator, mit dem das
   Haus Schilder in Minuten nachsetzt, ist die konsequente Fortsetzung
   der DIY-Anleitung.
3. **Der Untergrund ist der erste Parameter.** Ein künftiger
   Schilder-Generator fragt zuerst «worauf kommt das?» (Putz, Beton,
   Glas, Holz, freistehendes Schild) — daraus folgen Farbe, Folie,
   Verfahren und Grössenreihe, nicht umgekehrt.
4. **Ehrlich dokumentierte offene Fragen** haben das Wissen fünf Jahre
   über Personalwechsel hinweg gerettet — die Rubrik gehört auch in
   unsere Werkzeuge und Befunde.
5. **Icons aus der Schrift entwickeln** hat sich bewährt: der
   Geissler-Duktus überlebte den Schriftwechsel, weil er ein Prinzip war,
   keine Datei.

## 8 · Nächste Schritte (Vorschlag, nicht begonnen)

1. Entscheid einholen: Schnitt-Zuordnung Deutsch/Englisch in der neuen
   Hausschrift (Abschnitt 6).
2. Etagen-Katalog-Fotos vom Squarespace-CDN sichern (`reference/` oder
   Übergabe-Ablage).
3. Schilder-App: Türschild-Vorlagen aus den Grössenstufen ableiten;
   Untergrund-Wahl als ersten Parameter einplanen.
4. Bei Ablösung des Portals: `/leitsystem-grundsaetze` auf unsere
   Fassung weiterleiten, damit die einzige Quelle nicht bricht.
