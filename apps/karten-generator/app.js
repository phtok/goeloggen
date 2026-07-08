"use strict";

/* Kartentool — Zustand, Szene und Interaktion.
   Grundkarte: assets/gelaende.svg (generiert aus der Original-AI-Datei).
   Orte: orte.js (generiert aus den Beispielkarten, mm-genau).
   Alle Farben im Szenen-SVG sind Druck-Artefaktfarben der gedruckten Karte
   (aus den Beispielkarten übernommen), keine Theme-Flächen — die Bedien-
   oberfläche selbst läuft vollständig über die Design-System-Tokens. */

const SZENE = { breite: KARTE.blatt.breite, hoehe: KARTE.blatt.hoehe };
const EIGENE_START_NR = 60; // feste Nummern (Modus ‹wie Vorlage›)

// Markerfarben wie in den Beispielkarten (LT25-Reader) plus Hauspalette
// (dunkles Gold und Grün, damit Weiss darauf lesbar bleibt — B01).
const MARKER_FARBEN = {
  rot: "#ec5f6c",
  blau: "#81b2cb",
  gold: "#94702e",
  gruen: "#3e7d4e"
};
const FARB_ZYKLUS = ["rot", "blau", "gold", "gruen"];
const TINTE = "#4e4f4a";

// Schriftrollen: Sprache (Titel, Legende, Gebäudenamen) in der Hausschrift
// (Titelschnitt = Deutlich), Werte/Badges (Markernummern, Treppen-Buchstaben,
// Kompass) in der Lese-Grotesk (Source Sans 3 halbfett).
const SCHRIFT_SPRACHE = "GoetheanumDeutlich";
const SCHRIFT_WERT = "SourceSans3Semibold";

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
  ["akzent", "Akzente"]
];

// Voreinstellungen: aus den Original-Varianten der Kartierungsseite abgeleitet
// (Form-Abgleich identischer Pfade).
const PRESETS = {
  "Tagung hell": {
    umgebung: "#edf6fb", "umgebung-hell": "#edf6fb", campus: "#9fccec",
    gebaeude: "#737e8f", "gebaeude-campus": "#67a8da", goetheanum: "#006eb4",
    wege: "#ffffff", parkflaeche: "#edf6fb", akzent: "#006eb4"
  },
  "Campusfest": {
    umgebung: "#e5f2f9", "umgebung-hell": "#e5f2f9", campus: "#90acc6",
    gebaeude: "#657489", "gebaeude-campus": "#436990", goetheanum: "#004071",
    wege: "#ffffff", parkflaeche: "#e5f2f9", akzent: "#004071"
  },
  "Original 2022": {
    umgebung: "#c5d1d9", "umgebung-hell": "#d9e5ec", campus: "#a2b7ce",
    gebaeude: "#455055", "gebaeude-campus": "#4f7095", goetheanum: "#004070",
    wege: "#ffffff", parkflaeche: "#e7e7e7", akzent: "#c2afbd"
  },
  "Hellgrau": {
    umgebung: "#edf6fb", "umgebung-hell": "#edf6fb", campus: "#a2b7ce",
    gebaeude: "#737e8f", "gebaeude-campus": "#4f7095", goetheanum: "#004070",
    wege: "#ffffff", parkflaeche: "#edf6fb", akzent: "#c6c6c6"
  },
  "Recolor 2023": {
    umgebung: "#edf5fa", "umgebung-hell": "#edf5fa", campus: "#8abfe5",
    gebaeude: "#5298cc", "gebaeude-campus": "#5298cc", goetheanum: "#0067b2",
    wege: "#ffffff", parkflaeche: "#edf5fa", akzent: "#0067b2"
  }
};

const SPEICHER_SCHLUESSEL = "goetheanum-karten-v2";

const state = {
  titel: "Herzlich Willkommen",
  format: "a4",
  beschnitt: true,
  marken: false,
  nummerierung: "fortlaufend",   // oder "vorlage" (feste Nummern der Beispiele)
  zoom: 1.15,
  an: {},              // Ort-id -> true = auf der Karte (Start: leeres Blatt)
  labels: {},          // Ort-id -> geänderte Beschriftung
  markerFarben: {},    // Ort-id -> Farbname (überschreibt die Vorlagen-Farbe)
  eigene: [],          // { id, label, farbe, x, y, marker } — x/y in Blatt-mm der Standardlage
  ausschnitt: { skala: 1, dx: 0, dy: 0 },  // Kartenausschnitt relativ zur Standardlage
  preset: "Tagung hell",
  farben: { ...PRESETS["Tagung hell"] },
  platzieren: null,    // { label, farbe } während der Platzierung
  bearbeiten: null     // Ort-id, deren Beschriftung gerade editiert wird
};

/* ---------- Grundkarte, Logo, Kompass laden ---------- */

let gelaendeInhalt = null;   // SVG-Inhalt ohne Wurzel/<style>
let gelaendeMasse = { breite: 1006.3, hoehe: 651.968 };
let logoInhalt = null;       // Campus-Wortmarke aus dem Logogenerator (reine Pfade)
let kompassInhalt = null;    // Kompassrose aus den Icons v2.7 (kompass-2)

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

async function ladeKompass() {
  try {
    const antwort = await fetch("../../assets/fonts/goetheanum/Icons-Einzeldateien/svg/kompass-2.svg");
    const text = await antwort.text();
    kompassInhalt = text
      .replace(/^[\s\S]*?<svg[^>]*>/, "")
      .replace(/<\/svg>\s*$/, "")
      .replace(/ fill="#1a1a1a"/g, ""); // Farbe kommt von der Gruppe (weiss wie in der Vorlage)
  } catch (fehler) {
    console.warn("Kompass-Icon nicht ladbar:", fehler);
  }
}

function gelaendeMarkup() {
  let inhalt = gelaendeInhalt;
  inhalt = inhalt.replace(/class="k-parkflaeche" id="parkflaeche-(\d+)"/g, (voll, nr) => {
    return `fill="${state.farben.parkflaeche}" id="parkflaeche-${nr}"`;
  });
  inhalt = inhalt.replace(/class="k-([a-z-]+)"/g, (voll, rolle) => {
    return `fill="${state.farben[rolle] || "#cccccc"}"`;
  });
  // Striche folgen denselben Rollen wie die Füllungen — sonst zeichnen die
  // Original-Strichfarben Konturen an Flächen, die flach gemeint sind.
  inhalt = inhalt.replace(/data-ks="([a-z-]+)"/g, (voll, rolle) => {
    return `stroke="${state.farben[rolle] || "#cccccc"}"`;
  });
  return inhalt;
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
  return Boolean(state.an[ort.id]);
}

function ortLabel(ort) {
  return state.labels[ort.id] != null ? state.labels[ort.id] : ort.label;
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
let nummern = null;

function nummernBerechnen() {
  if (state.nummerierung !== "fortlaufend") { nummern = null; return; }
  nummern = {};
  let n = 1;
  alleOrte().filter(ortAktiv).forEach((ort) => {
    if (ort.art === "treppe" || !/^\d+$/.test(ort.marker)) return;
    nummern[ort.id] = String(n);
    n += 1;
  });
}

function ortMarker(ort) {
  if (nummern && nummern[ort.id]) return nummern[ort.id];
  return ort.marker;
}

/* ---------- SVG-Bausteine der Szene ---------- */

function escapeXml(wert) {
  return String(wert)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function textGroesse(text, basis) {
  return String(text).length >= 2 ? basis * 0.85 : basis;
}

function markenKreis(x, y, hex, text, r) {
  // Nummern wie im Original: Grotesk halbfett, ~0.7 des Kreisdurchmessers;
  // Grundlinie um ZIFFERN_SITZ unter der Kreismitte (optischer Sitz, DS).
  const groesse = textGroesse(text, r * 1.4);
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="${hex}" />`
    + `<text x="${x}" y="${y + groesse * ZIFFERN_SITZ}" text-anchor="middle" font-size="${groesse}"`
    + ` fill="#ffffff" font-family="${SCHRIFT_WERT}">${escapeXml(text)}</text>`;
}

function pfeilMarkup(x, y, r, hex, richtung) {
  const laenge = 3.4, kopf = 1.5;
  let dx = 1, dy = 0;
  if (richtung === "unten-links") { dx = -0.7071; dy = 0.7071; }
  if (richtung === "unten-rechts") { dx = 0.7071; dy = 0.7071; }
  const x1 = x + dx * r, y1 = y + dy * r;
  const x2 = x + dx * (r + laenge), y2 = y + dy * (r + laenge);
  const winkel = Math.atan2(dy, dx);
  const s1 = winkel + 2.6, s2 = winkel - 2.6;
  const spitze = `${x2 + dx * kopf},${y2 + dy * kopf} `
    + `${x2 + Math.cos(s1) * kopf},${y2 + Math.sin(s1) * kopf} `
    + `${x2 + Math.cos(s2) * kopf},${y2 + Math.sin(s2) * kopf}`;
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${hex}" stroke-width="0.55" />`
    + `<polygon points="${spitze}" fill="${hex}" />`;
}

function treppenGlyph(x, y, hex, skala) {
  const s = skala;
  const d = `M ${x - 1.05 * s} ${y + 0.75 * s}`
    + ` h ${0.7 * s} v ${-0.5 * s} h ${0.7 * s} v ${-0.5 * s} h ${0.7 * s} v ${-0.5 * s}`;
  return `<path d="${d}" fill="none" stroke="${hex}" stroke-width="${0.34 * s}" />`;
}

function liftGlyph(x, y, hex, skala) {
  const s = skala;
  return `<polygon points="${x - 0.55 * s},${y - 0.15 * s} ${x + 0.55 * s},${y - 0.15 * s} ${x},${y - 1.05 * s}" fill="${hex}" />`
    + `<polygon points="${x - 0.55 * s},${y + 0.15 * s} ${x + 0.55 * s},${y + 0.15 * s} ${x},${y + 1.05 * s}" fill="${hex}" />`;
}

function treppenBadge(x, y, buchstabe, form, hex) {
  const farbe = hex || MARKER_FARBEN.rot;
  if (form === "lift") {
    return `<rect x="${x - 1.45}" y="${y - 2.15}" width="2.9" height="4.3" rx="0.7" fill="#ffffff" stroke="${farbe}" stroke-width="0.18" />`
      + `<text x="${x}" y="${y - 0.35}" text-anchor="middle" font-size="1.85" fill="${farbe}" font-family="${SCHRIFT_WERT}">${buchstabe}</text>`
      + liftGlyph(x, y + 1.1, farbe, 0.9);
  }
  return `<circle cx="${x}" cy="${y}" r="2.22" fill="#ffffff" stroke="${farbe}" stroke-width="0.18" />`
    + `<text x="${x - 0.9}" y="${y + 0.85}" text-anchor="middle" font-size="2.5" fill="${farbe}" font-family="${SCHRIFT_WERT}">${buchstabe}</text>`
    + treppenGlyph(x + 0.95, y, farbe, 1.05);
}

// Gebäudenamen in der Hausschrift (Deutlich), optisch mittig in die Fläche
// gesetzt (Anker = Flächenmitte, aus der Vorlage gemessen).
const GEBAEUDE_LABELS = [
  { text: "Goetheanum", x: 198.6, y: 115.0, groesse: 4.23, winkel: 0 },
  { text: "Schreinerei", x: 226.7, y: 95.4, groesse: 3.18, winkel: -76 }
];

function gebaeudeLabelMarkup() {
  return GEBAEUDE_LABELS.map((l) => {
    const drehung = l.winkel ? ` transform="rotate(${l.winkel} ${l.x} ${l.y})"` : "";
    return `<text x="${l.x}" y="${l.y}" font-size="${l.groesse}" fill="#ffffff" text-anchor="middle"`
      + ` font-family="${SCHRIFT_SPRACHE}"${drehung}>${escapeXml(l.text)}</text>`;
  }).join("");
}

function ortMarkup(ort) {
  const hex = ortFarbeHex(ort);
  let teile = "";
  if (ort.art === "treppe") {
    (ort.badges || []).forEach((b) => {
      const [x, y] = anp(b.x, b.y);
      teile += treppenBadge(x, y, ort.marker, b.form, hex);
    });
    return teile;
  }
  (ort.positionen || []).forEach(([px, py]) => {
    const [x, y] = anp(px, py);
    teile += markenKreis(x, y, hex, ortMarker(ort), 2.03);
    if (ort.pfeil) teile += pfeilMarkup(x, y, 2.03, hex, ort.pfeil);
  });
  return teile;
}

/* ---------- Legende ---------- */

const LEGENDE_LAYOUT = {
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

function legendeZeilen(spalte) {
  const zeilen = [];
  let vorher = null;
  alleOrte().filter((o) => o.spalte === spalte && ortAktiv(o)).forEach((ort) => {
    if (vorher) {
      const a = parseInt(vorher.marker, 10), b = parseInt(ort.marker, 10);
      const dekade = state.nummerierung === "vorlage"
        && !Number.isNaN(a) && !Number.isNaN(b) && Math.floor(a / 10) !== Math.floor(b / 10);
      const treppen = vorher.art === "treppe" && ort.art === "treppe";
      if (vorher.art !== ort.art || dekade || treppen) zeilen.push({ typ: "abstand" });
    }
    zeilen.push({ typ: "ort", ort });
    if (ort.art === "treppe") {
      (ort.notizen || []).forEach((n) => zeilen.push({ typ: "notiz", notiz: n, ort }));
    }
    vorher = ort;
  });
  return zeilen;
}

function legendeMarkup() {
  const L = LEGENDE_LAYOUT;
  const start = state.titel.trim() ? L.startMitTitel : L.startOhneTitel;
  let teile = "";
  [0, 1].forEach((spalte) => {
    const x = L.spaltenX[spalte];
    let y = start;
    legendeZeilen(spalte).forEach((zeile) => {
      if (zeile.typ === "abstand") { y += L.gruppe; return; }
      if (zeile.typ === "notiz") {
        const n = zeile.notiz;
        if (n.badge === "lift") {
          teile += treppenBadge(x, y - 0.9, zeile.ort.marker, "lift", ortFarbeHex(zeile.ort));
        }
        teile += `<text x="${x + L.labelAbstand}" y="${y}" font-size="${L.notizGroesse}"`
          + ` fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(n.label)}</text>`;
        y += L.notiz;
        return;
      }
      const ort = zeile.ort;
      const hex = ortFarbeHex(ort);
      const zeilenTexte = ortLabel(ort).split("\n");
      if (ort.art === "treppe") {
        teile += treppenBadge(x, y - 0.9, ort.marker, "treppe", hex);
      } else {
        teile += markenKreis(x, y - 0.9, hex, ortMarker(ort), 2.03);
      }
      zeilenTexte.forEach((text, index) => {
        teile += `<text x="${x + L.labelAbstand}" y="${y + index * L.extraZeile}"`
          + ` font-size="${L.labelGroesse}" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(text)}</text>`;
      });
      y += L.zeile + (zeilenTexte.length - 1) * L.extraZeile;
    });
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

function logoMarkup() {
  if (!logoInhalt) return "";
  const breite = 22; // mm — rechtsbündig, Rand wie die Legende links (10.5)
  const skala = breite / logoInhalt.breite;
  const x = SZENE.breite - 10.5 - breite;
  return `<g transform="translate(${x} 6.5) scale(${skala})">${logoInhalt.markup}</g>`;
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
    <line x1="${KARTE.falz}" y1="0" x2="${KARTE.falz}" y2="${SZENE.hoehe}" stroke="${TINTE}" stroke-opacity="0.4" stroke-width="0.18" />
    ${titel ? `<text x="10.5" y="14.2" font-size="5.3" fill="${TINTE}" font-family="${SCHRIFT_SPRACHE}">${escapeXml(titel)}</text>` : ""}
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
  printSvg.classList.toggle("platzieren", Boolean(state.platzieren));
}

/* ---------- Seitenleiste ---------- */

const orteGruppen = document.getElementById("orte-gruppen");
const eigeneListe = document.getElementById("eigene-liste");
const eigeneHint = document.getElementById("eigene-hint");
const farbRollen = document.getElementById("farb-rollen");
const presetRow = document.getElementById("preset-row");

const GRUPPEN = [
  ["Orientierung", (o) => o.art === "orientierung"],
  ["Veranstaltungsorte", (o) => o.art === "ort"],
  ["Treppenhaus", (o) => o.art === "treppe"]
];

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
  zeile.className = "object-row" + (ortAktiv(ort) ? "" : " aus");

  const farbKnopf = document.createElement("button");
  farbKnopf.type = "button";
  farbKnopf.className = "row-btn";
  farbKnopf.title = "Markerfarbe wechseln (Rot → Blau → Gold → Grün)";
  const punkt = document.createElement("span");
  punkt.className = "object-dot";
  punkt.style.background = ortFarbeHex(ort);
  farbKnopf.appendChild(punkt);
  farbKnopf.addEventListener("click", (e) => {
    e.stopPropagation();
    farbeWeiterschalten(ort);
  });
  zeile.appendChild(farbKnopf);

  if (state.bearbeiten === ort.id) {
    const eingabe = document.createElement("input");
    eingabe.type = "text";
    eingabe.className = "label-edit";
    eingabe.value = ortLabel(ort).replace(/\n/g, " / ");
    const uebernehmen = () => {
      const wert = eingabe.value.trim();
      state.bearbeiten = null;
      if (ort.art === "eigene") {
        const eintrag = state.eigene.find((e) => e.id === ort.id);
        if (eintrag && wert) eintrag.label = wert;
      } else if (!wert || wert === ort.label.replace(/\n/g, " / ")) {
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
  markerSpan.textContent = ortAktiv(ort) ? ortMarker(ort) : (state.nummerierung === "vorlage" ? ort.marker : "–");
  zeile.appendChild(markerSpan);

  const stift = document.createElement("button");
  stift.type = "button";
  stift.className = "row-btn";
  stift.title = "Beschriftung ändern";
  stift.textContent = "✎";
  stift.addEventListener("click", (e) => {
    e.stopPropagation();
    state.bearbeiten = ort.id;
    render();
  });
  zeile.appendChild(stift);

  if (loeschbar) {
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

  zeile.addEventListener("click", () => {
    if (state.an[ort.id]) delete state.an[ort.id];
    else state.an[ort.id] = true;
    render();
  });
  return zeile;
}

function renderOrte() {
  document.querySelectorAll("#nummerierung-row [data-nummerierung]").forEach((knopf) => {
    knopf.setAttribute("aria-pressed", knopf.dataset.nummerierung === state.nummerierung ? "true" : "false");
  });
  orteGruppen.innerHTML = "";
  GRUPPEN.forEach(([titel, filter]) => {
    const gruppe = document.createElement("div");
    gruppe.innerHTML = `<div class="object-group-title">${titel}</div>`;
    const liste = document.createElement("div");
    liste.className = "object-list";
    ORTE.filter(filter).forEach((ort) => liste.appendChild(ortZeile(ort, false)));
    gruppe.appendChild(liste);
    orteGruppen.appendChild(gruppe);
  });

  eigeneListe.innerHTML = "";
  alleOrte().filter((o) => o.art === "eigene").forEach((ort) => {
    eigeneListe.appendChild(ortZeile(ort, true));
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
  presetRow.innerHTML = "";
  Object.keys(PRESETS).forEach((name) => {
    const knopf = document.createElement("button");
    knopf.type = "button";
    knopf.setAttribute("aria-pressed", state.preset === name ? "true" : "false");
    knopf.textContent = name;
    knopf.addEventListener("click", () => {
      state.preset = name;
      state.farben = { ...PRESETS[name] };
      render();
    });
    presetRow.appendChild(knopf);
  });

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

  const regler = document.getElementById("ausschnitt-skala");
  regler.value = String(Math.round(state.ausschnitt.skala * 100));
  document.getElementById("ausschnitt-wert").textContent = `${Math.round(state.ausschnitt.skala * 100)}%`;
}

/* ---------- Zoom (nur Bildschirm-Vorschau) ---------- */

function setzeZoom(wert) {
  state.zoom = Math.min(2.5, Math.max(0.5, wert));
  document.documentElement.style.setProperty("--preview-zoom", String(state.zoom));
  document.getElementById("zoom-value").textContent = `${Math.round(state.zoom * 100)}%`;
}

/* ---------- Speichern / Laden ---------- */

function speichern() {
  try {
    localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify({
      titel: state.titel, format: state.format,
      beschnitt: state.beschnitt, marken: state.marken,
      nummerierung: state.nummerierung,
      an: Object.keys(state.an), labels: state.labels,
      markerFarben: state.markerFarben,
      eigene: state.eigene, ausschnitt: state.ausschnitt,
      preset: state.preset, farben: state.farben
    }));
  } catch (fehler) {
    console.warn("Zustand nicht speicherbar:", fehler);
  }
}

function laden() {
  let roh = null;
  try { roh = localStorage.getItem(SPEICHER_SCHLUESSEL); } catch (fehler) { return; }
  if (!roh) return;
  try {
    const s = JSON.parse(roh);
    if (typeof s.titel === "string") state.titel = s.titel;
    if (s.format === "a3") state.format = "a3";
    state.beschnitt = s.beschnitt !== false;
    state.marken = Boolean(s.marken);
    if (s.nummerierung === "vorlage") state.nummerierung = "vorlage";
    (s.an || []).forEach((id) => { state.an[id] = true; });
    state.labels = s.labels || {};
    state.markerFarben = s.markerFarben || {};
    state.eigene = Array.isArray(s.eigene) ? s.eigene : [];
    if (s.ausschnitt && typeof s.ausschnitt.skala === "number") {
      state.ausschnitt = {
        skala: Math.min(1.8, Math.max(0.7, s.ausschnitt.skala)),
        dx: Number(s.ausschnitt.dx) || 0,
        dy: Number(s.ausschnitt.dy) || 0
      };
    }
    if (typeof s.preset === "string") state.preset = s.preset;
    if (s.farben) state.farben = { ...PRESETS["Tagung hell"], ...s.farben };
  } catch (fehler) {
    console.warn("Gespeicherter Stand unlesbar, Standard geladen:", fehler);
  }
}

/* ---------- Interaktion Vorschau: Platzieren und Ausschnitt ziehen ---------- */

function svgPunkt(clientX, clientY) {
  const punkt = new DOMPoint(clientX, clientY);
  const matrix = printSvg.getScreenCTM();
  if (!matrix) return null;
  const p = punkt.matrixTransform(matrix.inverse());
  return { x: p.x, y: p.y };
}

let ziehen = null;

printSvg.addEventListener("pointerdown", (ereignis) => {
  if (state.platzieren || ereignis.button !== 0) return;
  ziehen = {
    startX: ereignis.clientX, startY: ereignis.clientY,
    dx: state.ausschnitt.dx, dy: state.ausschnitt.dy,
    bewegt: false
  };
  printSvg.setPointerCapture(ereignis.pointerId);
});

printSvg.addEventListener("pointermove", (ereignis) => {
  if (!ziehen) return;
  const matrix = printSvg.getScreenCTM();
  if (!matrix) return;
  const proMm = matrix.a; // Pixel je Blatt-mm
  const dxMm = (ereignis.clientX - ziehen.startX) / proMm;
  const dyMm = (ereignis.clientY - ziehen.startY) / proMm;
  if (!ziehen.bewegt && Math.hypot(dxMm, dyMm) < 0.5) return;
  ziehen.bewegt = true;
  state.ausschnitt.dx = ziehen.dx + dxMm;
  state.ausschnitt.dy = ziehen.dy + dyMm;
  renderVorschau();
});

printSvg.addEventListener("pointerup", () => {
  if (ziehen && ziehen.bewegt) {
    renderOptionen();
    speichern();
  }
  ziehen = ziehen && ziehen.bewegt ? { fertig: true } : null;
  setTimeout(() => { ziehen = null; }, 0);
});

printSvg.addEventListener("click", (ereignis) => {
  if (ziehen && ziehen.fertig) return; // Klick am Ende einer Zieh-Geste
  if (!state.platzieren) return;
  const p = svgPunkt(ereignis.clientX, ereignis.clientY);
  if (!p) return;
  const [x, y] = anpZurueck(p.x, p.y);
  state.eigene.push({
    id: `eigen-${Date.now()}`,
    label: state.platzieren.label,
    farbe: state.platzieren.farbe,
    marker: String(naechsteEigeneNummer()),
    x: Math.round(x * 100) / 100,
    y: Math.round(y * 100) / 100
  });
  const neue = state.eigene[state.eigene.length - 1];
  state.an[neue.id] = true;
  state.platzieren = null;
  eigeneHint.textContent = "Erst Beschriftung eingeben, dann in der Vorschau die Stelle anklicken. ‹Esc› bricht ab.";
  render();
});

document.addEventListener("keydown", (ereignis) => {
  if (ereignis.key === "Escape" && state.platzieren) {
    state.platzieren = null;
    eigeneHint.textContent = "Erst Beschriftung eingeben, dann in der Vorschau die Stelle anklicken. ‹Esc› bricht ab.";
    render();
  }
});

/* ---------- Bedienelemente verdrahten ---------- */

document.getElementById("titel-input").addEventListener("input", (ereignis) => {
  state.titel = ereignis.target.value;
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

document.querySelectorAll("#nummerierung-row [data-nummerierung]").forEach((knopf) => {
  knopf.addEventListener("click", () => {
    state.nummerierung = knopf.dataset.nummerierung;
    render();
  });
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

document.getElementById("zuruecksetzen").addEventListener("click", () => {
  if (!window.confirm("Alle Anpassungen verwerfen und zum Standard zurückkehren?")) return;
  try { localStorage.removeItem(SPEICHER_SCHLUESSEL); } catch (fehler) { /* egal */ }
  window.location.reload();
});

document.getElementById("zoom-in").addEventListener("click", () => setzeZoom(state.zoom + 0.15));
document.getElementById("zoom-out").addEventListener("click", () => setzeZoom(state.zoom - 0.15));
document.getElementById("zoom-reset").addEventListener("click", () => setzeZoom(1));

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
  await Promise.all([ladeGelaende(), ladeKompass()]);
  setzeZoom(state.zoom);
  render();
})();
