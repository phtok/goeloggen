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
   "traegt": "Lesetext in --ink, die Marke in Tinte oder Grund",
   "faelle": "Plakat, Folienhintergrund, Wallpaper, Hintergrund einer Sektionsseite, grosse Kachel",
   "regel": "--ink darauf ≥ 7:1 (1.4.6); Tinte darauf ≥ 3:1 als Objekt"
  },
  {
   "id": "leuchten",
   "name": "Leuchten",
   "traegt": "grosse weisse Schrift (≥ 24 px) – keinen Lesetext",
   "faelle": "Marke und Logo, Linie und Kante, Punkt im Menü, Diagramm, Wallpaper-Motiv, Plakattitel gross in Weiss, Icon",
   "regel": "auf Papier ≥ 3:1 als Objekt (1.4.11); Weiss darauf ≥ 3:1 nur gross (1.4.3)"
  },
  {
   "id": "tinte",
   "name": "Tinte",
   "traegt": "sich selbst als Schrift",
   "faelle": "Kicker, Link, Titel in Sektionsfarbe, Zahl, Label, Icon neben Text, Schrift im Chip",
   "regel": "auf Papier, Karte und Hauch ≥ 4.5:1 (1.4.3)"
  },
  {
   "id": "grund",
   "name": "Grund",
   "traegt": "Weiss, auch klein",
   "faelle": "Kopfband, Titelfeld, Knopf, Fusszeile, Auswahl, tiefe Fläche im Dunkelmodus",
   "regel": "Weiss darauf ≥ 5.5:1 (B01, Ziel über AA)"
  }
 ],
 "sektionen": [
  {
   "key": "aas",
   "name": "Allgemeine Anthroposophische Sektion",
   "kurz": "Allgemeine Anthroposophie",
   "ort": "Purpur",
   "H": 335,
   "heute": "#a24f8a",
   "stufen": {
    "hauch": "#feeef9",
    "pastell": "#f7bbe9",
    "leuchten": "#ff39e3",
    "tinte": "#ca00b2",
    "grund": "#a82794",
    "hauch_dk": "#31202d",
    "tinte_dk": "#ffb2ee"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 5.06,
    "tinte_karte": 4.77,
    "tinte_hauch": 4.53,
    "weiss_grund": 6.21,
    "ink_pastell": 9.48,
    "tinte_pastell": 3.19,
    "ink_hauch": 13.47,
    "tinte_dk_papier": 10.8,
    "tinte_dk_hauch": 9.35,
    "ink_dk_hauch_dk": 12.43
   }
  },
  {
   "key": "sbk",
   "name": "Sektion für Bildende Künste",
   "kurz": "Bildende Künste",
   "ort": "Purpur, zur warmen Seite",
   "H": 358,
   "heute": "#d072a0",
   "stufen": {
    "hauch": "#ffeef3",
    "pastell": "#ffbbd1",
    "leuchten": "#ff539d",
    "tinte": "#d60077",
    "grund": "#b52568",
    "hauch_dk": "#341f26",
    "tinte_dk": "#ffbfd3"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_auf_leuchten": 3.01,
    "tinte_papier": 5.09,
    "tinte_karte": 4.8,
    "tinte_hauch": 4.55,
    "weiss_grund": 6.12,
    "ink_pastell": 9.51,
    "tinte_pastell": 3.22,
    "ink_hauch": 13.44,
    "tinte_dk_papier": 11.47,
    "tinte_dk_hauch": 9.96,
    "ink_dk_hauch_dk": 12.48
   }
  },
  {
   "key": "szw",
   "name": "Sektion für Sozialwissenschaften",
   "kurz": "Sozialwissenschaften",
   "ort": "Gelbrot",
   "H": 18,
   "heute": "#df4164",
   "stufen": {
    "hauch": "#ffefef",
    "pastell": "#ffbdbe",
    "leuchten": "#ff5b6c",
    "tinte": "#de0040",
    "grund": "#bb263f",
    "hauch_dk": "#361f20",
    "tinte_dk": "#ffc2c3"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 5.02,
    "tinte_karte": 4.74,
    "tinte_hauch": 4.51,
    "weiss_grund": 6.07,
    "ink_pastell": 9.51,
    "tinte_pastell": 3.18,
    "ink_hauch": 13.49,
    "tinte_dk_papier": 11.56,
    "tinte_dk_hauch": 10.01,
    "ink_dk_hauch_dk": 12.44
   }
  },
  {
   "key": "js",
   "name": "Jugendsektion",
   "kurz": "Jugendsektion",
   "ort": "Rotgelb",
   "H": 35,
   "heute": "#ff675d",
   "stufen": {
    "hauch": "#fff0ec",
    "pastell": "#ffc0af",
    "leuchten": "#ff5f37",
    "tinte": "#d03500",
    "grund": "#af3a1c",
    "hauch_dk": "#36201b",
    "tinte_dk": "#ffc3b3"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 5.01,
    "tinte_karte": 4.72,
    "tinte_hauch": 4.52,
    "weiss_grund": 6.1,
    "ink_pastell": 9.6,
    "tinte_pastell": 3.2,
    "ink_hauch": 13.55,
    "tinte_dk_papier": 11.52,
    "tinte_dk_hauch": 9.94,
    "ink_dk_hauch_dk": 12.39
   }
  },
  {
   "key": "hpise",
   "name": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
   "kurz": "Heilpädagogik und inklusive soziale Entwicklung",
   "ort": "Gelb, zum Rotgelb",
   "H": 55,
   "heute": "#f98a3c",
   "stufen": {
    "hauch": "#fff0e7",
    "pastell": "#ffc299",
    "leuchten": "#e47600",
    "tinte": "#ad5800",
    "grund": "#93501b",
    "hauch_dk": "#342215",
    "tinte_dk": "#ffc197"
   },
   "kontrast": {
    "leuchten_papier": 3.05,
    "weiss_auf_leuchten": 3.05,
    "tinte_papier": 5.03,
    "tinte_karte": 4.74,
    "tinte_hauch": 4.52,
    "weiss_grund": 6.17,
    "ink_pastell": 9.62,
    "tinte_pastell": 3.22,
    "ink_hauch": 13.51,
    "tinte_dk_papier": 11.2,
    "tinte_dk_hauch": 9.62,
    "ink_dk_hauch_dk": 12.34
   }
  },
  {
   "key": "lws",
   "name": "Sektion für Landwirtschaft",
   "kurz": "Landwirtschaft",
   "ort": "Grün",
   "H": 140,
   "heute": "#63b145",
   "stufen": {
    "hauch": "#ecf7e9",
    "pastell": "#b2e0a8",
    "leuchten": "#34ab00",
    "tinte": "#258100",
    "grund": "#2b6e19",
    "hauch_dk": "#1d2b1a",
    "tinte_dk": "#9edb91"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_auf_leuchten": 3.01,
    "tinte_papier": 4.98,
    "tinte_karte": 4.69,
    "tinte_hauch": 4.51,
    "weiss_grund": 6.27,
    "ink_pastell": 10.11,
    "tinte_pastell": 3.35,
    "ink_hauch": 13.64,
    "tinte_dk_papier": 10.92,
    "tinte_dk_hauch": 9.2,
    "ink_dk_hauch_dk": 12.1
   }
  },
  {
   "key": "nws",
   "name": "Naturwissenschaftliche Sektion",
   "kurz": "Naturwissenschaften",
   "ort": "Meergrün",
   "H": 181,
   "heute": "#1e7b6e",
   "stufen": {
    "hauch": "#e5f9f4",
    "pastell": "#a2e0d3",
    "leuchten": "#00a794",
    "tinte": "#007e70",
    "grund": "#1e6c61",
    "hauch_dk": "#172b27",
    "tinte_dk": "#97d7ca"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 4.98,
    "tinte_karte": 4.69,
    "tinte_hauch": 4.55,
    "weiss_grund": 6.23,
    "ink_pastell": 10.12,
    "tinte_pastell": 3.35,
    "ink_hauch": 13.74,
    "tinte_dk_papier": 10.83,
    "tinte_dk_hauch": 9.13,
    "ink_dk_hauch_dk": 12.11
   }
  },
  {
   "key": "ps",
   "name": "Pädagogische Sektion",
   "kurz": "Pädagogik",
   "ort": "Blau, zum Grün",
   "H": 205,
   "heute": "#3b4881",
   "stufen": {
    "hauch": "#e4f8fa",
    "pastell": "#a1dde4",
    "leuchten": "#00a4b1",
    "tinte": "#007c86",
    "grund": "#1d6b73",
    "hauch_dk": "#172a2c",
    "tinte_dk": "#99d7de"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 4.97,
    "tinte_karte": 4.68,
    "tinte_hauch": 4.52,
    "weiss_grund": 6.17,
    "ink_pastell": 10.01,
    "tinte_pastell": 3.31,
    "ink_hauch": 13.68,
    "tinte_dk_papier": 11.03,
    "tinte_dk_hauch": 9.35,
    "ink_dk_hauch_dk": 12.18
   }
  },
  {
   "key": "srmk",
   "name": "Sektion für Redende und Musizierende Künste",
   "kurz": "Redende und Musizierende Künste",
   "ort": "Blau, licht",
   "H": 232,
   "heute": "#598ddc",
   "stufen": {
    "hauch": "#e7f6ff",
    "pastell": "#a0daf9",
    "leuchten": "#009fd6",
    "tinte": "#0078a2",
    "grund": "#1d6889",
    "hauch_dk": "#162933",
    "tinte_dk": "#98d5f5"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_auf_leuchten": 3.03,
    "tinte_papier": 4.99,
    "tinte_karte": 4.7,
    "tinte_hauch": 4.52,
    "weiss_grund": 6.19,
    "ink_pastell": 9.95,
    "tinte_pastell": 3.3,
    "ink_hauch": 13.62,
    "tinte_dk_papier": 11.07,
    "tinte_dk_hauch": 9.41,
    "ink_dk_hauch_dk": 12.22
   }
  },
  {
   "key": "mas",
   "name": "Mathematisch-Astronomische Sektion",
   "kurz": "Mathematik und Astronomie",
   "ort": "Blau",
   "H": 258,
   "heute": "#2e54a4",
   "stufen": {
    "hauch": "#edf4ff",
    "pastell": "#b5d3ff",
    "leuchten": "#4b94ff",
    "tinte": "#006ae5",
    "grund": "#004395",
    "hauch_dk": "#1c2738",
    "tinte_dk": "#84b6ff"
   },
   "kontrast": {
    "leuchten_papier": 3.01,
    "weiss_auf_leuchten": 3.01,
    "tinte_papier": 5.01,
    "tinte_karte": 4.72,
    "tinte_hauch": 4.53,
    "weiss_grund": 9.39,
    "ink_pastell": 9.83,
    "tinte_pastell": 3.27,
    "ink_hauch": 13.59,
    "tinte_dk_papier": 8.5,
    "tinte_dk_hauch": 7.24,
    "ink_dk_hauch_dk": 12.24
   }
  },
  {
   "key": "ssw",
   "name": "Sektion für Schöne Wissenschaften",
   "kurz": "Schöne Wissenschaften",
   "ort": "Blau, zum Rotblau",
   "H": 282,
   "heute": "#5168c0",
   "stufen": {
    "hauch": "#f1f2ff",
    "pastell": "#c9ccff",
    "leuchten": "#8a86ff",
    "tinte": "#694eff",
    "grund": "#5949cf",
    "hauch_dk": "#242437",
    "tinte_dk": "#c3c6ff"
   },
   "kontrast": {
    "leuchten_papier": 3.03,
    "weiss_auf_leuchten": 3.03,
    "tinte_papier": 5.08,
    "tinte_karte": 4.79,
    "tinte_hauch": 4.57,
    "weiss_grund": 6.4,
    "ink_pastell": 9.71,
    "tinte_pastell": 3.28,
    "ink_hauch": 13.52,
    "tinte_dk_papier": 10.79,
    "tinte_dk_hauch": 9.29,
    "ink_dk_hauch_dk": 12.37
   }
  },
  {
   "key": "ms",
   "name": "Medizinische Sektion",
   "kurz": "Medizin",
   "ort": "Rotblau",
   "H": 300,
   "heute": "#5f5599",
   "stufen": {
    "hauch": "#f5f1ff",
    "pastell": "#d9c6ff",
    "leuchten": "#af78ff",
    "tinte": "#982fff",
    "grund": "#6826af",
    "hauch_dk": "#292335",
    "tinte_dk": "#caadff"
   },
   "kontrast": {
    "leuchten_papier": 3.02,
    "weiss_auf_leuchten": 3.02,
    "tinte_papier": 5.02,
    "tinte_karte": 4.73,
    "tinte_hauch": 4.52,
    "weiss_grund": 8.45,
    "ink_pastell": 9.65,
    "tinte_pastell": 3.22,
    "ink_hauch": 13.54,
    "tinte_dk_papier": 9.19,
    "tinte_dk_hauch": 7.89,
    "ink_dk_hauch_dk": 12.33
   }
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
