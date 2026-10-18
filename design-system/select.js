/* =============================================================================
   Goetheanum CI – ds-select: gestaltbare Klappliste (Hausschrift auch geöffnet)
   -----------------------------------------------------------------------------
   Wandelt native <select> in eine gestaltete Liste, damit die GEÖFFNETE Auswahl
   in der Hausschrift erscheint (native <option> nutzt sonst die System-Schrift,
   v. a. in Safari/Chrome). Das native <select> bleibt Quelle der Wahrheit:
   change-Events, Formular, Wert. Auf Touch-Geräten bleibt die native Auswahl
   (der OS-Picker ist dort besser). Nach base.css einbinden; verbessert alle
   .field select automatisch und re-beschriftet sich, wenn ein Werkzeug die
   Optionen per JS ändert (MutationObserver).
   ============================================================================= */
(function () {
  if (window.matchMedia && matchMedia("(pointer: coarse)").matches) return; // Touch: native

  function enhance(sel) {
    if (sel.dataset.dsSel) return; sel.dataset.dsSel = "1";
    var wrap = document.createElement("div"); wrap.className = "ds-select";
    sel.parentNode.insertBefore(wrap, sel); wrap.appendChild(sel);
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "ds-select__btn";
    btn.setAttribute("aria-haspopup", "listbox"); btn.setAttribute("aria-expanded", "false");
    var list = document.createElement("ul");
    list.className = "ds-select__list"; list.setAttribute("role", "listbox"); list.hidden = true;
    wrap.appendChild(btn); wrap.appendChild(list);

    function sync() { var o = sel.options[sel.selectedIndex]; btn.textContent = o ? o.textContent : ""; }
    function build() {
      list.innerHTML = "";
      [].forEach.call(sel.options, function (o, i) {
        var li = document.createElement("li");
        li.className = "ds-select__opt"; li.setAttribute("role", "option"); li.tabIndex = -1;
        li.textContent = o.textContent; li.setAttribute("aria-selected", String(i === sel.selectedIndex));
        li.addEventListener("click", function () { choose(i); });
        list.appendChild(li);
      });
    }
    function choose(i) { sel.selectedIndex = i; sync(); close(); btn.focus(); sel.dispatchEvent(new Event("change", { bubbles: true })); }
    function open() {
      build(); list.hidden = false; btn.setAttribute("aria-expanded", "true");
      document.addEventListener("click", outside, true); document.addEventListener("keydown", onkey, true);
      var cur = list.children[sel.selectedIndex] || list.children[0]; if (cur) cur.focus();
    }
    function close() {
      list.hidden = true; btn.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", outside, true); document.removeEventListener("keydown", onkey, true);
    }
    function outside(e) { if (!wrap.contains(e.target)) close(); }
    function onkey(e) {
      if (list.hidden) return;
      var opts = [].slice.call(list.children), idx = opts.indexOf(document.activeElement);
      if (e.key === "Escape") { e.preventDefault(); close(); btn.focus(); }
      else if (e.key === "ArrowDown") { e.preventDefault(); (opts[idx + 1] || opts[0]).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); (opts[idx - 1] || opts[opts.length - 1]).focus(); }
      else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (idx >= 0) choose(idx); }
    }
    btn.addEventListener("click", function () { list.hidden ? open() : close(); });
    btn.addEventListener("keydown", function (e) { if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    sel.addEventListener("change", sync);
    new MutationObserver(sync).observe(sel, { childList: true, subtree: true, attributes: true });
    sync();
  }
  function run() { [].forEach.call(document.querySelectorAll(".field select"), enhance); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
})();
