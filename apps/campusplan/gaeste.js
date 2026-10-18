"use strict";

/* Gäste-Zeile je Ort (Konzept § 10, docs/specs/campusplan-besucher-konzept.md).
   Ergänzt den generierten Katalog apps/karten-generator/orte.js — der bleibt
   unberührt. Erster Entwurf vom 14. September 2026: Rang, Dauer, Zugang und
   Gehfolge sind Schätzungen zur Abnahme. Jeder Einzeiler hat eine Quelle in
   docs/campusplan-faktenpruefung.md — ohne Quelle kein Einzeiler (14. 9. 2026).

   WICHTIG: Die Reihenfolge in GAESTE ist das Bit im geteilten Link
   (#p=…). Nie umsortieren, nur hinten anhängen — sonst brechen alte Links. */

const THEMEN = [
  { id: "bau", name: { de: "Der Bau", en: "The Building" },
    kurz: { de: "Grosser Saal, Treppenhäuser, Glasfenster, Holzplastik",
            en: "Great Hall, staircases, stained glass, the wood sculpture" } },
  { id: "sammlung", name: { de: "Architektursammlung", en: "Architecture Collection" },
    kurz: { de: "Die Nebenbauten 1913 bis 1924: Heizhaus, Glashaus, Duldeck, de Jaager",
            en: "The colony buildings 1913 to 1924: Heizhaus, Glashaus, Duldeck, de Jaager" } },
  { id: "garten", name: { de: "Gartenpark", en: "Garden Park" },
    kurz: { de: "Felsli, Wasserspiel, Gärten, Gedenkhain",
            en: "Felsli rock, water feature, gardens, memorial grove" } },
  { id: "kultur", name: { de: "Bücher, Kunst, Ausstellungen", en: "Books, Art, Exhibitions" },
    kurz: { de: "Buchhandlung, Modell des Ersten Goetheanum, Atelier, Galerie",
            en: "Bookshop, model of the First Goetheanum, studio, gallery" } },
  { id: "essen", name: { de: "Essen und Verweilen", en: "Food and Rest" },
    kurz: { de: "Café in der Wandelhalle, Speisehaus, Vitalshop", en: "Café in the Wandelhalle, Speisehaus, Vitalshop" } },
  { id: "sektionen", name: { de: "Sektionen der Hochschule", en: "Sections of the School" },
    kurz: { de: "Wo die zwölf Sektionen arbeiten: Glashaus, Halde, Goetheanum und mehr",
            en: "Where the twelve sections work: Glashaus, Halde, Goetheanum and more" } }
];

const UMSTAENDE = [
  { id: "kinder", name: { de: "Mit Kindern", en: "With children" } },
  { id: "barrierefrei", name: { de: "Barrierefrei", en: "Step-free" } }
];

const ZEITEN = [
  { id: "2h", name: { de: "Zwei Stunden", en: "Two hours" }, minuten: 120 },
  { id: "halb", name: { de: "Halber Tag", en: "Half a day" }, minuten: 240 },
  { id: "ganz", name: { de: "Ganzer Tag", en: "Full day" }, minuten: 480 }
];

const WEGZEIT = 5; // Minuten Fussweg je Station, pauschal

const ZUGANG = {
  betreten: { de: "zu betreten", en: "open to enter" },
  aussen: { de: "von aussen, innen mit Führung", en: "from outside, inside with a guided tour" },
  anfrage: { de: "auf Anfrage", en: "on request" },
  fuehrung: { de: "mit Führung", en: "with a guided tour" }
};

/* Orte, die es nur im Gästeplan gibt (kein Katalog-Ort). Lage in Blatt-mm.
   Heizhaus, Transformatorenhaus, Verlagshaus, Schreinerei, Grosser Saal,
   Menschheitsrepräsentant und Café stehen seit dem 14. September 2026 im
   Katalog des Kartentools (tools/karten/extract-marker-positionen.py). */
const NEUE_ORTE = [
  { id: "n-treppen", label: { de: "Treppenhäuser", en: "Staircases" },
    positionen: [[184.3, 125.9]], gebaeude: "campusbau-53" }
];

/* oeffnung = Öffnungszeiten als Zeitfenster, ein Eintrag je Teil (der erste
   ist massgeblich für Zeitplan und «geschlossen»): fenster = { tage
   (0 = Sonntag, 1 = Montag …), von, bis }, dazu wahlweise ersterImMonat,
   zuMonate (1–12), vor (Vorsatz im Text, z. B. «innen»). Aus den Fenstern
   wird auch der Text der Zeile gesetzt.
   seite + quelle = woher die Zeiten live kommen: seite ist die Website (ohne
   Angabe goetheanum.ch/de/campus/oeffnungszeiten; sonst buchhandlung,
   bibliothek, archiv, speisehaus — Adressen in ZEITEN_SEITEN), quelle der Ort
   dort (Titel oder Teil davon). Alle Seiten liest die Edge Function
   campusplan-ausnahmen live (services/campusplan/): der Plan rechnet immer
   mit dem Stand der Websites (Aufträge 18. Oktober 2026: «Alle Öffnungszeiten
   aktuell abgleichen!»). Die Fenster hier sind nur der Rückfall; greift er,
   sagt der Plan «nicht bestätigt» und verlinkt die Seite. Ein täglicher
   Wächter prüft, dass jede quelle live gefunden wird
   (.github/workflows/oeffnungszeiten-waechter.yml).
   Orte im Goetheanum ohne eigene Zeiten (Haupteingang, Treppenhäuser,
   Galerie) tragen die Zeiten des Baus. Stand der Rückfallwerte: 18. Oktober 2026.
   name = Name im Gästeplan, wenn er vom Katalog abweicht; ausstellung = die
   Zeile zeigt die laufende Ausstellung (Sektion für Bildende Künste, live).
   ausnahmen = Seite mit tagesaktuellen Einschränkungen (Grosser Saal,
   Glashaus) — die Zeile verlinkt sie; live = Schlüssel in der Antwort der
   Edge Function, die zum Besuchstag die Tageszeile liefert.

   thema: basis (immer dabei, nummeriert) · anreise (immer dabei, unnummeriert)
   · eines der fünf Themen. rang 1 = Highlight. dauer in Minuten.
   barrierefrei:false = fällt bei ‹Barrierefrei› weg. kinder:true = rückt bei
   ‹Mit Kindern› nach vorn. gehfolge = Reihenfolge des Rundwegs. */
const TAEGLICH = [0, 1, 2, 3, 4, 5, 6];

// Websites der Öffnungszeiten (wie in der Edge Function) — der Plan verlinkt
// sie, wenn eine Zeit nicht live bestätigt ist.
const ZEITEN_SEITEN = {
  zeiten: "https://goetheanum.ch/de/campus/oeffnungszeiten",
  buchhandlung: "https://www.goetheanum-buchhandlung.ch/pages/oeffnungszeiten",
  bibliothek: "https://goetheanum.ch/de/dokumentation/bibliothek",
  archiv: "https://www.rudolf-steiner.com/",
  speisehaus: "https://www.speisehaus.ch/",
  ausstellungen: "https://sbk.goetheanum.org/veranstaltungen/ausstellungen"
};

const GAESTE = [
  { id: "o1", thema: "basis", gehfolge: 1, dauer: 0, zugang: "betreten",
    oeffnung: [{ quelle: "Goetheanum", fenster: [{ tage: TAEGLICH, von: "09:00", bis: "20:00" }] }] },
  { id: "o3", thema: "basis", gehfolge: 2, dauer: 5, zugang: "betreten",
    oeffnung: [{ quelle: "Kartenverkauf am Empfang", fenster: [{ tage: [2, 3, 4, 5, 6, 0], von: "09:00", bis: "18:00" }] }] },
  { id: "wc-goetheanum", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f46", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-bus", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-p", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "b-zugang", thema: "anreise", gehfolge: 0, dauer: 0, nurBarrierefrei: true },

  // Der Bau
  { id: "v16", thema: "bau", rang: 1, gehfolge: 6, dauer: 30, zugang: "betreten",
    oeffnung: [{ quelle: "Grosser Saal", fenster: [{ tage: TAEGLICH, von: "13:30", bis: "14:30" }] }],
    ausnahmen: "https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal", live: "saal",
    einzeiler: { de: "Knapp tausend Plätze unter einer Deckenmalerei in Pflanzenfarben, farbige Glasfenster von 1945.",
                 en: "Nearly a thousand seats under a ceiling painted in plant colours, stained glass from 1945." } },
  { id: "o46", thema: "bau", rang: 2, gehfolge: 8, dauer: 20, zugang: "betreten",
    oeffnung: [{ quelle: "Ausstellungsraum mit Holzskulptur", fenster: [{ tage: [1, 2, 3, 4], von: "14:30", bis: "15:30" }, { tage: [5], von: "14:00", bis: "16:00" },
      { tage: [6, 0], von: "10:00", bis: "12:00" }, { tage: [6, 0], von: "14:00", bis: "16:00" }] }],
    einzeiler: { de: "Die monumentale Skulptur des Menschheitsrepräsentanten: über acht Meter Holz, von Rudolf Steiner und Edith Maryon ab 1914.",
                 en: "The monumental sculpture of the Representative of Humanity: over eight metres of wood, by Rudolf Steiner and Edith Maryon from 1914." } },
  { id: "v12", thema: "bau", rang: 3, gehfolge: 5, dauer: 20, zugang: "betreten", kinder: true,
    oeffnung: [{ quelle: "Goetheanum", fenster: [{ tage: TAEGLICH, von: "09:00", bis: "20:00" }] },
      { quelle: "Vital-Café in der Wandelhalle", vor: { de: "Vital-Café", en: "Vital café" }, fenster: [{ tage: TAEGLICH, von: "09:00", bis: "17:00" }] }],
    einzeiler: { de: "Die Halle mit dem Vital-Café.", en: "The hall with the Vital café." } },
  { id: "n-treppen", thema: "bau", rang: 4, gehfolge: 7, dauer: 25, zugang: "betreten",
    oeffnung: [{ quelle: "Goetheanum", fenster: [{ tage: TAEGLICH, von: "09:00", bis: "20:00" }] }],
    einzeiler: { de: "Drei öffentliche Treppenhäuser, jedes eine architektonische Besonderheit: im Westtreppenhaus ganz oben das Rote Fenster, Nord- und Südtreppenhaus mit je einem Lift.",
                 en: "Three public staircases, each an architectural highlight: the Red Window at the very top of the west staircase; the north and south staircases each have a lift." } },

  // Architektursammlung
  { id: "h-heizhaus", thema: "sammlung", rang: 1, gehfolge: 17, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Die Heizanlage des Goetheanum, aus dem Hauptbau an den Nordhang gesetzt; der Kamin zwischen den Kuppeln formt Rauch und Feuer (1914).",
                 en: "The Goetheanum's heating plant, moved out of the main building onto the north slope; the chimney between the domes gives form to smoke and fire (1914)." } },
  { id: "v32", thema: "sammlung", rang: 2, gehfolge: 33, dauer: 10, zugang: "aussen",
    oeffnung: [{ quelle: "Entdeckung der Ganzheit", vor: { de: "Ausstellung ‹Die Entdeckung der Ganzheit›", en: "Exhibition ‹Die Entdeckung der Ganzheit›" }, fenster: [{ tage: [0], von: "15:00", bis: "16:00" }] }],
    ausnahmen: "https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe", live: "glashaus",
    einzeiler: { de: "Schleifatelier für die farbigen Fenster des Grossen Saals; die zwei Kuppeln des Ersten Goetheanum, hier auseinandergezogen und gleich gross (1914).",
                 en: "Grinding studio for the coloured windows of the Great Hall; the two domes of the First Goetheanum, here pulled apart and of equal size (1914)." } },
  { id: "h-schreinerei", thema: "sammlung", rang: 3, gehfolge: 12, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Die Bauhütte des Ersten Goetheanum, in der Steiner arbeitete und 1925 starb (1913).",
                 en: "The building lodge of the First Goetheanum, where Steiner worked and died in 1925 (1913)." } },
  { id: "o44", thema: "sammlung", rang: 4, gehfolge: 29, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-45"],
    oeffnung: [{ seite: "archiv", quelle: "Lesesaal & Shop", vor: { de: "Lesesaal und Shop des Archivs", en: "Archive reading room and shop" }, fenster: [{ tage: [1, 2, 3, 4, 5], von: "15:00", bis: "18:00" }] }],
    einzeiler: { de: "Von Steiner als Wohnhaus für die Familie Grossheintz entworfen, zum Dank für die Schenkung des Geländes; heute Rudolf-Steiner-Archiv (1915).",
                 en: "Designed by Steiner as a home for the Grossheintz family in thanks for donating the land; today the Rudolf Steiner Archive (1915)." } },
  { id: "v31", thema: "sammlung", rang: 5, gehfolge: 32, dauer: 15, zugang: "aussen", kinder: true,
    einzeiler: { de: "Den Anbau entwarf Steiner 1924 als Proberaum für die Eurythmie; seine zwei Pfeiler an der Westfront kehren am Zweiten Goetheanum wieder.",
                 en: "Steiner designed the extension in 1924 as a eurythmy rehearsal room; its two pillars on the west front return on the Second Goetheanum." } },
  { id: "h-trafo", thema: "sammlung", rang: 6, gehfolge: 26, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Steiners Bau für die unsichtbare Elektrizität: gerade, kubisch ineinandergesteckte Formen (1921).",
                 en: "Steiner's building for invisible electricity: straight, cubic forms slotted into one another (1921)." } },
  { id: "h-jaager", thema: "sammlung", rang: 7, gehfolge: 25, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-50"],
    oeffnung: [{ quelle: "Haus de Jaager", vor: { de: "innen", en: "inside" }, ersterImMonat: true, zuMonate: [7, 8], fenster: [{ tage: [5], von: "15:00", bis: "16:00" }] }],
    einzeiler: { de: "Von Steiner für den Nachlass des Bildhauers Jacques de Jaager entworfen: Wohnhaus und Ausstellungsatelier in einem (1921/22).",
                 en: "Designed by Steiner for the estate of the sculptor Jacques de Jaager: home and exhibition studio in one (1921/22)." } },
  { id: "h-eurythmie", thema: "sammlung", rang: 8, gehfolge: 23, dauer: 10, zugang: "aussen",
    gebaeude: ["campusbau-47", "campusbau-48", "campusbau-49"],
    einzeiler: { de: "Drei Wohnhäuser für die Eurythmistinnen und Eurythmisten am Goetheanum; die Bildhauerin Edith Maryon entwarf mit und wohnte hier (1921).",
                 en: "Three houses for the eurythmists at the Goetheanum; the sculptor Edith Maryon co-designed them and lived here (1921)." } },
  { id: "h-verlag", thema: "sammlung", rang: 9, gehfolge: 34, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Nach Skizzen Steiners als Büchermagazin des Philosophisch-Anthroposophischen Verlags gebaut, heute Lager; das umhüllende Dach weist auf das Gewölbe des Zweiten Goetheanum (1924).",
                 en: "Built to Steiner's sketches as the book store of the Philosophisch-Anthroposophischer Verlag, today used for storage; its enveloping roof points to the vault of the Second Goetheanum (1924)." } },

  // Gartenpark
  { id: "g-felsli", thema: "garten", rang: 1, gehfolge: 30, dauer: 15, zugang: "betreten", barrierefrei: false,
    einzeiler: { de: "Das westliche Ende des Hügels.", en: "The western end of the hill." } },
  { id: "g-wasserspiel", thema: "garten", rang: 2, gehfolge: 35, dauer: 10, zugang: "betreten", kinder: true },
  { id: "g-gedenkhain", thema: "garten", rang: 3, gehfolge: 31, dauer: 15, zugang: "betreten",
    einzeiler: { de: "Urnenhain, in dem Rudolf Steiner, Marie Steiner-von Sivers und Christian Morgenstern ruhen.",
                 en: "Urn grove where Rudolf Steiner, Marie Steiner-von Sivers and Christian Morgenstern rest." } },
  { id: "g-heilkraeuter", thema: "garten", rang: 6, gehfolge: 11, dauer: 10, zugang: "betreten" },
  { id: "g-duftkraeuter", thema: "garten", rang: 7, gehfolge: 19, dauer: 10, zugang: "betreten" },
  { id: "g-faerberpflanzen", thema: "garten", rang: 8, gehfolge: 20, dauer: 10, zugang: "betreten" },
  { id: "g-schnittblumen", thema: "garten", rang: 9, gehfolge: 21, dauer: 10, zugang: "betreten" },
  { id: "g-bienen", thema: "garten", rang: 4, gehfolge: 22, dauer: 10, zugang: "betreten", kinder: true,
    einzeiler: { de: "Begehbare Skulptur von Barbara Schnetzler, sieben Meter hoch im Grundriss einer Wabe; innen riecht man Wachs und sieht durch Glas ins Bienenvolk. Ausgezeichnet vom Kanton Solothurn und der Plattform March.",
                 en: "Walk-in sculpture by Barbara Schnetzler, seven metres tall on a honeycomb plan; inside you smell wax and see the bees through glass. Honoured by the Canton of Solothurn and the platform March." } },
  { id: "g-praeparate", thema: "garten", rang: 5, gehfolge: 18, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Neubau von 2025 für die Herstellung der biodynamischen Präparate: gedrehte Holzträger wie eine Blüte, begrüntes Dach; Iconic Award 2025 und German Design Award 2026.",
                 en: "New building of 2025 for making the biodynamic preparations: twisted timber beams like a flower, green roof; Iconic Award 2025 and German Design Award 2026." } },

  // Bücher, Kunst, Ausstellungen
  { id: "o5", thema: "kultur", rang: 1, gehfolge: 4, dauer: 20, zugang: "betreten",
    oeffnung: [{ seite: "buchhandlung", quelle: "Allgemeine Öffnungszeiten", fenster: [{ tage: [2, 3, 4, 5], von: "10:00", bis: "18:00" }, { tage: [6], von: "10:00", bis: "17:00" }, { tage: [0], von: "11:00", bis: "16:00" }] }] },
  { id: "o41", thema: "kultur", rang: 2, gehfolge: 13, dauer: 30, zugang: "betreten",
    oeffnung: [{ quelle: "Baugeschichte und Modell Erstes Goetheanum", fenster: [{ tage: [5, 6, 0], von: "14:00", bis: "16:00" }] }],
    einzeiler: { de: "Modell des Ersten Goetheanum, das in der Silvesternacht 1922 abbrannte. Schreinerei Südsaal links, Eintritt CHF 5.",
                 en: "Model of the First Goetheanum, which burned on New Year's Eve 1922. Schreinerei south hall, left; admission CHF 5." } },
  { id: "o40", thema: "kultur", rang: 3, gehfolge: 14, dauer: 15, zugang: "betreten",
    oeffnung: [{ quelle: "Rudolf Steiner Atelier", fenster: [{ tage: [5], von: "14:00", bis: "15:00" }] }],
    einzeiler: { de: "Schreinerei, rechter Eingang.", en: "Schreinerei, right-hand entrance." } },
  { id: "o6", thema: "kultur", rang: 4, gehfolge: 9, dauer: 20, zugang: "betreten", ausstellung: true,
    name: { de: "Galerie, 1. Etage", en: "Gallery, 1st floor" },
    oeffnung: [{ quelle: "Goetheanum", fenster: [{ tage: TAEGLICH, von: "09:00", bis: "20:00" }] }] },
  { id: "o7", thema: "kultur", rang: 5, gehfolge: 10, dauer: 20, zugang: "betreten",
    oeffnung: [{ seite: "bibliothek", quelle: "Öffnungszeiten", fenster: [{ tage: [2, 4, 5], von: "14:00", bis: "18:00" }] }] },
  { id: "o42", thema: "kultur", rang: 6, gehfolge: 15, dauer: 10, zugang: "betreten",
    oeffnung: [{ quelle: "Hochatelier", fenster: [{ tage: [5], von: "14:30", bis: "15:30" }] }],
    einzeiler: { de: "Blaues Holzhaus im Südwesten der Schreinerei: hier arbeiteten Steiner und Edith Maryon 1914 bis 1925 an der Holzskulptur; ihr 1:1-Modell steht noch heute hier.",
                 en: "Blue wooden house south-west of the Schreinerei: here Steiner and Edith Maryon worked on the wood sculpture from 1914 to 1925; its 1:1 model still stands here." } },
  { id: "o43", thema: "kultur", rang: 7, gehfolge: 24, dauer: 10, zugang: "betreten",
    oeffnung: [{ quelle: "Künstlerwohnung Edith Maryon", fenster: [{ tage: [5], von: "15:30", bis: "16:30" }] }],
    einzeiler: { de: "Unteres Eurythmiehaus, Rüttiweg 30, 1. Etage.", en: "Lower Eurythmiehaus, Rüttiweg 30, first floor." } },

  // Essen und Verweilen
  // Grabstein: das Café war kurz ein eigener Ort (o8), liegt aber in der
  // Wandelhalle (v12). Die Zeile bleibt, damit das Link-Bit nicht rutscht.
  { id: "o8", thema: "aus", rang: 99, gehfolge: 0, dauer: 0 },
  { id: "o45", thema: "essen", rang: 2, gehfolge: 27, dauer: 60, zugang: "betreten", kinder: true,
    oeffnung: [{ seite: "speisehaus", quelle: "Laden", vor: { de: "Laden", en: "Shop" }, fenster: [{ tage: [1, 2, 3, 4, 5], von: "08:00", bis: "18:30" }, { tage: [6, 0], von: "08:00", bis: "16:00" }] }],
    hinweis: { de: "Restaurant zurzeit geschlossen", en: "restaurant currently closed" } },
  { id: "f-vital", thema: "essen", rang: 3, gehfolge: 28, dauer: 15, zugang: "betreten",
    oeffnung: [{ seite: "speisehaus", quelle: "Laden", fenster: [{ tage: [1, 2, 3, 4, 5], von: "08:00", bis: "18:30" }, { tage: [6, 0], von: "08:00", bis: "16:00" }] }] },
  { id: "v23", thema: "essen", rang: 4, gehfolge: 16, dauer: 15, zugang: "anfrage",
    einzeiler: { de: "Ein Eurythmiesaal bei der Schreinerei; im Sommer wird er so heiss, dass er seinen Spitznamen bekam.",
                 en: "A eurythmy hall by the Schreinerei; in summer it gets so hot that it earned its nickname." } },

  // Sektionen der Hochschule (Arbeitsorte: Zugang auf Anfrage; Gehfolge folgt
  // dem Haus, in dem sie sitzen — nachgestellt hinter den jeweiligen Bau)
  { id: "s-allgemein", thema: "sektionen", rang: 1, gehfolge: 7, dauer: 10, zugang: "anfrage" },
  { id: "s-natur", thema: "sektionen", rang: 2, gehfolge: 33, dauer: 10, zugang: "anfrage" },
  { id: "s-landwirtschaft", thema: "sektionen", rang: 3, gehfolge: 33, dauer: 10, zugang: "anfrage" },
  { id: "s-paedagogik", thema: "sektionen", rang: 4, gehfolge: 7, dauer: 10, zugang: "anfrage" },
  { id: "s-schoene", thema: "sektionen", rang: 5, gehfolge: 32, dauer: 10, zugang: "anfrage" },
  { id: "s-redende", thema: "sektionen", rang: 6, gehfolge: 7, dauer: 10, zugang: "anfrage" },
  { id: "s-sozial", thema: "sektionen", rang: 7, gehfolge: 18, dauer: 10, zugang: "anfrage" },
  { id: "s-mathematik", thema: "sektionen", rang: 8, gehfolge: 21, dauer: 10, zugang: "anfrage" },
  { id: "s-medizin", thema: "sektionen", rang: 9, gehfolge: 25, dauer: 10, zugang: "anfrage" },
  { id: "s-jugend", thema: "sektionen", rang: 10, gehfolge: 10, dauer: 10, zugang: "anfrage" },
  { id: "s-bildende", thema: "sektionen", rang: 11, gehfolge: 35, dauer: 10, zugang: "anfrage" },
  { id: "s-heilpaedagogik", thema: "sektionen", rang: 12, gehfolge: 26, dauer: 10, zugang: "anfrage" },

  // Nachtrag 14. 9.: das Helene-Finckh-Haus ist samstags offen (goetheanum.ch)
  { id: "h-finckh", thema: "sammlung", rang: 10, gehfolge: 18, dauer: 10, zugang: "betreten",
    oeffnung: [{ quelle: "Helene-Finckh-Haus", fenster: [{ tage: [6], von: "15:00", bis: "16:00" }] }],
    einzeiler: { de: "Benannt nach Helene Finckh (1883 bis 1960), Rudolf Steiners wichtigster Stenographin, die ab 1915 rund 1700 seiner Vorträge mitschrieb. Hügelweg 64 A, oberhalb des Parkplatzes.",
                 en: "Named after Helene Finckh (1883 to 1960), Rudolf Steiner's most important stenographer, who took down some 1,700 of his lectures from 1915. Hügelweg 64 A, above the car park." } }
];
