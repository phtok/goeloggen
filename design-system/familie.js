/* =============================================================================
   Goetheanum CI – Familienmenü: von jeder Seite der Familie zurück ins Ganze.
   -----------------------------------------------------------------------------
   Einbinden (eine Zeile, auf jeder Seite der Familie – auch fremden CMS):

     <script src="https://werkzeuge.goetheanum.ch/design-system/familie.js"
             data-here="ms" data-lang="de"></script>

   Attribute:
     data-here   Schlüssel der eigenen Seite (Sektion/Bereich/Eintrag, z. B. "ms")
                 → dieser Eintrag trägt aria-current und steht in Deutlich.
     data-lang   de | en | fr | es (Standard: <html lang>, sonst de)
     data-seite  links | rechts – wo der Schweber sitzt (Standard: links; rechts
                 unten wohnen auf fremden Seiten meist Chat und Cookie-Hinweis)
     data-json   andere Datenquelle (Standard: familie.json neben diesem Skript)

   Das Skript bindet tokens.css und familie.css selbst ein, wenn sie fehlen.
   Fällt die Datenquelle aus, bleibt ein einfacher Link «Goetheanum» stehen.
   Nur Titel – das Menü koordiniert, es erklärt nicht (G03).
   ============================================================================= */
(function () {
  var s = document.currentScript;
  var SRC = (s && s.src) || "";
  var DIR = SRC ? SRC.slice(0, SRC.lastIndexOf("/") + 1) : "";
  var JSON_URL = (s && s.dataset.json) || DIR + "familie.json";
  var LANG = ((s && s.dataset.lang) || document.documentElement.lang || "de").slice(0, 2).toLowerCase();
  var SEITE = (s && s.dataset.seite) === "rechts" ? "rechts" : "links";
  var HERE = (s && s.dataset.here) || "";
  var DACH_URL = "https://goetheanum.ch/";

  // Die Marke kommt aus dem Logo-Generator, nicht aus freier Hand (DS08):
  // die Geometrie ist die des Kreis-Layouts (‹point›, apps/logos/engine.js) –
  // Kreisfläche, darin das Zeichen an seinem Platz.
  //
  // Farbe folgt dem Theme, nicht dem Druck: gerechnet hält festes Markenblau
  // auf dunklem Papier nur 2.76:1 und reisst damit unter die 3:1 für Grafik
  // (B02). --blue hellt im Dunkel auf und trägt 6.69:1 – hell wie dunkel, und
  // auch noch im Ruhezustand (3.12 bzw. 3.57). Der Schweber ist ein Bedien-
  // element, das die Markenform trägt, kein gedrucktes Logo; darum Fläche in
  // --paper und Zeichen in --blue statt zweier fester Werte.
  //
  // Leise statt laut: die gefüllte blaue Scheibe war auf schmalen Schirmen zu
  // dominant (Befund Auftraggeber, 8. September). Jetzt trägt der Ring die
  // Kontur, die Fläche ist Papier.
  var ZEICHEN = [
    "m11.3891,8.0134l8.1716-2.8083v17.0421h-4.8546l.0057-6.2604c.0024-.4052-.0696-.7838-.1957-1.1631-.3842-1.1566-3.1269-6.8104-3.1269-6.8104",
    "m11.041,11.0259s2.4766,3.9592,2.4766,4.8845l.0388,6.3364h-2.8617l-.0178-2.1782c-.0283-1.3208-3.025-5.0471-3.025-5.0471l3.389-3.9956Z",
    "m6.7607,19.7208l1.9048-1.3532s.8921,1.4899.9714,2.0124c.0801.5225.0162,1.8676.0162,1.8676h-2.0253s.004-.491.0065-.7085c.0057-.385-.1165-.7142-.3033-1.0304-.0874-.148-.4926-.6616-.5702-.7878"
  ];
  function punkt() {
    return '<svg class="goe-fam-marke" viewBox="0 0 28.3465 28.3465" aria-hidden="true" focusable="false">' +
      '<circle class="grund" cx="14.173" cy="14.173" r="13.5"/>' +
      ZEICHEN.map(function (d) { return '<path d="' + d + '"/>'; }).join("") + '</svg>';
  }
  var PFEIL = '<svg class="pfeil" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>';

  var WORTE = {
    de: { alle: "Alle Bereiche", menue: "Goetheanum – alle Bereiche", zu: "Schliessen", dach: "Goetheanum – zur Startseite" },
    en: { alle: "All areas", menue: "Goetheanum – all areas", zu: "Close", dach: "Goetheanum – home" },
    fr: { alle: "Tous les domaines", menue: "Goetheanum – tous les domaines", zu: "Fermer", dach: "Goetheanum – accueil" },
    es: { alle: "Todas las áreas", menue: "Goetheanum – todas las áreas", zu: "Cerrar", dach: "Goetheanum – inicio" }
  };
  function W() { return WORTE[LANG] || WORTE.de; }
  function T(obj) { if (!obj) return ""; if (typeof obj === "string") return obj; return obj[LANG] || obj.de || ""; }

  // --- Fundament sicherstellen (auf fremden Seiten fehlt es) ----------------
  function hasCss(name) {
    var ls = document.querySelectorAll('link[rel="stylesheet"]');
    for (var i = 0; i < ls.length; i++) if ((ls[i].getAttribute("href") || "").indexOf(name) >= 0) return true;
    return false;
  }
  function addCss(name) {
    var l = document.createElement("link"); l.rel = "stylesheet"; l.href = DIR + name; document.head.appendChild(l);
  }
  if (DIR) { if (!hasCss("tokens.css")) addCss("tokens.css"); if (!hasCss("familie.css")) addCss("familie.css"); }

  function el(tag, cls, html) { var n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; }

  // --- Der Öffner: zuerst ein Link, nach den Daten ein Knopf ----------------
  var knopf = el("a", "goe-fam-knopf " + SEITE, punkt());
  knopf.href = DACH_URL;
  knopf.setAttribute("aria-label", W().dach);
  knopf.setAttribute("data-tip", W().alle);

  var schleier = el("div", "goe-fam-schleier");
  var panel = el("div", "goe-fam-panel " + SEITE);
  panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", W().menue); panel.hidden = true;

  var DATA = null;

  function setSeite(seite) {
    SEITE = seite === "rechts" ? "rechts" : "links";
    knopf.classList.remove("links", "rechts"); knopf.classList.add(SEITE);
    panel.classList.remove("links", "rechts"); panel.classList.add(SEITE);
  }

  // --- Schublade rendern -----------------------------------------------------
  function render() {
    if (!DATA) return;
    var dachHref = (DATA.dach && ((DATA.dach.hrefs || {})[LANG] || DATA.dach.href)) || DACH_URL;
    knopf.href = dachHref;
    panel.innerHTML = '<div class="kopf"><a class="dach" href="' + dachHref + '">' + punkt() +
      '<span>' + (T(DATA.dach && DATA.dach.titel) || "Goetheanum") + '</span></a>' +
      '<button class="zu" type="button" aria-label="' + W().zu + '">×</button></div><div class="rumpf"></div>';
    var rumpf = panel.querySelector(".rumpf");
    var breit = matchMedia("(min-width:760px)").matches;
    var hereGruppe = null;
    (DATA.gruppen || []).forEach(function (g) {
      var d = el("details", "goe-fam-grp");
      d.appendChild(el("summary", null, '<span>' + T(g.titel) + '</span>' + PFEIL));
      var ul = el("ul", "goe-fam-liste liste");
      (g.eintraege || []).forEach(function (e) {
        var li = el("li");
        var a = el("a", "goe-fam-link");
        a.href = e.href;
        if (e.farbe) a.style.setProperty("--goe-fam-farbe", "var(--" + e.farbe + ")");
        a.innerHTML = (e.farbe ? '<span class="pt" aria-hidden="true"></span>' : "") + '<span>' + T(e.titel) + '</span>';
        if (HERE && e.key === HERE) { a.setAttribute("aria-current", "page"); hereGruppe = d; }
        li.appendChild(a); ul.appendChild(li);
      });
      d.appendChild(ul); rumpf.appendChild(d);
    });
    var grps = rumpf.querySelectorAll(".goe-fam-grp");
    for (var i = 0; i < grps.length; i++) grps[i].open = breit || grps[i] === hereGruppe || (!hereGruppe && i === 0);
    panel.querySelector(".zu").addEventListener("click", schliessen);
  }

  // --- Öffnen, schliessen, Fokus halten --------------------------------------
  function istOffen() { return panel.classList.contains("is-offen"); }
  function focusables() {
    var all = panel.querySelectorAll('a[href],button,summary,[tabindex]:not([tabindex="-1"])');
    return Array.prototype.filter.call(all, function (n) { return n.offsetParent !== null; });
  }
  function oeffnen() {
    panel.hidden = false;
    // Erst sichtbar machen, dann einblenden – sonst gibt es keinen Übergang.
    requestAnimationFrame(function () { panel.classList.add("is-offen"); schleier.classList.add("is-offen"); });
    panel.setAttribute("aria-modal", "true");
    knopf.setAttribute("aria-expanded", "true");
    wach();
    var f = focusables(); if (f.length) f[0].focus();
  }
  function schliessen() {
    if (!istOffen()) return;
    panel.classList.remove("is-offen"); schleier.classList.remove("is-offen");
    panel.removeAttribute("aria-modal");
    knopf.setAttribute("aria-expanded", "false");
    setTimeout(function () { if (!istOffen()) panel.hidden = true; }, 220);
    if (knopf.parentNode) knopf.focus();
  }
  function umschalten() { istOffen() ? schliessen() : oeffnen(); }

  schleier.addEventListener("click", schliessen);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && istOffen()) schliessen(); });
  panel.addEventListener("keydown", function (e) {
    if (e.key !== "Tab") return;
    var f = focusables(); if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  // --- Leise werden, wenn die Seite ruht -------------------------------------
  // Kein Wegklicken, kein gemerkter Zustand: der Schweber tritt von selbst
  // zurück und ist bei der ersten Regung wieder da. Die Ruhe-Deckkraft steht
  // in familie.css und ist so gewählt, dass der Ring 3:1 hält (B02).
  var ruheUhr = null;
  function wach() {
    knopf.classList.remove("is-ruhe");
    if (ruheUhr) clearTimeout(ruheUhr);
    if (istOffen()) return;
    ruheUhr = setTimeout(function () { if (!istOffen()) knopf.classList.add("is-ruhe"); }, 2600);
  }
  ["pointermove", "pointerdown", "scroll", "keydown", "wheel", "touchstart"].forEach(function (ev) {
    window.addEventListener(ev, wach, { passive: true });
  });
  wach();

  // Fokus nie verdecken (2.4.11): liegt das fokussierte Element unter dem
  // Schweber, weicht er aus – und kommt zurück, sobald der Fokus weiterzieht.
  document.addEventListener("focusin", function (e) {
    var t = e.target;
    if (!knopf.parentNode || !t || t === knopf || panel.contains(t)) { knopf.classList.remove("is-weg"); return; }
    var r = t.getBoundingClientRect(), k = knopf.getBoundingClientRect();
    var deckt = r.width && r.height && r.left < k.right && r.right > k.left && r.top < k.bottom && r.bottom > k.top;
    knopf.classList.toggle("is-weg", !!deckt);
  });
  document.addEventListener("focusout", function () { knopf.classList.remove("is-weg"); });

  // Breit ↔ schmal: Gruppen auf/zu wie beim ersten Rendern.
  matchMedia("(min-width:760px)").addEventListener("change", render);

  function setHere(k) { HERE = k || ""; render(); }
  function setLang(l) { LANG = (l || "de").slice(0, 2).toLowerCase(); zumKnopf(); render(); }

  function zumKnopf() {
    // Der Link wird zum Knopf – gleiche Klasse, gleiches Aussehen.
    if (knopf.tagName === "BUTTON") {
      knopf.setAttribute("aria-label", W().menue); knopf.setAttribute("data-tip", W().alle); return;
    }
    var b = el("button", knopf.className, knopf.innerHTML);
    b.type = "button"; b.setAttribute("aria-haspopup", "dialog"); b.setAttribute("aria-expanded", "false");
    b.setAttribute("aria-label", W().menue); b.setAttribute("data-tip", W().alle);
    b.addEventListener("click", umschalten);
    if (knopf.parentNode) knopf.parentNode.replaceChild(b, knopf);
    knopf = b;
    wach();
  }

  document.body.appendChild(schleier); document.body.appendChild(panel); document.body.appendChild(knopf);
  // Anwesenheit melden: die Rückmelde-Pille der Kopfzeile (nav.css) sitzt unten
  // mittig und überlappte den Schweber auf schmalen Schirmen ab 360 px abwärts
  // (gemessen). Sie weicht aus, sobald diese Klasse steht. Fehlt nav.css – auf
  // fremden Seiten der Normalfall – bleibt die Klasse folgenlos.
  document.documentElement.classList.add("goe-hat-schweber");

  fetch(JSON_URL, { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (j) {
    DATA = j; zumKnopf(); render();
  }).catch(function () { /* ohne Daten bleibt der Link «Goetheanum» */ });

  window.goeFamilie = { setSeite: setSeite, setHere: setHere, setLang: setLang, oeffnen: oeffnen, schliessen: schliessen };
})();
