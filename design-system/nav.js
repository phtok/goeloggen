/* =============================================================================
   Goetheanum CI – ds-nav: EINE Navigation, schlicht.
   -----------------------------------------------------------------------------
   Gerendert aus tools.json. Einbinden:

     <link rel="stylesheet" href="…/design-system/nav.css">
     <script src="…/design-system/nav.js" data-root="…/"></script>

   Bewusst nur ZWEI Dinge:
   1) Kopfzeile: Lockup links, Burger (☰) rechts. Auf dem DESKTOP zusätzlich die
      vier meistgenutzten Werkzeuge als Schnellzugriff (echter Mehrwert). Auf dem
      HANDY verschwindet die Navigation ganz im Burger.
   2) Schublade: EINE vertikale Liste mit aufklappbaren Bereichen (Welten). Der
      Bereich der aktuellen Seite ist offen, die übrigen eingeklappt.

   Keine zweite/dritte Leiste mehr – das war zu viel.

   FOKUS: öffentlich nur Fertiges (live/beta). INTERN (Pflege) blendet ALLES ein
   (alle Status + Backstage-Welten). Auslöser: das Wort „intern" tippen, oder
   einmalig ?intern an die URL. Gemerkt im localStorage; aus: erneut „intern".
   ============================================================================= */
(function () {
  var s = document.currentScript;
  var ROOT  = (s && s.dataset.root)  || "https://phtok.github.io/goeloggen/";
  if (ROOT.slice(-1) !== "/") ROOT += "/";
  var TOOLS = (s && s.dataset.tools) || ROOT + "tools.json";
  var HOME  = (s && s.dataset.home)  || ROOT;
  var ACTIVE = (s && s.dataset.active) || "";   // optional: aktiver Eintrag (slug); sonst aus der URL
  var KEY = "goeNavIntern";
  var THEME_KEY = "goeTheme";

  // --- Hell/Dunkel -----------------------------------------------------------
  function prefersDark() { return !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches); }
  function getTheme() {
    try { var t = localStorage.getItem(THEME_KEY); if (t === "light" || t === "dark") return t; } catch (e) {}
    return prefersDark() ? "dark" : "light";
  }
  // Sonne/Mond als Inline-SVG (currentColor) – NICHT als Unicode, das iOS sonst
  // zu Emoji umfärbt. Deterministisch in Hell wie Dunkel.
  var MOON_SVG = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" style="display:block" fill="currentColor"><path d="M20.7 13.3A8 8 0 1 1 10.7 3.3a6.3 6.3 0 1 0 10 10Z"/></svg>';
  var SUN_SVG = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" style="display:block" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.1M12 19.3v2.1M2.6 12h2.1M19.3 12h2.1M5.2 5.2l1.5 1.5M17.3 17.3l1.5 1.5M18.8 5.2l-1.5 1.5M6.7 17.3l-1.5 1.5"/></svg>';
  var SHARE_SVG = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" style="display:block" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 14V3.6M8.2 7.2 12 3.4l3.8 3.8"/><path d="M5.5 11.5v8h13v-8"/></svg>';
  var CHECK_SVG = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" style="display:block" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>';
  function updateThemeBtn() {
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    var alle = document.querySelectorAll(".dsnav .theme, .dsnav-drawer .theme");
    for (var i = 0; i < alle.length; i++) {
      alle[i].querySelector(".ic").innerHTML = dark ? SUN_SVG : MOON_SVG;
      alle[i].setAttribute("aria-label", dark ? "Hell schalten" : "Dunkel schalten");
      if (alle[i].hasAttribute("data-tip")) alle[i].setAttribute("data-tip", dark ? "Hellmodus" : "Dunkelmodus");
      alle[i].setAttribute("aria-pressed", String(dark));
      var lb = alle[i].querySelector(".lb");
      if (lb) lb.textContent = dark ? "Hell" : "Dunkel";
    }
  }
  function setTheme(t) {
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    document.documentElement.setAttribute("data-theme", t);
    updateThemeBtn();
  }
  // Sofort anwenden – vor dem Zeichnen, gegen Aufblitzen.
  document.documentElement.setAttribute("data-theme", getTheme());

  // --- Lesemodus (Block C) ---------------------------------------------------
  // Opt-in: tauscht NUR Textkörper + Erklärtexte Display→Source und erhöht das
  // Spacing (Regeln in base.css). Titel/Kicker/Marke bleiben Goetheanum. Zustand
  // in localStorage('goeRead'), VOR dem ersten Paint gesetzt – kein Aufblitzen.
  var READ_KEY = "goeRead", readBtn = null;
  function getRead() { try { return localStorage.getItem(READ_KEY) === "easy" ? "easy" : ""; } catch (e) { return ""; } }
  function updateReadBtn() {
    var on = document.documentElement.getAttribute("data-read") === "easy";
    var alle = document.querySelectorAll(".dsnav .read, .dsnav-drawer .read");
    for (var i = 0; i < alle.length; i++) {
      alle[i].setAttribute("aria-pressed", String(on));
      alle[i].setAttribute("aria-label", on ? "Lesemodus ausschalten" : "Lesemodus – Fliesstext in der Leseschrift");
    }
  }
  function setRead(on) {
    try { localStorage.setItem(READ_KEY, on ? "easy" : "off"); } catch (e) {}
    if (on) document.documentElement.setAttribute("data-read", "easy");
    else document.documentElement.removeAttribute("data-read");
    updateReadBtn();
  }
  if (getRead() === "easy") document.documentElement.setAttribute("data-read", "easy");

  // --- Anonyme Nutzungszählung (mitwachsend) ---------------------------------
  // Zählt je Werkzeug (data-active) den Seitenaufruf und Download-Klicks – ohne
  // Cookies, ohne IP/Personendaten, nur anonyme Summen über goeloggen_bump().
  // Jedes Werkzeug mit nav.js zählt automatisch mit; neue brauchen nichts extra.
  // Werkzeuge mit JS-Download rufen window.goeStat('download', name) selbst auf.
  var STAT_SB = "https://dagcsnfrlbpxcmdimnrw.supabase.co";
  var STAT_KEY = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";
  function goeBump(tool, event, label) {
    try {
      fetch(STAT_SB + "/rest/v1/rpc/goeloggen_bump", {
        method: "POST", keepalive: true,
        headers: { "Content-Type": "application/json", "apikey": STAT_KEY, "Authorization": "Bearer " + STAT_KEY },
        body: JSON.stringify({ p_tool: tool, p_event: event, p_label: (label || "").slice(0, 160) })
      }).catch(function () {});
    } catch (e) {}
  }
  function goeStat(event, label) {
    if (!ACTIVE || !event) return;
    goeBump(ACTIVE, event, label);
    // Grob-Region je Seitenaufruf: die ZEITZONE des Browsers (z. B. „Europe/Zurich")
    // – kein IP, keine Personendaten, nur eine anonyme Summe je Zeitzone. Gezählt
    // über dieselbe (tool,event,label)-Zählung mit dem reservierten Schlüssel
    // „__region" (die Statistik blendet ihn aus der Werkzeugliste aus).
    if (event === "view") {
      var tz = "";
      try { tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || ""); } catch (e) {}
      if (!tz) { try { tz = (navigator.language || ""); } catch (e) {} }
      if (tz) goeBump("__region", "view", tz);
    }
  }
  window.goeStat = goeStat;
  goeStat("view", "");
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[download]");
    if (!a) return;
    goeStat("download", (a.getAttribute("download") || a.getAttribute("href") || "").split("/").pop());
  });

  // Die meistgenutzten – nur als Desktop-Schnellzugriff in der Kopfzeile.
  var PRIMARY = [
    { label: "Logos",         slug: "logo-generator" },
    { label: "Schriften",     slug: "schriften" },
    { label: "Icons",         slug: "icons" },
    { label: "Mail-Signatur", slug: "signatur" },
    { label: "Visitenkarte",  slug: "visitenkarten" }
  ];

  // Öffentliche Welten (für alle sichtbar). Reihenfolge = Nutzungsbreite.
  var WORLDS = [
    { id: "werkzeuge", label: "Werkzeuge",
      intro: "Eintragen, fertiges Ergebnis übernehmen – täglicher Gebrauch.", cats: ["generatoren"] },
    { id: "schrift", label: "Schrift",
      intro: "Hausschrift und Regeln – ansehen, herunterladen, einbinden.", cats: ["schrift"] },
    { id: "elemente", label: "Elemente",
      intro: "Farben, Zeichen, Logos, Design-System – nachschlagen und holen.", cats: ["system"] },
    { id: "anwendungen", label: "Anwendungen",
      intro: "Fertige Vorlagen zum Übernehmen – Wallpaper, Präsentationen.", cats: ["anwendung"] }
  ];
  // Nur intern zusätzlich – die Backstage-Welten. Kuratierte Reihenfolge: erst die
  // Redaktions- und Beobachtungs-Welten, dann das Labor als Sammelort für Erprobung
  // und Abgelegtes. Das Labor trägt Unterwelten (verschachtelte Kisten) – die
  // Etiketten je Werkzeug (Beta/Entwurf/intern/geparkt) sagen ohnehin, was
  // öffentlich ist. Manifest-Kategorien, die hier fehlen, laufen beim Laden
  // automatisch als eigene Welt nach (Sicherheitsnetz).
  var INTERN_EXTRA = [
    { id: "kistenpflege", label: "Kistenpflege", intro: "Die Werkzeuge selbst pflegen – Stats, Sortierer, Post.", cats: ["kistenpflege"] },
    { id: "kampagne", label: "Kampagne", intro: "Kampagnen planen, verlinken, mailen, zählen.", cats: ["kampagne"] },
    { id: "schau", label: "Schau & Mockups", intro: "Präsentations-Mockups und Studien.", cats: ["schau"] },
    { id: "labor", label: "Labor", intro: "Erprobung und Abgelegtes – zum Ausprobieren, mit verschachtelten Kisten.",
      cats: ["labor"], sub: [
        { id: "ligaturen", label: "Ligaturen", intro: "Die Kiste nur für die Ligaturen.", cats: ["ligaturen"] },
        { id: "schriftpflege", label: "Schriftpflege", intro: "Grotesk, Gewichte und Mischsatz prüfen.", cats: ["schriftpflege"] },
        { id: "geparkt", label: "Geparktes", intro: "Konzepte, die später kommen.", cats: ["geparkt"] },
        { id: "archiv", label: "Überreste", intro: "Frühere Stände, eingefroren.", cats: ["archiv"] }
    ] }
  ];
  var PUBLIC_IDS = WORLDS.map(function (w) { return w.id; });

  function isIntern() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function setIntern(v) { try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {} }
  // Die Intern-/Backstage-Ansicht ist EINE Wahrheit – Werkzeuge können sie abfragen
  // (window.goeIntern()) und auf Wechsel reagieren (Event „goe:intern"). So koppeln
  // sich versteckte Profi-Optionen ans selbe Schloss wie die Backstage-Welten.
  window.goeIntern = isIntern;
  function emitIntern(on) { try { window.dispatchEvent(new CustomEvent("goe:intern", { detail: { on: on } })); } catch (e) {} }

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function resolveHref(h) {
    if (!h) return HOME;
    if (/^https?:/i.test(h)) return h;
    return ROOT + h.replace(/^\//, "");
  }
  function isExternal(h) { return /^https?:/i.test(h) && h.indexOf(ROOT) !== 0; }
  // Alle Kategorien einer Welt inklusive ihrer Unterwelten (flach).
  function catsOf(w) {
    var cs = (w.cats || []).slice();
    (w.sub || []).forEach(function (s) { cs = cs.concat(catsOf(s)); });
    return cs;
  }
  function currentFile() { var p = location.pathname.replace(/\/+$/, ""); return p.slice(p.lastIndexOf("/") + 1); }
  function isActiveTool(t) {
    if (ACTIVE) return t.slug === ACTIVE;
    var f = currentFile(); if (!f) return false;
    return t.href.replace(/^\//, "") === f;
  }

  // ?intern in der URL auswerten (einmalig aktivieren, dann säubern)
  (function () {
    var m = /[?&]intern(?:=([^&]*))?/.exec(location.search);
    if (m) {
      setIntern(m[1] !== "0" && m[1] !== "false");
      try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) {}
    }
  })();

  // --- Kopfzeile -------------------------------------------------------------
  // Optionaler Seiten-CTA in der Kopfzeile: data-cta="Beschriftung:#anker"
  // (Aktion = volles Blau + Weiss, B01). Immer sichtbar – keine Suchbewegung.
  var CTA = (s && s.dataset.cta) || "";
  var ctaHTML = "";
  if (CTA) {
    var ci = CTA.indexOf(":");
    var clabel = ci > 0 ? CTA.slice(0, ci) : CTA;
    var ctarget = ci > 0 ? CTA.slice(ci + 1) : "#";
    ctaHTML = '<a class="cta" href="' + ctarget + '">' + clabel + '</a>';
  }
  var header = el("header", "dsnav");
  header.innerHTML =
    '<div class="bar">' +
      '<a class="brand" href="' + HOME + '" aria-label="Goetheanum Werkzeuge – zur Übersicht">' +
        '<img class="lockup" src="' + ROOT + 'assets/logos/goetheanum-werkzeuge.svg" alt="Goetheanum Werkzeuge">' +
      '</a>' +
      '<nav class="worlds"></nav>' + ctaHTML +
      '<button class="read" type="button" aria-pressed="false" aria-label="Lesemodus – Fliesstext in der Leseschrift" data-tip="Lesemodus"><span class="ic" aria-hidden="true">a</span></button>' +
      '<button class="share" type="button" aria-label="Seite teilen – Link kopieren" data-tip="Teilen"><span class="ic">' + SHARE_SVG + '</span></button>' +
      '<button class="theme" type="button" aria-label="Dunkel schalten"><span class="ic"></span></button>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false" aria-label="Menü">' +
        '<span class="ic">☰</span><span class="idot" hidden></span></button>' +
    '</div>';
  document.body.insertBefore(header, document.body.firstChild);

  // Sprunglink „Zum Inhalt" (WCAG 2.4.1, Verbesserung): erstes fokussierbares
  // Element im Body, springt zur Hauptregion. main bekommt id=inhalt, falls es
  // nicht schon eine trägt (die Startseite setzt sie z. B. selbst). Erst nach
  // DOM-Ready, da nav.js vor <main> im Markup steht.
  var placeSkip = function () {
    var mainEl = document.querySelector("main");
    if (!mainEl || document.querySelector(".skip")) return;
    if (!mainEl.id) mainEl.id = "inhalt";
    var skip = el("a", "skip"); skip.href = "#" + mainEl.id; skip.textContent = "Zum Inhalt";
    document.body.insertBefore(skip, document.body.firstChild);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", placeSkip);
  else placeSkip();

  // Optionale Seiten-Sprungleiste: data-onpage="Label:#anker|…". Sie sitzt UNTER
  // dem Hero/der Lede (nicht über dem Titel) und klebt beim Scrollen unter der
  // Kopfzeile. Auf jeder Breite sichtbar (auch mobil), horizontal scrollbar.
  var ONPAGE = (s && s.dataset.onpage) || "";
  if (ONPAGE) {
    var pairs = ONPAGE.split("|").map(function (pair) {
      var ci = pair.indexOf(":");
      return { label: ci > 0 ? pair.slice(0, ci) : pair, target: ci > 0 ? pair.slice(ci + 1) : "#" };
    });
    // Eine reine Seiten-Leiste (kein einziges #-Ziel) ist die Klammer über mehrere
    // Seiten und gehört direkt unter die Kopfzeile, immer sichtbar. Sobald ein
    // #-Anker dabei ist, ist es eine Sprungleiste und sitzt unter dem Hero/der Lede.
    var isPageNav = pairs.every(function (p) { return p.target.charAt(0) !== "#"; });
    // Aktive Seite markieren: Ziel-URL relativ auflösen (über ein <a>) und mit der
    // aktuellen Seite vergleichen (index.html und Schrägstrich normalisiert). So
    // trifft es auch nachbarschaftliche Ziele wie „../utm-generator/".
    var canon = function (p) { return p.replace(/index\.html$/, "").replace(/\/+$/, "/"); };
    var herePath = canon(location.pathname);
    var resolve = function (t) { var a = document.createElement("a"); a.href = t; return canon(a.pathname); };
    var sub = el("nav", "dsnav-onpage");
    sub.setAttribute("aria-label", isPageNav ? "Kampagne – Seiten" : "Auf dieser Seite");
    sub.innerHTML = '<div class="row">' + pairs.map(function (p) {
      var self = isPageNav && p.target.charAt(0) !== "#" && resolve(p.target) === herePath;
      return '<a href="' + p.target + '"' + (self ? ' aria-current="page"' : '') + '>' + p.label + '</a>';
    }).join("") + '</div>';
    // Reine Seiten-Leiste: direkt unter die Kopfzeile. Sonst unter den Hero/die Lede.
    // nav.js läuft oft VOR <main> – darum die Platzierung bis DOM-ready aufschieben.
    var placeOnpage = function () {
      var heroEl = isPageNav ? null : document.querySelector("main .hero, .hero, main .lede");
      (heroEl || header).insertAdjacentElement("afterend", sub);
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", placeOnpage);
    } else {
      placeOnpage();
    }
    document.documentElement.classList.add("has-onpage");
  }

  var backdrop = el("div", "dsnav-backdrop");
  var drawer = el("aside", "dsnav-drawer");
  drawer.setAttribute("role", "dialog");
  drawer.setAttribute("aria-label", "Navigation");
  drawer.innerHTML =
    '<div class="dhead"><span class="t">Navigation</span>' +
      '<button class="close" type="button" aria-label="Schliessen">×</button></div>' +
    // Modi-Schalter (Lesemodus · Hell/Dunkel · Teilen): auf schmalen Schirmen
    // ziehen sie aus der Kopfzeile hierher – die Leiste behält nur Marke + Menü
    // (Fingerziel-Luft, B04); mit Wortmarke statt blossem Zeichen.
    '<div class="dmodes" role="group" aria-label="Anzeige-Modi">' +
      '<button class="read" type="button" aria-pressed="false" aria-label="Lesemodus – Fliesstext in der Leseschrift"><span class="ic" aria-hidden="true">a</span><span class="lb">Lesemodus</span></button>' +
      // Kurzes Wort («Dunkel»/«Hell») – im Gruppenkontext ‹Anzeige-Modi› eindeutig,
      // und die Reihe trägt so auch 320px-Schirme ohne Gedränge.
      '<button class="theme" type="button" aria-label="Dunkel schalten"><span class="ic"></span><span class="lb">Dunkel</span></button>' +
      '<button class="share" type="button" aria-label="Seite teilen – Link kopieren"><span class="ic">' + SHARE_SVG + '</span><span class="lb">Teilen</span></button>' +
    '</div>' +
    '<div class="dsearch"><input type="search" class="dsnav-q" placeholder="Werkzeug suchen …" aria-label="Werkzeug suchen" autocomplete="off"></div>' +
    '<div class="body"></div>' +
    '<div class="foot"><a href="mailto:philipp.tok@goetheanum.ch?subject=Feedback%20Goetheanum%20Werkzeuge">Feedback geben</a> · <a href="' + ROOT + 'design-system/">Design-System</a></div>';
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

  // Globaler Feedback-Einblender (unten, dezent, wegklickbar). Eine einladende
  // Frage statt Beta-Hinweis: motiviert zur Rückmeldung und öffnet die Mail mit
  // vorbereitetem Betreff samt aktueller Seite – niedrige Schwelle.
  var INVITE_KEY = "goeInviteSeen";
  var inviteSeen = false; try { inviteSeen = localStorage.getItem(INVITE_KEY) === "1"; } catch (e) {}
  if (!inviteSeen) {
    var subj = encodeURIComponent("Rückmeldung – " + (document.title || "Goetheanum Werkzeuge"));
    var invite = el("div", "dsnav-invite");
    invite.innerHTML =
      '<a class="ask" href="mailto:philipp.tok@goetheanum.ch?subject=' + subj + '">Fehlt Dir etwas? <b>Sag es uns</b></a>' +
      '<button class="x" type="button" aria-label="Ausblenden">×</button>';
    document.body.appendChild(invite);
    invite.querySelector(".x").addEventListener("click", function () {
      invite.remove(); try { localStorage.setItem(INVITE_KEY, "1"); } catch (e) {}
    });
  }

  var toast = el("div", "dsnav-toast"); document.body.appendChild(toast);
  function flash(msg) { toast.textContent = msg; toast.classList.add("show"); setTimeout(function () { toast.classList.remove("show"); }, 1400); }

  var btnAll = header.querySelector(".all");
  // --- Teilen: kopiert die KURZE Adresse des Werkzeugs (Alias /<slug>/) -------
  function shareUrl() {
    if (location.hostname === "werkzeuge.goetheanum.ch" && ACTIVE && location.pathname.indexOf("/apps/") === 0) {
      return "https://werkzeuge.goetheanum.ch/" + ACTIVE + "/";
    }
    return location.href.split("#")[0];
  }
  function wireShare(shareBtn) {
  shareBtn.addEventListener("click", function () {
    var url = shareUrl();
    var done = function () {
      shareBtn.querySelector(".ic").innerHTML = CHECK_SVG;
      shareBtn.classList.add("ok");
      setTimeout(function () {
        shareBtn.querySelector(".ic").innerHTML = SHARE_SVG;
        shareBtn.classList.remove("ok");
      }, 1400);
    };
    if (navigator.share && window.matchMedia && matchMedia("(pointer:coarse)").matches) {
      navigator.share({ title: document.title, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(done, function () {});
    }
  });
  }
  wireShare(header.querySelector(".share"));
  wireShare(drawer.querySelector(".dmodes .share"));

  function toggleTheme() {
    setTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
  }
  header.querySelector(".theme").addEventListener("click", toggleTheme);
  drawer.querySelector(".dmodes .theme").addEventListener("click", toggleTheme);
  updateThemeBtn();
  function toggleRead() {
    setRead(document.documentElement.getAttribute("data-read") !== "easy");
  }
  header.querySelector(".read").addEventListener("click", toggleRead);
  drawer.querySelector(".dmodes .read").addEventListener("click", toggleRead);
  updateReadBtn();
  var worldsNav = header.querySelector(".worlds");
  var drawerBody = drawer.querySelector(".body");
  var drawerTitle = drawer.querySelector(".dhead .t");
  var idot = btnAll.querySelector(".idot");
  var searchInput = drawer.querySelector(".dsnav-q");

  // Tippen filtert die Werkzeugliste; leere Bereiche werden ausgeblendet.
  function applySearch() {
    var q = (searchInput.value || "").trim().toLowerCase();
    // Werkzeug-Links filtern (Startseite bleibt immer sichtbar).
    var links = drawerBody.querySelectorAll(".dsnav-link:not(.dsnav-home)");
    for (var j = 0; j < links.length; j++) {
      var hay = (links[j].textContent + " " + (links[j].dataset.such || "")).toLowerCase();
      var hit = !q || hay.indexOf(q) !== -1;
      links[j].style.display = hit ? "" : "none";
    }
    // Bereiche (intern) ohne Treffer ausblenden, Treffer aufklappen.
    var groups = drawerBody.querySelectorAll(".dsnav-group");
    for (var i = 0; i < groups.length; i++) {
      var gl = groups[i].querySelectorAll(".dsnav-link"), any = false;
      for (var k = 0; k < gl.length; k++) { if (gl[k].style.display !== "none") any = true; }
      groups[i].style.display = any ? "" : "none";
      if (q) groups[i].open = true;
    }
  }
  searchInput.addEventListener("input", applySearch);

  // Fokusführung nach ARIA-Dialog-Pattern (WCAG 2.4.3): beim Öffnen den Fokus in
  // den Dialog (erstes Ziel = Schliessen-Knopf, kein Auto-Fokus ins Suchfeld),
  // Tab zirkuliert nur im Dialog, beim Schliessen zurück auf den Auslöser (Burger).
  var lastFocus = null;
  function focusables(r) {
    var all = r.querySelectorAll('a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])');
    return Array.prototype.filter.call(all, function (el) { return el.offsetParent !== null; });
  }
  function openDrawer() {
    lastFocus = document.activeElement;
    backdrop.classList.add("open"); drawer.classList.add("open");
    btnAll.setAttribute("aria-expanded", "true"); drawer.setAttribute("aria-modal", "true");
    var f = focusables(drawer); if (f.length) f[0].focus();
  }
  function closeDrawer() {
    backdrop.classList.remove("open"); drawer.classList.remove("open");
    btnAll.setAttribute("aria-expanded", "false"); drawer.removeAttribute("aria-modal");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  btnAll.addEventListener("click", function () { drawer.classList.contains("open") ? closeDrawer() : openDrawer(); });
  backdrop.addEventListener("click", closeDrawer);
  drawer.querySelector(".close").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && drawer.classList.contains("open")) closeDrawer(); });
  drawer.addEventListener("keydown", function (e) {
    if (e.key !== "Tab") return;
    var f = focusables(drawer); if (!f.length) return;
    var a = f[0], z = f[f.length - 1];
    if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
    else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
  });

  // Unsichtbarer Intern-Schalter
  function toggleIntern() {
    var now = !isIntern(); setIntern(now);
    renderDrawer();
    emitIntern(now);
    flash(now ? "Intern-Ansicht: an" : "Intern-Ansicht: aus");
    if (now) openDrawer();
  }
  var buf = "";
  document.addEventListener("keydown", function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || (e.key && e.key.length !== 1)) { return; }
    buf = (buf + e.key.toLowerCase()).slice(-6);
    if (buf === "intern") { buf = ""; toggleIntern(); }
  });
  var bar = header.querySelector(".bar"), taps = [];
  bar.addEventListener("click", function (e) {
    if (e.target.closest("a,button")) return;
    var now = e.timeStamp; taps.push(now);
    taps = taps.filter(function (t) { return now - t < 800; });
    if (taps.length >= 3) { taps = []; toggleIntern(); }
  });

  // --- Schublade: eine vertikale Liste mit aufklappbaren Bereichen -----------
  var ALL = [];
  function bySlug(slug) { return ALL.filter(function (t) { return t.slug === slug; })[0]; }

  // Kategorie der aktiven Seite – so öffnet sich ihre Welt (und Unterwelt).
  function currentCat() {
    for (var i = 0; i < ALL.length; i++) { if (isActiveTool(ALL[i])) return ALL[i].cat; }
    return null;
  }

  function linkEl(t) {
    var active = isActiveTool(t);
    var a = el("a", "dsnav-link" + (active ? " is-active" : ""));
    a.href = resolveHref(t.href);
    if (isExternal(t.href)) { a.target = "_blank"; a.rel = "noopener"; }
    if (active) a.setAttribute("aria-current", "page");
    // Suchbegriffe (Synonyme) fürs Filtern – „Farben" findet so auch das Design-System.
    if (t.such) a.dataset.such = t.such;
    a.innerHTML = '<span class="tt">' + t.title + '</span>';
    // Status-Marker, nur in der Intern-Schublade: Live bleibt unmarkiert (G03 –
    // der Normalfall trägt kein Zeichen), alles andere sagt leise, was es ist.
    if (isIntern() && t.status && t.status !== "live") {
      var wort = { beta: "Beta", entwurf: "Entwurf", intern: "intern", geparkt: "geparkt" }[t.status] || t.status;
      a.insertAdjacentHTML("beforeend", '<span class="st">' + wort + '</span>');
    }
    return a;
  }

  // Eine Welt als aufklappbarer Bereich. Unterwelten verschachteln sich als eigene
  // Bereiche darunter (Labor → Ligaturen, Schriftpflege, Geparktes, Überreste).
  // Leere Welten (kein Werkzeug, keine gefüllte Unterwelt) entfallen. curCat =
  // Kategorie der aktiven Seite: ihre Welt und Unterwelt stehen offen.
  function worldGroupEl(w, curCat) {
    var tools = ALL.filter(function (t) {
      return (w.cats || []).indexOf(t.cat) !== -1;
    });
    // Auch intern in Sortierer-Reihenfolge (reihenfolge.schublade); Unbekannte ans Ende.
    tools.sort(function (a, b) { return flatRank(a) - flatRank(b); });
    var subs = (w.sub || []).map(function (s) { return worldGroupEl(s, curCat); })
                            .filter(function (n) { return n; });
    if (!tools.length && !subs.length) return null;
    var g = el("details", "dsnav-group");
    g.setAttribute("data-world", w.id);
    g.open = catsOf(w).indexOf(curCat) !== -1;
    // Das Menü koordiniert, es erklärt nicht: nur Titel, kein Beiwerk-Text.
    g.appendChild(el("summary", null,
      '<span class="ttl">' + w.label + '</span><span class="arr">›</span>'));
    tools.forEach(function (t) { g.appendChild(linkEl(t)); });
    subs.forEach(function (n) { g.appendChild(n); });
    return g;
  }

  // Öffentliche Reihenfolge (flach) – wie die Startseite. Vom Sortierer gepflegt
  // (tools.json → reihenfolge.schublade); fehlt sie, gilt diese eingebaute
  // Vorgabe. Unbekannte ans Ende.
  var DEFAULT_FLAT_ORDER = ["logo-generator", "signatur", "visitenkarten", "schriften", "icons",
    "uebersetzungen", "sektionsfarben", "typografie", "karten", "powerpoint",
    "editor", "wallpaper", "design-system"];
  var FLAT_ORDER = DEFAULT_FLAT_ORDER;
  // Vom Sortierer ausgeblendete Schubladen-Einträge (tools.json → reihenfolge.aus.schublade):
  // weg aus dem ÖFFENTLICHEN Menü, in der Intern-Ansicht bleiben sie sichtbar.
  var AUS_SCHUBLADE = [];
  var PUBLIC_CATS = WORLDS.reduce(function (a, w) { return a.concat(w.cats); }, []);
  var flatRank = function (t) { var k = FLAT_ORDER.indexOf(t.slug); return k < 0 ? 999 : k; };

  function renderDrawer() {
    var intern = isIntern();
    drawerBody.innerHTML = "";
    drawerTitle.textContent = intern ? "Alles · intern" : "Navigation";
    idot.hidden = !intern;

    // Startseite immer ganz oben (nicht von der Suche gefiltert).
    var home = el("a", "dsnav-link dsnav-home" + (ACTIVE === "start" ? " is-active" : ""));
    home.href = HOME; home.innerHTML = '<span class="tt">Startseite</span>';
    drawerBody.appendChild(home);

    if (!intern) {
      // FLACH: eine priorisierte Liste aller öffentlichen Werkzeuge, keine Bereiche.
      // Vom Sortierer Ausgeblendete bleiben hier draussen (Intern-Ansicht zeigt sie).
      var pub = ALL.filter(function (t) {
        return PUBLIC_CATS.indexOf(t.cat) !== -1 && (t.status === "live" || t.status === "beta") &&
               AUS_SCHUBLADE.indexOf(t.slug) === -1;
      });
      pub.sort(function (a, b) { return flatRank(a) - flatRank(b); });
      pub.forEach(function (t) { drawerBody.appendChild(linkEl(t)); });
    } else {
      // intern: nach Backstage-Welten gruppiert; Unterwelten verschachteln sich
      // (Labor). Kistenpflege bündelt Stats · Sortierer · Post.
      var curCat = currentCat();
      WORLDS.concat(INTERN_EXTRA).forEach(function (w) {
        var node = worldGroupEl(w, curCat);
        if (node) drawerBody.appendChild(node);
      });
    }
    applySearch();
  }

  // --- Manifest laden --------------------------------------------------------
  fetch(TOOLS).then(function (r) { return r.json(); }).then(function (m) {
    ALL = m.tools || [];
    // Reihenfolge der öffentlichen Schublade: vom Sortierer gepflegt (eine Quelle),
    // sonst die eingebaute Vorgabe.
    if (m.reihenfolge && m.reihenfolge.schublade && m.reihenfolge.schublade.length) {
      FLAT_ORDER = m.reihenfolge.schublade;
    }
    if (m.reihenfolge && m.reihenfolge.aus && Array.isArray(m.reihenfolge.aus.schublade)) {
      AUS_SCHUBLADE = m.reihenfolge.aus.schublade;
    }
    // Sicherheitsnetz: Manifest-Kategorien ohne Welt werden automatisch eigene
    // Backstage-Welten (Titel/Intro aus tools.json) — eine neue Kategorie im
    // Manifest verschwindet damit nie mehr stillschweigend aus dem Menü.
    var known = WORLDS.concat(INTERN_EXTRA).reduce(function (a, w) { return a.concat(catsOf(w)); }, []);
    (m.categories || []).forEach(function (c) {
      if (c && c.id && known.indexOf(c.id) === -1) {
        INTERN_EXTRA.push({ id: c.id, label: c.title || c.id, intro: c.intro || "", cats: [c.id] });
      }
    });
    PRIMARY.forEach(function (p) {
      var t = bySlug(p.slug);
      var a = el("a", null, p.label);
      a.href = t ? resolveHref(t.href) : HOME;
      worldsNav.appendChild(a);
    });
    // Beta-Kennzeichen in der Kopfzeile: folgt dem Status im Manifest —
    // Seiten mit status "beta" tragen die Marke neben dem Lockup, ohne
    // dass die Seite selbst etwas setzen muss (eine Wahrheit: tools.json).
    var active = ACTIVE && bySlug(ACTIVE);
    if (active && active.status === "beta") {
      var chip = el("span", "badge beta-chip", "Beta");
      header.querySelector(".brand").insertAdjacentElement("afterend", chip);
    }
    renderDrawer();
  }).catch(function () {
    drawerBody.innerHTML = '<p style="padding:22px;color:var(--muted)">Werkzeugliste konnte nicht geladen werden.</p>';
  });
})();
