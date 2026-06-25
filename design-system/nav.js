/* =============================================================================
   Goetheanum CI – ds-nav (Prototyp)
   -----------------------------------------------------------------------------
   Eine globale Navigation für alle Seiten, gerendert aus tools.json. Einbinden:

     <link rel="stylesheet" href="…/design-system/nav.css">
     <script src="…/design-system/nav.js"
             data-root="https://phtok.github.io/goeloggen/"
             data-variant="werkzeug"          (optional: zeigt „← Übersicht")
             data-path="Schrift › Tester"></script>  (optional: Kontext-Pfad)

   Kopfzeile: Lockup · Logos · Schriften · Mail-Signatur · Visitenkarte · ☰
   Der Burger (☰) öffnet die Schublade. Ganz oben darin: die vier meistgenutzten
   Werkzeuge als prominente Kacheln (auch auf dem Handy gut sichtbar).

   FOKUS: öffentlich nur fertige Werkzeuge (Status „live") – nicht übervoll.
   INTERN (Pflege): unsichtbarer Schalter blendet ALLES ein (alle Status +
   Werkstatt + Geparktes). Auslöser: das Wort „intern" tippen, oder einmalig
   ?intern an die URL. Gemerkt im localStorage; ausschalten: erneut „intern".
   ============================================================================= */
(function () {
  var s = document.currentScript;
  var ROOT  = (s && s.dataset.root)  || "https://phtok.github.io/goeloggen/";
  if (ROOT.slice(-1) !== "/") ROOT += "/";
  var TOOLS = (s && s.dataset.tools) || ROOT + "tools.json";
  var HOME  = (s && s.dataset.home)  || ROOT;
  var VARIANT = (s && s.dataset.variant) || "";
  var KEY = "goeNavIntern";

  // Die vier meistgenutzten Werkzeuge – Kopfzeile UND prominent in der Schublade.
  var PRIMARY = [
    { label: "Logos",        slug: "logo-generator" },
    { label: "Schriften",    slug: "schriften" },
    { label: "Mail-Signatur", slug: "signatur" },
    { label: "Visitenkarte", slug: "visitenkarten" }
  ];
  var PRIMARY_SLUGS = PRIMARY.map(function (p) { return p.slug; });

  // Die drei öffentlichen Welten (öffentlich nur Status „live").
  var WORLDS = [
    { id: "werkzeuge", label: "Werkzeuge",
      intro: "Eintragen, fertiges Ergebnis übernehmen – für den täglichen Gebrauch.",
      cats: ["generatoren"] },
    { id: "schrift", label: "Schrift",
      intro: "Die Hausschrift und die Regeln dazu – ansehen, herunterladen, einbinden.",
      cats: ["schrift"] },
    { id: "elemente", label: "Elemente",
      intro: "Farben, Logos und das Design-System – zum Nachschlagen und Holen.",
      cats: ["system"] }
  ];
  // Nur intern zusätzlich (Pflege).
  var INTERN_EXTRA = [
    { id: "werkstatt", label: "Werkstatt",
      intro: "Werkschau und Prüfwerkzeuge der Schriftpflege – intern.", cats: ["werkstatt"] },
    { id: "geparkt", label: "Geparktes",
      intro: "Durchdachte Konzepte, die später kommen – intern.", cats: ["geparkt"] }
  ];

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

  // ?intern in der URL auswerten (einmalig aktivieren, dann säubern)
  (function () {
    var m = /[?&]intern(?:=([^&]*))?/.exec(location.search);
    if (m) {
      setIntern(m[1] !== "0" && m[1] !== "false");
      try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) {}
    }
  })();

  // --- Kopfzeile -------------------------------------------------------------
  var header = el("header", "dsnav" + (VARIANT === "werkzeug" ? " is-werkzeug" : ""));
  header.innerHTML =
    '<div class="bar">' +
      '<a class="brand" href="' + HOME + '" aria-label="Goetheanum Werkzeuge – zur Übersicht">' +
        '<img class="lockup" src="' + ROOT + 'assets/logos/goetheanum-werkzeuge.svg" alt="Goetheanum Werkzeuge">' +
      '</a>' +
      '<a class="back" href="' + HOME + '">← Übersicht</a>' +
      '<nav class="worlds"></nav>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false" aria-label="Menü">' +
        '<span class="ic">☰</span><span class="idot" hidden></span></button>' +
    '</div>';
  document.body.insertBefore(header, document.body.firstChild);

  var backdrop = el("div", "dsnav-backdrop");
  var drawer = el("aside", "dsnav-drawer");
  drawer.setAttribute("role", "dialog");
  drawer.setAttribute("aria-label", "Werkzeuge");
  drawer.innerHTML =
    '<div class="dhead"><span class="t">Werkzeuge</span>' +
      '<button class="close" type="button" aria-label="Schliessen">×</button></div>' +
    '<div class="body"></div>' +
    '<div class="foot">Goetheanum Hausgrafik · <a href="' + ROOT + 'design-system/">Design-System</a></div>';
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

  var toast = el("div", "dsnav-toast"); document.body.appendChild(toast);
  function flash(msg) { toast.textContent = msg; toast.classList.add("show"); setTimeout(function () { toast.classList.remove("show"); }, 1400); }

  var btnAll = header.querySelector(".all");
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

  // Unsichtbarer Schalter (zwei Wege, gleicher Effekt)
  function toggleIntern() {
    var now = !isIntern(); setIntern(now);
    renderDrawer();
    flash(now ? "Intern-Ansicht: an" : "Intern-Ansicht: aus");
    if (now) openDrawer();
  }

  // (1) Desktop: das Wort „intern" tippen
  var buf = "";
  document.addEventListener("keydown", function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || (e.key && e.key.length !== 1)) { return; }
    buf = (buf + e.key.toLowerCase()).slice(-6);
    if (buf === "intern") { buf = ""; toggleIntern(); }
  });

  // (2) Handy & Desktop: drei schnelle Tipps in die leere Mitte der Kopfzeile
  // (alles, was kein Link/Knopf ist – also der Bereich zwischen Lockup und Navi).
  var bar = header.querySelector(".bar");
  var taps = [];
  bar.addEventListener("click", function (e) {
    if (e.target.closest("a,button")) return;        // echte Bedienelemente nicht zählen
    var now = e.timeStamp;
    taps.push(now);
    taps = taps.filter(function (t) { return now - t < 800; });
    if (taps.length >= 3) { taps = []; toggleIntern(); }
  });

  // --- Schublade rendern -----------------------------------------------------
  var ALL = [];
  function bySlug(slug) { return ALL.filter(function (t) { return t.slug === slug; })[0]; }

  function quickBlock() {
    var q = el("div", "dsnav-quick");
    PRIMARY.forEach(function (p) {
      var t = bySlug(p.slug);
      var a = el("a", null,
        '<span class="qt">' + p.label + '</span>' +
        (t && t.desc ? '<span class="qd">' + t.desc + '</span>' : ""));
      a.href = t ? resolveHref(t.href) : HOME;
      q.appendChild(a);
    });
    return q;
  }
  function groupEl(w, tools) {
    var g = el("details", "dsnav-group");
    g.setAttribute("data-world", w.id);
    g.open = true;
    g.appendChild(el("summary", null,
      '<span><span class="ttl">' + w.label + '</span>' +
      '<span class="intro">' + w.intro + '</span></span><span class="arr">›</span>'));
    tools.forEach(function (t) {
      var a = el("a", "dsnav-link");
      a.href = resolveHref(t.href);
      if (isExternal(t.href)) { a.target = "_blank"; a.rel = "noopener"; }
      a.innerHTML =
        '<span class="st ' + (t.status || "") + '" title="' + (t.status || "") + '"></span>' +
        '<span class="txt"><span class="tt">' + t.title + '</span>' +
        (t.desc ? '<span class="dd">' + t.desc + '</span>' : "") + '</span>';
      g.appendChild(a);
    });
    return g;
  }
  function renderDrawer() {
    var intern = isIntern();
    drawerBody.innerHTML = "";
    drawerTitle.textContent = intern ? "Alles · intern" : "Werkzeuge";
    idot.hidden = !intern;

    // Ganz oben: die vier prominent
    drawerBody.appendChild(quickBlock());

    // Darunter der Rest (ohne die vier). Öffentlich nur „live"; intern alles + Extra.
    var groups = intern ? WORLDS.concat(INTERN_EXTRA) : WORLDS;
    groups.forEach(function (w) {
      var tools = ALL.filter(function (t) {
        return w.cats.indexOf(t.cat) !== -1 && PRIMARY_SLUGS.indexOf(t.slug) === -1;
      });
      if (!intern) tools = tools.filter(function (t) { return t.status === "live"; });
      if (tools.length) drawerBody.appendChild(groupEl(w, tools));
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
