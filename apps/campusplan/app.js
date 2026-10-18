"use strict";

/* Campusplan für Gäste — die Auswahl (Laborseite, Konzept § 13).
   Eine Seite, keine Schritte: Interessen, Zeit und Besuchstag wählen, der
   Plan darunter füllt sich sofort. Mitgenommen wird er als A4-Blatt (pdf.js,
   Karte des Kartentools) oder als Link aufs Telefon (plan.html). Die Karte
   selbst steht hier nicht — sie gehört zu den beiden Ausgaben.
   Gemeinsames (Texte, Zustand, Link, Öffnungszeiten, Zeitplan) in gemeinsam.js. */

/* ---------- Vorauswahl ---------- */

function budgetMinuten() {
  const z = ZEITEN.find((x) => x.id === state.zeit) || ZEITEN[1];
  return z.minuten;
}

function immerDabei() {
  return GAESTE.filter((g) => (g.thema === "basis" || g.thema === "anreise")
    && (!g.nurBarrierefrei || state.umstaende.barrierefrei)).map((g) => g.id);
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

/* ---------- Oberfläche ---------- */

function texteSetzen() {
  document.querySelectorAll("[data-ui]").forEach((el) => { el.textContent = ui(el.dataset.ui); });
  document.documentElement.lang = state.sprache === "en" ? "en" : "de-CH";
  document.querySelectorAll("#sprache-seg button").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.dataset.sprache === state.sprache));
  });
}

function wahlZeichnen() {
  document.getElementById("themen").innerHTML = THEMEN.map((th) =>
    `<button type="button" class="kachel" data-thema="${th.id}" aria-pressed="${state.themen.has(th.id)}">` +
    `<span class="k-name">${t(th.name)}</span><span class="k-kurz">${t(th.kurz)}</span></button>`).join("");
  document.getElementById("umstaende").innerHTML = UMSTAENDE.map((u) =>
    `<button type="button" data-umstand="${u.id}" aria-pressed="${state.umstaende[u.id]}">${t(u.name)}</button>`).join("");
  document.getElementById("zeiten").innerHTML = ZEITEN.map((z) =>
    `<button type="button" class="kachel" data-zeit="${z.id}" aria-pressed="${state.zeit === z.id}">` +
    `<span class="k-name">${t(z.name)}</span></button>`).join("");
}

function zeileMarkup(g, nummer, imPlan, plan) {
  const id = g.id;
  const anreise = g.thema === "anreise";
  const name = ortName(id);
  const meta = metaMarkup(g);
  const termin = imPlan ? zeitplanVon(plan, id) : null;
  const ausserhalb = imPlan && plan && plan.ausserhalb.includes(id);
  const kasten = anreise ? ""
    : `<label class="stn-check"><input type="checkbox" data-dabei="${id}" ${imPlan ? "checked" : ""} aria-label="${name}: ${ui("dabei")}"></label>`;
  const nr = anreise ? "" : imPlan ? `<span class="step-num blue"><b>${nummer}</b></span>` : "";
  const klassen = ["stn", anreise ? "anreise" : "", !anreise && !imPlan ? "weg-aus" : ""].filter(Boolean).join(" ");
  return `<li class="${klassen}" data-id="${id}">${kasten}${nr}<span class="stn-text">` +
    (termin ? `<span class="stn-zeit">${spanneText(termin)}</span>` : "") +
    `<span class="stn-name">${name}</span>` +
    (g.einzeiler ? `<span class="stn-line">${t(g.einzeiler)}</span>` : "") +
    (meta ? `<span class="meta">${meta}</span>` : "") +
    (ausserhalb ? `<span class="meta stn-zu">${ui("ausserhalb")}</span>` : "") + `</span></li>`;
}

function planZeichnen() {
  const { nummeriert, anreise, plan } = stationen();
  const pausen = {};
  if (plan) plan.eintraege.forEach((e, i) => { const n = plan.eintraege[i + 1]; if (e.pause && n) pausen[n.id] = e; });
  document.getElementById("stationen").innerHTML = nummeriert.map((g, i) =>
    (pausen[g.id] ? `<li class="pause hint">${ui("pause-bis")} ${uhrText(pausen[g.id].bis)}${state.sprache === "en" ? "" : " Uhr"}</li>` : "") +
    zeileMarkup(g, i + 1, true, plan)).join("");
  document.getElementById("anreise").innerHTML = anreise.map((g) => zeileMarkup(g, "", true, null)).join("");
  document.getElementById("anreise-titel").hidden = !anreise.length;

  const spanne = plan && plan.eintraege.length ? spanneText({ von: plan.eintraege[0].von, bis: plan.ende })
    : `${ui("etwa")} ${dauerText(planMinuten())}`;
  const tag = state.datum ? `${datumText(state.datum)} · ` : "";
  document.getElementById("summe").textContent = `${tag}${nummeriert.length} ${ui("stationen")} · ${spanne}`;

  // Ein Hinweis, nicht mehrere: ohne Thema der Weg dorthin, mit Besuchstag,
  // was an dem Tag zu ist.
  const hinweis = document.getElementById("plan-hint");
  let text = "";
  if (!state.themen.size && !state.umstaende.kinder) text = ui("s1-leer");
  else if (state.datum) {
    const zu = GAESTE.filter((g) => g.thema !== "aus" && g.thema !== "anreise" && !state.an.has(g.id)
      && (state.themen.has(g.thema) || (state.umstaende.kinder && g.kinder))
      && ortGeschlossenAm(g, state.datum)).length;
    if (zu) text = `${zu} ${ui(zu === 1 ? "ort-zu" : "orte-zu")}.`;
  }
  hinweis.textContent = text;
  hinweis.hidden = !text;

  // Mehr Orte: je Thema, was nicht im Plan ist — zum Dazunehmen.
  const gewaehlt = THEMEN.filter((th) => state.themen.has(th.id) || GAESTE.some((g) => g.thema === th.id && state.an.has(g.id)));
  document.getElementById("mehr-orte").innerHTML = THEMEN.map((th) => {
    const offen = GAESTE.filter((g) => g.thema === th.id && !state.an.has(g.id)
      && !(state.umstaende.barrierefrei && g.barrierefrei === false));
    if (!offen.length) return "";
    const auf = gewaehlt.includes(th) ? " open" : "";
    return `<details class="mehr"${auf}><summary>${ui("mehr-orte")}: ${t(th.name)}</summary>` +
      `<ol class="stationen">${offen.sort((a, b) => a.rang - b.rang).map((g) => zeileMarkup(g, "", false, null)).join("")}</ol></details>`;
  }).join("");

  ausgabeZeichnen();
}

// Link und QR folgen jedem Wechsel — was hier steht, ist immer der Plan darüber.
function ausgabeZeichnen() {
  const link = planLink();
  document.getElementById("qr-box").innerHTML = qrMarkup(link);
  document.getElementById("plan-oeffnen").href = link;
  const feld = document.getElementById("linkfeld");
  if (!feld.hidden) document.getElementById("link-wert").value = link;
}

function qrMarkup(text) {
  if (typeof qrcode !== "function") return "";
  const q = qrcode(0, "M");
  q.addData(text);
  q.make();
  const n = q.getModuleCount();
  let pfad = "";
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) pfad += `M${c} ${r}h1v1h-1z`;
  return `<svg viewBox="-2 -2 ${n + 4} ${n + 4}" role="img" aria-label="${ui("qr")}">` +
    `<rect x="-2" y="-2" width="${n + 4}" height="${n + 4}" fill="#ffffff"/>` + /* # ds-ok: QR-Code ist ein Artefakt, immer weiss */
    `<path d="${pfad}" fill="#000000"/></svg>`; /* # ds-ok: QR-Module sind immer schwarz */
}

/* ---------- Ereignisse ---------- */

// Themen, Umstände, Zeit und Tag stellen den Plan neu zusammen; die Kästchen
// im Plan ändern ihn von Hand (bis zum nächsten Wechsel oben).
function neuZusammenstellen() {
  vorauswahl();
  wahlZeichnen();
  planZeichnen();
}

function verdrahten() {
  document.getElementById("sprache-seg").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-sprache]");
    if (!b) return;
    state.sprache = b.dataset.sprache;
    texteSetzen(); wahlZeichnen(); planZeichnen();
  });
  document.getElementById("themen").addEventListener("click", (e) => {
    const b = e.target.closest(".kachel");
    if (!b) return;
    const id = b.dataset.thema;
    if (state.themen.has(id)) state.themen.delete(id); else state.themen.add(id);
    neuZusammenstellen();
  });
  document.getElementById("umstaende").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-umstand]");
    if (!b) return;
    state.umstaende[b.dataset.umstand] = !state.umstaende[b.dataset.umstand];
    neuZusammenstellen();
  });
  document.getElementById("zeiten").addEventListener("click", (e) => {
    const b = e.target.closest(".kachel");
    if (!b) return;
    state.zeit = b.dataset.zeit;
    neuZusammenstellen();
  });
  document.getElementById("datum").addEventListener("change", (e) => { state.datum = e.target.value || ""; neuZusammenstellen(); });
  document.getElementById("ankunft").addEventListener("change", (e) => { state.ankunft = e.target.value || "10:00"; planZeichnen(); });

  document.getElementById("plan").addEventListener("change", (e) => {
    const id = e.target.dataset.dabei;
    if (!id) return;
    if (e.target.checked) state.an.add(id); else state.an.delete(id);
    planZeichnen();
  });

  document.getElementById("pdf").addEventListener("click", async () => {
    const knopf = document.getElementById("pdf");
    const text = knopf.textContent;
    knopf.disabled = true; knopf.textContent = ui("pdf-laeuft");
    try { await planPdf(); }
    catch (fehler) { console.error(fehler); window.alert(ui("pdf-fehler")); }
    finally { knopf.disabled = false; knopf.textContent = text; }
  });
  document.getElementById("link-kopieren").addEventListener("click", async () => {
    const link = planLink();
    document.getElementById("linkfeld").hidden = false;
    document.getElementById("link-wert").value = link;
    const hint = document.getElementById("link-hint");
    try { await navigator.clipboard.writeText(link); hint.textContent = ui("kopiert"); }
    catch (fehler) { hint.textContent = ui("kopieren-hand"); }
  });

  // Ein eingefügter Plan-Link gehört auf die Telefonansicht.
  window.addEventListener("hashchange", () => {
    const h = hashLesen();
    if (h.p) window.location.replace(PLAN_SEITE + window.location.hash);
    else if (h.e) window.location.reload();
  });
}

/* ---------- Start ---------- */

function start() {
  const h = hashLesen();
  // Alte Links (index.html#p=…) führen weiter auf die Telefonansicht.
  if (h.p) { window.location.replace(PLAN_SEITE + window.location.hash); return; }
  hashAnwenden(h);
  document.getElementById("datum").value = state.datum;
  document.getElementById("ankunft").value = state.ankunft;
  verdrahten();
  texteSetzen();
  if (h.e) {
    // ‹Plan ändern› von der Telefonansicht: den Plan zur Bearbeitung laden,
    // Themen aus dem Plan zurücklesen, damit ‹Mehr Orte› die richtigen Gruppen zeigt.
    state.an = dekodieren(h.e);
    state.themen = new Set([...state.an].map((id) => gast(id) && gast(id).thema).filter((th) => th && th !== "basis" && th !== "anreise"));
    history.replaceState(null, "", window.location.pathname);
    wahlZeichnen();
    planZeichnen();
  } else {
    neuZusammenstellen();
  }
  // Kommen die Öffnungszeiten live an, rechnet der Plan neu (Text, Zeitplan).
  ausnahmenLaden(planZeichnen);
}

start();
