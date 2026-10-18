/* =============================================================================
   Goetheanum CI – Akkordeon (Modul-Skript)
   -----------------------------------------------------------------------------
   Macht <details class="acc"> weich (Bloom-Kurve). Antworten öffnen UNABHÄNGIG
   voneinander – beliebige Kombinationen bleiben offen (GOV.UK-Muster), weil
   zusammengehörige Fragen sich vergleichen lassen müssen. «Alle aufklappen»
   (.acc-kopf .alle) öffnet und schliesst die ganze Liste; beim Drucken ist alles
   offen und danach steht der Stand wieder wie vorher. Wer eine Antwort öffnet,
   bekommt ihre Adresse in die Adresszeile; «Link kopieren» legt sie in die
   Zwischenablage. Ohne Skript bleibt alles nativ klappbar.
   Einbinden am Ende des <body> oder mit defer.
   ============================================================================= */
(function(){
  var KURVE = "cubic-bezier(.32,.08,.24,1)";
  var reduziert = window.matchMedia("(prefers-reduced-motion: reduce)");
  function dauer(ms){ return reduziert.matches ? 0 : ms; }

  function oeffnen(d, sofort){
    var body = d.querySelector(".acc-body");
    d.open = true; d.classList.add("is-open");
    if (!sofort && body.animate) {
      var h = body.scrollHeight;
      d.classList.add("anim");
      var a = body.animate([{height:"0px",opacity:0},{height:h+"px",opacity:1}],{duration:dauer(280),easing:KURVE});
      a.onfinish = a.oncancel = function(){ d.classList.remove("anim"); };
    }
    adresse(d);
    knopfStand(d);
  }
  function schliessen(d, sofort){
    var body = d.querySelector(".acc-body");
    d.classList.remove("is-open");
    if (sofort || !body.animate) { d.open = false; d.classList.remove("anim"); }
    else {
      var h = body.offsetHeight;
      d.classList.add("anim");
      var a = body.animate([{height:h+"px",opacity:1},{height:"0px",opacity:0}],{duration:dauer(220),easing:KURVE});
      a.onfinish = a.oncancel = function(){ d.open = false; d.classList.remove("anim"); };
    }
    // Schliesst sich die Antwort, auf die die Adresse zeigt, verliert die Adresse ihren Anker.
    if (location.hash.slice(1) === d.id) adresse(null);
    knopfStand(d);
  }

  /* Die Adresse zeigt auf die zuletzt geöffnete Antwort – ohne Sprung und ohne
     einen Eintrag in der Zurück-Geschichte (replaceState löst kein hashchange). */
  function adresse(d){
    if (!history.replaceState) return;
    var u = new URL(location.href);
    u.hash = d ? d.id : "";
    history.replaceState(null, "", u.toString().replace(/#$/, ""));
  }

  /* «Alle aufklappen» spiegelt den Stand der Liste, egal wie er zustande kam. */
  function knopfStand(d){
    var l = d.closest(".acc-liste"); if (!l) return;
    var b = l.querySelector(".alle"); if (!b) return;
    var alle = l.querySelectorAll("details.acc");
    var offen = l.querySelectorAll("details.acc.is-open");
    var ganz = alle.length > 0 && offen.length === alle.length;
    b.setAttribute("aria-pressed", ganz ? "true" : "false");
    b.textContent = ganz ? "Alle zuklappen" : "Alle aufklappen";
  }
  function alleSetzen(l, offen, sofort){
    l.querySelectorAll("details.acc").forEach(function(d){
      var ist = d.classList.contains("is-open");
      if (offen && !ist) { d.open = true; d.classList.add("is-open"); }
      if (!offen && ist) { if (sofort) { d.open = false; d.classList.remove("is-open"); } else schliessen(d); }
    });
    var b = l.querySelector(".alle");
    if (b) { b.setAttribute("aria-pressed", offen ? "true" : "false"); b.textContent = offen ? "Alle zuklappen" : "Alle aufklappen"; }
  }

  function teilen(d, b){
    var u = new URL(location.href); u.hash = d.id;
    var wort = b.dataset.wort || b.textContent;
    b.dataset.wort = wort;
    function sagen(t){ b.textContent = t; setTimeout(function(){ b.textContent = wort; }, 2000); }
    if (navigator.clipboard) navigator.clipboard.writeText(u.toString()).then(function(){ sagen("Link kopiert"); }, function(){ sagen("Kopieren nicht erlaubt"); });
    else sagen("Kopieren nicht erlaubt");
  }

  function ausHash(){
    var id = decodeURIComponent(location.hash.slice(1));
    var d = id && document.getElementById(id);
    if (d && d.matches("details.acc") && !d.classList.contains("is-open")) {
      d.open = true; d.classList.add("is-open"); knopfStand(d);
      d.scrollIntoView({block:"start"});
    }
  }

  function init(){
    document.querySelectorAll("details.acc").forEach(function(d){
      if (d.dataset.accBereit) return; d.dataset.accBereit = "1";
      if (d.open) d.classList.add("is-open");
      d.querySelector("summary").addEventListener("click", function(e){
        e.preventDefault();
        if (d.classList.contains("anim")) return;
        if (d.classList.contains("is-open")) schliessen(d); else oeffnen(d);
      });
      var t = d.querySelector(".teilen");
      if (t) t.addEventListener("click", function(){ teilen(d, t); });
    });
    document.querySelectorAll(".acc-kopf .alle").forEach(function(b){
      if (b.dataset.accBereit) return; b.dataset.accBereit = "1";
      b.addEventListener("click", function(){
        var l = b.closest(".acc-liste");
        alleSetzen(l, b.getAttribute("aria-pressed") !== "true", false);
      });
    });
    ausHash();
  }

  // Drucken: alles öffnen, danach den vorherigen Stand wiederherstellen.
  var vorDruck = null;
  window.addEventListener("beforeprint", function(){
    vorDruck = [];
    document.querySelectorAll(".acc-liste").forEach(function(l){
      vorDruck.push({l:l, offen:[].map.call(l.querySelectorAll("details.acc.is-open"), function(d){return d.id;})});
      alleSetzen(l, true, true);
    });
  });
  window.addEventListener("afterprint", function(){
    if (!vorDruck) return;
    vorDruck.forEach(function(s){
      alleSetzen(s.l, false, true);
      s.offen.forEach(function(id){ var d = document.getElementById(id); if (d) { d.open = true; d.classList.add("is-open"); } });
      var erste = s.l.querySelector("details.acc"); if (erste) knopfStand(erste);
    });
    vorDruck = null;
  });
  window.addEventListener("hashchange", ausHash);

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.GoetheanumAkkordeon = {init:init, oeffnen:oeffnen, schliessen:schliessen, alle:alleSetzen};
})();
