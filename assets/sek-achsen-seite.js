/* Seitenskript zu sektionsfarben-achsen.html – Doppelfarben auf Goethes Achsen.
   Liest assets/sek-achsen.js (generiert), setzt die Töne als Custom Properties
   (--a-*), baut Kreis, Achsenkarten, Sektionskarten und die Anwendung und misst
   die Kontraste am gerenderten Blatt nach. */
(function () {
  "use strict";
  var D = window.GOE_SEK_ACHSEN; if (!D) return;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var el = function (t, c, h) { var e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
  var ROOT = document.documentElement, SEK = D.sektionen, byKey = {};
  var reihe = SEK.slice().sort(function (a, b) { return a.platz - b.platz; });
  reihe.forEach(function (s, i) { s.nr = i + 1; });
  SEK.forEach(function (s) { byKey[s.key] = s; });
  var NATUR = { licht: "leuchtet – Schrift in der geforderten Farbe", grund: "trägt Weiss – Zeichen in der geforderten Farbe" };
  var KURZNATUR = { licht: "leuchtende Fläche", grund: "tragende Fläche" };

  /* --- Töne als Custom Properties (eine Quelle: die Daten) ------------------ */
  function istDunkel() {
    var t = ROOT.getAttribute("data-theme");
    return t === "dark" || (!t && matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function setzeTokens() {
    var dunkel = istDunkel();
    SEK.forEach(function (s) {
      var p = "--a-" + s.key;
      ROOT.style.setProperty(p, s.flaeche);
      ROOT.style.setProperty(p + "-zeichen", s.zeichen);
      ROOT.style.setProperty(p + "-schrift", s.schrift);
      ROOT.style.setProperty(p + "-hauch", dunkel ? s.hauch_dk : s.hauch);
      ROOT.style.setProperty(p + "-tinte", dunkel ? s.tinte_dk : s.schrift);
    });
    D.mono.forEach(function (m) { ROOT.style.setProperty("--a-mono-" + m.key, m.hex); });
    D.anker.forEach(function (a) {
      ROOT.style.setProperty("--a-anker-" + a.name.toLowerCase().replace("ü", "ue"), a.hex);
    });
  }

  /* --- Farbmathematik für die Messung am Blatt ------------------------------ */
  function hexToRgb(hex) { var h = hex.replace("#", ""); if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2]; return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16) }; }
  function rgbToHex(r, g, b) { return "#" + [r, g, b].map(function (c) { c = Math.max(0, Math.min(255, Math.round(c))); return (c < 16 ? "0" : "") + c.toString(16); }).join(""); }
  function lin(c) { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
  function lum(hex) { var c = hexToRgb(hex); return 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b); }
  function kontrast(a, b) { var la = lum(a), lb = lum(b), hi = Math.max(la, lb), lo = Math.min(la, lb); return (hi + 0.05) / (lo + 0.05); }
  function fmt(k) { return (Math.round(k * 10) / 10).toFixed(1) + ":1"; }
  function cssToHex(v) { v = (v || "").trim(); if (v[0] === "#") return v.length === 4 ? "#" + v[1] + v[1] + v[2] + v[2] + v[3] + v[3] : v; var m = v.match(/rgba?\(([^)]+)\)/); if (!m) return "#000000"; var p = m[1].split(/[\s,\/]+/).map(parseFloat); return rgbToHex(p[0], p[1], p[2]); }
  function paintHex(node, prop) { return cssToHex(getComputedStyle(node)[prop || "backgroundColor"]); }

  /* --- Kopieren -------------------------------------------------------------- */
  function copy(txt) {
    if (navigator.clipboard) navigator.clipboard.writeText(txt);
    var t = $("#toast"); t.textContent = "‹" + txt + "› kopiert"; t.classList.add("show");
    setTimeout(function () { t.classList.remove("show"); }, 1100);
  }
  function wert(txt, art, punkt) {
    var b = el("button", "wert"); b.type = "button"; b.title = "Klick kopiert";
    if (punkt) { var p = el("span", "punkt"); p.style.background = punkt; b.appendChild(p); }
    if (art) b.appendChild(el("span", "art", art));
    b.appendChild(document.createTextNode(txt));
    b.addEventListener("click", function () { copy(txt); });
    return b;
  }

  /* --- Der Kreis (SVG) ------------------------------------------------------- */
  var NS = "http://www.w3.org/2000/svg", CX = 380, CY = 380;
  function pol(r, deg) { var a = (deg - 90) * Math.PI / 180; return [CX + r * Math.cos(a), CY + r * Math.sin(a)]; }
  function ring(r1, r2, a0, a1) {
    var p0 = pol(r2, a0), p1 = pol(r2, a1), p2 = pol(r1, a1), p3 = pol(r1, a0), gross = (a1 - a0) > 180 ? 1 : 0;
    return "M" + p0.join(",") + " A" + r2 + "," + r2 + " 0 " + gross + " 1 " + p1.join(",") +
           " L" + p2.join(",") + " A" + r1 + "," + r1 + " 0 " + gross + " 0 " + p3.join(",") + "Z";
  }
  function sv(t, attrs, txt) { var e = document.createElementNS(NS, t); for (var k in attrs) e.setAttribute(k, attrs[k]); if (txt != null) e.textContent = txt; return e; }

  function bauKreis() {
    var svg = $("#svg-kreis");
    // Goethes sechs Farben innen
    D.anker.forEach(function (a) {
      var tok = "--a-anker-" + a.name.toLowerCase().replace("ü", "ue");
      svg.appendChild(sv("path", { d: ring(150, 224, a.winkel - 30, a.winkel + 30), fill: "var(" + tok + ")", "class": "sektor" }));
      var p = pol(187, a.winkel);
      svg.appendChild(sv("text", { x: p[0], y: p[1] + 8, "text-anchor": "middle", "class": "ort",
        fill: a.name === "Gelb" ? "var(--ink)" : "var(--on-accent)" }, a.name));
    });
    // Aussen: die zwölf Sektionsplätze. Die Monofarben stehen auf keiner Achse
    // und darum auch nicht im Ring.
    var felder = reihe.map(function (s) {
      return { platz: s.platz, farbe: "var(--a-" + s.key + ")", text: String(s.nr),
               schrift: s.natur === "licht" ? "var(--a-" + s.key + "-schrift)" : "var(--on-accent)" };
    });
    felder.forEach(function (f, i) {
      var prev = felder[(i - 1 + felder.length) % felder.length], next = felder[(i + 1) % felder.length];
      var a0 = (f.platz + prev.platz + (i === 0 ? -360 : 0)) / 2;
      var a1 = (f.platz + next.platz + (i === felder.length - 1 ? 360 : 0)) / 2;
      svg.appendChild(sv("path", { d: ring(252, 300, a0, a1), fill: f.farbe, "class": "sektor" }));
      var p = pol(276, f.platz);
      svg.appendChild(sv("text", { x: p[0], y: p[1] + 8, "text-anchor": "middle", "class": "nr", fill: f.schrift }, f.text));
    });
    // Die sechs Achsen als Durchmesser durch die Mitte
    D.achsen.forEach(function (a) {
      var p0 = pol(142, a.a.platz), p1 = pol(142, a.b.platz);
      svg.appendChild(sv("line", { x1: p0[0], y1: p0[1], x2: p1[0], y2: p1[1], "class": "diam" }));
    });
  }

  /* --- Die sechs Achsen ------------------------------------------------------ */
  function seite(a, welche) {
    var P = a[welche], s = byKey[P.key], d = el("div", "seite");
    var t = "--a-" + s.key;
    d.style.background = "var(" + t + ")";
    d.style.color = P.natur === "licht" ? "var(" + t + "-schrift)" : "var(--on-accent)";
    var kopf = el("div");
    kopf.appendChild(el("div", "rolle", P.ort + " · " + KURZNATUR[P.natur]));
    var n = el("div", "sek"); n.textContent = s.kurz;
    if (P.natur === "grund") n.style.color = "var(" + t + "-zeichen)";
    kopf.appendChild(n);
    kopf.appendChild(el("p", "probe", P.natur === "licht"
      ? "Diese Fläche trägt kein Weiss. Darum steht hier die geforderte Farbe – auch klein."
      : "Diese Fläche trägt Weiss. Die geforderte Farbe leuchtet darauf als Zeichen."));
    d.appendChild(kopf);
    d.appendChild(el("div", "hx", P.eigen.toUpperCase()));
    return d;
  }
  function bauAchsen() {
    var wrap = $("#achsen-liste");
    D.achsen.forEach(function (a) {
      var c = el("article", "ach");
      c.appendChild(el("h3", null, a.name));
      c.appendChild(el("p", "satz", a.satz));
      var p = el("div", "paar");
      p.appendChild(seite(a, "a")); p.appendChild(seite(a, "b"));
      c.appendChild(p);
      var z = el("div", "zahlen");
      [["Schrift auf " + a.a.ort, a.kontrast.a_flaeche_schrift],
       ["Schrift auf " + a.b.ort, a.kontrast.b_flaeche_schrift],
       ["auf Papier", Math.min(a.kontrast.a_auf_papier, a.kontrast.b_auf_papier)]]
        .forEach(function (x) { z.appendChild(el("span", null, "<b>" + x[0] + "</b> " + fmt(x[1]))); });
      c.appendChild(z);
      wrap.appendChild(c);
    });
  }

  /* --- Die zwölf Sektionen --------------------------------------------------- */
  function karte(s) {
    var t = "--a-" + s.key, a = el("article", "sk"); a.dataset.key = s.key;
    var band = el("div", "band");
    band.style.background = "var(" + t + ")";
    band.style.color = s.natur === "licht" ? "var(" + t + "-schrift)" : "var(--on-accent)";
    var nr = el("div", "nr", s.nr + " · " + s.kurz); band.appendChild(nr);
    var zeichen = el("div", "zeichen", s.ort + " · " + NATUR[s.natur]);
    if (s.natur === "grund") zeichen.style.color = "var(" + t + "-zeichen)";
    band.appendChild(zeichen);
    a.appendChild(band);
    var kopf = el("div", "kopf");
    var h = el("h4"); h.textContent = s.name; kopf.appendChild(h);
    kopf.appendChild(el("p", "satz", s.satz));
    var orte = el("div", "orte");
    orte.appendChild(el("span", "chip", s.achse_name));
    orte.appendChild(el("span", "meta", s.para));
    orte.appendChild(el("span", "wandert", s.wandert));
    kopf.appendChild(orte);
    a.appendChild(kopf);
    a.appendChild(el("p", "grund-text", s.grund_text));
    var w = el("div", "werte");
    w.appendChild(wert(s.flaeche.toUpperCase(), "Fläche", s.flaeche));
    w.appendChild(wert(s.zeichen.toUpperCase(), s.natur === "licht" ? "Schrift" : "Zeichen", s.zeichen));
    if (s.heute) {
      var heute = el("span", "meta");
      var pt = el("span", "punkt"); pt.style.background = s.heute; heute.appendChild(pt);
      heute.appendChild(document.createTextNode(" heute " + s.heute.toUpperCase()));
      w.appendChild(heute);
    }
    a.appendChild(w);
    return a;
  }
  function bauSektionen() {
    var wrap = $("#sektionen-liste");
    reihe.forEach(function (s) { wrap.appendChild(karte(s)); });
  }

  function bauMono() {
    var wrap = $("#mono-liste");
    D.mono.forEach(function (m) {
      var c = el("article", "mk");
      var f = el("div", "flaeche");
      f.style.background = "var(--a-mono-" + m.key + ")";
      f.appendChild(document.createTextNode(m.name));
      f.appendChild(el("small", null, m.hex.toUpperCase() + " · Weiss " + fmt(m.weiss)));
      c.appendChild(f);
      c.appendChild(el("p", null, m.grund_text));
      var n = m.naehe;
      c.appendChild(el("p", "meta", "Nächster Sektionston: " + n.kurz + " " + n.hex.toUpperCase() +
        " – " + n.platz_abstand + "° entfernt auf dem Kreis, Helligkeitsabstand " + n.d_L +
        ", Buntheitsabstand " + n.d_C + "."));
      wrap.appendChild(c);
    });
  }

  /* --- Anwendung -------------------------------------------------------------- */
  function bandFuellen(node, s, klein) {
    var t = "--a-" + s.key;
    node.style.background = "var(" + t + ")";
    node.style.color = s.natur === "licht" ? "var(" + t + "-schrift)" : "var(--on-accent)";
    if (klein) {
      node.innerHTML = "";
      var k = el("span", "kick", s.achse_name);
      var h = el("h3", null, s.name);
      var p = el("p", null, s.natur === "licht"
        ? "Leuchtende Fläche, Schrift in der geforderten Farbe."
        : "Tragende Fläche, Weiss darauf, Zeichen in der geforderten Farbe.");
      if (s.natur === "grund") k.style.color = "var(" + t + "-zeichen)";
      node.appendChild(k); node.appendChild(h); node.appendChild(p);
    }
  }
  function waehle(key) {
    var s = byKey[key] || reihe[0], t = "--a-" + s.key;
    var band = $("#bsp-band");
    bandFuellen(band, s, false);
    $("#bsp-titel").textContent = s.name;
    $("#bsp-kick").textContent = "Tagung · 14. bis 16. Mai";
    if (s.natur === "grund") $("#bsp-kick").style.color = "var(" + t + "-zeichen)";
    else $("#bsp-kick").style.color = "";
    $("#bsp-band-meta").textContent = s.natur === "licht"
      ? "Kopfband · leuchtende Fläche, Schrift in der geforderten Farbe"
      : "Kopfband · tragende Fläche, Weiss darauf, Kicker im Zeichen";

    var chip1 = $("#bsp-chip1"), chip2 = $("#bsp-chip2"), knopf = $("#bsp-knopf");
    chip1.textContent = s.kurz;
    chip1.style.background = "var(" + t + "-hauch)"; chip1.style.color = "var(" + t + "-tinte)";
    chip2.style.background = "var(" + t + "-hauch)"; chip2.style.color = "var(" + t + "-tinte)";
    knopf.style.background = "var(" + t + "-schrift)"; knopf.style.color = "var(--on-accent)";
    $("#bsp-zeichen-meta").textContent = "Chip · Hauch mit der tragenden Farbe. Knopf · tragende Farbe mit Weiss – für beide Naturen gleich";

    $("#bsp-kick2").textContent = s.kurz;
    $("#bsp-kick2").style.color = "var(" + t + "-tinte)";
    $("#bsp-titel2").style.color = "var(" + t + "-tinte)";
    $("#bsp-text-meta").textContent = "Kicker und Titel in der Schriftfarbe der Sektion – im Dunkelmodus ein heller Hauch · " + s.ort;

    var gegen = byKey[s.partner_key];
    bandFuellen($("#bsp-gegen"), gegen, true);

    document.querySelectorAll("#waehler button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.key === s.key));
    });
  }
  function bauWaehler() {
    var w = $("#waehler");
    reihe.forEach(function (s) {
      var b = el("button"); b.type = "button"; b.dataset.key = s.key; b.setAttribute("aria-pressed", "false");
      var p = el("span", "punkt"); p.style.background = "var(--a-" + s.key + ")"; b.appendChild(p);
      b.appendChild(document.createTextNode(s.kurz));
      b.addEventListener("click", function () { waehle(s.key); });
      w.appendChild(b);
    });
  }

  /* --- Das Vorbild, gemessen --------------------------------------------------- */
  function bauVorbild() {
    var v = D.vorbild;
    $("#pf-gelb").textContent = v.gelb;
    $("#pf-petrol").textContent = v.petrol + " (" + fmt(kontrast(v.petrol, v.gelb)) + " auf dem Gelb)";
  }

  /* --- Nachmessen am gerenderten Blatt ------------------------------------------ */
  function messen() {
    document.querySelectorAll(".paar .seite").forEach(function (d) {
      var bg = paintHex(d), fg = paintHex(d, "color"), k = kontrast(fg, bg);
      var hx = d.querySelector(".hx");
      hx.textContent = bg.toUpperCase() + " · Schrift " + fmt(k) + (k >= 4.5 ? " ✓" : " ✗");
    });
  }

  function render() {
    setzeTokens(); bauKreis(); bauAchsen(); bauSektionen(); bauMono(); bauWaehler(); bauVorbild();
    requestAnimationFrame(function () { messen(); waehle("ps"); });
    new MutationObserver(function () { setzeTokens(); requestAnimationFrame(messen); })
      .observe(ROOT, { attributes: true, attributeFilter: ["data-theme"] });
    try {
      matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
        setzeTokens(); requestAnimationFrame(messen);
      });
    } catch (e) { /* ältere Browser: der Hauch bleibt beim Hellwert */ }
  }
  if (document.readyState !== "loading") render();
  else document.addEventListener("DOMContentLoaded", render);
})();
