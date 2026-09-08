/* =============================================================================
   Goetheanum CI – Familienmenü: von jeder Seite der Familie zurück ins Ganze.
   -----------------------------------------------------------------------------
   Einbinden (zwei Zeilen, auf jeder Seite der Familie – auch fremden CMS):

     <script src="https://werkzeuge.goetheanum.ch/design-system/familie.js"
             data-here="ms" data-lang="de"></script>

   Attribute:
     data-here   Schlüssel der eigenen Seite (Sektion/Bereich/Eintrag, z. B. "ms")
                 → dieser Eintrag trägt aria-current und steht in Deutlich.
     data-lang   de | en | fr | es (Standard: <html lang>, sonst de)
     data-form   schweber | zeile | beide (Standard: schweber)
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
  var FORM = (s && s.dataset.form) || "schweber";
  var HERE = (s && s.dataset.here) || "";
  var DACH_URL = "https://goetheanum.ch/";

  var MARK = '<svg class="mk" viewBox="6 5 14 18" aria-hidden="true" focusable="false" fill="currentColor">' +
    '<path d="m11.3891,8.0134l8.1716-2.8083v17.0421h-4.8546l.0057-6.2604c.0024-.4052-.0696-.7838-.1957-1.1631-.3842-1.1566-3.1269-6.8104-3.1269-6.8104"/>' +
    '<path d="m11.041,11.0259s2.4766,3.9592,2.4766,4.8845l.0388,6.3364h-2.8617l-.0178-2.1782c-.0283-1.3208-3.025-5.0471-3.025-5.0471l3.389-3.9956Z"/>' +
    '<path d="m6.7607,19.7208l1.9048-1.3532s.8921,1.4899.9714,2.0124c.0801.5225.0162,1.8676.0162,1.8676h-2.0253s.004-.491.0065-.7085c.0057-.385-.1165-.7142-.3033-1.0304-.0874-.148-.4926-.6616-.5702-.7878"/></svg>';
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

  // --- Öffner 1: Schweber – zuerst als Link, nach den Daten als Knopf --------
  var knopf = el("a", "goe-fam-knopf", MARK + '<span class="wort">Goetheanum</span>');
  knopf.href = DACH_URL; knopf.setAttribute("aria-label", W().dach);
  // --- Öffner 2: Familienzeile -----------------------------------------------
  var zeile = el("div", "goe-fam-zeile");
  zeile.innerHTML = '<div class="innen"><a class="dach" href="' + DACH_URL + '" aria-label="' + W().dach + '">' + MARK + '<span>Goetheanum</span></a>' +
    '<button class="alle" type="button" aria-haspopup="dialog" aria-expanded="false">' + W().alle + PFEIL + '</button></div>';
  var zeileBtn = zeile.querySelector(".alle");

  var schleier = el("div", "goe-fam-schleier");
  var panel = el("div", "goe-fam-panel");
  panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", W().menue); panel.hidden = true;

  var DATA = null, letzterOeffner = null;

  function setForm(f) {
    FORM = f;
    var zeigeSchweber = f !== "zeile", zeigeZeile = f !== "schweber";
    if (zeigeSchweber) { if (!knopf.parentNode) document.body.appendChild(knopf); } else if (knopf.parentNode) knopf.parentNode.removeChild(knopf);
    if (zeigeZeile) { if (!zeile.parentNode) document.body.insertBefore(zeile, document.body.firstChild); } else if (zeile.parentNode) zeile.parentNode.removeChild(zeile);
    if (istOffen()) schliessen();
  }

  // --- Schublade rendern -------------------------------------------------------
  function render() {
    if (!DATA) return;
    var dachHref = (DATA.dach && ((DATA.dach.hrefs || {})[LANG] || DATA.dach.href)) || DACH_URL;
    knopf.href = dachHref; zeile.querySelector(".dach").href = dachHref;
    panel.innerHTML = '<div class="kopf"><a class="dach" href="' + dachHref + '">' + MARK + '<span>' + (T(DATA.dach && DATA.dach.titel) || "Goetheanum") + '</span></a>' +
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

  // --- Öffnen, schliessen, Fokus halten ----------------------------------------
  function istOffen() { return panel.classList.contains("is-offen"); }
  function focusables() {
    var all = panel.querySelectorAll('a[href],button,summary,[tabindex]:not([tabindex="-1"])');
    return Array.prototype.filter.call(all, function (n) { return n.offsetParent !== null; });
  }
  function oeffnen(von) {
    letzterOeffner = von;
    panel.hidden = false;
    panel.classList.toggle("oben", von === zeileBtn);
    // Erst sichtbar machen, dann einblenden – sonst gibt es keinen Übergang.
    requestAnimationFrame(function () { panel.classList.add("is-offen"); schleier.classList.add("is-offen"); });
    panel.setAttribute("aria-modal", "true");
    knopf.setAttribute("aria-expanded", "true"); zeileBtn.setAttribute("aria-expanded", "true");
    var f = focusables(); if (f.length) f[0].focus();
  }
  function schliessen() {
    if (!istOffen()) return;
    panel.classList.remove("is-offen"); schleier.classList.remove("is-offen");
    panel.removeAttribute("aria-modal");
    knopf.setAttribute("aria-expanded", "false"); zeileBtn.setAttribute("aria-expanded", "false");
    setTimeout(function () { if (!istOffen()) panel.hidden = true; }, 220);
    if (letzterOeffner && letzterOeffner.parentNode) letzterOeffner.focus();
  }
  function umschalten(von) { istOffen() ? schliessen() : oeffnen(von); }

  schleier.addEventListener("click", schliessen);
  zeileBtn.addEventListener("click", function () { umschalten(zeileBtn); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && istOffen()) schliessen(); });
  panel.addEventListener("keydown", function (e) {
    if (e.key !== "Tab") return;
    var f = focusables(); if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

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
  function setLang(l) { LANG = (l || "de").slice(0, 2).toLowerCase(); knopfZuKnopf(); render(); }

  function knopfZuKnopf() {
    // Der Link wird zum Knopf – gleiche Klasse, gleiches Aussehen.
    if (knopf.tagName === "BUTTON") { knopf.setAttribute("aria-label", W().menue); return; }
    var b = el("button", "goe-fam-knopf", knopf.innerHTML);
    b.type = "button"; b.setAttribute("aria-haspopup", "dialog"); b.setAttribute("aria-expanded", "false");
    b.setAttribute("aria-label", W().menue);
    b.addEventListener("click", function () { umschalten(b); });
    if (knopf.parentNode) knopf.parentNode.replaceChild(b, knopf);
    knopf = b;
  }

  document.body.appendChild(schleier); document.body.appendChild(panel);
  setForm(FORM);

  fetch(JSON_URL, { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (j) {
    DATA = j; knopfZuKnopf(); render();
  }).catch(function () { /* ohne Daten bleibt der Link «Goetheanum» */ });

  window.goeFamilie = { setForm: setForm, setHere: setHere, setLang: setLang, oeffnen: function () { oeffnen(knopf); }, schliessen: schliessen };
})();
