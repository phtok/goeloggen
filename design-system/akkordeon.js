/* =============================================================================
   Goetheanum CI – Akkordeon (Modul-Skript)
   -----------------------------------------------------------------------------
   Macht <details class="acc"> weich (Bloom-Kurve), hält je .acc-liste eines offen
   (ohne dass die Seite springt), bietet «Alle aufklappen» (.acc-kopf .alle),
   öffnet beim Drucken alles und stellt danach den Stand wieder her, und öffnet
   per Adresse (#faden-7) die verlinkte Frage. Ohne Skript bleibt alles nativ
   klappbar. Einbinden am Ende des <body> oder mit defer.
   ============================================================================= */
(function(){
  var KURVE = "cubic-bezier(.32,.08,.24,1)";
  var reduziert = window.matchMedia("(prefers-reduced-motion: reduce)");
  function dauer(ms){ return reduziert.matches ? 0 : ms; }
  function kopfHoehe(){
    // Klebende Leisten (Kopfzeile, Sprungleiste) – die Frage soll darunter sichtbar bleiben.
    var h = 0;
    document.querySelectorAll("[data-acc-kopf], .dsnav, .dsnav-onpage, #navigation").forEach(function(k){
      var cs = getComputedStyle(k);
      if (cs.position === "sticky" || cs.position === "fixed") h += k.offsetHeight;
    });
    return h + 16;
  }
  function liste(d){ return d.closest(".acc-liste"); }

  function oeffnen(d, sofort){
    var body = d.querySelector(".acc-body"), sum = d.querySelector("summary");
    var l = liste(d);
    if (l && !l.dataset.alle) {
      // Eines aufs Mal – und die angetippte Frage bleibt an ihrem Platz:
      // was DARÜBER zugeht, geht ohne Bewegung zu, der Versatz wird ausgeglichen.
      var vorher = sum.getBoundingClientRect().top;
      l.querySelectorAll("details.acc.is-open").forEach(function(o){
        if (o === d) return;
        var oben = o.compareDocumentPosition(d) & Node.DOCUMENT_POSITION_FOLLOWING;
        schliessen(o, oben);
      });
      var nachher = sum.getBoundingClientRect().top;
      if (nachher !== vorher) window.scrollBy(0, nachher - vorher);
    }
    d.open = true; d.classList.add("is-open");
    if (sofort || !body.animate) return;
    var h = body.scrollHeight;
    d.classList.add("anim");
    var a = body.animate([{height:"0px",opacity:0},{height:h+"px",opacity:1}],{duration:dauer(280),easing:KURVE});
    a.onfinish = a.oncancel = function(){
      d.classList.remove("anim");
      // Liegt die Frage jetzt unter der Kopfzeile, nachziehen.
      var t = sum.getBoundingClientRect().top, k = kopfHoehe();
      if (t < k) window.scrollBy({top: t - k, behavior: reduziert.matches ? "instant" : "smooth"});
    };
  }
  function schliessen(d, sofort){
    var body = d.querySelector(".acc-body");
    d.classList.remove("is-open");
    if (sofort || !body.animate) { d.open = false; d.classList.remove("anim"); return; }
    var h = body.offsetHeight;
    d.classList.add("anim");
    var a = body.animate([{height:h+"px",opacity:1},{height:"0px",opacity:0}],{duration:dauer(220),easing:KURVE});
    a.onfinish = a.oncancel = function(){ d.open = false; d.classList.remove("anim"); };
  }

  // Alle aufklappen / zuklappen – je Liste; hebt «eines aufs Mal» auf, solange alles offen ist.
  function alleSetzen(l, offen, sofort){
    l.querySelectorAll("details.acc").forEach(function(d){
      var ist = d.classList.contains("is-open");
      if (offen && !ist) { d.open = true; d.classList.add("is-open"); }
      if (!offen && ist) { if (sofort) { d.open = false; d.classList.remove("is-open"); } else schliessen(d); }
    });
    if (offen) l.dataset.alle = "1"; else delete l.dataset.alle;
    var b = l.querySelector(".alle");
    if (b) { b.setAttribute("aria-pressed", offen ? "true" : "false"); b.textContent = offen ? "Alle zuklappen" : "Alle aufklappen"; }
  }

  function ausHash(){
    var id = decodeURIComponent(location.hash.slice(1));
    var d = id && document.getElementById(id);
    if (d && d.matches("details.acc") && !d.classList.contains("is-open")) {
      oeffnen(d, true);
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
    });
    document.querySelectorAll(".acc-kopf .alle").forEach(function(b){
      if (b.dataset.accBereit) return; b.dataset.accBereit = "1";
      b.addEventListener("click", function(){
        var l = b.closest(".acc-liste");
        alleSetzen(l, !l.dataset.alle, false);
      });
    });
    ausHash();
  }

  // Drucken: alles öffnen, danach den vorherigen Stand wiederherstellen.
  var vorDruck = null;
  window.addEventListener("beforeprint", function(){
    vorDruck = [];
    document.querySelectorAll(".acc-liste").forEach(function(l){
      vorDruck.push({l:l, alle:!!l.dataset.alle, offen:[].map.call(l.querySelectorAll("details.acc.is-open"), function(d){return d.id;})});
      alleSetzen(l, true, true);
    });
  });
  window.addEventListener("afterprint", function(){
    if (!vorDruck) return;
    vorDruck.forEach(function(s){
      if (s.alle) return;
      alleSetzen(s.l, false, true);
      s.offen.forEach(function(id){ var d = document.getElementById(id); if (d) { d.open = true; d.classList.add("is-open"); } });
    });
    vorDruck = null;
  });
  window.addEventListener("hashchange", ausHash);

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.GoetheanumAkkordeon = {init:init, oeffnen:oeffnen, schliessen:schliessen, alle:alleSetzen};
})();
