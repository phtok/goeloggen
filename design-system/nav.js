/* =============================================================================
   Goetheanum CI – ds-nav (Prototyp)
   -----------------------------------------------------------------------------
   Eine globale Navigation für alle Seiten, gerendert aus tools.json. Einbinden:

     <link rel="stylesheet" href="…/design-system/nav.css">
     <script src="…/design-system/nav.js"
             data-root="https://phtok.github.io/goeloggen/"
             data-variant="werkzeug"          (optional: zeigt „← Übersicht")
             data-path="Schrift › Tester"></script>  (optional: Kontext-Pfad)

   Drei nutzernahe Welten – Werkzeuge · Schrift · Elemente – in Kopfzeile UND
   Schublade. Über die technischen tools.json-Kategorien liegt nur eine
   freundliche Sprachschicht (WORLDS). Werkstatt und Geparktes sind intern und
   erscheinen NICHT im breiten Menü (sie leben im Hub start/).
   Akkordeon = native <details>.
   ============================================================================= */
(function () {
  var s = document.currentScript;
  var ROOT  = (s && s.dataset.root)  || "https://phtok.github.io/goeloggen/";
  if (ROOT.slice(-1) !== "/") ROOT += "/";
  var TOOLS = (s && s.dataset.tools) || ROOT + "tools.json";
  var HOME  = (s && s.dataset.home)  || ROOT;
  var VARIANT = (s && s.dataset.variant) || "";
  var PATH  = (s && s.dataset.path)  || "";

  // Die drei Welten in nutzernaher Sprache. cats = welche tools.json-Kategorien
  // hier hineinfallen. Werkstatt/Geparktes fehlen bewusst (intern, nur im Hub).
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

  // --- Grundgerüst (vor dem Laden des Manifests sichtbar) ---------------------
  var header = el("header", "dsnav" + (VARIANT === "werkzeug" ? " is-werkzeug" : "") + (PATH ? " has-path" : ""));
  header.innerHTML =
    '<div class="bar">' +
      '<a class="brand" href="' + HOME + '" aria-label="Zur Übersicht">' +
        '<img class="mk" src="' + ROOT + 'assets/logos/goetheanum-mark-blue.svg" alt="">' +
        '<span class="wm">Goetheanum</span>' +
      '</a>' +
      '<a class="back" href="' + HOME + '">← Übersicht</a>' +
      '<nav class="worlds"></nav>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="ic">☰</span> Alles</button>' +
    '</div>' +
    (PATH ? '<div class="path">' + PATH.replace(/›\s*([^›]+)$/, '› <b>$1</b>') + '</div>' : "");
  document.body.insertBefore(header, document.body.firstChild);

  var backdrop = el("div", "dsnav-backdrop");
  var drawer = el("aside", "dsnav-drawer");
  drawer.setAttribute("role", "dialog");
  drawer.setAttribute("aria-label", "Alle Werkzeuge");
  drawer.innerHTML =
    '<div class="dhead"><span class="t">Alles</span>' +
      '<button class="close" type="button" aria-label="Schliessen">×</button></div>' +
    '<div class="body"></div>' +
    '<div class="foot">Goetheanum Hausgrafik · <a href="' + ROOT + 'design-system/">Design-System</a></div>';
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

  var btnAll = header.querySelector(".all");
  var worldsNav = header.querySelector(".worlds");
  var drawerBody = drawer.querySelector(".body");

  function openDrawer() { backdrop.classList.add("open"); drawer.classList.add("open"); btnAll.setAttribute("aria-expanded", "true"); }
  function closeDrawer() { backdrop.classList.remove("open"); drawer.classList.remove("open"); btnAll.setAttribute("aria-expanded", "false"); }
  btnAll.addEventListener("click", function () { drawer.classList.contains("open") ? closeDrawer() : openDrawer(); });
  backdrop.addEventListener("click", closeDrawer);
  drawer.querySelector(".close").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  // --- Aus dem Manifest füllen, gegliedert in die drei Welten ----------------
  fetch(TOOLS).then(function (r) { return r.json(); }).then(function (m) {
    var allTools = m.tools || [];

    WORLDS.forEach(function (w) {
      var tools = allTools.filter(function (t) { return w.cats.indexOf(t.cat) !== -1; });
      if (!tools.length) return;

      // Primär-Welt in die Kopfzeile
      var btn = el("button", null, w.label);
      btn.type = "button";
      btn.addEventListener("click", function () {
        openDrawer();
        var grp = drawerBody.querySelector('[data-world="' + w.id + '"]');
        if (grp) { grp.open = true; grp.scrollIntoView({ block: "start", behavior: "smooth" }); }
      });
      worldsNav.appendChild(btn);

      // Schubladen-Gruppe (alle drei offen – es sind nur drei)
      var g = el("details", "dsnav-group");
      g.setAttribute("data-world", w.id);
      g.open = true;
      g.appendChild(el("summary", null,
        '<span><span class="ttl">' + w.label + '</span>' +
        '<span class="intro">' + w.intro + '</span></span>' +
        '<span class="arr">›</span>'));
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
      drawerBody.appendChild(g);
    });
  }).catch(function () {
    drawerBody.innerHTML = '<p style="padding:22px;color:var(--muted)">Werkzeugliste konnte nicht geladen werden.</p>';
  });
})();
