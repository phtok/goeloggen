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

const ORTE = [
  {
    "id": "o1",
    "marker": "1",
    "art": "orientierung",
    "farbe": "blau",
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
    "farbe": "blau",
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
    "farbe": "blau",
    "label": {
      "de": "Empfang",
      "en": "Reception"
    },
    "positionen": [
      [
        204.56,
        148.35
      ]
    ]
  },
  {
    "id": "o4",
    "marker": "4",
    "art": "orientierung",
    "farbe": "blau",
    "label": {
      "de": "Infotisch",
      "en": "Info Desk"
    },
    "positionen": [
      [
        192.86,
        148.05
      ]
    ]
  },
  {
    "id": "o5",
    "marker": "5",
    "art": "orientierung",
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
    ]
  },
  {
    "id": "o6",
    "marker": "6",
    "art": "orientierung",
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
    ]
  },
  {
    "id": "o7",
    "marker": "7",
    "art": "orientierung",
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
    ]
  },
  {
    "id": "v10",
    "marker": "10",
    "art": "ort",
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
    ]
  },
  {
    "id": "v11",
    "marker": "11",
    "art": "ort",
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
    ]
  },
  {
    "id": "v12",
    "marker": "12",
    "art": "ort",
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
    ]
  },
  {
    "id": "v13",
    "marker": "13",
    "art": "ort",
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
    ]
  },
  {
    "id": "v14",
    "marker": "14",
    "art": "ort",
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
    ]
  },
  {
    "id": "v15",
    "marker": "15",
    "art": "ort",
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
    ]
  },
  {
    "id": "t-main",
    "marker": "M",
    "art": "treppe",
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
    ]
  },
  {
    "id": "t-nord",
    "marker": "N",
    "art": "treppe",
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
    ]
  },
  {
    "id": "t-sued",
    "marker": "S",
    "art": "treppe",
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
    ]
  },
  {
    "id": "v20",
    "marker": "20",
    "art": "ort",
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
    ]
  },
  {
    "id": "v21",
    "marker": "21",
    "art": "ort",
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
    ]
  },
  {
    "id": "v22",
    "marker": "22",
    "art": "ort",
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
    ]
  },
  {
    "id": "v23",
    "marker": "23",
    "art": "ort",
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
    ]
  },
  {
    "id": "v24",
    "marker": "24",
    "art": "ort",
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
    ]
  },
  {
    "id": "v30",
    "marker": "30",
    "art": "ort",
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
    ]
  },
  {
    "id": "v31",
    "marker": "31",
    "art": "ort",
    "farbe": "rot",
    "label": {
      "de": "Halde",
      "en": "Halde"
    },
    "positionen": [
      [
        145.47,
        170.38
      ]
    ]
  },
  {
    "id": "v32",
    "marker": "32",
    "art": "ort",
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
    ]
  },
  {
    "id": "v33",
    "marker": "33",
    "art": "ort",
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
    ]
  },
  {
    "id": "v34",
    "marker": "34",
    "art": "ort",
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
    ]
  },
  {
    "id": "v35",
    "marker": "35",
    "art": "ort",
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
    ]
  },
  {
    "id": "v36",
    "marker": "36",
    "art": "ort",
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
    "id": "o40",
    "marker": "40",
    "art": "orientierung",
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
    ]
  },
  {
    "id": "o41",
    "marker": "41",
    "art": "orientierung",
    "farbe": "blau",
    "label": {
      "de": "Modell Erstes Goetheanum",
      "en": "1st Goetheanum Model"
    },
    "positionen": [
      [
        241.27,
        105.37
      ]
    ]
  },
  {
    "id": "o42",
    "marker": "42",
    "art": "orientierung",
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
    ]
  },
  {
    "id": "o43",
    "marker": "43",
    "art": "orientierung",
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
    "id": "o44",
    "marker": "44",
    "art": "orientierung",
    "farbe": "blau",
    "label": {
      "de": "Rudolf-Steiner-Archiv",
      "en": "Rudolf Steiner Archive"
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
    "farbe": "blau",
    "label": {
      "de": "Speisehaus",
      "en": "Speisehaus"
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
        "de": "Speisehaus",
        "en": "Speisehaus"
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
    "id": "f46",
    "marker": "46",
    "art": "orientierung",
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
    "pfeil": "unten-links"
  },
  {
    "id": "f-p",
    "marker": "P",
    "art": "orientierung",
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
  }
];
