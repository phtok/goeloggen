/* GENERIERT von tools/sek-modell.py – nicht von Hand ändern. */
window.GOE_SEK_MODELL = {
 "$quelle": "GENERIERT von tools/sek-modell.py – nicht von Hand ändern.",
 "stufen": [
  {
   "id": "hauch",
   "name": "Hauch",
   "traegt": "Lesetext in --ink und die Tinte",
   "faelle": "Chip, Hinweiskasten, markierte Tabellenzeile, aktives Feld, Zeile im Menü",
   "regel": "Tinte darauf ≥ 4.5:1 (1.4.3)"
  },
  {
   "id": "pastell",
   "name": "Pastell",
   "traegt": "Lesetext in --ink, die Marke in Tinte oder Kern",
   "faelle": "Plakat, Folienhintergrund, Wallpaper, Hintergrund einer Sektionsseite, grosse Kachel",
   "regel": "--ink darauf ≥ 7:1 (1.4.6); Tinte darauf ≥ 3:1 als Objekt"
  },
  {
   "id": "leuchten",
   "name": "Leuchten",
   "traegt": "Objekte und grosse weisse Schrift (≥ 24 px) – keinen Lesetext",
   "faelle": "Marke und Logo, Linie und Kante, Punkt im Menü, Diagramm, Wallpaper-Motiv, Plakattitel gross in Weiss, Icon",
   "regel": "auf Papier ≥ 3:1 als Objekt (1.4.11); Weiss darauf ≥ 3:1 nur gross"
  },
  {
   "id": "kern",
   "name": "Kern",
   "traegt": "Weiss, auch klein",
   "faelle": "Kopfband, Titelfeld, Knopf, Auswahl, Kachel mit weisser Schrift",
   "regel": "Weiss darauf ≥ 4.5:1 (1.4.3, B01)"
  },
  {
   "id": "tinte",
   "name": "Tinte",
   "traegt": "sich selbst als Schrift auf Weiss",
   "faelle": "Kicker, Link, Titel in Sektionsfarbe, Zahl, Label, Icon neben Text, Schrift im Chip",
   "regel": "auf Papier ≥ 5.5:1, auf Karte ≥ 5:1, auf Hauch ≥ 4.5:1 (1.4.3)"
  },
  {
   "id": "grund",
   "name": "Grund",
   "traegt": "Weiss, auch klein – als Hintergrund",
   "faelle": "Fusszeile, Hintergrundelement, tiefe Fläche im Dunkelmodus, Schatten der Marke",
   "regel": "Weiss darauf ≥ 5.5:1 (B01)"
  }
 ],
 "sektionen": [
  {
   "key": "aas",
   "name": "Allgemeine Anthroposophische Sektion",
   "kurz": "Allgemeine Anthroposophie",
   "ort": "Purpur",
   "satz": "Das Ganze: Purpur ‹enthält alle andern Farben›.",
   "para": "§§ 793–794",
   "H": 340,
   "winkel": 348.0,
   "heute": "#a24f8a",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#feeef8",
    "pastell": "#ffd7f0",
    "leuchten": "#d275b5",
    "kern": "#ab448e",
    "tinte": "#ac3d8e",
    "grund": "#8e3f77",
    "hauch_dk": "#32202c",
    "tinte_dk": "#fbb6e3"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.32,
    "tinte_papier": 5.51,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.93,
    "weiss_grund": 6.71,
    "ink_pastell": 11.62,
    "tinte_pastell": 4.26,
    "tinte_dk_papier": 10.84,
    "tinte_dk_hauch": 9.36
   }
  },
  {
   "key": "sbk",
   "name": "Sektion für Bildende Künste",
   "kurz": "Bildende Künste",
   "ort": "Purpur, zur warmen Seite",
   "satz": "Das Schöne: ‹Huld und Anmut›.",
   "para": "§ 796",
   "H": 358,
   "winkel": 10.7,
   "heute": "#d072a0",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#ffeef3",
    "pastell": "#ffd9e4",
    "leuchten": "#de729a",
    "kern": "#be3f75",
    "tinte": "#b7386f",
    "grund": "#9e3c64",
    "hauch_dk": "#341f26",
    "tinte_dk": "#ffbfd3"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 5.05,
    "tinte_papier": 5.51,
    "tinte_karte": 5.2,
    "tinte_hauch": 4.93,
    "weiss_grund": 6.39,
    "ink_pastell": 11.67,
    "tinte_pastell": 4.28,
    "tinte_dk_papier": 11.47,
    "tinte_dk_hauch": 9.96
   }
  },
  {
   "key": "szw",
   "name": "Sektion für Sozialwissenschaften",
   "kurz": "Sozialwissenschaften",
   "ort": "Gelbrot",
   "satz": "Die Tat: ‹die aktive Seite in ihrer höchsten Energie›.",
   "para": "§ 775",
   "H": 18,
   "winkel": 37.3,
   "heute": "#df4164",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#ffefef",
    "pastell": "#ffdada",
    "leuchten": "#f16772",
    "kern": "#cd334a",
    "tinte": "#ca2141",
    "grund": "#aa3543",
    "hauch_dk": "#361f20",
    "tinte_dk": "#ffc2c3"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_kern": 5.04,
    "tinte_papier": 5.52,
    "tinte_karte": 5.2,
    "tinte_hauch": 4.95,
    "weiss_grund": 6.36,
    "ink_pastell": 11.67,
    "tinte_pastell": 4.28,
    "tinte_dk_papier": 11.56,
    "tinte_dk_hauch": 10.01
   }
  },
  {
   "key": "js",
   "name": "Jugendsektion",
   "kurz": "Jugendsektion",
   "ort": "Rotgelb",
   "satz": "Die Glut: ‹Wärme und Wonne›.",
   "para": "§§ 772–773",
   "H": 40,
   "winkel": 64.9,
   "heute": "#ff675d",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#fff0ea",
    "pastell": "#ffdcd0",
    "leuchten": "#ee6e3f",
    "kern": "#c2460d",
    "tinte": "#ba3f00",
    "grund": "#a0411c",
    "hauch_dk": "#352119",
    "tinte_dk": "#ffc2ad"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_kern": 5.03,
    "tinte_papier": 5.53,
    "tinte_karte": 5.21,
    "tinte_hauch": 4.98,
    "weiss_grund": 6.43,
    "ink_pastell": 11.74,
    "tinte_pastell": 4.32,
    "tinte_dk_papier": 11.41,
    "tinte_dk_hauch": 9.81
   }
  },
  {
   "key": "hpise",
   "name": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
   "kurz": "Heilpädagogik und inklusive soziale Entwicklung",
   "ort": "Rotgelb, zum Gelb",
   "satz": "Die Wärme: ‹warm und behaglich›.",
   "para": "§§ 768, 773",
   "H": 60,
   "winkel": 84.6,
   "heute": "#f98a3c",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#fff0e5",
    "pastell": "#ffddc3",
    "leuchten": "#da7e1e",
    "kern": "#a75c00",
    "tinte": "#9e5700",
    "grund": "#8a5017",
    "hauch_dk": "#332214",
    "tinte_dk": "#ffc18e"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 5.03,
    "tinte_papier": 5.5,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.94,
    "weiss_grund": 6.48,
    "ink_pastell": 11.73,
    "tinte_pastell": 4.29,
    "tinte_dk_papier": 11.15,
    "tinte_dk_hauch": 9.62
   }
  },
  {
   "key": "ps",
   "name": "Pädagogische Sektion",
   "kurz": "Pädagogik",
   "ort": "Gelb",
   "satz": "Das Licht: ‹die nächste Farbe am Licht›.",
   "para": "§§ 765–766",
   "H": 97,
   "winkel": 121.4,
   "heute": "#3b4881",
   "selbstlos": true,
   "fest": false,
   "stufen": {
    "hauch": "#f7f4e3",
    "pastell": "#efe5b8",
    "leuchten": "#f7d731",
    "kern": "#504d41",
    "tinte": "#23272b",
    "grund": "#37362d",
    "hauch_dk": "#2b2712",
    "tinte_dk": "#e6e8ea"
   },
   "kontrast": {
    "leuchten_papier": 1.43,
    "weiss_kern": 8.47,
    "tinte_papier": 15.04,
    "tinte_karte": 14.18,
    "tinte_hauch": 13.61,
    "weiss_grund": 12.15,
    "ink_pastell": 11.86,
    "tinte_pastell": 11.86,
    "tinte_dk_papier": 14.37,
    "tinte_dk_hauch": 12.2
   }
  },
  {
   "key": "lws",
   "name": "Sektion für Landwirtschaft",
   "kurz": "Landwirtschaft",
   "ort": "Grün",
   "satz": "Die Erde: ‹reale Befriedigung›.",
   "para": "§ 802",
   "H": 138,
   "winkel": 177.3,
   "heute": "#63b145",
   "selbstlos": false,
   "fest": true,
   "stufen": {
    "hauch": "#ecf7e9",
    "pastell": "#d2efc8",
    "leuchten": "#63b145",
    "kern": "#3a7f1a",
    "tinte": "#2e7800",
    "grund": "#366a20",
    "hauch_dk": "#1e2b1a",
    "tinte_dk": "#a4db91"
   },
   "kontrast": {
    "leuchten_papier": 2.66,
    "weiss_kern": 4.96,
    "tinte_papier": 5.52,
    "tinte_karte": 5.21,
    "tinte_hauch": 5.01,
    "weiss_grund": 6.48,
    "ink_pastell": 12.12,
    "tinte_pastell": 4.45,
    "tinte_dk_papier": 11.03,
    "tinte_dk_hauch": 9.27
   }
  },
  {
   "key": "nws",
   "name": "Naturwissenschaftliche Sektion",
   "kurz": "Naturwissenschaften",
   "ort": "Meergrün",
   "satz": "Die Anschauung: die Vereinigung der Urfarben Gelb und Blau.",
   "para": "§§ 785, 801",
   "H": 181,
   "winkel": 202.4,
   "heute": "#1e7b6e",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#e7f8f4",
    "pastell": "#c2f0e6",
    "leuchten": "#25a694",
    "kern": "#007d6f",
    "tinte": "#007668",
    "grund": "#19685d",
    "hauch_dk": "#162b27",
    "tinte_dk": "#8ed9cb"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.04,
    "tinte_papier": 5.54,
    "tinte_karte": 5.22,
    "tinte_hauch": 5.05,
    "weiss_grund": 6.6,
    "ink_pastell": 12.1,
    "tinte_pastell": 4.46,
    "tinte_dk_papier": 10.87,
    "tinte_dk_hauch": 9.18
   }
  },
  {
   "key": "srmk",
   "name": "Sektion für Redende und Musizierende Künste",
   "kurz": "Redende und Musizierende Künste",
   "ort": "Blau, zum Grün",
   "satz": "Der Klang: ‹Reiz und Ruhe›.",
   "para": "§§ 779, 781",
   "H": 225,
   "winkel": 226.4,
   "heute": "#598ddc",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#e5f7fe",
    "pastell": "#c0edff",
    "leuchten": "#00a1cb",
    "kern": "#00799a",
    "tinte": "#007291",
    "grund": "#19667f",
    "hauch_dk": "#132a32",
    "tinte_dk": "#86d7f7"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.0,
    "tinte_papier": 5.5,
    "tinte_karte": 5.19,
    "tinte_hauch": 5.0,
    "weiss_grund": 6.46,
    "ink_pastell": 12.03,
    "tinte_pastell": 4.4,
    "tinte_dk_papier": 10.99,
    "tinte_dk_hauch": 9.31
   }
  },
  {
   "key": "mas",
   "name": "Mathematisch-Astronomische Sektion",
   "kurz": "Mathematik und Astronomie",
   "ort": "Blau, tief",
   "satz": "Der Himmel: ‹die fernen Berge blau›.",
   "para": "§ 780",
   "H": 275,
   "winkel": 270.0,
   "heute": "#2e54a4",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#f0f3ff",
    "pastell": "#dde3ff",
    "leuchten": "#7e8eec",
    "kern": "#454ead",
    "tinte": "#525dcc",
    "grund": "#373e87",
    "hauch_dk": "#212538",
    "tinte_dk": "#a2aff3"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 7.13,
    "tinte_papier": 5.53,
    "tinte_karte": 5.21,
    "tinte_hauch": 5.0,
    "weiss_grund": 9.54,
    "ink_pastell": 11.82,
    "tinte_pastell": 4.35,
    "tinte_dk_papier": 8.37,
    "tinte_dk_hauch": 7.19
   }
  },
  {
   "key": "ssw",
   "name": "Sektion für Schöne Wissenschaften",
   "kurz": "Schöne Wissenschaften",
   "ort": "Blaurot",
   "satz": "Das Lesen: ‹fortgehen› und ‹ausruhen›.",
   "para": "§§ 787–788",
   "H": 292,
   "winkel": 290.4,
   "heute": "#5168c0",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#f3f2ff",
    "pastell": "#e4e0ff",
    "leuchten": "#9b86e7",
    "kern": "#725abd",
    "tinte": "#7354c6",
    "grund": "#604e9b",
    "hauch_dk": "#272336",
    "tinte_dk": "#ccc2ff"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.37,
    "tinte_papier": 5.51,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.97,
    "weiss_grund": 6.86,
    "ink_pastell": 11.75,
    "tinte_pastell": 4.3,
    "tinte_dk_papier": 10.7,
    "tinte_dk_hauch": 9.22
   }
  },
  {
   "key": "ms",
   "name": "Medizinische Sektion",
   "kurz": "Medizin",
   "ort": "Rotblau",
   "satz": "Das Wirksame: ‹erhält dadurch etwas Wirksames›.",
   "para": "§ 787",
   "H": 312,
   "winkel": 314.4,
   "heute": "#5f5599",
   "selbstlos": false,
   "fest": false,
   "stufen": {
    "hauch": "#f8f0fd",
    "pastell": "#f1dbff",
    "leuchten": "#b282cf",
    "kern": "#7d499a",
    "tinte": "#8b4fac",
    "grund": "#673f7d",
    "hauch_dk": "#2b2231",
    "tinte_dk": "#d1afe6"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 6.38,
    "tinte_papier": 5.51,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.95,
    "weiss_grund": 8.13,
    "ink_pastell": 11.68,
    "tinte_pastell": 4.28,
    "tinte_dk_papier": 9.23,
    "tinte_dk_hauch": 7.98
   }
  }
 ],
 "anker": [
  {
   "name": "Purpur",
   "winkel": 0,
   "hex": "#b93780"
  },
  {
   "name": "Gelbrot",
   "winkel": 60,
   "hex": "#e14d28"
  },
  {
   "name": "Gelb",
   "winkel": 120,
   "hex": "#efcc1d"
  },
  {
   "name": "Grün",
   "winkel": 180,
   "hex": "#57a943"
  },
  {
   "name": "Blau",
   "winkel": 240,
   "hex": "#0f74c5"
  },
  {
   "name": "Blaurot",
   "winkel": 300,
   "hex": "#7347af"
  }
 ],
 "sphaeren": [
  {
   "id": "vernunft",
   "name": "Vernunft",
   "von": 0,
   "bis": 90
  },
  {
   "id": "verstand",
   "name": "Verstand",
   "von": 90,
   "bis": 180
  },
  {
   "id": "sinnlichkeit",
   "name": "Sinnlichkeit",
   "von": 180,
   "bis": 270
  },
  {
   "id": "phantasie",
   "name": "Phantasie",
   "von": 270,
   "bis": 360
  }
 ],
 "sonder": [
  {
   "key": "goetheanum",
   "name": "Goetheanum",
   "hex": "#0061a9",
   "H": 255,
   "grund": "Das Markenblau des Ganzen – kein Sektionston liegt darauf.",
   "winkel": 246.0
  },
  {
   "key": "buehne",
   "name": "Bühne",
   "hex": "#968250",
   "H": 85,
   "grund": "Das Gold der Bühne – darum kein dunkles Gelb bei den Sektionen.",
   "winkel": 109.2
  }
 ],
 "theme": {
  "paper": [
   "#ffffff",
   "#16191c"
  ],
  "soft": [
   "#faf8f4",
   "#1e2329"
  ],
  "ink": [
   "#23272b",
   "#e6e8ea"
  ]
 }
};
