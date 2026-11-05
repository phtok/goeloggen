/* Lesetest · Ablauf. Ein Schritt aufs Mal; die Lesezeit läuft vom Erscheinen
   des Texts (Schrift geladen) bis «Fertig gelesen». Zeit in einem verborgenen
   Tab wird mitgezählt und gesondert vermerkt. ?bogen=N wählt Papier mit
   Bogen N vor; ?probe=1 ist ein Probelauf, der nichts speichert. */
(function () {
  const $ = (id) => document.getElementById(id);
  const Q = new URLSearchParams(location.search);
  const PROBE = Q.has("probe");
  const OFFEN = "lesetest:offen";
  const SCHRIFT = { G: '440 20px "Goetheanum"', S: '400 20px "Source Sans 3"' };
  const S = { alter: null, medium: "bildschirm", bogen: null, id: null, schluessel: null, gruppe: null, plan: null, i: 0, ergebnisse: [], t0: 0, verborgen: 0, weg: 0, start: 0 };

  function zeige(id) {
    document.querySelectorAll(".schritt").forEach((s) => { s.hidden = s.id !== id; });
    window.scrollTo(0, 0);
    const h = $(id).querySelector("h1, h2, legend");
    if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  }

  // Auswahl-Pillen (aria-pressed), eine Wahl je Gruppe.
  function wahl(gruppe, wert) {
    gruppe.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.wert === wert)));
  }
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-wahl] button");
    if (!b) return;
    const g = b.closest("[data-wahl]");
    wahl(g, b.dataset.wert);
    const name = g.dataset.wahl;
    if (name === "alter") S.alter = b.dataset.wert;
    if (name === "medium") {
      S.medium = b.dataset.wert;
      $("bogenwahl").hidden = S.medium !== "papier";
      g.querySelector('[data-wert="papier"]').setAttribute("aria-expanded", String(S.medium === "papier"));
    }
    if (name === "bogen") S.bogen = Number(b.dataset.wert);
  });

  const vorBogen = Number(Q.get("bogen"));
  if (vorBogen >= 1 && vorBogen <= 8) {
    S.medium = "papier"; S.bogen = vorBogen;
    wahl(document.querySelector('[data-wahl="medium"]'), "papier");
    wahl(document.querySelector('[data-wahl="bogen"]'), String(vorBogen));
    $("bogenwahl").hidden = false;
    document.querySelector('[data-wert="papier"]').setAttribute("aria-expanded", "true");
  }

  // ---- Beginnen ------------------------------------------------------------
  $("startform").addEventListener("submit", async (e) => {
    e.preventDefault();
    const m = $("startmeldung");
    if (S.medium === "papier" && !S.bogen) { m.className = "said schlecht"; m.textContent = "Wähle die Nummer deines Bogens."; return; }
    $("beginnen").disabled = true; $("beginnen").textContent = "Einen Moment …";
    if (PROBE) {
      S.gruppe = S.bogen ? S.bogen - 1 : Math.floor(Math.random() * 8);
    } else {
      try {
        const r = await LESEBACKEND.rpc("lesetest_beginnen", { p_medium: S.medium, p_alter: S.alter || "", p_fenster: innerWidth, p_bogen: S.bogen });
        if (r && r.status === "ok") { S.id = r.id; S.schluessel = r.schluessel; S.gruppe = r.gruppe; }
      } catch (err) { /* ohne Verbindung weiter; die Gruppe wählt der Browser */ }
      if (S.gruppe === null) S.gruppe = S.bogen ? S.bogen - 1 : Math.floor(Math.random() * 8);
    }
    S.plan = LESEPLAN.plan(S.gruppe);
    S.start = performance.now();
    // Beide Schriften vorladen, damit kein Text in einer Ersatzschrift erscheint.
    try { await Promise.all([document.fonts.load(SCHRIFT.G), document.fonts.load(SCHRIFT.S)]); } catch (err) { /* misst trotzdem */ }
    vorbereiten();
  });

  // ---- Ein Text ------------------------------------------------------------
  function vorbereiten() {
    const p = S.plan[S.i];
    const n = `Text ${p.pos} von 4`;
    $("vor-kicker").textContent = n;
    $("fragen-kicker").textContent = n;
    if (S.medium === "papier") {
      $("vor-titel").textContent = `Nimm Text ${p.pos} auf deinem Bogen zur Hand.`;
      $("vor-text").textContent = "Lies ihn noch nicht. Tippe auf ‹Ich beginne zu lesen›, lies in deinem gewohnten Tempo und tippe danach auf ‹Fertig gelesen›.";
      $("zeigen").textContent = "Ich beginne zu lesen";
    } else {
      $("vor-titel").textContent = p.pos === 1 ? "Lies in deinem gewohnten Tempo." : "Weiter mit dem nächsten Text.";
      $("vor-text").textContent = `Etwa ${rund(p.text.woerter)} Wörter. Lies so, wie du sonst liest. Danach kommen drei Fragen; zurückblättern geht dann nicht mehr.`;
      $("zeigen").textContent = "Text zeigen";
    }
    zeige("vor");
  }
  const rund = (w) => (w < 150 ? Math.round(w / 10) * 10 : Math.round(w / 50) * 50);

  $("zeigen").addEventListener("click", async () => {
    const p = S.plan[S.i];
    const art = $("probe");
    if (S.medium === "papier") {
      art.hidden = true;
      $("papier-lesen").hidden = false;
      $("papier-text").textContent = `Lies jetzt Text ${p.pos} auf deinem Bogen. Tippe danach auf ‹Fertig gelesen›.`;
    } else {
      art.hidden = false;
      $("papier-lesen").hidden = true;
      try { await document.fonts.load(SCHRIFT[p.schrift]); } catch (err) { /* misst trotzdem */ }
      art.className = `probe schrift-${p.schrift.toLowerCase()}`;
      $("probe-titel").textContent = p.text.titel;
      const box = $("probe-text");
      box.textContent = "";
      p.text.absaetze.forEach((a) => { const el = document.createElement("p"); el.textContent = a; box.appendChild(el); });
    }
    zeige("lesen");
    requestAnimationFrame(() => requestAnimationFrame(() => { S.t0 = performance.now(); S.verborgen = 0; S.weg = 0; }));
  });

  document.addEventListener("visibilitychange", () => {
    if (!S.t0) return;
    if (document.hidden) S.weg = performance.now();
    else if (S.weg) { S.verborgen += performance.now() - S.weg; S.weg = 0; }
  });

  $("fertig").addEventListener("click", () => {
    const ms = Math.round(performance.now() - S.t0);
    const p = S.plan[S.i];
    S.aktuell = { pos: p.pos, id: p.text.id, laenge: p.laenge, set: p.text.set, schrift: p.schrift, woerter: p.text.woerter, ms, ms_verborgen: Math.round(S.verborgen) };
    S.t0 = 0;
    fragenAufbauen(p);
    zeige("fragen");
  });

  // ---- Fragen --------------------------------------------------------------
  function mischen(n) {
    const a = [...Array(n).keys()];
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  function fragenAufbauen(p) {
    const liste = $("fragen-liste");
    liste.textContent = "";
    S.antworten = [null, null, null];
    p.text.fragen.forEach((f, k) => {
      const fs = document.createElement("fieldset");
      fs.className = "frage"; fs.id = `f-frage${k}`;
      const lg = document.createElement("legend");
      lg.textContent = f.frage; fs.appendChild(lg);
      const box = document.createElement("div");
      box.className = "kacheln"; box.dataset.frage = k;
      mischen(f.antworten.length).forEach((idx) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "kachel"; b.setAttribute("aria-pressed", "false"); b.dataset.idx = idx;
        const s = document.createElement("span"); s.className = "k-kurz"; s.textContent = f.antworten[idx];
        b.appendChild(s); box.appendChild(b);
      });
      fs.appendChild(box); liste.appendChild(fs);
    });
    ["anstrengung", "weiterlesen"].forEach((name) => {
      const g = document.querySelector(`[data-wahl="${name}"]`);
      g.textContent = "";
      for (let v = 1; v <= 7; v++) {
        const b = document.createElement("button");
        b.type = "button"; b.setAttribute("aria-pressed", "false"); b.dataset.wert = String(v); b.textContent = String(v);
        g.appendChild(b);
      }
    });
    $("bekannt").checked = false;
    $("fehler").hidden = true;
  }
  $("fragen-liste").addEventListener("click", (e) => {
    const b = e.target.closest("button.kachel");
    if (!b) return;
    const box = b.closest(".kacheln");
    box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    S.antworten[Number(box.dataset.frage)] = Number(b.dataset.idx);
  });

  function gewaehlt(name) {
    const b = document.querySelector(`[data-wahl="${name}"] button[aria-pressed="true"]`);
    return b ? Number(b.dataset.wert) : null;
  }

  $("fragenform").addEventListener("submit", (e) => {
    e.preventDefault();
    const p = S.plan[S.i];
    const fehlt = [];
    S.antworten.forEach((a, k) => { if (a === null) fehlt.push([`f-frage${k}`, `Wähle eine Antwort auf ‹${p.text.fragen[k].frage}›`]); });
    const anstrengung = gewaehlt("anstrengung"), weiterlesen = gewaehlt("weiterlesen");
    if (!anstrengung) fehlt.push(["f-anstrengung", "Wähle, wie anstrengend das Lesen war."]);
    if (!weiterlesen) fehlt.push(["f-weiterlesen", "Wähle, wie gern du weiterlesen würdest."]);
    const box = $("fehler");
    if (fehlt.length) {
      box.textContent = "";
      const ul = document.createElement("ul");
      fehlt.forEach(([id, txt]) => { const li = document.createElement("li"); const a = document.createElement("a"); a.href = `#${id}`; a.textContent = txt; li.appendChild(a); ul.appendChild(li); });
      box.appendChild(ul); box.hidden = false; box.focus();
      return;
    }
    S.ergebnisse.push({ ...S.aktuell, antworten: S.antworten, richtig: S.antworten.filter((a) => a === 0).length, anstrengung, weiterlesen, bekannt: $("bekannt").checked });
    S.i += 1;
    if (S.i < S.plan.length) vorbereiten(); else abschliessen();
  });

  // ---- Abgeben -------------------------------------------------------------
  function daten() {
    const probe = getComputedStyle($("probe"));
    return {
      version: 1, gruppe: S.gruppe, medium: S.medium, texte: S.ergebnisse,
      dauer_ms: Math.round(performance.now() - S.start),
      umgebung: {
        fenster: innerWidth, dpr: devicePixelRatio || 1,
        dunkel: document.documentElement.dataset.theme === "dark" || (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches),
        grad_px: parseFloat(probe.fontSize) || null,
        geraet: matchMedia("(pointer: coarse)").matches ? "touch" : "maus",
      },
    };
  }
  async function senden(offen) {
    if (!offen.id) {
      const r = await LESEBACKEND.rpc("lesetest_beginnen", { p_medium: offen.daten.medium, p_alter: offen.alter || "", p_fenster: offen.daten.umgebung.fenster, p_bogen: offen.daten.gruppe + 1 });
      if (!r || r.status !== "ok") throw new Error("beginnen");
      offen.id = r.id; offen.schluessel = r.schluessel;
      try { localStorage.setItem(OFFEN, JSON.stringify(offen)); } catch (e) { /* privat */ }
    }
    const r = await LESEBACKEND.rpc("lesetest_abgeben", { p_id: offen.id, p_schluessel: offen.schluessel, p_daten: offen.daten });
    if (!r || r.status !== "ok") throw new Error("abgeben");
    try { localStorage.removeItem(OFFEN); } catch (e) { /* privat */ }
  }
  function dankText() {
    const n = S.plan.filter((p) => p.schrift === "G").map((p) => p.pos).join(" und ");
    return `Danke! Die Texte ${n} standen in der Goetheanum Schrift, die anderen beiden in Source Sans 3. Du kannst das Fenster jetzt schliessen.`;
  }
  async function abschliessen() {
    zeige("ende");
    const offen = { id: S.id, schluessel: S.schluessel, alter: S.alter, daten: daten() };
    if (PROBE) {
      $("ende-titel").textContent = "Probelauf beendet.";
      $("ende-text").textContent = "Im Probelauf wird nichts gespeichert. " + dankText();
      return;
    }
    try { localStorage.setItem(OFFEN, JSON.stringify(offen)); } catch (e) { /* privat */ }
    S.offen = offen;
    await versuchen();
  }
  async function versuchen() {
    $("nochmal").hidden = true;
    try {
      await senden(S.offen);
      $("ende-titel").textContent = "Geschafft. Deine Antworten sind gespeichert.";
      $("ende-text").textContent = dankText();
    } catch (e) {
      $("ende-titel").textContent = "Das Speichern hat nicht geklappt.";
      $("ende-text").textContent = "Deine Antworten sind in diesem Browser aufbewahrt. Prüfe die Verbindung und sende sie noch einmal.";
      $("nochmal").hidden = false;
    }
  }
  $("nochmal").addEventListener("click", versuchen);

  // Hängt von einem früheren Besuch noch etwas, still nachsenden.
  if (!PROBE) {
    try {
      const alt = JSON.parse(localStorage.getItem(OFFEN) || "null");
      if (alt && alt.daten) senden(alt).catch(() => {});
    } catch (e) { /* privat */ }
  }
})();
