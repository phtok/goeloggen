/* Tagungs-Reader · Logik (Fassung 2: die InDesign-Vorlage ist das Blatt)
   ---------------------------------------------------------------------------
   Die Seiten kommen aus der IDML-Vorlage (vorlage/LT27-Reader.idml), gezeichnet
   von idml-seite.js. Der Jahrgang (jahrgaenge/<jahr>.json, live im Archiv)
   trägt nur, was vom Vorlagenstand abweicht: Texte je Rahmen (story),
   Ersetzungen (Jahreszahlen, Daten), Bilder, Farben, Karte.
   Die Karte (Seiten 2–3) kommt aus dem Kartentool (apps/karten-generator,
   unsichtbar eingebettet) in den Farben der Palette.
   Geschrieben wird direkt im Blatt; jede Änderung landet im Verlauf.
   Konzept: docs/specs/lt-reader-konzept.md · Anleitung: ANLEITUNG.md
   ------------------------------------------------------------------------- */
import { idmlLaden, seiteZeichnen, storyAbsaetze, uebersatzPruefen, farbe as swatchFarbe } from './idml-seite.js';

const SB = "https://dagcsnfrlbpxcmdimnrw.supabase.co";
const SBK = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";
const JAHR_START = 2027;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let S = null;                 // Jahrgang
let DOC = null;               // Vorlage (IDML)
let META = { updated_at: null, von: "" };
let PROG = null;              // Stand der Webseite (apps/lt-programm/webseite.json)
let KARTE = null;             // Kartentool-Schnittstelle (iframe)
let KARTE_SZENE = "";         // SVG-Markup der Blattszene (mm)
let REITER = "stand";
let SPERRE = false;
let bauUhr = null, sichernUhr = null;
const B = $("blaetter"), W = $("werkstatt");

// Seitenplan: welche Quelle welche Seite liefert (20 Seiten, fünf Bogen)
const SEITEN = [];
for (let n = 1; n <= 20; n++) SEITEN.push(n === 2 ? { n, quelle: "karte", haelfte: "links" } : n === 3 ? { n, quelle: "karte", haelfte: "rechts" } : { n, quelle: "vorlage", seite: String(n) });

// Palette des Faltblatts (Farbleiste auf der Montagefläche der Vorlage LT27.idml, 8. 10. 2026)
const PALETTE = [
  ["dunkelblau", "#024363"], ["teal", "#3c7c5a"], ["olive", "#809226"], ["gold", "#d1b03f"], ["beige", "#fbe6d5"],
  ["grau", "#848693"], ["dunkelgruen", "#076857"], ["khaki", "#b5a256"], ["petrol", "#07545c"],
];

// ------------------------------------------------------------ Hilfen
const hex2 = (h) => [1, 3, 5].map((i) => parseInt(String(h).substr(i, 2), 16) || 0);
const hexAus = (r, g, b) => "#" + [r, g, b].map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0")).join("");
const lum = (r, g, b) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
const kontrast = (h1, h2) => { const a = lum(...hex2(h1)), b = lum(...hex2(h2)); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
const mischen = (h, anteil, mit = "#ffffff") => { const a = hex2(h), b = hex2(mit); return hexAus(...a.map((v, i) => v * anteil + b[i] * (1 - anteil))); };
const k1 = (v) => (Math.round(v * 10) / 10).toFixed(1);
const jetzt = () => new Date().toISOString();

// ------------------------------------------------------------ Texte
/* Ersetzung: Leerraum im Suchtext passt auch auf Zeilenumbrüche der Vorlage.
   Ohne ‹seiten› gilt eine Regel auf den Textseiten (nicht Cover, Rückseite, Zeitplan). */
const TEXTSEITEN = [4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19];
function ersetzen(text, n) {
  let t = text;
  for (const e of S.ersetzungen || []) {
    if (!e.von) continue;
    const seiten = Array.isArray(e.seiten) && e.seiten.length ? e.seiten : TEXTSEITEN;
    if (!seiten.includes(n)) continue;
    const re = new RegExp(e.von.trim().split(/\s+/).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("[\\s\\u2028]+"), "g");
    t = t.replace(re, () => e.nach ?? "");
  }
  return t;
}
/* Absätze eines Rahmens: Jahrgangs-Override oder Vorlage mit Ersetzungen */
function storyText(sid, n) {
  if (S.texte && S.texte[sid]) return S.texte[sid];
  const story = DOC.stories[sid]; if (!story) return [];
  const abs = storyAbsaetze(DOC, story);
  return abs.map((a) => ({ ...a, runs: a.runs.map((r) => ({ ...r, text: ersetzen(r.text, n) })) }));
}
const absText = (abs) => abs.map((a) => a.runs.map((r) => r.text).join("")).join("\n");

// Bilder: Link-Dateiname der Vorlage → Datei (relativ zu apps/lt-reader/) oder Daten-URL
function bilder() { return { ...(S.bilder || {}) }; }

// Farben: Swatch-Überschreibungen (Reader-Swatch → Hex) in die Vorlage einspielen
function swatchesAnwenden() {
  if (!DOC) return;
  if (!DOC._farbenOriginal) DOC._farbenOriginal = { ...DOC.farben };
  DOC.farben = { ...DOC._farbenOriginal, ...((S.farben && S.farben.swatches) || {}) };
}

// ------------------------------------------------------------- Seiten
function seiteVorlage(def) {
  const texte = {};
  for (const sid of storiesAufSeite(def.seite)) texte[sid] = storyText(sid, def.n);
  const el = seiteZeichnen(DOC, def.seite, { texte, bilder: bilder(), bearbeitbar: true });
  el.dataset.n = def.n;
  return el;
}
function storiesAufSeite(name) {
  const seite = DOC.seiten[name]; if (!seite) return [];
  return [...new Set([...seite.spread.el.getElementsByTagName("TextFrame")].map((tf) => tf.getAttribute("ParentStory")))];
}
function seiteKarte(def) {
  const el = document.createElement("article");
  el.className = "seite karte-seite"; el.dataset.n = def.n;
  const b = 3, bl = 297, h = 210, falz = 148.5;
  const x0 = def.haelfte === "links" ? -b : falz - b, w = falz + 2 * b;
  el.innerHTML = KARTE_SZENE
    ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x0} ${-b} ${w} ${h + 2 * b}" width="${w}mm" height="${h + 2 * b}mm">${KARTE_SZENE}</svg>`
    : `<div class="leer">Karte: Kartentool lädt …</div>`;
  return el;
}

function bauen() {
  if (!S || !DOC) return;
  swatchesAnwenden();
  const seiten = SEITEN.map((def) => (def.quelle === "karte" ? seiteKarte(def) : seiteVorlage(def)));
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
  const ueber = [];
  B.querySelectorAll(".seite").forEach((el) => { const u = uebersatzPruefen(el); if (u.length) ueber.push(el.dataset.n); });
  B.dataset.ueber = ueber.join(", ");
  standZeigen();
}
function bauenBald() { clearTimeout(bauUhr); bauUhr = setTimeout(bauen, 300); }
function zoomen() {
  const breit = B.clientWidth || 800, seite = 154 / 25.4 * 96;
  const z = window.innerWidth < 700 ? Math.min(1, (breit - 4) / seite) : Math.min(1, (breit - 8) / (2 * seite + 2));
  B.style.setProperty("--z", z.toFixed(3));
}
window.addEventListener("resize", zoomen);

// ------------------------------------------------------- Schreiben im Blatt
/* Aus dem bearbeiteten Rahmen das Absatzmodell zurücklesen (data-stil/data-pattrs/data-run der Zeichnung) */
function modellAusRahmen(tf) {
  const aus = [];
  for (const p of tf.querySelectorAll("p")) {
    let stil = p.dataset.stil, pattrs = {};
    try { pattrs = JSON.parse(p.dataset.pattrs || "{}"); } catch (e) { /* leer */ }
    const abs = { stil, attrs: pattrs, runs: [] };
    const lesen = (node, attrs) => {
      for (const k of node.childNodes) {
        if (k.nodeType === 3) { if (k.textContent) abs.runs.push({ text: k.textContent, attrs }); }
        else if (k.nodeName === "BR") abs.runs.push({ text: " ", attrs });
        else if (k.nodeType === 1) {
          let ra = attrs; if (k.dataset && k.dataset.run) { try { ra = JSON.parse(k.dataset.run); } catch (e) { /* bleibt */ } }
          if (k.classList && k.classList.contains("tab")) abs.runs.push({ text: "\t", attrs: ra });
          else lesen(k, ra);
        }
      }
    };
    lesen(p, {});
    // Zeilenumbrüche (U+2028) an den Nachbarlauf hängen
    const runs = [];
    for (const r of abs.runs) { if (runs.length && JSON.stringify(runs[runs.length - 1].attrs) === JSON.stringify(r.attrs)) runs[runs.length - 1].text += r.text; else runs.push({ ...r }); }
    abs.runs = runs.length ? runs : [{ text: "", attrs: {} }];
    if (!abs.stil && aus.length) abs.stil = aus[aus.length - 1].stil;
    aus.push(abs);
  }
  return aus;
}
let BEARBEITET = null; // { sid, n, vorher }
B.addEventListener("focusin", (e) => {
  const tf = e.target.closest(".tf"); if (!tf) return;
  BEARBEITET = { sid: tf.dataset.story, n: +tf.closest(".seite").dataset.n, vorher: absText(storyText(tf.dataset.story, +tf.closest(".seite").dataset.n)) };
});
B.addEventListener("input", (e) => {
  const tf = e.target.closest(".tf"); if (!tf) return;
  const sid = tf.dataset.story;
  (S.texte ??= {})[sid] = modellAusRahmen(tf);
  (S.pruefung ??= {})[sid] = "geaendert";
  sichernBald();
});
B.addEventListener("focusout", (e) => {
  const tf = e.target.closest(".tf"); if (!tf || !BEARBEITET) return;
  const nachher = absText(S.texte[BEARBEITET.sid] || []);
  if (nachher !== BEARBEITET.vorher) {
    (S.verlauf ??= []).push({ am: jetzt(), von: META.von || "", story: BEARBEITET.sid, seite: BEARBEITET.n, vorher: BEARBEITET.vorher, nachher });
    if (S.verlauf.length > 500) S.verlauf.splice(0, S.verlauf.length - 500);
  }
  BEARBEITET = null;
  // Rahmen neu setzen (Spaltenfluss, Übersatz), ohne die ganze Seite zu verlieren
  bauenBald(); sichernBald();
});
B.addEventListener("paste", (e) => {
  if (!e.target.closest(".tf")) return;
  e.preventDefault();
  document.execCommand("insertText", false, e.clipboardData.getData("text/plain") || "");
});

// ------------------------------------------------------------ Karte
async function karteStarten() {
  if (KARTE) return KARTE;
  const f = document.createElement("iframe");
  f.src = "../karten-generator/?einbett=1"; f.setAttribute("aria-hidden", "true"); f.tabIndex = -1;
  f.style.cssText = "position:absolute;left:-9999px;top:0;width:1200px;height:900px;visibility:hidden";
  document.body.appendChild(f);
  await new Promise((res) => { f.addEventListener("load", res, { once: true }); });
  KARTE = await f.contentWindow.Kartentool.bereit;
  return KARTE;
}
function kartenFarben() {
  const r = (S.farben && S.farben.karte) || {};
  const p = Object.fromEntries(PALETTE);
  return {
    umgebung: r.umgebung || mischen(p.olive, 0.08), "umgebung-hell": r.umgebung || mischen(p.olive, 0.08),
    campus: r.campus || mischen(p.olive, 0.3), gebaeude: r.gebaeude || p.grau, "gebaeude-campus": r["gebaeude-campus"] || p.olive,
    goetheanum: r.goetheanum || p.dunkelgruen, wege: "#ffffff", parkflaeche: r.umgebung || mischen(p.olive, 0.08),
    akzent: r.akzent || p.gold, wiese: r.wiese || mischen(p.teal, 0.35),
  };
}
async function karteZeichnen() {
  try {
    const K = await karteStarten();
    const k = S.karte || {};
    K.anwenden({ titel: "", untertitel: "", sprache: k.sprache || "en", an: k.an || [], kompakt: !!k.kompakt, festeNummern: true, farben: kartenFarben(), preset: "eigene Mischung", positionen: k.positionen || {}, labels: k.labels || {} });
    KARTE_SZENE = K.szene(3);
  } catch (e) { console.warn("Kartentool nicht erreichbar", e); KARTE_SZENE = ""; }
  bauenBald();
}

// ------------------------------------------------------------ Stand
function standZeigen() {
  if (!S) return;
  const p = S.pruefung || {};
  const n = { geprueft: 0, geaendert: 0 }; Object.values(p).forEach((v) => { if (n[v] != null) n[v]++; });
  const wann = META.updated_at ? new Date(META.updated_at).toLocaleString("de-CH", { dateStyle: "short", timeStyle: "short" }) : "noch nicht";
  const ueber = B.dataset.ueber ? ` · <b>Übersatz auf Seite ${esc(B.dataset.ueber)}</b>` : "";
  $("stand").innerHTML = `<b>Jahrgang ${S.jahr}</b> · Vorlage ${esc((S.vorlage || "").split("/").pop())}${ueber}<br>` +
    `${n.geaendert} Rahmen geändert · ${n.geprueft} geprüft · ${(S.verlauf || []).length} Einträge im Verlauf<br>` +
    `gesichert ${wann}${META.von ? ` (${esc(META.von)})` : ""}${SPERRE ? " · <b>gesperrt, bitte neu laden</b>" : ""}`;
}

// --------------------------------------------------------- Werkstatt
$("reiter").addEventListener("click", (e) => { const b = e.target.closest("[data-reiter]"); if (!b) return; REITER = b.dataset.reiter; werkstatt(); });

function werkstatt() {
  if (!S) return;
  $("reiter").querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.reiter === REITER)));
  let h = "";
  if (REITER === "stand") {
    h += `<div class="block"><p class="titel">So geht es</p><p class="hinweis">Texte direkt im Blatt anklicken und schreiben. Jede Änderung wird gesichert und im Verlauf festgehalten. Rot umrandete Rahmen tragen mehr Text, als Platz ist (Übersatz). Zahlen und Daten des Vorjahres werden über die Ersetzungen umgestellt (Reiter ‹Ersetzungen›).</p></div>`;
    const geaendert = Object.entries(S.pruefung || {}).filter(([, v]) => v === "geaendert");
    h += `<div class="block"><p class="titel">Geänderte Rahmen</p>${geaendert.length ? `<ul class="offen">${geaendert.map(([sid]) => `<li>${esc(rahmenName(sid))} <span class="ampel" data-ampel="${esc(sid)}"><button type="button" data-wert="geprueft">geprüft</button><button type="button" class="weg" data-wert="zuruecksetzen">auf Vorlage zurück</button></span></li>`).join("")}</ul>` : `<p class="hinweis">Noch keine Änderung gegenüber der Vorlage.</p>`}</div>`;
  } else if (REITER === "ersetzungen") {
    h += `<div class="block"><p class="titel">Ersetzungen</p><p class="hinweis">Werden beim Setzen auf alle Textseiten angewendet (nicht auf den Zeitplan), in dieser Reihenfolge. So wird aus dem Vorjahrsstand der neue Jahrgang, ohne jeden Rahmen anzufassen.</p>
      <div class="liste">${(S.ersetzungen || []).map((e, i) => `<div class="eintrag"><div class="zeile"><label class="field"><span class="lab">von</span><input type="text" data-pfad="ersetzungen.${i}.von" value="${esc(e.von)}" /></label><label class="field"><span class="lab">nach</span><input type="text" data-pfad="ersetzungen.${i}.nach" value="${esc(e.nach)}" /></label></div>
        <label class="field"><span class="lab">Seiten (leer = alle Textseiten 4–9, 12–19)</span><input type="text" data-pfad="ersetzungen.${i}.seiten" value="${esc((e.seiten || []).join(", "))}" /></label>
        <div class="tat"><button type="button" data-tat="hoch" data-pfad="ersetzungen" data-i="${i}" aria-label="nach oben">↑</button><button type="button" class="weg" data-tat="weg" data-pfad="ersetzungen" data-i="${i}">entfernen</button></div></div>`).join("")}
      <div class="tat"><button type="button" data-tat="neu" data-pfad="ersetzungen" data-neu='{"von":"","nach":""}'>+ Ersetzung</button></div></div></div>`;
  } else if (REITER === "motiv") {
    const motivKey = Object.keys(S.bilder || {}).find((k) => /\.jpe?g$|\.png$/i.test(k) && !/logo|Logo|badge|signet|Element/.test(k)) || "";
    const motiv = motivKey ? S.bilder[motivKey] : "";
    h += `<div class="block"><p class="titel">Motiv</p>${motiv ? `<img class="motivbild" src="${esc(motiv)}" alt="Motiv" />` : `<p class="hinweis">Kein Motiv zugeordnet.</p>`}
      <p class="hinweis">Rahmen der Vorlage: <b>${esc(motivKey || "–")}</b>. Ein neues Bild ersetzt es in der Vorschau; der Druck nimmt die Originaldatei in InDesign.</p>
      <label class="field"><span class="lab">Motiv ersetzen (JPG/PNG)</span><input type="file" id="motiv-datei" accept="image/*" data-key="${esc(motivKey)}" /></label></div>`;
    h += `<div class="block"><p class="titel">Palette des Faltblatts</p><div class="vorschlag">${PALETTE.map(([n, hx]) => `<button type="button" data-palette="${hx}" style="background:${hx}" title="${n} ${hx}" aria-label="${n}"></button>`).join("")}</div>
      <p class="hinweis">Die neun Felder der Farbleiste in der Faltblatt-Vorlage (LT27.idml). Anklicken kopiert den Wert; unten einer Rolle zuweisen.</p></div>`;
    const sw = (S.farben && S.farben.swatches) || {};
    const zeitplan = zeitplanSwatches();
    h += `<div class="block"><p class="titel">Farben des Zeitplans (Seiten 10–11)</p>
      ${zeitplan.map(([ref, name, orig]) => `<div class="farbe"><input type="color" data-swatch="${esc(ref)}" value="${sw[ref] || orig}" aria-label="${esc(name)}" /><span class="lab">${esc(name)}</span><span class="wert">${sw[ref] ? "<b>geändert</b>" : "Vorlage"} ${esc(sw[ref] || orig)}</span></div>`).join("")}
      <div class="knoepfe"><button type="button" class="btn" id="swatches-zurueck">Alle auf Vorlage zurück</button></div></div>`;
    const kf = kartenFarben();
    h += `<div class="block"><p class="titel">Farben der Karte (Rollen des Kartentools)</p>
      ${[["goetheanum", "Goetheanum"], ["gebaeude-campus", "Campus-Gebäude"], ["campus", "Campus-Gelände"], ["umgebung", "Umgebung"], ["gebaeude", "Gebäude Umgebung"], ["wiese", "Wiesen"], ["akzent", "Akzente"]].map(([k, n]) => `<div class="farbe"><input type="color" data-karte="${k}" value="${kf[k]}" aria-label="${n}" /><span class="lab">${n}</span><span class="wert">${k === "goetheanum" || k === "gebaeude-campus" ? `<b>${k1(kontrast("#ffffff", kf[k]))}:1</b> Weiss darauf` : ""}</span></div>`).join("")}
      <p class="hinweis">Vorgabe aus der Palette: Goetheanum dunkelgrün, Campus-Gebäude olive, Gelände und Umgebung als Tönungen davon, Akzente gold. Marken behalten das Feintuning des Kartentools (rote Zielmarken, blaue Orientierung, Treppen-Badges).</p></div>`;
  } else if (REITER === "karte") {
    const orte = KARTE ? KARTE.orte() : [];
    const an = new Set((S.karte || {}).an || []);
    h += `<div class="block"><p class="titel">Karte (Seiten 2–3)</p><p class="hinweis">Gezeichnet vom Kartentool: Legende links, Plan rechts, Ziffernbälle und Treppen-Badges wie dort. Orte an- und abwählen; verschieben und Beschriftungen im <a href="../karten-generator/">Kartentool</a> selbst, der Stand wird hier übernommen (Export → Kartenstand laden).</p>
      <label class="field"><span class="lab">Sprache der Legende</span><select data-pfad="karte.sprache"><option value="en" ${(S.karte || {}).sprache !== "de" ? "selected" : ""}>Englisch</option><option value="de" ${(S.karte || {}).sprache === "de" ? "selected" : ""}>Deutsch</option></select></label>
      <label class="field" style="display:flex;gap:var(--s2);align-items:center"><input type="checkbox" data-pfad="karte.kompakt" ${(S.karte || {}).kompakt ? "checked" : ""}/><span class="lab">kompakte Legende</span></label></div>`;
    const gruppen = {};
    orte.forEach((o) => { (gruppen[o.kategorie] ??= []).push(o); });
    h += `<div class="block"><p class="titel">Orte</p>${Object.entries(gruppen).map(([k, L]) => `<p class="lab">${esc(k)}</p><div class="orte">${L.map((o) => `<label class="ort-wahl"><input type="checkbox" data-ort="${esc(o.id)}" ${an.has(o.id) ? "checked" : ""}/><span class="marke">${esc(o.marker || "")}</span> ${esc((o.label || {}).en || (o.label || {}).de || o.id)}</label>`).join("")}</div>`).join("")}</div>`;
  } else if (REITER === "programm") {
    const n = (PROG && PROG.arbeitsgruppen || []).length;
    h += `<div class="block"><p class="titel">Stand der Webseite</p><p class="hinweis">Quelle: <a href="https://www.agriculture-conference.org/programm">agriculture-conference.org/programm</a>, gelesen vom Tagungsprogramm (<a href="../lt-programm/">apps/lt-programm</a>). Stand: ${esc(PROG && PROG.stand || "–")}, ${n} Arbeitsgruppen.</p>
      <p class="hinweis">Zeitplan (Seiten 10–11) und Arbeitsgruppen (12–15) stehen hier so, wie sie in der Vorlage gesetzt sind. Etappe 3 verbindet sie mit der Webseite: Überschreibungen je Arbeitsgruppen-Nummer, Abgleich mit Protokoll, offene Punkte.</p></div>`;
  } else if (REITER === "verlauf") {
    const V = [...(S.verlauf || [])].reverse();
    h += `<div class="block"><p class="titel">Verlauf</p>${V.length ? `<ul class="verlauf">${V.slice(0, 80).map((v) => `<li><span class="wann">${new Date(v.am).toLocaleString("de-CH", { dateStyle: "short", timeStyle: "short" })}${v.von ? ` · ${esc(v.von)}` : ""} · Seite ${v.seite}</span><br><span class="vorher">${esc(kurz(v.vorher))}</span><br><span class="nachher">${esc(kurz(v.nachher))}</span></li>`).join("")}</ul>` : `<p class="hinweis">Noch keine Änderung.</p>`}</div>`;
  } else if (REITER === "export") {
    h += `<div class="block"><p class="titel">Ausgabe</p>
      <div class="knoepfe"><button type="button" class="btn primary" id="pdf">Vorschau-PDF (Drucken → als PDF sichern)</button><button type="button" class="btn" id="idml" disabled>IDML für InDesign (Etappe 3)</button></div>
      <p class="hinweis">A5 mit 3 mm Beschnitt, RGB, aus dem Browser. Im Druckdialog Hintergrundgrafiken einschalten und Ränder ‹Keine›. Das Druck-PDF entsteht aus dem IDML in InDesign.</p></div>
      <div class="block"><p class="titel">Jahrgangsdatei</p>
      <div class="knoepfe"><button type="button" class="btn" id="json-ab">Herunterladen (JSON)</button><label class="btn" for="json-auf">Laden (JSON)</label><input type="file" id="json-auf" accept="application/json" style="display:none" /><button type="button" class="btn" id="karte-laden">Kartenstand aus dem Kartentool laden</button></div>
      <div class="knoepfe"><button type="button" class="btn" id="jahr-neu">Neues Jahr anlegen (${S.jahr + 1})</button></div>
      <label class="field"><span class="lab">Jahrgang wechseln</span><select id="jahr-wahl"><option value="${S.jahr}">${S.jahr}</option></select></label></div>
      <div class="block"><p class="titel">Fassungen</p><ul class="fassungen" id="fassungen"><li class="hinweis">Lade …</li></ul></div>`;
  }
  W.innerHTML = h;
  if (REITER === "export") { fassungenZeigen(); jahrgaengeZeigen(); }
}
const kurz = (t) => (t.length > 160 ? t.slice(0, 160) + "…" : t);
function rahmenName(sid) {
  const abs = storyText(sid, 0); const t = absText(abs).replace(/\s+/g, " ").trim();
  const n = SEITEN.find((d) => d.quelle === "vorlage" && storiesAufSeite(d.seite).includes(sid));
  return `${n ? `Seite ${n.n} · ` : ""}${t.slice(0, 40)}${t.length > 40 ? "…" : ""}`;
}
// Swatches, die auf dem Zeitplan (Seiten 10–11) Flächen füllen – mit Beispieltext aus dem Rahmen darin
function zeitplanSwatches() {
  const aus = new Map();
  for (const n of ["10", "11"]) {
    const seite = DOC.seiten[n]; if (!seite) continue;
    for (const el of seite.spread.el.querySelectorAll("Rectangle, Polygon")) {
      const ref = el.getAttribute("FillColor");
      if (!ref || ref === "Swatch/None" || ref === "Color/Paper" || /Schwarz|Black|r255g255b255/.test(ref)) continue;
      if (!aus.has(ref)) aus.set(ref, { name: ref.replace(/^Color\//, "").replace(/^Tint\//, "Tönung "), n: 0 });
      aus.get(ref).n++;
    }
  }
  return [...aus.entries()].sort((a, b) => b[1].n - a[1].n).map(([ref, v]) => [ref, `${v.name} (${v.n}×)`, DOC._farbenOriginal ? (DOC._farbenOriginal[ref] || swatchFarbe({ farben: DOC._farbenOriginal, tints: DOC.tints }, ref)) : DOC.farben[ref]]).filter((x) => x[2]);
}

function holen(pfad) { return pfad.split(".").reduce((o, k) => (o == null ? o : o[k]), S); }
function setzen(pfad, wert) { const teile = pfad.split("."), k = teile.pop(); let o = S; for (const t of teile) { o[t] ??= {}; o = o[t]; } o[k] = wert; }

W.addEventListener("input", (e) => {
  const el = e.target;
  if (el.dataset.pfad) { setzen(el.dataset.pfad, el.type === "checkbox" ? el.checked : /\.seiten$/.test(el.dataset.pfad) ? el.value.split(/[,\s]+/).map(Number).filter(Boolean) : el.value); if (/^karte\./.test(el.dataset.pfad)) karteZeichnen(); else bauenBald(); sichernBald(); }
  if (el.dataset.swatch) { ((S.farben ??= {}).swatches ??= {})[el.dataset.swatch] = el.value; bauenBald(); sichernBald(); }
  if (el.dataset.karte) { ((S.farben ??= {}).karte ??= {})[el.dataset.karte] = el.value; karteZeichnen(); sichernBald(); }
});
W.addEventListener("change", async (e) => {
  const el = e.target;
  if (el.dataset.ort) { const an = new Set(((S.karte ??= {}).an ??= [])); el.checked ? an.add(el.dataset.ort) : an.delete(el.dataset.ort); S.karte.an = [...an]; karteZeichnen(); sichernBald(); }
  if (el.id === "motiv-datei") { const f = el.files[0]; if (!f || !el.dataset.key) return; (S.bilder ??= {})[el.dataset.key] = await bildLesen(f, 1800, "image/jpeg"); werkstatt(); bauen(); sichernBald(); }
  if (el.id === "json-auf") { const f = el.files[0]; if (!f) return; try { const d = JSON.parse(await f.text()); if (!d.jahr || !d.vorlage) throw new Error("keine Jahrgangsdatei (Fassung 2)"); S = d; META = { updated_at: null, von: META.von }; SPERRE = false; await nachLaden(); sichern("import"); } catch (err) { melden(`Datei nicht lesbar: ${err.message}`, "bad"); } }
  if (el.id === "jahr-wahl") { const j = +el.value; if (j && j !== S.jahr) laden(j); }
});
W.addEventListener("click", async (e) => {
  const amp = e.target.closest("[data-ampel] button");
  if (amp) {
    const sid = amp.closest("[data-ampel]").dataset.ampel;
    if (amp.dataset.wert === "zuruecksetzen") { delete S.texte[sid]; delete S.pruefung[sid]; (S.verlauf ??= []).push({ am: jetzt(), von: META.von || "", story: sid, seite: 0, vorher: "(Änderung)", nachher: "(auf Vorlage zurückgesetzt)" }); bauen(); }
    else (S.pruefung ??= {})[sid] = amp.dataset.wert;
    werkstatt(); standZeigen(); sichernBald(); return;
  }
  const t = e.target.closest("[data-tat]");
  if (t) {
    const arr = holen(t.dataset.pfad) || (setzen(t.dataset.pfad, []), holen(t.dataset.pfad)); const i = +t.dataset.i;
    if (t.dataset.tat === "neu") arr.push(JSON.parse(t.dataset.neu));
    if (t.dataset.tat === "weg") arr.splice(i, 1);
    if (t.dataset.tat === "hoch" && i > 0) [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
    werkstatt(); bauen(); sichernBald(); return;
  }
  const pal = e.target.closest("[data-palette]");
  if (pal) { try { await navigator.clipboard.writeText(pal.dataset.palette); melden(`${pal.dataset.palette} kopiert`, "ok"); } catch (err) { melden(pal.dataset.palette, "ok"); } return; }
  switch (e.target.id) {
    case "pdf": window.print(); sichern("export-pdf"); break;
    case "json-ab": { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(S, null, 1)], { type: "application/json" })); a.download = `${S.jahr}.json`; a.click(); break; }
    case "jahr-neu": jahrNeu(); break;
    case "swatches-zurueck": if (S.farben) S.farben.swatches = {}; werkstatt(); bauen(); sichernBald(); break;
    case "karte-laden": { // den im Kartentool gespeicherten Stand des Browsers übernehmen
      let roh = null; try { roh = JSON.parse(localStorage.getItem("goetheanum-karten-v2") || "null"); } catch (err) { /* keiner */ }
      if (!roh) { melden("Im Kartentool dieses Browsers ist kein Stand gespeichert.", "bad"); break; }
      S.karte = { ...(S.karte || {}), an: roh.an || [], positionen: roh.positionen || {}, labels: roh.labels || {}, kompakt: !!roh.kompakt, sprache: roh.sprache || "en" };
      karteZeichnen(); werkstatt(); sichernBald(); melden("Kartenstand übernommen.", "ok"); break; }
  }
  const fa = e.target.closest("[data-fassung]");
  if (fa) fassungHerstellen(+fa.dataset.fassung);
});
$("von").addEventListener("input", (e) => { META.von = e.target.value.trim(); try { localStorage.setItem("lt-reader:von", META.von); } catch (err) { /* privat */ } });

function bildLesen(file, max, typ) {
  return new Promise((res, rej) => {
    const img = new Image(); const url = URL.createObjectURL(file);
    img.onload = () => { const s = Math.min(1, max / Math.max(img.width, img.height)); const c = document.createElement("canvas"); c.width = Math.round(img.width * s); c.height = Math.round(img.height * s); c.getContext("2d").drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url); res(c.toDataURL(typ, 0.84)); };
    img.onerror = rej; img.src = url;
  });
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
  if (art === "ok") setTimeout(() => { if (m.classList.contains("ok")) m.remove(); }, 4000);
}
function sichernBald() { try { localStorage.setItem(`lt-reader:${S.jahr}`, JSON.stringify(S)); } catch (e) { /* voll */ } clearTimeout(sichernUhr); sichernUhr = setTimeout(() => sichern(""), 2500); }
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
  try { const L = await rpc("reader_fassungen", { p_jahr: S.jahr }); ul.innerHTML = (L || []).length ? L.map((f) => `<li><button type="button" data-fassung="${f.id}">${new Date(f.am).toLocaleString("de-CH", { dateStyle: "short", timeStyle: "short" })}${f.von ? ` · ${esc(f.von)}` : ""}${f.anlass ? ` <span class="wann">· ${esc(f.anlass)}</span>` : ""}</button></li>`).join("") : `<li class="hinweis">Noch keine Fassung.</li>`; }
  catch (e) { ul.innerHTML = `<li class="hinweis">Archiv nicht erreichbar.</li>`; }
}
async function fassungHerstellen(id) {
  if (!confirm("Diese Fassung herstellen? Der aktuelle Stand wird vorher als Fassung gesichert.")) return;
  await sichern("vor-herstellen");
  try { const st = await rpc("reader_fassung_holen", { p_id: id }); if (st && st.jahr && st.vorlage) { S = st; await nachLaden(); sichern("hergestellt"); } else melden("Diese Fassung stammt aus der alten Werkzeug-Fassung und lässt sich nicht herstellen.", "bad"); } catch (e) { melden(`Fassung nicht geladen (${esc(e.message)})`, "bad"); }
}
async function jahrgaengeZeigen() {
  const sel = $("jahr-wahl"); if (!sel) return;
  try { const L = await rpc("reader_jahrgaenge", {}); const jahre = new Set([S.jahr, JAHR_START, ...(L || []).map((j) => j.jahr)]); sel.innerHTML = [...jahre].sort((a, b) => b - a).map((j) => `<option value="${j}" ${j === S.jahr ? "selected" : ""}>${j}</option>`).join(""); } catch (e) { /* bleibt */ }
}
function jahrNeu() {
  const neu = S.jahr + 1;
  if (!confirm(`Jahrgang ${neu} aus ${S.jahr} anlegen? Texte und Vorlage werden übernommen; die Ersetzungen zählen die Jahreszahl hoch, der Verlauf beginnt neu.`)) return;
  const d = JSON.parse(JSON.stringify(S));
  d.jahr = neu; d.verlauf = []; d.pruefung = {};
  d.ersetzungen = [{ von: String(S.jahr), nach: String(neu), seiten: [1, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20] }, ...(d.ersetzungen || []).filter((e) => !/^\d{4}$/.test(e.von))];
  for (const k of Object.keys(d.tagung || {})) if (typeof d.tagung[k] === "string") d.tagung[k] = d.tagung[k].split(String(S.jahr)).join(String(neu));
  S = d; META = { updated_at: null, von: META.von }; SPERRE = false;
  history.replaceState(null, "", `?jahr=${neu}`); nachLaden().then(() => sichern("neues-jahr"));
}

// ---------------------------------------------------------------- Laden
async function programmLaden() { try { PROG = await (await fetch("../lt-programm/webseite.json")).json(); } catch (e) { PROG = null; } }
async function nachLaden() {
  S.texte ??= {}; S.pruefung ??= {}; S.verlauf ??= []; S.bilder ??= {}; S.farben ??= {}; S.karte ??= {}; S.ersetzungen ??= [];
  if (!DOC || DOC.url !== S.vorlage) { $("stand").textContent = "Lade Vorlage …"; DOC = await idmlLaden(S.vorlage); }
  werkstatt(); bauen(); karteZeichnen();
}
async function laden(jahr) {
  $("stand").textContent = `Lade Jahrgang ${jahr} …`;
  try { META.von = localStorage.getItem("lt-reader:von") || ""; } catch (e) { /* privat */ }
  $("von").value = META.von;
  let stand = null;
  try { const r = await rpc("reader_holen", { p_jahr: jahr }); if (r && r.stand && r.stand.jahr && r.stand.vorlage) { stand = r.stand; META.updated_at = r.updated_at; } }
  catch (e) { melden("Archiv nicht erreichbar – Stand aus dem Repo beziehungsweise diesem Browser.", "bad"); }
  if (!stand) { try { const l = JSON.parse(localStorage.getItem(`lt-reader:${jahr}`) || "null"); if (l && l.vorlage) stand = l; } catch (e) { /* keiner */ } }
  if (!stand) { try { const r = await fetch(`jahrgaenge/${jahr}.json`); if (r.ok) stand = await r.json(); } catch (e) { /* keiner */ } }
  if (!stand || !stand.vorlage) { $("stand").textContent = `Jahrgang ${jahr} gibt es noch nicht. Im Reiter ‹Export› ein neues Jahr anlegen oder eine Jahrgangsdatei laden.`; if (!S) stand = { jahr, vorlage: "vorlage/LT27-Reader.idml", tagung: {} }; else return; }
  S = stand; SPERRE = false;
  if (!PROG) await programmLaden();
  await nachLaden();
}
laden(+(new URLSearchParams(location.search).get("jahr")) || JAHR_START);
