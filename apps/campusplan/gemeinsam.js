"use strict";

/* Campusplan — was Auswahl (index.html) und Telefon (plan.html) teilen:
   Texte, Zustand, Orte, Öffnungs-Ausnahmen, Link-Kodierung, Abhaken.
   Der Plan ist die URL (#p=…), Abhaken lebt im localStorage des Geräts.
   Katalog und Karte kommen aus dem Kartentool (apps/karten-generator/). */

const AUSNAHMEN_URL = "https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/campusplan-ausnahmen";
const SPEICHER_PRAEFIX = "campusplan:";
const PLAN_SEITE = "plan.html";

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
  "heute-zu": { de: "heute geschlossen", en: "closed today" },
  ausnahmen: { de: "aktuelle Ausnahmen", en: "current exceptions" },
  "an-diesem-tag": { de: "an diesem Tag", en: "on this day" },
  "orte-zu": { de: "Orte sind an diesem Tag zu und nicht im Plan", en: "places are closed that day and left out" },
  "ort-zu": { de: "Ort ist an diesem Tag zu und nicht im Plan", en: "place is closed that day and left out" },
  "alles-offen": { de: "alle Orte des Plans sind offen", en: "every place in the plan is open" },
  "fuehrung-hint": { de: "Mit einer Führung ist alles zugänglich, auch die Häuser der Architektursammlung.", en: "With a guided tour everything is accessible, including the houses of the architecture collection." },
  "fuehrung-link": { de: "Führungen buchen", en: "Book a guided tour" },
  "nummer-hint": { de: "Ein Tipp auf eine Nummer in der Liste zeigt den Ort auf der Karte – und umgekehrt.",
                   en: "Tap a number in the list to see the place on the map – and the other way round." },
  "karte-laedt": { de: "Karte wird geladen …", en: "Loading map …" },
  "karte-fehlt": { de: "Die Karte konnte nicht geladen werden. Die Liste gilt trotzdem.", en: "The map could not be loaded. The list still works." },
  "plan-leer": { de: "Dieser Link enthält keinen Plan.", en: "This link holds no plan." },
  "plan-erstellen": { de: "Eigenen Plan zusammenstellen", en: "Put together your own plan" }
};

/* ---------- Zustand ---------- */

const state = {
  sprache: "de",
  modus: "erstellen",         // ‹erstellen› (Auswahl) | ‹plan› (Telefon)
  schritt: 1,
  themen: new Set(),
  umstaende: { kinder: false, barrierefrei: false },
  zeit: "halb",
  an: new Set(),              // Ort-IDs im Plan
  besucht: new Set(),         // Ort-IDs abgehakt (nur Telefon)
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
  if (id === "wc-goetheanum") return ui("wc");
  if (o.teile) return t(o.teile[0]);
  return t(o.label);
}
function ortPosition(id) {
  const o = ort(id);
  if (o.positionen && o.positionen.length) return o.positionen[0];
  if (o.badges && o.badges.length) return [o.badges[0].x, o.badges[0].y];
  return [KARTE.blatt.breite / 2, KARTE.blatt.hoehe / 2];
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

function stationen() {
  // Nummerierte Stationen in Gehreihenfolge; Anreise separat, ohne Nummer.
  // Grabsteine (thema ‹aus›) und unbekannte IDs aus alten Links fallen still weg.
  const liste = [...state.an].map((id) => gast(id)).filter((g) => g && g.thema !== "aus" && ort(g.id));
  const nummeriert = liste.filter((g) => g.thema !== "anreise").sort((a, b) => a.gehfolge - b.gehfolge);
  const anreise = liste.filter((g) => g.thema === "anreise");
  return { nummeriert, anreise };
}

/* ---------- Tage und Öffnungs-Ausnahmen ---------- */

function heuteIso() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Der Tag, für den der Plan gilt: der Besuchstag, am Telefon ohne Datum der heutige.
function planTag() {
  return state.datum || (state.modus === "plan" ? heuteIso() : "");
}

async function ausnahmenLaden(danach) {
  try {
    const r = await fetch(AUSNAHMEN_URL);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    state.ausnahmen = await r.json();
  } catch (fehler) {
    state.ausnahmen = null;   // ohne Live-Daten bleibt der Link auf die Seite
  }
  if (danach) danach();
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

function planHash() {
  const teile = [`p=${kodieren()}`, `s=${state.sprache}`, `z=${state.zeit}`];
  if (state.umstaende.kinder) teile.push("k=1");
  if (state.umstaende.barrierefrei) teile.push("b=1");
  if (state.datum) teile.push(`d=${state.datum}`);
  return `#${teile.join("&")}`;
}

// Der Link führt immer auf die Telefonansicht (plan.html), gleich von welcher Seite.
function planLink() {
  return new URL(PLAN_SEITE, window.location.href.split("#")[0]).href + planHash();
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

// Sprache, Zeit, Umstände und Besuchstag aus dem Hash in den Zustand.
function hashAnwenden(h) {
  if (h.s === "en") state.sprache = "en";
  if (h.z && ZEITEN.some((z) => z.id === h.z)) state.zeit = h.z;
  state.umstaende.kinder = h.k === "1";
  state.umstaende.barrierefrei = h.b === "1";
  if (/^\d{4}-\d{2}-\d{2}$/.test(h.d || "")) state.datum = h.d;
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

/* ---------- Zeile eines Orts: Zugang, Dauer, Zeiten, Tageslage ---------- */

function metaMarkup(g) {
  const zugang = g.zugang ? t(ZUGANG[g.zugang]) : "";
  const tag = planTag();
  const zu = ortGeschlossenAm(g, tag);
  const live = ausnahmeAm(g, tag);
  const zuText = state.modus === "plan" && !state.datum ? ui("heute-zu") : ui("geschlossen-am");
  return [zugang, g.dauer ? dauerText(g.dauer) : "", g.zeiten ? t(g.zeiten) : ""].filter(Boolean).join(" · ")
    + (zu ? ` · <span class="stn-zu">${zuText}</span>` : "")
    + (live && !live.zu ? ` · <span class="stn-live">${ui("an-diesem-tag")} ${live.text}</span>` : "")
    + (g.ausnahmen && !state.ausnahmen ? ` · <a href="${g.ausnahmen}" target="_blank" rel="noopener">${ui("ausnahmen")}</a>` : "");
}
