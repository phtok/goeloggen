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
   "H": 335,
   "winkel": 342.0,
   "heute": "#a24f8a",
   "stufen": {
    "hauch": "#feeef9",
    "pastell": "#f4bde7",
    "leuchten": "#ce76bc",
    "kern": "#a74696",
    "tinte": "#a83f96",
    "grund": "#8b407d",
    "hauch_dk": "#31202d",
    "tinte_dk": "#f8b7e9"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_kern": 5.3,
    "tinte_papier": 5.5,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.93,
    "weiss_grund": 6.72,
    "ink_pastell": 9.51,
    "tinte_pastell": 3.48,
    "tinte_dk_papier": 10.88,
    "tinte_dk_hauch": 9.41
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
   "stufen": {
    "hauch": "#ffeef3",
    "pastell": "#ffbbd1",
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
    "ink_pastell": 9.51,
    "tinte_pastell": 3.49,
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
   "stufen": {
    "hauch": "#ffefef",
    "pastell": "#ffbdbe",
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
    "ink_pastell": 9.51,
    "tinte_pastell": 3.49,
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
   "H": 35,
   "winkel": 60.0,
   "heute": "#ff675d",
   "stufen": {
    "hauch": "#fff0ec",
    "pastell": "#ffc0af",
    "leuchten": "#f06c4c",
    "kern": "#c44424",
    "tinte": "#c53100",
    "grund": "#a24028",
    "hauch_dk": "#36201b",
    "tinte_dk": "#ffc3b3"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.0,
    "tinte_papier": 5.51,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.96,
    "weiss_grund": 6.36,
    "ink_pastell": 9.6,
    "tinte_pastell": 3.52,
    "tinte_dk_papier": 11.52,
    "tinte_dk_hauch": 9.94
   }
  },
  {
   "key": "hpise",
   "name": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
   "kurz": "Heilpädagogik und inklusive soziale Entwicklung",
   "ort": "Gelb, zum Rotgelb",
   "satz": "Die Wärme: ‹warm und behaglich›.",
   "para": "§§ 768, 773",
   "H": 55,
   "winkel": 79.7,
   "heute": "#f98a3c",
   "stufen": {
    "hauch": "#fff0e7",
    "pastell": "#ffc299",
    "leuchten": "#dd7b2b",
    "kern": "#ad5800",
    "tinte": "#a45300",
    "grund": "#8f4e17",
    "hauch_dk": "#342215",
    "tinte_dk": "#ffc197"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 5.03,
    "tinte_papier": 5.5,
    "tinte_karte": 5.19,
    "tinte_hauch": 4.95,
    "weiss_grund": 6.42,
    "ink_pastell": 9.62,
    "tinte_pastell": 3.52,
    "tinte_dk_papier": 11.2,
    "tinte_dk_hauch": 9.62
   }
  },
  {
   "key": "lws",
   "name": "Sektion für Landwirtschaft",
   "kurz": "Landwirtschaft",
   "ort": "Grün",
   "satz": "Die Erde: ‹reale Befriedigung›.",
   "para": "§ 802",
   "H": 140,
   "winkel": 180.0,
   "heute": "#63b145",
   "stufen": {
    "hauch": "#ecf7e9",
    "pastell": "#b2e0a8",
    "leuchten": "#5aa649",
    "kern": "#337f1f",
    "tinte": "#227900",
    "grund": "#316a23",
    "hauch_dk": "#1d2b1a",
    "tinte_dk": "#a4d998"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 5.0,
    "tinte_papier": 5.52,
    "tinte_karte": 5.21,
    "tinte_hauch": 5.01,
    "weiss_grund": 6.53,
    "ink_pastell": 10.11,
    "tinte_pastell": 3.71,
    "tinte_dk_papier": 10.89,
    "tinte_dk_hauch": 9.17
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
   "stufen": {
    "hauch": "#e7f8f4",
    "pastell": "#a1e0d3",
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
    "ink_pastell": 10.11,
    "tinte_pastell": 3.72,
    "tinte_dk_papier": 10.87,
    "tinte_dk_hauch": 9.18
   }
  },
  {
   "key": "ps",
   "name": "Pädagogische Sektion",
   "kurz": "Pädagogik",
   "ort": "Blau, zum Grün",
   "satz": "Das Wachsen: Ruhe, aus der Kraft wird.",
   "para": "§§ 779, 802",
   "H": 205,
   "winkel": 215.5,
   "heute": "#3b4881",
   "stufen": {
    "hauch": "#e5f8fa",
    "pastell": "#98dfe7",
    "leuchten": "#00a4b1",
    "kern": "#007c87",
    "tinte": "#00747e",
    "grund": "#196870",
    "hauch_dk": "#132b2d",
    "tinte_dk": "#85dbe4"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 4.96,
    "tinte_papier": 5.53,
    "tinte_karte": 5.21,
    "tinte_hauch": 5.04,
    "weiss_grund": 6.45,
    "ink_pastell": 10.06,
    "tinte_pastell": 3.7,
    "tinte_dk_papier": 11.14,
    "tinte_dk_hauch": 9.39
   }
  },
  {
   "key": "srmk",
   "name": "Sektion für Redende und Musizierende Künste",
   "kurz": "Redende und Musizierende Künste",
   "ort": "Blau, licht",
   "satz": "Der Klang: ‹Reiz und Ruhe›.",
   "para": "§§ 779, 781",
   "H": 232,
   "winkel": 230.2,
   "heute": "#598ddc",
   "stufen": {
    "hauch": "#e7f6ff",
    "pastell": "#9ddbfc",
    "leuchten": "#179fd4",
    "kern": "#0078a3",
    "tinte": "#007098",
    "grund": "#186586",
    "hauch_dk": "#152934",
    "tinte_dk": "#8cd6fd"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_kern": 4.98,
    "tinte_papier": 5.57,
    "tinte_karte": 5.25,
    "tinte_hauch": 5.04,
    "weiss_grund": 6.47,
    "ink_pastell": 10.0,
    "tinte_pastell": 3.71,
    "tinte_dk_papier": 11.05,
    "tinte_dk_hauch": 9.4
   }
  },
  {
   "key": "mas",
   "name": "Mathematisch-Astronomische Sektion",
   "kurz": "Mathematik und Astronomie",
   "ort": "Blau",
   "satz": "Der Himmel: ‹die fernen Berge blau›.",
   "para": "§ 780",
   "H": 258,
   "winkel": 249.6,
   "heute": "#2e54a4",
   "stufen": {
    "hauch": "#edf4ff",
    "pastell": "#b5d3ff",
    "leuchten": "#5c95ea",
    "kern": "#1a57ad",
    "tinte": "#1e66ca",
    "grund": "#174687",
    "hauch_dk": "#1c2738",
    "tinte_dk": "#8db6f3"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_kern": 6.98,
    "tinte_papier": 5.51,
    "tinte_karte": 5.2,
    "tinte_hauch": 4.98,
    "weiss_grund": 9.28,
    "ink_pastell": 9.83,
    "tinte_pastell": 3.6,
    "tinte_dk_papier": 8.5,
    "tinte_dk_hauch": 7.24
   }
  },
  {
   "key": "ssw",
   "name": "Sektion für Schöne Wissenschaften",
   "kurz": "Schöne Wissenschaften",
   "ort": "Blau, zum Rotblau",
   "satz": "Das Lesen: ‹fortgehen› und ‹ausruhen›.",
   "para": "§§ 787–788",
   "H": 282,
   "winkel": 278.4,
   "heute": "#5168c0",
   "stufen": {
    "hauch": "#f1f2ff",
    "pastell": "#c9ccff",
    "leuchten": "#8b8beb",
    "kern": "#635fc2",
    "tinte": "#6159ca",
    "grund": "#54529f",
    "hauch_dk": "#242437",
    "tinte_dk": "#c3c6ff"
   },
   "kontrast": {
    "leuchten_papier": 3.0,
    "weiss_kern": 5.32,
    "tinte_papier": 5.54,
    "tinte_karte": 5.22,
    "tinte_hauch": 4.98,
    "weiss_grund": 6.81,
    "ink_pastell": 9.71,
    "tinte_pastell": 3.58,
    "tinte_dk_papier": 10.79,
    "tinte_dk_hauch": 9.29
   }
  },
  {
   "key": "ms",
   "name": "Medizinische Sektion",
   "kurz": "Medizin",
   "ort": "Rotblau",
   "satz": "Das Wirksame: ‹erhält dadurch etwas Wirksames›.",
   "para": "§ 787",
   "H": 300,
   "winkel": 300.0,
   "heute": "#5f5599",
   "stufen": {
    "hauch": "#f5f1ff",
    "pastell": "#d8c7fa",
    "leuchten": "#a486d7",
    "kern": "#704ea4",
    "tinte": "#7c54b6",
    "grund": "#5c4385",
    "hauch_dk": "#292333",
    "tinte_dk": "#c7b3ed"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_kern": 6.34,
    "tinte_papier": 5.53,
    "tinte_karte": 5.21,
    "tinte_hauch": 4.98,
    "weiss_grund": 8.09,
    "ink_pastell": 9.64,
    "tinte_pastell": 3.54,
    "tinte_dk_papier": 9.33,
    "tinte_dk_hauch": 8.03
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
