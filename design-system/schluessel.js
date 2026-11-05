/* =============================================================================
   Goetheanum CI – Werkzeug-Schlüssel (Modul-Skript)
   -----------------------------------------------------------------------------
   Schreibende und heikle RPCs verlangen einen Schlüssel je Werkzeug
   (public.werkzeug_tor, services/werkzeug-schluessel/schema.sql). Dieses
   Skript fragt ihn einmal je Gerät ab, prüft ihn sofort (werkzeug_key_ok)
   und merkt ihn in localStorage. Ein falscher Schlüssel (HTTP 403) wird
   vergessen und neu erfragt.

     GoeSchluessel.rpc('folder', 'folder_liste', {})          → Promise<json>
     GoeSchluessel.rpc('folder', 'folder_sichern', body,
                       { fragen: false, keepalive: true })   → still im Hintergrund
     GoeSchluessel.rpc('kurzlinks', 'sommer2026_link_anlegen', body,
                       { param: 'p_schluessel' })            → anderer Parametername

   Fehler: Error mit .status (HTTP) bzw. .abgebrochen = true.
   ============================================================================= */
(function(){
  "use strict";
  var SB  = "https://dagcsnfrlbpxcmdimnrw.supabase.co";
  var KEY = "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY";   // öffentlicher Anon-Key
  var NAMEN = {
    kurzlinks: "die Kurzlinks", folder: "das Folder-Archiv", reader: "den LT-Reader",
    zaehler: "den Sommer-Zähler", lesetest: "die Lesetest-Auswertung"
  };
  var offen = {};      // laufende Abfrage je Werkzeug – nie zwei Dialoge zugleich
  var abgelehnt = {};  // einmal abgebrochen = für diesen Seitenbesuch nicht mehr fragen

  function speicher(w){ return "goe-schluessel:" + w; }
  function gemerkt(w){ try { return localStorage.getItem(speicher(w)) || ""; } catch(e){ return ""; } }
  function merken(w, k){ try { localStorage.setItem(speicher(w), k); } catch(e){} }
  function vergessen(w){ try { localStorage.removeItem(speicher(w)); } catch(e){} }

  function post(name, body, keepalive){
    return fetch(SB + "/rest/v1/rpc/" + name, {
      method: "POST", keepalive: !!keepalive,
      headers: { "Content-Type": "application/json", "apikey": KEY, "Authorization": "Bearer " + KEY },
      body: JSON.stringify(body || {})
    });
  }

  function pruefen(w, k){
    return post("werkzeug_key_ok", { p_werkzeug: w, p_key: k })
      .then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); });
  }

  var STIL =
    ".goe-schluessel{border:1px solid var(--line);border-radius:var(--r-card);background:var(--paper,Canvas);color:var(--ink,CanvasText);" +
      "padding:var(--s5);width:min(34rem,calc(100vw - 2rem));box-shadow:var(--shadow-card);" +
      "position:fixed;inset:0;margin:auto;height:fit-content;max-height:calc(100dvh - 2rem);hyphens:manual}" +
    ".goe-schluessel::backdrop{background:color-mix(in srgb,var(--ink,CanvasText) 35%,transparent)}" +
    ".goe-schluessel form{display:grid;gap:var(--s4);margin:0}" +
    ".goe-schluessel h2{margin:0;font-size:var(--t-h3);text-wrap:balance}" +
    ".goe-schluessel p{margin:0;font-family:var(--font-text);font-size:var(--t-small);color:var(--muted);text-wrap:pretty}" +
    ".goe-schluessel .fehler{color:var(--bad)}" +
    ".goe-schluessel .knoepfe{display:flex;flex-wrap:wrap;gap:var(--s2);justify-content:flex-end}";

  function dialog(w, grund){
    if (!document.getElementById("goe-schluessel-stil")){
      var st = document.createElement("style"); st.id = "goe-schluessel-stil"; st.textContent = STIL;
      document.head.appendChild(st);
    }
    return new Promise(function(fertig){
      var d = document.createElement("dialog");
      d.className = "goe-schluessel";
      d.setAttribute("aria-labelledby", "goe-schluessel-titel");
      d.innerHTML =
        '<form method="dialog" novalidate>' +
          '<h2 id="goe-schluessel-titel">Schlüssel für ' + (NAMEN[w] || w) + '</h2>' +
          '<p>Einmal je Gerät, danach merkt sich der Browser ihn. Den Schlüssel gibt das Team.</p>' +
          '<label class="field"><span class="lab">Schlüssel</span>' +
            '<input name="k" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" ' +
              'inputmode="text" aria-describedby="goe-schluessel-meldung"></label>' +
          '<p id="goe-schluessel-meldung" class="fehler" role="alert"></p>' +
          '<div class="knoepfe">' +
            '<button type="button" class="btn ghost" value="ab">Abbrechen</button>' +
            '<button type="submit" class="btn primary">Weiter</button>' +
          '</div>' +
        '</form>';
      document.body.appendChild(d);
      var f = d.querySelector("form"), feld = f.elements.k, meldung = d.querySelector("#goe-schluessel-meldung");
      function sag(t){ meldung.textContent = t; feld.setAttribute("aria-invalid", t ? "true" : "false"); }
      if (grund === "falsch") sag("Der gemerkte Schlüssel gilt nicht mehr. Bitte geben Sie den aktuellen ein.");
      if (grund === "fehlt") sag("Ohne Schlüssel geht es hier nicht weiter.");
      function zu(k){ d.close(); d.remove(); fertig(k); }
      d.querySelector('button[value="ab"]').addEventListener("click", function(){ zu(""); });
      d.addEventListener("cancel", function(ev){ ev.preventDefault(); zu(""); });
      f.addEventListener("submit", function(ev){
        ev.preventDefault();
        var k = feld.value.trim();
        if (!k){ sag("Geben Sie den Schlüssel ein."); feld.focus(); return; }
        sag("");
        pruefen(w, k).then(function(ok){
          if (ok){ merken(w, k); zu(k); }
          else { sag("Dieser Schlüssel stimmt nicht. Gross- und Kleinschreibung, Leerzeichen und Bindestriche sind egal."); feld.focus(); }
        }).catch(function(){ sag("Der Dienst ist gerade nicht erreichbar. Bitte später noch einmal."); });
      });
      d.showModal(); feld.focus();
    });
  }

  function holen(w, opt){
    opt = opt || {};
    var k = gemerkt(w);
    if (k && !opt.falsch) return Promise.resolve(k);
    if (opt.fragen === false || abgelehnt[w]) return Promise.resolve("");
    if (!offen[w]) offen[w] = dialog(w, opt.grund || (opt.falsch ? "falsch" : "")).then(function(k){ delete offen[w]; if (!k) abgelehnt[w] = true; return k; });
    return offen[w];
  }

  function rpc(w, name, body, opt){
    opt = opt || {};
    var param = opt.param || "p_key";
    var gesendet = "";
    function los(k){
      gesendet = k;
      var b = Object.assign({}, body || {}); b[param] = k;
      return post(name, b, opt.keepalive);
    }
    return holen(w, opt).then(los).then(function(r){
      if (r.status !== 403) return r;
      vergessen(w);
      if (opt.fragen === false) return r;
      return holen(w, { falsch: true, grund: gesendet ? "falsch" : "fehlt" }).then(function(k){
        if (!k){ var e = new Error("abgebrochen"); e.abgebrochen = true; e.status = 403; throw e; }
        return los(k);
      });
    }).then(function(r){
      if (!r.ok){ var e = new Error(String(r.status)); e.status = r.status; throw e; }
      return r.json();
    });
  }

  window.GoeSchluessel = { rpc: rpc, holen: holen, gemerkt: gemerkt, vergessen: vergessen };
})();
