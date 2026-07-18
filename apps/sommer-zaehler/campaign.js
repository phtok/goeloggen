// =============================================================================
// campaign.js · geteilte Logik der Kampagnen-App. Aus dem Cockpit extrahiert.
// Jede Seite laedt dieselbe Datei; Renderer und Verdrahtung sind element-
// gewaechtert (if el(...)), sodass jede Seite nur ihre eigenen Abschnitte
// rendert. Nur Aggregate verlassen die DB (RPCs). Backend unveraendert.
// =============================================================================
  /* ── Einstellungen · HART VERDRAHTET ──────────────────────────────────────
     Zahlen der Anmeldungen kommen live aus dem Backend. Zielmarken, Preise und
     Bleibe-Quote werden hier gesetzt – sobald die echten Werte vorliegen, nur
     diese Werte anpassen. */
  var CONFIG = {
    start: '2026-07-03',            // Aktionsstart (Nachmittag 3. Juli 2026)
    ende:  '2026-08-08',            // Aktionsende
    bleibeQuote: 0.62,             // Annahme, bis Erfahrungswerte vorliegen
    meilensteine: [100, 250, 500, 1000],
    zielGesamt: 1000,               // Gesamtziel der Aktion (neue Abos)
    ziele: {                        // Zielmarke je Strom (Zwischenmarken, Summe = Gesamtziel)
      'wos.de.papier': 200, 'wos.de.digital': 250,
      'wos.en.digital': 120,
      'gtv.de': 250, 'gtv.en': 180
    },
    // Anzeige-Währung aller Geldbeträge (Kosten, CPA, Summenzeile Folgejahr-Umsatz).
    waehrung: 'CHF',
    // Umrechnung EUR→CHF – nur für die Summenzeile (EUR-Umsatz in die
    // CHF-Gesamtsumme einrechnen). Bei Kursbewegung hier nachführen.
    eurChf: 0.93,
    // ECHTE Preise (Stand 17.7.2026): Wochenschrift aus den vier Kampagnen-
    // Formularen (Paperform, CHF/EUR × Papier&Online/Online), goetheanum.tv aus
    // dem Uscreen-Store (rechnet ausschliesslich in EUR: 14.90/Monat, 149/Jahr).
    // «Ermässigt» ist im Shop KEIN eigener Preis, sondern läuft über Coupons
    // (20/30/50 %) – ermässigte Zeilen rechnen darum zum Standardpreis (Fallback).
    // Das Förderabo der Wochenschrift (Papier 249 CHF/239 EUR, Online 199/189
    // im Jahr) führt das Backend nicht als Tarif – es zählt als Standard.
    preise: {
      chf: {
        wos: { papier:  { standard:{monatlich:14.9, jaehrlich:149} },
               digital: { standard:{monatlich:10.9, jaehrlich:109} } }
      },
      eur: {
        wos: { papier:  { standard:{monatlich:13.9, jaehrlich:139} },
               digital: { standard:{monatlich:9.9,  jaehrlich:99} } },
        gtv: { stream:  { standard:{monatlich:14.9, jaehrlich:149} } }
      }
    },
    // Herkunftswege (Attribution) mit Hauptaufgabe – nicht jeder Kanal verkauft.
    // Social stiftet Aufmerksamkeit, der Newsletter Beziehung, das Mailing die
    // Entscheidung. Die Rolle sagt, gegen welche Aufgabe man den Kanal fair liest.
    kanaele: [
      { key:'newsletter', label:'Newsletter',     rolle:'Beziehung' },
      { key:'mailer',     label:'Mailing',        rolle:'Entscheidung' },
      { key:'social',     label:'Social Media',   rolle:'Aufmerksamkeit' },
      { key:'popup',      label:'Popup',          rolle:'Entscheidung' },
      { key:'website',    label:'Website direkt', rolle:'Orientierung' },
      { key:'empfehlung', label:'Empfehlung',     rolle:'Vertrauen' },
      { key:'andere',     label:'ohne UTM',       rolle:'' }
    ],
    // Kosten der Aktion (in CONFIG.waehrung) – stehen auf 0, echte Zahlen werden erfragt.
    zahlenProvisorisch: true,      // blendet den Hinweis auf Beispielwerte ein
    // Externe Quelle der Social-Media-Zahlen (Reichweite/Klicks je Kanal).
    // Metricool gibt die Zahlen nur im geschützten Dashboard aus – ein Live-Abgriff
    // aus dem Browser ist nicht möglich. Darum ablesen und je Aktivität eintragen.
    quelleSocial: {
      label: 'Metricool · Kampagnen-Auswertung',
      url:   'https://app.metricool.com/reporting/campaigns-dashboard/public?token=eyJ6aXAiOiJERUYiLCJhbGciOiJIUzUxMiJ9.eJxVztFSgkAUgOF3ObcywhrCxh3VTLLWZmZmNU2Dy5Lgrhzg5AhN7x7jXZf_d_X_QPqdQfQOOyJsI9dNEcdWU1OoqjJjVVn4cKBICSIW8ouQ-YwFDhy2-X_QJxyAs-lk6p3B0icaiEBjU6_atpJHafY66b6sElsSM755NJORZFjGwdO8v85ewxN7vkoal4tDvWyThUrucS1fVOnFYo_Ey5u7oq770L_t5w9Wr5ualqsyrUaoWrmIdZG7lF_yYOfHb8UmnOVCd4EHDlCHejjBLDUE5zM6Ds3g9w85oFAH.cL8xJiluV4VRcqD2tsOIXKgpvI7UfN_fbvREgPpiP_r0T0JTBfS_vH2cnrq50d-kogWBjyZLE_OMINhFqo8dIw',
      takt:  'Empfehlung: wöchentlich (montags) übernehmen; in der Schlussspurt-Woche ab 3. August täglich.'
    }
  };

  var SB  = 'https://dagcsnfrlbpxcmdimnrw.supabase.co';
  var KEY = 'sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY';
  var REFRESH = 60000;

  var STREAMS = [
    { key:'wos.de.papier',  produkt:'wos', sprache:'de', format:'papier',  name:'Deutsch · Papier',  panel:'wos' },
    { key:'wos.de.digital', produkt:'wos', sprache:'de', format:'digital', name:'Deutsch · Digital', panel:'wos' },
    { key:'wos.en.digital', produkt:'wos', sprache:'en', format:'digital', name:'Englisch · Digital', panel:'wos' },
    { key:'gtv.de',         produkt:'gtv', sprache:'de', format:'stream',  name:'Deutsch',  panel:'gtv' },
    { key:'gtv.en',         produkt:'gtv', sprache:'en', format:'stream',  name:'Englisch', panel:'gtv' }
  ];

  function fmt(n){ return (Number(n)||0).toLocaleString('de-CH'); }
  function geld(n){ return CONFIG.waehrung + ' ' + Math.round(Number(n)||0).toLocaleString('de-CH'); }
  function el(id){ return document.getElementById(id); }
  function dmy(d){ return d.toLocaleDateString('de-CH',{day:'numeric',month:'long'}); }

  function rpc(name){
    return fetch(SB + '/rest/v1/rpc/' + name, {
      method:'POST',
      headers:{ 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
      body:'{}'
    }).then(function(r){ if(!r.ok) throw new Error(name + ' ' + r.status); return r.json(); });
  }

  function setStatus(state, when){
    var s = el('status');
    if (!s) return;
    if(state === 'ok'){ s.className = 'status readout'; s.textContent = '· Stand ' + when.toLocaleTimeString('de-CH',{hour:'2-digit',minute:'2-digit'}); }
    else if(state === 'err'){ s.className = 'status err'; s.textContent = '· nicht ladbar'; }
    else { s.className = 'status readout'; s.textContent = 'lädt …'; }
  }

  // ── Deadline-Meter ─────────────────────────────────────────────────────────
  function renderDeadline(){
    if (!el('ddBar')) return;
    var start = new Date(CONFIG.start + 'T00:00:00');
    var ende  = new Date(CONFIG.ende  + 'T23:59:59');
    var now   = new Date();
    var pct = Math.max(0, Math.min(100, (now - start) / (ende - start) * 100));
    el('ddBar').style.width = pct.toFixed(1) + '%';
    var days = Math.max(0, Math.ceil((ende - now) / 86400000));
    el('ddText').textContent = days > 0 ? ('noch ' + days + ' Tage') : 'Aktion beendet';
    el('ddStart').textContent = dmy(start);
  }

  // ── Aggregation aus sommer2026_stats() ─────────────────────────────────────
  function streamValue(rows, s){
    return rows.reduce(function(sum, r){
      if(r.produkt === s.produkt && r.sprache === s.sprache && r.format === s.format) return sum + Number(r.n);
      return sum;
    }, 0);
  }

  function renderStreams(rows){
    if (!el('wosStreams')) return;
    ['wos','gtv'].forEach(function(panel){
      var host = el(panel === 'wos' ? 'wosStreams' : 'gtvStreams');
      host.innerHTML = '';
      STREAMS.filter(function(s){ return s.panel === panel; }).forEach(function(s){
        var val = streamValue(rows, s);
        var ziel = CONFIG.ziele[s.key] || 0;
        var pct = ziel > 0 ? Math.min(100, Math.round(val / ziel * 100)) : 0;
        var row = document.createElement('div'); row.className = 'stream';
        row.innerHTML =
          '<div class="top2"><span class="name"></span>' +
          '<span class="val"><b></b> <span class="g"></span></span></div>' +
          '<div class="track"><span></span><i class="tick" style="left:100%"></i></div>';
        row.querySelector('.name').textContent = s.name;
        row.querySelector('.val b').textContent = fmt(val);
        row.querySelector('.val .g').textContent = ziel ? ('/ ' + fmt(ziel)) : '';
        row.querySelector('.track > span').style.width = Math.max(3, pct) + '%';
        host.appendChild(row);
      });
    });
  }

  // ── Woher (Attribution) ────────────────────────────────────────────────────
  function renderKanaele(kanaele, total){
    if (!el('kanalBars')) return;
    var host = el('kanalBars'); host.innerHTML = '';
    var byKanal = {}; kanaele.forEach(function(r){ byKanal[r.kanal] = Number(r.n); });
    var items = CONFIG.kanaele.map(function(k){ return { label:k.label, rolle:k.rolle, n:byKanal[k.key] || 0 }; })
                              .filter(function(x){ return x.n > 0; })
                              .sort(function(a, b){ return b.n - a.n; });
    if(!items.length){ host.innerHTML = '<div class="empty">Noch keine Anmeldungen.</div>'; return; }
    var max = items.reduce(function(m, x){ return Math.max(m, x.n); }, 0) || 1;
    items.forEach(function(x){
      var anteil = total > 0 ? Math.round(x.n / total * 100) : 0;
      var row = document.createElement('div'); row.className = 'stream';
      row.innerHTML = '<div class="top2"><span class="name"></span>' +
        '<span class="val"><b></b> <span class="g"></span></span></div>' +
        '<div class="track"><span></span></div>';
      row.querySelector('.name').textContent = x.label;
      if(x.rolle){
        var r = document.createElement('span'); r.className = 'kanal-rolle';
        r.textContent = x.rolle; row.querySelector('.name').appendChild(r);
      }
      row.querySelector('.val b').textContent = fmt(x.n);
      row.querySelector('.val .g').textContent = anteil + ' %';
      row.querySelector('.track > span').style.width = Math.max(3, Math.round(x.n / max * 100)) + '%';
      host.appendChild(row);
    });
    // «ohne UTM» einordnen: kein eigener Kanal, sondern Anmeldungen ohne UTM-Spur.
    // Seit 18.7. liefern beide Wege die Spur (goetheanum.tv über das
    // user_created-Event mit utm_params, Paperform über Felder + device.utm);
    // übrig bleiben Direktbesucher ohne Parameter und der nicht mehr
    // rekonstruierbare Rest des Altbestands vor dem 18.7.
    var ohneSpur = byKanal['andere'] || 0;
    if (ohneSpur > 0){
      var note = document.createElement('div'); note.className = 'fnote';
      note.textContent = '«ohne UTM» = ' + fmt(ohneSpur) + ' Anmeldungen, die ohne UTM-Parameter ankamen: ' +
        'Direktbesuche ohne Link-Parameter und ein Teil des Altbestands vor dem 18. Juli ' +
        '(seit dem 18.7. liefern Wochenschrift-Formulare UND goetheanum.tv die Spur automatisch). ' +
        'Die Einzel-Ereignisse stehen unter Momentum → «Was ist passiert?», dort auch die vermutete Herkunft.';
      host.appendChild(note);
    }
  }

  // ── Wirkungskette: Reichweite → Klicks → Abschlüsse → Geblieben ─────────────
  // Alle vier Stufen sind GEMESSENE Zahlen, nicht die im Eintrag gewählte Aufgabe:
  // Reichweite/Klicks summiert aus den Aktivitäten, Abschlüsse/Geblieben live aus
  // den Anmeldungen. Darum tragen Kanäle mit Reichweite direkt hier bei.
  var TRICHTER = {
    sichtbarkeit: { name:'Reichweite', frage:'Menschen erreicht',   cls:'s1' },
    aktivierung:  { name:'Klicks',     frage:'haben geklickt',       cls:'s2' },
    wirkung:      { name:'Abschlüsse', frage:'Abo gestartet',        cls:'s3' },
    bindung:      { name:'Geblieben',  frage:'nach 3 Monaten dabei', cls:'s4' }
  };
  function renderFunnel(trichter, massnahmen){
    if (!el('funnel')) return;
    var host = el('funnel'); host.innerHTML = '';
    var vals = {}; (trichter || []).forEach(function(r){ vals[r.stufe] = Number(r.wert) || 0; });
    var order = ['sichtbarkeit','aktivierung','wirkung','bindung'];
    var max = order.reduce(function(m, s){ return Math.max(m, vals[s] || 0); }, 0) || 1;
    // Umwandlung je Stufe gegen die vorige gemessene Grösse (Klickrate, Abschlussrate, Bleibequote).
    var rate = { aktivierung: vals.sichtbarkeit > 0 ? vals.aktivierung / vals.sichtbarkeit : null,
                 wirkung:     vals.aktivierung  > 0 ? vals.wirkung / vals.aktivierung   : null,
                 bindung:     vals.wirkung      > 0 ? vals.bindung / vals.wirkung       : null };
    order.forEach(function(s){
      var meta = TRICHTER[s]; var v = vals[s] || 0;
      var lvl = document.createElement('div'); lvl.className = 'lvl';
      lvl.innerHTML = '<div class="l2"><span class="fname"></span><span class="fval"></span></div>' +
        '<div class="ftrack ' + meta.cls + '"><span></span></div>';
      var nm = lvl.querySelector('.fname'); nm.textContent = meta.name;
      var rr = document.createElement('span'); rr.className = 'r'; rr.textContent = meta.frage; nm.appendChild(rr);
      var vtxt = fmt(v);
      if (rate[s] != null) vtxt += '  ·  ' + Math.round(rate[s] * 100) + ' %';
      lvl.querySelector('.fval').textContent = vtxt;
      lvl.querySelector('.ftrack > span').style.width = Math.max(3, Math.round(v / max * 100)) + '%';
      host.appendChild(lvl);
    });
    // Reichweite je Kanal – aus den Aktivitäten summiert (Social, Newsletter, …).
    // Neben der Summe je Kanal auch die einzelnen Aktivitäten sammeln, damit der
    // Balken zu einer Liste der Quellen aufklappt (Herkunft der Reichweite prüfbar).
    var reach = {}, klick = {}, quellen = {};
    (massnahmen || []).forEach(function(m){
      var r = Number(m.reichweite) || 0, k = Number(m.klicks) || 0, kn = m.kanal || 'andere';
      if (r) reach[kn] = (reach[kn] || 0) + r;
      if (k) klick[kn] = (klick[kn] || 0) + k;
      if (r || k) (quellen[kn] = quellen[kn] || []).push({ name:m.massnahme || '—', tag:m.tag, reichweite:r, klicks:k });
    });
    var kanalItems = Object.keys(reach).map(function(kn){ return { kanal:kn, reach:reach[kn], klick:klick[kn] || 0 }; })
                                       .sort(function(a, b){ return b.reach - a.reach; });
    if (kanalItems.length){
      var kmax = kanalItems.reduce(function(m, x){ return Math.max(m, x.reach); }, 0) || 1;
      var box = document.createElement('div'); box.className = 'reach-kanal';
      var head = document.createElement('div'); head.className = 'rk-h'; head.textContent = 'Reichweite je Kanal';
      box.appendChild(head);
      kanalItems.forEach(function(x){
        // Jeder Kanal-Balken ist aufklappbar (details/summary) und listet darunter
        // die einzelnen Quellen (Aktivitäten), die die Reichweite ausmachen.
        var det = document.createElement('details'); det.className = 'reach-detail';
        var sum = document.createElement('summary');
        var row = document.createElement('div'); row.className = 'stream';
        row.innerHTML = '<div class="top2"><span class="name"></span>' +
          '<span class="val"><b></b> <span class="g"></span></span></div>' +
          '<div class="track"><span></span></div>';
        var qs = (quellen[x.kanal] || []).slice().sort(function(a, b){ return b.reichweite - a.reichweite; });
        row.querySelector('.name').textContent = KANAL_LABEL[x.kanal] || x.kanal;
        var caret = document.createElement('span'); caret.className = 'rk-caret'; caret.setAttribute('aria-hidden', 'true');
        row.querySelector('.name').appendChild(caret);
        row.querySelector('.val b').textContent = fmt(x.reach);
        var g = x.klick ? (fmt(x.klick) + ' Klicks') : '';
        if (qs.length) g += (g ? ' · ' : '') + qs.length + (qs.length === 1 ? ' Quelle' : ' Quellen');
        row.querySelector('.val .g').textContent = g;
        row.querySelector('.track > span').style.width = Math.max(3, Math.round(x.reach / kmax * 100)) + '%';
        sum.appendChild(row); det.appendChild(sum);

        var list = document.createElement('div'); list.className = 'quellen';
        qs.forEach(function(q){
          var qr = document.createElement('div'); qr.className = 'motrow';
          var mc = document.createElement('span'); mc.className = 'mc'; mc.textContent = q.name;
          if (q.tag){ var ms = document.createElement('span'); ms.className = 'ms';
            ms.textContent = new Date(q.tag + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' });
            mc.appendChild(ms); }
          var mn = document.createElement('span'); mn.className = 'mn';
          mn.textContent = fmt(q.reichweite) + (q.klicks ? (' · ' + fmt(q.klicks) + ' Klicks') : '');
          qr.appendChild(mc); qr.appendChild(mn); list.appendChild(qr);
        });
        if (!qs.length){
          var leer = document.createElement('div'); leer.className = 'qz-hint';
          leer.textContent = 'Keine Einzel-Quellen erfasst.'; list.appendChild(leer);
        }
        // Social: die externe Quelle (Metricool) direkt aus der Liste verlinken.
        if (x.kanal === 'social' && CONFIG.quelleSocial){
          var qlink = document.createElement('div'); qlink.className = 'qz-hint';
          qlink.appendChild(document.createTextNode('Quelle der Zahlen: '));
          var qa = document.createElement('a'); qa.href = CONFIG.quelleSocial.url;
          qa.target = '_blank'; qa.rel = 'noopener'; qa.textContent = CONFIG.quelleSocial.label;
          qlink.appendChild(qa); list.appendChild(qlink);
        }
        det.appendChild(list);
        box.appendChild(det);
      });
      host.appendChild(box);
    }
    var note = document.createElement('div'); note.className = 'fnote';
    note.textContent = 'Reichweite kommt aus den Aktivitäten (je Eintrag erfassen). Klicks = erfasste Aktivitäts-Klicks plus die automatisch gezählten Kurzlink-Klicks aller Kampagnen-Links; dieselben Klicks nicht zusätzlich von Hand eintragen, sonst zählen sie doppelt. Abschlüsse und Geblieben zählt das Cockpit live aus den Anmeldungen.';
    host.appendChild(note);
  }

  // ── Quelle der Social-Media-Zahlen (Metricool) ─────────────────────────────
  // Reichweite und Klicks der Social-Kanäle liegen nicht im Backend, sondern in
  // Metricool. Der Block nennt die Quelle mit Link und den Übernahme-Takt; die
  // Zahlen selbst trägt man je Aktivität ein (Reichweite/Klicks). Element-gewächtert,
  // erscheint also nur auf Seiten mit einem #quelleSocial-Container.
  function renderQuelleSocial(){
    var host = el('quelleSocial'); if (!host) return;
    var q = CONFIG.quelleSocial; if (!q) return;
    host.innerHTML = '';
    var row = document.createElement('div'); row.className = 'landing';
    var lab = document.createElement('span'); lab.className = 'meta';
    lab.textContent = 'Quelle · Social-Media-Zahlen';
    var a = document.createElement('a'); a.className = 'btn';
    a.href = q.url; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = q.label;
    row.appendChild(lab); row.appendChild(a);
    var note = document.createElement('p'); note.className = 'provisorisch';
    note.textContent = 'Reichweite und Klicks der Social-Media-Kanäle kommen aus Metricool. ' +
      q.takt + ' Ein automatischer Abruf ist nicht möglich – die abgelesenen Zahlen je Aktivität eintragen.';
    host.appendChild(row); host.appendChild(note);
  }

  // ── Attribution nach Motiv (utm_content) ───────────────────────────────────
  function renderMotive(attribution){
    if (!el('motive')) return;
    var items = (attribution || []).filter(function(r){ return r.utm_content || r.utm_campaign || r.utm_source; })
      .map(function(r){
        var label = r.utm_content || r.utm_campaign || r.utm_source;
        var quelle = [r.utm_source, r.utm_medium].filter(Boolean).join(' · ');
        return { label:label, quelle:quelle, n:Number(r.n) || 0 };
      })
      .sort(function(a, b){ return b.n - a.n; }).slice(0, 12);
    var wrap = el('motive'), list = el('motiveList');
    if(!items.length){ wrap.hidden = true; return; }
    wrap.hidden = false; list.innerHTML = '';
    items.forEach(function(x){
      var row = document.createElement('div'); row.className = 'motrow';
      row.innerHTML = '<span class="mc"></span><span class="mn"></span>';
      var mc = row.querySelector('.mc'); mc.textContent = x.label;
      if(x.quelle){ var s = document.createElement('span'); s.className = 'ms'; s.textContent = x.quelle; mc.appendChild(s); }
      row.querySelector('.mn').textContent = fmt(x.n);
      list.appendChild(row);
    });
  }

  // ── Aktivitäten-Protokoll ───────────────────────────────────────────────────
  var KANAL_LABEL = { newsletter:'Newsletter', mailer:'Mailing', flyer:'Flyer/Stand', social:'Social Media', popup:'Popup', website:'Website', empfehlung:'Empfehlung', andere:'Andere' };
  // ── Zeitband: Phasen × Wochen × Kanäle ─────────────────────────────────────
  // Phasen der Aktion (anpassbar): Auftakt → Verdichtung → Schlussspurt.
  var PHASEN = [
    { name: 'Auftakt',       von: '2026-06-29', bis: '2026-07-19' },
    { name: 'Verdichtung',   von: '2026-07-20', bis: '2026-08-02' },
    { name: 'Schlussspurt',  von: '2026-08-03', bis: '2026-08-08' }
  ];
  var ZB_KANAELE = [
    ['social', 'Social'], ['newsletter', 'Newsletter'], ['mailer', 'Mailing/Post'], ['flyer', 'Flyer/Stand'],
    ['popup', 'Popup'], ['website', 'Website'], ['empfehlung', 'Empfehlung'], ['andere', 'Anderes']
  ];

  function zbWochen(){
    // Montagsraster über den Aktionszeitraum.
    var start = new Date(CONFIG.start + 'T00:00:00');
    var ende  = new Date(CONFIG.ende  + 'T00:00:00');
    var mo = new Date(start); mo.setDate(mo.getDate() - ((mo.getDay() + 6) % 7));
    var wochen = [];
    while (mo <= ende){
      var so = new Date(mo); so.setDate(so.getDate() + 6);
      wochen.push({ von: new Date(mo), bis: so });
      mo = new Date(mo); mo.setDate(mo.getDate() + 7);
    }
    return wochen;
  }
  function zbTag(d){ return d.getDate() + '.' + (d.getMonth() + 1) + '.'; }

  // Zeitband-Chips sind kompakt (Punkt · Tag · Titel einzeilig) – Antippen klappt
  // die Felder auf (Kürzel, Reichweite, Klicks, Kosten, Notiz + Bearbeiten-Knopf).
  // Delegation über die Tabelle; die Zeilen-Zuordnung liegt in zbById (je Render neu).
  // zbOffen merkt sich aufgeklappte Chips über die 60-Sekunden-Neu-Renderings hinweg.
  var zbById = {}, zbWired = false, zbOffen = {};

  function renderZeitband(rows){
    if (!el('zeitband')) return;
    var tbl = el('zeitband'); if(!tbl) return;
    var wochen = zbWochen();
    var heute = new Date(); heute.setHours(0,0,0,0);

    // Kopf 1: Phasen (Zellen je Woche, gleiche Phase = zusammenhängende Färbung)
    var h1 = '<tr class="ph"><th></th>';
    var i, w, ph;
    var phasenJeWoche = wochen.map(function(wo){
      var mitte = new Date(wo.von); mitte.setDate(mitte.getDate() + 3);
      for (var p = 0; p < PHASEN.length; p++){
        if (mitte >= new Date(PHASEN[p].von + 'T00:00:00') && mitte <= new Date(PHASEN[p].bis + 'T23:59:59')) return PHASEN[p].name;
      }
      return '';
    });
    i = 0;
    while (i < phasenJeWoche.length){
      var span = 1;
      while (i + span < phasenJeWoche.length && phasenJeWoche[i + span] === phasenJeWoche[i]) span++;
      h1 += '<th colspan="' + span + '">' + (phasenJeWoche[i] || '·') + '</th>';
      i += span;
    }
    h1 += '</tr>';

    // Kopf 2: Wochen (heutige Woche markiert)
    var h2 = '<tr class="wk"><th>Kanal</th>';
    for (i = 0; i < wochen.length; i++){
      w = wochen[i];
      var istHeute = heute >= w.von && heute <= w.bis;
      h2 += '<th' + (istHeute ? ' class="heute"' : '') + '>' + zbTag(w.von) + '–' + zbTag(w.bis) + '</th>';
    }
    h2 += '</tr>';

    // Zeilen: je Kanal, Chips je Woche
    var body = '';
    ZB_KANAELE.forEach(function(k){
      var zeile = '<tr><td class="kz">' + k[1] + '</td>';
      for (var wi = 0; wi < wochen.length; wi++){
        var von = wochen[wi].von, bis = wochen[wi].bis;
        var chips = '';
        (rows || []).forEach(function(m){
          if ((m.kanal || 'andere') !== k[0] || !m.tag) return;
          var d = new Date(m.tag + 'T00:00:00');
          if (d < von || d > bis) return;
          var det = [];
          if (m.ersteller) det.push(['Kürzel', m.ersteller]);
          if (m.reichweite) det.push(['Reichweite', Number(m.reichweite).toLocaleString('de-CH')]);
          if (m.klicks) det.push(['Klicks', Number(m.klicks).toLocaleString('de-CH')]);
          if (m.kosten) det.push(['Kosten', Number(m.kosten).toLocaleString('de-CH')]);
          if (m.notiz) det.push(['Notiz', m.notiz]);
          zbById[m.id] = m;
          var istOffen = !!zbOffen[m.id];
          var span = document.createElement('span');
          span.className = 'zb-chip clickable' + (istOffen ? ' open' : '') + (m.notiz ? ' has-note' : '');
          span.setAttribute('data-mid', m.id);
          span.setAttribute('role', 'button');
          span.setAttribute('tabindex', '0');
          span.setAttribute('aria-expanded', istOffen ? 'true' : 'false');
          span.title = m.massnahme + (det.length ? ' – ' + det.map(function(p){ return p[0] + ' ' + p[1]; }).join(' · ') : '') + ' · antippen zum Ausklappen';
          var kopf = document.createElement('span'); kopf.className = 'zk';
          kopf.innerHTML = '<span class="zr"></span><span class="zt">' + zbTag(d) + '</span>';
          var zm = document.createElement('span'); zm.className = 'zm'; zm.textContent = m.massnahme;
          kopf.appendChild(zm);
          span.appendChild(kopf);
          var box = document.createElement('span'); box.className = 'zb-det';
          det.forEach(function(p){
            var zd = document.createElement('span'); zd.className = 'zd' + (p[0] === 'Notiz' ? ' zd-note' : '');
            var l = document.createElement('span'); l.className = 'zdl'; l.textContent = p[0];
            var v = document.createElement('span'); v.className = 'zdv'; v.textContent = p[1];
            zd.appendChild(l); zd.appendChild(v); box.appendChild(zd);
          });
          var eb = document.createElement('button'); eb.type = 'button'; eb.className = 'zb-edit';
          eb.setAttribute('data-mid', m.id); eb.textContent = 'Bearbeiten';
          box.appendChild(eb);
          span.appendChild(box);
          chips += span.outerHTML;
        });
        zeile += '<td>' + chips + '</td>';
      }
      body += zeile + '</tr>';
    });

    tbl.innerHTML = '<thead>' + h1 + h2 + '</thead><tbody>' + body + '</tbody>';
    // Delegierter Klick/Tastatur: Chip klappt die Felder auf/zu, der Bearbeiten-Knopf
    // im aufgeklappten Chip lädt die Aktivität in die Maske.
    if (!zbWired){
      zbWired = true;
      var kippe = function(c){
        var offen = c.classList.toggle('open');
        c.setAttribute('aria-expanded', offen ? 'true' : 'false');
        var id = c.getAttribute('data-mid');
        if (offen) zbOffen[id] = true; else delete zbOffen[id];
      };
      tbl.addEventListener('click', function(e){
        var b = e.target.closest && e.target.closest('.zb-edit[data-mid]');
        if (b){ var m = zbById[b.getAttribute('data-mid')]; if (m) massnahmeBearbeiten(m); return; }
        var c = e.target.closest && e.target.closest('.zb-chip[data-mid]');
        if (c) kippe(c);
      });
      tbl.addEventListener('keydown', function(e){
        if (e.key !== 'Enter' && e.key !== ' ') return;
        if (e.target.closest && e.target.closest('.zb-edit')) return; // Knopf reagiert selbst
        var c = e.target.closest && e.target.closest('.zb-chip[data-mid]');
        if (c){ e.preventDefault(); kippe(c); }
      });
    }
    el('zbLegende').innerHTML = '<span>Zeilen = Kanal, Spalten = Woche. Jeder Punkt eine Aktivität – antippen klappt Reichweite, Klicks, Kosten und Notiz auf; Bearbeiten dort.</span>';
  }

  // Eintragen/Bearbeiten: offener Schreibweg (Muster Link-Register),
  // erscheint sofort überall. Bearbeiten lädt die Zeile über den Knopf im Protokoll.
  if (el('mfTag')) el('mfTag').value = new Date().toISOString().slice(0, 10);
  if (el('mfBtn')) el('mfBtn').addEventListener('click', function(){
    var sagen = function(msg, bad){ var s = el('mfSaid'); s.textContent = msg; s.style.color = bad ? 'var(--bad)' : 'var(--ok)'; };
    var titel = (el('mfTitel').value || '').trim();
    var wer = (el('mfWer').value || '').trim();
    if (!el('mfTag').value || !titel || !wer){ sagen('Datum, Aktivität und Kürzel sind Pflicht.', true); return; }
    var zahl = function(id){ var e = el(id); return (e && e.value !== '') ? Math.max(0, Math.round(Number(e.value) || 0)) : null; };
    var istEdit = mfEditId != null;
    var notiz = el('mfNotiz') ? (el('mfNotiz').value || '').trim() : '';
    var params = {
      p_tag: el('mfTag').value, p_massnahme: titel,
      p_kanal: el('mfKanal').value, p_rolle: null,
      p_ersteller: wer, p_kosten: null,
      p_reichweite: zahl('mfReichweite'), p_klicks: zahl('mfKlicks'),
      p_notiz: notiz || null
    };
    if (istEdit) { params.p_id = mfEditId; } else { params.p_zielgruppe = null; }
    fetch(SB + '/rest/v1/rpc/' + (istEdit ? 'sommer2026_massnahme_aendern' : 'sommer2026_massnahme_eintragen'), {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
      body: JSON.stringify(params)
    }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(ergebnis){
        if (ergebnis === 'ok'){
          sagen(istEdit ? 'Geändert.' : 'Eingetragen – erscheint im Zeitband, im Protokoll und in der Reichweite.');
          mfZuruecksetzen();
          // Reichweite/Klicks fliessen in die Wirkungskette – darum Zeitband, Protokoll UND Trichter neu laden.
          Promise.all([rpc('sommer2026_massnahmen_public'), rpc('sommer2026_trichter')])
            .then(function(res){ var rows = res[0] || []; renderZeitband(rows); renderMassnahmen(rows); renderFunnel(res[1] || [], rows); })
            .catch(function(){});
        } else { sagen('Datum und Aktivität prüfen.', true); }
      })
      .catch(function(){ sagen(istEdit ? 'Ändern nicht erreichbar.' : 'Eintragen nicht erreichbar.', true); });
  });

  function renderMassnahmen(rows){
    if (!el('massnahmenBody')) return;
    var body = el('massnahmenBody'); body.innerHTML = '';
    if(!rows || !rows.length){
      body.innerHTML = '<tr><td class="empty" colspan="7">Noch keine Aktivitäten erfasst – das Protokoll wird gepflegt, sobald die Aktionen laufen.</td></tr>';
      return;
    }
    rows.forEach(function(r){
      var tag = r.tag ? new Date(r.tag + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' }) : '–';
      var kanal = KANAL_LABEL[r.kanal] || r.kanal || '';
      var tr = document.createElement('tr');
      tr.innerHTML = '<td></td><td></td><td></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="act"></td>';
      tr.children[0].textContent = tag;
      tr.children[1].textContent = (r.massnahme || '') + (r.ersteller ? ' · ' + r.ersteller : '');
      if (r.notiz){ var nn = document.createElement('span'); nn.className = 'mnote'; nn.textContent = r.notiz; tr.children[1].appendChild(nn); }
      tr.children[2].textContent = kanal;
      tr.children[3].textContent = (r.kosten != null) ? geld(r.kosten) : '–';
      tr.children[4].textContent = (r.reichweite != null) ? fmt(r.reichweite) : '–';
      tr.children[5].textContent = (r.klicks != null) ? fmt(r.klicks) : '–';
      var edit = document.createElement('button');
      edit.type = 'button'; edit.className = 'medit'; edit.textContent = 'Bearbeiten';
      edit.addEventListener('click', function(){ massnahmeBearbeiten(r); });
      tr.children[6].appendChild(edit);
      body.appendChild(tr);
    });
  }

  // Bearbeiten: Zeile in die Maske laden; Speichern übernimmt auch nachgetragene
  // Reichweite und Klicks (Kosten bleiben dem Kosten-Modul vorbehalten).
  var mfEditId = null;
  function massnahmeBearbeiten(r){
    mfEditId = r.id;
    var d = el('mfForm'); if (d) d.open = true;
    el('mfTag').value = r.tag || '';
    el('mfTitel').value = r.massnahme || '';
    el('mfKanal').value = r.kanal || 'andere';
    if (el('mfReichweite')) el('mfReichweite').value = (r.reichweite != null) ? r.reichweite : '';
    if (el('mfKlicks')) el('mfKlicks').value = (r.klicks != null) ? r.klicks : '';
    if (el('mfNotiz')) el('mfNotiz').value = r.notiz || '';
    el('mfWer').value = r.ersteller || '';
    el('mfBtn').textContent = 'Änderung speichern';
    el('mfSaid').textContent = 'Bearbeitung von «' + (r.massnahme || '') + '» – Speichern übernimmt.';
    el('mfSaid').style.color = 'var(--muted)';
    d.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function mfZuruecksetzen(){
    mfEditId = null;
    el('mfTitel').value = ''; el('mfWer').value = '';
    if (el('mfReichweite')) el('mfReichweite').value = '';
    if (el('mfKlicks')) el('mfKlicks').value = '';
    if (el('mfNotiz')) el('mfNotiz').value = '';
    el('mfTag').value = new Date().toISOString().slice(0, 10);
    el('mfBtn').textContent = 'Eintragen';
  }

  // ── Multiplikatoren: Liste, Verlauf, Passwort-Schleier ─────────────────────
  var MU_ART = { anruf:'Anruf', mail:'Mail', treffen:'Treffen', andere:'Anderes' };
  var MU_STATUS = { offen:'offen', erreicht:'erreicht', zugesagt:'zugesagt', abgesagt:'abgesagt', spaeter:'später' };
  var muListe = [], muProto = [], muNamen = {}, muOffen = null;

  function muSag(msg, bad){ var s = el('muSaid'); if (!s) return; s.textContent = msg; s.style.color = bad ? 'var(--bad)' : 'var(--ok)'; }
  function muPwGespeichert(){ try { return sessionStorage.getItem('sommer26_multi_pw') || ''; } catch(e){ return ''; } }

  function muNamenLaden(pw, still){
    // Erst Passwort separat prüfen (funktioniert auch bei leerer Namensliste),
    // dann die Namen laden.
    return fetch(SB + '/rest/v1/rpc/sommer2026_multi_pw_ok', {
      method:'POST', headers:{ 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
      body: JSON.stringify({ p_passwort: pw })
    }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(ok){
        if (!ok){
          try { sessionStorage.removeItem('sommer26_multi_pw'); } catch(e){}
          if (!still) muSag('Passwort stimmt nicht.', true);
          return;
        }
        try { sessionStorage.setItem('sommer26_multi_pw', pw); } catch(e){}
        if (el('muNamenBtn')) el('muNamenBtn').textContent = 'Namen ausblenden';
        if (!still) muSag('Namen eingeblendet – nur in diesem Browser.');
        return fetch(SB + '/rest/v1/rpc/sommer2026_multi_namen', {
          method:'POST', headers:{ 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
          body: JSON.stringify({ p_passwort: pw })
        }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
          .then(function(rows){
            muNamen = {}; (rows || []).forEach(function(x){ muNamen[x.id] = x.name; });
            renderMultis();
          });
      }).catch(function(){ if (!still) muSag('Nicht erreichbar.', true); });
  }

  if (el('muNamenBtn')) el('muNamenBtn').addEventListener('click', function(){
    if (Object.keys(muNamen).length){
      muNamen = {}; try { sessionStorage.removeItem('sommer26_multi_pw'); } catch(e){}
      el('muNamenBtn').textContent = 'Namen einblenden';
      muSag('Namen ausgeblendet.');
      renderMultis(); return;
    }
    var pw = (window.prompt('Passwort für die Klarnamen:') || '').trim().toLowerCase();
    if (pw) muNamenLaden(pw, false);
  });

  function muDatum(d){ return d ? new Date(d + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' }) : '–'; }

  function renderMultis(){
    if (!el('muBody')) return;
    var body = el('muBody'); body.innerHTML = '';
    if (!muListe.length){
      body.innerHTML = '<tr><td class="empty" colspan="6">Noch keine Multiplikatoren erfasst – unten anlegen.</td></tr>';
      return;
    }
    muListe.forEach(function(m){
      var tr = document.createElement('tr');
      tr.innerHTML = '<td></td><td></td><td></td><td></td><td class="num"></td><td class="act"></td>';
      tr.children[0].textContent = muNamen[m.id] || m.alias;
      tr.children[1].textContent = m.rolle_funktion || '–';
      var letzter = muProto.filter(function(k){ return k.multiplikator_id === m.id; })[0];
      tr.children[2].textContent = m.letzter_tag ? (muDatum(m.letzter_tag) + (letzter ? ' · ' + letzter.wer : '')) : '–';
      var st = document.createElement('span');
      st.className = 'mstat ' + (m.letzter_status || '');
      st.textContent = MU_STATUS[m.letzter_status] || '–';
      tr.children[3].appendChild(st);
      tr.children[4].textContent = m.kontakte_n || 0;
      var btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'medit';
      btn.textContent = (muOffen === m.id) ? 'Schliessen' : 'Verlauf & Kontakt';
      btn.addEventListener('click', function(){ muOffen = (muOffen === m.id) ? null : m.id; renderMultis(); });
      tr.children[5].appendChild(btn);
      body.appendChild(tr);

      if (muOffen === m.id){
        var vr = document.createElement('tr'); vr.className = 'mv';
        var td = document.createElement('td'); td.colSpan = 6;
        var eintraege = muProto.filter(function(k){ return k.multiplikator_id === m.id; });
        if (!eintraege.length){
          var leer = document.createElement('p'); leer.className = 'empty'; leer.textContent = 'Noch kein Kontakt protokolliert.';
          td.appendChild(leer);
        }
        eintraege.forEach(function(k){
          var row = document.createElement('div'); row.className = 'mvrow';
          var meta = document.createElement('span'); meta.className = 'mvmeta';
          meta.textContent = muDatum(k.tag) + ' · ' + k.wer + ' · ' + (MU_ART[k.art] || k.art);
          var stx = document.createElement('span'); stx.className = 'mstat ' + (k.status || '');
          stx.textContent = MU_STATUS[k.status] || '';
          var erg = document.createElement('span'); erg.textContent = k.ergebnis || '';
          row.appendChild(meta); row.appendChild(stx); row.appendChild(erg);
          td.appendChild(row);
        });
        // Mini-Maske: Kontakt nachtragen
        var f = document.createElement('div'); f.className = 'mvform';
        function feld(labelText, elx){
          var l = document.createElement('label'); l.className = 'field';
          var s = document.createElement('span'); s.className = 'lab'; s.textContent = labelText;
          l.appendChild(s); l.appendChild(elx); return l;
        }
        var iTag = document.createElement('input'); iTag.type = 'date'; iTag.value = new Date().toISOString().slice(0, 10);
        var iWer = document.createElement('input'); iWer.type = 'text'; iWer.placeholder = 'z. B. pt'; iWer.autocomplete = 'off';
        var sArt = document.createElement('select');
        Object.keys(MU_ART).forEach(function(a){ var o = document.createElement('option'); o.value = a; o.textContent = MU_ART[a]; sArt.appendChild(o); });
        var sSt = document.createElement('select');
        Object.keys(MU_STATUS).forEach(function(a){ var o = document.createElement('option'); o.value = a; o.textContent = MU_STATUS[a]; sSt.appendChild(o); });
        var iErg = document.createElement('input'); iErg.type = 'text'; iErg.placeholder = 'Ergebnis – keine Klarnamen (offen sichtbar)';
        f.appendChild(feld('Datum', iTag)); f.appendChild(feld('Kürzel', iWer));
        f.appendChild(feld('Art', sArt)); f.appendChild(feld('Status', sSt));
        var ergWrap = feld('Ergebnis', iErg); ergWrap.className = 'field mvspan'; f.appendChild(ergWrap);
        var aktion = document.createElement('div'); aktion.className = 'mvspan';
        aktion.style.cssText = 'display:flex;gap:var(--s3);align-items:center;flex-wrap:wrap';
        var kBtn = document.createElement('button'); kBtn.type = 'button'; kBtn.className = 'btn primary'; kBtn.textContent = 'Kontakt nachtragen';
        var kSaid = document.createElement('span'); kSaid.className = 'said';
        aktion.appendChild(kBtn); aktion.appendChild(kSaid);
        f.appendChild(aktion);
        kBtn.addEventListener('click', function(){
          var wer = (iWer.value || '').trim();
          if (!iTag.value || !wer){ kSaid.textContent = 'Datum und Kürzel sind Pflicht.'; kSaid.style.color = 'var(--bad)'; return; }
          fetch(SB + '/rest/v1/rpc/sommer2026_multi_kontakt_anlegen', {
            method:'POST', headers:{ 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
            body: JSON.stringify({ p_multiplikator: m.id, p_tag: iTag.value, p_wer: wer, p_art: sArt.value, p_ergebnis: (iErg.value || '').trim() || null, p_status: sSt.value })
          }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
            .then(function(ergebnis){
              if (ergebnis === 'ok'){ muNeuLaden(); }
              else { kSaid.textContent = 'Angaben prüfen.'; kSaid.style.color = 'var(--bad)'; }
            })
            .catch(function(){ kSaid.textContent = 'Nicht erreichbar.'; kSaid.style.color = 'var(--bad)'; });
        });
        td.appendChild(f);
        vr.appendChild(td);
        body.appendChild(vr);
      }
    });
  }

  function muNeuLaden(){
    Promise.all([rpc('sommer2026_multi_liste'), rpc('sommer2026_multi_protokoll')])
      .then(function(res){ muListe = res[0] || []; muProto = res[1] || []; renderMultis(); })
      .catch(function(){});
  }

  if (el('muAnlegenBtn')) el('muAnlegenBtn').addEventListener('click', function(){
    var sag = function(msg, bad){ var s = el('muASaid'); s.textContent = msg; s.style.color = bad ? 'var(--bad)' : 'var(--ok)'; };
    var name = (el('muName').value || '').trim();
    var wer = (el('muWer').value || '').trim();
    if (!name || !wer){ sag('Name und Kürzel sind Pflicht.', true); return; }
    fetch(SB + '/rest/v1/rpc/sommer2026_multi_anlegen', {
      method:'POST', headers:{ 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
      body: JSON.stringify({ p_name: name, p_rolle: (el('muRolle').value || '').trim() || null, p_ersteller: wer })
    }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(ergebnis){
        if (ergebnis === 'ok'){
          sag('Angelegt – erscheint in der Liste als M-Nummer.');
          el('muName').value = ''; el('muRolle').value = '';
          muNeuLaden();
          if (muPwGespeichert()) muNamenLaden(muPwGespeichert(), true);
        } else { sag('Name und Kürzel prüfen.', true); }
      })
      .catch(function(){ sag('Anlegen nicht erreichbar.', true); });
  });

  // ── Kosten und Wirkung ─────────────────────────────────────────────────────
  var KAT_LABEL = { stunden:'Stunden intern', social:'Social Media', druck:'Druck & Versand', infrastruktur:'Infrastruktur', andere:'Andere' };
  var lastTotal = 0, lastRevenue = 0;
  function renderKosten(total, revenue, posten){
    if (!el('costTotal')) return;
    lastTotal = total; lastRevenue = revenue;
    posten = posten || [];
    var jeKat = {}; var summe = 0;
    posten.forEach(function(k){ var b = Number(k.betrag) || 0; summe += b; jeKat[k.kategorie] = (jeKat[k.kategorie] || 0) + b; });
    el('costTotal').textContent = geld(summe);
    el('costCpa').textContent   = (summe > 0 && total > 0) ? geld(summe / total) : '–';
    var revChf = revenue && revenue.chfGesamt || 0;
    el('costRoi').textContent   = summe > 0 ? (revChf / summe).toFixed(1) + '×' : '–';

    var body = el('costBody'); body.innerHTML = '';
    Object.keys(KAT_LABEL).forEach(function(kat){
      if (kat === 'andere' && !jeKat[kat]) return;
      var tr = document.createElement('tr');
      tr.innerHTML = '<td></td><td class="num"></td>';
      tr.children[0].textContent = KAT_LABEL[kat];
      tr.children[1].textContent = geld(jeKat[kat] || 0);
      body.appendChild(tr);
    });
    var foot = el('costFoot');
    foot.innerHTML = '<tr><td>Summe</td><td class="num"></td></tr>';
    foot.querySelector('tr').children[1].textContent = geld(summe);

    var pb = el('kostenPostenBody'); pb.innerHTML = '';
    if (!posten.length){
      pb.innerHTML = '<tr><td class="empty" colspan="4">Noch keine Einzelposten erfasst.</td></tr>';
    } else {
      posten.forEach(function(k){
        var tr = document.createElement('tr');
        tr.innerHTML = '<td></td><td></td><td></td><td class="num"></td>';
        tr.children[0].textContent = k.tag ? new Date(k.tag + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' }) : '–';
        tr.children[1].textContent = (k.posten || '') + (k.ersteller ? ' · ' + k.ersteller : '');
        tr.children[2].textContent = KAT_LABEL[k.kategorie] || k.kategorie || '';
        tr.children[3].textContent = geld(k.betrag);
        pb.appendChild(tr);
      });
    }
  }

  // Kosten eintragen: offener Schreibweg mit Pflicht-Kuerzel.
  if (el('kfTag')) el('kfTag').value = new Date().toISOString().slice(0, 10);
  if (el('kfBtn')) el('kfBtn').addEventListener('click', function(){
    var sagen = function(msg, bad){ var s = el('kfSaid'); s.textContent = msg; s.style.color = bad ? 'var(--bad)' : 'var(--ok)'; };
    var posten = (el('kfPosten').value || '').trim();
    var wer = (el('kfWer').value || '').trim();
    var betrag = el('kfBetrag').value;
    if (!el('kfTag').value || !posten || !wer || betrag === '' || Number(betrag) < 0){ sagen('Datum, Posten, Betrag und Kürzel sind Pflicht.', true); return; }
    fetch(SB + '/rest/v1/rpc/sommer2026_kosten_eintragen', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'apikey':KEY, 'Authorization':'Bearer ' + KEY },
      body: JSON.stringify({ p_tag: el('kfTag').value, p_posten: posten, p_kategorie: el('kfKategorie').value, p_betrag: Number(betrag), p_ersteller: wer })
    }).then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(ergebnis){
        if (ergebnis === 'ok'){
          sagen('Eingetragen – Summe, Kosten je Abo und Rückfluss sind aktualisiert.');
          el('kfPosten').value = ''; el('kfBetrag').value = '';
          rpc('sommer2026_kosten_public').then(function(rows){ renderKosten(lastTotal, lastRevenue, rows); }).catch(function(){});
        } else { sagen('Angaben prüfen.', true); }
      })
      .catch(function(){ sagen('Eintragen nicht erreichbar.', true); });
  });

  // ── Tarif-Tabelle ──────────────────────────────────────────────────────────
  function renderTarif(rows){
    if (!el('tarifBody')) return;
    function cell(produkt, tarif, intervall){
      return rows.reduce(function(sum, r){
        if(r.produkt === produkt && r.tarif === tarif && r.intervall === intervall) return sum + Number(r.n);
        return sum;
      }, 0);
    }
    var body = el('tarifBody'); body.innerHTML = '';
    var colM = 0, colJ = 0;
    [['wos','Wochenschrift'], ['gtv','goetheanum.tv']].forEach(function(p){
      var hr = document.createElement('tr'); hr.className = 'prod-h';
      hr.innerHTML = '<td colspan="4"></td>'; hr.querySelector('td').textContent = p[1];
      body.appendChild(hr);
      [['standard','Standard'], ['ermaessigt','Ermässigt']].forEach(function(t){
        var m = cell(p[0], t[0], 'monatlich'), j = cell(p[0], t[0], 'jaehrlich');
        colM += m; colJ += j;
        var tr = document.createElement('tr');
        tr.innerHTML = '<td></td><td class="num"></td><td class="num"></td><td class="num"></td>';
        tr.children[0].textContent = t[1];
        tr.children[1].textContent = fmt(m);
        tr.children[2].textContent = fmt(j);
        tr.children[3].textContent = fmt(m + j);
        body.appendChild(tr);
      });
    });
    var foot = el('tarifFoot');
    foot.innerHTML = '<tr><td>Summe</td><td class="num"></td><td class="num"></td><td class="num"></td></tr>';
    foot.querySelector('tr').children[1].textContent = fmt(colM);
    foot.querySelector('tr').children[2].textContent = fmt(colJ);
    foot.querySelector('tr').children[3].textContent = fmt(colM + colJ);
  }

  // ── Umsatz-Projektion (Folgejahr) ──────────────────────────────────────────
  // Rechnet je Zahlungswährung getrennt (CHF- und EUR-Zahler zum je echten
  // Preis) und liefert zusätzlich die CHF-Gesamtsumme (EUR über CONFIG.eurChf).
  // goetheanum.tv rechnet ausschliesslich in EUR – Zeilen ohne Währungsangabe
  // fallen darum auf EUR. Preis-Lookup: Währung → Produkt → Format → Tarif
  // (ermässigt hat im Shop keinen eigenen Preis → Fallback Standard).
  function projectRevenue(rows){
    var summe = { chf: 0, eur: 0 };
    rows.forEach(function(r){
      var w = r.waehrung === 'chf' ? 'chf' : 'eur';
      var jeFormat = ((CONFIG.preise[w] || {})[r.produkt] || {})[r.format] || {};
      var jeTarif = jeFormat[r.tarif] || jeFormat.standard || {};
      var preis = jeTarif[r.intervall];
      if(!preis) return;
      var jahr = r.intervall === 'monatlich' ? preis * 12 : preis;
      var bleibend;
      if(r.status === 'bleibt') bleibend = Number(r.n);
      else if(r.status === 'neu' || r.status === 'laeuft-aus') bleibend = Number(r.n) * CONFIG.bleibeQuote;
      else bleibend = 0;                     // gekuendigt zählt nicht
      summe[w] += bleibend * jahr;
    });
    summe.chfGesamt = summe.chf + summe.eur * CONFIG.eurChf;
    return summe;
  }

  // ── Kacheln, Meilensteine ──────────────────────────────────────────────────
  function renderTiles(total, avg, avgDays){
    if (!el('total')) return;
    el('total').textContent = fmt(total);
    el('kTotal').textContent = fmt(total);
    el('kAvg').textContent = fmt(avg);
    el('kAvgSub').textContent = 'letzte ' + avgDays + ' Tage';
    var ziel = CONFIG.zielGesamt || STREAMS.reduce(function(s, x){ return s + (CONFIG.ziele[x.key] || 0); }, 0);
    var goalPct = ziel > 0 ? Math.round(total / ziel * 100) : 0;
    el('kGoal').innerHTML = goalPct + '<span class="u"> %</span>';
    el('kGoalSub').textContent = fmt(total) + ' von ' + fmt(ziel) + ' · Ziel 8. August';
  }

  // ── Attributions-Gesundheit: Anteil der Anmeldungen mit UTM-Spur ───────────
  // Aus den Kanal-Buckets gerechnet: alles ausser «andere» (= ohne UTM) hat
  // eine Spur. Die Kachel macht sichtbar, ob die Attributions-Arbeit greift.
  function renderSpurTile(kanaele, total){
    if (!el('kSpur')) return;
    var ohne = 0;
    (kanaele || []).forEach(function(r){ if (r.kanal === 'andere') ohne += Number(r.n) || 0; });
    var mit = Math.max(0, total - ohne);
    var pct = total > 0 ? Math.round(mit / total * 100) : 0;
    el('kSpur').innerHTML = pct + '<span class="u"> %</span>';
    el('kSpurSub').textContent = fmt(mit) + ' von ' + fmt(total) + ' Anmeldungen · Rest ohne UTM';
  }

  function renderMilestones(total){
    if (!el('msLine')) return;
    // Meilenstein als eine Zeile in der Held-Gruppe (statt eigener Sektion).
    var ms = CONFIG.meilensteine;
    var next = ms.find(function(m){ return m > total; }) || ms[ms.length - 1];
    var rest = Math.max(0, next - total);
    el('msLine').textContent = rest > 0 ? (fmt(next) + ' Abos · noch ' + fmt(rest)) : ('alle erreicht – ' + fmt(total));
  }

  // ── Wer bleibt? (jüngste Kohorte) ──────────────────────────────────────────
  function renderCohort(kohorten, revenue){
    if (!el('cohortCard')) return;
    var card = el('cohortCard');
    if(!kohorten || !kohorten.length){ card.innerHTML = '<div class="empty">Noch keine Kohorte.</div>'; return; }
    var k = kohorten[kohorten.length - 1];
    var neu = Number(k.neu), bleibt = Number(k.bleibt), offen = Number(k.offen);
    var projektiert = bleibt + Math.round(offen * CONFIG.bleibeQuote);
    var quote = neu > 0 ? Math.round(projektiert / neu * 100) : 0;
    var kMonat = new Date(k.kohorte + 'T00:00:00');
    var kEntsch = new Date(k.entscheidung_ab + 'T00:00:00');
    var monat = kMonat.toLocaleDateString('de-CH', { month:'long', year:'numeric' });
    card.innerHTML =
      '<div class="when"></div><h4></h4>' +
      '<div class="conv"><div class="ring"><div class="inner"></div></div>' +
      '<div class="txt"><b></b><br><span class="m"></span><div class="pill"></div></div></div>';
    card.querySelector('.when').textContent = 'Kohorte ' + monat + ' · Entscheidung ab ' + dmy(kEntsch);
    card.querySelector('h4').textContent = fmt(neu) + ' Anmeldungen im Gratis-Zeitraum';
    card.querySelector('.ring').style.setProperty('--p', quote);
    card.querySelector('.ring .inner').textContent = quote + '%';
    card.querySelector('.txt b').textContent = '~' + fmt(projektiert) + ' bleiben voraussichtlich zahlend';
    card.querySelector('.txt .m').textContent = fmt(offen) + ' Entscheidungen noch offen · ' + fmt(bleibt) + ' bereits umgewandelt';
    card.querySelector('.pill').textContent = 'Projektion · Annahme ' + Math.round(CONFIG.bleibeQuote * 100) + ' % Bleibe-Quote';

    el('projValue').textContent = geld(revenue.chfGesamt);
    var teile = [];
    if (revenue.chf > 0) teile.push('CHF ' + Math.round(revenue.chf).toLocaleString('de-CH') + ' von CHF-Zahlern');
    if (revenue.eur > 0) teile.push('€ ' + Math.round(revenue.eur).toLocaleString('de-CH') + ' von EUR-Zahlern, umgerechnet zum Kurs ' + CONFIG.eurChf);
    el('projNote').textContent = 'Hochgerechnet: bleibende Abos zum echten Vollpreis je Zahlungswährung' +
      (teile.length ? ' (' + teile.join(' + ') + ')' : '') + ', bei ' +
      Math.round(CONFIG.bleibeQuote * 100) + ' % Bleibe-Quote.';
  }

  // ── Momentum ───────────────────────────────────────────────────────────────
  function renderSpark(timeline){
    if (!el('spark')) return { avg: 0, days: 0 };
    var byDay = {};
    timeline.forEach(function(r){ byDay[r.day] = (byDay[r.day] || 0) + Number(r.n); });
    var days = Object.keys(byDay).sort();
    var recent = days.slice(-10);
    var host = el('spark'); host.innerHTML = '';
    if(!recent.length){ host.innerHTML = '<div class="empty">Noch keine Anmeldungen.</div>'; return { avg:0, days:0 }; }
    var max = recent.reduce(function(m, d){ return Math.max(m, byDay[d]); }, 0) || 1;
    recent.forEach(function(d){
      var v = byDay[d];
      var date = new Date(d + 'T00:00:00');
      var cell = document.createElement('div'); cell.className = 'd';
      cell.innerHTML = '<div class="bv"></div><div class="barcell"><div class="bar"></div></div><div class="dl"></div>';
      cell.querySelector('.bv').textContent = fmt(v);
      cell.querySelector('.bar').style.height = Math.max(3, Math.round(v / max * 100)) + '%';
      cell.querySelector('.dl').textContent = date.toLocaleDateString('de-CH', { day:'numeric', month:'numeric' });
      host.appendChild(cell);
    });
    var sum = recent.reduce(function(s, d){ return s + byDay[d]; }, 0);
    return { avg: Math.round(sum / recent.length), days: recent.length };
  }

  // ── Ereignis-Protokoll: die einzelnen Abos («Was ist passiert?») ────────────
  // RPC sommer2026_ereignisse: Einzel-Anmeldungen der letzten 14 Tage, stunden-
  // genau gerundet, ohne Personendaten. Beantwortet «woher kamen heute welche
  // Abos?» – je Tag aufklappbar, heute offen. Abos ohne UTM-Spur sind markiert.
  function evProduktLabel(r){
    if (r.produkt === 'gtv') return 'goetheanum.tv · ' + (r.sprache === 'en' ? 'EN' : 'DE');
    return 'Wochenschrift · ' + (r.sprache === 'en' ? 'EN' : 'DE') + ' · ' + (r.format === 'papier' ? 'Papier' : 'Digital');
  }
  function renderEreignisse(rows){
    var host = el('evList'); if (!host) return;
    host.innerHTML = '';
    if (!rows || !rows.length){
      host.innerHTML = '<div class="empty">Noch keine Anmeldungen in den letzten 14 Tagen.</div>';
      return;
    }
    var heute = new Date(); heute.setHours(0, 0, 0, 0);
    var gestern = new Date(heute); gestern.setDate(gestern.getDate() - 1);
    var tage = {}, folge = [];
    rows.forEach(function(r){
      var d = new Date(r.stunde);
      var k = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
      if (!tage[k]){ tage[k] = { datum: new Date(d.getFullYear(), d.getMonth(), d.getDate()), rows: [] }; folge.push(k); }
      tage[k].rows.push(r);
    });
    folge.forEach(function(k){
      var t = tage[k];
      var mitSpur = t.rows.filter(function(r){ return r.utm_source || r.utm_content; }).length;
      var det = document.createElement('details'); det.className = 'ev-day';
      if (t.datum.getTime() === heute.getTime()) det.open = true;
      var wann = t.datum.getTime() === heute.getTime() ? 'Heute'
               : t.datum.getTime() === gestern.getTime() ? 'Gestern'
               : t.datum.toLocaleDateString('de-CH', { weekday: 'long' });
      var sum = document.createElement('summary');
      var sb = document.createElement('b');
      sb.textContent = wann + ' · ' + t.datum.toLocaleDateString('de-CH', { day: 'numeric', month: 'long' });
      var sn = document.createElement('span'); sn.className = 'ev-sum';
      sn.textContent = fmt(t.rows.length) + (t.rows.length === 1 ? ' Abo' : ' Abos') +
        ' · ' + fmt(mitSpur) + ' mit UTM · ' + fmt(t.rows.length - mitSpur) + ' ohne';
      sum.appendChild(sb); sum.appendChild(sn); det.appendChild(sum);
      var list = document.createElement('div'); list.className = 'ev-list';
      t.rows.forEach(function(r){
        var row = document.createElement('div'); row.className = 'ev-row';
        var zeit = document.createElement('span'); zeit.className = 'ev-zeit';
        zeit.textContent = new Date(r.stunde).toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' });
        var was = document.createElement('span'); was.className = 'ev-was';
        was.textContent = evProduktLabel(r);
        var wm = document.createElement('span'); wm.className = 'ev-meta';
        wm.textContent = (r.tarif === 'ermaessigt' ? 'Ermässigt' : 'Standard') + ' · ' + (r.intervall === 'monatlich' ? 'monatlich' : 'jährlich');
        was.appendChild(wm);
        var her = document.createElement('span'); her.className = 'ev-her';
        if (r.utm_source || r.utm_content){
          var kb = document.createElement('span'); kb.className = 'ev-kanal';
          kb.textContent = KANAL_LABEL[r.kanal] || r.kanal;
          her.appendChild(kb);
          var spur = document.createElement('span'); spur.className = 'ev-spur';
          spur.textContent = [r.utm_source, r.utm_medium, r.utm_content].filter(Boolean).join(' · ');
          her.appendChild(spur);
        } else {
          var ob = document.createElement('span'); ob.className = 'ev-kanal ev-ohne';
          ob.textContent = 'ohne UTM';
          her.appendChild(ob);
          var wo = document.createElement('span'); wo.className = 'ev-spur';
          wo.textContent = r.landing_path ? ('via ' + r.landing_path) : ('via ' + (r.source === 'uscreen' ? 'goetheanum.tv-Checkout' : r.source));
          her.appendChild(wo);
          // «Vermutete Herkunft»: zeitlich nächster Kurzlink-Klick vor dem
          // Abschluss (aus dem RPC) – Indiz, keine Messung, darum eigene,
          // klar abgesetzte Beschriftung. Die harte Attribution bleibt leer.
          if (r.vermutet_code){
            var vm = document.createElement('span'); vm.className = 'ev-vermutet';
            vm.textContent = 'vermutet: ' + [r.vermutet_source, r.vermutet_content].filter(Boolean).join(' · ') +
              ' — Klick auf /s/' + r.vermutet_code + ' ' + fmt(r.vermutet_min) + ' Min. davor';
            her.appendChild(vm);
          }
        }
        row.appendChild(zeit); row.appendChild(was); row.appendChild(her);
        list.appendChild(row);
      });
      det.appendChild(list);
      host.appendChild(det);
    });
    var note = document.createElement('div'); note.className = 'fnote';
    note.textContent = 'Zeiten auf die Stunde gerundet, keine Personendaten. «ohne UTM» = Anmeldung kam ohne UTM-Parameter an – so heisst sie auch in der Wirkung. ' +
      '«vermutet» = der zeitlich nächste Kurzlink-Klick (bis 90 Minuten davor) auf einen passenden Kampagnen-Link – ein Indiz, keine Messung; gezählt wird es nirgends.';
    host.appendChild(note);
  }

  // ── Laden ──────────────────────────────────────────────────────────────────
  function load(){
    renderDeadline();
    renderQuelleSocial();
    // Ereignis-Protokoll separat laden: fällt der RPC aus, bleibt der Rest des
    // Cockpits vollständig – nur die Liste meldet sich als nicht ladbar.
    if (el('evList')) rpc('sommer2026_ereignisse')
      .then(renderEreignisse)
      .catch(function(){ el('evList').innerHTML = '<div class="err">nicht ladbar</div>'; });
    if(CONFIG.zahlenProvisorisch && el('provisorisch')){
      el('provisorisch').textContent = 'Zielmarken, Preise und die Bleibe-Quote sind vorläufig hinterlegt – sobald die echten Werte gesetzt sind, rechnet das Cockpit unverändert weiter.';
    }
    Promise.all([ rpc('sommer2026_stats'), rpc('sommer2026_timeline'), rpc('sommer2026_kohorten'), rpc('sommer2026_kanaele'),
                  rpc('sommer2026_trichter'), rpc('sommer2026_attribution'), rpc('sommer2026_massnahmen_public'), rpc('sommer2026_kosten_public'), rpc('sommer2026_multi_liste'), rpc('sommer2026_multi_protokoll') ])
      .then(function(res){
        var stats = res[0] || [], timeline = res[1] || [], kohorten = res[2] || [], kanaele = res[3] || [];
        var trichter = res[4] || [], attribution = res[5] || [], massnahmen = res[6] || [], kostenPosten = res[7] || [];
        muListe = res[8] || []; muProto = res[9] || [];
        var total = stats.reduce(function(s, r){ return s + Number(r.n); }, 0);
        var revenue = projectRevenue(stats);
        var mo = renderSpark(timeline);
        renderTiles(total, mo.avg, mo.days);
        renderStreams(stats);
        renderFunnel(trichter, massnahmen);
        renderKanaele(kanaele, total);
        renderSpurTile(kanaele, total);
        renderMotive(attribution);
        renderTarif(stats);
        renderMilestones(total);
        renderCohort(kohorten, revenue);
        renderKosten(total, revenue, kostenPosten);
        renderMassnahmen(massnahmen);
        renderZeitband(massnahmen);
        renderMultis();
        if (muPwGespeichert()) muNamenLaden(muPwGespeichert(), true);
        if(total === 0 && el('status')){ el('status').className = 'status empty'; }
        setStatus('ok', new Date());
      })
      .catch(function(){
        setStatus('err');
        ['wosStreams','gtvStreams','kanalBars','funnel'].forEach(function(id){ var e = el(id); if (e) e.innerHTML = '<div class="err">nicht ladbar</div>'; });
        if (el('spark')) el('spark').innerHTML = '<div class="err">nicht ladbar</div>';
      });
  }

  load();
  setInterval(load, REFRESH);
