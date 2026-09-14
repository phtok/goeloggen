"use strict";

/* Gäste-Zeile je Ort (Konzept § 10, docs/specs/campusplan-besucher-konzept.md).
   Ergänzt den generierten Katalog apps/karten-generator/orte.js — der bleibt
   unberührt. Erster Entwurf vom 14. September 2026: Rang, Dauer, Zugang und
   Gehfolge sind Schätzungen zur Abnahme; Einzeiler mit Quelle im Konzept § 11.

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
    kurz: { de: "Café, Speisehaus, Vitalshop", en: "Café, Speisehaus, Vitalshop" } }
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

/* Orte, die im Katalog fehlen. Lage in Blatt-mm; lageGeschaetzt = noch nicht
   am Gelände geprüft (Konzept § 11, Nebenbefund). */
const NEUE_ORTE = [
  { id: "n-saal", label: { de: "Grosser Saal", en: "Great Hall" },
    positionen: [[198.6, 127.5]], gebaeude: "campusbau-53" },
  { id: "n-mensch", label: { de: "Menschheitsrepräsentant", en: "Representative of Humanity" },
    positionen: [[210.8, 121.5]], gebaeude: "campusbau-53" },
  { id: "n-treppen", label: { de: "Treppenhäuser", en: "Staircases" },
    positionen: [[184.3, 125.9]], gebaeude: "campusbau-53" },
  { id: "n-cafe", label: { de: "Café", en: "Café" },
    positionen: [[207.0, 141.0]], gebaeude: "campusbau-52", lageGeschaetzt: true },
  { id: "n-schreinerei", label: { de: "Schreinerei", en: "Schreinerei (Carpentry)" },
    positionen: [[228.0, 93.0]], gebaeude: "campusbau-19" },
  { id: "n-heizhaus", label: { de: "Heizhaus", en: "Heizhaus (Boiler House)" },
    positionen: [[246.6, 77.0]], gebaeude: "campusbau-23", lageGeschaetzt: true },
  { id: "n-trafo", label: { de: "Transformatorenhaus", en: "Transformer House" },
    positionen: [[291.6, 143.5]], gebaeude: "campusbau-24", lageGeschaetzt: true },
  { id: "n-verlag", label: { de: "Verlagshaus", en: "Publishing House" },
    positionen: [[137.4, 94.4]], gebaeude: "campusbau-43", lageGeschaetzt: true }
];

/* thema: basis (immer dabei, nummeriert) · anreise (immer dabei, unnummeriert)
   · eines der fünf Themen. rang 1 = Highlight. dauer in Minuten.
   barrierefrei:false = fällt bei ‹Barrierefrei› weg. kinder:true = rückt bei
   ‹Mit Kindern› nach vorn. gehfolge = Reihenfolge des Rundwegs. */
const GAESTE = [
  { id: "o1", thema: "basis", gehfolge: 1, dauer: 0, zugang: "betreten" },
  { id: "o3", thema: "basis", gehfolge: 2, dauer: 5, zugang: "betreten" },
  { id: "wc-goetheanum", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f46", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-bus", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "f-p", thema: "anreise", gehfolge: 0, dauer: 0 },
  { id: "b-zugang", thema: "anreise", gehfolge: 0, dauer: 0, nurBarrierefrei: true },

  // Der Bau
  { id: "n-saal", thema: "bau", rang: 1, gehfolge: 6, dauer: 30, zugang: "betreten",
    einzeiler: { de: "Knapp tausend Plätze unter einer Deckenmalerei in Pflanzenfarben, farbige Glasfenster von 1945.",
                 en: "Nearly a thousand seats under a ceiling painted in plant colours, stained glass from 1945." } },
  { id: "n-mensch", thema: "bau", rang: 2, gehfolge: 8, dauer: 20, zugang: "anfrage",
    einzeiler: { de: "Über acht Meter Holz: die Christusfigur zwischen Luzifer und Ahriman, von Rudolf Steiner und Edith Maryon ab 1914.",
                 en: "Over eight metres of wood: the Christ figure between Lucifer and Ahriman, by Rudolf Steiner and Edith Maryon from 1914." } },
  { id: "v12", thema: "bau", rang: 3, gehfolge: 5, dauer: 10, zugang: "betreten",
    einzeiler: { de: "Das Foyer unter dem Grossen Saal.", en: "The foyer beneath the Great Hall." } },
  { id: "n-treppen", thema: "bau", rang: 4, gehfolge: 7, dauer: 10, zugang: "betreten",
    einzeiler: { de: "Die geschwungenen Betontreppen im Norden und Süden des Baus.",
                 en: "The sweeping concrete staircases in the north and south of the building." } },

  // Architektursammlung
  { id: "n-heizhaus", thema: "sammlung", rang: 1, gehfolge: 17, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Der erste Betonbau des Hügels: ein Heizwerk mit sphinxhafter Form, bis heute in Betrieb (1915).",
                 en: "The hill's first concrete building: a boiler house of sphinx-like form, still in use (1915)." } },
  { id: "v32", thema: "sammlung", rang: 2, gehfolge: 33, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Zwei Kuppeln unter Schiefer, gebaut zum Schleifen der Glasfenster des Ersten Goetheanum (1914).",
                 en: "Two domes under slate, built for grinding the stained glass of the First Goetheanum (1914)." } },
  { id: "n-schreinerei", thema: "sammlung", rang: 3, gehfolge: 12, dauer: 10, zugang: "betreten",
    einzeiler: { de: "Die Bauhütte des Ersten Goetheanum, in der Steiner arbeitete und 1925 starb (1913).",
                 en: "The building lodge of the First Goetheanum, where Steiner worked and died in 1925 (1913)." } },
  { id: "o44", thema: "sammlung", rang: 4, gehfolge: 29, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-45"],
    einzeiler: { de: "Eisenbeton-Wohnhaus für den Stifter des Grundstücks, seit 2002 Rudolf-Steiner-Archiv (1915).",
                 en: "Reinforced-concrete home of the land's donor, the Rudolf Steiner Archive since 2002 (1915)." } },
  { id: "v31", thema: "sammlung", rang: 5, gehfolge: 32, dauer: 15, zugang: "betreten", kinder: true,
    einzeiler: { de: "Der Betonanbau von 1923 war der Versuchsbau für das zweite Goetheanum, heute Tagungshaus.",
                 en: "The 1923 concrete extension was the trial build for the second Goetheanum, now a conference house." } },
  { id: "n-trafo", thema: "sammlung", rang: 6, gehfolge: 26, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Steiners Trafostation mit kubischen Auskragungen, bis heute am Netz (1921).",
                 en: "Steiner's transformer station with cubic projections, still on the grid (1921)." } },
  { id: "h-jaager", thema: "sammlung", rang: 7, gehfolge: 25, dauer: 10, zugang: "aussen", gebaeude: ["campusbau-50"],
    einzeiler: { de: "Wohn- und Atelierhaus für einen Bildhauer, kantig und doch mit Anklang an die Doppelkuppel (1921).",
                 en: "Home and studio for a sculptor, angular yet echoing the double dome (1921)." } },
  { id: "h-eurythmie", thema: "sammlung", rang: 8, gehfolge: 23, dauer: 10, zugang: "aussen",
    gebaeude: ["campusbau-47", "campusbau-48", "campusbau-49"],
    einzeiler: { de: "Drei Wohnhäuser nach Entwurf von Edith Maryon (1920).",
                 en: "Three houses designed by Edith Maryon (1920)." } },
  { id: "n-verlag", thema: "sammlung", rang: 9, gehfolge: 34, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Der letzte von Steiner entworfene Bau der Kolonie.",
                 en: "The last building of the colony designed by Steiner." } },

  // Gartenpark
  { id: "g-felsli", thema: "garten", rang: 1, gehfolge: 30, dauer: 15, zugang: "betreten", barrierefrei: false,
    einzeiler: { de: "Der Felsvorsprung am Westende des Hügels: der Aussichtspunkt.",
                 en: "The rock spur at the western end of the hill: the lookout." } },
  { id: "g-wasserspiel", thema: "garten", rang: 2, gehfolge: 35, dauer: 10, zugang: "betreten", kinder: true },
  { id: "g-gedenkhain", thema: "garten", rang: 3, gehfolge: 31, dauer: 15, zugang: "betreten",
    einzeiler: { de: "Urnenhain, in dem Rudolf Steiner, Marie Steiner-von Sivers und Christian Morgenstern ruhen.",
                 en: "Urn grove where Rudolf Steiner, Marie Steiner-von Sivers and Christian Morgenstern rest." } },
  { id: "g-heilkraeuter", thema: "garten", rang: 4, gehfolge: 11, dauer: 10, zugang: "betreten" },
  { id: "g-duftkraeuter", thema: "garten", rang: 5, gehfolge: 19, dauer: 10, zugang: "betreten" },
  { id: "g-faerberpflanzen", thema: "garten", rang: 6, gehfolge: 20, dauer: 10, zugang: "betreten" },
  { id: "g-schnittblumen", thema: "garten", rang: 7, gehfolge: 21, dauer: 10, zugang: "betreten" },
  { id: "g-bienen", thema: "garten", rang: 8, gehfolge: 22, dauer: 10, zugang: "betreten", kinder: true },
  { id: "g-praeparate", thema: "garten", rang: 9, gehfolge: 18, dauer: 10, zugang: "aussen",
    einzeiler: { de: "Hier entstehen die biodynamischen Präparate der Gärtnerei.",
                 en: "Where the garden's biodynamic preparations are made." } },

  // Bücher, Kunst, Ausstellungen
  { id: "o5", thema: "kultur", rang: 1, gehfolge: 4, dauer: 20, zugang: "betreten" },
  { id: "o41", thema: "kultur", rang: 2, gehfolge: 13, dauer: 30, zugang: "betreten",
    einzeiler: { de: "Das Modell des 1922 abgebrannten Holzbaus, dazu seine Geschichte.",
                 en: "The model of the wooden building that burned in 1922, and its story." } },
  { id: "o40", thema: "kultur", rang: 3, gehfolge: 14, dauer: 15, zugang: "betreten",
    einzeiler: { de: "Steiners Arbeitsraum in der Schreinerei.", en: "Steiner's workroom in the Schreinerei." } },
  { id: "o6", thema: "kultur", rang: 4, gehfolge: 9, dauer: 20, zugang: "betreten",
    einzeiler: { de: "Ausstellungsraum im Goetheanum.", en: "Exhibition space in the Goetheanum." } },
  { id: "o7", thema: "kultur", rang: 5, gehfolge: 10, dauer: 20, zugang: "betreten" },
  { id: "o42", thema: "kultur", rang: 6, gehfolge: 15, dauer: 10, zugang: "anfrage",
    einzeiler: { de: "Der hohe Raum, in dem die Holzplastik entstand.", en: "The tall room where the wood sculpture was made." } },
  { id: "o43", thema: "kultur", rang: 7, gehfolge: 24, dauer: 10, zugang: "anfrage",
    einzeiler: { de: "Erinnerungsraum an die Bildhauerin, Mitschöpferin der Holzplastik.",
                 en: "Memorial room for the sculptor, co-creator of the wood sculpture." } },

  // Essen und Verweilen
  { id: "n-cafe", thema: "essen", rang: 1, gehfolge: 3, dauer: 30, zugang: "betreten" },
  { id: "o45", thema: "essen", rang: 2, gehfolge: 27, dauer: 60, zugang: "betreten", kinder: true },
  { id: "f-vital", thema: "essen", rang: 3, gehfolge: 28, dauer: 15, zugang: "betreten" },
  { id: "v23", thema: "essen", rang: 4, gehfolge: 16, dauer: 15, zugang: "aussen", kinder: true,
    einzeiler: { de: "Der Holzofen bei der Schreinerei.", en: "The wood-fired oven by the Schreinerei." } }
];
