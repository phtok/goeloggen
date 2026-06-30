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
  function updateThemeBtn() {
    if (!themeBtn) return;
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    themeBtn.querySelector(".ic").innerHTML = dark ? SUN_SVG : MOON_SVG;
    themeBtn.setAttribute("aria-label", dark ? "Hell schalten" : "Dunkel schalten");
    themeBtn.setAttribute("aria-pressed", String(dark));
  }
  function setTheme(t) {
    try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
    document.documentElement.setAttribute("data-theme", t);
    updateThemeBtn();
  }
  // Sofort anwenden – vor dem Zeichnen, gegen Aufblitzen.
  document.documentElement.setAttribute("data-theme", getTheme());

  // --- Anonyme Nutzungszählung (mitwachsend) ---------------------------------
  // Zählt je Werkzeug (data-active) den Seitenaufruf und Download-Klicks – ohne
  // Cookies, ohne IP/Personendaten, nur anonyme Summen über goeloggen_bump().
  // Jedes Werkzeug mit nav.js zählt automatisch mit; neue brauchen nichts extra.
  // Werkzeuge mit JS-Download rufen window.goeStat('download', name) selbst auf.
  var STAT_SB = "https://dagcsnfrlbpxcmdimnrw.supabase.co";
  var STAT_KEY = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";
  function goeStat(event, label) {
    if (!ACTIVE || !event) return;
    try {
      fetch(STAT_SB + "/rest/v1/rpc/goeloggen_bump", {
        method: "POST", keepalive: true,
        headers: { "Content-Type": "application/json", "apikey": STAT_KEY, "Authorization": "Bearer " + STAT_KEY },
        body: JSON.stringify({ p_tool: ACTIVE, p_event: event, p_label: (label || "").slice(0, 160) })
      }).catch(function () {});
    } catch (e) {}
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
  // Nur intern zusätzlich – die Backstage-Welten (A/B/C-Qualifizierung).
  var INTERN_EXTRA = [
    { id: "vorbereitung", label: "In Vorbereitung", intro: "In Arbeit – noch nicht freigegeben.", cats: ["vorbereitung"] },
    { id: "ligaturen", label: "Ligaturen", intro: "Die Kiste nur für die Ligaturen.", cats: ["ligaturen"] },
    { id: "schriftpflege", label: "Schriftpflege", intro: "Grotesk, Gewichte und Mischsatz prüfen.", cats: ["schriftpflege"] },
    { id: "statistik", label: "Statistik", intro: "Nutzungszahlen aller Werkzeuge.", cats: ["statistik"] },
    { id: "schau", label: "Schau & Mockups", intro: "Präsentations-Mockups und Studien.", cats: ["schau"] },
    { id: "geparkt", label: "Geparktes", intro: "Konzepte, die später kommen.", cats: ["geparkt"] },
    { id: "archiv", label: "Archiv", intro: "Frühere Stände, eingefroren.", cats: ["archiv"] }
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
  function worldFor(catId) {
    var all = WORLDS.concat(INTERN_EXTRA);
    for (var i = 0; i < all.length; i++) { if (all[i].cats.indexOf(catId) !== -1) return all[i]; }
    return null;
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
      '<button class="theme" type="button" aria-label="Dunkel schalten"><span class="ic"></span></button>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false" aria-label="Menü">' +
        '<span class="ic">☰</span><span class="idot" hidden></span></button>' +
    '</div>';
  document.body.insertBefore(header, document.body.firstChild);

  // Optionale Seiten-Sprungleiste: data-onpage="Label:#anker|…". Sie sitzt UNTER
  // dem Hero/der Lede (nicht über dem Titel) und klebt beim Scrollen unter der
  // Kopfzeile. Auf jeder Breite sichtbar (auch mobil), horizontal scrollbar.
  var ONPAGE = (s && s.dataset.onpage) || "";
  if (ONPAGE) {
    var sub = el("nav", "dsnav-onpage");
    sub.setAttribute("aria-label", "Auf dieser Seite");
    sub.innerHTML = '<div class="row">' + ONPAGE.split("|").map(function (pair) {
      var ci = pair.indexOf(":");
      var label = ci > 0 ? pair.slice(0, ci) : pair;
      var anchor = ci > 0 ? pair.slice(ci + 1) : "#";
      return '<a href="' + anchor + '">' + label + '</a>';
    }).join("") + '</div>';
    // Unter den Hero/die Lede hängen; wenn es keinen gibt, direkt unter die Kopfzeile.
    // nav.js läuft oft VOR <main> – darum die Platzierung bis DOM-ready aufschieben.
    var placeOnpage = function () {
      var heroEl = document.querySelector("main .hero, .hero, main .lede");
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
    '<div class="dsearch"><input type="search" class="dsnav-q" placeholder="Werkzeug suchen …" aria-label="Werkzeug suchen" autocomplete="off"></div>' +
    '<div class="body"></div>' +
    '<div class="foot"><a href="mailto:philipp.tok@goetheanum.ch?subject=Feedback%20Goetheanum%20Werkzeuge">Feedback geben</a> · <a href="' + ROOT + 'design-system/">Design-System</a></div>';
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

  // Globaler Beta-Einblender (unten, dezent, wegklickbar – merkt sich „gesehen").
  var BETA_KEY = "goeBetaSeen";
  var betaSeen = false; try { betaSeen = localStorage.getItem(BETA_KEY) === "1"; } catch (e) {}
  if (!betaSeen) {
    var beta = el("div", "dsnav-beta");
    beta.innerHTML =
      '<span class="t"><b>Beta</b> – die Werkzeuge wachsen noch.</span>' +
      '<a class="fb" href="mailto:philipp.tok@goetheanum.ch?subject=Feedback%20Goetheanum%20Werkzeuge">Feedback geben</a>' +
      '<button class="x" type="button" aria-label="Hinweis schliessen">×</button>';
    document.body.appendChild(beta);
    beta.querySelector(".x").addEventListener("click", function () {
      beta.remove(); try { localStorage.setItem(BETA_KEY, "1"); } catch (e) {}
    });
  }

  var toast = el("div", "dsnav-toast"); document.body.appendChild(toast);
  function flash(msg) { toast.textContent = msg; toast.classList.add("show"); setTimeout(function () { toast.classList.remove("show"); }, 1400); }

  var btnAll = header.querySelector(".all");
  var themeBtn = header.querySelector(".theme");
  themeBtn.addEventListener("click", function () {
    setTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });
  updateThemeBtn();
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
      var hit = !q || links[j].textContent.toLowerCase().indexOf(q) !== -1;
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

  function openDrawer() { backdrop.classList.add("open"); drawer.classList.add("open"); btnAll.setAttribute("aria-expanded", "true"); }
  function closeDrawer() { backdrop.classList.remove("open"); drawer.classList.remove("open"); btnAll.setAttribute("aria-expanded", "false"); }
  btnAll.addEventListener("click", function () { drawer.classList.contains("open") ? closeDrawer() : openDrawer(); });
  backdrop.addEventListener("click", closeDrawer);
  drawer.querySelector(".close").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

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

  function currentWorldId() {
    for (var i = 0; i < ALL.length; i++) {
      if (isActiveTool(ALL[i])) { var w = worldFor(ALL[i].cat); return w ? w.id : null; }
    }
    return null;
  }

  function linkEl(t) {
    var active = isActiveTool(t);
    var a = el("a", "dsnav-link" + (active ? " is-active" : ""));
    a.href = resolveHref(t.href);
    if (isExternal(t.href)) { a.target = "_blank"; a.rel = "noopener"; }
    if (active) a.setAttribute("aria-current", "page");
    a.innerHTML = '<span class="tt">' + t.title + '</span>';
    return a;
  }

  function groupEl(w, tools, open) {
    var g = el("details", "dsnav-group");
    g.setAttribute("data-world", w.id);
    g.open = open;
    // Das Menü koordiniert, es erklärt nicht: nur Titel, kein Beiwerk-Text.
    g.appendChild(el("summary", null,
      '<span class="ttl">' + w.label + '</span><span class="arr">›</span>'));
    tools.forEach(function (t) { g.appendChild(linkEl(t)); });
    return g;
  }

  // Öffentliche Reihenfolge (flach) – wie die Startseite. Unbekannte ans Ende.
  var FLAT_ORDER = ["logo-generator", "signatur", "visitenkarten", "icons", "schriften",
    "sektionsfarben", "uebersetzungen", "wallpaper", "powerpoint", "typografie", "design-system"];
  var PUBLIC_CATS = WORLDS.reduce(function (a, w) { return a.concat(w.cats); }, []);

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
      var pub = ALL.filter(function (t) {
        return PUBLIC_CATS.indexOf(t.cat) !== -1 && (t.status === "live" || t.status === "beta");
      });
      var rank = function (t) { var k = FLAT_ORDER.indexOf(t.slug); return k < 0 ? 999 : k; };
      pub.sort(function (a, b) { return rank(a) - rank(b); });
      pub.forEach(function (t) { drawerBody.appendChild(linkEl(t)); });
    } else {
      // intern: nach Backstage-Welten gruppiert (kurze, scannbare Bereiche).
      var cur = currentWorldId();
      WORLDS.concat(INTERN_EXTRA).forEach(function (w) {
        var tools = ALL.filter(function (t) { return w.cats.indexOf(t.cat) !== -1; });
        if (!tools.length) return;
        drawerBody.appendChild(groupEl(w, tools, w.id === cur));
      });
    }
    applySearch();
  }

  // --- Manifest laden --------------------------------------------------------
  fetch(TOOLS).then(function (r) { return r.json(); }).then(function (m) {
    ALL = m.tools || [];
    PRIMARY.forEach(function (p) {
      var t = bySlug(p.slug);
      var a = el("a", null, p.label);
      a.href = t ? resolveHref(t.href) : HOME;
      worldsNav.appendChild(a);
    });
    renderDrawer();
  }).catch(function () {
    drawerBody.innerHTML = '<p style="padding:22px;color:var(--muted)">Werkzeugliste konnte nicht geladen werden.</p>';
  });
})();
