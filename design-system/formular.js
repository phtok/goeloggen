/* =============================================================================
   Goetheanum CI – Formular (Modul-Skript)
   -----------------------------------------------------------------------------
   Logik ohne Backend für <form class="formular" data-formular>: Wahl in den
   .seg-Gruppen, Betrag im Knopf, freier Betrag, bedingte Adresse, Prüfung,
   Fehlerzusammenfassung, Dank. Alle Texte stehen im Markup (data-*), damit
   das Formular übersetzbar bleibt; Kurven und Dauern liest das Skript aus den
   Bewegungs-Tokens (tokens.css) – weniger Bewegung nullt sie dort.
   Prüfen: beim Verlassen eines Felds, aber erst wenn der Klick vorbei ist –
   eine Meldung, die zwischen Drücken und Loslassen erscheint, schiebt das Ziel
   unter dem Zeiger weg (Befund Prototyp 31. 10. 2026). Vor dem ersten
   Absenden prüft nur, wer schon etwas eingegeben hat.
   Backend: GoetheanumFormular.init(form, {absenden: function(daten){ return
   Promise }}) – ohne diese Angabe dankt das Formular nach 700 ms (Vorschau).
   Einbinden am Ende des <body> oder mit defer.
   ============================================================================= */
(function(){
  "use strict";
  var NB = " ";

  function token(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function dauer(n){ var v = token(n); var z = parseFloat(v) || 0; return /ms$/.test(v) ? z : z * 1000; }
  function kurve(){ return token("--kurve-bloom") || "ease"; }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
  /* Betrag ohne «.00», Tausender ab 10 000 mit schmalem Abstand (G25). */
  function zahl(n){
    var s = Number.isInteger(n) ? String(n) : n.toFixed(2);
    return n >= 10000 ? s.replace(/\B(?=(\d{3})+(?!\d))/g, " ") : s;
  }

  function init(form, opt){
    if (!form || form._formular) return form && form._formular;
    opt = opt || {};
    var $ = function(s){ return form.querySelector(s); };
    var $$ = function(s, r){ return [].slice.call((r || form).querySelectorAll(s)); };
    var rolle = function(n){ return $('[data-rolle="' + n + '"]'); };

    var waehrung = form.dataset.waehrung || "CHF";
    /* data-stufen-<frequenz>="20 50 100" · data-vorwahl-<frequenz>="50" */
    var STUFEN = {}, VORWAHL = {};
    Object.keys(form.dataset).forEach(function(k){
      var m = k.match(/^(stufen|vorwahl)(\w+)$/); if (!m) return;
      var f = m[2].charAt(0).toLowerCase() + m[2].slice(1), v = form.dataset[k].trim().split(/\s+/).map(Number);
      if (m[1] === "stufen") STUFEN[f] = v; else VORWAHL[f] = v[0];
    });
    var g = {frequenz:rolle("frequenz"), stufen:rolle("stufen"), betrag:rolle("betrag"), zahlart:rolle("zahlart"),
      bescheinigung:rolle("bescheinigung"), adresse:rolle("adresse"), fehlerliste:rolle("fehlerliste"),
      dank:rolle("dank"), knopf:rolle("absenden"), kosten:rolle("kosten"), hinweis:rolle("zahlart-hinweis"),
      vorlage:form.querySelector("template.dank-vorlage")};
    var einheit = g.betrag && g.betrag.closest(".einheit");
    var stand = {frequenz:null, stufe:null, zahlart:null, versucht:false};
    var meldungen = {};
    var ctl = {form:form, absenden:opt.absenden || null, vorbelegt:null};

    function betragEigen(){
      if (!g.betrag) return null;
      var v = g.betrag.value.replace(/[\s'’  ]/g, "").replace(",", ".");
      if (v === "") return null;
      var n = Number(v);
      return isFinite(n) ? n : NaN;
    }
    function betrag(){ var e = betragEigen(); return e === null ? stand.stufe : e; }
    function geld(n){ return '<span class="num">' + zahl(n) + NB + esc(waehrung) + "</span>"; }

    /* Ein Knopf, eine Gruppe: Wahl setzen; der Berührpunkt ist der Keim. */
    function waehlen(gruppe, b){
      $$("button", gruppe).forEach(function(x){ x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    }
    $$(".seg").forEach(function(s){
      s.addEventListener("pointerdown", function(e){
        var b = e.target.closest("button"); if (!b) return;
        var r = b.getBoundingClientRect();
        b.style.setProperty("--x", (e.clientX - r.left) + "px");
        b.style.setProperty("--y", (e.clientY - r.top) + "px");
      });
      s.addEventListener("keydown", function(e){
        var b = e.target.closest("button");
        if (b && (e.key === "Enter" || e.key === " ")) { b.style.removeProperty("--x"); b.style.removeProperty("--y"); }
      });
    });

    /* Knopf: Beschriftung folgt der Wahl – «Jetzt 50 CHF spenden». */
    function knopfText(){
      if (!g.knopf) return;
      var n = betrag(), k = g.knopf.dataset;
      var t = (n && n > 0) ? ((stand.frequenz === "monatlich" && k.textMonatlich) || k.text || "{betrag}") : (k.textLeer || "");
      g.knopf.innerHTML = "<span>" + esc(t).replace("{betrag}", n > 0 ? geld(n) : "") + "</span>";
    }
    function zahlHinweis(){
      if (!g.hinweis) return;
      var b = stand.zahlart && $('[data-rolle="zahlart"] [data-wert="' + stand.zahlart + '"]');
      var t = b ? (b.dataset.hinweis || "") : "";
      var max = b && Number(b.dataset.max);
      if (max && betrag() > max && b.dataset.maxHinweis) t = b.dataset.maxHinweis.replace("{max}", zahl(max) + NB + waehrung);
      g.hinweis.textContent = t;
    }

    /* Häufigkeit: neue Stufen, die Ziffern kommen gestaffelt. */
    function frequenzSetzen(f, sanft){
      stand.frequenz = f;
      if (g.frequenz) waehlen(g.frequenz, $('[data-rolle="frequenz"] [data-wert="' + f + '"]'));
      var reihe = STUFEN[f];
      if (g.stufen && reihe) {
        stand.stufe = VORWAHL[f] != null ? VORWAHL[f] : null;
        if (g.betrag) { g.betrag.value = ""; if (einheit) einheit.classList.remove("gewaehlt"); }
        var st = dauer("--staffel"), d = dauer("--dauer-mittel");
        $$("button", g.stufen).forEach(function(b, i){
          b.textContent = reihe[i] != null ? reihe[i] : "";
          b.hidden = reihe[i] == null;
          b.setAttribute("aria-pressed", reihe[i] === stand.stufe ? "true" : "false");
          if (sanft && d && b.animate) b.animate([{opacity:0},{opacity:1}], {duration:d, delay:i * st, easing:kurve(), fill:"backwards"});
        });
      }
      knopfText(); zahlHinweis();
    }
    if (g.frequenz) g.frequenz.addEventListener("click", function(e){
      var b = e.target.closest("button"); if (b && b.dataset.wert !== stand.frequenz) frequenzSetzen(b.dataset.wert, true);
    });

    /* Stufe ↔ freier Betrag: wer tippt, lässt die Stufe welken und den Ring
       wachsen; wer das Feld leert, bekommt die zuletzt gewählte Stufe zurück. */
    if (g.stufen) g.stufen.addEventListener("click", function(e){
      var b = e.target.closest("button"); if (!b) return;
      stand.stufe = Number(b.textContent);
      waehlen(g.stufen, b);
      if (g.betrag) { g.betrag.value = ""; if (einheit) einheit.classList.remove("gewaehlt"); feldFehler(g.betrag, ""); zusammenfassung(); }
      knopfText(); zahlHinweis();
    });
    if (g.betrag) g.betrag.addEventListener("input", function(){
      var eigen = g.betrag.value.trim() !== "";
      if (einheit) einheit.classList.toggle("gewaehlt", eigen);
      if (g.stufen) $$("button", g.stufen).forEach(function(b){
        b.setAttribute("aria-pressed", !eigen && Number(b.textContent) === stand.stufe ? "true" : "false");
      });
      knopfText(); zahlHinweis();
    });

    if (g.zahlart) g.zahlart.addEventListener("click", function(e){
      var b = e.target.closest("button"); if (!b) return;
      stand.zahlart = b.dataset.wert;
      waehlen(g.zahlart, b);
      zahlHinweis();
      if (stand.versucht) pruefen([g.zahlart]);
    });

    /* Bescheinigung: erst dann wächst die Adresse heran. */
    function adresseSetzen(){
      if (!g.bescheinigung || !g.adresse) return;
      var an = g.bescheinigung.checked, innen = g.adresse.querySelector(".innen");
      g.adresse.classList.toggle("offen", an);
      if (innen) innen.inert = !an;
      if (!an) { $$("[required]", g.adresse).forEach(function(f){ feldFehler(f, ""); }); zusammenfassung(); }
    }
    if (g.bescheinigung) g.bescheinigung.addEventListener("change", adresseSetzen);

    /* --- Prüfen: Sätze statt Signalwörter, Wortlaut aus dem Markup --------- */
    function reihe(){
      return $$('[data-rolle="betrag"],[data-rolle="zahlart"],[required]').filter(function(el){
        return !(g.adresse && g.adresse.contains(el) && !(g.bescheinigung && g.bescheinigung.checked));
      });
    }
    function regel(el){
      var d = el.dataset;
      if (el === g.zahlart) return stand.zahlart ? "" : (d.leer || "");
      if (el === g.betrag) {
        var e = betragEigen(), min = Number(d.min || 1);
        if (e === null) return stand.stufe ? "" : (d.leer || "");
        if (isNaN(e)) return d.format || "";
        if (e < min) return (d.minText || "").replace("{min}", zahl(min) + NB + waehrung);
        return "";
      }
      var v = el.value.trim();
      if (!v) return d.leer || "";
      if (el.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return d.format || "";
      return "";
    }
    function fehlerFeld(el){ return el.id ? form.querySelector("#" + el.id + "-fehler") : null; }
    function feldFehler(el, text){
      meldungen[el.id] = text;
      var s = fehlerFeld(el);
      if (s) { s.hidden = !text; s.innerHTML = text ? '<span class="sr-only">' + esc(form.dataset.fehlerVorsatz || "Fehler:") + " </span>" + esc(text) : ""; }
      if (el === g.zahlart) { var fs = el.closest("fieldset"); if (fs) fs.classList.toggle("gruppe-fehler", !!text); }
      else if (text) el.setAttribute("aria-invalid", "true"); else el.removeAttribute("aria-invalid");
    }
    function pruefen(els){ els.forEach(function(el){ feldFehler(el, regel(el)); }); zusammenfassung(); }
    function zusammenfassung(){
      var box = g.fehlerliste; if (!box) return;
      var ul = box.querySelector("ul"), offen = reihe().filter(function(el){ return meldungen[el.id]; });
      ul.innerHTML = "";
      offen.forEach(function(el){
        var li = document.createElement("li"), a = document.createElement("a");
        a.href = "#" + el.id;
        a.textContent = meldungen[el.id];
        a.addEventListener("click", function(e){
          e.preventDefault();
          var z = el === g.zahlart ? el.querySelector("button") : el;
          z.focus(); z.scrollIntoView({block:"center"});
        });
        li.appendChild(a); ul.appendChild(li);
      });
      box.hidden = !(stand.versucht && offen.length);
    }
    var zeiger = false;
    document.addEventListener("pointerdown", function(){ zeiger = true; }, true);
    document.addEventListener("pointercancel", function(){ zeiger = false; }, true);
    function nachDemKlick(fn){
      if (!zeiger) return fn();
      document.addEventListener("pointerup", function los(){
        document.removeEventListener("pointerup", los, true);
        zeiger = false; setTimeout(fn, 0);
      }, true);
    }
    $$('[data-rolle="betrag"],[required]').forEach(function(el){
      el.addEventListener("blur", function(){
        if (stand.versucht || el.value.trim() || meldungen[el.id]) nachDemKlick(function(){ pruefen([el]); });
      });
    });

    /* --- Absenden: der Knopf wartet, dann wächst der Dank aus ihm --------- */
    function daten(){
      var d = {frequenz:stand.frequenz, betrag:betrag(), waehrung:waehrung, zahlart:stand.zahlart,
        bescheinigung:!!(g.bescheinigung && g.bescheinigung.checked)};
      $$("input[name],select[name],textarea[name]").forEach(function(f){
        if (f.type === "checkbox") return;
        if (g.adresse && g.adresse.contains(f) && !d.bescheinigung) return;
        if (f !== g.betrag) d[f.name] = f.value.trim();
      });
      return d;
    }
    form.addEventListener("submit", function(e){
      e.preventDefault();
      stand.versucht = true;
      var els = reihe();
      pruefen(els);
      if (els.some(function(el){ return meldungen[el.id]; })) { if (g.fehlerliste) g.fehlerliste.focus(); return; }
      var d = daten();
      g.knopf.disabled = true;
      g.knopf.textContent = g.knopf.dataset.textWarten || "…";
      var p = ctl.absenden ? Promise.resolve(ctl.absenden(d)) : new Promise(function(r){ setTimeout(r, 700); });
      p.then(function(){ danken(d); }, function(){ g.knopf.disabled = false; knopfText(); });
    });

    function danken(d){
      if (!g.dank || !g.vorlage) return;
      var hoehe = g.knopf.offsetHeight;
      var frag = g.vorlage.content.cloneNode(true);
      [].slice.call(frag.querySelectorAll("[data-wenn]")).forEach(function(x){
        var w = x.dataset.wenn, nicht = w.charAt(0) === "!", k = nicht ? w.slice(1) : w;
        var gilt = k === "bescheinigung" ? d.bescheinigung : d.frequenz === k;
        if (nicht ? gilt : !gilt) x.remove();
      });
      [].slice.call(frag.querySelectorAll("[data-feld]")).forEach(function(x){
        var f = x.dataset.feld;
        if (f === "betrag") x.innerHTML = geld(d.betrag); else x.textContent = d[f] || "";
      });
      g.dank.innerHTML = "";
      g.dank.appendChild(frag);
      g.knopf.hidden = true; if (g.kosten) g.kosten.hidden = true;
      var innen = g.dank.firstElementChild, ziel = g.dank.offsetHeight, lang = dauer("--dauer-lang");
      if (lang && g.dank.animate && innen) {
        var k = kurve();
        g.dank.animate([{height:hoehe + "px"},{height:ziel + "px"}], {duration:lang, easing:k});
        innen.animate([{backgroundColor:getComputedStyle(g.knopf).backgroundColor},{backgroundColor:getComputedStyle(innen).backgroundColor}], {duration:lang, easing:k});
        [].slice.call(innen.children).forEach(function(x, i){
          x.animate([{opacity:0},{opacity:1}], {duration:dauer("--dauer-mittel"), delay:lang * .5 + i * dauer("--staffel"), easing:k, fill:"backwards"});
        });
      }
      var h = g.dank.querySelector("h2,h3");
      if (h) { h.tabIndex = -1; h.focus({preventScroll:true}); }
      var neuKnopf = g.dank.querySelector('[data-rolle="neu"]');
      if (neuKnopf) neuKnopf.addEventListener("click", neu);
    }
    function neu(){
      form.reset();
      g.dank.innerHTML = "";
      g.knopf.hidden = false; g.knopf.disabled = false; if (g.kosten) g.kosten.hidden = false;
      stand.zahlart = null; stand.versucht = false;
      if (g.zahlart) $$("button", g.zahlart).forEach(function(b){ b.setAttribute("aria-pressed", "false"); });
      adresseSetzen();
      reihe().concat($$("[required]")).forEach(function(el){ feldFehler(el, ""); });
      meldungen = {};
      zusammenfassung();
      frequenzSetzen(ctl.vorbelegt || start, false);
      var erst = g.frequenz ? g.frequenz.querySelector("button") : form.querySelector("button,input");
      if (erst) erst.focus();
    }

    var start = g.frequenz ? ((g.frequenz.querySelector('[aria-pressed="true"]') || g.frequenz.querySelector("button")).dataset.wert) : "einmalig";
    frequenzSetzen(start, false);
    adresseSetzen();

    ctl.frequenz = frequenzSetzen;
    ctl.neu = neu;
    ctl.daten = daten;
    form._formular = ctl;
    return ctl;
  }

  function alle(){ [].slice.call(document.querySelectorAll("form[data-formular]")).forEach(function(f){ init(f); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", alle); else alle();
  window.GoetheanumFormular = {init:init};
})();
