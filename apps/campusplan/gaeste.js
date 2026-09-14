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
  aussen: { de: "von aussen", en: "from outside" },
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

/* zeiten = Öffnungszeit als Satz (DE/EN); geschlossen = Wochentage (0 = Sonntag,
   1 = Montag …), an denen der Ort zu ist — bei gewähltem Besuchstag fällt er
   aus der Vorauswahl und die Zeile sagt es. Ohne Angabe: keine Aussage.
   Belegt (Stand 14. September 2026): Goetheanum täglich 9 bis 20 Uhr und
   Empfang Di bis So 9 bis 18 Uhr (goetheanum.ch/de/besuch); Buchhandlung
   Di bis Fr 10 bis 18, Sa 10 bis 17, So 11 bis 16 Uhr, Mo zu
   (goetheanum-buchhandlung.ch); Bibliothek Di, Do, Fr 14 bis 18 Uhr,
   Sommerpause (goetheanum.ch/en/documentation/library); Archiv-Lesesaal
   Mo bis Fr 15 bis 18 Uhr (rudolf-steiner.com); Speisehaus-Laden Mo bis Fr
   8 bis 18.30, Sa und So 8 bis 16 Uhr, Restaurant zurzeit geschlossen
   (speisehaus.ch). Ausstellungsräume, Grosser Saal, Vital-Café, Glashaus,
   Haus de Jaager, Helene-Finckh-Haus: goetheanum.ch/de/campus/oeffnungszeiten.
   ausnahmen = Seite mit tagesaktuellen Einschränkungen (Grosser Saal,
   Glashaus) — die Zeile verlinkt sie; live = Schlüssel in der Antwort der
   Edge Function campusplan-ausnahmen (services/campusplan/), die diese
   Seiten liest und zum Besuchstag die Tageszeile liefert.

   thema: basis (immer dabei, nummeriert) · anreise (immer dabei, unnummeriert)
   · eines der fünf Themen. rang 1 = Highlight. dauer in Minuten.
   barrierefrei:false = fällt bei ‹Barrierefrei› weg. kinder:true = rückt bei
   ‹Mit Kindern› nach vorn. gehfolge = Reihenfolge des Rundwegs. */
const GAESTE = [
  { id: "o1", thema: "basis", gehfolge: 1, dauer: 0, zugang: "betreten" },
  { id: "o3", thema: "basis", gehfolge: 2, dauer: 5, zugang: "betreten",
    zeiten: { de: "Di bis So 9 bis 18 Uhr", en: "Tue to Sun 9 am to 6 pm" }, geschlossen: [1] },
  { id: "wc-goetheanum", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f46", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-bus", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-p", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "b-zugang", thema: "anreise", gehfolge: 0, dauer: 0, nurBarrierefrei: true },

  // Der Bau
  { id: "v16", thema: "bau", rang: 1, gehfolge: 6, dauer: 30, zugang: "betreten",
    zeiten: { de: "Besichtigung täglich 13.30 bis 14.30 Uhr, Ausnahmen bei Veranstaltungen und Proben", en: "Viewing daily 1.30 to 2.30 pm, exceptions for events and rehearsals" },
    ausnahmen: "https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal", live: "saal",
    einzeiler: { de: "Knapp tausend Plätze unter einer Deckenmalerei in Pflanzenfarben, farbige Glasfenster von 1945.",
                 en: "Nearly a thousand seats under a ceiling painted in plant colours, stained glass from 1945." } },
  { id: "o46", thema: "bau", rang: 2, gehfolge: 8, dauer: 20, zugang: "betreten",
    zeiten: { de: "Mo bis Do 14.30 bis 15.30, Fr 14 bis 16, Sa und So 10 bis 12 und 14 bis 16 Uhr", en: "Mon to Thu 2.30 to 3.30 pm, Fri 2 to 4 pm, Sat and Sun 10 am to noon and 2 to 4 pm" },
    einzeiler: { de: "Die über acht Meter hohe Holzskulptur von Rudolf Steiner und Edith Maryon, entstanden ab 1914.",
                 en: "The wood sculpture over eight metres tall by Rudolf Steiner and Edith Maryon, begun in 1914." } },
  { id: "v12", thema: "bau", rang: 3, gehfolge: 5, dauer: 20, zugang: "betreten", kinder: true,
    zeiten: { de: "täglich 9 bis 20 Uhr, Vital-Café 9 bis 17 Uhr", en: "daily 9 am to 8 pm, Vital café 9 am to 5 pm" },
    einzeiler: { de: "Die Halle mit dem Vital-Café.", en: "The hall with the Vital café." } },
  { id: "n-treppen", thema: "bau", rang: 4, gehfolge: 7, dauer: 10, zugang: "betreten",
    einzeiler: { de: "Haupt-, Nord- und Südtreppe mit Liften zu Galerie und Grossem Saal.",
                 en: "Main, north and south staircases with lifts to the gallery and the Great Hall." } },

  // Architektursammlung
  { id: "h-heizhaus", thema: "sammlung", rang: 1, gehfolge: 17, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Der erste Betonbau des Hügels: ein Heizwerk mit sphinxhafter Form, bis heute in Betrieb (1915).",
                 en: "The hill's first concrete building: a boiler house of sphinx-like form, still in use (1915)." } },
  { id: "v32", thema: "sammlung", rang: 2, gehfolge: 33, dauer: 10, zugang: "aussen",
    zeiten: { de: "Ausstellung ‹Die Entdeckung der Ganzheit› So 15 bis 16 Uhr", en: "Exhibition ‹Die Entdeckung der Ganzheit› Sun 3 to 4 pm" },
    ausnahmen: "https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe", live: "glashaus",
    einzeiler: { de: "Zwei Kuppeln unter Schiefer, gebaut zum Schleifen der Glasfenster des Ersten Goetheanum (1914).",
                 en: "Two domes under slate, built for grinding the stained glass of the First Goetheanum (1914)." } },
  { id: "h-schreinerei", thema: "sammlung", rang: 3, gehfolge: 12, dauer: 10, zugang: "betreten",
    einzeiler: { de: "Die Bauhütte des Ersten Goetheanum, in der Steiner arbeitete und 1925 starb (1913).",
                 en: "The building lodge of the First Goetheanum, where Steiner worked and died in 1925 (1913)." } },
  { id: "o44", thema: "sammlung", rang: 4, gehfolge: 29, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-45"],
    zeiten: { de: "Lesesaal und Shop des Archivs Mo bis Fr 15 bis 18 Uhr", en: "Archive reading room and shop Mon to Fri 3 pm to 6 pm" },
    einzeiler: { de: "Eisenbeton-Wohnhaus für den Stifter des Grundstücks, seit 2002 Rudolf-Steiner-Archiv (1915).",
                 en: "Reinforced-concrete home of the land's donor, the Rudolf Steiner Archive since 2002 (1915)." } },
  { id: "v31", thema: "sammlung", rang: 5, gehfolge: 32, dauer: 15, zugang: "betreten", kinder: true,
    einzeiler: { de: "Der Betonanbau von 1923 war der Versuchsbau für das zweite Goetheanum, heute Tagungshaus.",
                 en: "The 1923 concrete extension was the trial build for the second Goetheanum, now a conference house." } },
  { id: "h-trafo", thema: "sammlung", rang: 6, gehfolge: 26, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Steiners Trafostation mit kubischen Auskragungen, bis heute am Netz (1921).",
                 en: "Steiner's transformer station with cubic projections, still on the grid (1921)." } },
  { id: "h-jaager", thema: "sammlung", rang: 7, gehfolge: 25, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-50"],
    zeiten: { de: "innen jeden ersten Freitag im Monat 15 bis 16 Uhr, Juli und August geschlossen", en: "inside every first Friday of the month 3 to 4 pm, closed July and August" },
    einzeiler: { de: "Privates Wohnhaus von 1921 mit dem künstlerischen Nachlass des Bildhauers Jacques de Jaager.",
                 en: "Private home of 1921 with the artistic estate of the sculptor Jacques de Jaager." } },
  { id: "h-eurythmie", thema: "sammlung", rang: 8, gehfolge: 23, dauer: 10, zugang: "aussen",
    gebaeude: ["campusbau-47", "campusbau-48", "campusbau-49"],
    einzeiler: { de: "Drei Wohnhäuser nach Entwurf von Edith Maryon (1920).",
                 en: "Three houses designed by Edith Maryon (1920)." } },
  { id: "h-verlag", thema: "sammlung", rang: 9, gehfolge: 34, dauer: 10, zugang: "aussen" },

  // Gartenpark
  { id: "g-felsli", thema: "garten", rang: 1, gehfolge: 30, dauer: 15, zugang: "betreten", barrierefrei: false,
    einzeiler: { de: "Das westliche Ende des Hügels.", en: "The western end of the hill." } },
  { id: "g-wasserspiel", thema: "garten", rang: 2, gehfolge: 35, dauer: 10, zugang: "betreten", kinder: true },
  { id: "g-gedenkhain", thema: "garten", rang: 3, gehfolge: 31, dauer: 15, zugang: "betreten",
    einzeiler: { de: "Urnenhain, in dem Rudolf Steiner, Marie Steiner-von Sivers und Christian Morgenstern ruhen.",
                 en: "Urn grove where Rudolf Steiner, Marie Steiner-von Sivers and Christian Morgenstern rest." } },
  { id: "g-heilkraeuter", thema: "garten", rang: 4, gehfolge: 11, dauer: 10, zugang: "betreten" },
  { id: "g-duftkraeuter", thema: "garten", rang: 5, gehfolge: 19, dauer: 10, zugang: "betreten" },
  { id: "g-faerberpflanzen", thema: "garten", rang: 6, gehfolge: 20, dauer: 10, zugang: "betreten" },
  { id: "g-schnittblumen", thema: "garten", rang: 7, gehfolge: 21, dauer: 10, zugang: "betreten" },
  { id: "g-bienen", thema: "garten", rang: 8, gehfolge: 22, dauer: 10, zugang: "betreten", kinder: true },
  { id: "g-praeparate", thema: "garten", rang: 9, gehfolge: 18, dauer: 10, zugang: "aussen" },

  // Bücher, Kunst, Ausstellungen
  { id: "o5", thema: "kultur", rang: 1, gehfolge: 4, dauer: 20, zugang: "betreten",
    zeiten: { de: "Di bis Fr 10 bis 18, Sa 10 bis 17, So 11 bis 16 Uhr", en: "Tue to Fri 10 am to 6 pm, Sat 10 am to 5 pm, Sun 11 am to 4 pm" }, geschlossen: [1] },
  { id: "o41", thema: "kultur", rang: 2, gehfolge: 13, dauer: 30, zugang: "betreten",
    zeiten: { de: "Fr bis So 14 bis 16 Uhr", en: "Fri to Sun 2 to 4 pm" }, geschlossen: [1, 2, 3, 4],
    einzeiler: { de: "Modell des Ersten Goetheanum, das in der Silvesternacht 1922 abbrannte. Schreinerei Südsaal links, Eintritt CHF 5.",
                 en: "Model of the First Goetheanum, which burned on New Year's Eve 1922. Schreinerei south hall, left; admission CHF 5." } },
  { id: "o40", thema: "kultur", rang: 3, gehfolge: 14, dauer: 15, zugang: "betreten",
    zeiten: { de: "Fr 14 bis 15 Uhr", en: "Fri 2 to 3 pm" }, geschlossen: [0, 1, 2, 3, 4, 6],
    einzeiler: { de: "Schreinerei, rechter Eingang.", en: "Schreinerei, right-hand entrance." } },
  { id: "o6", thema: "kultur", rang: 4, gehfolge: 9, dauer: 20, zugang: "betreten" },
  { id: "o7", thema: "kultur", rang: 5, gehfolge: 10, dauer: 20, zugang: "betreten",
    zeiten: { de: "Di, Do und Fr 14 bis 18 Uhr", en: "Tue, Thu and Fri 2 pm to 6 pm" }, geschlossen: [0, 1, 3, 6] },
  { id: "o42", thema: "kultur", rang: 6, gehfolge: 15, dauer: 10, zugang: "betreten",
    zeiten: { de: "Fr 14.30 bis 15.30 Uhr", en: "Fri 2.30 to 3.30 pm" }, geschlossen: [0, 1, 2, 3, 4, 6],
    einzeiler: { de: "Blaues Holzhaus im Südwesten der Schreinerei.", en: "Blue wooden house south-west of the Schreinerei." } },
  { id: "o43", thema: "kultur", rang: 7, gehfolge: 24, dauer: 10, zugang: "betreten",
    zeiten: { de: "Fr 15.30 bis 16.30 Uhr", en: "Fri 3.30 to 4.30 pm" }, geschlossen: [0, 1, 2, 3, 4, 6],
    einzeiler: { de: "Unteres Eurythmiehaus, Rüttiweg 30, 1. Etage.", en: "Lower Eurythmiehaus, Rüttiweg 30, first floor." } },

  // Essen und Verweilen
  // Grabstein: das Café war kurz ein eigener Ort (o8), liegt aber in der
  // Wandelhalle (v12). Die Zeile bleibt, damit das Link-Bit nicht rutscht.
  { id: "o8", thema: "aus", rang: 99, gehfolge: 0, dauer: 0 },
  { id: "o45", thema: "essen", rang: 2, gehfolge: 27, dauer: 60, zugang: "betreten", kinder: true,
    zeiten: { de: "Laden Mo bis Fr 8 bis 18.30, Sa und So 8 bis 16 Uhr; Restaurant zurzeit geschlossen", en: "Shop Mon to Fri 8 am to 6.30 pm, Sat and Sun 8 am to 4 pm; restaurant currently closed" } },
  { id: "f-vital", thema: "essen", rang: 3, gehfolge: 28, dauer: 15, zugang: "betreten",
    zeiten: { de: "Mo bis Fr 8 bis 18.30, Sa und So 8 bis 16 Uhr", en: "Mon to Fri 8 am to 6.30 pm, Sat and Sun 8 am to 4 pm" } },
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
    zeiten: { de: "Sa 15 bis 16 Uhr", en: "Sat 3 to 4 pm" }, geschlossen: [0, 1, 2, 3, 4, 5],
    einzeiler: { de: "Hügelweg 64 A, in der Kurve oberhalb des Parkplatzes.", en: "Hügelweg 64 A, on the bend above the car park." } }
];
