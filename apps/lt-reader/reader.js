/* Tagungs-Reader · Logik
   ---------------------------------------------------------------------------
   Ein Jahrgang ist eine Datei (jahrgaenge/<jahr>.json, live in Supabase
   reader_jahrgang). Dieses Skript setzt daraus die Seiten (bauen), zeigt die
   Werkstätten (werkstatt) und sichert im Hintergrund (sichern).
   Etappe 1 (Gerüst, Inhalte, Vorschau, Speichern, Vorschau-PDF per Druck).
   Konzept: docs/specs/lt-reader-konzept.md
   ------------------------------------------------------------------------- */
"use strict";

const SB = "https://dagcsnfrlbpxcmdimnrw.supabase.co";
const SBK = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";
const JAHR_START = 2027;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let S = null;                 // Jahrgang (die eine Datei)
let META = { updated_at: null, von: "" };
let PROG = null;              // Stand der Webseite (apps/lt-programm/webseite.json)
let KARTE_SVG = null, KARTE_URL = null, KARTE_FARBE = null;
let REITER = "inhalte";
let SPERRE = false;           // true, wenn jemand anderes zuletzt gesichert hat – dann nicht überschreiben
const OFFEN = new Set();      // aufgeklappte Blöcke der Werkstatt
let bauUhr = null, sichernUhr = null;
const SEITE_VON = {};        // Index im Seitenplan → erste Seitenzahl (Arbeitsgruppen füllen mehrere Seiten)

const B = $("blaetter"), W = $("werkstatt");
// Messraum: unsichtbar, aber gesetzt – dort fliessen die Arbeitsgruppen in Spalten.
const MESS = document.createElement("div");
MESS.className = "blaetter"; MESS.setAttribute("aria-hidden", "true");
MESS.style.cssText = "position:absolute;left:-9999px;top:0;visibility:hidden;--z:1";
document.body.appendChild(MESS);

// ------------------------------------------------------------------ Farben
const hex2 = (h) => [1, 3, 5].map((i) => parseInt(String(h).substr(i, 2), 16) || 0);
const hexAus = (r, g, b) => "#" + [r, g, b].map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const lum = (r, g, b) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
function kontrast(h1, h2) { const a = lum(...hex2(h1)), b = lum(...hex2(h2)); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); }
function mischen(h, anteil, mit = "#ffffff") { const a = hex2(h), b = hex2(mit); return hexAus(...a.map((v, i) => v * anteil + b[i] * (1 - anteil))); }
function dunkler(h, ziel, gegen = "#ffffff") { let c = h; for (let i = 0; i < 60 && kontrast(c, gegen) < ziel; i++) c = mischen(c, 0.95, "#000000"); return c; }
const k1 = (v) => (Math.round(v * 10) / 10).toFixed(1);

function farbenAbgeleitet() {
  const f = S.farben || {};
  const acc = f.tagung || "#5f9c23";
  return {
    acc, accDunkel: dunkler(acc, 4.5), accInk: dunkler(f.tinte || acc, 4.5),
    marker: dunkler(f.marker || "#b23543", 4.5), treppe: dunkler(f.treppe || "#0061a9", 4.5),
  };
}
function farbenAnwenden() {
  const f = farbenAbgeleitet();
  for (const el of [B, MESS]) {
    el.style.setProperty("--acc", f.acc); el.style.setProperty("--acc-dunkel", f.accDunkel);
    el.style.setProperty("--acc-ink", f.accInk); el.style.setProperty("--marker", f.marker); el.style.setProperty("--treppe", f.treppe);
  }
}

// ------------------------------------------------------------ Platzhalter
const MON = {
  en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  de: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
  fr: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
  es: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
  it: ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
  nl: ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
};
const WT = { en: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], de: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"] };
function platzhalter() {
  const t = S.tagung || {}, m = { jahr: S.jahr };
  for (const k of Object.keys(t)) m[k] = t[k];
  const start = t.tag1 && /^\d{4}-\d{2}-\d{2}$/.test(t.tag1) ? new Date(t.tag1 + "T12:00:00") : null;
  if (start) for (let n = 1; n <= 5; n++) {
    const d = new Date(start.getTime() + (n - 1) * 864e5), tag = d.getDate(), mo = d.getMonth();
    m[`tag${n}_en`] = `${tag} ${MON.en[mo]}`; m[`tag${n}_de`] = `${tag}. ${MON.de[mo]}`;
    m[`tag${n}_fr`] = `${tag} ${MON.fr[mo]}`; m[`tag${n}_es`] = `${tag} de ${MON.es[mo]}`;
    m[`tag${n}_it`] = `${tag} ${MON.it[mo]}`; m[`tag${n}_nl`] = `${tag} ${MON.nl[mo]}`;
    m[`tag${n}_zh`] = `${mo + 1}月${tag}日`; m[`tag${n}_kurz`] = `${tag}.`;
    m[`wochentag${n}_en`] = WT.en[d.getDay()]; m[`wochentag${n}_de`] = WT.de[d.getDay()];
  }
  return m;
}
let PH = {};
const fuellen = (s) => String(s ?? "").replace(/\{([a-z0-9_]+)\}/g, (m, k) => (k in PH ? PH[k] : m));

// ----------------------------------------------------------------- Satz
function pillen(html) {
  return html.replace(/\[([A-Za-z0-9]{1,3})\]/g, (m, k) => `<span class="pille${/^[A-Za-z]/.test(k) ? " treppe" : ""}">${k}</span>`);
}
const satz = (s) => pillen(fuellen(esc(s)));
function absatz(text, klasse) {
  const t = fuellen(String(text ?? "")).trim();
  if (!t) return "";
  return t.split(/\n\s*\n/).map((p) => {
    const zeilen = p.split("\n").map((z) => (/^>\s?/.test(z) ? `<span class="adresse">${pillen(esc(z.replace(/^>\s?/, "")))}</span>` : pillen(esc(z))));
    return `<p class="${klasse}">${zeilen.join("<br>")}</p>`;
  }).join("");
}
function kopfHtml(b, lang, klein) {
  const en = lang !== "de" && b.kopf_en ? `<span class="en">${satz(b.kopf_en)}</span>` : "";
  const de = lang !== "en" && b.kopf_de ? `<span class="de">${satz(b.kopf_de)}</span>` : "";
  return en || de ? `<h3 class="kopf${klein ? " klein" : ""}">${en}${de}</h3>` : "";
}
const blockVon = (id) => (S.bloecke || []).find((b) => b.id === id);

// Ein Block als HTML (lang = null | "en" | "de" – für Blöcke, die auf einer Seite nach Sprache geteilt stehen)
function blockHtml(ref) {
  const [id, lang] = ref.split("#");
  const b = blockVon(id);
  if (!b) return `<div class="block-seite"><p>Block ‹${esc(id)}› fehlt</p></div>`;
  let inner = "";
  switch (b.art) {
    case "text":
      inner = (lang !== "de" ? absatz(b.en, "en") : "") + (lang !== "en" ? absatz(b.de, "de") : "");
      break;
    case "zeilen":
      inner = absatz(b.en, "en") + absatz(b.de, "de") +
        `<div class="zeilen-liste">${(b.eintraege || []).map((e) => `<div>${e.en ? `<p class="en">${satz(e.en)}</p>` : ""}${e.de ? `<p class="de">${satz(e.de)}</p>` : ""}</div>`).join("")}</div>`;
      break;
    case "orte":
      inner = `<div class="orte-liste">${(b.eintraege || []).map((o) => `<div class="ort">
        <p class="ortname"><span class="en">${satz(o.ort_en)}</span>${o.ort_de ? `<span class="de">${satz(o.ort_de)}</span>` : ""}${(o.marker || "").split(/\s+/).filter(Boolean).map((m) => `<span class="pille${/^[A-Za-z]/.test(m) ? " treppe" : ""}">${esc(m)}</span>`).join("")}</p>
        ${(o.zeiten || []).map((z) => `<p class="zeit">${z.en ? `<span class="en">${satz(z.en)}</span>` : ""}${z.de ? `<span class="de">${satz(z.de)}</span>` : ""}${z.zeit ? `<span class="uhr">${esc(z.zeit)}</span>` : ""}</p>`).join("")}
      </div>`).join("")}</div>`;
      break;
    case "sprachen":
      inner = `<div class="sprachen-liste">${(b.eintraege || []).map((e) => `<div><p class="sprache">${satz(e.sprache)}</p><p class="fremd">${satz(e.text)} ${satz(e.raum)}${e.marker ? ` <span class="pille${/^[A-Za-z]/.test(e.marker) ? " treppe" : ""}">${esc(e.marker)}</span>` : ""}</p></div>`).join("")}</div>`;
      break;
    case "liste":
      inner = `<ul class="pub-liste">${(b.eintraege || []).map((e) => `<li class="${e.laut ? "laut" : ""}">${satz(e.text)}</li>`).join("")}</ul>` +
        (b.nachsatz_en || b.nachsatz_de ? `<div class="nachsatz">${absatz(b.nachsatz_en, "en")}${absatz(b.nachsatz_de, "de")}</div>` : "");
      break;
    case "logos": {
      const L = S.logos || [];
      inner = `<div class="logo-raster">${L.length ? L.map((l) => `<img src="${l.bild}" alt="${esc(l.name)}" />`).join("") : [1, 2, 3, 4, 5, 6].map(() => `<div class="leer">Logo</div>`).join("")}</div>`;
      break;
    }
    case "fuehrungen":
      return `<div class="kaestchen-reihe"><div class="kaestchen">${kopfHtml(b)}<p class="zeit">${esc(b.zeit)}</p>${absatz(b.hinweis_en, "en")}${absatz(b.hinweis_de, "de")}</div>
        ${(b.tage || []).map((t) => `<div><p class="tag-kopf"><span class="en">${satz(t.datum_en)}</span><span class="de">${satz(t.datum_de)}</span></p>
          ${(t.eintraege || []).map((e) => `<div class="fuehrung"><p class="sprache">${esc(e.sprache)}</p><p class="titel">${satz(e.titel)}</p>${e.name ? `<p class="name">${esc(e.name)}</p>` : ""}</div>`).join("")}</div>`).join("")}</div>`;
    case "openspaces":
      return `<div class="kaestchen-reihe"><div class="kaestchen">${kopfHtml(b)}<p class="zeit">${esc(b.zeit)}</p></div>
        ${(b.eintraege || []).map((e) => `<div class="open"><p class="sprache">${esc(e.sprachen)}</p><p class="titel">${satz(e.titel_en)}${e.titel_de ? `<br><span class="de">${satz(e.titel_de)}</span>` : ""}</p>${e.name ? `<p class="name">${esc(e.name)}</p>` : ""}<p class="ort">${satz(e.ort)}${e.wann ? `<br>${satz(e.wann)}` : ""}</p></div>`).join("")}</div>`;
    case "legende":
      return legendeHtml(b);
    default:
      inner = `<p>Unbekannte Blockart ‹${esc(b.art)}›</p>`;
  }
  return `<div class="block-seite" data-block="${esc(id)}">${kopfHtml(b, lang)}${inner}</div>`;
}

function legendeHtml(b) {
  const orte = b.orte || [], h = Math.ceil(orte.length / 2);
  const eintrag = (o) => `<p><span class="pille">${esc(o.nr)}</span><span>${satz(o.name)}</span></p>`;
  const treppen = (b.treppen || []).map((t) => `<div class="gruppe"><p><span class="pille treppe">${esc(t.kuerzel)}</span><span class="en">${satz(t.name)}</span></p>
    ${t.lift ? `<p><span class="pille treppe">${esc(t.kuerzel)}</span><span class="en">${satz(t.lift)}</span></p>` : ""}
    ${String(t.etagen || "").split("\n").filter(Boolean).map((e) => `<p class="etage">${satz(e)}</p>`).join("")}</div>`).join("");
  return `<div class="legende-spalten"><div>${orte.slice(0, h).map(eintrag).join("")}${treppen}</div><div>${orte.slice(h).map(eintrag).join("")}</div></div>`;
}

// ---------------------------------------------------------------- Seiten
function seiteNeu(klasse, inhaltKlasse = "") {
  const el = document.createElement("article");
  el.className = `seite ${klasse}`;
  el.innerHTML = `<div class="inhalt ${inhaltKlasse}"></div>` + schnittmarken();
  return el;
}
function schnittmarken() {
  // 3 mm Beschnitt: Marken an den vier Ecken, nur im Druck sichtbar (CSS)
  const m = [];
  for (const [x, y] of [["left:0", "top:3mm"], ["right:0", "top:3mm"], ["left:0", "bottom:3mm"], ["right:0", "bottom:3mm"]]) m.push(`<i class="marke-s h" style="${x};${y}"></i>`);
  for (const [x, y] of [["left:3mm", "top:0"], ["right:3mm", "top:0"], ["left:3mm", "bottom:0"], ["right:3mm", "bottom:0"]]) m.push(`<i class="marke-s v" style="${x};${y}"></i>`);
  return m.join("");
}
const motivSrc = () => (S.motiv && S.motiv.datei) || "";

function titelSeite() {
  const t = S.tagung || {}, el = seiteNeu("titel-seite", "voll");
  const bild = motivSrc() ? `<img class="motiv" src="${esc(motivSrc())}" alt="" />` : `<div class="ohne"></div>`;
  el.insertAdjacentHTML("afterbegin", bild);
  el.querySelector(".inhalt").style.padding = "11mm 10mm 9mm";
  el.querySelector(".inhalt").innerHTML = `
    <div class="oben"><div class="marke"><img src="../../assets/logos/goetheanum-marke.svg" alt="" /><span>Goetheanum<br>${esc(t.sektion_en)}</span></div>
      <div style="text-align:right">${esc(t.name_en)}<br>${esc(t.datum_en)}</div></div>
    <div class="motto"><div class="en">${esc(t.motto_en)}</div><div class="de">${esc(t.motto_de)}</div></div>
    <div class="unten"><div>${esc(t.name_de)}<br>${esc(t.datum_de)}</div><div class="credit">${esc(t.bildnachweis)}</div></div>`;
  return el;
}
function rueckSeite() {
  const t = S.tagung || {}, el = seiteNeu("rueck-seite", "voll");
  const bild = motivSrc() ? `<img class="motiv" src="${esc(motivSrc())}" alt="" />` : `<div class="ohne"></div>`;
  el.insertAdjacentHTML("afterbegin", bild);
  el.querySelector(".inhalt").style.padding = "11mm 10mm 9mm";
  el.querySelector(".inhalt").innerHTML = `<p class="adresse-block"><span class="en">${esc(t.sektion_en)}</span><span class="de">${esc(t.sektion_de)}</span>${esc(t.adresse)}\n${esc(t.links)}</p>`;
  return el;
}
function textSeite(def) {
  const el = seiteNeu("text-seite");
  el.querySelector(".inhalt").innerHTML = `<div class="reihen">${(def.zeilen || []).map((reihe) =>
    `<div class="reihe${reihe.length === 1 ? " eins" : ""}">${reihe.map((spalte) => `<div class="spalte">${spalte.map(blockHtml).join("")}</div>`).join("")}</div>`).join("")}</div>`;
  return el;
}
function legendeSeite() {
  const el = seiteNeu("text-seite");
  const b = blockVon("legende");
  el.querySelector(".inhalt").innerHTML = b ? legendeHtml(b) : "<p>Block ‹legende› fehlt</p>";
  return el;
}
function karteSeite() {
  const el = seiteNeu("karte-seite", "voll");
  el.querySelector(".inhalt").innerHTML = KARTE_URL ? `<img src="${KARTE_URL}" alt="Campusplan" />` : `<div class="leer">Campusplan – Etappe 2 bringt Marken und Nummern aus dem Kartentool</div>`;
  return el;
}
function leerSeite() { return seiteNeu("leer-seite"); }

// Programm (Seiten 10–11): vorerst schlichte Tagesliste aus dem Stand der Webseite; Etappe 3 setzt die Doppelseite des Faltblatts.
function programmSeite(def) {
  const el = seiteNeu("prog-seite");
  const tage = (PROG && PROG.plenum) || [];
  const teil = def.seite === "links" ? tage.slice(0, 2) : tage.slice(2, 4);
  el.querySelector(".inhalt").innerHTML = `<div class="tage">${teil.map((t) => `<div class="tag"><h3 class="kopf"><span class="en">${esc(WT.en[WT.de.indexOf(t.wochentag)] || t.wochentag)}</span><span class="de">${esc(t.kopf)}</span></h3>
    ${(t.veranstaltungen || []).map((v) => `<div class="punkt-z"><span class="uhr">${esc(v.zeit)}</span><span><span class="en">${esc(v.titel_en || v.art_en)}</span>${v.titel_de || v.art_de ? `<br><span class="de">${esc(v.titel_de || v.art_de)}</span>` : ""}${(v.mitwirkende || []).length ? `<br><span class="wer">${esc(v.mitwirkende.join(" · "))}</span>` : ""}</span></div>`).join("")}</div>`).join("")}</div>
    <p class="etappe">Zeitplan-Doppelseite: kommt in Etappe 3 aus dem Tagungsprogramm (apps/lt-programm). Stand der Webseite: ${esc(PROG && PROG.stand ? PROG.stand : "–")}</p>`;
  return el;
}

// Arbeitsgruppen (Seiten 12–15): fliessen durch drei Spalten, so viele Seiten wie nötig.
function workshopSeiten(def) {
  const items = ((PROG && PROG.arbeitsgruppen) || []).filter((a) => a.block === def.block).sort((a, b) => a.nr - b.nr);
  const vormittag = def.block === "vormittag";
  const kasten = `<div class="kaestchen farbig"><h3 class="kopf"><span class="en">${vormittag ? "Morning Workshops" : "Afternoon Workshops"}</span><span class="de">${vormittag ? "Vormittags Arbeitsgruppen" : "Nachmittags Arbeitsgruppen"}</span></h3><p class="zeit">${vormittag ? "10:45–12:30" : "14:30–16:00"}</p></div>`;
  const seiten = []; let spalten = null, si = 0;
  const neueSeite = (erste) => {
    const el = seiteNeu("ws-seite");
    el.querySelector(".inhalt").innerHTML = `<div class="spalten"><div class="sp"></div><div class="sp"></div><div class="sp"></div></div>`;
    spalten = [...el.querySelectorAll(".sp")]; si = 0;
    MESS.appendChild(el); seiten.push(el);
    if (erste) { spalten[0].innerHTML = kasten; si = 1; }
  };
  neueSeite(true);
  for (const a of items) {
    const w = document.createElement("div"); w.className = "ws";
    const ort = a.ort ? `<p class="ort">${satz(a.ort)}</p>` : "";
    w.innerHTML = `<p class="nr">${a.nr} · ${(a.sprachen || []).join(" · ")}</p><p class="t1">${esc(a.titel_1)}</p>${a.titel_2 ? `<p class="t2">${esc(a.titel_2)}</p>` : ""}<p class="wer">${(a.mitwirkende || []).map(esc).join("<br>")}</p>${ort}`;
    spalten[si].appendChild(w);
    if (spalten[si].scrollHeight > spalten[si].clientHeight + 1 && spalten[si].children.length > 1) {
      spalten[si].removeChild(w); si++;
      if (si > 2) neueSeite(false);
      spalten[si].appendChild(w);
    }
  }
  if (!items.length) spalten[1].innerHTML = `<p class="ws">Keine Arbeitsgruppen im Stand der Webseite (${vormittag ? "Vormittag" : "Nachmittag"}). Werkstatt ‹Programm› → neu laden.</p>`;
  seiten.forEach((s) => s.remove());
  return seiten;
}

function seitenBauen(def) {
  switch (def.art) {
    case "titel": return [titelSeite()];
    case "rueckseite": return [rueckSeite()];
    case "text": return [textSeite(def)];
    case "legende": return [legendeSeite()];
    case "karte": return [karteSeite()];
    case "leer": return [leerSeite()];
    case "programm": return [programmSeite(def)];
    case "workshops": return workshopSeiten(def);
    default: { const el = seiteNeu("leer-seite"); el.querySelector(".inhalt").innerHTML = `<p>Unbekannte Seitenart ‹${esc(def.art)}›</p>`; return [el]; }
  }
}

function bauen() {
  if (!S) return;
  PH = platzhalter(); farbenAnwenden();
  const seiten = [];
  (S.seiten || []).forEach((def, i) => seitenBauen(def).forEach((el) => { el.dataset.seitenplan = i; if (!(i in SEITE_VON) || SEITE_VON[i] > seiten.length + 1) SEITE_VON[i] = seiten.length + 1; seiten.push(el); }));
  for (const k of Object.keys(SEITE_VON)) delete SEITE_VON[k];
  (S.seiten || []).forEach((def, i) => { if (!(i in SEITE_VON)) SEITE_VON[i] = 0; });
  let lauf = 0; seiten.forEach((el) => { const i = +el.dataset.seitenplan; lauf++; if (!SEITE_VON[i]) SEITE_VON[i] = lauf; });
  B.innerHTML = "";
  let i = 0;
  const bogen = (els, label) => {
    const w = document.createElement("div"); w.className = "bogen";
    const d = document.createElement("div"); d.className = "doppel"; els.forEach((e) => d.appendChild(e));
    w.appendChild(d); w.insertAdjacentHTML("beforeend", `<p class="unterschrift">${label}</p>`); B.appendChild(w);
  };
  while (i < seiten.length) {
    if (i === 0 || i === seiten.length - 1) { bogen([seiten[i]], `Seite ${i + 1}`); i++; }
    else { bogen([seiten[i], seiten[i + 1]], `Seite ${i + 1} · ${i + 2}`); i += 2; }
  }
  zoomen();
  const ueber = [], kleiner = [];
  [...B.querySelectorAll(".seite")].forEach((el, n) => {
    const inh = el.querySelector(".inhalt");
    const passt = () => !inh || inh.scrollHeight <= inh.clientHeight + 2;
    // Textseiten atmen: bis 14 % kleiner, bevor sie als Überlauf gelten (der Satz bleibt relativ, em).
    el.style.removeProperty("--grad"); delete el.dataset.grad;
    if (el.classList.contains("text-seite") && !passt()) {
      let g = 1; while (!passt() && g > 0.86) { g = Math.round((g - 0.02) * 100) / 100; el.style.setProperty("--grad", String(g)); }
      el.dataset.grad = String(Math.round(g * 100)); kleiner.push(`${n + 1} (${Math.round(g * 100)} %)`);
    }
    const voll = !passt();
    el.classList.toggle("ueberlauf", voll); if (voll) ueber.push(n + 1);
  });
  B.dataset.seiten = seiten.length; B.dataset.ueber = ueber.join(", "); B.dataset.kleiner = kleiner.join(", ");
  standZeigen();
}
function zoomen() {
  const breit = B.clientWidth || 800, seite = 154 / 25.4 * 96;
  const z = window.innerWidth < 700 ? Math.min(1, (breit - 4) / seite) : Math.min(1, (breit - 8) / (2 * seite + 2));
  B.style.setProperty("--z", z.toFixed(3));
}
window.addEventListener("resize", () => { zoomen(); });
function bauenBald() { clearTimeout(bauUhr); bauUhr = setTimeout(bauen, 250); }

// Karte: die vier Blaustufen des Standardplans werden Stufen der Tagungsfarbe (wie im Folder)
const KARTE_STUFEN = { "#edf5fa": 0.07, "#8abfe5": 0.45, "#5298cc": 0.68, "#0067b2": 1 };
async function karteFaerben() {
  const f = farbenAbgeleitet().acc;
  if (KARTE_FARBE === f && KARTE_URL) return;
  try {
    KARTE_SVG ??= await (await fetch("../programmheft/lageplan-standard.svg")).text();
  } catch (e) { return; }
  let t = KARTE_SVG;
  for (const [alt, anteil] of Object.entries(KARTE_STUFEN)) t = t.split(alt).join(anteil === 1 ? f : mischen(f, anteil));
  if (KARTE_URL) URL.revokeObjectURL(KARTE_URL);
  KARTE_URL = URL.createObjectURL(new Blob([t], { type: "image/svg+xml" })); KARTE_FARBE = f;
  bauenBald();
}

// ---------------------------------------------------------------- Stand
function standZeigen() {
  if (!S) return;
  const p = S.pruefung || {}, ids = (S.bloecke || []).map((b) => b.id).concat(["tagung"]);
  const n = { vorjahr: 0, geprueft: 0, geaendert: 0 };
  ids.forEach((id) => { n[p[id] || "vorjahr"]++; });
  const wann = META.updated_at ? new Date(META.updated_at).toLocaleString("de-CH", { dateStyle: "short", timeStyle: "short" }) : "noch nicht";
  const ueber = (B.dataset.ueber ? ` · <b>läuft über: Seite ${esc(B.dataset.ueber)}</b>` : "") + (B.dataset.kleiner ? ` · verkleinert: Seite ${esc(B.dataset.kleiner)}` : "");
  $("stand").innerHTML = `<b>Jahrgang ${S.jahr}</b> · ${B.dataset.seiten || 0} Seiten${(B.dataset.seiten || 0) % 4 ? " <b>(nicht durch 4 teilbar)</b>" : ""}${ueber}<br>` +
    `${n.vorjahr} vom Vorjahr · ${n.geprueft} geprüft · ${n.geaendert} geändert<br>` +
    `gesichert ${wann}${META.von ? ` (${esc(META.von)})` : ""}${SPERRE ? " · <b>gesperrt, bitte neu laden</b>" : ""}`;
}

// ------------------------------------------------------------- Werkstatt
const KOPF = [["kopf_en", "Kopf EN"], ["kopf_de", "Kopf DE"]];
const FORM = {
  text: { felder: [...KOPF, ["en", "Text EN", "lang"], ["de", "Text DE", "lang"]] },
  zeilen: { felder: [...KOPF, ["en", "Text EN", "lang"], ["de", "Text DE", "lang"]],
    listen: [{ key: "eintraege", titel: "Zeilen", neu: { en: "", de: "" }, felder: [["en", "EN", "kurz"], ["de", "DE", "kurz"]] }] },
  orte: { felder: KOPF, listen: [{ key: "eintraege", titel: "Orte", neu: { ort_en: "", ort_de: "", marker: "", zeiten: [] }, felder: [["ort_en", "Ort EN"], ["ort_de", "Ort DE"], ["marker", "Marken (z. B. 4 oder M)"]],
    listen: [{ key: "zeiten", titel: "Zeiten", neu: { en: "", de: "", zeit: "" }, felder: [["en", "Tag EN"], ["de", "Tag DE"], ["zeit", "Zeit"]] }] }] },
  sprachen: { felder: KOPF, listen: [{ key: "eintraege", titel: "Sprachen", neu: { sprache: "", text: "", raum: "", marker: "" }, felder: [["sprache", "Sprache"], ["text", "Text", "lang"], ["raum", "Raum"], ["marker", "Marke"]] }] },
  liste: { felder: [...KOPF, ["nachsatz_en", "Nachsatz EN", "kurz"], ["nachsatz_de", "Nachsatz DE", "kurz"]],
    listen: [{ key: "eintraege", titel: "Titel", neu: { text: "", laut: false }, felder: [["text", "Titel", "kurz"], ["laut", "Englischer Titel (Deutlich)", "ja"]] }] },
  fuehrungen: { felder: [...KOPF, ["zeit", "Zeit"], ["hinweis_en", "Hinweis EN", "kurz"], ["hinweis_de", "Hinweis DE", "kurz"]],
    listen: [{ key: "tage", titel: "Tage", neu: { datum_en: "", datum_de: "", eintraege: [] }, felder: [["datum_en", "Datum EN"], ["datum_de", "Datum DE"]],
      listen: [{ key: "eintraege", titel: "Führungen", neu: { sprache: "", titel: "", name: "" }, felder: [["sprache", "Sprache"], ["titel", "Titel"], ["name", "Name"]] }] }] },
  openspaces: { felder: [...KOPF, ["zeit", "Zeit"]], listen: [{ key: "eintraege", titel: "Open Spaces", neu: { sprachen: "", titel_en: "", titel_de: "", name: "", ort: "", wann: "" },
    felder: [["sprachen", "Sprachen"], ["titel_en", "Titel EN"], ["titel_de", "Titel DE"], ["name", "Name"], ["ort", "Ort"], ["wann", "Wann"]] }] },
  logos: { felder: KOPF, logos: true },
  legende: { felder: [], listen: [{ key: "orte", titel: "Orte mit Nummer", neu: { nr: "", name: "" }, felder: [["nr", "Nr."], ["name", "Name"]] },
    { key: "treppen", titel: "Treppen und Lifte", neu: { kuerzel: "", name: "", lift: "", etagen: "" }, felder: [["kuerzel", "Kürzel"], ["name", "Treppe"], ["lift", "Lift (leer = keiner)"], ["etagen", "Etagen, eine je Zeile", "kurz"]] }] },
};
const FORM_TAGUNG = { felder: [["name_en", "Tagungsname EN"], ["name_de", "Tagungsname DE"], ["motto_en", "Motto EN"], ["motto_de", "Motto DE"],
  ["datum_en", "Datum EN"], ["datum_de", "Datum DE"], ["tag1", "Erster Tag (JJJJ-MM-TT, für die Platzhalter)"], ["webseite", "Webseite"],
  ["rabattcode", "Rabattcode Aufzeichnungen"], ["aufzeichnung_bis_en", "Aufzeichnungen bis EN"], ["aufzeichnung_bis_de", "Aufzeichnungen bis DE"],
  ["sektion_en", "Sektion EN"], ["sektion_de", "Sektion DE"], ["adresse", "Adresse (Rückseite)", "kurz"], ["links", "Links (Rückseite)", "kurz"], ["bildnachweis", "Bildnachweis"]] };

function feldHtml(pfad, wert, [key, lab, art]) {
  const p = `${pfad}.${key}`;
  if (art === "ja") return `<label class="field" style="display:flex;gap:var(--s2);align-items:center"><input type="checkbox" data-pfad="${p}" ${wert ? "checked" : ""}/><span class="lab">${esc(lab)}</span></label>`;
  if (art === "kurz" || art === "lang") return `<label class="field"><span class="lab">${esc(lab)}</span><textarea data-pfad="${p}" class="${art}">${esc(wert ?? "")}</textarea></label>`;
  return `<label class="field"><span class="lab">${esc(lab)}</span><input type="text" data-pfad="${p}" value="${esc(wert ?? "")}" /></label>`;
}
function formularHtml(obj, pfad, schema) {
  let h = `<div class="felder">${(schema.felder || []).map((f) => feldHtml(pfad, obj[f[0]], f)).join("")}</div>`;
  for (const L of schema.listen || []) {
    const arr = obj[L.key] || [];
    h += `<div class="liste"><span class="lab">${esc(L.titel)}</span>${arr.map((e, i) => `<div class="eintrag">${formularHtml(e, `${pfad}.${L.key}.${i}`, L)}
      <div class="tat"><button type="button" data-tat="hoch" data-pfad="${pfad}.${L.key}" data-i="${i}" aria-label="nach oben">↑</button><button type="button" class="weg" data-tat="weg" data-pfad="${pfad}.${L.key}" data-i="${i}">entfernen</button></div></div>`).join("")}
      <div class="tat"><button type="button" data-tat="neu" data-pfad="${pfad}.${L.key}" data-neu="${esc(JSON.stringify(L.neu))}">+ ${esc(L.titel)}</button></div></div>`;
  }
  return h;
}
function ampelHtml(id) {
  const w = (S.pruefung || {})[id] || "vorjahr";
  return `<span class="ampel" data-ampel="${esc(id)}">${[["vorjahr", "vom Vorjahr"], ["geprueft", "geprüft"]].map(([v, t]) => `<button type="button" data-wert="${v}" aria-pressed="${w === v}">${t}</button>`).join("")}${w === "geaendert" ? `<span class="chip"><b>geändert</b></span>` : ""}</span>`;
}
function blockFormHtml(b, wo) {
  const i = S.bloecke.indexOf(b);
  const schema = FORM[b.art] || { felder: KOPF };
  let extra = "";
  if (schema.logos) extra = logosFormHtml();
  return `<details class="block" data-block="${esc(b.id)}" ${OFFEN.has(b.id) ? "open" : ""}><summary><span class="punkt ${(S.pruefung || {})[b.id] || "vorjahr"}"></span><span class="titel">${esc(fuellen(b.kopf_en || b.kopf_de || b.id))}</span><span class="wo">${esc(wo)}</span></summary>
    ${ampelHtml(b.id)}${formularHtml(b, `bloecke.${i}`, schema)}${extra}</details>`;
}
function logosFormHtml() {
  const L = S.logos || [];
  return `<div class="liste"><span class="lab">Logos (PNG, JPG oder SVG; Reihenfolge wie im Raster)</span>
    <div class="logoliste">${L.map((l, i) => `<div class="eintrag"><img src="${l.bild}" alt="" /><input type="text" data-pfad="logos.${i}.name" value="${esc(l.name)}" aria-label="Name" />
      <div class="tat"><button type="button" data-tat="hoch" data-pfad="logos" data-i="${i}" aria-label="nach oben">↑</button><button type="button" class="weg" data-tat="weg" data-pfad="logos" data-i="${i}">entfernen</button></div></div>`).join("")}</div>
    <label class="field"><span class="lab">Logos hinzufügen</span><input type="file" id="logo-datei" accept="image/*" multiple /></label></div>`;
}

function werkstatt() {
  if (!S) return;
  $("reiter").querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.reiter === REITER)));
  let h = "";
  if (REITER === "inhalte") {
    h += `<details class="block" data-block="tagung" ${OFFEN.has("tagung") ? "open" : ""}><summary><span class="punkt ${(S.pruefung || {}).tagung || "vorjahr"}"></span><span class="titel">Tagung</span><span class="wo">Titel · Rückseite · Platzhalter</span></summary>${ampelHtml("tagung")}${formularHtml(S.tagung, "tagung", FORM_TAGUNG)}
      <p class="hinweis">Platzhalter in Texten: {jahr} {datum_de} {datum_en} {motto_de} {motto_en} {webseite} {rabattcode} {aufzeichnung_bis_de} {aufzeichnung_bis_en}; aus dem ersten Tag: {tag1_de} … {tag4_de}, {tag2_en}, {tag2_fr}, {tag2_es}, {tag2_it}, {tag2_nl}, {tag2_zh}, {tag3_kurz}.</p></details>`;
    const gesehen = new Set();
    (S.seiten || []).forEach((def, n) => {
      const refs = (def.zeilen || []).flat(2).map((r) => r.split("#")[0]);
      if (def.art === "legende") refs.push("legende");
      refs.forEach((id) => { if (gesehen.has(id)) return; gesehen.add(id); const b = blockVon(id); if (b && b.art !== "legende") h += blockFormHtml(b, `Seite ${SEITE_VON[n] || n + 1}`); });
    });
    (S.bloecke || []).forEach((b) => { if (!gesehen.has(b.id) && b.art !== "legende") h += blockFormHtml(b, "auf keiner Seite"); });
    h += `<p class="hinweis">Markierungen im Text: [45] Nummer auf der Karte, [M] [N] [S] Treppe oder Lift. Eine Zeile, die mit › beginnt, steht eingerückt (Adressen).</p>`;
  } else if (REITER === "motiv") {
    const f = farbenAbgeleitet();
    const zeile = (key, lab, wert, probe) => `<div class="farbe"><input type="color" data-pfad="farben.${key}" value="${esc(wert)}" aria-label="${esc(lab)}" /><span class="lab">${esc(lab)}</span><span class="wert ${probe.k < 4.5 ? "bad" : ""}"><b>${k1(probe.k)}:1</b> ${esc(probe.t)}</span></div>`;
    h += `<div class="block"><p class="titel">Motiv</p>
      ${motivSrc() ? `<img class="motivbild" src="${esc(motivSrc())}" alt="Motiv" />` : `<p class="hinweis">Noch kein Motiv. Das Bild des Plakats hochladen – es trägt Titel und Rückseite.</p>`}
      <label class="field"><span class="lab">Motiv hochladen (JPG/PNG, Vorschau; der Druck nimmt die Originaldatei in InDesign)</span><input type="file" id="motiv-datei" accept="image/*" /></label>
      <label class="field"><span class="lab">Bild, Name</span><input type="text" data-pfad="motiv.name" value="${esc(S.motiv && S.motiv.name)}" /></label>
      <div class="knoepfe"><button type="button" class="btn" id="farben-ableiten" ${motivSrc() ? "" : "disabled"}>Farben aus dem Motiv ableiten</button></div>
      <div class="vorschlag" id="vorschlag"></div></div>
      <div class="block"><p class="titel">Farben</p>
      ${zeile("tagung", "Tagungsfarbe (Flächen, Karte)", S.farben.tagung, { k: kontrast("#ffffff", f.accDunkel), t: "Weiss auf der Kopffläche" })}
      ${zeile("tinte", "Tinte (farbige Schrift)", S.farben.tinte || S.farben.tagung, { k: kontrast(f.accInk, "#ffffff"), t: "auf Papier" })}
      ${zeile("marker", "Marke Nummern", S.farben.marker || "#b23543", { k: kontrast("#ffffff", f.marker), t: "Weiss auf der Marke" })}
      ${zeile("treppe", "Marke Treppen", S.farben.treppe || "#0061a9", { k: kontrast("#ffffff", f.treppe), t: "Weiss auf der Marke" })}
      <p class="hinweis">Jede Rolle wird so weit abgedunkelt, dass Weiss darauf beziehungsweise die Tinte auf Papier mindestens 4,5:1 hält (B01/B02). Angezeigt ist der Wert nach dem Abdunkeln. Rollen für die Programm-Doppelseite folgen in Etappe 2.</p></div>`;
  } else if (REITER === "karte") {
    const b = blockVon("legende");
    h += `<p class="meldung">Etappe 2 bringt die Karte aus dem Kartentool: Marken und Nummern aus den Räumen des Programms, Legende automatisch. Vorerst zeigt Seite 3 den Standardplan in der Tagungsfarbe; die Legende auf Seite 2 wird hier gepflegt.</p>`;
    if (b) h += blockFormHtml(b, "Seite 2");
  } else if (REITER === "programm") {
    const n = (PROG && PROG.arbeitsgruppen || []).length, v = (PROG && PROG.arbeitsgruppen || []).filter((a) => a.block === "vormittag").length;
    h += `<div class="block"><p class="titel">Stand der Webseite</p><p class="hinweis">Quelle: <a href="https://www.agriculture-conference.org/programm">agriculture-conference.org/programm</a>, gelesen vom Tagungsprogramm-Werkzeug (<a href="../lt-programm/">apps/lt-programm</a>). Stand: ${esc(PROG && PROG.stand || "–")}.</p>
      <p class="hinweis">${n} Arbeitsgruppen (${v} am Vormittag, ${n - v} am Nachmittag), ${(PROG && PROG.plenum || []).length} Tage Plenum.</p>
      <div class="knoepfe"><button type="button" class="btn" id="prog-laden">Stand neu laden</button><a class="btn" href="../lt-programm/">Tagungsprogramm öffnen</a></div>
      <p class="hinweis">Etappe 3 holt die Webseite direkt hier, meldet offene Punkte (Platzhalter, fehlende Räume) und setzt die Zeitplan-Doppelseite.</p></div>`;
  } else if (REITER === "export") {
    h += `<div class="block"><p class="titel">Ausgabe</p>
      <div class="knoepfe"><button type="button" class="btn primary" id="pdf">Vorschau-PDF (Drucken → als PDF sichern)</button><button type="button" class="btn" id="idml" disabled>IDML für InDesign (Etappe 3)</button></div>
      <p class="hinweis">Das Vorschau-PDF kommt aus dem Browser: A5 mit 3 mm Beschnitt und Schnittmarken, RGB. Im Druckdialog ‹Hintergrundgrafiken› einschalten und Ränder ‹Keine›. Das Druck-PDF für die Druckerei entsteht aus dem IDML in InDesign.</p></div>
      <div class="block"><p class="titel">Jahrgangsdatei</p>
      <div class="knoepfe"><button type="button" class="btn" id="json-ab">Herunterladen (JSON)</button><label class="btn" for="json-auf">Laden (JSON)</label><input type="file" id="json-auf" accept="application/json" style="display:none" /></div>
      <p class="hinweis">Die Datei ist der ganze Jahrgang. Eingecheckt liegt sie unter <a href="https://github.com/phtok/goeloggen/blob/main/apps/lt-reader/jahrgaenge/">apps/lt-reader/jahrgaenge/</a>.</p>
      <div class="knoepfe"><button type="button" class="btn" id="jahr-neu">Neues Jahr anlegen (${S.jahr + 1})</button></div>
      <label class="field"><span class="lab">Jahrgang wechseln</span><select id="jahr-wahl"><option value="${S.jahr}">${S.jahr}</option></select></label></div>
      <div class="block"><p class="titel">Fassungen</p><p class="hinweis">Jede Sicherung, die mehr als zehn Minuten nach der letzten liegt, bleibt als Fassung erhalten. Anklicken stellt sie her (der aktuelle Stand wird vorher als Fassung gesichert).</p><ul class="fassungen" id="fassungen"><li class="hinweis">Lade …</li></ul></div>`;
  }
  W.innerHTML = h;
  if (REITER === "export") { fassungenZeigen(); jahrgaengeZeigen(); }
  if (REITER === "motiv") vorschlagZeigen();
}

// ------------------------------------------------------------ Bedienung
$("reiter").addEventListener("click", (e) => { const b = e.target.closest("[data-reiter]"); if (!b) return; REITER = b.dataset.reiter; werkstatt(); });

function holen(pfad) { return pfad.split(".").reduce((o, k) => (o == null ? o : o[k]), S); }
function setzen(pfad, wert) {
  const teile = pfad.split("."), k = teile.pop(), o = holen(teile.join("."));
  if (o && typeof o === "object") o[k] = wert;
}
function geaendert(pfad) {
  const m = pfad.match(/^bloecke\.(\d+)\./);
  const id = m ? (S.bloecke[+m[1]] || {}).id : /^tagung\./.test(pfad) ? "tagung" : /^logos\b/.test(pfad) ? "support" : null;
  if (!id) return;
  S.pruefung ??= {};
  if (S.pruefung[id] !== "geaendert") { S.pruefung[id] = "geaendert"; const d = W.querySelector(`[data-block="${id}"]`); if (d) { const p = d.querySelector(".punkt"); if (p) p.className = "punkt geaendert"; } }
}
W.addEventListener("input", (e) => {
  const el = e.target.closest("[data-pfad]"); if (!el) return;
  setzen(el.dataset.pfad, el.type === "checkbox" ? el.checked : el.value);
  geaendert(el.dataset.pfad);
  if (/^farben\./.test(el.dataset.pfad)) { farbenAnwenden(); karteFaerben(); }
  bauenBald(); sichernBald();
});
W.addEventListener("toggle", (e) => { const d = e.target.closest("details[data-block]"); if (!d) return; d.open ? OFFEN.add(d.dataset.block) : OFFEN.delete(d.dataset.block); }, true);
W.addEventListener("change", async (e) => {
  if (e.target.id === "logo-datei") { for (const f of e.target.files) { const bild = await bildLesen(f, 800, "image/png"); (S.logos ??= []).push({ name: f.name.replace(/\.[^.]+$/, ""), bild }); } geaendert("logos"); werkstatt(); bauen(); sichernBald(); }
  if (e.target.id === "motiv-datei") { const f = e.target.files[0]; if (!f) return; S.motiv = { ...(S.motiv || {}), datei: await bildLesen(f, 1600, "image/jpeg") }; farbenAbleiten(); werkstatt(); bauen(); sichernBald(); }
  if (e.target.id === "json-auf") { const f = e.target.files[0]; if (!f) return; try { const d = JSON.parse(await f.text()); if (!d.jahr || !d.bloecke) throw new Error("keine Jahrgangsdatei"); S = d; META = { updated_at: null, von: META.von }; SPERRE = false; nachLaden(); sichern("import"); } catch (err) { melden(`Datei nicht lesbar: ${err.message}`, "bad"); } }
  if (e.target.id === "jahr-wahl") { const j = +e.target.value; if (j && j !== S.jahr) laden(j); }
});
W.addEventListener("click", async (e) => {
  const amp = e.target.closest("[data-ampel] button");
  if (amp) { const id = amp.closest("[data-ampel]").dataset.ampel; (S.pruefung ??= {})[id] = amp.dataset.wert; werkstatt(); standZeigen(); sichernBald(); return; }
  const t = e.target.closest("[data-tat]");
  if (t) {
    const arr = holen(t.dataset.pfad) || (setzen(t.dataset.pfad, []), holen(t.dataset.pfad)); const i = +t.dataset.i;
    if (t.dataset.tat === "neu") arr.push(JSON.parse(t.dataset.neu));
    if (t.dataset.tat === "weg") arr.splice(i, 1);
    if (t.dataset.tat === "hoch" && i > 0) [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
    geaendert(t.dataset.pfad + "."); werkstatt(); bauen(); sichernBald(); return;
  }
  switch (e.target.id) {
    case "pdf": window.print(); sichern("export-pdf"); break;
    case "json-ab": { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(S, null, 1)], { type: "application/json" })); a.download = `${S.jahr}.json`; a.click(); break; }
    case "jahr-neu": jahrNeu(); break;
    case "prog-laden": await programmLaden(true); werkstatt(); bauen(); break;
    case "farben-ableiten": farbenAbleiten(); werkstatt(); bauen(); sichernBald(); break;
  }
  const v = e.target.closest("[data-vorschlag]");
  if (v) { S.farben.tagung = v.dataset.vorschlag; S.farben.tinte = dunkler(v.dataset.vorschlag, 4.5); geaendert("tagung."); farbenAnwenden(); karteFaerben(); werkstatt(); bauen(); sichernBald(); }
  const fa = e.target.closest("[data-fassung]");
  if (fa) fassungHerstellen(+fa.dataset.fassung);
});
$("von").addEventListener("input", (e) => { META.von = e.target.value.trim(); try { localStorage.setItem("lt-reader:von", META.von); } catch (err) { /* privat */ } });

function bildLesen(file, max, typ) {
  return new Promise((res, rej) => {
    const img = new Image(); const url = URL.createObjectURL(file);
    img.onload = () => {
      const s = Math.min(1, max / Math.max(img.width, img.height));
      const c = document.createElement("canvas"); c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
      res(c.toDataURL(typ, 0.84));
    };
    img.onerror = rej; img.src = url;
  });
}

// Farben aus dem Motiv: die häufigsten gesättigten Mitteltöne als Vorschlag, der erste wird Tagungsfarbe.
let VORSCHLAG = [];
function farbenAbleiten() {
  const img = new Image();
  img.onload = () => {
    const c = document.createElement("canvas"); c.width = 60; c.height = Math.round(60 * img.height / img.width) || 80;
    const ctx = c.getContext("2d"); ctx.drawImage(img, 0, 0, c.width, c.height);
    const d = ctx.getImageData(0, 0, c.width, c.height).data, bins = new Map();
    for (let i = 0; i < d.length; i += 4) {
      const r = d[i], g = d[i + 1], b = d[i + 2], mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 510, s = mx === mn ? 0 : (mx - mn) / (1 - Math.abs(2 * l - 1)) / 255;
      if (s < 0.25 || l < 0.18 || l > 0.68) continue;
      const k = `${r >> 5},${g >> 5},${b >> 5}`; const e = bins.get(k) || { n: 0, r: 0, g: 0, b: 0 }; e.n++; e.r += r; e.g += g; e.b += b; bins.set(k, e);
    }
    VORSCHLAG = [...bins.values()].sort((a, b) => b.n - a.n).slice(0, 6).map((e) => hexAus(e.r / e.n, e.g / e.n, e.b / e.n));
    if (VORSCHLAG[0]) { S.farben.tagung = VORSCHLAG[0]; S.farben.tinte = dunkler(VORSCHLAG[0], 4.5); geaendert("tagung."); farbenAnwenden(); karteFaerben(); }
    vorschlagZeigen(); bauen(); sichernBald();
  };
  img.src = motivSrc();
}
function vorschlagZeigen() {
  const v = $("vorschlag"); if (!v) return;
  v.innerHTML = VORSCHLAG.map((h) => `<button type="button" data-vorschlag="${h}" style="background:${h}" aria-pressed="${h === S.farben.tagung}" aria-label="${h}" title="${h}"></button>`).join("");
}

// ------------------------------------------------------------ Speichern
async function rpc(name, body) {
  const r = await fetch(`${SB}/rest/v1/rpc/${name}`, { method: "POST", headers: { "Content-Type": "application/json", apikey: SBK, Authorization: `Bearer ${SBK}` }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
  const t = await r.text(); return t ? JSON.parse(t) : null;
}
function melden(text, art = "") {
  let m = $("meldung"); if (!m) { m = document.createElement("p"); m.id = "meldung"; $("leiste").insertBefore(m, $("reiter")); }
  m.className = `meldung ${art}`; m.innerHTML = text;
}
function sichernBald() { try { localStorage.setItem(`lt-reader:${S.jahr}`, JSON.stringify(S)); } catch (e) { /* voll oder privat */ } clearTimeout(sichernUhr); sichernUhr = setTimeout(() => sichern(""), 2500); }
async function sichern(anlass) {
  if (!S || SPERRE) return;
  clearTimeout(sichernUhr);
  try {
    const r = await rpc("reader_sichern", { p_jahr: S.jahr, p_stand: S, p_von: META.von || "", p_seit: META.updated_at, p_anlass: anlass || "" });
    if (r && r.status === "ok") { META.updated_at = r.updated_at; standZeigen(); const m = $("meldung"); if (m && /nicht gesichert/.test(m.textContent)) m.remove(); }
    else if (r && r.status === "ueberholt") { SPERRE = true; melden(`Nicht gesichert: ${esc(r.von || "jemand anderes")} hat um ${new Date(r.updated_at).toLocaleTimeString("de-CH", { timeStyle: "short" })} einen neueren Stand gesichert. <button type="button" class="btn" onclick="location.reload()">Neu laden</button>`, "bad"); standZeigen(); }
    else melden(`Nicht gesichert (${esc(r && r.status)}).`, "bad");
  } catch (e) { melden(`Nicht gesichert – kein Zugang zum Archiv (${esc(e.message)}). Die Änderungen bleiben in diesem Browser.`, "bad"); }
}
async function fassungenZeigen() {
  const ul = $("fassungen"); if (!ul) return;
  try {
    const L = await rpc("reader_fassungen", { p_jahr: S.jahr });
    ul.innerHTML = (L || []).length ? L.map((f) => `<li><button type="button" data-fassung="${f.id}">${new Date(f.am).toLocaleString("de-CH", { dateStyle: "short", timeStyle: "short" })}${f.von ? ` · ${esc(f.von)}` : ""}${f.anlass ? ` <span class="wann">· ${esc(f.anlass)}</span>` : ""}</button></li>`).join("") : `<li class="hinweis">Noch keine Fassung.</li>`;
  } catch (e) { ul.innerHTML = `<li class="hinweis">Archiv nicht erreichbar.</li>`; }
}
async function fassungHerstellen(id) {
  if (!confirm("Diese Fassung herstellen? Der aktuelle Stand wird vorher als Fassung gesichert.")) return;
  await sichern("vor-herstellen");
  try { const st = await rpc("reader_fassung_holen", { p_id: id }); if (st && st.jahr) { S = st; nachLaden(); sichern("hergestellt"); } } catch (e) { melden(`Fassung nicht geladen (${esc(e.message)})`, "bad"); }
}
async function jahrgaengeZeigen() {
  const sel = $("jahr-wahl"); if (!sel) return;
  try {
    const L = await rpc("reader_jahrgaenge", {}); const jahre = new Set([S.jahr, JAHR_START, ...(L || []).map((j) => j.jahr)]);
    sel.innerHTML = [...jahre].sort((a, b) => b - a).map((j) => `<option value="${j}" ${j === S.jahr ? "selected" : ""}>${j}</option>`).join("");
  } catch (e) { /* bleibt beim aktuellen */ }
}
function jahrNeu() {
  const neu = S.jahr + 1;
  if (!confirm(`Jahrgang ${neu} aus ${S.jahr} anlegen? Texte werden übernommen und als ‹vom Vorjahr› markiert; Motiv, Logos und Farben beginnen neu.`)) return;
  const d = JSON.parse(JSON.stringify(S));
  d.jahr = neu; d.fassung = 1; d.logos = []; d.motiv = { datei: "", name: "" };
  d.pruefung = {}; (d.bloecke || []).forEach((b) => { d.pruefung[b.id] = "vorjahr"; }); d.pruefung.tagung = "vorjahr";
  for (const k of Object.keys(d.tagung)) if (typeof d.tagung[k] === "string") d.tagung[k] = d.tagung[k].split(String(S.jahr)).join(String(neu));
  S = d; META = { updated_at: null, von: META.von }; SPERRE = false;
  history.replaceState(null, "", `?jahr=${neu}`); nachLaden(); sichern("neues-jahr");
}

// ---------------------------------------------------------------- Laden
async function programmLaden(frisch) {
  try { PROG = await (await fetch(`../lt-programm/webseite.json${frisch ? `?t=${Date.now()}` : ""}`)).json(); } catch (e) { PROG = null; }
}
function nachLaden() {
  S.farben ??= { tagung: "#5f9c23" }; S.pruefung ??= {}; S.logos ??= []; S.tagung ??= {};
  farbenAnwenden(); karteFaerben(); werkstatt(); bauen();
}
async function laden(jahr) {
  $("stand").textContent = `Lade Jahrgang ${jahr} …`;
  try { META.von = localStorage.getItem("lt-reader:von") || ""; } catch (e) { /* privat */ }
  $("von").value = META.von;
  let stand = null;
  try { const r = await rpc("reader_holen", { p_jahr: jahr }); if (r && r.stand && r.stand.jahr) { stand = r.stand; META.updated_at = r.updated_at; } }
  catch (e) { melden("Archiv nicht erreichbar – Stand aus dem Repo beziehungsweise diesem Browser.", "bad"); }
  if (!stand) { try { const l = localStorage.getItem(`lt-reader:${jahr}`); if (l) stand = JSON.parse(l); } catch (e) { /* keiner */ } }
  if (!stand) { try { const r = await fetch(`jahrgaenge/${jahr}.json`); if (r.ok) stand = await r.json(); } catch (e) { /* keiner */ } }
  if (!stand) { $("stand").textContent = `Jahrgang ${jahr} gibt es noch nicht. Im Reiter ‹Export› ein neues Jahr anlegen oder eine Jahrgangsdatei laden.`; if (!S) { stand = { jahr, tagung: {}, bloecke: [], seiten: [], farben: { tagung: "#5f9c23" } }; } else return; }
  S = stand; SPERRE = false;
  if (!PROG) await programmLaden(false);
  nachLaden();
}
laden(+(new URLSearchParams(location.search).get("jahr")) || JAHR_START);
