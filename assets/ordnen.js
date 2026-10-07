/* Ordnen-Modus der Startseite (index.html?ordnen).
   Zeigt die Startseite so, wie sie live steht – dieselben Karten, dieselbe
   Schublade –, und legt die Sortier-Griffe direkt darauf: verschieben (Ziehen
   oder Pfeile), ausblenden, wieder einblenden. Speichern schreibt
   tools.json → reihenfolge über die Edge Function sortierer-commit (Verlauf =
   Git). Ersetzt die getrennte Listen-Ansicht des alten Sortierers.
   Aufruf: window.goeOrdnen(manifest, tile) – tile(t) baut die echte Karte. */
(function () {
  "use strict";
  var LS = "goe-ordnen-entwurf-v1";
  var FUNKTION = "https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/sortierer-commit";
  var PUBKEY = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";
  var PUBLIC = ["generatoren", "schrift", "system", "anwendung"];
  var FLAECHEN = ["karten", "schublade"];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); }
  function kopie(o) { return JSON.parse(JSON.stringify(o)); }
  function gleich(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  window.goeOrdnen = function (man, tile) {
    var bySlug = {};
    var publik = (man.tools || []).filter(function (t) {
      return PUBLIC.indexOf(t.cat) >= 0 && (t.status === "live" || t.status === "beta");
    });
    publik.forEach(function (t) { bySlug[t.slug] = t; });
    var slugs = publik.map(function (t) { return t.slug; });

    // Stand der Datei, bereinigt: fehlende Werkzeuge hinten anhängen,
    // verschwundene entfernen; bewusst Ausgeblendetes bleibt ausgeblendet.
    function bereinigt(R) {
      R = R || {}; var A = R.aus || {};
      var s = { an: {}, aus: {} };
      FLAECHEN.forEach(function (k) {
        var aus = (Array.isArray(A[k]) ? A[k] : []).filter(function (x) { return slugs.indexOf(x) >= 0; });
        var an = (Array.isArray(R[k]) ? R[k] : []).filter(function (x) { return slugs.indexOf(x) >= 0 && aus.indexOf(x) < 0; });
        slugs.forEach(function (x) { if (an.indexOf(x) < 0 && aus.indexOf(x) < 0) an.push(x); });
        s.an[k] = an; s.aus[k] = aus;
      });
      return s;
    }
    var datei = bereinigt(man.reihenfolge);
    var stand = kopie(datei);
    try {
      var e = JSON.parse(localStorage.getItem(LS) || "null");
      if (e && e.an && e.aus) stand = bereinigt({ karten: e.an.karten, schublade: e.an.schublade, aus: e.aus });
    } catch (x) {}
    var flaeche = "karten";
    try { if (sessionStorage.getItem(LS + "-flaeche") === "schublade") flaeche = "schublade"; } catch (x) {}

    // --- Gerüst -------------------------------------------------------------
    document.documentElement.classList.add("goe-ordnen");
    var main = document.getElementById("inhalt");
    var cards = document.getElementById("cards");
    var bar = document.createElement("div");
    bar.className = "ord-bar";
    bar.innerHTML =
      '<div class="seg" role="group" aria-label="Fläche">' +
        '<button type="button" data-flaeche="karten">Startseite</button>' +
        '<button type="button" data-flaeche="schublade">Schublade</button>' +
      '</div>' +
      '<p class="ord-status" role="status"></p>' +
      '<span class="ord-luft"></span>' +
      '<button class="btn ghost" type="button" data-tu="verwerfen">Verwerfen</button>' +
      '<button class="btn primary" type="button" data-tu="speichern">Speichern</button>' +
      '<a class="btn ghost" href="./">Fertig</a>';
    main.insertBefore(bar, cards);
    var statusEl = bar.querySelector(".ord-status");
    var schublade = document.createElement("div");
    schublade.className = "ord-schublade";
    main.insertBefore(schublade, cards.nextSibling);
    var ausWrap = document.createElement("section");
    ausWrap.className = "ord-aus";
    main.appendChild(ausWrap);

    var meldung = "";
    function status(msg, fehler) { meldung = msg || ""; statusEl.classList.toggle("err", !!fehler); zeigeStatus(); }
    function zeigeStatus() {
      statusEl.textContent = meldung || (gleich(stand, datei) ? "Live-Stand" : "Ungespeicherte Änderungen");
    }
    function sichern() {
      try {
        if (gleich(stand, datei)) localStorage.removeItem(LS);
        else localStorage.setItem(LS, JSON.stringify(stand));
      } catch (x) {}
    }

    // --- Zeichnen -----------------------------------------------------------
    function name(s) { var t = bySlug[s]; return t ? t.title : s; }
    function knopf(akt, i, zeichen, label, aus) {
      return '<button class="btn ord-k" type="button" data-akt="' + akt + '" data-i="' + i + '"' +
        (aus ? " disabled" : "") + ' aria-label="' + esc(label) + '">' + zeichen + '</button>';
    }
    function zeichnen() {
      bar.querySelectorAll("[data-flaeche]").forEach(function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-flaeche") === flaeche ? "true" : "false");
      });
      bar.querySelector('[data-tu="verwerfen"]').disabled = gleich(stand, datei);
      cards.hidden = flaeche !== "karten";
      schublade.hidden = flaeche !== "schublade";
      var an = stand.an[flaeche], aus = stand.aus[flaeche], n = an.length;

      cards.innerHTML = ""; schublade.innerHTML = "";
      if (flaeche === "karten") {
        an.forEach(function (s, i) {
          var w = document.createElement("div");
          w.className = "ord-item"; w.draggable = true; w.setAttribute("data-i", i);
          var t = tile(bySlug[s]); t.draggable = false; t.tabIndex = -1;
          w.appendChild(t);
          w.insertAdjacentHTML("beforeend", '<div class="ord-ctl">' +
            knopf("vor", i, "‹", name(s) + " nach vorn", i === 0) +
            knopf("nach", i, "›", name(s) + " nach hinten", i === n - 1) +
            knopf("aus", i, "Ausblenden", name(s) + " ausblenden") + '</div>');
          cards.appendChild(w);
        });
      } else {
        schublade.innerHTML = '<div class="dhead"><span class="t">Navigation</span></div>' +
          '<div class="body"><span class="dsnav-link dsnav-home"><span class="tt">Startseite</span></span>' +
          an.map(function (s, i) {
            return '<div class="dsnav-link ord-item" draggable="true" data-i="' + i + '">' +
              '<span class="tt">' + esc(name(s)) + '</span><span class="ord-ctl">' +
              knopf("vor", i, "↑", name(s) + " nach oben", i === 0) +
              knopf("nach", i, "↓", name(s) + " nach unten", i === n - 1) +
              knopf("aus", i, "Ausblenden", name(s) + " ausblenden") + '</span></div>';
          }).join("") + '</div>';
      }

      ausWrap.hidden = !aus.length;
      ausWrap.innerHTML = aus.length ? '<h2>Ausgeblendet</h2><ul>' + aus.map(function (s, j) {
        return '<li><span>' + esc(name(s)) + '</span>' +
          knopf("ein", j, "Einblenden", name(s) + " einblenden") + '</li>';
      }).join("") + '</ul>' : "";
      zeigeStatus();
    }

    // --- Handeln ------------------------------------------------------------
    function aendern(fn, fokus) {
      fn(stand.an[flaeche], stand.aus[flaeche]);
      meldung = ""; sichern(); zeichnen();
      if (fokus) {
        var z = document.querySelector(fokus);
        if (z && !z.disabled) z.focus();
        else { var alt = document.querySelector(".ord-ctl .ord-k:not([disabled])"); if (alt) alt.focus(); }
      }
    }
    function schiebe(von, nach) {
      aendern(function (an) {
        if (nach < 0 || nach >= an.length || von === nach) return;
        an.splice(nach, 0, an.splice(von, 1)[0]);
      });
    }
    document.addEventListener("click", function (ev) {
      var f = ev.target.closest("[data-flaeche]");
      if (f && bar.contains(f)) {
        flaeche = f.getAttribute("data-flaeche"); meldung = "";
        try { sessionStorage.setItem(LS + "-flaeche", flaeche); } catch (x) {}
        zeichnen(); return;
      }
      // Karten führen im Ordnen-Modus nirgendwohin – sie sind Griff, nicht Link.
      if (ev.target.closest(".ord-item .tile")) { ev.preventDefault(); return; }
      var k = ev.target.closest("[data-akt]");
      if (!k) return;
      var i = +k.getAttribute("data-i"), akt = k.getAttribute("data-akt");
      if (akt === "vor" || akt === "nach") {
        var z = akt === "vor" ? i - 1 : i + 1;
        aendern(function (an) { if (z >= 0 && z < an.length) an.splice(z, 0, an.splice(i, 1)[0]); },
          '.ord-item[data-i="' + z + '"] [data-akt="' + akt + '"]');
      } else if (akt === "aus") {
        aendern(function (an, aus) { aus.push(an.splice(i, 1)[0]); },
          '.ord-item[data-i="' + i + '"] [data-akt="aus"]');
      } else if (akt === "ein") {
        aendern(function (an, aus) { an.push(aus.splice(i, 1)[0]); },
          '.ord-aus [data-akt="ein"][data-i="' + i + '"]');
      }
    });

    // Ziehen (Maus): innerhalb der sichtbaren Fläche.
    var zieht = null;
    document.addEventListener("dragstart", function (ev) {
      var it = ev.target.closest && ev.target.closest(".ord-item"); if (!it) return;
      zieht = +it.getAttribute("data-i"); it.classList.add("zieht");
      try { ev.dataTransfer.effectAllowed = "move"; ev.dataTransfer.setData("text/plain", ""); } catch (x) {}
    });
    document.addEventListener("dragover", function (ev) {
      var it = ev.target.closest && ev.target.closest(".ord-item"); if (!it || zieht === null) return;
      ev.preventDefault();
      document.querySelectorAll(".ord-item.ueber").forEach(function (z) { z.classList.remove("ueber"); });
      it.classList.add("ueber");
    });
    document.addEventListener("drop", function (ev) {
      var it = ev.target.closest && ev.target.closest(".ord-item"); if (!it || zieht === null) return;
      ev.preventDefault(); var von = zieht; zieht = null;
      schiebe(von, +it.getAttribute("data-i"));
    });
    document.addEventListener("dragend", function () {
      zieht = null;
      document.querySelectorAll(".ord-item.zieht, .ord-item.ueber").forEach(function (z) { z.classList.remove("zieht", "ueber"); });
    });

    bar.querySelector('[data-tu="verwerfen"]').addEventListener("click", function () {
      stand = kopie(datei); meldung = ""; sichern(); zeichnen();
    });

    function nutzlast() {
      return { reihenfolge: { schublade: stand.an.schublade, karten: stand.an.karten,
        aus: { schublade: stand.aus.schublade, karten: stand.aus.karten } } };
    }
    var speichernBtn = bar.querySelector('[data-tu="speichern"]');
    speichernBtn.addEventListener("click", function () {
      if (gleich(stand, datei)) { status("Nichts zu speichern – schon live."); return; }
      speichernBtn.disabled = true; status("Speichere …");
      fetch(FUNKTION, {
        method: "POST",
        headers: { "Content-Type": "application/json", "apikey": PUBKEY, "Authorization": "Bearer " + PUBKEY },
        body: JSON.stringify(nutzlast())
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, code: r.status, j: j }; });
      }).then(function (res) {
        if (res.ok && res.j && res.j.ok) {
          datei = kopie(stand); sichern(); zeichnen();
          status(res.j.unchanged ? "Schon live." : "Gespeichert. Live in rund einer Minute.");
        } else if (res.code === 403) {
          status("Speichern geht nur auf werkzeuge.goetheanum.ch.", true);
        } else {
          status("Nicht gespeichert (" + ((res.j && res.j.error) || res.code) + "). Der Entwurf bleibt hier.", true);
        }
      }).catch(function () {
        status("Netzwerkfehler – nicht gespeichert. Der Entwurf bleibt hier.", true);
      }).then(function () { speichernBtn.disabled = false; });
    });

    zeichnen();
  };
})();
