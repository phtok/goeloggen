/* Schriftgrenze – Goetheanum und Source Sans 3 nebeneinander.
   Texte aus dem Lesetest (apps/lesetest/texte.js, Kafka, gemeinfrei).
   Zustand in der Adresse (?laenge=…&grad=…), damit ein Blick teilbar ist. */
(function () {
  "use strict";
  var T = {};
  (window.LESETEXTE || []).forEach(function (t) { T[t.id] = t; });

  // Länge → Text. ‹Ein Satz› ist der lange Mittelsatz aus ‹Zerstreutes Hinausschaun›.
  var LAENGE = {
    satz:   { id: "hinausschaun", absaetze: function (t) { return [t.absaetze[1]]; }, titel: false },
    absatz: { id: "fabel",        absaetze: function (t) { return t.absaetze; },      titel: false },
    "250":  { id: "fahrgast",     absaetze: function (t) { return t.absaetze; },      titel: true },
    "500":  { id: "hausvater",    absaetze: function (t) { return t.absaetze; },      titel: true },
    "1000": { id: "landstrasse",  absaetze: function (t) { return t.absaetze; },      titel: true }
  };
  var SCHNITT = { ruhig: ["Ruhig", "var(--w-ruhig)"], klar: ["Klar", "var(--w-klar)"], deutlich: ["Deutlich", "var(--w-deutlich)"] };
  var GEGEN = { source: "Source Sans 3", "noto-sans": "Noto Sans", "noto-serif": "Noto Serif" };
  var WAHL = { gegen: "source", laenge: "absatz", grad: "haus", mass: "70", schnitt: "klar", grund: null };
  var GUELTIG = {
    gegen: Object.keys(GEGEN), laenge: Object.keys(LAENGE), grad: ["14", "16", "18", "20", "24", "haus"],
    mass: ["70", "haus"], schnitt: Object.keys(SCHNITT), grund: ["light", "dark"]
  };

  var html = document.documentElement;
  WAHL.grund = html.getAttribute("data-theme") === "dark" ? "dark" : "light";
  var q = new URLSearchParams(location.search);
  ["gegen", "laenge", "grad", "mass", "schnitt"].forEach(function (k) {
    var v = q.get(k); if (v && GUELTIG[k].indexOf(v) >= 0) WAHL[k] = v;
  });

  var paar = document.getElementById("paar");
  var druck = document.getElementById("druck");

  function fuellen(ziel, text, mitTitel) {
    ziel.textContent = "";
    if (mitTitel) {
      var h = document.createElement("h3");
      h.className = "probe-titel"; h.textContent = text.titel; ziel.appendChild(h);
    }
    LAENGE[WAHL.laenge].absaetze(text).forEach(function (a) {
      var p = document.createElement("p"); p.textContent = a; ziel.appendChild(p);
    });
  }

  function setzen(spalten, grad) {
    var g = spalten.querySelector('[data-probe="g"]');
    g.style.fontWeight = SCHNITT[WAHL.schnitt][1];
    spalten.querySelector('[data-probe="s"]').setAttribute("data-gegen", WAHL.gegen);
    spalten.querySelectorAll(".probe").forEach(function (el) { el.style.fontSize = grad; });
    spalten.setAttribute("data-mass", WAHL.mass);
  }

  // Zeichen je Zeile, gemessen: jede Zeile eines Absatzes ausser der letzten,
  // davon der Median. Ohne volle Zeile zählt die einzige.
  function zeichenJeZeile(probe) {
    var zeilen = [], r = document.createRange();
    probe.querySelectorAll("p").forEach(function (p) {
      var eigene = [], oben = null, n = 0;
      var w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
      for (var k = w.nextNode(); k; k = w.nextNode()) {
        for (var i = 0; i < k.length; i++) {
          r.setStart(k, i); r.setEnd(k, i + 1);
          var rs = r.getClientRects(); if (!rs.length) continue;
          var y = rs[0].top;
          if (oben !== null && Math.abs(y - oben) > 2) { eigene.push(n); n = 0; }
          if (oben === null || Math.abs(y - oben) > 2) oben = y;
          n++;
        }
      }
      if (!eigene.length) eigene.push(n);
      zeilen = zeilen.concat(eigene);
    });
    zeilen.sort(function (a, b) { return a - b; });
    return zeilen.length ? zeilen[Math.floor(zeilen.length / 2)] : 0;
  }

  function ablesen() {
    ["g", "s"].forEach(function (s) {
      var n = zeichenJeZeile(paar.querySelector('[data-probe="' + s + '"]'));
      var pt = paar.querySelector('[data-probe="' + s + '"]');
      var px = Math.round(parseFloat(getComputedStyle(pt).fontSize) * 10) / 10;
      paar.querySelector('[data-ablese="' + s + '"]').textContent =
        String(px).replace(".", ",") + " px · ≈ " + n + " Zeichen je Zeile";
    });
  }

  function druckBauen(text, mitTitel) {
    druck.textContent = "";
    [9, 10, 11, 12].forEach(function (pt) {
      var block = document.createElement("div"); block.className = "druck-block";
      var h = document.createElement("h2");
      h.textContent = pt + " pt · Goetheanum " + SCHNITT[WAHL.schnitt][0] + " | " + GEGEN[WAHL.gegen];
      block.appendChild(h);
      var kopie = paar.cloneNode(true);
      kopie.removeAttribute("id");
      kopie.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); });
      kopie.querySelectorAll(".spalte>h2,.ablese").forEach(function (el) { el.remove(); });
      kopie.querySelectorAll(".probe").forEach(function (el) { el.style.fontSize = pt + "pt"; });
      block.appendChild(kopie);
      druck.appendChild(block);
    });
  }

  function zeigen() {
    var L = LAENGE[WAHL.laenge], text = T[L.id];
    if (!text) return;
    paar.querySelectorAll(".probe").forEach(function (el) { fuellen(el, text, L.titel); });
    setzen(paar, WAHL.grad === "haus" ? "var(--t-body)" : WAHL.grad + "px");
    document.querySelector("[data-schnitt-name]").textContent = SCHNITT[WAHL.schnitt][0];
    document.querySelector("[data-gegen-name]").textContent = GEGEN[WAHL.gegen];
    document.getElementById("quelle").textContent = text.quelle;
    druckBauen(text, L.titel);

    document.querySelectorAll(".seg[data-wahl]").forEach(function (seg) {
      var k = seg.getAttribute("data-wahl");
      seg.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-wert") === WAHL[k]));
      });
    });
    var neu = new URLSearchParams({ gegen: WAHL.gegen, laenge: WAHL.laenge, grad: WAHL.grad, mass: WAHL.mass, schnitt: WAHL.schnitt });
    try { history.replaceState(null, "", "?" + neu.toString()); } catch (e) {}
    requestAnimationFrame(ablesen);
  }

  document.querySelectorAll(".seg[data-wahl]").forEach(function (seg) {
    seg.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b) return;
      var k = seg.getAttribute("data-wahl");
      WAHL[k] = b.getAttribute("data-wert");
      if (k === "grund") {
        html.setAttribute("data-theme", WAHL.grund);
        try { localStorage.setItem("goeTheme", WAHL.grund); } catch (e) {}
      }
      zeigen();
    });
  });

  document.getElementById("drucken").addEventListener("click", function () { window.print(); });
  // Gedruckt wird immer hell: Papier ist weiss.
  var vorher = null;
  addEventListener("beforeprint", function () { vorher = html.getAttribute("data-theme"); html.setAttribute("data-theme", "light"); });
  addEventListener("afterprint", function () { if (vorher) html.setAttribute("data-theme", vorher); });

  var warte;
  addEventListener("resize", function () { clearTimeout(warte); warte = setTimeout(ablesen, 150); });

  zeigen();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(ablesen);
})();
