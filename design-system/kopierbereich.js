/* =============================================================================
   Goetheanum CI – Kopierbereich (Schau-Skript)
   -----------------------------------------------------------------------------
   Code zum Kopieren auf Schauseiten, geladen aus den Quelldateien – so steht
   auf der Seite immer der Stand von main, nie eine veraltete Abschrift.
   Markup:
     <div class="kopieren"><div class="seg" data-kopier-wahl>
        <button data-code="id-des-pre" aria-pressed="true">CSS</button> …</div>
       <button class="btn primary" data-kopier-knopf>Kopieren</button>
       <span class="said" aria-live="polite" data-kopier-meldung></span></div>
     <pre class="code" id="…" data-quelle="design-system/x.css">Fallback</pre>
     <pre … data-quelle="seite.html" data-ausschnitt="name"> – nur der Teil
        zwischen <!-- name:anfang --> und <!-- name:ende -->, Einzug bereinigt.
     <pre … data-token-auszug="design-system/a.css design-system/b.css"
        data-anhang="id-eines-script-type-text-plain"> – die Tokens, die diese
        Dateien brauchen, mit ihren Werten aus tokens.css (hell, weniger
        Bewegung, dunkel), für Seiten ohne tokens.css.
   Pfade relativ zur Seite; data-wurzel am <script> setzt einen Präfix.
   ============================================================================= */
(function(){
  "use strict";
  var skript = document.currentScript;
  var wurzel = (skript && skript.dataset.wurzel) || "";
  var cache = {};
  function laden(pfad){
    if (!cache[pfad]) cache[pfad] = fetch(wurzel + pfad, {cache:"no-cache"}).then(function(r){
      if (!r.ok) throw new Error(r.status); return r.text();
    });
    return cache[pfad];
  }

  function ausschnitt(text, name){
    var a = text.indexOf("<!-- " + name + ":anfang -->"), e = text.indexOf("<!-- " + name + ":ende -->");
    if (a < 0 || e < 0) return text;
    var zeilen = text.slice(text.indexOf("\n", a) + 1, e).replace(/\s+$/, "").split("\n");
    var einzug = Math.min.apply(null, zeilen.filter(function(z){ return z.trim(); }).map(function(z){ return z.match(/^ */)[0].length; }));
    return zeilen.map(function(z){ return z.slice(einzug); }).join("\n");
  }

  /* tokens.css in Blöcke zerlegen: Selektor → Rumpf, eine Ebene tief in @media. */
  function bloecke(css){
    var out = [], tiefe = 0, start = 0, sel = "";
    for (var i = 0; i < css.length; i++) {
      var c = css[i];
      if (c === "{") { if (tiefe === 0) { sel = css.slice(start, i).trim(); start = i + 1; } tiefe++; }
      else if (c === "}") { tiefe--; if (tiefe === 0) { out.push({sel:sel, rumpf:css.slice(start, i)}); start = i + 1; } }
    }
    return out;
  }
  function decl(rumpf, ziel){
    rumpf.split(";").forEach(function(d){
      var m = d.match(/^\s*(--[\w-]+)\s*:\s*([\s\S]+?)\s*$/);
      if (m) ziel[m[1]] = m[2].replace(/\s+/g, " ");
    });
    return ziel;
  }
  function tokenAuszug(tokens, module, namen){
    tokens = tokens.replace(/\/\*[\s\S]*?\*\//g, "");
    var hell = {}, dunkel = {}, ruhig = {};
    bloecke(tokens).forEach(function(b){
      if (b.sel === ":root") decl(b.rumpf, hell);
      else if (b.sel === ':root[data-theme="dark"]') decl(b.rumpf, dunkel);
      else if (/prefers-reduced-motion/.test(b.sel)) bloecke(b.rumpf).forEach(function(i){ decl(i.rumpf, ruhig); });
    });
    var eigen = {}, gesucht = {};
    module.forEach(function(css){
      css = css.replace(/\/\*[\s\S]*?\*\//g, "");
      (css.match(/(--[\w-]+)\s*:/g) || []).forEach(function(m){ eigen[m.replace(/\s*:$/, "")] = 1; });
      (css.match(/@property\s+(--[\w-]+)/g) || []).forEach(function(m){ eigen[m.split(/\s+/)[1]] = 1; });
      (css.match(/var\(\s*--[\w-]+/g) || []).forEach(function(m){ gesucht[m.replace(/var\(\s*/, "")] = 1; });
    });
    var noetig = {}, fehlt = [];
    function ziehen(n){
      if (noetig[n]) return;
      if (!(n in hell)) { if (!eigen[n] && fehlt.indexOf(n) < 0) fehlt.push(n); return; }
      noetig[n] = 1;
      [hell[n], dunkel[n] || "", ruhig[n] || ""].join(" ").replace(/var\(\s*(--[\w-]+)/g, function(_, x){ ziehen(x); });
    }
    Object.keys(gesucht).forEach(ziehen);
    function block(sel, quelle, ein){
      var z = Object.keys(quelle).filter(function(n){ return noetig[n]; }).map(function(n){ return ein + "  " + n + ":" + quelle[n] + ";"; });
      return z.length ? ein + sel + "{\n" + z.join("\n") + "\n" + ein + "}" : "";
    }
    var ruhe = block(":root", ruhig, "  ");
    return [
      "/* Token-Auszug für Seiten OHNE design-system/tokens.css – nur, was " + namen.join(" und ") + " braucht,",
      "   berechnet aus tokens.css (Stand dieser Seite). Die Webfonts (Goetheanum, Source Sans 3)",
      "   lädt die Seite selbst per @font-face. */",
      block(":root", hell, ""),
      ruhe ? "@media (prefers-reduced-motion:reduce){\n" + ruhe + "\n}" : "",
      block(':root[data-theme="dark"]', dunkel, ""),
      fehlt.length ? "/* nicht in tokens.css: " + fehlt.join(", ") + " – Rückfall im Modul, gesetzt vom Skript oder von einem data-sek */" : ""
    ].filter(Boolean).join("\n");
  }

  function fuellen(pre){
    var d = pre.dataset, p;
    if (d.tokenAuszug) {
      var dateien = d.tokenAuszug.split(/\s+/);
      p = Promise.all([laden("design-system/tokens.css")].concat(dateien.map(laden))).then(function(t){
        return tokenAuszug(t[0], t.slice(1), dateien.map(function(x){ return x.split("/").pop(); }));
      });
    } else if (d.quelle) {
      p = laden(d.quelle).then(function(t){ return d.ausschnitt ? ausschnitt(t, d.ausschnitt) : t.replace(/\s+$/, ""); });
    } else return;
    p.then(function(t){
      var an = d.anhang && document.getElementById(d.anhang);
      pre.textContent = an ? t + "\n\n" + an.textContent.replace(/^\s*\n/, "").replace(/\s+$/, "") : t;
    }, function(){ /* Fallback-Text im <pre> bleibt stehen (Link auf die Datei). */ });
  }

  function wahl(bereich){
    var seg = bereich.querySelector("[data-kopier-wahl]"), knopf = bereich.querySelector("[data-kopier-knopf]");
    var said = bereich.querySelector("[data-kopier-meldung]");
    if (!seg || !knopf) return;
    var ids = [].map.call(seg.querySelectorAll("button[data-code]"), function(b){ return b.dataset.code; });
    var aktiv = (seg.querySelector('[aria-pressed="true"]') || seg.querySelector("button")).dataset.code;
    seg.addEventListener("click", function(e){
      var b = e.target.closest("button[data-code]"); if (!b) return;
      aktiv = b.dataset.code;
      seg.querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      ids.forEach(function(id){ document.getElementById(id).hidden = id !== aktiv; });
      if (said) { said.textContent = ""; said.className = "said"; }
    });
    knopf.addEventListener("click", function(){
      var pre = document.getElementById(aktiv), txt = pre.textContent;
      var name = pre.dataset.name || seg.querySelector('[data-code="' + aktiv + '"]').textContent;
      function sagen(t, gut){ if (said) { said.textContent = t; said.className = "said " + (gut ? "gut" : "schlecht"); } }
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(function(){ var n = txt.split("\n").length; sagen(name + " kopiert – " + n + "\u00a0" + (n === 1 ? "Zeile." : "Zeilen."), true); },
        function(){ sagen("Kopieren nicht erlaubt – Block markieren und selbst kopieren.", false); });
      else sagen("Kopieren nicht erlaubt – Block markieren und selbst kopieren.", false);
    });
  }

  function start(){
    [].forEach.call(document.querySelectorAll("pre[data-quelle],pre[data-token-auszug]"), fuellen);
    [].forEach.call(document.querySelectorAll(".kopieren"), wahl);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
