"use strict";

/* Campusplan für Gäste — Laborseite.
   Drei Schritte (Themen → Zeit → Plan), der Plan ist die URL (#p=…),
   Abhaken lebt im localStorage des Geräts. Karte und Katalog kommen aus
   dem Kartentool (apps/karten-generator/), Farben aus dessen Preset
   ‹gedeckt› (dort dokumentiert). */

/* ---------- Karte: Palette und Geometrie (aus dem Kartentool) ---------- */

const PALETTE = {
  umgebung: "#edf5fa", "umgebung-hell": "#edf5fa", campus: "#8abfe5",
  gebaeude: "#5298cc", "gebaeude-campus": "#5298cc", goetheanum: "#0067b2",
  wege: "#ffffff", parkflaeche: "#edf5fa", akzent: "#0067b2", wiese: "#96c68c"
};
const GELAENDE_PFAD = "../karten-generator/assets/gelaende.svg";
const BLATT = { breite: KARTE.blatt.breite, hoehe: KARTE.blatt.hoehe };
const MARKE_R = 3.0;          // mm auf dem Blatt
// Markenfarben auf der Karte — Artefakt-Farben wie im Kartentool (Aquarell-
// Palette), gerechnet gegen die Kartengründe: Gold #7a5a20 3.2:1 auf dem
// Campusblau, Weiss darauf 6.3:1; Markenblau 3.3:1 / 6.4:1; Grün 3.2:1 / 6.4:1.
// Der weisse Ring trennt zusätzlich auf dem dunklen Goetheanum-Blau.
const MARKE_FARBEN = { station: "#7a5a20", anreise: "#0061a9", besucht: "#226b52", ring: "#ffffff", fokus: "#dfb87a", ziffer: "#ffffff" }; // # ds-ok: Artefakt-Farben der Karte
const AUSNAHMEN_URL = "https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/campusplan-ausnahmen";
const ZOOM_MIN_BREITE = 24;   // mm sichtbare Breite bei maximalem Zoom
const SPEICHER_PRAEFIX = "campusplan:";

/* ---------- Texte ---------- */

const UI = {
  "s1-titel": { de: "Themen", en: "Themes" },
  "s2-titel": { de: "Zeit", en: "Time" },
  "s3-titel": { de: "Dein Plan", en: "Your plan" },
  "s1-frage": { de: "Was zieht dich an?", en: "What draws you in?" },
  "s1-hilfe": { de: "Eines oder mehrere wählen. Der Plan füllt sich daraus von selbst.",
                en: "Pick one or more. The plan fills itself from your choice." },
  "s2-frage": { de: "Wie viel Zeit hast du?", en: "How much time do you have?" },
  "s2-hilfe": { de: "Die Zeit entscheidet, wie viele Orte auf den Plan kommen. Ändern geht später jederzeit.",
                en: "Time decides how many places make the plan. You can change it any time." },
  weiter: { de: "Weiter", en: "Next" },
  zurueck: { de: "Zurück", en: "Back" },
  "plan-zeigen": { de: "Plan zeigen", en: "Show plan" },
  "zurueck-zeit": { de: "Zurück zur Zeit", en: "Back to time" },
  neu: { de: "Neu beginnen", en: "Start over" },
  link: { de: "Link kopieren", en: "Copy link" },
  qr: { de: "QR-Code", en: "QR code" },
  "link-lab": { de: "Dein Link, zum Weitergeben oder aufs Telefon", en: "Your link, to share or to open on your phone" },
  "plan-aendern": { de: "Plan ändern", en: "Change plan" },
  "plan-hint": { de: "Abgehakt wird nur auf diesem Gerät gespeichert. Der Link bleibt gleich.",
                 en: "Ticks are stored on this device only. The link stays the same." },
  "karte-hint": { de: "Ziehen bewegt die Karte, zwei Finger zoomen. Ein Tipp auf eine Nummer springt zur Station.",
                  en: "Drag to move the map, pinch to zoom. Tap a number to jump to its station." },
  titel: { de: "Mein Campusplan", en: "My Campus Plan" },
  lede: { de: "Den eigenen Besuch am Goetheanum planen: Themen wählen, Zeit wählen, fertig. Den Plan als PDF mitnehmen oder als Link aufs Telefon und unterwegs abhaken.",
          en: "Plan your own visit to the Goetheanum: pick themes, pick a time, done. Take the plan as a PDF or as a link on your phone and tick off places as you go." },
  besuch: { de: "Mein Besuch", en: "My visit" },
  stationen: { de: "Stationen", en: "stops" },
  etwa: { de: "etwa", en: "about" },
  besucht: { de: "besucht", en: "visited" },
  von: { de: "von", en: "of" },
  dabei: { de: "dabei", en: "included" },
  "mehr-orte": { de: "Mehr Orte", en: "More places" },
  "karte-knopf": { de: "Karte", en: "Map" },
  "s1-leer": { de: "Ohne Thema zeigt der Plan nur Eingang, Empfang und Anreise.",
               en: "Without a theme the plan shows only entrance, reception and arrival." },
  kopiert: { de: "Kopiert.", en: "Copied." },
  "kopieren-hand": { de: "Link markieren und von Hand kopieren.", en: "Select the link and copy it by hand." },
  anreise: { de: "Anreise und Service", en: "Arrival and service" },
  min: { de: "Min.", en: "min" },
  std: { de: "Std.", en: "h" },
  "lage-hint": { de: "Lage noch nicht am Gelände geprüft:", en: "Position not yet checked on site:" },
  "wc": { de: "Toiletten", en: "Toilets" },
  pdf: { de: "PDF herunterladen", en: "Download PDF" },
  "pdf-laeuft": { de: "PDF wird erzeugt …", en: "Creating PDF …" },
  "pdf-fehler": { de: "PDF konnte nicht erzeugt werden.", en: "The PDF could not be created." },
  blatt: { de: "Blatt", en: "sheet" },
  "stationen-titel": { de: "Die Stationen", en: "The stops" },
  "pdf-link-hint": { de: "Derselbe Plan auf dem Telefon: Link öffnen oder QR-Code scannen, unterwegs abhaken.",
                     en: "The same plan on your phone: open the link or scan the QR code, tick off as you go." },
  "datum-lab": { de: "Besuchstag, wenn du ihn schon kennst", en: "Day of your visit, if you know it" },
  "datum-hint": { de: "Mit Besuchstag kommen nur Orte in den Plan, die an diesem Tag offen sind. Geschlossene bleiben unter «Mehr Orte» und sind markiert.",
                  en: "With a visit day, only places open on that day make the plan. Closed ones stay under «More places», marked." },
  "geschlossen-am": { de: "am Besuchstag geschlossen", en: "closed on your visit day" },
  ausnahmen: { de: "aktuelle Ausnahmen", en: "current exceptions" },
  "an-diesem-tag": { de: "an diesem Tag", en: "on this day" },
  "orte-zu": { de: "Orte sind an diesem Tag zu und nicht im Plan", en: "places are closed that day and left out" },
  "ort-zu": { de: "Ort ist an diesem Tag zu und nicht im Plan", en: "place is closed that day and left out" },
  "alles-offen": { de: "alle Orte des Plans sind offen", en: "every place in the plan is open" },
  "fuehrung-hint": { de: "Mit einer Führung ist alles zugänglich, auch die Häuser der Architektursammlung.", en: "With a guided tour everything is accessible, including the houses of the architecture collection." },
  "fuehrung-link": { de: "Führungen buchen", en: "Book a guided tour" }
};

/* ---------- Zustand ---------- */

const state = {
  sprache: "de",
  modus: "erstellen",         // ‹erstellen› | ‹plan›
  schritt: 1,
  themen: new Set(),
  umstaende: { kinder: false, barrierefrei: false },
  zeit: "halb",
  an: new Set(),              // Ort-IDs im Plan
  besucht: new Set(),         // Ort-IDs abgehakt (nur Modus ‹plan›)
  code: "",                   // Plan-Code aus dem Link
  datum: "",                  // Besuchstag ISO (optional)
  ausnahmen: null,            // Antwort der Edge Function (saal, glashaus) oder null
  fokus: null
};

/* ---------- Orte ---------- */

const ORTE_ALLE = ORTE.concat(NEUE_ORTE);
const ORT_NACH_ID = {};
ORTE_ALLE.forEach((o) => { ORT_NACH_ID[o.id] = o; });
const GAST_NACH_ID = {};
GAESTE.forEach((g) => { GAST_NACH_ID[g.id] = g; });

function t(wert) {
  if (wert && typeof wert === "object") return wert[state.sprache] || wert.de;
  return wert;
}
function ui(schluessel) { return t(UI[schluessel]) || schluessel; }
function ort(id) { return ORT_NACH_ID[id]; }
function gast(id) { return GAST_NACH_ID[id]; }
function ortName(id) {
  const o = ort(id);
  if (!o) return id;
  if (o.teile) return t(o.teile[0]);
  return t(o.label);
}
function ortPosition(id) {
  const o = ort(id);
  if (o.positionen && o.positionen.length) return o.positionen[0];
  if (o.badges && o.badges.length) return [o.badges[0].x, o.badges[0].y];
  return [BLATT.breite / 2, BLATT.hoehe / 2];
}
function ortGebaeude(id) {
  const g = gast(id), o = ort(id);
  if (g && g.gebaeude) return g.gebaeude;
  if (o && o.gebaeudeTeile) return o.gebaeudeTeile;
  if (o && o.gebaeude) return [o.gebaeude];
  return [];
}
function ortMarker(id) {
  const o = ort(id);
  return o && o.marker && /^[A-Z]{1,2}$/.test(o.marker) ? o.marker : "";
}

/* ---------- Vorauswahl (Konzept § 9, Schritt 2) ---------- */

function budgetMinuten() {
  const z = ZEITEN.find((x) => x.id === state.zeit) || ZEITEN[1];
  return z.minuten;
}

function immerDabei() {
  return GAESTE.filter((g) => (g.thema === "basis" || g.thema === "anreise")
    && (!g.nurBarrierefrei || state.umstaende.barrierefrei)).map((g) => g.id);
}

function heuteIso() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Der Tag, für den der Plan gilt: der Besuchstag, im Modus ‹plan› ohne Datum der heutige.
function planTag() {
  return state.datum || (state.modus === "plan" ? heuteIso() : "");
}

async function ausnahmenLaden() {
  try {
    const r = await fetch(AUSNAHMEN_URL);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    state.ausnahmen = await r.json();
  } catch (fehler) {
    state.ausnahmen = null;   // ohne Live-Daten bleibt der Link auf die Seite
  }
  if (state.schritt === 3) planZeichnen();
}

// Tagesaktuelle Ausnahme eines Orts (Grosser Saal, Glashaus) für einen Tag.
function ausnahmeAm(g, iso) {
  if (!g.live || !iso || !state.ausnahmen) return null;
  const liste = state.ausnahmen[g.live] || [];
  return liste.find((e) => e.datum === iso) || null;
}

function ortGeschlossenAm(g, iso) {
  if (!iso) return false;
  const a = ausnahmeAm(g, iso);
  if (a && a.zu) return true;
  if (!g.geschlossen) return false;
  const [j, m, tag] = iso.split("-").map(Number);
  const wochentag = new Date(j, m - 1, tag).getDay();
  return g.geschlossen.includes(wochentag);
}

function datumText(iso) {
  if (!iso) return "";
  const [j, m, tag] = iso.split("-").map(Number);
  return new Date(j, m - 1, tag).toLocaleDateString(state.sprache === "en" ? "en-GB" : "de-CH",
    { weekday: "long", day: "numeric", month: "long" });
}

function vorauswahl() {
  const an = new Set(immerDabei());
  const kandidaten = GAESTE.filter((g) => {
    if (g.thema === "basis" || g.thema === "anreise") return false;
    if (state.umstaende.barrierefrei && g.barrierefrei === false) return false;
    if (ortGeschlossenAm(g, planTag())) return false;
    return state.themen.has(g.thema) || (state.umstaende.kinder && g.kinder);
  });
  // Je Thema nach Rang sortieren, dann reihum ein Ort je Thema — so bekommt
  // jedes gewählte Thema seine Highlights, bevor das zweite Glied kommt.
  const rang = (g) => (state.umstaende.kinder && g.kinder ? 0 : g.rang || 99);
  const gruppen = {};
  kandidaten.forEach((g) => { (gruppen[g.thema] = gruppen[g.thema] || []).push(g); });
  Object.values(gruppen).forEach((liste) => liste.sort((a, b) => rang(a) - rang(b)));
  const reihe = [];
  let offen = true;
  for (let i = 0; offen; i++) {
    offen = false;
    Object.values(gruppen).forEach((liste) => { if (liste[i]) { reihe.push(liste[i]); offen = true; } });
  }
  let rest = budgetMinuten() - GAESTE.filter((g) => g.thema === "basis").reduce((s, g) => s + g.dauer + WEGZEIT, 0);
  reihe.forEach((g) => {
    const kosten = g.dauer + WEGZEIT;
    if (kosten <= rest) { an.add(g.id); rest -= kosten; }
  });
  state.an = an;
}

function planMinuten() {
  let summe = 0;
  state.an.forEach((id) => { const g = gast(id); if (g && g.thema !== "anreise" && g.thema !== "aus") summe += g.dauer + WEGZEIT; });
  return summe;
}

function dauerText(minuten) {
  if (minuten < 60) return `${minuten} ${ui("min")}`;
  const h = Math.floor(minuten / 60), m = minuten % 60;
  return m ? `${h} ${ui("std")} ${m} ${ui("min")}` : `${h} ${ui("std")}`;
}

/* ---------- Link: der Plan ist die URL ---------- */

function kodieren() {
  const bytes = new Uint8Array(Math.ceil(GAESTE.length / 8));
  GAESTE.forEach((g, i) => { if (state.an.has(g.id)) bytes[i >> 3] |= 128 >> (i & 7); });
  let bin = "";
  bytes.forEach((b) => { bin += String.fromCharCode(b); });
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function dekodieren(code) {
  const an = new Set();
  try {
    const bin = atob(code.replace(/-/g, "+").replace(/_/g, "/"));
    GAESTE.forEach((g, i) => {
      const b = bin.charCodeAt(i >> 3) || 0;
      if (b & (128 >> (i & 7))) an.add(g.id);
    });
  } catch (fehler) { /* kaputter Code → leerer Plan */ }
  return an;
}

function planLink() {
  const teile = [`p=${kodieren()}`, `s=${state.sprache}`, `z=${state.zeit}`];
  if (state.umstaende.kinder) teile.push("k=1");
  if (state.umstaende.barrierefrei) teile.push("b=1");
  if (state.datum) teile.push(`d=${state.datum}`);
  const basis = window.location.href.split("#")[0];
  return `${basis}#${teile.join("&")}`;
}

function hashLesen() {
  const roh = window.location.hash.replace(/^#/, "");
  const werte = {};
  roh.split("&").forEach((paar) => {
    const [k, v] = paar.split("=");
    if (k) werte[decodeURIComponent(k)] = decodeURIComponent(v || "");
  });
  return werte;
}

/* ---------- Abhaken (nur dieses Gerät) ---------- */

function besuchtLaden() {
  state.besucht = new Set();
  if (!state.code) return;
  try {
    const roh = localStorage.getItem(SPEICHER_PRAEFIX + state.code);
    if (roh) JSON.parse(roh).forEach((id) => state.besucht.add(id));
  } catch (fehler) { /* privater Modus: dann eben ohne Gedächtnis */ }
}

function besuchtSpeichern() {
  if (!state.code) return;
  try { localStorage.setItem(SPEICHER_PRAEFIX + state.code, JSON.stringify([...state.besucht])); }
  catch (fehler) { /* egal */ }
}

/* ---------- Karte ---------- */

let gelaendeInhalt = null;
let gelaendeMasse = { breite: 1006.3, hoehe: 651.968 };
let karteSvg = null;
let markenGruppe = null;
const sicht = { x: 0, y: 0, b: BLATT.breite, h: BLATT.hoehe };

async function ladeGelaende() {
  const antwort = await fetch(GELAENDE_PFAD);
  const text = await antwort.text();
  const wurzel = text.match(/<svg[^>]*>/)[0];
  gelaendeMasse = {
    breite: parseFloat(wurzel.match(/width="([\d.]+)"/)[1]),
    hoehe: parseFloat(wurzel.match(/height="([\d.]+)"/)[1])
  };
  gelaendeInhalt = text.replace(/^[\s\S]*?<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "");
}

function karteBauen() {
  const box = document.getElementById("karte-box");
  const skala = KARTE.gelaende.breite / gelaendeMasse.breite;
  const vars = Object.keys(PALETTE).map((k) => `--karte-${k}:${PALETTE[k]}`).join(";");
  const svgNs = "http://www.w3.org/2000/svg";
  karteSvg = document.createElementNS(svgNs, "svg");
  karteSvg.setAttribute("id", "karte");
  karteSvg.setAttribute("viewBox", `0 0 ${BLATT.breite} ${BLATT.hoehe}`);
  karteSvg.setAttribute("style", vars);
  karteSvg.setAttribute("role", "img");
  karteSvg.setAttribute("aria-label", "Campusplan");
  karteSvg.innerHTML =
    `<rect x="-500" y="-500" width="1300" height="1200" fill="${PALETTE.umgebung}"/>` +
    `<g transform="translate(${KARTE.gelaende.x} ${KARTE.gelaende.y}) scale(${skala})">${gelaendeInhalt}</g>` +
    `<g id="marken"></g>`;
  box.insertBefore(karteSvg, box.firstChild);
  markenGruppe = karteSvg.querySelector("#marken");
  karteBedienung();
}

function gebaeudeFaerben() {
  if (!karteSvg) return;
  karteSvg.querySelectorAll("[data-aktiv]").forEach((el) => el.removeAttribute("data-aktiv"));
  state.an.forEach((id) => {
    ortGebaeude(id).forEach((bauId) => {
      const el = karteSvg.querySelector(`#${bauId}`);
      if (el) el.setAttribute("data-aktiv", "");
    });
  });
}

function stationen() {
  // Nummerierte Stationen in Gehreihenfolge; Anreise separat, ohne Nummer.
  // Grabsteine (thema ‹aus›) und unbekannte IDs aus alten Links fallen still weg.
  const liste = [...state.an].map((id) => gast(id)).filter((g) => g && g.thema !== "aus" && ort(g.id));
  const nummeriert = liste.filter((g) => g.thema !== "anreise").sort((a, b) => a.gehfolge - b.gehfolge);
  const anreise = liste.filter((g) => g.thema === "anreise");
  return { nummeriert, anreise };
}

function markenZeichnen() {
  if (!markenGruppe) return;
  const { nummeriert, anreise } = stationen();
  let markup = "";
  const marke = (id, text, klasse) => {
    const [x, y] = ortPosition(id);
    const fokus = state.fokus === id ? " fokus" : "";
    const besucht = state.besucht.has(id);
    const fuellung = besucht ? MARKE_FARBEN.besucht : (klasse ? MARKE_FARBEN.anreise : MARKE_FARBEN.station);
    const ring = fokus ? MARKE_FARBEN.fokus : MARKE_FARBEN.ring;
    return `<g class="marke${klasse}${fokus}${besucht ? " besucht" : ""}" data-id="${id}" transform="translate(${x} ${y})">` +
      `<circle r="${MARKE_R}" fill="${fuellung}" stroke="${ring}" stroke-width="0.35"/>` +
      `<text font-size="${MARKE_R}" fill="${MARKE_FARBEN.ziffer}">${text}</text></g>`;
  };
  anreise.forEach((g) => { markup += marke(g.id, ortMarker(g.id) || "·", " anreise"); });
  nummeriert.forEach((g, i) => { markup += marke(g.id, String(i + 1), ""); });
  markenGruppe.innerHTML = markup;
}

function sichtSetzen() {
  if (!karteSvg) return;
  karteSvg.setAttribute("viewBox", `${sicht.x} ${sicht.y} ${sicht.b} ${sicht.h}`);
}

function sichtAlle() {
  // Auf alle Marken des Plans einpassen, mindestens 60 mm breit.
  const ids = [...state.an];
  if (!ids.length) { Object.assign(sicht, { x: 0, y: 0, b: BLATT.breite, h: BLATT.hoehe }); sichtSetzen(); return; }
  let minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
  ids.forEach((id) => {
    const [x, y] = ortPosition(id);
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);
  });
  const rand = 12;
  let b = Math.max(60, maxX - minX + 2 * rand);
  let h = Math.max(42, maxY - minY + 2 * rand);
  const seite = seitenverhaeltnis();
  if (b / h < seite) b = h * seite; else h = b / seite;
  sicht.x = (minX + maxX) / 2 - b / 2;
  sicht.y = (minY + maxY) / 2 - h / 2;
  sicht.b = b; sicht.h = h;
  sichtSetzen();
}

function seitenverhaeltnis() {
  const r = karteSvg.getBoundingClientRect();
  return r.height ? r.width / r.height : BLATT.breite / BLATT.hoehe;
}

function zoomUm(faktor, px, py) {
  // px/py in Blatt-mm (Zoomzentrum); ohne Angabe die Mitte.
  const cx = px == null ? sicht.x + sicht.b / 2 : px;
  const cy = py == null ? sicht.y + sicht.h / 2 : py;
  const maxB = BLATT.breite * 1.2, minB = ZOOM_MIN_BREITE;
  let b = sicht.b / faktor;
  b = Math.min(maxB, Math.max(minB, b));
  const f = b / sicht.b;
  sicht.x = cx - (cx - sicht.x) * f;
  sicht.y = cy - (cy - sicht.y) * f;
  sicht.b = b; sicht.h = sicht.h * f;
  sichtSetzen();
}

function punktInMm(clientX, clientY) {
  const r = karteSvg.getBoundingClientRect();
  return [sicht.x + (clientX - r.left) / r.width * sicht.b, sicht.y + (clientY - r.top) / r.height * sicht.h];
}

function zuOrt(id) {
  const [x, y] = ortPosition(id);
  const zielB = Math.min(sicht.b, 70);
  const zielH = zielB / seitenverhaeltnis();
  const start = { ...sicht };
  const ziel = { x: x - zielB / 2, y: y - zielH / 2, b: zielB, h: zielH };
  const t0 = performance.now();
  const dauer = 260;
  function schritt(now) {
    const p = Math.min(1, (now - t0) / dauer);
    const e = 1 - Math.pow(1 - p, 3);
    sicht.x = start.x + (ziel.x - start.x) * e;
    sicht.y = start.y + (ziel.y - start.y) * e;
    sicht.b = start.b + (ziel.b - start.b) * e;
    sicht.h = start.h + (ziel.h - start.h) * e;
    sichtSetzen();
    if (p < 1) requestAnimationFrame(schritt);
  }
  requestAnimationFrame(schritt);
}

function karteBedienung() {
  const zeiger = new Map();
  let start = null;   // { x, y, sicht } bei einem Finger
  let pinch = null;   // { abstand, mitte, sicht } bei zwei Fingern
  let bewegt = false;

  karteSvg.addEventListener("pointerdown", (e) => {
    karteSvg.setPointerCapture(e.pointerId);
    zeiger.set(e.pointerId, [e.clientX, e.clientY]);
    bewegt = false;
    if (zeiger.size === 1) start = { x: e.clientX, y: e.clientY, sicht: { ...sicht } };
    if (zeiger.size === 2) {
      const [a, b] = [...zeiger.values()];
      pinch = { abstand: Math.hypot(a[0] - b[0], a[1] - b[1]),
                mitte: punktInMm((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), sicht: { ...sicht } };
      start = null;
    }
    karteSvg.classList.add("zieht");
  });

  karteSvg.addEventListener("pointermove", (e) => {
    if (!zeiger.has(e.pointerId)) return;
    zeiger.set(e.pointerId, [e.clientX, e.clientY]);
    const r = karteSvg.getBoundingClientRect();
    if (zeiger.size === 1 && start) {
      const dx = (e.clientX - start.x) / r.width * start.sicht.b;
      const dy = (e.clientY - start.y) / r.height * start.sicht.h;
      if (Math.abs(e.clientX - start.x) + Math.abs(e.clientY - start.y) > 4) bewegt = true;
      sicht.x = start.sicht.x - dx; sicht.y = start.sicht.y - dy;
      sichtSetzen();
    } else if (zeiger.size === 2 && pinch) {
      bewegt = true;
      const [a, b] = [...zeiger.values()];
      const abstand = Math.hypot(a[0] - b[0], a[1] - b[1]);
      const f = Math.max(0.2, abstand / pinch.abstand);
      let nb = pinch.sicht.b / f;
      nb = Math.min(BLATT.breite * 1.2, Math.max(ZOOM_MIN_BREITE, nb));
      const nh = nb / (pinch.sicht.b / pinch.sicht.h);
      // Die Blattstelle unter der Fingermitte bleibt unter der Fingermitte.
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
      sicht.b = nb; sicht.h = nh;
      sicht.x = pinch.mitte[0] - (mx - r.left) / r.width * nb;
      sicht.y = pinch.mitte[1] - (my - r.top) / r.height * nh;
      sichtSetzen();
    }
  });

  const loslassen = (e) => {
    zeiger.delete(e.pointerId);
    if (zeiger.size === 0) { karteSvg.classList.remove("zieht"); start = null; pinch = null; }
    if (zeiger.size === 1) { const [p] = [...zeiger.values()]; start = { x: p[0], y: p[1], sicht: { ...sicht } }; pinch = null; }
  };
  karteSvg.addEventListener("pointerup", loslassen);
  karteSvg.addEventListener("pointercancel", loslassen);

  // Tipp auf eine Marke: zur Station in der Liste springen (kein Abhaken —
  // das bleibt beim grossen Kästchen, damit nichts aus Versehen passiert).
  karteSvg.addEventListener("click", (e) => {
    if (bewegt) return;
    const marke = e.target.closest(".marke");
    if (!marke) return;
    fokusSetzen(marke.dataset.id, true);
  });

  karteSvg.addEventListener("wheel", (e) => {
    e.preventDefault();
    const [px, py] = punktInMm(e.clientX, e.clientY);
    zoomUm(e.deltaY < 0 ? 1.25 : 0.8, px, py);
  }, { passive: false });

  document.getElementById("zoom-in").addEventListener("click", () => zoomUm(1.4));
  document.getElementById("zoom-out").addEventListener("click", () => zoomUm(1 / 1.4));
  document.getElementById("zoom-alle").addEventListener("click", sichtAlle);
}

function fokusSetzen(id, zurListe) {
  state.fokus = id;
  document.querySelectorAll(".stn").forEach((el) => el.classList.toggle("fokus", el.dataset.id === id));
  markenGruppe.querySelectorAll(".marke").forEach((el) => el.classList.toggle("fokus", el.dataset.id === id));
  if (zurListe) {
    const zeile = document.querySelector(`.stn[data-id="${id}"]`);
    if (zeile) zeile.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

/* ---------- Oberfläche ---------- */

function textErsetzen() {
  document.querySelectorAll("[data-ui]").forEach((el) => { el.textContent = ui(el.dataset.ui); });
  document.getElementById("titel").textContent = state.modus === "plan" ? ui("besuch") : ui("titel");
  document.getElementById("lede").textContent = ui("lede");
  document.getElementById("s3-frage").textContent = state.modus === "plan" ? ui("besuch") : ui("s3-titel");
  document.documentElement.lang = state.sprache === "en" ? "en" : "de-CH";
  document.querySelectorAll("#sprache-seg button").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.dataset.sprache === state.sprache));
  });
}

function themenZeichnen() {
  const box = document.getElementById("themen");
  box.innerHTML = THEMEN.map((th) =>
    `<button type="button" class="kachel" data-thema="${th.id}" aria-pressed="${state.themen.has(th.id)}">` +
    `<span class="k-name">${t(th.name)}</span><span class="k-kurz">${t(th.kurz)}</span></button>`).join("");
  const um = document.getElementById("umstaende");
  um.innerHTML = UMSTAENDE.map((u) =>
    `<button type="button" data-umstand="${u.id}" aria-pressed="${state.umstaende[u.id]}">${t(u.name)}</button>`).join("");
  document.getElementById("s1-hint").textContent = state.themen.size ? "" : ui("s1-leer");
}

function zeitenZeichnen() {
  const box = document.getElementById("zeiten");
  box.innerHTML = ZEITEN.map((z) =>
    `<button type="button" class="kachel" data-zeit="${z.id}" aria-pressed="${state.zeit === z.id}">` +
    `<span class="k-name">${t(z.name)}</span></button>`).join("");
}

function zeileMarkup(g, nummer, imPlan) {
  const id = g.id;
  const o = ort(id);
  const anreise = g.thema === "anreise";
  const abgehakt = state.besucht.has(id);
  const zugang = g.zugang ? t(ZUGANG[g.zugang]) : "";
  const tag = planTag();
  const zu = ortGeschlossenAm(g, tag);
  const live = ausnahmeAm(g, tag);
  const liveText = live && !live.zu ? ` · <span class="stn-live">${ui("an-diesem-tag")} ${live.text}</span>` : "";
  const meta = [zugang, g.dauer ? dauerText(g.dauer) : "", g.zeiten ? t(g.zeiten) : ""].filter(Boolean).join(" · ")
    + (zu ? ` · <span class="stn-zu">${ui("geschlossen-am")}</span>` : "")
    + liveText
    + (g.ausnahmen && !state.ausnahmen ? ` · <a href="${g.ausnahmen}" target="_blank" rel="noopener">${ui("ausnahmen")}</a>` : "");
  const zeile = g.einzeiler ? `<span class="stn-line">${t(g.einzeiler)}</span>` : "";
  const name = id === "wc-goetheanum" ? ui("wc") : ortName(id);
  const klassen = ["stn", anreise ? "anreise" : "", state.fokus === id ? "fokus" : "", abgehakt ? "abgehakt" : ""].filter(Boolean).join(" ");
  let kasten = "";
  if (!anreise) {
    if (state.modus === "plan") {
      kasten = `<label class="stn-check"><input type="checkbox" data-besucht="${id}" ${abgehakt ? "checked" : ""} aria-label="${name}: ${ui("besucht")}"></label>`;
    } else {
      kasten = `<label class="stn-check"><input type="checkbox" data-dabei="${id}" ${imPlan ? "checked" : ""} aria-label="${name}: ${ui("dabei")}"></label>`;
    }
  }
  const nr = anreise ? "" : `<span class="step-num blue"><b>${nummer}</b></span>`;
  const zeigen = imPlan || state.modus === "plan"
    ? `<button type="button" class="btn stn-karte" data-zeigen="${id}" aria-label="${name}: ${ui("karte-knopf")}">${ui("karte-knopf")}</button>` : "";
  return `<li class="${klassen}" data-id="${id}">${kasten}${nr}` +
    `<span class="stn-text"><span class="stn-name">${name}</span>${zeile}${meta ? `<span class="meta">${meta}</span>` : ""}</span>${zeigen}</li>`;
}

function planZeichnen() {
  const { nummeriert, anreise } = stationen();
  const liste = document.getElementById("stationen");
  liste.innerHTML = nummeriert.map((g, i) => zeileMarkup(g, i + 1, true)).join("") +
    (anreise.length ? `<li class="lab" style="margin-top:var(--s3)">${ui("anreise")}</li>` : "") +
    anreise.map((g) => zeileMarkup(g, "", true)).join("");

  const summe = document.getElementById("summe");
  if (state.modus === "plan") {
    const n = nummeriert.length, b = nummeriert.filter((g) => state.besucht.has(g.id)).length;
    summe.textContent = `${b} ${ui("von")} ${n} ${ui("besucht")}`;
  } else {
    summe.textContent = `${nummeriert.length} ${ui("stationen")} · ${ui("etwa")} ${dauerText(planMinuten())}`;
  }
  const info = document.getElementById("datum-info");
  const tag = planTag();
  if (tag) {
    // Gezählt wird nur, was der Gast überhaupt gewählt hätte: im Erstellen die
    // gewählten Themen, im Plan-Modus alles.
    const zu = GAESTE.filter((g) => g.thema !== "aus" && g.thema !== "anreise" && !state.an.has(g.id)
      && (state.modus === "plan" || state.themen.has(g.thema) || (state.umstaende.kinder && g.kinder))
      && ortGeschlossenAm(g, tag)).length;
    info.textContent = `${datumText(tag)}: ${zu ? `${zu} ${ui(zu === 1 ? "ort-zu" : "orte-zu")}` : ui("alles-offen")}`;
  } else info.textContent = "";

  // Mehr Orte: je gewähltem Thema, was nicht im Plan ist.
  const mehr = document.getElementById("mehr-orte");
  if (state.modus === "plan") { mehr.innerHTML = ""; }
  else {
    const themen = THEMEN.filter((th) => state.themen.has(th.id) || GAESTE.some((g) => g.thema === th.id && state.an.has(g.id)));
    mehr.innerHTML = THEMEN.map((th) => {
      const offen = GAESTE.filter((g) => g.thema === th.id && !state.an.has(g.id)
        && !(state.umstaende.barrierefrei && g.barrierefrei === false));
      if (!offen.length) return "";
      const auf = themen.includes(th) ? " open" : "";
      return `<details class="mehr"${auf}><summary>${ui("mehr-orte")}: ${t(th.name)}</summary>` +
        `<ol class="stationen">${offen.sort((a, b) => a.rang - b.rang).map((g) => zeileMarkup(g, "", false)).join("")}</ol></details>`;
    }).join("");
  }

  // Hinweis auf geschätzte Lagen (Labor; fällt weg, sobald geprüft).
  const lage = document.getElementById("lage-hint");
  const geschaetzt = [...state.an].filter((id) => ort(id) && ort(id).lageGeschaetzt).map(ortName);
  lage.hidden = !geschaetzt.length;
  lage.textContent = geschaetzt.length ? `${ui("lage-hint")} ${geschaetzt.join(", ")}.` : "";

  document.getElementById("ausgabe").hidden = state.modus === "plan";
  document.getElementById("plan-modus").hidden = state.modus !== "plan";
  gebaeudeFaerben();
  markenZeichnen();
}

function schrittZeigen(n) {
  state.schritt = n;
  [1, 2, 3].forEach((i) => { document.getElementById(`s${i}`).hidden = i !== n; });
  document.querySelectorAll("#schritte li").forEach((li) => {
    if (Number(li.dataset.schritt) === n) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
  });
  document.getElementById("schritte").hidden = state.modus === "plan";
  if (n === 3) {
    planZeichnen();
    requestAnimationFrame(sichtAlle);
    document.getElementById("s3").scrollIntoView({ block: "start" });
  }
}

function alles() {
  textErsetzen();
  themenZeichnen();
  zeitenZeichnen();
  if (state.schritt === 3) planZeichnen();
}

/* ---------- Ereignisse ---------- */

function verdrahten() {
  document.getElementById("sprache-seg").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-sprache]");
    if (!b) return;
    state.sprache = b.dataset.sprache;
    alles();
  });

  document.getElementById("themen").addEventListener("click", (e) => {
    const b = e.target.closest(".kachel");
    if (!b) return;
    const id = b.dataset.thema;
    if (state.themen.has(id)) state.themen.delete(id); else state.themen.add(id);
    themenZeichnen();
  });
  document.getElementById("umstaende").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-umstand]");
    if (!b) return;
    state.umstaende[b.dataset.umstand] = !state.umstaende[b.dataset.umstand];
    themenZeichnen();
  });
  document.getElementById("s1-weiter").addEventListener("click", () => schrittZeigen(2));

  document.getElementById("zeiten").addEventListener("click", (e) => {
    const b = e.target.closest(".kachel");
    if (!b) return;
    state.zeit = b.dataset.zeit;
    zeitenZeichnen();
  });
  document.getElementById("s2-zurueck").addEventListener("click", () => schrittZeigen(1));
  document.getElementById("s2-weiter").addEventListener("click", () => { vorauswahl(); linkVerstecken(); schrittZeigen(3); });

  // Schritt 3: Kästchen (dabei / besucht) und Karten-Knöpfe, in Liste und ‹Mehr Orte›.
  const s3 = document.getElementById("s3");
  s3.addEventListener("change", (e) => {
    const el = e.target;
    if (el.dataset.dabei) {
      if (el.checked) state.an.add(el.dataset.dabei); else state.an.delete(el.dataset.dabei);
      linkVerstecken();
      planZeichnen();
    }
    if (el.dataset.besucht) {
      if (el.checked) state.besucht.add(el.dataset.besucht); else state.besucht.delete(el.dataset.besucht);
      besuchtSpeichern();
      planZeichnen();
    }
  });
  s3.addEventListener("click", (e) => {
    const b = e.target.closest("[data-zeigen]");
    if (!b) return;
    fokusSetzen(b.dataset.zeigen, false);
    zuOrt(b.dataset.zeigen);
    if (window.innerWidth < 900) document.getElementById("karte-box").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  document.getElementById("s3-zurueck").addEventListener("click", () => schrittZeigen(2));
  document.getElementById("neu").addEventListener("click", () => {
    state.themen.clear(); state.umstaende = { kinder: false, barrierefrei: false }; state.zeit = "halb"; state.an.clear();
    state.datum = ""; document.getElementById("datum").value = "";
    window.location.hash = "";
    alles(); schrittZeigen(1);
  });
  document.getElementById("datum").addEventListener("change", (e) => { state.datum = e.target.value || ""; });
  ["pdf", "plan-pdf"].forEach((id) => {
    document.getElementById(id).addEventListener("click", async () => {
      const knopf = document.getElementById(id);
      const text = knopf.textContent;
      knopf.disabled = true; knopf.textContent = ui("pdf-laeuft");
      try { await planPdf(); }
      catch (fehler) { console.error(fehler); window.alert(ui("pdf-fehler")); }
      finally { knopf.disabled = false; knopf.textContent = text; }
    });
  });

  document.getElementById("link-kopieren").addEventListener("click", async () => {
    const link = planLink();
    const feld = document.getElementById("linkfeld");
    feld.hidden = false;
    document.getElementById("link-wert").value = link;
    const hint = document.getElementById("link-hint");
    try { await navigator.clipboard.writeText(link); hint.textContent = ui("kopiert"); }
    catch (fehler) { hint.textContent = ui("kopieren-hand"); }
  });
  document.getElementById("qr-zeigen").addEventListener("click", () => {
    const box = document.getElementById("qr-box");
    box.hidden = !box.hidden;
    if (!box.hidden) box.innerHTML = qrMarkup(planLink());
  });

  document.getElementById("plan-aendern").addEventListener("click", () => {
    state.modus = "erstellen";
    // Themen aus dem Plan zurücklesen, damit ‹Mehr Orte› die richtigen Gruppen zeigt.
    state.themen = new Set([...state.an].map((id) => gast(id) && gast(id).thema).filter((th) => th && th !== "basis" && th !== "anreise"));
    window.location.hash = "";
    alles(); schrittZeigen(3);
  });

  window.addEventListener("resize", () => { if (state.schritt === 3) sichtAlle(); });
  // Ein eingefügter Plan-Link im selben Tab lädt die Seite neu — sonst bliebe der alte Zustand stehen.
  window.addEventListener("hashchange", () => { if (hashLesen().p) window.location.reload(); });
}

function linkVerstecken() {
  document.getElementById("linkfeld").hidden = true;
  document.getElementById("qr-box").hidden = true;
}

function qrMarkup(text) {
  if (typeof qrcode !== "function") return `<span class="hint">${text}</span>`;
  const q = qrcode(0, "M");
  q.addData(text);
  q.make();
  const n = q.getModuleCount();
  let pfad = "";
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) pfad += `M${c} ${r}h1v1h-1z`;
  return `<svg viewBox="-2 -2 ${n + 4} ${n + 4}" role="img" aria-label="QR-Code">` +
    `<rect x="-2" y="-2" width="${n + 4}" height="${n + 4}" fill="#ffffff"/>` + /* # ds-ok: QR-Code ist ein Artefakt, immer weiss */
    `<path d="${pfad}" fill="#000000"/></svg>`; /* # ds-ok: QR-Module sind immer schwarz */
}

/* ---------- Start ---------- */

async function start() {
  const h = hashLesen();
  if (h.s === "en") state.sprache = "en";
  if (h.z && ZEITEN.some((z) => z.id === h.z)) state.zeit = h.z;
  state.umstaende.kinder = h.k === "1";
  state.umstaende.barrierefrei = h.b === "1";
  if (/^\d{4}-\d{2}-\d{2}$/.test(h.d || "")) { state.datum = h.d; document.getElementById("datum").value = h.d; }
  verdrahten();
  ausnahmenLaden();
  await ladeGelaende();
  karteBauen();
  if (h.p) {
    state.modus = "plan";
    state.code = h.p;
    state.an = dekodieren(h.p);
    besuchtLaden();
    alles();
    schrittZeigen(3);
  } else {
    alles();
    schrittZeigen(1);
  }
}

start();
