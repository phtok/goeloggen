"use strict";

/* Campusplan · Telefonansicht. Der Link (#p=…) trägt den Plan; die Seite
   zeigt nur die Karte des Kartentools (zoombar) und die Stationen zum
   Abhaken. Abgehakt wird im localStorage dieses Geräts (gemeinsam.js). */

const ZOOM_MIN_BREITE = 24;   // mm sichtbare Breite bei maximalem Zoom
const MARKE_R = 2.03;         // Markenradius im Kartentool (mm)

// Zeichen auf der Karte, die das Kartentool nicht kennt: Abhak-Haken und
// Fokus-Ring — Artefakt-Farben der Karte wie dort, gerechnet gegen die
// Kartengründe: Grün #226b52 3.2:1 auf dem Campusblau, Weiss darauf 6.4:1.
const ZEICHEN_FARBEN = { besucht: "#226b52", rand: "#ffffff", fokus: "#dfb87a" }; // # ds-ok: Artefakt-Farben der Karte

// Nummern in der Liste tragen die Farbe ihrer Marke — als dunkle Verwandte
// aus der Aquarell-Palette des Kartentools, damit Weiss darauf hält (B01/B02,
// je ≥ 6:1). Schlüssel = Vektorfarbe der Karte.
const LISTEN_FARBEN = { // # ds-ok: Artefakt-Farben der Karte (Kartentool-Paletten)
  "#ec5f6c": "#b23543", "#0061a9": "#0061a9", "#369e7a": "#226b52", // # ds-ok
  "#949596": "#5f6266", "#94702e": "#7a5a20" // # ds-ok
};

let szene = null;             // { markup, farben, lagen, breite, hoehe }
let karteSvg = null;
let zeichenGruppe = null;
const sicht = { x: 0, y: 0, b: 297, h: 210 };

/* ---------- Liste ---------- */

function nummerFarbe(id) {
  const hex = szene && szene.farben[id];
  return (hex && LISTEN_FARBEN[hex.toLowerCase()]) || "";
}

function zeileMarkup(g, nummer, plan) {
  const id = g.id;
  const termin = zeitplanVon(plan, id);
  const aussen = plan && plan.ausserhalb.includes(id);
  const anreise = g.thema === "anreise";
  const abgehakt = state.besucht.has(id);
  const name = ortName(id);
  const meta = metaMarkup(g);
  const farbe = nummerFarbe(id);
  const stil = farbe ? ` style="background:${farbe}"` : "";
  const kasten = anreise ? ""
    : `<label class="stn-check"><input type="checkbox" data-besucht="${id}" ${abgehakt ? "checked" : ""} aria-label="${name}: ${ui("besucht")}"></label>`;
  // Die Nummer ist der Knopf zur Karte (Gegenstück zum Tipp auf die Marke).
  const nr = `<button type="button" class="stn-nr" data-zeigen="${id}" aria-label="${name}: ${ui("karte-knopf")}">` +
    `<span class="step-num blue"${stil}><b>${anreise ? ortMarker(id) || "·" : nummer}</b></span></button>`;
  const klassen = ["stn", anreise ? "anreise" : "", state.fokus === id ? "fokus" : "", abgehakt ? "abgehakt" : ""].filter(Boolean).join(" ");
  return `<li class="${klassen}" data-id="${id}">${kasten}${nr}` +
    `<span class="stn-text">${termin ? `<span class="stn-zeit">${spanneText(termin)}</span>` : ""}<span class="stn-name">${name}</span>` +
    (g.einzeiler ? `<span class="stn-line">${t(g.einzeiler)}</span>` : "") +
    (meta ? `<span class="meta">${meta}</span>` : "") +
    (aussen ? `<span class="meta stn-zu">${ui("ausserhalb")}</span>` : "") + `</span></li>`;
}

function listeZeichnen() {
  const { nummeriert, anreise, plan } = stationen();
  // Mit Zeitplan stehen die Pausen zwischen den Stationen, an ihrem Platz.
  const pausen = {};
  if (plan) {
    plan.eintraege.forEach((e, i) => {
      const naechste = plan.eintraege[i + 1];
      if (e.pause && naechste) pausen[naechste.id] = e;
    });
  }
  document.getElementById("stationen").innerHTML = nummeriert.map((g, i) =>
    (pausen[g.id] ? `<li class="pause hint">${ui("pause-bis")} ${uhrText(pausen[g.id].bis)}${state.sprache === "en" ? "" : " Uhr"}</li>` : "") +
    zeileMarkup(g, i + 1, plan)).join("");
  document.getElementById("anreise").innerHTML = anreise.map((g) => zeileMarkup(g, "", null)).join("");
  document.getElementById("anreise-titel").hidden = !anreise.length;
  const b = nummeriert.filter((g) => state.besucht.has(g.id)).length;
  const tag = state.datum ? ` · ${datumText(state.datum)}` : "";
  document.getElementById("summe").textContent = `${b} ${ui("von")} ${nummeriert.length} ${ui("besucht")}${tag}`;
}

function texteSetzen() {
  document.querySelectorAll("[data-ui]").forEach((el) => { el.textContent = ui(el.dataset.ui); });
  document.getElementById("titel").textContent = ui("besuch");
  document.title = `${ui("besuch")} · Goetheanum`;
  document.documentElement.lang = state.sprache === "en" ? "en" : "de-CH";
  document.querySelectorAll("#sprache-seg button").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.dataset.sprache === state.sprache));
  });
  // ‹Plan ändern› öffnet die Auswahl mit diesem Plan (#e=…), nicht leer.
  document.getElementById("plan-aendern").href = `index.html${planHash().replace("#p=", "#e=")}`;
}

/* ---------- Karte ---------- */

async function karteZeichnen() {
  const { nummeriert, anreise } = stationen();
  const status = document.getElementById("karte-status");
  try {
    szene = await kartenSzene({ nummeriert, anreise, legende: false });
  } catch (fehler) {
    console.warn("Kartentool nicht erreichbar:", fehler);
    status.textContent = ui("karte-fehlt");
    return;
  }
  const svgNs = "http://www.w3.org/2000/svg";
  if (!karteSvg) {
    karteSvg = document.createElementNS(svgNs, "svg");
    karteSvg.setAttribute("role", "img");
    karteSvg.setAttribute("aria-label", ui("besuch"));
    document.getElementById("karte-box").prepend(karteSvg);
    karteBedienung();
  }
  karteSvg.innerHTML = szene.markup + `<g id="zeichen"></g>`;
  zeichenGruppe = karteSvg.querySelector("#zeichen");
  status.hidden = true;
  zeichenSetzen();
  listeZeichnen();          // Nummern bekommen jetzt die Markenfarben
  sichtAlle();
}

// Über der Szene: Haken an abgehakten Stationen, Ring um die gewählte,
// und unsichtbare Trefferflächen (8 mm), damit ein Tipp die Station findet.
function zeichenSetzen() {
  if (!zeichenGruppe) return;
  const { nummeriert, anreise } = stationen();
  let markup = "";
  nummeriert.concat(anreise).forEach((g) => {
    const p = szene.lagen[g.id];
    if (!p) return;
    const [x, y] = p;
    if (state.fokus === g.id) {
      markup += `<circle cx="${x}" cy="${y}" r="${MARKE_R + 1}" fill="none" stroke="${ZEICHEN_FARBEN.fokus}" stroke-width="0.7"/>`;
    }
    if (state.besucht.has(g.id)) {
      const hx = x + MARKE_R * 0.9, hy = y - MARKE_R * 0.9, r = 1.15;
      markup += `<circle cx="${hx}" cy="${hy}" r="${r}" fill="${ZEICHEN_FARBEN.besucht}" stroke="${ZEICHEN_FARBEN.rand}" stroke-width="0.26"/>` +
        `<path d="M${hx - 0.55} ${hy + 0.02}l0.4 0.42l0.75 -0.85" fill="none" stroke="${ZEICHEN_FARBEN.rand}" stroke-width="0.3" stroke-linecap="round" stroke-linejoin="round"/>`;
    }
    markup += `<circle class="treffer" data-id="${g.id}" cx="${x}" cy="${y}" r="4" fill="transparent"/>`;
  });
  zeichenGruppe.innerHTML = markup;
}

function sichtSetzen() {
  if (karteSvg) karteSvg.setAttribute("viewBox", `${sicht.x} ${sicht.y} ${sicht.b} ${sicht.h}`);
}

function seitenverhaeltnis() {
  const r = karteSvg.getBoundingClientRect();
  return r.height ? r.width / r.height : 297 / 210;
}

function sichtAlle() {
  // Auf alle Marken des Plans einpassen, mindestens 60 mm breit.
  if (!szene || !karteSvg) return;
  const punkte = Object.values(szene.lagen);
  let minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
  punkte.forEach(([x, y]) => {
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);
  });
  if (!punkte.length) { minX = 0; minY = 0; maxX = szene.breite; maxY = szene.hoehe; }
  const rand = 8;
  let b = Math.max(60, maxX - minX + 2 * rand);
  let h = Math.max(42, maxY - minY + 2 * rand);
  const seite = seitenverhaeltnis();
  if (b / h < seite) b = h * seite; else h = b / seite;
  Object.assign(sicht, { x: (minX + maxX) / 2 - b / 2, y: (minY + maxY) / 2 - h / 2, b, h });
  sichtSetzen();
}

function zoomUm(faktor, px, py) {
  const cx = px == null ? sicht.x + sicht.b / 2 : px;
  const cy = py == null ? sicht.y + sicht.h / 2 : py;
  const b = Math.min(szene.breite * 1.2, Math.max(ZOOM_MIN_BREITE, sicht.b / faktor));
  const f = b / sicht.b;
  sicht.x = cx - (cx - sicht.x) * f;
  sicht.y = cy - (cy - sicht.y) * f;
  sicht.b = b; sicht.h *= f;
  sichtSetzen();
}

function punktInMm(clientX, clientY) {
  const r = karteSvg.getBoundingClientRect();
  return [sicht.x + (clientX - r.left) / r.width * sicht.b, sicht.y + (clientY - r.top) / r.height * sicht.h];
}

function zuOrt(id) {
  const p = szene && szene.lagen[id];
  if (!p) return;
  const zielB = Math.min(sicht.b, 50);
  const zielH = zielB / seitenverhaeltnis();
  const start = { ...sicht };
  const ziel = { x: p[0] - zielB / 2, y: p[1] - zielH / 2, b: zielB, h: zielH };
  const t0 = performance.now();
  function schritt(jetzt) {
    const q = Math.min(1, (jetzt - t0) / 260);
    const e = 1 - Math.pow(1 - q, 3);
    ["x", "y", "b", "h"].forEach((k) => { sicht[k] = start[k] + (ziel[k] - start[k]) * e; });
    sichtSetzen();
    if (q < 1) requestAnimationFrame(schritt);
  }
  requestAnimationFrame(schritt);
}

function karteBedienung() {
  const zeiger = new Map();
  let start = null;   // ein Finger: { x, y, sicht }
  let pinch = null;   // zwei Finger: { abstand, mitte, sicht }
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
      if (Math.abs(e.clientX - start.x) + Math.abs(e.clientY - start.y) > 4) bewegt = true;
      sicht.x = start.sicht.x - (e.clientX - start.x) / r.width * start.sicht.b;
      sicht.y = start.sicht.y - (e.clientY - start.y) / r.height * start.sicht.h;
      sichtSetzen();
    } else if (zeiger.size === 2 && pinch) {
      bewegt = true;
      const [a, b] = [...zeiger.values()];
      const f = Math.max(0.2, Math.hypot(a[0] - b[0], a[1] - b[1]) / pinch.abstand);
      const nb = Math.min(szene.breite * 1.2, Math.max(ZOOM_MIN_BREITE, pinch.sicht.b / f));
      const nh = nb / (pinch.sicht.b / pinch.sicht.h);
      // Die Blattstelle unter der Fingermitte bleibt unter der Fingermitte.
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
      Object.assign(sicht, { b: nb, h: nh,
        x: pinch.mitte[0] - (mx - r.left) / r.width * nb,
        y: pinch.mitte[1] - (my - r.top) / r.height * nh });
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

  // Tipp auf eine Marke: zur Station in der Liste (Abhaken bleibt beim
  // grossen Kästchen, damit unterwegs nichts aus Versehen passiert).
  karteSvg.addEventListener("click", (e) => {
    if (bewegt) return;
    const treffer = e.target.closest(".treffer");
    if (treffer) fokusSetzen(treffer.dataset.id, true);
  });

  karteSvg.addEventListener("wheel", (e) => {
    e.preventDefault();
    const [px, py] = punktInMm(e.clientX, e.clientY);
    zoomUm(e.deltaY < 0 ? 1.25 : 0.8, px, py);
  }, { passive: false });
}

function fokusSetzen(id, zurListe) {
  state.fokus = id;
  document.querySelectorAll(".stn").forEach((el) => el.classList.toggle("fokus", el.dataset.id === id));
  zeichenSetzen();
  if (zurListe) {
    const zeile = document.querySelector(`.stn[data-id="${id}"]`);
    if (zeile) zeile.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

/* ---------- Ereignisse und Start ---------- */

function verdrahten() {
  document.getElementById("sprache-seg").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-sprache]");
    if (!b) return;
    state.sprache = b.dataset.sprache;
    texteSetzen();
    listeZeichnen();
    karteZeichnen();          // Ortsnamen der Szene in der neuen Sprache
  });
  document.addEventListener("change", (e) => {
    const id = e.target.dataset.besucht;
    if (!id) return;
    if (e.target.checked) state.besucht.add(id); else state.besucht.delete(id);
    besuchtSpeichern();
    listeZeichnen();
    zeichenSetzen();
  });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-zeigen]");
    if (!b) return;
    fokusSetzen(b.dataset.zeigen, false);
    zuOrt(b.dataset.zeigen);
  });
  document.getElementById("zoom-in").addEventListener("click", () => zoomUm(1.4));
  document.getElementById("zoom-out").addEventListener("click", () => zoomUm(1 / 1.4));
  document.getElementById("zoom-alle").addEventListener("click", sichtAlle);
  window.addEventListener("resize", sichtAlle);
  window.addEventListener("hashchange", () => window.location.reload());
}

function start() {
  const h = hashLesen();
  hashAnwenden(h);
  state.modus = "plan";
  state.code = h.p || "";
  state.an = dekodieren(state.code);
  verdrahten();
  texteSetzen();
  if (!state.an.size) {
    // Ohne Plan im Link: kein leeres Blatt, sondern der Weg zur Auswahl.
    document.querySelector(".plan").innerHTML = `<p>${ui("plan-leer")}</p>` +
      `<p><a class="btn primary" href="index.html">${ui("plan-erstellen")}</a></p>`;
    document.getElementById("summe").textContent = "";
    return;
  }
  besuchtLaden();
  listeZeichnen();
  // Kommen die Öffnungszeiten live an, kann sich der Zeitplan ändern —
  // Liste und Nummern der Karte ziehen nach.
  ausnahmenLaden(() => { listeZeichnen(); if (szene) karteZeichnen(); });
  karteZeichnen();
}

start();
