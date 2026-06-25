/* =============================================================================
   Goetheanum CI – ds-nav (Prototyp)
   -----------------------------------------------------------------------------
   Eine globale Navigation für alle Seiten, gerendert aus tools.json. Einbinden:

     <link rel="stylesheet" href="…/design-system/nav.css">
     <script src="…/design-system/nav.js"
             data-root="https://phtok.github.io/goeloggen/"
             data-variant="werkzeug"          (optional: zeigt „← Übersicht")
             data-path="Schrift › Tester"></script>  (optional: Kontext-Pfad)

   Kopfzeile: die vier meistgenutzten Werkzeuge beim Namen, plus „Mehr".
     Logos · Schriften · Mail-Signatur · Visitenkarte · Mehr
   Ein Tipp auf die vier führt direkt zum Ziel. „Mehr" öffnet die Schublade
   mit dem ganzen Sortiment, in drei nutzernahe Welten gegliedert
   (Werkzeuge · Schrift · Elemente). Werkstatt/Geparktes sind intern und NICHT
   im Menü (sie leben im Hub start/). Akkordeon = native <details>.
   ============================================================================= */
(function () {
  var s = document.currentScript;
  var ROOT  = (s && s.dataset.root)  || "https://phtok.github.io/goeloggen/";
  if (ROOT.slice(-1) !== "/") ROOT += "/";
  var TOOLS = (s && s.dataset.tools) || ROOT + "tools.json";
  var HOME  = (s && s.dataset.home)  || ROOT;
  var VARIANT = (s && s.dataset.variant) || "";
  var PATH  = (s && s.dataset.path)  || "";

  // Die vier Direkt-Sprünge der Kopfzeile (für die Breite der Mitarbeitenden).
  // href kommt aus tools.json (per slug) – eine Quelle, keine doppelten Pfade.
  var PRIMARY = [
    { label: "Logos",        slug: "logo-generator" },
    { label: "Schriften",    slug: "schriften" },
    { label: "Mail-Signatur", slug: "signatur" },
    { label: "Visitenkarte", slug: "visitenkarten" }
  ];

  // Die Schublade „Mehr" – das ganze Sortiment in drei nutzernahen Welten.
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
      '<a class="brand" href="' + HOME + '" aria-label="Goetheanum Werkzeuge – zur Übersicht">' +
        '<img class="lockup" src="' + ROOT + 'assets/logos/goetheanum-werkzeuge.svg" alt="Goetheanum Werkzeuge">' +
      '</a>' +
      '<a class="back" href="' + HOME + '">← Übersicht</a>' +
      '<nav class="worlds"></nav>' +
      '<button class="all" type="button" aria-haspopup="dialog" aria-expanded="false">' +
        '<span class="ic">☰</span> Mehr</button>' +
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

  // --- Aus dem Manifest füllen -----------------------------------------------
  fetch(TOOLS).then(function (r) { return r.json(); }).then(function (m) {
    var allTools = m.tools || [];
    function bySlug(slug) { return allTools.filter(function (t) { return t.slug === slug; })[0]; }

    // Kopfzeile: vier Direkt-Sprünge
    PRIMARY.forEach(function (p) {
      var t = bySlug(p.slug);
      var a = el("a", null, p.label);
      a.href = t ? resolveHref(t.href) : HOME;
      worldsNav.appendChild(a);
    });

    // Schublade: drei Welten mit dem ganzen Sortiment
    WORLDS.forEach(function (w) {
      var tools = allTools.filter(function (t) { return w.cats.indexOf(t.cat) !== -1; });
      if (!tools.length) return;
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
