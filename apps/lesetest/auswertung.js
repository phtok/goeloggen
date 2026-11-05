/* Lesetest · Auswertung (Rechnung und Zeichnung). Siehe Kopf von auswertung.html. */
(function () {
  const $ = (id) => document.getElementById(id);
  const DEMO = new URLSearchParams(location.search).has("demo");
  const LAENGEN = [1, 2, 3, 4];
  const SCHRIFTEN = [["G", "Goetheanum Klar", "g"], ["S", "Source Sans 3", "s"]];
  const MASSE = [
    { key: "rel", titel: "Lesetempo", sub: "relativ zum eigenen Tempo, 100 = eigenes Mittel; höher ist schneller", fmt: (v) => v.toFixed(0) },
    { key: "verst", titel: "Verständnis", sub: "richtige Antworten in Prozent", fmt: (v) => `${v.toFixed(0)} %`, min: 0, max: 100 },
    { key: "anstr", titel: "Anstrengung", sub: "1 = gar nicht, 7 = sehr; tiefer ist besser", fmt: (v) => v.toFixed(1), min: 1, max: 7 },
    { key: "weiter", titel: "Lust weiterzulesen", sub: "1 = gar nicht, 7 = sehr gern; höher ist besser", fmt: (v) => v.toFixed(1), min: 1, max: 7 },
  ];
  const F = { medium: "", alter: "", bekannt: "weg" };
  let ROH = [];

  // ---- Daten ---------------------------------------------------------------
  function demoDaten() {
    // Erfunden: 28 Personen; Source leicht im Vorteil, wachsend mit der Länge.
    let s = 7; const zufall = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    const normal = () => Math.sqrt(-2 * Math.log(zufall() + 1e-9)) * Math.cos(2 * Math.PI * zufall());
    const alter = ["unter 30", "30–44", "45–59", "60–74", "75 und älter"];
    const out = [];
    for (let i = 0; i < 28; i++) {
      const g = i % 8, basis = 230 * Math.exp(0.25 * normal()), a = alter[i % 5];
      const texte = LESEPLAN.plan(g).map((p) => {
        const vorteil = p.schrift === "S" ? [0, 0.02, 0.05, 0.08][p.laenge - 1] : 0;
        const wpm = basis * (1 + vorteil) * Math.exp(0.12 * normal());
        const richtig = [0, 1, 2].map(() => (zufall() < 0.8 + vorteil ? 0 : 1 + Math.floor(zufall() * 3)));
        const sk = (m) => Math.max(1, Math.min(7, Math.round(m + normal())));
        return { pos: p.pos, id: p.text.id, laenge: p.laenge, set: p.text.set, schrift: p.schrift, woerter: p.text.woerter,
          ms: Math.round(p.text.woerter / wpm * 60000), ms_verborgen: 0, antworten: richtig, richtig: richtig.filter((x) => x === 0).length,
          anstrengung: sk(3 + p.laenge * 0.3 - vorteil * 12), weiterlesen: sk(4.5 + vorteil * 8), bekannt: p.text.id === "gesetz" && zufall() < 0.3 };
      });
      out.push({ id: i + 1, gruppe: g, medium: i % 3 === 0 ? "papier" : "bildschirm", alter_gruppe: a, daten: { texte } });
    }
    return out;
  }
  async function laden() {
    if (DEMO) { $("demo").hidden = false; return demoDaten(); }
    return (await LESEBACKEND.rpc("lesetest_ergebnisse", {})) || [];
  }

  // ---- Rechnen -------------------------------------------------------------
  const jung = (a) => a === "unter 30" || a === "30–44";
  const alt = (a) => a === "45–59" || a === "60–74" || a === "75 und älter";
  function zeilen() {
    const z = []; let aus = 0, personen = 0;
    ROH.forEach((d) => {
      if (F.medium && d.medium !== F.medium) return;
      if (F.alter === "jung" && !jung(d.alter_gruppe)) return;
      if (F.alter === "alt" && !alt(d.alter_gruppe)) return;
      const texte = ((d.daten && d.daten.texte) || []).map((t) => ({ ...t, wpm: t.woerter / (t.ms / 60000) }));
      const gut = texte.filter((t) => {
        const ok = t.wpm >= 40 && t.wpm <= 800 && (t.ms_verborgen || 0) <= 0.2 * t.ms && !(F.bekannt === "weg" && t.bekannt);
        if (!ok) aus++;
        return ok;
      });
      if (!gut.length) return;
      personen++;
      const mittel = gut.length >= 3 ? Math.exp(gut.reduce((s, t) => s + Math.log(t.wpm), 0) / gut.length) : null;
      gut.forEach((t) => z.push({ person: d.id, medium: d.medium, alter: d.alter_gruppe, laenge: t.laenge, schrift: t.schrift, text: t.id,
        woerter: t.woerter, wpm: t.wpm, rel: mittel ? 100 * t.wpm / mittel : null, verst: 100 * t.richtig / 3,
        anstr: t.anstrengung, weiter: t.weiterlesen, bekannt: !!t.bekannt }));
    });
    return { z, aus, personen };
  }
  const T975 = [0, 12.71, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228];
  function stat(werte) {
    const v = werte.filter((x) => x !== null && !Number.isNaN(x));
    const n = v.length; if (!n) return null;
    const m = v.reduce((a, b) => a + b, 0) / n;
    if (n < 2) return { n, m, lo: null, hi: null };
    const sd = Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / (n - 1));
    const t = n - 1 <= 10 ? T975[n - 1] : 1.96 + 2.4 / (n - 1);
    const h = t * sd / Math.sqrt(n);
    return { n, m, lo: m - h, hi: m + h };
  }
  const median = (v) => { const s = [...v].sort((a, b) => a - b); const k = s.length >> 1; return s.length % 2 ? s[k] : (s[k - 1] + s[k]) / 2; };
  function mittelWoerter(l) { const t = LESETEXTE.filter((x) => x.laenge === l); return Math.round(t.reduce((a, x) => a + x.woerter, 0) / t.length); }

  // ---- Zeichnen ------------------------------------------------------------
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, at, kl) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); if (kl) e.setAttribute("class", kl); return e; };
  function bild(mass, zellen, W) {
    const schmal = W < 400, H = 250, L = 44, R = 12, O = 12, U = 36;
    const alle = []; zellen.forEach((c) => { if (c[mass.key]) { alle.push(c[mass.key].m); if (c[mass.key].lo !== null) alle.push(c[mass.key].lo, c[mass.key].hi); } });
    let lo = mass.min ?? Math.min(...alle, 100), hi = mass.max ?? Math.max(...alle, 100);
    if (mass.key === "rel") { const r = Math.max(10, ...alle.map((x) => Math.abs(x - 100))); lo = 100 - Math.ceil(r / 5) * 5; hi = 100 + Math.ceil(r / 5) * 5; }
    if (mass.key === "verst") { lo = 0; hi = 100; }
    const x = (l) => L + (l - 0.5) * (W - L - R) / 4, y = (v) => O + (hi - v) / (hi - lo) * (H - O - U);
    const fig = document.createElement("figure"); fig.className = "bild";
    const h = document.createElement("h3"); h.textContent = mass.titel; fig.appendChild(h);
    const p = document.createElement("p"); p.className = "meta"; p.textContent = mass.sub; fig.appendChild(p);
    const svg = sv("svg", { viewBox: `0 0 ${W} ${schmal ? H + 14 : H}`, width: W, role: "img", "aria-label": `${mass.titel} je Länge, Goetheanum Klar und Source Sans 3. Zahlen in der Tabelle unten.` });
    const schritt = mass.key === "rel" ? (hi - lo > 40 ? 10 : 5) : mass.key === "verst" ? 25 : 2;
    for (let v = lo; v <= hi + 1e-9; v += schritt) {
      const yy = y(v);
      svg.appendChild(sv("line", { x1: L, x2: W - R, y1: yy, y2: yy }, mass.key === "rel" && Math.abs(v - 100) < 1e-6 ? "null" : "gitter"));
      const t = sv("text", { x: L - 8, y: yy + 4, "text-anchor": "end" }, "achse"); t.textContent = String(Math.round(v)); svg.appendChild(t);
    }
    LAENGEN.forEach((l) => { const t = sv("text", { x: x(l), y: H - 12, "text-anchor": "middle" }, "achse"); t.textContent = schmal ? `≈${mittelWoerter(l)}` : `≈${mittelWoerter(l)} Wörter`; svg.appendChild(t); });
    if (schmal) { const t = sv("text", { x: W - R, y: H + 8, "text-anchor": "end" }, "achse"); t.textContent = "Wörter je Text"; svg.appendChild(t); }
    SCHRIFTEN.forEach(([k, name, kl], si) => {
      const dx = si ? 7 : -7;
      const pts = LAENGEN.map((l) => { const c = zellen.find((z) => z.laenge === l && z.schrift === k); return c && c[mass.key] ? { l, c, s: c[mass.key] } : null; }).filter(Boolean);
      if (pts.length > 1) svg.appendChild(sv("polyline", { points: pts.map((q) => `${x(q.l) + dx},${y(q.s.m)}`).join(" ") }, `linie ${kl}`));
      pts.forEach((q) => {
        if (q.s.lo !== null) svg.appendChild(sv("line", { x1: x(q.l) + dx, x2: x(q.l) + dx, y1: y(Math.max(lo, q.s.lo)), y2: y(Math.min(hi, q.s.hi)) }, `ci ${kl}`));
        const ziel = sv("circle", { cx: x(q.l) + dx, cy: y(q.s.m), r: 14, tabindex: 0, "aria-label": `${name}, ≈${mittelWoerter(q.l)} Wörter: ${mass.fmt(q.s.m)}, ${q.s.n} Texte` }, "ziel");
        const tipp = `${name}\n≈${mittelWoerter(q.l)} Wörter\n${mass.titel}: ${mass.fmt(q.s.m)}${q.s.lo !== null ? ` (${mass.fmt(q.s.lo)}–${mass.fmt(q.s.hi)})` : ""}\n${q.s.n} Texte`;
        ["mouseenter", "focus"].forEach((ev) => ziel.addEventListener(ev, () => zeigeTipp(fig, svg, x(q.l) + dx, y(q.s.m), tipp)));
        ["mouseleave", "blur"].forEach((ev) => ziel.addEventListener(ev, () => versteckeTipp(fig)));
        svg.appendChild(ziel);
        svg.appendChild(k === "G" ? sv("circle", { cx: x(q.l) + dx, cy: y(q.s.m), r: 5.5 }, `pt ${kl}`) : sv("rect", { x: x(q.l) + dx - 5, y: y(q.s.m) - 5, width: 10, height: 10 }, `pt ${kl}`));
      });
    });
    fig.appendChild(svg);
    return fig;
  }
  function zeigeTipp(fig, svg, cx, cy, txt) {
    let t = fig.querySelector(".tipp"); if (!t) { t = document.createElement("div"); t.className = "tipp"; t.setAttribute("aria-hidden", "true"); fig.appendChild(t); }
    t.textContent = ""; txt.split("\n").forEach((z, i) => { const d = document.createElement("div"); d.textContent = z; if (!i) d.style.fontWeight = "600"; t.appendChild(d); });
    const k = 1, f = fig.getBoundingClientRect(), s = svg.getBoundingClientRect();
    let left = s.left - f.left + cx * k + 14; if (left + 240 > f.width) left = s.left - f.left + cx * k - 254;
    t.style.left = `${Math.max(0, left)}px`; t.style.top = `${s.top - f.top + cy * k - 20}px`;
  }
  function versteckeTipp(fig) { const t = fig.querySelector(".tipp"); if (t) t.remove(); }

  function zeichnen() {
    const { z, aus, personen } = zeilen();
    const zellen = [];
    LAENGEN.forEach((l) => SCHRIFTEN.forEach(([k]) => {
      const r = z.filter((x) => x.laenge === l && x.schrift === k);
      zellen.push({ laenge: l, schrift: k, n: r.length, median: r.length ? median(r.map((x) => x.wpm)) : null,
        rel: stat(r.map((x) => x.rel)), verst: stat(r.map((x) => x.verst)), anstr: stat(r.map((x) => x.anstr)), weiter: stat(r.map((x) => x.weiter)) });
    }));
    $("stand").textContent = personen
      ? `${personen} Personen, ${z.length} Texte gewertet${aus ? `, ${aus} ausgeschlossen (überflogen, unterbrochen oder schon bekannt)` : ""}.`
      : "Noch keine Antworten für diese Auswahl.";
    const box = $("bilder"); box.textContent = "";
    if (personen) {
      const breit = box.clientWidth, spalte = matchMedia("(min-width: 900px)").matches ? (breit - 24) / 2 : breit;
      MASSE.forEach((m) => box.appendChild(bild(m, zellen, Math.floor(spalte))));
    }
    const tb = $("tab"); tb.textContent = "";
    zellen.forEach((c) => {
      const tr = document.createElement("tr");
      const zelle = (s, m) => (s ? `${m.fmt(s.m)}${s.lo !== null ? ` (${m.fmt(s.lo)}–${m.fmt(s.hi)})` : ""}` : "–");
      [`≈${mittelWoerter(c.laenge)} Wörter`, c.schrift === "G" ? "Goetheanum Klar" : "Source Sans 3", String(c.n),
        c.median ? Math.round(c.median).toString() : "–", zelle(c.rel, MASSE[0]), zelle(c.verst, MASSE[1]), zelle(c.anstr, MASSE[2]), zelle(c.weiter, MASSE[3])]
        .forEach((v, i) => { const td = document.createElement(i === 0 ? "th" : "td"); if (i === 0) td.scope = "row"; td.textContent = v; tr.appendChild(td); });
      tb.appendChild(tr);
    });
    zeichnen.letzte = z;
  }

  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-filter] button"); if (!b) return;
    const g = b.closest("[data-filter]");
    g.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    F[g.dataset.filter] = b.dataset.wert; zeichnen();
  });
  $("csv").addEventListener("click", () => {
    const k = ["person", "medium", "alter", "laenge", "text", "woerter", "schrift", "wpm", "rel", "verst", "anstr", "weiter", "bekannt"];
    const z = (zeichnen.letzte || []).map((r) => k.map((x) => { const v = r[x]; return typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(2)) : `"${String(v ?? "").replace(/"/g, '""')}"`; }).join(","));
    const blob = new Blob([[k.join(","), ...z].join("\n")], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = DEMO ? "lesetest-beispiel.csv" : "lesetest.csv"; a.click();
  });

  let uhr; addEventListener("resize", () => { clearTimeout(uhr); uhr = setTimeout(() => { if (ROH.length) zeichnen(); }, 200); });
  laden().then((d) => { ROH = d; zeichnen(); }).catch(() => { $("stand").className = "said schlecht stand"; $("stand").textContent = "Die Antworten liessen sich nicht laden. Später noch einmal versuchen."; });
})();
