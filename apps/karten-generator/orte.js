// GENERIERT von tools/karten/extract-marker-positionen.py —
// nicht von Hand ändern. Quelle: LT25-Reader-Kartenseiten
// (grafik.goetheanum.ch/kartierung), Masse in mm auf dem A4-quer-Blatt.
const KARTE = {
  "blatt": {
    "breite": 297.0,
    "hoehe": 210.0
  },
  "falz": 148.5,
  "gelaende": {
    "x": 30.709,
    "y": -35.229,
    "breite": 499.935,
    "hoehe": 323.901
  }
};

const KATEGORIEN = [
  {
    "id": "eingaenge",
    "name": {
      "de": "Eingänge & Empfang",
      "en": "Entrances & Reception"
    }
  },
  {
    "id": "verkehr",
    "name": {
      "de": "Verkehr & Anreise",
      "en": "Transport & Arrival"
    }
  },
  {
    "id": "treppen",
    "name": {
      "de": "Treppenhäuser",
      "en": "Staircases"
    }
  },
  {
    "id": "saele",
    "name": {
      "de": "Säle & Veranstaltungsräume",
      "en": "Halls & Event Rooms"
    }
  },
  {
    "id": "ausstellung",
    "name": {
      "de": "Ausstellung & Orientierung",
      "en": "Exhibition & Orientation"
    }
  },
  {
    "id": "haeuser",
    "name": {
      "de": "Häuser auf dem Campus",
      "en": "Houses on Campus"
    }
  },
  {
    "id": "sektionen",
    "name": {
      "de": "Sektionen",
      "en": "Sections"
    }
  },
  {
    "id": "gaerten",
    "name": {
      "de": "Gärten & Orte im Grünen",
      "en": "Gardens & Green Spaces"
    }
  }
];

const ORTE = [
  {
    "id": "o1",
    "marker": "1",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "gold",
    "label": {
      "de": "Haupteingang",
      "en": "Main Entrance"
    },
    "positionen": [
      [
        198.59,
        154.7
      ]
    ]
  },
  {
    "id": "o2",
    "marker": "2",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "gold",
    "label": {
      "de": "Südeingang",
      "en": "South Entrance"
    },
    "positionen": [
      [
        222.49,
        125.9
      ]
    ]
  },
  {
    "id": "o3",
    "marker": "3",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "gold",
    "label": {
      "de": "Empfang",
      "en": "Reception"
    },
    "positionen": [
      [
        204.56,
        148.35
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "o4",
    "marker": "4",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "gold",
    "label": {
      "de": "Infotisch",
      "en": "Info Desk"
    },
    "positionen": [
      [
        192.86,
        148.05
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "b-zugang",
    "marker": "BF",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "gold",
    "label": {
      "de": "Barrierefreier Zugang",
      "en": "Barrier-free access"
    },
    "positionen": [
      [
        222.5,
        130.6
      ]
    ],
    "symbol": "wc-rollstuhl"
  },
  {
    "id": "wc-goetheanum",
    "marker": "WC",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "blau",
    "label": {
      "de": "WC Goetheanum",
      "en": "WC Goetheanum"
    },
    "positionen": [
      [
        188.5,
        150.8
      ]
    ],
    "symbol": "wc-gruppe"
  },
  {
    "id": "wc-schreinerei",
    "marker": "WC",
    "art": "orientierung",
    "kategorie": "eingaenge",
    "farbe": "blau",
    "label": {
      "de": "WC Schreinerei",
      "en": "WC Schreinerei"
    },
    "positionen": [
      [
        224.5,
        83.5
      ]
    ],
    "symbol": "wc-gruppe"
  },
  {
    "id": "f46",
    "marker": "46",
    "art": "orientierung",
    "kategorie": "verkehr",
    "farbe": "blau",
    "label": {
      "de": "Bahnhof",
      "en": "Train Station"
    },
    "positionen": [
      [
        103.78,
        197.44
      ]
    ],
    "pfeil": 105
  },
  {
    "id": "f-p",
    "marker": "P",
    "art": "orientierung",
    "kategorie": "verkehr",
    "farbe": "blau",
    "label": {
      "de": "Parkplatz",
      "en": "Parking"
    },
    "positionen": [
      [
        159.07,
        73.4
      ]
    ]
  },
  {
    "id": "t-main",
    "marker": "M",
    "art": "treppe",
    "kategorie": "treppen",
    "farbe": "rot",
    "label": {
      "de": "Haupttreppe",
      "en": "Main Stairs"
    },
    "positionen": [],
    "notizen": [
      {
        "de": "Galerie · 1. Etage",
        "en": "Gallery · 1st Floor"
      },
      {
        "de": "Grosser Saal · 2. Etage",
        "en": "Grosser Saal · 2nd Floor"
      }
    ],
    "badges": [
      {
        "x": 198.6,
        "y": 145.99,
        "form": "treppe"
      }
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "t-nord",
    "marker": "N",
    "art": "treppe",
    "kategorie": "treppen",
    "farbe": "rot",
    "label": {
      "de": "Nordtreppe",
      "en": "North Stairs"
    },
    "positionen": [],
    "notizen": [
      {
        "de": "Nord-Lift",
        "en": "North Lift",
        "badge": "lift"
      },
      {
        "de": "Galerie · 1. Etage",
        "en": "Gallery · 1st Floor"
      },
      {
        "de": "Grosser Saal · 2. Etage",
        "en": "Grosser Saal · 2nd Floor"
      },
      {
        "de": "Nordsaal · 5. Etage",
        "en": "Nordsaal · 5th Floor"
      },
      {
        "de": "Nordatelier · 6. Etage",
        "en": "Nordatelier · 6th Floor"
      }
    ],
    "badges": [
      {
        "x": 184.28,
        "y": 125.92,
        "form": "treppe"
      },
      {
        "x": 188.58,
        "y": 125.68,
        "form": "lift"
      }
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "t-sued",
    "marker": "S",
    "art": "treppe",
    "kategorie": "treppen",
    "farbe": "rot",
    "label": {
      "de": "Südtreppe",
      "en": "South Stairs"
    },
    "positionen": [],
    "notizen": [
      {
        "de": "Süd-Lift",
        "en": "South Lift",
        "badge": "lift"
      },
      {
        "de": "Konferenzraum · 1. Etage",
        "en": "Konferenzraum · 1st Floor"
      },
      {
        "de": "Galerie · 1. Etage",
        "en": "Gallery · 1st Floor"
      },
      {
        "de": "Grosser Saal · 2. Etage",
        "en": "Grosser Saal · 2nd Floor"
      },
      {
        "de": "Seminarraum · 4. Etage",
        "en": "Seminarraum · 4th Floor"
      },
      {
        "de": "Holzplastik · 5. Etage",
        "en": "Wooden Sculpture · 5th Floor"
      },
      {
        "de": "Südatelier · 6. Etage",
        "en": "Südatelier · 6th Floor"
      }
    ],
    "badges": [
      {
        "x": 210.79,
        "y": 125.8,
        "form": "treppe"
      },
      {
        "x": 206.34,
        "y": 125.44,
        "form": "lift"
      }
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "v10",
    "marker": "10",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Grundsteinsaal",
      "en": "Grundsteinsaal"
    },
    "positionen": [
      [
        198.59,
        120.02
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "v11",
    "marker": "11",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Terrassensaal",
      "en": "Terrassensaal"
    },
    "positionen": [
      [
        182.35,
        135.43
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "v12",
    "marker": "12",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Wandelhalle",
      "en": "Wandelhalle"
    },
    "positionen": [
      [
        213.98,
        135.43
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "v13",
    "marker": "13",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Im Hof",
      "en": "Im Hof"
    },
    "positionen": [
      [
        204.03,
        135.43
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "v14",
    "marker": "14",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Ostsäle 1-4",
      "en": "Ostsäle 1-4"
    },
    "positionen": [
      [
        213.98,
        120.02
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "v15",
    "marker": "15",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Foyer",
      "en": "Foyer"
    },
    "positionen": [
      [
        198.47,
        135.39
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "v20",
    "marker": "20",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Schreinereisaal",
      "en": "Schreinereisaal"
    },
    "positionen": [
      [
        220.07,
        87.8
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "v21",
    "marker": "21",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Plastizierraum",
      "en": "Plastizierraum"
    },
    "positionen": [
      [
        210.37,
        90.4
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "v22",
    "marker": "22",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Gartenatelier",
      "en": "Gartenatelier"
    },
    "positionen": [
      [
        216.22,
        75.95
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "v23",
    "marker": "23",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Backofen",
      "en": "Backofen"
    },
    "positionen": [
      [
        235.52,
        93.56
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "v24",
    "marker": "24",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "Schreinerei Südsaal",
      "en": "Schreinerei Südsaal"
    },
    "positionen": [
      [
        242.46,
        100.92
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "v30",
    "marker": "30",
    "art": "ort",
    "kategorie": "saele",
    "farbe": "rot",
    "label": {
      "de": "English Studies",
      "en": "English Studies"
    },
    "positionen": [
      [
        157.37,
        167.2
      ]
    ],
    "gebaeude": "campusbau-6"
  },
  {
    "id": "o5",
    "marker": "5",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Buchhandlung",
      "en": "Bookshop"
    },
    "positionen": [
      [
        189.16,
        142.11
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "o6",
    "marker": "6",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Nordgalerie",
      "en": "North Gallery"
    },
    "positionen": [
      [
        191.33,
        132.57
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "o7",
    "marker": "7",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Bibliothek",
      "en": "Library"
    },
    "positionen": [
      [
        193.21,
        107.6
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "o40",
    "marker": "40",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Rudolf-Steiner-Atelier",
      "en": "Rudolf Steiner Atelier"
    },
    "positionen": [
      [
        234.52,
        98.26
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "o41",
    "marker": "41",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Baugeschichte + Modell Erstes Goetheanum",
      "en": "Building History + 1st Goetheanum Model"
    },
    "positionen": [
      [
        241.27,
        105.37
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "o42",
    "marker": "42",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Hochatelier",
      "en": "Hochatelier"
    },
    "positionen": [
      [
        229.67,
        109.37
      ]
    ],
    "gebaeude": "campusbau-19"
  },
  {
    "id": "o43",
    "marker": "43",
    "art": "orientierung",
    "kategorie": "ausstellung",
    "farbe": "blau",
    "label": {
      "de": "Edith-Maryon-Zimmer",
      "en": "Edith Maryon Flat"
    },
    "positionen": [
      [
        271.58,
        100.48
      ]
    ]
  },
  {
    "id": "v31",
    "marker": "31",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Rudolf Steiner Halde",
      "en": "Rudolf Steiner Halde"
    },
    "positionen": [
      [
        145.47,
        170.38
      ]
    ],
    "teile": [
      {
        "de": "Rudolf Steiner Halde",
        "en": "Rudolf Steiner Halde"
      },
      {
        "de": "Puppentheater Felicia",
        "en": "Puppet Theatre Felicia"
      }
    ],
    "gebaeudeTeile": [
      "campusbau-41",
      "campusbau-6"
    ],
    "gebaeude": "campusbau-41"
  },
  {
    "id": "v32",
    "marker": "32",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Glashaus",
      "en": "Glashaus"
    },
    "positionen": [
      [
        129.03,
        118.26
      ]
    ],
    "gebaeude": "campusbau-46"
  },
  {
    "id": "v33",
    "marker": "33",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Studierendenwohnheim",
      "en": "Students Residence"
    },
    "positionen": [
      [
        174.94,
        4.56
      ]
    ],
    "gebaeude": "campusbau-10"
  },
  {
    "id": "v34",
    "marker": "34",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Haus Schuurman",
      "en": "Haus Schuurman"
    },
    "positionen": [
      [
        222.72,
        25.14
      ]
    ],
    "gebaeude": "campusbau-44"
  },
  {
    "id": "v35",
    "marker": "35",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Färberei",
      "en": "Färberei"
    },
    "positionen": [
      [
        248.22,
        33.36
      ]
    ],
    "gebaeude": "campusbau-16"
  },
  {
    "id": "v36",
    "marker": "36",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Holzhaus",
      "en": "Holzhaus"
    },
    "positionen": [
      [
        278.18,
        39.14
      ]
    ]
  },
  {
    "id": "v37",
    "marker": "37",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "AfaP",
      "en": "AfaP"
    },
    "positionen": [
      [
        285.52,
        130.6
      ]
    ],
    "pfeil": "rechts"
  },
  {
    "id": "v38",
    "marker": "38",
    "art": "ort",
    "kategorie": "haeuser",
    "farbe": "rot",
    "label": {
      "de": "Trigon",
      "en": "Trigon"
    },
    "positionen": [
      [
        285.52,
        79.69
      ]
    ],
    "pfeil": "rechts"
  },
  {
    "id": "o44",
    "marker": "44",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Haus Duldeck · Rudolf-Steiner-Archiv",
      "en": "Haus Duldeck · Rudolf Steiner Archive"
    },
    "positionen": [
      [
        209.09,
        195.49
      ]
    ]
  },
  {
    "id": "o45",
    "marker": "45",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Speisehaus · Laden",
      "en": "Restaurant · Shop"
    },
    "positionen": [
      [
        280.19,
        199.65
      ]
    ],
    "pfeil": "unten-rechts",
    "teile": [
      {
        "de": "Speisehaus · Laden",
        "en": "Restaurant · Shop"
      },
      {
        "de": "Schweizer Landesgesellschaft",
        "en": "Schweizer Landesgesellschaft"
      },
      {
        "de": "Bushaltestelle",
        "en": "Bus Stop"
      }
    ]
  },
  {
    "id": "h-kepler",
    "marker": "50",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Kepler-Sternwarte",
      "en": "Kepler Observatory"
    },
    "positionen": [
      [
        255.47,
        36.32
      ]
    ],
    "gebaeude": "campusbau-15"
  },
  {
    "id": "h-finckh",
    "marker": "51",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Helene Finckh Häuschen",
      "en": "Helene Finckh Häuschen"
    },
    "positionen": [
      [
        190.85,
        67.22
      ]
    ]
  },
  {
    "id": "h-jaager",
    "marker": "52",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Haus de Jaager",
      "en": "Haus de Jaager"
    },
    "positionen": [
      [
        266.08,
        134.87
      ]
    ]
  },
  {
    "id": "h-eurythmie",
    "marker": "53",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Eurythmiehaus",
      "en": "Eurythmiehaus"
    },
    "positionen": [
      [
        268.5,
        97.0
      ]
    ]
  },
  {
    "id": "h-jugendhaus",
    "marker": "54",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Jugendsektionshaus",
      "en": "House of the Youth Section"
    },
    "positionen": [
      [
        292.0,
        192.5
      ]
    ]
  },
  {
    "id": "h-friedwart",
    "marker": "55",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Gästehaus Friedwart",
      "en": "Guesthouse Friedwart"
    },
    "positionen": [
      [
        118.0,
        202.5
      ]
    ],
    "pfeil": "unten-links"
  },
  {
    "id": "h-kristall",
    "marker": "56",
    "art": "orientierung",
    "kategorie": "haeuser",
    "farbe": "blau",
    "label": {
      "de": "Kristallisationslabor",
      "en": "Kristallisationslabor"
    },
    "positionen": [
      [
        168.0,
        60.3
      ]
    ],
    "gebaeude": "campusbau-9"
  },
  {
    "id": "s-allgemein",
    "marker": "a",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Allgemeine Anthroposophische Sektion",
      "en": "General Anthroposophical Section"
    },
    "positionen": [
      [
        179.5,
        131.5
      ]
    ],
    "gebaeude": "campusbau-52"
  },
  {
    "id": "s-natur",
    "marker": "b",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Naturwissenschaftliche Sektion",
      "en": "Natural Science Section"
    },
    "positionen": [
      [
        125.88,
        113.88
      ]
    ],
    "gebaeude": "campusbau-46"
  },
  {
    "id": "s-paedagogik",
    "marker": "c",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Pädagogische Sektion",
      "en": "Pedagogical Section"
    },
    "positionen": [
      [
        189.14,
        131.87
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "s-schoene",
    "marker": "d",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Schöne Wissenschaften",
      "en": "Section for the Literary Arts and Humanities"
    },
    "positionen": [
      [
        149.93,
        170.31
      ]
    ],
    "gebaeude": "campusbau-41"
  },
  {
    "id": "s-jugend",
    "marker": "e",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Jugendsektion",
      "en": "Youth Section"
    },
    "positionen": [
      [
        192.92,
        109.33
      ]
    ]
  },
  {
    "id": "s-medizin",
    "marker": "f",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Medizinische Sektion",
      "en": "Medical Section"
    },
    "positionen": [
      [
        270.95,
        125.81
      ]
    ]
  },
  {
    "id": "s-landwirtschaft",
    "marker": "g",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Landwirtschaft",
      "en": "Section for Agriculture"
    },
    "positionen": [
      [
        124.94,
        121.64
      ]
    ],
    "gebaeude": "campusbau-46"
  },
  {
    "id": "s-bildende",
    "marker": "h",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Bildende Künste",
      "en": "Visual Art Section"
    },
    "positionen": [
      [
        109.98,
        151.18
      ]
    ]
  },
  {
    "id": "s-redende",
    "marker": "i",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Redende und Musizierende Künste",
      "en": "Section for the Performing Arts"
    },
    "positionen": [
      [
        193.3,
        136.41
      ]
    ],
    "gebaeude": "campusbau-53"
  },
  {
    "id": "s-sozial",
    "marker": "j",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Sozialwissenschaften",
      "en": "Section for Social Sciences"
    },
    "positionen": [
      [
        167.74,
        61.04
      ]
    ],
    "gebaeude": "campusbau-9"
  },
  {
    "id": "s-mathematik",
    "marker": "k",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Mathematisch-Astronomische Sektion",
      "en": "Section for Mathematics and Astronomy"
    },
    "positionen": [
      [
        251.82,
        32.06
      ]
    ],
    "gebaeude": "campusbau-15"
  },
  {
    "id": "s-heilpaedagogik",
    "marker": "m",
    "art": "orientierung",
    "kategorie": "sektionen",
    "farbe": "grau",
    "label": {
      "de": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
      "en": "Section for Inclusive Social Development"
    },
    "positionen": [
      [
        291.97,
        133.19
      ]
    ],
    "pfeil": "rechts"
  },
  {
    "id": "g-felsli",
    "marker": "10",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Felsli",
      "en": "Felsli"
    },
    "positionen": [
      [
        232.12,
        193.41
      ]
    ]
  },
  {
    "id": "g-wasserspiel",
    "marker": "11",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Wasserspiel",
      "en": "Flowforms"
    },
    "positionen": [
      [
        107.9,
        129.6
      ]
    ]
  },
  {
    "id": "g-gedenkhain",
    "marker": "12",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Gedenkhain",
      "en": "Memorial Grove"
    },
    "positionen": [
      [
        165.65,
        178.45
      ]
    ]
  },
  {
    "id": "g-heilkraeuter",
    "marker": "13",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Heilkräutergarten",
      "en": "Medicinal Plant Garden"
    },
    "positionen": [
      [
        247.2,
        94.2
      ]
    ]
  },
  {
    "id": "g-faerberpflanzen",
    "marker": "14",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Färberpflanzengarten",
      "en": "Plant Dye Garden"
    },
    "positionen": [
      [
        243.87,
        29.79
      ]
    ]
  },
  {
    "id": "g-schnittblumen",
    "marker": "15",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Schnittblumengarten",
      "en": "Cut Flower Garden"
    },
    "positionen": [
      [
        229.09,
        25.06
      ]
    ]
  },
  {
    "id": "g-duftkraeuter",
    "marker": "16",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Duftkräutergarten",
      "en": "Fragrant Herb Garden"
    },
    "positionen": [
      [
        239.3,
        39.0
      ]
    ]
  },
  {
    "id": "g-bienen",
    "marker": "17",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Bienenskulptur",
      "en": "Bee Sculpture"
    },
    "positionen": [
      [
        264.89,
        41.53
      ]
    ]
  },
  {
    "id": "g-praeparate",
    "marker": "18",
    "art": "orientierung",
    "kategorie": "gaerten",
    "farbe": "gruen",
    "label": {
      "de": "Präparatepavillon",
      "en": "Präparatepavillon"
    },
    "positionen": [
      [
        219.62,
        62.18
      ]
    ]
  }
];
