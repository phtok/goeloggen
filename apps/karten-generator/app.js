"use strict";

/* Kartentool — Zustand, Szene und Interaktion.
   Grundkarte: assets/gelaende.svg (generiert aus der Original-AI-Datei).
   Orte: orte.js (generiert aus den Beispielkarten, mm-genau).
   Alle Farben im Szenen-SVG sind Druck-Artefaktfarben der gedruckten Karte
   (aus den Beispielkarten übernommen), keine Theme-Flächen — die Bedien-
   oberfläche selbst läuft vollständig über die Design-System-Tokens. */

const SZENE = { breite: KARTE.blatt.breite, hoehe: KARTE.blatt.hoehe };
const EIGENE_START_NR = 60; // feste Nummern (Modus ‹wie Vorlage›)

// Markerfarben aus den Beispielkarten (LT25 rot/blau, Willkommensplan
// grau/gartengrün) plus dunkles Hausgold (Weiss bleibt lesbar — B01).
const MARKER_FARBEN = {
  rot: "#ec5f6c",
  blau: "#81b2cb",
  gruen: "#369e7a",
  grau: "#949596",
  gold: "#94702e"
};
const FARB_ZYKLUS = ["rot", "blau", "gruen", "grau", "gold"];
const TINTE = "#4e4f4a";
// Leise Druck-Tinte für Strukturbeiwerk (Kategorie-Titel der Legende):
// gerechnet 5.07:1 auf Weiss (B02, ≥4.5:1 für Lesetext).
const TINTE_LEISE = "#6e6f6a";

// Schriftrollen: Sprache (Titel, Legende, Gebäudenamen) in der Hausschrift
// (Titelschnitt = Deutlich); die Kreiszahlen der Marker sind das
// Sonderelement des Design-Systems (.step-num) und laufen in der
// Hausschrift Laut (680 = --w-strong, dort vermessen).
const SCHRIFT_SPRACHE = "GoetheanumDeutlich";
const SCHRIFT_ZAHL = "GoetheanumLaut";

// Optischer Sitz von Ziffern im Kreis: reine Zentrierung zentriert die
// Zeilenbox, nicht die Zeichen-Tinte — Tintenmitte der Ziffern liegt bei
// ~330/1000 über der Grundlinie (im Design-System vermessen, base.css
// .step-num). Grundlinie also um 0.33 × Schriftgrad unter die Kreismitte.
const ZIFFERN_SITZ = 0.33;

// Grundfarben-Rollen der Geländekarte (siehe tools/karten/build-gelaende-svg.py).
const ROLLEN = [
  ["umgebung", "Umgebung"],
  ["umgebung-hell", "Umgebung, hell"],
  ["campus", "Campus-Gelände"],
  ["gebaeude", "Gebäude Umgebung"],
  ["gebaeude-campus", "Campus-Gebäude"],
  ["goetheanum", "Goetheanum"],
  ["wege", "Wege und Plätze"],
  ["parkflaeche", "Parkflächen"],
  ["akzent", "Akzente"],
  ["wiese", "Wiesen (eingefärbt)"]
];

// Zwei Voreinstellungen: ‹hell› (Tagung/LT25) und ‹gedeckt› (Recolor 2023),
// aus den Original-Varianten abgeleitet (Form-Abgleich identischer Pfade).
// ‹wiese› greift nur auf eingefärbte Wiesenflächen (stimmiger Grünton).
const PRESETS = {
  "hell": {
    umgebung: "#edf6fb", "umgebung-hell": "#edf6fb", campus: "#9fccec",
    gebaeude: "#737e8f", "gebaeude-campus": "#67a8da", goetheanum: "#006eb4",
    wege: "#ffffff", parkflaeche: "#edf6fb", akzent: "#006eb4",
    wiese: "#a6d19b"
  },
  "gedeckt": {
    umgebung: "#edf5fa", "umgebung-hell": "#edf5fa", campus: "#8abfe5",
    gebaeude: "#5298cc", "gebaeude-campus": "#5298cc", goetheanum: "#0067b2",
    wege: "#ffffff", parkflaeche: "#edf5fa", akzent: "#0067b2",
    wiese: "#96c68c"
  }
};
const PRESET_MIGRATION = { "Tagung hell": "hell", "Recolor 2023": "gedeckt" };

const SPEICHER_SCHLUESSEL = "goetheanum-karten-v2";

const state = {
  titel: "",           // Kurztitel der Tagung samt Jahr (Platzhalter im Feld)
  untertitel: "",      // Datum der Veranstaltung, z. B. ‹1. bis 5. Juli 2026›
  eigeneTitel: "",     // Gruppentitel der eigenen Marken in der Legende
  sprache: "de",
  format: "a4",
  beschnitt: true,
  marken: false,
  zoom: 1.15,
  an: { o1: true, o2: true, o3: true },  // Start: die ersten drei als Beispiel
  gebaeudeAn: {},      // Campus-Gebäude, von Hand aktiviert (zusätzlich zu Markern)
  gebaeudeAus: {},     // Campus-Gebäude, von Hand passiviert (übersteuert Marker)
  teileAus: {},        // Ort-id -> { Teil-Index: true } (abgewählte Teil-Orte)
  notizenAus: {},      // Ort-id -> { Notiz-Index: true } (abgewählte Etagen/Lifte)
  labels: {},          // Ort-id -> geänderte Beschriftung
  markerFarben: {},    // Ort-id -> Farbname (überschreibt die Vorlagen-Farbe)
  positionen: {},      // Ort-id -> [x, y] (verschobene Marke, Standardlage)
  eigene: [],          // { id, label, farbe, x, y, marker } — x/y in Blatt-mm der Standardlage
  wiesen: { klein: false, gross: false },
  kompakt: false,       // kompakte Legende (kleinerer Grad, engere Zeilen)
  ausschnitt: { skala: 1, dx: 0, dy: 0 },  // Kartenausschnitt relativ zur Standardlage
  logo: { x: null, y: null, skala: 1 },    // Campus-Logo: Mitte (mm) + Grösse
  titelLogo: null,     // { markup, verhaeltnis, breite } — Sonderlogo statt Titel
  preset: "gedeckt",   // Standard; Anpassung je Rolle bleibt möglich
  farben: { ...PRESETS["gedeckt"] },
  platzieren: null,    // { label, farbe } während der Platzierung (neue Marke)
  platzierenOrt: null, // Ort-id, deren Marke gerade verschoben wird
  platzierenLogo: false, // Logo wird gerade neu platziert
  bearbeiten: null     // Ort-id, deren Beschriftung gerade editiert wird
};

/* ---------- Grundkarte, Logo, Kompass laden ---------- */

let gelaendeInhalt = null;   // SVG-Inhalt ohne Wurzel/<style>
let gelaendeMasse = { breite: 1006.3, hoehe: 651.968 };
let logoInhalt = null;       // Campus-Wortmarke aus dem Logogenerator (reine Pfade)
let kompassInhalt = null;    // Kompassrose aus den Icons v2.7 (kompass-2)
const ikonen = {};           // weitere Icons v2.7 (treppe, fahrstuhl, pfeil)

async function ladeGelaende() {
  const antwort = await fetch("assets/gelaende.svg");
  const text = await antwort.text();
  const wurzel = text.match(/<svg[^>]*>/)[0];
  const breite = parseFloat(wurzel.match(/width="([\d.]+)"/)[1]);
  const hoehe = parseFloat(wurzel.match(/height="([\d.]+)"/)[1]);
  gelaendeMasse = { breite, hoehe };
  gelaendeInhalt = text
    .replace(/^[\s\S]*?<svg[^>]*>/, "")
    .replace(/<\/svg>\s*$/, "")
    .replace(/<style>[\s\S]*?<\/style>/, "");
}

// Das Logo kommt aus dem Logogenerator (LogoEngine) — dieselben Pfaddaten
// wie bei allen anderen Anwendungen, dadurch vektor-exportierbar.
function logoErzeugen() {
  try {
    const svgText = window.LogoEngine.svg({
      cat: "teilbereiche", org: "campus", layout: "desktop",
      lang: "de", mode: "original", txt: ""
    });
    const element = new DOMParser().parseFromString(svgText, "image/svg+xml").documentElement;
    const vb = (element.getAttribute("viewBox") || "0 0 1 1").split(/\s+/).map(Number);
    logoInhalt = { breite: vb[2], hoehe: vb[3], markup: element.innerHTML };
  } catch (fehler) {
    console.warn("Logogenerator nicht verfügbar, Karte ohne Logo:", fehler);
  }
}

async function ladeIkone(name) {
  const antwort = await fetch(`../../assets/fonts/goetheanum/Icons-Einzeldateien/svg/${name}.svg`);
  const text = await antwort.text();
  // Farbe kommt jeweils von der einbettenden Gruppe.
  return text
    .replace(/^[\s\S]*?<svg[^>]*>/, "")
    .replace(/<\/svg>\s*$/, "")
    .replace(/ fill="#1a1a1a"/g, "");
}

async function ladeIkonen() {
  const namen = ["kompass-2", "pfeil-rechts-fett", "wc-rollstuhl", "wc-gruppe", "wc-herren", "wc-damen", "wickelraum"];
  await Promise.all(namen.map(async (name) => {
    try {
      ikonen[name] = await ladeIkone(name);
    } catch (fehler) {
      console.warn(`Icon ${name} nicht ladbar:`, fehler);
    }
  }));
  kompassInhalt = ikonen["kompass-2"] || null;
  ikonBoxenMessen();
}

// Tinten-Boxen der Icons vermessen (die Einzeldateien tragen je eigene
// viewBoxen und Versätze — Symbol-Marken werden auf die Tinte zentriert).
const ikonBoxen = {};

function ikonBoxenMessen() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.style.position = "absolute";
  svg.style.visibility = "hidden";
  document.body.appendChild(svg);
  Object.entries(ikonen).forEach(([name, inhalt]) => {
    const g = document.createElementNS(ns, "g");
    g.innerHTML = inhalt;
    svg.appendChild(g);
    try { ikonBoxen[name] = g.getBBox(); } catch (fehler) { /* bleibt ohne Box */ }
    g.remove();
  });
  svg.remove();
}

// Symbol in Zielgrösse (mm, längere Tintenkante) mit Tintenmitte auf (x, y);
// leichter Konturauftrag in gleicher Farbe kräftigt die feinen Stege.
function symbolMarkup(name, x, y, groesse, farbe, maxHoehe) {
  const inhalt = ikonen[name];
  const box = ikonBoxen[name];
  if (!inhalt || !box) return "";
  let skala = groesse / Math.max(box.width, box.height);
  if (maxHoehe) skala = Math.min(groesse / box.width, maxHoehe / box.height);
  const tx = x - (box.x + box.width / 2) * skala;
  const ty = y - (box.y + box.height / 2) * skala;
  const auftrag = (0.09 / skala).toFixed(1);  // ~0.09 mm Fettung
  return `<g transform="translate(${tx.toFixed(3)} ${ty.toFixed(3)}) scale(${skala.toFixed(5)})"`
    + ` fill="${farbe}" stroke="${farbe}" stroke-width="${auftrag}">${inhalt}</g>`;
}

// Icons v2.7: viewBox "16.2 -983.8 967.6 967.6", Inhalt y-gespiegelt.
// Einbettung: Zielgrösse in mm, zentriert auf (x, y).
function ikonMarkup(name, x, y, groesse, farbe, drehung) {
  const inhalt = ikonen[name];
  if (!inhalt) return "";
  const skala = groesse / 967.6;
  const dreh = drehung ? ` rotate(${drehung})` : "";
  return `<g transform="translate(${x} ${y})${dreh} scale(${skala}) translate(-500 500)" fill="${farbe}">${inhalt}</g>`;
}

// Campus-Gebäude: aktiv (dunkel) durch Handschaltung oder einen aktiven
// zugehörigen Marker; passiv = helleres Campus-Gebäude-Blau.
// Die beiden Goetheanum-Schalen schalten als Einheit.
const BAU_ALIAS = { "campusbau-52": "goetheanum-bau", "campusbau-53": "goetheanum-bau" };

function bauEinheit(bauId) {
  return BAU_ALIAS[bauId] || bauId;
}

// Gebäude eines Orts: bei geteilten Orten (Halde/Puppentheater) schaltet
// jeder aktive Teil sein eigenes Gebäude (gebaeudeTeile, Index = Teil).
function ortGebaeude(ort, alleTeile) {
  if (ort.gebaeudeTeile) {
    const indizes = alleTeile
      ? ort.gebaeudeTeile.map((g, index) => ({ index }))
      : aktiveTeile(ort);
    return indizes.map(({ index }) => ort.gebaeudeTeile[index]).filter(Boolean);
  }
  return ort.gebaeude ? [ort.gebaeude] : [];
}

function bauAktiv(bauId) {
  const einheit = bauEinheit(bauId);
  if (state.gebaeudeAus[einheit]) return false;  // Handschaltung schlägt Marker
  if (state.gebaeudeAn[einheit]) return true;
  return alleOrte().some((ort) => ortAktiv(ort)
    && ortGebaeude(ort).some((g) => bauEinheit(g) === einheit));
}

// Fugendichtung: jede Fläche trägt eine Eigenkontur in ihrer Füllfarbe
// (0.35 pt ≈ 0.12 mm). Sie deckt die haarfeinen weissen Fugen, wo
// angrenzende Flächen beim Rastern nicht ganz schliessen — unsichtbar,
// weil Ton in Ton, und sie folgt jeder Umfärbung (auch aktiven Gebäuden).
function flaechenFarbe(farbe) {
  return `fill="${farbe}" stroke="${farbe}" stroke-width="0.35"`;
}

function gelaendeMarkup() {
  let inhalt = gelaendeInhalt;
  inhalt = inhalt.replace(/class="k-parkflaeche" id="parkflaeche-(\d+)"/g, (voll, nr) => {
    return `${flaechenFarbe(state.farben.parkflaeche)} id="parkflaeche-${nr}"`;
  });
  // Wiesenflächen: eingefärbt im Wiesen-Grün, sonst wie das Campus-Gelände;
  // die Halter beschneiden die Quellpolygone am Weg vor dem Rondell.
  inhalt = inhalt.replace(/class="k-wiese" id="wiese-(klein|gross)"/g, (voll, name) => {
    const farbe = state.wiesen[name] ? state.farben.wiese : state.farben.campus;
    return `${flaechenFarbe(farbe)} id="wiese-${name}"`;
  });
  inhalt = inhalt.replace(/data-wiese-strich="(klein|gross)"/g, (voll, name) => {
    const farbe = state.wiesen[name] ? state.farben.wiese : state.farben.campus;
    return `stroke="${farbe}"`;
  });
  // Der beschnittene Südzipfel bleibt Campus-blau: unter die geclippte
  // (grüne) Fläche legt sich eine ungeclippte Kopie in Campus-Farbe.
  // Der Beschnitt gilt nur der grossen Wiese (ihr Quellpolygon läuft unter
  // dem Weg am Rondell weiter) — die kleine Wiese bleibt ungeteilt grün.
  inhalt = inhalt.replace(/<g data-wiese-halter="(klein|gross)">([\s\S]*?)<\/g>/g,
    (voll, name, kern) => {
      if (name === "klein") return kern;
      const basis = kern
        .replace(/fill="[^"]*"/, `fill="${state.farben.campus}"`)
        .replace(/stroke="[^"]*"/, `stroke="${state.farben.campus}"`)
        .replace(/ id="wiese-(?:klein|gross)"/, "");
      return basis + `<g clip-path="url(#wiese-clip)">${kern}</g>`;
    });
  // Campus-Gebäude aktiv/passiv (id steht vor der Klasse im Tag).
  inhalt = inhalt.replace(
    /<path id="(campusbau-\d+)"([^>]*?)class="k-(goetheanum|gebaeude-campus|akzent)"/g,
    (voll, bauId, mitte) => {
      const farbe = bauAktiv(bauId) ? state.farben.goetheanum : state.farben["gebaeude-campus"];
      return `<path id="${bauId}"${mitte}${flaechenFarbe(farbe)}`;
    }
  );
  inhalt = inhalt.replace(/class="k-([a-z-]+)"/g, (voll, rolle) => {
    return flaechenFarbe(state.farben[rolle] || "#cccccc");
  });
  // Striche folgen denselben Rollen wie die Füllungen — sonst zeichnen die
  // Original-Strichfarben Konturen an Flächen, die flach gemeint sind.
  inhalt = inhalt.replace(/data-ks="([a-z-]+)"/g, (voll, rolle) => {
    return `stroke="${state.farben[rolle] || "#cccccc"}"`;
  });
  return inhalt;
}

// Beschnitt der Wiesenpolygone (Gelände-Koordinaten aus Blatt-mm gerechnet).
function wieseClipMarkup() {
  const g = KARTE.gelaende;
  const s = g.breite / gelaendeMasse.breite;
  const punkte = [[150, 40], [250, 40], [250, 212], [216, 212], [216, 192],
    [196, 190], [176, 167], [150, 148]]
    .map(([x, y]) => `${((x - g.x) / s).toFixed(1)},${((y - g.y) / s).toFixed(1)}`)
    .join(" ");
  return `<clipPath id="wiese-clip"><polygon points="${punkte}" /></clipPath>`;
}

/* ---------- Kartenausschnitt ----------
   Der Ausschnitt ist eine Ähnlichkeitsabbildung auf den Blattkoordinaten der
   Standardlage: p' = (dx + skala·px, dy + skala·py). Karte, Gebäudenamen und
   Kompass werden als Gruppe transformiert; Marker behalten ihre Grösse und
   werden nur in der Position mitgenommen — so bleiben die aus den Beispielen
   extrahierten Koordinaten die eine Quelle der Wahrheit. */

function anp(x, y) {
  const a = state.ausschnitt;
  return [a.dx + a.skala * x, a.dy + a.skala * y];
}

function anpZurueck(x, y) {
  const a = state.ausschnitt;
  return [(x - a.dx) / a.skala, (y - a.dy) / a.skala];
}

function ausschnittSetzen(skala) {
  // Zoom um die Blattmitte, damit der Ausschnitt nicht wegläuft.
  const a = state.ausschnitt;
  const neu = Math.min(1.8, Math.max(0.7, skala));
  const cx = SZENE.breite / 2, cy = SZENE.hoehe / 2;
  a.dx = cx - (neu / a.skala) * (cx - a.dx);
  a.dy = cy - (neu / a.skala) * (cy - a.dy);
  a.skala = neu;
}

/* ---------- Orte / Daten ---------- */

function alleOrte() {
  return ORTE.concat(state.eigene.map((e) => ({
    id: e.id, marker: e.marker, art: "eigene", farbe: e.farbe,
    label: e.label, spalte: 1, positionen: [[e.x, e.y]]
  })));
}

function ortAktiv(ort) {
  if (!state.an[ort.id]) return false;
  if (ort.teile) return aktiveTeile(ort).length > 0;
  return true;
}

function sprachText(wert) {
  if (wert && typeof wert === "object") return wert[state.sprache] || wert.de;
  return wert;
}

function aktiveTeile(ort) {
  const aus = state.teileAus[ort.id] || {};
  return (ort.teile || []).map((teil, index) => ({ teil, index }))
    .filter(({ index }) => !aus[index]);
}

function aktiveNotizen(ort) {
  const aus = state.notizenAus[ort.id] || {};
  return (ort.notizen || []).map((notiz, index) => ({ notiz, index }))
    .filter(({ index }) => !aus[index]);
}

function ortLabel(ort) {
  if (state.labels[ort.id] != null) return state.labels[ort.id];
  if (ort.teile) {
    const teile = aktiveTeile(ort).map(({ teil }) => sprachText(teil));
    return (teile.length ? teile : [sprachText(ort.label)]).join("\n");
  }
  return sprachText(ort.label);
}

function ortFarbe(ort) {
  return state.markerFarben[ort.id] || ort.farbe;
}

function ortFarbeHex(ort) {
  return MARKER_FARBEN[ortFarbe(ort)] || MARKER_FARBEN.rot;
}

function naechsteEigeneNummer() {
  const belegt = state.eigene.map((e) => parseInt(e.marker, 10));
  let nr = EIGENE_START_NR;
  while (belegt.includes(nr)) nr += 1;
  return nr;
}

// Fortlaufende Nummerierung: aktive Orte zählen in Legendenreihenfolge ab 1;
// Buchstabenmarken (Treppen, P) behalten ihre Buchstaben.
let nummern = {};

function nummernBerechnen() {
  nummern = {};
  let n = 1;
  alleOrte().filter(ortAktiv).forEach((ort) => {
    if (ort.art === "treppe" || !/^\d+$/.test(ort.marker)) return;
    nummern[ort.id] = String(n);
    n += 1;
  });
}

function ortMarker(ort) {
  return nummern[ort.id] || ort.marker;
}

// Beweglich sind der Infotisch und die eigenen Marken — alles andere
// ist fixiert (auch der barrierefreie Zugang: er sitzt am Südeingang).
// Ausnahme auf Zeit: Sektionen und Gärten stammen vom gequetschten
// Willkommensschild und dürfen von Hand justiert werden; ebenso die
// WCs und die Verkehrsmarken (Bushaltestelle von Hand gesetzt). Die
// justierten Lagen lassen sich exportieren und wandern in die Vorlage.
function ortJustierbar(ort) {
  return ort.kategorie === "sektionen" || ort.kategorie === "gaerten"
    || ort.kategorie === "verkehr" || ort.id.indexOf("wc-") === 0;
}

function ortBeweglich(ort) {
  // Gärten/Sektionen/WCs sind fixiert — verschiebbar nur im Backend-
  // Modus, um Überlagerungen auszugleichen (Feinlagen wandern dann
  // über den Lagen-Export in die Vorlage).
  return ort.id === "o4" || ort.art === "eigene"
    || (ortJustierbar(ort) && backendAktiv());
}

function justierteLagen() {
  // Nur echte Abweichungen von der Vorlage — bereits übernommene
  // Justagen (identische Lage) verstopfen den Export nicht mehr.
  const lagen = {};
  ORTE.forEach((ort) => {
    const p = state.positionen[ort.id];
    if (!ortJustierbar(ort) || !p) return;
    const vorlage = (ort.positionen || [])[0];
    if (vorlage && Math.abs(p[0] - vorlage[0]) < 0.05 && Math.abs(p[1] - vorlage[1]) < 0.05) return;
    lagen[ort.id] = p;
  });
  return lagen;
}

/* ---------- SVG-Bausteine der Szene ---------- */

function escapeXml(wert) {
  return String(wert)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Vorschübe der Laut-Glyphen in em (aus der TTF vermessen, upm 1000).
// Die Zeichen werden damit SELBST zentriert (Start-Anker, berechnete x) —
// text-anchor="middle" misst der PDF-Renderer sonst mit fremden Metriken,
// und zweistellige Zahlen rutschen im Druck nach links.
const LAUT_VORSCHUB = {
  "0": 0.615, "1": 0.433, "2": 0.553, "3": 0.563, "4": 0.603,
  "5": 0.577, "6": 0.609, "7": 0.539, "8": 0.62, "9": 0.609,
  "a": 0.509, "b": 0.508, "c": 0.402, "d": 0.509, "e": 0.463,
  "f": 0.324, "g": 0.479, "h": 0.518, "i": 0.239, "j": 0.239,
  "k": 0.475, "l": 0.24, "m": 0.789, "P": 0.546, "W": 0.858, "C": 0.497,
  "S": 0.503, "B": 0.563, "V": 0.553
};

function zentrierterText(x, y, text, groesse, farbe) {
  const zeichen = String(text).split("");
  if (!zeichen.every((z) => LAUT_VORSCHUB[z] != null)) {
    return `<text x="${x}" y="${y}" text-anchor="middle" font-size="${groesse}"`
      + ` fill="${farbe}" font-family="${SCHRIFT_ZAHL}">${escapeXml(text)}</text>`;
  }
  const gesamt = zeichen.reduce((summe, z) => summe + LAUT_VORSCHUB[z], 0) * groesse;
  let lauf = x - gesamt / 2;
  return zeichen.map((z) => {
    const teil = `<text x="${lauf.toFixed(3)}" y="${y}" font-size="${groesse}"`
      + ` fill="${farbe}" font-family="${SCHRIFT_ZAHL}">${escapeXml(z)}</text>`;
    lauf += LAUT_VORSCHUB[z] * groesse;
    return teil;
  }).join("");
}

// Symbol-Marken sind eine Spur grösser als Zahlkreise (Piktos brauchen
// Fläche); mehrere Piktos teilen sich eine Pille.
const SYMBOL_FAKTOR = 1.25;

function markenBreite(ort, r) {
  if (ort.legendeText) return 2 * r;      // Legende zeigt die Textmarke
  if (ort.symbol && ort.feldBreite) return ort.feldBreite * (r / 2.03);
  if (!ort.symbol || !Array.isArray(ort.symbol)) return 2 * r * (ort.symbol ? SYMBOL_FAKTOR : 1);
  const rr = r * SYMBOL_FAKTOR;
  return rr * 1.55 * (ort.symbol.length - 1) + 2 * rr;
}

function markenKreis(x, y, hex, text, r, symbol, feldBreite) {
  // Kreiszahl nach dem Sonderelement des Design-Systems (.step-num):
  // Hausschrift Laut, fester Kreis, Tintenmitte der Ziffern auf der
  // Kreismitte (ZIFFERN_SITZ). Grad = 0.5 × Durchmesser — eine Spur
  // kräftiger als die 0.72/1.6-Proportion, zweistellige Zahlen füllen
  // den Kreis, ohne ihn zu sprengen (Entscheid Auftraggeber, 8. Juli 2026).
  // Symbol-Marken (z. B. WCs) tragen Piktos statt Ziffer — einzeln im
  // grösseren Kreis, mehrere nebeneinander in einer Pille.
  if (symbol && feldBreite) {
    // Breites Feld (z. B. Toiletten): das fertige Gruppen-Icon läuft
    // eingepasst über die ganze Pille — Figuren bleiben erkennbar.
    const b = feldBreite * (r / 2.03);
    const h = r * 2.75;
    return `<rect x="${(x - b / 2).toFixed(3)}" y="${(y - h / 2).toFixed(3)}"`
      + ` width="${b.toFixed(3)}" height="${h.toFixed(3)}" rx="${(h / 2).toFixed(3)}" fill="${hex}" />`
      + symbolMarkup(symbol, x, y, b - h * 0.7, "#ffffff", h * 0.72);
  }
  if (symbol) {
    const symbole = Array.isArray(symbol) ? symbol : [symbol];
    const rr = r * SYMBOL_FAKTOR;
    if (symbole.length === 1) {
      // Das Pikto braucht Luft zum Kreisrand (Karte wie Liste) — 1.26 ×
      // Radius entspricht optisch dem Sitz der Ziffern im Zahlkreis.
      return `<circle cx="${x}" cy="${y}" r="${rr}" fill="${hex}" />`
        + symbolMarkup(symbole[0], x, y, rr * 1.26, "#ffffff");
    }
    const schritt = rr * 1.55;
    const breite = schritt * (symbole.length - 1) + 2 * rr;
    let aus = `<rect x="${(x - breite / 2).toFixed(3)}" y="${(y - rr).toFixed(3)}"`
      + ` width="${breite.toFixed(3)}" height="${(2 * rr).toFixed(3)}" rx="${rr}" fill="${hex}" />`;
    symbole.forEach((s, index) => {
      const cx = x + (index - (symbole.length - 1) / 2) * schritt;
      aus += symbolMarkup(s, cx, y, rr * 1.5, "#ffffff");
    });
    return aus;
  }
  const groesse = r;
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="${hex}" />`
    + zentrierterText(x, y + groesse * ZIFFERN_SITZ, text, groesse, "#ffffff");
}

function pfeilMarkup(x, y, r, hex, richtung) {
  // Richtungs-Pfeil = Original-Icon ‹pfeil-rechts-fett›, gedreht —
  // der fette Schnitt entspricht den Vorlagenpfeilen an den Aussenmarken.
  // Richtung wahlweise benannt oder als Gradzahl (z. B. entlang einer Strasse).
  const winkel = typeof richtung === "number"
    ? richtung
    : ({ rechts: 0, "unten-rechts": 45, "unten-links": 135 }[richtung] || 0);
  const abstand = r + 2.6;
  const dx = Math.cos(winkel * Math.PI / 180), dy = Math.sin(winkel * Math.PI / 180);
  return ikonMarkup("pfeil-rechts-fett", x + dx * abstand, y + dy * abstand, 4.4, hex, winkel);
}

/* Treppen- und Lift-Badges: exakte Vektorgeometrie der Vorlage
   (Karten-mit-spezifischen-Lokalisierungen, Kartenmarken Seite 2 —
   badge-lokal in mm ausgelesen, Zentrum = Kreis- bzw. Boxmitte).
   Treppe: weisser Kreis r 2.39, Zickzack-Lauflinie 1.2 pt, Buchstabe
   oben links als Original-Pfad. Lift: weisses Rundrechteck, Doppel-
   Chevron 1.2 pt, Buchstabe mittig. Legende = 0.85-fach mit Ring 0.25 pt. */
const BADGE_STRICH = 0.4247;   // 1.204 pt der Vorlage in mm
const BADGE_RING = 0.088;      // 0.25 pt Legenden-Ring in mm
const TREPPEN_BADGES = {
  M: {
    zug: "M-1.633 .998 H-.527 V.043 H.519 V-.911 H1.63",
    buchstabe: "M-1.26 -.478 H-1.024 V-1.377 H-.999 L-.771 -.529 H-.535 L-.307 -1.377 H-.282 V-.478 H-.046 V-1.64 H-.448 L-.653 -.793 L-.858 -1.64 H-1.26 Z"
  },
  N: {
    zug: "M-1.567 .858 H-.461 V-.097 H.585 V-1.051 H1.696",
    buchstabe: "M-1.085 -.653 H-.818 V-1.738 H-.799 L-.47 -.653 H-.03 V-1.97 H-.297 V-.886 H-.317 L-.634 -1.97 H-1.085 Z"
  },
  S: {
    zug: "M-1.861 .965 H-.755 V.01 H.291 V-.944 H1.402",
    buchstabe: "M-.34 -1.868 C-.34 -1.868 -.568 -1.917 -.725 -1.917 C-.962 -1.917 -1.123 -1.806 -1.123 -1.546 C-1.123 -1.346 -1.023 -1.25 -.761 -1.17 C-.592 -1.118 -.551 -1.083 -.551 -1.006 C-.551 -.909 -.606 -.844 -.734 -.844 C-.856 -.844 -1.086 -.877 -1.086 -.877 L-1.11 -.681 C-1.11 -.681 -.88 -.624 -.72 -.624 C-.489 -.624 -.316 -.751 -.316 -1.022 C-.316 -1.23 -.393 -1.306 -.646 -1.392 C-.842 -1.458 -.888 -1.486 -.888 -1.565 C-.888 -1.648 -.828 -1.697 -.701 -1.697 C-.601 -1.697 -.359 -1.668 -.359 -1.668 L-.34 -1.868 Z"
  }
};
const LIFT_BADGES = {
  N: {
    chevrons: "M-.778 -.91 L.032 -1.54 L.842 -.91 M.842 1.123 L.032 1.753 L-.778 1.123",
    buchstabe: "M-.444 .724 H-.212 V-.219 H-.195 L.092 .724 H.474 V-.421 H.242 V.522 H.225 L-.051 -.421 H-.444 Z"
  },
  S: {
    chevrons: "M-.798 -.683 L.013 -1.313 L.822 -.683 M.823 1.35 L.012 1.98 L-.798 1.35",
    buchstabe: "M.375 -.238 C.375 -.237 .147 -.287 -.009 -.287 C-.246 -.287 -.408 -.175 -.408 .084 C-.408 .284 -.308 .38 -.045 .461 C.123 .512 .164 .547 .164 .624 C.164 .722 .109 .786 -.018 .786 C-.14 .786 -.37 .753 -.37 .753 L-.394 .949 C-.394 .949 -.164 1.006 -.004 1.006 C.226 1.006 .399 .879 .399 .608 C.399 .4 .322 .325 .07 .238 C-.126 .172 -.172 .145 -.172 .066 C-.172 -.017 -.112 -.067 .015 -.067 C.114 -.067 .356 -.037 .356 -.037 L.375 -.238 Z"
  }
};

function treppenBadge(x, y, buchstabe, form, hex, mitRand) {
  const farbe = hex || MARKER_FARBEN.rot;
  const skala = mitRand ? 0.85 : 1;    // Legende wie die Vorlage kleiner
  const ring = mitRand ? ` stroke="${farbe}" stroke-width="${(BADGE_RING / skala).toFixed(3)}"` : "";
  const strich = `fill="none" stroke="${farbe}" stroke-width="${BADGE_STRICH}"`;
  let kern;
  if (form === "lift") {
    const b = LIFT_BADGES[buchstabe] || LIFT_BADGES.N;
    const mitte = buchstabe === "S" ? 0.334 : 0.107;  // Chevron-Mitte der Vorlage
    kern = `<rect x="-1.33" y="${(mitte - 2.45).toFixed(3)}" width="2.66" height="4.9" rx="0.26" fill="#ffffff"${ring} />`
      + `<path d="${b.chevrons}" ${strich} />`
      + `<path d="${b.buchstabe}" fill="${farbe}" />`;
  } else {
    const b = TREPPEN_BADGES[buchstabe] || TREPPEN_BADGES.M;
    kern = `<circle cx="0" cy="0" r="2.39" fill="#ffffff"${ring} />`
      + `<path d="${b.zug}" ${strich} />`
      + `<path d="${b.buchstabe}" fill="${farbe}" />`;
  }
  return `<g transform="translate(${x} ${y})${skala === 1 ? "" : ` scale(${skala})`}">${kern}</g>`;
}

// Gebäudenamen in der Hausschrift (Deutlich), optisch mittig in die Fläche
// gesetzt (Anker = Flächenmitte).
const GEBAEUDE_LABELS = [
  { text: "Goetheanum", x: 198.6, y: 115.0, groesse: 4.23, winkel: 0 },
  { text: "Schreinerei", x: 224.4, y: 93.2, groesse: 3.18, winkel: -76 }
];

// Textbreite in mm — die Labels werden start-verankert selbst zentriert.
// text-anchor="middle" misst der PDF-Renderer mit fremden Metriken, und
// die Namen verrutschen im Druck. Erste Quelle ist die Vorschubtabelle
// (aus der TTF vermessen, upm 1000) — sie ist ladeunabhängig; die Canvas-
// Messung bleibt Rückfall für Zeichen ausserhalb der Tabelle, misst aber
// falsch, solange die Webschrift (noch) nicht geladen ist.
const DEUTLICH_VORSCHUB = {
  "G": 0.573, "S": 0.502, "a": 0.504, "c": 0.401, "e": 0.459, "h": 0.512,
  "i": 0.228, "m": 0.785, "n": 0.512, "o": 0.486, "r": 0.323, "t": 0.328,
  "u": 0.513
};

let messKontext = null;

function textBreiteMm(text, familie, groesseMm) {
  const zeichen = String(text).split("");
  if (familie === SCHRIFT_SPRACHE && zeichen.every((z) => DEUTLICH_VORSCHUB[z] != null)) {
    return zeichen.reduce((summe, z) => summe + DEUTLICH_VORSCHUB[z], 0) * groesseMm;
  }
  if (!messKontext) messKontext = document.createElement("canvas").getContext("2d");
  messKontext.font = `100px ${familie}`;
  return messKontext.measureText(text).width / 100 * groesseMm;
}

function gebaeudeLabelMarkup() {
  return GEBAEUDE_LABELS.map((l) => {
    const drehung = l.winkel ? ` transform="rotate(${l.winkel} ${l.x} ${l.y})"` : "";
    const links = l.x - textBreiteMm(l.text, SCHRIFT_SPRACHE, l.groesse) / 2;
    return `<text x="${links.toFixed(3)}" y="${l.y}" font-size="${l.groesse}" fill="#ffffff"`
      + ` font-family="${SCHRIFT_SPRACHE}"${drehung}>${escapeXml(l.text)}</text>`;
  }).join("");
}

function ortPositionen(ort) {
  if (state.positionen[ort.id]) return [state.positionen[ort.id]];
  return ort.positionen || [];
}

function ortMarkup(ort) {
  const hex = ortFarbeHex(ort);
  let teile = "";
  if (ort.art === "treppe") {
    const liftAktiv = aktiveNotizen(ort).some(({ notiz }) => notiz.badge === "lift");
    const verschoben = state.positionen[ort.id];
    (ort.badges || []).forEach((b, index) => {
      if (b.form === "lift" && !liftAktiv) return;
      const basis = verschoben
        ? [verschoben[0] + (b.x - ort.badges[0].x), verschoben[1] + (b.y - ort.badges[0].y)]
        : [b.x, b.y];
      const [x, y] = anp(basis[0], basis[1]);
      teile += treppenBadge(x, y, ort.marker, b.form, hex);
    });
    return teile;
  }
  ortPositionen(ort).forEach(([px, py]) => {
    const [x, y] = anp(px, py);
    teile += markenKreis(x, y, hex, ortMarker(ort), 2.03, ort.symbol, ort.feldBreite);
    if (ort.pfeil) teile += pfeilMarkup(x, y, 2.03, hex, ort.pfeil);
  });
  return teile;
}

/* ---------- Legende ---------- */

const LEGENDE_NORMAL = {
  spaltenX: [12.53, 64.28],
  startOhneTitel: 14.0,
  startMitTitel: 26.0,     // Luft unter dem Veranstaltungstitel
  zeile: 5.66,
  notiz: 4.7,
  extraZeile: 4.2,
  gruppe: 5.0,
  labelAbstand: 4.2,
  labelGroesse: 3.35,      // wie die Vorlage: Titelschnitt 9.5 pt
  notizGroesse: 3.0
};
// Kompakte Legende: gewinnt Platz bei vielen Orten (kleinerer Grad,
// engere Zeilen — fürs Druckblatt, nicht für Bildschirm-UI).
const LEGENDE_KOMPAKT = {
  ...LEGENDE_NORMAL,
  zeile: 4.9, notiz: 4.1, extraZeile: 3.7, gruppe: 4.0,
  labelGroesse: 2.9, notizGroesse: 2.6
};

function LEGENDE_LAYOUT_aktiv() {
  return state.kompakt ? LEGENDE_KOMPAKT : LEGENDE_NORMAL;
}

// Wird von legendeMarkup gesetzt: Zeilen passen nicht mehr aufs Blatt.
let legendeUeberlauf = false;

function legendeZeilen() {
  const L = LEGENDE_LAYOUT_aktiv();
  const zeilen = [];
  let vorher = null;
  const namen = {};
  KATEGORIEN.forEach((k) => { namen[k.id] = k.name; });
  const aktive = alleOrte().filter(ortAktiv);
  // Gruppenköpfe nur, wenn mehr als eine Kategorie vertreten ist —
  // eine kleine Karte mit drei Orten braucht keine Zwischenzeile.
  const kategorien = new Set(aktive.map((o) => o.kategorie || "eigene"));
  const mitKoepfen = kategorien.size > 1;
  aktive.forEach((ort) => {
    const kategorie = ort.kategorie || "eigene";
    // Gleiche Zeilen zusammenlegen: zwei Toiletten-Marker auf der Karte
    // brauchen nur EINE Legendenzeile (gleicher Text, gleiche Marke).
    if (vorher && (vorher.kategorie || "eigene") === kategorie
      && ortLabel(vorher) === ortLabel(ort)
      && (vorher.legendeText || vorher.marker) === (ort.legendeText || ort.marker)) {
      vorher = ort;
      return;
    }
    if (mitKoepfen && (!vorher || (vorher.kategorie || "eigene") !== kategorie)) {
      if (vorher) zeilen.push({ typ: "abstand", hoehe: L.gruppe * 0.6 });
      // Eigene (veranstaltungsspezifische) Marken beginnen in Spalte 2 —
      // klar getrennt vom Standard-Inventar der Karte.
      if (ort.art === "eigene" && (!vorher || vorher.art !== "eigene")) {
        zeilen.push({ typ: "umbruch" });
      }
      const eigener = state.eigeneTitel.trim();
      const name = ort.art === "eigene"
        ? (eigener ? { de: eigener, en: eigener } : { de: "Eigene Marken", en: "Own Markers" })
        : namen[kategorie];
      if (name) zeilen.push({ typ: "kopf", text: sprachText(name), hoehe: L.zeile });
    } else if (vorher && vorher.art === "treppe" && ort.art === "treppe") {
      zeilen.push({ typ: "abstand", hoehe: L.gruppe });
    }
    const zeilenTexte = ortLabel(ort).split("\n");
    zeilen.push({
      typ: "ort", ort, zeilenTexte,
      hoehe: L.zeile + (zeilenTexte.length - 1) * L.extraZeile
    });
    if (ort.art === "treppe") {
      aktiveNotizen(ort).forEach(({ notiz }) => {
        zeilen.push({ typ: "notiz", notiz, ort, hoehe: L.notiz });
      });
    }
    vorher = ort;
  });
  return zeilen;
}

function legendeMarkup() {
  // Fliess-Layout: erst füllt sich Spalte 1, dann Spalte 2 —
  // die Spaltenzuteilung der Vorlage gilt nicht mehr.
  const L = LEGENDE_LAYOUT_aktiv();
  let start = state.titel.trim() ? L.startMitTitel : L.startOhneTitel;
  if (state.titel.trim() && state.untertitel.trim()) start += 5.2;
  if (state.titelLogo) {
    // Luft unter dem Sonderlogo (und ggf. dem Untertitel darunter).
    start = 5.5 + titelLogoHoehe() + (state.untertitel.trim() ? 5.6 + 4 : 0) + 9;
  }
  const untergrenze = SZENE.hoehe - 12;
  let teile = "";
  let spalte = 0;
  let y = start;
  legendeUeberlauf = false;
  legendeZeilen().forEach((zeile) => {
    // Gruppenköpfe binden sich an ihren ersten Eintrag: reicht der Platz
    // nicht für Kopf UND eine Zeile, bricht die Spalte vor dem Kopf um.
    if (zeile.typ === "umbruch") {
      // manueller Spaltenwechsel (eigene Marken beginnen in Spalte 2)
      if (spalte < L.spaltenX.length - 1) { spalte += 1; y = start; }
      return;
    }
    const bedarf = zeile.hoehe + (zeile.typ === "kopf" ? L.zeile : 0);
    if (zeile.typ !== "abstand" && y + bedarf > untergrenze && spalte < L.spaltenX.length - 1) {
      spalte += 1;
      y = start;
    }
    if (zeile.typ !== "abstand" && y + zeile.hoehe > untergrenze) legendeUeberlauf = true;
    const x = L.spaltenX[spalte];
    if (zeile.typ === "abstand") { y += zeile.hoehe; return; }
    if (zeile.typ === "kopf") {
      // Gruppenname der Kategorie — Sprache, darum Hausschrift; beginnt
      // auf der Einrückung der Ortsnamen. Unterschieden wird mit GENAU
      // einem Merkmal (G01): leiser (TINTE_LEISE, gerechnet B02-fest) —
      // gleicher Grad wie die Einträge.
      teile += `<text x="${x + L.labelAbstand}" y="${y}" font-size="${L.labelGroesse}"`
        + ` fill="${TINTE_LEISE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(zeile.text)}</text>`;
      y += zeile.hoehe;
      return;
    }
    if (zeile.typ === "notiz") {
      const n = zeile.notiz;
      if (n.badge === "lift") {
        teile += treppenBadge(x, y - 0.9, zeile.ort.marker, "lift", ortFarbeHex(zeile.ort), true);
      }
      teile += `<text x="${x + L.labelAbstand}" y="${y}" font-size="${L.notizGroesse}"`
        + ` fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(sprachText(n))}</text>`;
      y += zeile.hoehe;
      return;
    }
    const ort = zeile.ort;
    const hex = ortFarbeHex(ort);
    let textX = x + L.labelAbstand;
    if (ort.art === "treppe") {
      teile += treppenBadge(x, y - 0.9, ort.marker, "treppe", hex, true);
    } else {
      // Breite Symbol-Pillen linksbündig zur Spalte, Text weicht aus;
      // Orte mit legendeText (Toiletten) zeigen in der Liste die
      // schlichte Textmarke statt des Kartenfelds. Symbol-Marken laufen
      // in der Liste im GLEICHEN Kreisdurchmesser wie die Zahlkreise —
      // der Grössenzuschlag (SYMBOL_FAKTOR) gilt nur auf der Karte.
      const symbol = ort.legendeText ? null : ort.symbol;
      const r = symbol ? 2.03 / SYMBOL_FAKTOR : 2.03;
      const b = markenBreite(ort, r);
      teile += markenKreis(x - 2.03 + b / 2, y - 0.9, hex,
        ort.legendeText || ortMarker(ort), r, symbol);
      textX = x + Math.max(L.labelAbstand, b - 2.03 + 1.6);
    }
    zeile.zeilenTexte.forEach((text, index) => {
      teile += `<text x="${textX}" y="${y + index * L.extraZeile}"`
        + ` font-size="${L.labelGroesse}" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(text)}</text>`;
    });
    y += zeile.hoehe;
  });
  return teile;
}

/* ---------- Szene ---------- */

function kompassMarkup() {
  // Kompassrose = Icon ‹kompass-2› (Icons v2.7), weiss wie in der Vorlage.
  // Platzierung aus dem LT25-Original gemessen: Nadel 174.6–187.5 mm,
  // Mitte (181.05, 34.0); Icon-Nadel liegt bei x 248–761, y-Mitte -500.
  if (!kompassInhalt) return "";
  const skala = 12.9 / 513;
  const tx = 181.05 - skala * 504.5;
  const ty = 34.0 + skala * 500;
  return `<g transform="translate(${tx} ${ty}) scale(${skala})" fill="#ffffff">${kompassInhalt}</g>`;
}

// Standardlage des Campus-Logos: vom Auftraggeber eingemessen und fixiert
// (8. Juli 2026) — Mitte 274.1 × 12.2 mm, Breite 31.7 mm (24 mm × 132 %).
// Für andere Anschnitte bleibt die Justage als Backend-Funktion (#justage).
const LOGO_STANDARD = { x: 274.1, y: 12.2, breite: 31.7 };

// Sonderlogo statt Titel (Backend-Funktion): hochgeladenes SVG links
// oben; reine Pfade empfohlen — Text im SVG braucht eingebettete Schriften.
function titelLogoMarkup() {
  const l = state.titelLogo;
  if (!l) return "";
  const skala = l.breite / l.vbBreite;
  const vx = l.vbX || 0, vy = l.vbY || 0;
  return `<g transform="translate(${(10.5 - vx * skala).toFixed(3)} ${(5.5 - vy * skala).toFixed(3)}) scale(${skala.toFixed(5)})">${l.markup}</g>`;
}

function titelLogoHoehe() {
  const l = state.titelLogo;
  return l ? l.breite * l.vbHoehe / l.vbBreite : 0;
}

function logoMarkup() {
  if (!logoInhalt) return "";
  const breite = LOGO_STANDARD.breite * state.logo.skala;
  const hoehe = breite * logoInhalt.hoehe / logoInhalt.breite;
  const skala = breite / logoInhalt.breite;
  const mx = state.logo.x != null ? state.logo.x : LOGO_STANDARD.x;
  const my = state.logo.y != null ? state.logo.y : LOGO_STANDARD.y;
  return `<g transform="translate(${(mx - breite / 2).toFixed(2)} ${(my - hoehe / 2).toFixed(2)}) scale(${skala})">${logoInhalt.markup}</g>`;
}

function szeneMarkup(anschnitt) {
  const b = anschnitt || 0;
  const g = KARTE.gelaende;
  const skala = g.breite / gelaendeMasse.breite;
  const a = state.ausschnitt;
  const titel = state.titel.trim();
  nummernBerechnen();
  const marker = alleOrte().filter(ortAktiv).map(ortMarkup).join("");
  return `
    <defs>
      <clipPath id="blatt-clip">
        <rect x="${-b}" y="${-b}" width="${SZENE.breite + 2 * b}" height="${SZENE.hoehe + 2 * b}" />
      </clipPath>
      ${wieseClipMarkup()}
    </defs>
    <rect x="${-b}" y="${-b}" width="${SZENE.breite + 2 * b}" height="${SZENE.hoehe + 2 * b}" fill="#ffffff" />
    <g clip-path="url(#blatt-clip)">
      <g transform="translate(${a.dx} ${a.dy}) scale(${a.skala})">
        <g id="gelaende" transform="translate(${g.x} ${g.y}) scale(${skala})">${gelaendeMarkup()}</g>
        ${gebaeudeLabelMarkup()}
        ${kompassMarkup()}
      </g>
      ${marker}
    </g>
    ${state.titelLogo
      ? titelLogoMarkup()
        + (state.untertitel.trim() ? `<text x="10.5" y="${(5.5 + titelLogoHoehe() + 5.6).toFixed(2)}" font-size="3.35" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(state.untertitel.trim())}</text>` : "")
      : (titel ? `<text x="10.5" y="14.2" font-size="5.3" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(titel)}</text>` : "")
        + (titel && state.untertitel.trim() ? `<text x="10.5" y="20.2" font-size="3.35" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(state.untertitel.trim())}</text>` : "")}
    ${legendeMarkup()}
    ${logoMarkup()}
  `;
}

// Schnittmarken: 0.25 pt Haarlinien in reinem Druckschwarz (Produktions-
// artefakt wie die weisse Blattfläche — # ds-ok-Logik, kein Theme-Wert).
function schnittmarkenMarkup(breite, hoehe, beschnitt, laenge) {
  const b = beschnitt, e = beschnitt + laenge, s = 'stroke="#000000" stroke-width="0.088"';
  const l = (x1, y1, x2, y2) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ${s} />`;
  return l(-e, 0, -b, 0) + l(0, -e, 0, -b)
    + l(breite + b, 0, breite + e, 0) + l(breite, -e, breite, -b)
    + l(-e, hoehe, -b, hoehe) + l(0, hoehe + b, 0, hoehe + e)
    + l(breite + b, hoehe, breite + e, hoehe) + l(breite, hoehe + b, breite, hoehe + e);
}

/* ---------- Vorschau ---------- */

const printSvg = document.getElementById("print-svg");
const paperStage = document.getElementById("paper-stage");
const previewNote = document.getElementById("preview-note");

function renderVorschau() {
  const marken = state.beschnitt && state.marken;
  if (marken) {
    printSvg.setAttribute("viewBox", "-8 -8 313 226");
    paperStage.style.aspectRatio = "313 / 226";
    printSvg.innerHTML = szeneMarkup(3)
      + schnittmarkenMarkup(SZENE.breite, SZENE.hoehe, 3, 5)
      + `<rect x="0" y="0" width="${SZENE.breite}" height="${SZENE.hoehe}" fill="none" stroke="${TINTE}" stroke-opacity="0.35" stroke-width="0.15" stroke-dasharray="2 1.4" />`;
  } else {
    printSvg.setAttribute("viewBox", `0 0 ${SZENE.breite} ${SZENE.hoehe}`);
    paperStage.style.aspectRatio = "297 / 210";
    printSvg.innerHTML = szeneMarkup(0);
  }
  const format = state.format === "a3" ? "A3 quer (420 × 297)" : "A4 quer (297 × 210)";
  previewNote.textContent = marken
    ? `${format} · gestrichelt = Endformat, aussen Beschnitt und Schnittmarken.`
    : `${format} · Vorschau im Endformat.`;
  if (legendeUeberlauf) {
    previewNote.textContent += state.kompakt
      ? " ⚠ Legende voll — bitte Orte reduzieren."
      : " ⚠ Legende voll — kompakte Legende einschalten oder Orte reduzieren.";
  }
  printSvg.classList.toggle("platzieren", Boolean(state.platzieren || state.platzierenOrt || state.platzierenLogo));
}

/* ---------- Seitenleiste ---------- */

const orteGruppen = document.getElementById("orte-gruppen");
const eigeneListe = document.getElementById("eigene-liste");
const eigeneHint = document.getElementById("eigene-hint");
const farbRollen = document.getElementById("farb-rollen");

// Kategorien aus orte.js (kuratierte Reihenfolge = Legenden-Sortierung).
const GRUPPEN = KATEGORIEN.map((k) => [k.id, k.name, (o) => o.kategorie === k.id]);

function farbeWeiterschalten(ort) {
  const aktuelle = ortFarbe(ort);
  const naechste = FARB_ZYKLUS[(FARB_ZYKLUS.indexOf(aktuelle) + 1) % FARB_ZYKLUS.length];
  if (ort.art === "eigene") {
    const eintrag = state.eigene.find((e) => e.id === ort.id);
    if (eintrag) eintrag.farbe = naechste;
  } else if (naechste === ort.farbe) {
    delete state.markerFarben[ort.id];
  } else {
    state.markerFarben[ort.id] = naechste;
  }
  render();
}

function ortZeile(ort, loeschbar) {
  const zeile = document.createElement("div");
  const an = ortAktiv(ort);
  zeile.className = "object-row" + (an ? "" : " aus");

  // Häkchen am Zeilenanfang: eindeutig ‹auf der Karte / nicht auf der Karte›.
  const haken = document.createElement("span");
  haken.className = "check" + (an ? " an" : "");
  haken.textContent = an ? "✓" : "";
  zeile.appendChild(haken);

  if (state.bearbeiten === ort.id) {
    const eingabe = document.createElement("input");
    eingabe.type = "text";
    eingabe.className = "label-edit";
    eingabe.value = ortLabel(ort).replace(/\n/g, " / ");
    const uebernehmen = () => {
      if (state.bearbeiten !== ort.id) return; // ‹Esc› hat schon abgebrochen
      const wert = eingabe.value.trim();
      state.bearbeiten = null;
      if (ort.art === "eigene") {
        const eintrag = state.eigene.find((e) => e.id === ort.id);
        if (eintrag && wert) eintrag.label = wert;
      } else if (!wert || wert === sprachText(ort.label).replace(/\n/g, " / ")) {
        delete state.labels[ort.id];
      } else {
        state.labels[ort.id] = wert;
      }
      render();
    };
    eingabe.addEventListener("keydown", (e) => {
      if (e.key === "Enter") uebernehmen();
      if (e.key === "Escape") { state.bearbeiten = null; render(); }
    });
    eingabe.addEventListener("blur", uebernehmen);
    zeile.appendChild(eingabe);
    setTimeout(() => eingabe.focus(), 0);
    return zeile;
  }

  const titelSpan = document.createElement("span");
  titelSpan.className = "object-title";
  titelSpan.textContent = ortLabel(ort).replace(/\n/g, " / ");
  zeile.appendChild(titelSpan);

  const markerSpan = document.createElement("span");
  markerSpan.className = "object-marker";
  markerSpan.textContent = ortAktiv(ort) ? ortMarker(ort) : "–";
  zeile.appendChild(markerSpan);

  // Eigene Marken tragen viele Knöpfe (Farbe, ✥, ▲▼, ✕) — die Zeile
  // bricht dafür in zwei Zeilen um: oben Titel, unten die Werkzeuge.
  if (loeschbar) {
    zeile.classList.add("zweizeilig");
    const umbruch = document.createElement("span");
    umbruch.className = "zeilen-umbruch";
    zeile.appendChild(umbruch);
  }

  const farbKnopf = document.createElement("button");
  farbKnopf.type = "button";
  farbKnopf.className = "row-btn";
  farbKnopf.title = "Markerfarbe wechseln (Rot → Blau → Grün → Grau → Gold)";
  const punkt = document.createElement("span");
  punkt.className = "object-dot";
  punkt.style.background = ortFarbeHex(ort);
  farbKnopf.appendChild(punkt);
  farbKnopf.addEventListener("click", (e) => {
    e.stopPropagation();
    farbeWeiterschalten(ort);
  });
  zeile.appendChild(farbKnopf);

  if (ortBeweglich(ort)) {
    const verschieben = document.createElement("button");
    verschieben.type = "button";
    verschieben.className = "row-btn";
    verschieben.title = "Marke auf der Karte verschieben";
    verschieben.textContent = "✥";
    verschieben.addEventListener("click", (e) => {
      e.stopPropagation();
      state.an[ort.id] = true;
      state.platzierenOrt = ort.id;
      state.platzieren = null;
      renderVorschau();
      eigeneHint.textContent = `‹${ortLabel(ort).split("\n")[0]}› — neue Stelle in der Vorschau anklicken. ‹Esc› bricht ab.`;
      printSvg.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
    zeile.appendChild(verschieben);
  }

  if (loeschbar) {
    // Reihenfolge der eigenen Marken = Reihenfolge in der Legende;
    // ▲/▼ sortieren nachträglich.
    const schieben = (richtung) => (e) => {
      e.stopPropagation();
      const index = state.eigene.findIndex((eintrag) => eintrag.id === ort.id);
      const ziel = index + richtung;
      if (index < 0 || ziel < 0 || ziel >= state.eigene.length) return;
      const [eintrag] = state.eigene.splice(index, 1);
      state.eigene.splice(ziel, 0, eintrag);
      render();
    };
    [["▲", -1, "In der Legende nach oben"], ["▼", 1, "In der Legende nach unten"]].forEach(([zeichen, richtung, titelText]) => {
      const knopf = document.createElement("button");
      knopf.type = "button";
      knopf.className = "row-btn";
      knopf.title = titelText;
      knopf.textContent = zeichen;
      knopf.addEventListener("click", schieben(richtung));
      zeile.appendChild(knopf);
    });
    const weg = document.createElement("button");
    weg.type = "button";
    weg.className = "row-btn";
    weg.title = "Marke entfernen";
    weg.textContent = "✕";
    weg.addEventListener("click", (e) => {
      e.stopPropagation();
      state.eigene = state.eigene.filter((eintrag) => eintrag.id !== ort.id);
      render();
    });
    zeile.appendChild(weg);
  }

  // Klick schaltet den Ort; Doppelklick (versteckte Option) ändert die
  // Beschriftung. Der Schaltklick wartet kurz, damit der zweite Klick den
  // ersten noch abfangen kann — sonst baut render() die Zeile schon neu.
  let klickTimer = null;
  zeile.title = "Klick: auf die Karte / herunter. Doppelklick: Beschriftung ändern.";
  zeile.addEventListener("click", (e) => {
    if (e.detail === 2) {
      clearTimeout(klickTimer);
      klickTimer = null;
      state.bearbeiten = ort.id;
      render();
      return;
    }
    if (e.detail > 2 || klickTimer) return;
    klickTimer = setTimeout(() => {
      if (state.an[ort.id]) delete state.an[ort.id];
      else state.an[ort.id] = true;
      render();
    }, 280);
  });
  return zeile;
}

// Unterzeilen für Teil-Orte (z. B. Speisehaus-Gruppe) und Treppen-Etagen:
// einzeln zu- und abschaltbar, eingerückt unter der Hauptzeile.
function unterZeile(ort, sammlung, index, text) {
  const zeile = document.createElement("div");
  const aus = (state[sammlung][ort.id] || {})[index];
  zeile.className = "object-row object-sub" + (aus ? " aus" : "");
  const platz = document.createElement("span");
  platz.className = "object-dot sub-dot" + (aus ? "" : " an");
  zeile.appendChild(platz);
  const titelSpan = document.createElement("span");
  titelSpan.className = "object-title";
  titelSpan.textContent = text;
  zeile.appendChild(titelSpan);
  zeile.addEventListener("click", (e) => {
    e.stopPropagation();
    const eintraege = state[sammlung][ort.id] || {};
    if (eintraege[index]) delete eintraege[index];
    else eintraege[index] = true;
    state[sammlung][ort.id] = eintraege;
    render();
  });
  return zeile;
}

function ortMitUnterzeilen(ort, loeschbar) {
  const halter = document.createDocumentFragment();
  halter.appendChild(ortZeile(ort, loeschbar));
  if (state.an[ort.id]) {
    (ort.teile || []).forEach((teil, index) => {
      halter.appendChild(unterZeile(ort, "teileAus", index, sprachText(teil)));
    });
    if (ort.art === "treppe") {
      (ort.notizen || []).forEach((notiz, index) => {
        halter.appendChild(unterZeile(ort, "notizenAus", index, sprachText(notiz)));
      });
    }
  }
  return halter;
}

// Hauptkategorien einklappbar — Übersicht in den Editing-Werkzeugen;
// zugeklappt zeigt der Kopf, wie viele Orte aktiv sind.
// Die erste Kategorie startet geöffnet (Beispiel für Erstnutzer).
const aufgeklappt = {};
GRUPPEN.forEach(([id], index) => { aufgeklappt[id] = index === 0; });
let gebaeudeAufgeklappt = false;

// Gruppenkopf mit Sammelschalter: ein Klick aktiviert bzw. deaktiviert
// alle Einträge der Kategorie (‹Auch Kategorienweise!›).
function gruppenKopf(kopfKnopf, kannAn, schalten) {
  const zeile = document.createElement("div");
  zeile.className = "group-head";
  zeile.appendChild(kopfKnopf);
  const schalter = document.createElement("button");
  schalter.type = "button";
  schalter.className = "group-toggle";
  schalter.textContent = kannAn ? "alle an" : "alle aus";
  schalter.title = kannAn
    ? "Alle Einträge dieser Gruppe aktivieren"
    : "Alle Einträge dieser Gruppe deaktivieren";
  schalter.addEventListener("click", (e) => {
    e.stopPropagation();
    schalten(kannAn);
  });
  zeile.appendChild(schalter);
  return zeile;
}

// Suche über alle Kategorien (die Ortsliste ist inzwischen lang):
// trifft Beschriftung (beide Sprachen, samt Umbenennung), Teil-Orte
// und Markerzeichen. Während der Suche öffnen sich die Treffer-Gruppen.
let orteSuchbegriff = "";

function ortPasstZurSuche(ort) {
  const texte = [ortLabel(ort), ort.marker || ""];
  if (ort.label && typeof ort.label === "object") texte.push(ort.label.de || "", ort.label.en || "");
  (ort.teile || []).forEach((teil) => texte.push(teil.de || "", teil.en || ""));
  return texte.join("\n").toLowerCase().includes(orteSuchbegriff);
}

function renderOrte() {
  document.querySelectorAll("#sprache-row [data-sprache]").forEach((knopf) => {
    knopf.setAttribute("aria-pressed", knopf.dataset.sprache === state.sprache ? "true" : "false");
  });
  orteGruppen.innerHTML = "";
  GRUPPEN.forEach(([id, name, filter]) => {
    let eintraege = ORTE.filter(filter);
    if (orteSuchbegriff) eintraege = eintraege.filter(ortPasstZurSuche);
    if (!eintraege.length) return; // leere Kategorien nicht anbieten
    const gruppe = document.createElement("div");
    const aktiv = eintraege.filter(ortAktiv).length;
    const offen = orteSuchbegriff ? true : aufgeklappt[id];

    const kopf = document.createElement("button");
    kopf.type = "button";
    kopf.className = "object-group-title";
    kopf.setAttribute("aria-expanded", offen ? "true" : "false");
    kopf.innerHTML = `<span class="chevron">${offen ? "▾" : "▸"}</span>`
      + `<span>${sprachText(name)}</span>`
      + `<span class="zaehler">${aktiv ? `${aktiv} aktiv` : ""}</span>`;
    kopf.addEventListener("click", () => {
      aufgeklappt[id] = !offen;
      renderOrte();
    });
    gruppe.appendChild(gruppenKopf(kopf, eintraege.length > aktiv, (an) => {
      eintraege.forEach((ort) => {
        if (an) state.an[ort.id] = true;
        else delete state.an[ort.id];
      });
      render();
    }));

    if (offen) {
      const liste = document.createElement("div");
      liste.className = "object-list";
      eintraege.forEach((ort) => liste.appendChild(ortMitUnterzeilen(ort, false)));
      gruppe.appendChild(liste);
    }
    orteGruppen.appendChild(gruppe);
  });

  eigeneListe.innerHTML = "";
  alleOrte().filter((o) => o.art === "eigene").forEach((ort) => {
    eigeneListe.appendChild(ortZeile(ort, true));
  });

  renderGebaeude();
}

/* ---------- Campus-Gebäude (aktiv/passiv) ---------- */

// Benannte Gebäude-Einheiten: Name = erster zugeordneter Ort;
// Goetheanum, Schreinerei und der Halde-Komplex tragen eigene Namen
// (Halde und Puppentheater sind zwei ineinander gebaute Gebäude).
const BAU_NAMEN = { "goetheanum-bau": { de: "Goetheanum", en: "Goetheanum" },
  "campusbau-19": { de: "Schreinerei", en: "Schreinerei" },
  "campusbau-41": { de: "Rudolf Steiner Halde", en: "Rudolf Steiner Halde" },
  "campusbau-6": { de: "Puppentheater Felicia", en: "Puppet Theatre Felicia" },
  // Sitz der Sektion für Sozialwissenschaften, auch Seminarhaus.
  "campusbau-9": { de: "Kristallisationslabor", en: "Kristallisationslabor" } };

function gebaeudeEinheiten() {
  const einheiten = new Map();
  alleOrte().forEach((ort) => {
    ortGebaeude(ort, true).forEach((g) => {
      const einheit = bauEinheit(g);
      if (!einheiten.has(einheit)) {
        einheiten.set(einheit, BAU_NAMEN[einheit] || ort.label);
      }
    });
  });
  return einheiten;
}

function renderGebaeude() {
  const halter = document.getElementById("gebaeude-liste");
  halter.innerHTML = "";
  const kopf = document.createElement("button");
  kopf.type = "button";
  kopf.className = "object-group-title";
  const einheiten = gebaeudeEinheiten();
  const aktiv = [...einheiten.keys()].filter((e) => bauAktiv(e)).length;
  kopf.innerHTML = `<span class="chevron">${gebaeudeAufgeklappt ? "▾" : "▸"}</span>`
    + `<span>Gebäude</span>`
    + `<span class="zaehler">${aktiv ? `${aktiv} aktiv` : ""}</span>`;
  kopf.addEventListener("click", () => {
    gebaeudeAufgeklappt = !gebaeudeAufgeklappt;
    renderGebaeude();
  });
  halter.appendChild(gruppenKopf(kopf, aktiv < einheiten.size, (an) => {
    state.gebaeudeAn = {};
    state.gebaeudeAus = {};
    if (an) einheiten.forEach((name, einheit) => { state.gebaeudeAn[einheit] = true; });
    else einheiten.forEach((name, einheit) => { state.gebaeudeAus[einheit] = true; });
    render();
  }));
  if (!gebaeudeAufgeklappt) return;

  einheiten.forEach((name, einheit) => {
    const an = bauAktiv(einheit);
    const durchMarker = an && !state.gebaeudeAn[einheit];
    const zeile = document.createElement("div");
    zeile.className = "object-row" + (an ? "" : " aus");
    const haken = document.createElement("span");
    haken.className = "check" + (an ? " an" : "");
    haken.textContent = an ? "✓" : "";
    zeile.appendChild(haken);
    const titelSpan = document.createElement("span");
    titelSpan.className = "object-title";
    titelSpan.textContent = sprachText(name) + (durchMarker ? " (durch Marker)" : "");
    zeile.appendChild(titelSpan);
    // Klick schaltet immer — auch gegen aktive Marker (verschiedene
    // Betonungen): aktiv -> von Hand aus; aus -> von Hand an.
    zeile.addEventListener("click", () => {
      if (an) {
        delete state.gebaeudeAn[einheit];
        state.gebaeudeAus[einheit] = true;
      } else {
        delete state.gebaeudeAus[einheit];
        state.gebaeudeAn[einheit] = true;
      }
      render();
    });
    halter.appendChild(zeile);
  });
}

let eigeneFarbe = "rot";

function renderEigeneFarben() {
  const halter = document.getElementById("eigene-farben");
  halter.innerHTML = "";
  Object.entries(MARKER_FARBEN).forEach(([name, hex]) => {
    const knopf = document.createElement("button");
    knopf.type = "button";
    knopf.className = "marken-farbe" + (eigeneFarbe === name ? " gewaehlt" : "");
    knopf.style.background = hex;
    knopf.title = name;
    knopf.addEventListener("click", () => { eigeneFarbe = name; renderEigeneFarben(); });
    halter.appendChild(knopf);
  });
}

function renderFarben() {
  // ‹gedeckt› ist der Standard (keine Preset-Wahl mehr) —
  // die Rollenfarben bleiben einzeln anpassbar.
  farbRollen.innerHTML = "";
  ROLLEN.forEach(([rolle, name]) => {
    const reihe = document.createElement("div");
    reihe.className = "farb-reihe";
    const label = document.createElement("label");
    label.textContent = name;
    const eingabe = document.createElement("input");
    eingabe.type = "color";
    eingabe.value = state.farben[rolle];
    eingabe.title = `${name} anpassen`;
    eingabe.addEventListener("input", () => {
      state.farben[rolle] = eingabe.value;
      state.preset = "eigene Mischung";
      renderVorschau();
      speichern();
    });
    eingabe.addEventListener("change", () => render());
    reihe.appendChild(label);
    reihe.appendChild(eingabe);
    farbRollen.appendChild(reihe);
  });
}

/* ---------- Format / Optionen / Ausschnitt ---------- */

function renderOptionen() {
  document.querySelectorAll("#format-row [data-format]").forEach((knopf) => {
    knopf.setAttribute("aria-pressed", knopf.dataset.format === state.format ? "true" : "false");
  });
  const beschnitt = document.getElementById("opt-beschnitt");
  const marken = document.getElementById("opt-marken");
  beschnitt.checked = state.beschnitt;
  marken.checked = state.beschnitt && state.marken;
  marken.disabled = !state.beschnitt;
  document.getElementById("row-marken").classList.toggle("aus", !state.beschnitt);
  document.getElementById("titel-input").value = state.titel;
  document.getElementById("untertitel-input").value = state.untertitel;
  document.getElementById("eigene-titel").value = state.eigeneTitel;

  const regler = document.getElementById("ausschnitt-skala");
  regler.value = String(Math.round(state.ausschnitt.skala * 100));
  document.getElementById("ausschnitt-wert").textContent = `${Math.round(state.ausschnitt.skala * 100)}%`;

  document.getElementById("opt-wiese-klein").checked = state.wiesen.klein;
  document.getElementById("opt-wiese-gross").checked = state.wiesen.gross;
  document.getElementById("opt-kompakt").checked = state.kompakt;

  document.getElementById("logo-skala").value = String(Math.round(state.logo.skala * 100));
  document.getElementById("logo-wert").textContent = `${Math.round(state.logo.skala * 100)}%`;
  document.getElementById("titellogo-breite").value = String(state.titelLogo ? state.titelLogo.breite : 45);
  document.getElementById("titellogo-status").textContent = state.titelLogo
    ? "Sonderlogo aktiv — ersetzt Titel und Untertitel auf dem Blatt."
    : "Kein Sonderlogo geladen.";
  document.getElementById("logo-lage").textContent = state.logo.x == null
    ? `Standard (${LOGO_STANDARD.x} × ${LOGO_STANDARD.y} mm)`
    : `${state.logo.x.toFixed(1)} × ${state.logo.y.toFixed(1)} mm`;
}

/* ---------- Zoom (nur Bildschirm-Vorschau) ---------- */

function setzeZoom(wert) {
  state.zoom = Math.min(2.5, Math.max(0.5, wert));
  document.documentElement.style.setProperty("--preview-zoom", String(state.zoom));
  document.getElementById("zoom-value").textContent = `${Math.round(state.zoom * 100)}%`;
}

/* ---------- Speichern / Laden ---------- */

function standAlsJson() {
  return {
    titel: state.titel, untertitel: state.untertitel,
    eigeneTitel: state.eigeneTitel,
    sprache: state.sprache, format: state.format,
    beschnitt: state.beschnitt, marken: state.marken,
    an: Object.keys(state.an), labels: state.labels,
    gebaeudeAn: Object.keys(state.gebaeudeAn),
    gebaeudeAus: Object.keys(state.gebaeudeAus),
    teileAus: state.teileAus, notizenAus: state.notizenAus,
    markerFarben: state.markerFarben, positionen: state.positionen,
    eigene: state.eigene, wiesen: state.wiesen, kompakt: state.kompakt, ausschnitt: state.ausschnitt,
    logo: { ...state.logo, basis: LOGO_STANDARD.breite },
    titelLogo: state.titelLogo,
    preset: state.preset, farben: state.farben
  };
}

function speichern() {
  try {
    localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify(standAlsJson()));
  } catch (fehler) {
    console.warn("Zustand nicht speicherbar:", fehler);
  }
}

function standAnwenden(s) {
    if (typeof s.titel === "string") state.titel = s.titel;
    state.untertitel = typeof s.untertitel === "string" ? s.untertitel : "";
    state.eigeneTitel = typeof s.eigeneTitel === "string" ? s.eigeneTitel : "";
    state.format = s.format === "a3" ? "a3" : "a4";
    state.beschnitt = s.beschnitt !== false;
    state.marken = Boolean(s.marken);
    state.sprache = s.sprache === "en" ? "en" : "de";
    state.an = {};  // Beispiel-Vorauswahl gilt nur ohne gespeicherten Stand
    (s.an || []).forEach((id) => { state.an[id] = true; });
    state.gebaeudeAn = {};
    state.gebaeudeAus = {};
    (s.gebaeudeAn || []).forEach((id) => { state.gebaeudeAn[id] = true; });
    (s.gebaeudeAus || []).forEach((id) => { state.gebaeudeAus[id] = true; });
    state.labels = s.labels || {};
    state.teileAus = s.teileAus || {};
    state.notizenAus = s.notizenAus || {};
    state.markerFarben = s.markerFarben || {};
    state.positionen = s.positionen || {};
    state.eigene = Array.isArray(s.eigene) ? s.eigene : [];
    state.wiesen = s.wiesen
      ? { klein: Boolean(s.wiesen.klein), gross: Boolean(s.wiesen.gross) }
      : { klein: false, gross: false };
    state.kompakt = Boolean(s.kompakt);
    if (s.ausschnitt && typeof s.ausschnitt.skala === "number") {
      state.ausschnitt = {
        skala: Math.min(1.8, Math.max(0.7, s.ausschnitt.skala)),
        dx: Number(s.ausschnitt.dx) || 0,
        dy: Number(s.ausschnitt.dy) || 0
      };
    }
    state.titelLogo = s.titelLogo && typeof s.titelLogo.markup === "string" ? s.titelLogo : null;
    if (s.logo && typeof s.logo === "object") {
      let skala = Number(s.logo.skala) || 1;
      // Altbestand: Skala bezog sich auf die alte Grundbreite 24 mm —
      // seit die Standardbreite 31.7 mm ist, sonst doppelt vergrössert.
      if (!s.logo.basis) skala = skala * 24 / LOGO_STANDARD.breite;
      let x = typeof s.logo.x === "number" ? s.logo.x : null;
      let y = typeof s.logo.y === "number" ? s.logo.y : null;
      // Von Hand gesetzte Lagen, die dem neuen Standard entsprechen,
      // werden wieder Standard (folgen künftigen Feinkorrekturen).
      if (x != null && Math.abs(x - LOGO_STANDARD.x) < 0.6
        && y != null && Math.abs(y - LOGO_STANDARD.y) < 0.6) { x = null; y = null; }
      state.logo = { x, y, skala: Math.min(2, Math.max(0.6, skala)) };
    } else {
      state.logo = { x: null, y: null, skala: 1 };
    }
    if (typeof s.preset === "string") state.preset = PRESET_MIGRATION[s.preset] || s.preset;
    if (!PRESETS[state.preset] && state.preset !== "eigene Mischung") state.preset = "gedeckt";
    if (s.farben) state.farben = { ...PRESETS["gedeckt"], ...s.farben };
    state.ausschnitt = state.ausschnitt || { skala: 1, dx: 0, dy: 0 };
}

function laden() {
  let roh = null;
  try { roh = localStorage.getItem(SPEICHER_SCHLUESSEL); } catch (fehler) { return; }
  if (!roh) return;
  try {
    standAnwenden(JSON.parse(roh));
  } catch (fehler) {
    console.warn("Gespeicherter Stand unlesbar, Standard geladen:", fehler);
  }
}

/* ---------- Gespeicherte Karten ----------
   Jeder Download legt den Stand unter Titel UND Datum ab (je Titel und
   Tag ein Eintrag; ein Stand braucht nur ~2 KB — der Verlauf kostet
   praktisch nichts und schützt vor versehentlichem Überschreiben).
   Zusätzlich: Sichern/Laden als JSON-Datei, für Kollegen und als Backup. */

const VARIANTEN_SCHLUESSEL = "goetheanum-karten-varianten";
const VARIANTEN_MAX = 80;   // ältester Eintrag fällt zuerst

function variantenLesen() {
  try {
    const roh = JSON.parse(localStorage.getItem(VARIANTEN_SCHLUESSEL)) || {};
    // Altbestand (Schlüssel = Titel ohne Datum) einmalig überführen.
    Object.keys(roh).forEach((schluessel) => {
      const e = roh[schluessel];
      if (e && e.stand && !e.titel) {
        roh[schluessel] = { titel: schluessel, stand: e.stand, gespeichert: e.gespeichert || "" };
      }
    });
    return roh;
  } catch (fehler) {
    return {};
  }
}

function varianteAblegen() {
  const titel = state.titel.trim();
  if (!titel) return;
  try {
    const varianten = variantenLesen();
    const jetzt = new Date();
    const tag = jetzt.toISOString().slice(0, 10);
    varianten[`${titel}|${tag}`] = {
      titel, stand: standAlsJson(),
      gespeichert: jetzt.toISOString().slice(0, 16).replace("T", " ")
    };
    const schluessel = Object.keys(varianten)
      .sort((a, b) => (varianten[a].gespeichert || "").localeCompare(varianten[b].gespeichert || ""));
    while (schluessel.length > VARIANTEN_MAX) delete varianten[schluessel.shift()];
    localStorage.setItem(VARIANTEN_SCHLUESSEL, JSON.stringify(varianten));
  } catch (fehler) {
    console.warn("Variante nicht speicherbar:", fehler);
  }
  renderVarianten();
}

function renderVarianten() {
  const halter = document.getElementById("varianten-liste");
  const eintraege = Object.entries(variantenLesen())
    .sort((a, b) => (b[1].gespeichert || "").localeCompare(a[1].gespeichert || ""));
  halter.innerHTML = "";
  if (!eintraege.length) {
    const hinweis = document.createElement("div");
    hinweis.className = "hint";
    hinweis.textContent = "Noch keine gespeicherten Karten — jeder Download legt den Stand unter Titel und Datum ab.";
    halter.appendChild(hinweis);
    return;
  }
  eintraege.forEach(([schluessel, eintrag]) => {
    const titel = eintrag.titel || schluessel;
    const zeile = document.createElement("div");
    zeile.className = "object-row";
    zeile.title = `‹${titel}› laden (ersetzt die aktuelle Ansicht)`;
    const titelSpan = document.createElement("span");
    titelSpan.className = "object-title";
    titelSpan.textContent = titel;
    zeile.appendChild(titelSpan);
    const datum = document.createElement("span");
    datum.className = "object-marker";
    datum.textContent = (eintrag.gespeichert || "").slice(0, 10);
    zeile.appendChild(datum);
    const weg = document.createElement("button");
    weg.type = "button";
    weg.className = "row-btn";
    weg.title = "Gespeicherte Karte löschen";
    weg.textContent = "✕";
    weg.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!window.confirm(`Gespeicherte Karte ‹${titel}› (${(eintrag.gespeichert || "").slice(0, 10)}) löschen?`)) return;
      const varianten = variantenLesen();
      delete varianten[schluessel];
      try { localStorage.setItem(VARIANTEN_SCHLUESSEL, JSON.stringify(varianten)); } catch (fehler) { /* egal */ }
      renderVarianten();
    });
    zeile.appendChild(weg);
    zeile.addEventListener("click", () => {
      if (!window.confirm(`Karte ‹${titel}› vom ${(eintrag.gespeichert || "").slice(0, 10)} laden? Die aktuelle Ansicht wird ersetzt.`)) return;
      standAnwenden(eintrag.stand || {});
      render();
    });
    halter.appendChild(zeile);
  });
}

/* ---------- Interaktion Vorschau: Platzieren; Ausschnitt über Pfeile ---------- */

function svgPunkt(clientX, clientY) {
  const punkt = new DOMPoint(clientX, clientY);
  const matrix = printSvg.getScreenCTM();
  if (!matrix) return null;
  const p = punkt.matrixTransform(matrix.inverse());
  return { x: p.x, y: p.y };
}

// Karte in Blatt-Millimetern verschieben (Pfeilknöpfe und Pfeiltasten).
const AUSSCHNITT_SCHRITT = 5;

function karteVerschieben(dx, dy) {
  state.ausschnitt.dx += dx;
  state.ausschnitt.dy += dy;
  renderVorschau();
  speichern();
}

const EIGENE_HINT_STANDARD = "Erst Beschriftung eingeben, dann in der Vorschau die Stelle anklicken. ‹Esc› bricht ab.";

printSvg.addEventListener("click", (ereignis) => {
  if (!state.platzieren && !state.platzierenOrt && !state.platzierenLogo) return;
  const p = svgPunkt(ereignis.clientX, ereignis.clientY);
  if (!p) return;
  if (state.platzierenLogo) {
    // Logo liegt fest auf dem Blatt (nicht im Ausschnitt): rohe Blatt-mm.
    state.logo.x = Math.round(p.x * 10) / 10;
    state.logo.y = Math.round(p.y * 10) / 10;
    state.platzierenLogo = false;
    eigeneHint.textContent = EIGENE_HINT_STANDARD;
    render();
    return;
  }
  const [x, y] = anpZurueck(p.x, p.y);
  const gerundet = [Math.round(x * 100) / 100, Math.round(y * 100) / 100];
  if (state.platzierenOrt) {
    const eintrag = state.eigene.find((e) => e.id === state.platzierenOrt);
    if (eintrag) {
      eintrag.x = gerundet[0];
      eintrag.y = gerundet[1];
    } else {
      state.positionen[state.platzierenOrt] = gerundet;
    }
    state.platzierenOrt = null;
  } else {
    state.eigene.push({
      id: `eigen-${Date.now()}`,
      label: state.platzieren.label,
      farbe: state.platzieren.farbe,
      marker: String(naechsteEigeneNummer()),
      x: gerundet[0], y: gerundet[1]
    });
    state.an[state.eigene[state.eigene.length - 1].id] = true;
    state.platzieren = null;
  }
  eigeneHint.textContent = EIGENE_HINT_STANDARD;
  render();
});

document.addEventListener("keydown", (ereignis) => {
  if (ereignis.key === "Escape" && (state.platzieren || state.platzierenOrt || state.platzierenLogo)) {
    state.platzieren = null;
    state.platzierenOrt = null;
    state.platzierenLogo = false;
    eigeneHint.textContent = EIGENE_HINT_STANDARD;
    render();
  }
});

/* ---------- Bedienelemente verdrahten ---------- */

document.getElementById("titel-input").addEventListener("input", (ereignis) => {
  state.titel = ereignis.target.value;
  renderVorschau();
  speichern();
});

document.getElementById("untertitel-input").addEventListener("input", (ereignis) => {
  state.untertitel = ereignis.target.value;
  renderVorschau();
  speichern();
});

document.getElementById("eigene-titel").addEventListener("input", (ereignis) => {
  state.eigeneTitel = ereignis.target.value;
  renderVorschau();
  speichern();
});

document.getElementById("eigene-setzen").addEventListener("click", () => {
  const eingabe = document.getElementById("eigene-label");
  const label = eingabe.value.trim();
  if (!label) { eingabe.focus(); return; }
  state.platzieren = { label, farbe: eigeneFarbe };
  eigeneHint.textContent = "Jetzt in der Vorschau die Stelle anklicken … (‹Esc› bricht ab)";
  eingabe.value = "";
  renderVorschau();
  printSvg.scrollIntoView({ behavior: "smooth", block: "nearest" });
});

document.querySelectorAll("#format-row [data-format]").forEach((knopf) => {
  knopf.addEventListener("click", () => {
    state.format = knopf.dataset.format;
    render();
  });
});

document.querySelectorAll("#sprache-row [data-sprache]").forEach((knopf) => {
  knopf.addEventListener("click", () => {
    state.sprache = knopf.dataset.sprache;
    render();
  });
});

document.getElementById("opt-wiese-klein").addEventListener("change", (e) => {
  state.wiesen.klein = e.target.checked;
  render();
});
document.getElementById("opt-wiese-gross").addEventListener("change", (e) => {
  state.wiesen.gross = e.target.checked;
  render();
});

document.getElementById("logo-skala").addEventListener("input", (e) => {
  state.logo.skala = Math.min(2, Math.max(0.6, Number(e.target.value) / 100));
  document.getElementById("logo-wert").textContent = `${Math.round(state.logo.skala * 100)}%`;
  renderVorschau();
});
document.getElementById("logo-skala").addEventListener("change", () => {
  renderOptionen();
  speichern();
});
// Logo mit Pfeiltasten verschieben (1-mm-Schritte); die Anzeige nennt die
// Mitte in Blatt-mm — so lassen sich finale Koordinaten durchgeben.
function logoVerschieben(dx, dy) {
  if (!logoInhalt) return;
  if (state.logo.x == null || state.logo.y == null) {
    state.logo.x = LOGO_STANDARD.x;
    state.logo.y = LOGO_STANDARD.y;
  }
  state.logo.x = Math.round((state.logo.x + dx) * 10) / 10;
  state.logo.y = Math.round((state.logo.y + dy) * 10) / 10;
  render();
}

document.getElementById("logo-links").addEventListener("click", () => logoVerschieben(-1, 0));
document.getElementById("logo-rechts").addEventListener("click", () => logoVerschieben(1, 0));
document.getElementById("logo-hoch").addEventListener("click", () => logoVerschieben(0, -1));
document.getElementById("logo-runter").addEventListener("click", () => logoVerschieben(0, 1));
document.getElementById("logo-reset").addEventListener("click", () => {
  state.logo = { x: null, y: null, skala: 1 };
  render();
});

// Backend-Modus: Justage-Funktionen (Logo, Titellogo, Marker-Feinlagen)
// folgen dem universellen Intern-Schalter der Werkzeugfamilie (nav.js:
// Dreifachklick auf die Kopfleiste oder Tastenfolge ‹intern›); zusätzlich
// öffnet #justage/?justage in der Adresse den Modus direkt.
function backendAktiv() {
  if (typeof window.goeIntern === "function" && window.goeIntern()) return true;
  return window.location.hash === "#justage" || window.location.search.indexOf("justage") >= 0;
}

function backendAnwenden() {
  document.body.classList.toggle("backend", backendAktiv());
  renderOrte();  // ✥ der justierbaren Marker folgt dem Modus
}

window.addEventListener("goe:intern", backendAnwenden);
if (backendAktiv()) document.body.classList.add("backend");

document.getElementById("titellogo-datei").addEventListener("change", (ereignis) => {
  const datei = ereignis.target.files && ereignis.target.files[0];
  ereignis.target.value = "";
  if (!datei) return;
  const leser = new FileReader();
  leser.onload = () => {
    try {
      const doc = new DOMParser().parseFromString(leser.result, "image/svg+xml");
      if (doc.querySelector("parsererror")) throw new Error("SVG unlesbar");
      const svg = doc.documentElement;
      // Tintenbox messen (robust gegen fehlende/krumme viewBoxen):
      const ns = "http://www.w3.org/2000/svg";
      const mess = document.createElementNS(ns, "svg");
      mess.style.position = "absolute";
      mess.style.visibility = "hidden";
      const gruppe = document.createElementNS(ns, "g");
      gruppe.innerHTML = svg.innerHTML;
      mess.appendChild(gruppe);
      document.body.appendChild(mess);
      const box = gruppe.getBBox();
      mess.remove();
      if (!box.width || !box.height) throw new Error("SVG ohne sichtbare Tinte");
      state.titelLogo = {
        markup: svg.innerHTML,
        vbX: box.x, vbY: box.y, vbBreite: box.width, vbHoehe: box.height,
        breite: 45
      };
      render();
    } catch (fehler) {
      window.alert("SVG nicht lesbar — bitte eine reine Vektor-SVG-Datei laden.");
    }
  };
  leser.readAsText(datei);
});

document.getElementById("titellogo-laden").addEventListener("click", () => {
  document.getElementById("titellogo-datei").click();
});

document.getElementById("titellogo-weg").addEventListener("click", () => {
  state.titelLogo = null;
  render();
});

document.getElementById("titellogo-breite").addEventListener("input", (e) => {
  if (!state.titelLogo) return;
  state.titelLogo.breite = Math.min(90, Math.max(20, Number(e.target.value)));
  renderVorschau();
});
document.getElementById("titellogo-breite").addEventListener("change", () => speichern());

document.getElementById("opt-kompakt").addEventListener("change", (e) => {
  state.kompakt = e.target.checked;
  render();
});

document.getElementById("orte-alle-an").addEventListener("click", () => {
  alleOrte().forEach((ort) => { state.an[ort.id] = true; });
  render();
});
document.getElementById("orte-alle-aus").addEventListener("click", () => {
  state.an = {};
  render();
});

const orteSucheFeld = document.getElementById("orte-suche");
orteSucheFeld.addEventListener("input", () => {
  orteSuchbegriff = orteSucheFeld.value.trim().toLowerCase();
  renderOrte();
});
orteSucheFeld.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    orteSucheFeld.value = "";
    orteSuchbegriff = "";
    renderOrte();
  }
});

document.getElementById("opt-beschnitt").addEventListener("change", (e) => {
  state.beschnitt = e.target.checked;
  render();
});
document.getElementById("opt-marken").addEventListener("change", (e) => {
  state.marken = e.target.checked;
  render();
});

document.getElementById("ausschnitt-skala").addEventListener("input", (e) => {
  ausschnittSetzen(Number(e.target.value) / 100);
  document.getElementById("ausschnitt-wert").textContent = `${Math.round(state.ausschnitt.skala * 100)}%`;
  renderVorschau();
});
document.getElementById("ausschnitt-skala").addEventListener("change", () => {
  renderOptionen();
  speichern();
});
document.getElementById("ausschnitt-reset").addEventListener("click", () => {
  state.ausschnitt = { skala: 1, dx: 0, dy: 0 };
  render();
});

document.getElementById("karte-links").addEventListener("click", () => karteVerschieben(-AUSSCHNITT_SCHRITT, 0));
document.getElementById("karte-rechts").addEventListener("click", () => karteVerschieben(AUSSCHNITT_SCHRITT, 0));
document.getElementById("karte-hoch").addEventListener("click", () => karteVerschieben(0, -AUSSCHNITT_SCHRITT));
document.getElementById("karte-runter").addEventListener("click", () => karteVerschieben(0, AUSSCHNITT_SCHRITT));

// Pfeiltasten verschieben die Karte, solange kein Eingabefeld den Fokus hat.
document.addEventListener("keydown", (ereignis) => {
  const ziel = ereignis.target;
  if (ziel && /^(INPUT|TEXTAREA|SELECT)$/.test(ziel.tagName)) return;
  const richtung = {
    ArrowLeft: [-AUSSCHNITT_SCHRITT, 0],
    ArrowRight: [AUSSCHNITT_SCHRITT, 0],
    ArrowUp: [0, -AUSSCHNITT_SCHRITT],
    ArrowDown: [0, AUSSCHNITT_SCHRITT]
  }[ereignis.key];
  if (!richtung) return;
  ereignis.preventDefault();
  karteVerschieben(richtung[0], richtung[1]);
});

document.getElementById("zuruecksetzen").addEventListener("click", () => {
  if (!window.confirm("Alle Anpassungen verwerfen und zum Standard zurückkehren?")) return;
  try { localStorage.removeItem(SPEICHER_SCHLUESSEL); } catch (fehler) { /* egal */ }
  window.location.reload();
});

document.getElementById("zoom-in").addEventListener("click", () => setzeZoom(state.zoom + 0.15));
document.getElementById("zoom-out").addEventListener("click", () => setzeZoom(state.zoom - 0.15));
document.getElementById("zoom-reset").addEventListener("click", () => setzeZoom(1));

// Karte als Datei sichern / aus Datei laden — für Kollegen (Netzlaufwerk,
// Mail) und als Backup; der Browser-Speicher bleibt lokal je Rechner.
document.getElementById("karte-sichern").addEventListener("click", () => {
  const slug = state.titel.trim() ? state.titel.trim().replace(/[^\wäöüÄÖÜß-]+/g, "-") : "campuskarte";
  herunterladen(`${slug}.karte.json`, JSON.stringify(standAlsJson(), null, 2), "application/json");
});

document.getElementById("karte-laden-datei").addEventListener("change", (ereignis) => {
  const datei = ereignis.target.files && ereignis.target.files[0];
  ereignis.target.value = "";
  if (!datei) return;
  const leser = new FileReader();
  leser.onload = () => {
    try {
      standAnwenden(JSON.parse(leser.result));
      render();
    } catch (fehler) {
      window.alert("Datei nicht lesbar — ist es eine .karte.json aus diesem Werkzeug?");
    }
  };
  leser.readAsText(datei);
});

document.getElementById("karte-laden").addEventListener("click", () => {
  document.getElementById("karte-laden-datei").click();
});

// Justierte Sektionen/Gärten-Lagen exportieren (fliessen in die Vorlage).
document.getElementById("lagen-export").addEventListener("click", () => {
  const lagen = justierteLagen();
  if (!Object.keys(lagen).length) {
    window.alert("Noch nichts justiert — Sektionen und Gärten erst mit ✥ verschieben.");
    return;
  }
  herunterladen("marker-korrekturen.json", JSON.stringify(lagen, null, 2), "application/json");
});

// Beim Öffnen passt sich die Vorschau dem Fenster an: das ganze Blatt
// ist sichtbar, unabhängig von Monitor- und Fenstergrösse.
function zoomEinpassen() {
  const rahmen = document.querySelector(".preview-canvas");
  if (!rahmen || !rahmen.clientWidth) return;
  const seite = state.beschnitt && state.marken ? 226 / 313 : 210 / 297;
  const innenBreite = rahmen.clientWidth - 48;          // Innenmass (2 × --s5)
  const verfuegbar = window.innerHeight - rahmen.getBoundingClientRect().top - 72;
  if (innenBreite <= 0 || verfuegbar <= 100) return;
  setzeZoom(Math.min(1.2, verfuegbar / (innenBreite * seite)));
}

/* ---------- Start ---------- */

function render() {
  nummernBerechnen();
  renderOrte();
  renderEigeneFarben();
  renderFarben();
  renderOptionen();
  renderVorschau();
  speichern();
}

(async function start() {
  laden();
  logoErzeugen();
  await Promise.all([ladeGelaende(), ladeIkonen()]);
  // Schriften vor dem ersten Satz laden — die Label-Zentrierung misst
  // mit der echten Hausschrift, nicht mit der Ausweichschrift.
  try {
    await Promise.all([
      document.fonts.load(`100px ${SCHRIFT_SPRACHE}`),
      document.fonts.load(`100px ${SCHRIFT_ZAHL}`)
    ]);
  } catch (fehler) { /* Messung fällt auf die Systemschrift zurück */ }
  renderVarianten();
  render();
  zoomEinpassen();
})();
