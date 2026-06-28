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
  function updateThemeBtn() {
    if (!themeBtn) return;
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    themeBtn.querySelector(".ic").textContent = dark ? "☀" : "☾";  // ☀ U+2600 / ☾ U+263E
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

  // Die vier meistgenutzten – nur als Desktop-Schnellzugriff in der Kopfzeile.
  var PRIMARY = [
    { label: "Logos",         slug: "logo-generator" },
    { label: "Schriften",     slug: "schriften" },
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
      intro: "Farben, Logos, Design-System – nachschlagen und holen.", cats: ["system"] }
  ];
  // Nur intern zusätzlich – die Backstage-Welten (A/B/C-Qualifizierung).
  var INTERN_EXTRA = [
    { id: "vorbereitung", label: "In Vorbereitung", intro: "In Arbeit – noch nicht freigegeben.", cats: ["vorbereitung"] },
    { id: "ligaturen", label: "Ligaturen", intro: "Die Kiste nur für die Ligaturen.", cats: ["ligaturen"] },
    { id: "schriftpflege", label: "Schriftpflege", intro: "Grotesk, Gewichte und Mischsatz prüfen.", cats: ["schriftpflege"] },
    { id: "statistik", label: "Statistik", intro: "Nutzungszahlen aller Werkzeuge.", cats: ["statistik"] },
    { id: "schau", label: "Schau & Mockups", intro: "Präsentations-Mockups und Studien.", cats: ["schau"] },
    { id: "geparkt", label: "Geparktes", intro: "Konzepte, die später kommen.", cats: ["geparkt"] }
  ];
  var PUBLIC_IDS = WORLDS.map(function (w) { return w.id; });

  function isIntern() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function setIntern(v) { try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {} }

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
  var header = el("header", "dsnav");
  header.innerHTML =
    '<div class="bar">' +
      '<a class="brand" href="' + HOME + '" aria-label="Goetheanum Werkzeuge – zur Übersicht">' +
        '<img class="lockup" src="' + ROOT + 'assets/logos/goetheanum-werkzeuge.svg" alt="Goetheanum Werkzeuge">' +
      '</a>' +
      '<nav class="worlds"></nav>' +
      '<button class="theme" type="button" aria-label="Dunkel schalten"><span class="ic">☾</span></button>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false" aria-label="Menü">' +
        '<span class="ic">☰</span><span class="idot" hidden></span></button>' +
    '</div>';
  document.body.insertBefore(header, document.body.firstChild);

  var backdrop = el("div", "dsnav-backdrop");
  var drawer = el("aside", "dsnav-drawer");
  drawer.setAttribute("role", "dialog");
  drawer.setAttribute("aria-label", "Navigation");
  drawer.innerHTML =
    '<div class="dhead"><span class="t">Navigation</span>' +
      '<button class="close" type="button" aria-label="Schliessen">×</button></div>' +
    '<div class="body"></div>' +
    '<div class="foot">Goetheanum Hausgrafik · <a href="' + ROOT + 'design-system/">Design-System</a></div>';
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

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

  function groupEl(w, tools, open) {
    var g = el("details", "dsnav-group");
    g.setAttribute("data-world", w.id);
    g.open = open;
    // Das Menü koordiniert, es erklärt nicht: nur Titel, kein Beiwerk-Text.
    g.appendChild(el("summary", null,
      '<span class="ttl">' + w.label + '</span><span class="arr">›</span>'));
    tools.forEach(function (t) {
      var active = isActiveTool(t);
      var a = el("a", "dsnav-link" + (active ? " is-active" : ""));
      a.href = resolveHref(t.href);
      if (isExternal(t.href)) { a.target = "_blank"; a.rel = "noopener"; }
      if (active) a.setAttribute("aria-current", "page");
      a.innerHTML = '<span class="tt">' + t.title + '</span>';
      g.appendChild(a);
    });
    return g;
  }

  function renderDrawer() {
    var intern = isIntern();
    drawerBody.innerHTML = "";
    drawerTitle.textContent = intern ? "Alles · intern" : "Navigation";
    idot.hidden = !intern;
    var cur = currentWorldId();
    var groups = intern ? WORLDS.concat(INTERN_EXTRA) : WORLDS;
    groups.forEach(function (w) {
      var tools = ALL.filter(function (t) { return w.cats.indexOf(t.cat) !== -1; });
      if (!intern) tools = tools.filter(function (t) { return t.status === "live" || t.status === "beta"; });
      if (!tools.length) return;
      // Offen: der Bereich der aktuellen Seite, sonst die öffentlichen Welten;
      // Backstage-Welten bleiben eingeklappt (kurze, scannbare Liste).
      var open = (w.id === cur) || (!intern && PUBLIC_IDS.indexOf(w.id) !== -1);
      if (intern) open = (w.id === cur);
      drawerBody.appendChild(groupEl(w, tools, open));
    });
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
