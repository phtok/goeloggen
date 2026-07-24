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
    // Dunkelfeld: die Anmeldungen OHNE UTM-Spur den Gebieten zuordnen.
    // Hinterlegt sind ANTEILE aus der datierten Lesart – sie werden auf den
    // jeweils aktuellen Stand angewandt, damit die Einordnung stimmig bleibt,
    // während die Zahlen weiterlaufen. Schätzung (±30 %), keine Messung; die
    // Messwerte in der Datenbank bleiben unangetastet. Bei neuer Auswertung:
    // stand/doc/anteile hier nachziehen, sonst nichts.
    // Korrektur 24. Juli: der Anteil der bezahlten Anzeige fiel von 40 % auf 7 %.
    // Die alte Zahl kam aus der vermuteten Herkunft (zeitnächster Klick) – ein
    // Anker, der nur bei spärlichen Klicks trägt. Die Anzeige stellt fast das
    // ganze Klick-Log und gewann darum fast jede Nähe-Lotterie; eine Placebo-Probe
    // (Anmeldezeiten um ±24/48 h verschoben) trifft sie fast gleich oft.
    dunkel: {
      stand: '24. Juli',
      doc:   'docs/wirkungs-lesart-24-07.md',
      anteile: {
        newsletter: 0.346,   // TV-Weekly und Haus-Newsletter (Placebo-Überschuss belegt)
        organik:    0.300,   // Direkt, Suche, Storefront, Bestandskonten
        mailing:    0.208,   // Nachlauf der Welle 1 ohne Spur
        bezahlt:    0.069,   // Meta-Anzeige – Obergrenze aus dem sauberen Fenster
        social:     0.069,   // Reels, Stories, Karussell
        print:      0.008
      }
    },
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

  // ── Gebiete: die eine Achse, auf der alles zusammenläuft ──────────────────
  // Ein «Gebiet» ist ein Wirkungsfeld der Kampagne (Mailing, bezahlte Anzeige,
  // Newsletter …). Alle drei Datenquellen werden darauf abgebildet, damit eine
  // Zeile die ganze Kette tragen kann: Reichweite und Hand-Klicks aus dem
  // Aktivitäten-Protokoll, Kurzlink-Klicks aus dem Link-Register, Abschlüsse aus
  // der Attribution. REIHENFOLGE ZÄHLT – der erste Treffer gewinnt: «bezahlt»
  // vor «social» (die Anzeige läuft als medium=social), «newsletter» vor
  // «mailing» (das Wort «email» enthält «mail»), «print» vor «organik»
  // (inserat_* trägt medium=web).
  var GEBIETE = [
    { key:'bezahlt',    label:'Bezahlt · Anzeige',          test:/anzeige|\bads?\b|\bcpc\b/ },
    { key:'newsletter', label:'Newsletter',                 test:/news|\bnl\b|nl-|weekly/ },
    { key:'mailing',    label:'Mailing',                    test:/mailing|mailer|\bpost\b|brief/ },
    { key:'social',     label:'Social organisch',           test:/insta|face|\bfb\b|linkedin|youtube|tiktok|twitter|social/ },
    { key:'print',      label:'Print · Stand · Inserat',    test:/inserat|print|flyer|stand|plakat|\bqr\b/ },
    { key:'popup',      label:'Popup',                      test:/popup|overlay/ },
    { key:'empfehlung', label:'Empfehlung',                 test:/refer|empfehl|partner|friend/ },
    { key:'organik',    label:'Organik · Direkt · Bestand', test:/uscreen|landing|\bweb\b|site|direct|organic/ },
    { key:'andere',     label:'Übrige',                     test:null }
  ];
  function gebietVonSpur(src, med){
    var s = ((src || '') + ' ' + (med || '')).toLowerCase();
    if (!s.trim()) return 'andere';
    for (var i = 0; i < GEBIETE.length; i++){
      var g = GEBIETE[i];
      if (g.test && g.test.test(s)) return g.key;
    }
    return 'andere';
  }
  // Aktivitäten tragen einen Kanal-Eimer; die bezahlte Anzeige steckt darin als
  // «social» und wird über den Titel herausgelöst (sonst verschwindet der
  // grösste Posten in der organischen Zeile).
  var KANAL_ZU_GEBIET = { social:'social', newsletter:'newsletter', mailer:'mailing',
                          flyer:'print', website:'organik', popup:'popup', empfehlung:'empfehlung' };
  function gebietVonMassnahme(m){
    if (/anzeige|\bads?\b/i.test(m.massnahme || '')) return 'bezahlt';
    return KANAL_ZU_GEBIET[m.kanal] || 'andere';
  }
  function gebietLabel(k){
    for (var i = 0; i < GEBIETE.length; i++) if (GEBIETE[i].key === k) return GEBIETE[i].label;
    return k;
  }

  // Dunkelfeld auf die Gebiete verteilen: die datierte Lesart liefert ANTEILE,
  // die auf den aktuellen Stand der Anmeldungen ohne Spur angewandt werden – so
  // bleibt die Einordnung stimmig, während die Zahlen weiterlaufen. Der Rest der
  // Rundung geht an das grösste Gebiet, damit die Summe exakt aufgeht.
  function dunkelVerteilen(ohne){
    var anteile = (CONFIG.dunkel && CONFIG.dunkel.anteile) || {};
    var out = {}, verteilt = 0, groesstes = null, max = -1;
    Object.keys(anteile).forEach(function(k){
      var n = Math.round(ohne * anteile[k]);
      out[k] = n; verteilt += n;
      if (anteile[k] > max){ max = anteile[k]; groesstes = k; }
    });
    if (groesstes && verteilt !== ohne) out[groesstes] += (ohne - verteilt);
    return out;
  }

  // ── 1 · Stand: eine Zahl, ein Tempo, eine Prognose ────────────────────────
  // Der Kern der Aufräumung: statt vier Kacheln, Deadline-Meter, Meilenstein und
  // eigener Momentum-Sektion EIN Block, der die Frage «wo stehen wir» beantwortet
  // – samt der Fortschreibung, die eine Prozentzahl allein verschweigt.
  function tempoUndPrognose(timeline){
    var byDay = {};
    (timeline || []).forEach(function(r){ byDay[r.day] = (byDay[r.day] || 0) + Number(r.n); });
    var tage = Object.keys(byDay).sort();
    var letzte = tage.slice(-3);
    var tempo = letzte.length ? letzte.reduce(function(s, d){ return s + byDay[d]; }, 0) / letzte.length : 0;
    var ende = new Date(CONFIG.ende + 'T00:00:00'), jetzt = new Date();
    var heute = new Date(jetzt.getFullYear(), jetzt.getMonth(), jetzt.getDate());
    var rest = Math.max(0, Math.round((ende - heute) / 86400000));
    return { byDay:byDay, tage:tage, tempo:tempo, rest:rest };
  }
  function renderStand(total, timeline){
    if (!el('standZahl')) return;
    var t = tempoUndPrognose(timeline);
    var ziel = CONFIG.zielGesamt || 0;
    el('standZahl').textContent = fmt(total);
    el('standUnter').textContent = 'neue Abos · Ziel ' + fmt(ziel) +
      (t.rest > 0 ? (' · noch ' + t.rest + ' Tage bis ' + dmy(new Date(CONFIG.ende + 'T00:00:00'))) : ' · Aktion beendet');
    var pct = ziel > 0 ? Math.round(total / ziel * 100) : 0;
    el('kZiel').textContent = pct + ' %';
    el('kTempo').textContent = t.tempo.toFixed(1).replace('.', ',');
    var noetig = t.rest > 0 ? Math.max(0, (ziel - total) / t.rest) : 0;
    el('kNoetig').textContent = t.rest > 0 ? noetig.toFixed(1).replace('.', ',') : '–';
    el('ddBar').style.width = Math.min(100, pct) + '%';

    // Puls: die letzten zehn Tage – der Takt neben der Zahl, nicht als eigene Sektion.
    var host = el('puls'); if (host){
      host.innerHTML = '';
      var recent = t.tage.slice(-10);
      var max = recent.reduce(function(m, d){ return Math.max(m, t.byDay[d]); }, 0) || 1;
      var spitze = recent.reduce(function(b, d){ return t.byDay[d] > t.byDay[b] ? d : b; }, recent[0]);
      recent.forEach(function(d){
        var b = document.createElement('span');
        b.className = 'p' + (d === spitze ? ' hoch' : '');
        b.style.height = Math.max(3, Math.round(t.byDay[d] / max * 100)) + '%';
        b.title = new Date(d + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'long' }) +
                  ' · ' + fmt(t.byDay[d]) + (t.byDay[d] === 1 ? ' Abo' : ' Abos');
        host.appendChild(b);
      });
      var lab = el('pulsL');
      if (lab && recent.length){
        lab.innerHTML = '';
        var von = document.createElement('span');
        von.textContent = new Date(recent[0] + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'long' });
        var top = document.createElement('span');
        top.textContent = 'Spitze ' + fmt(t.byDay[spitze]) + ' am ' + new Date(spitze + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' });
        var bis = document.createElement('span');
        bis.textContent = 'heute ' + fmt(t.byDay[recent[recent.length - 1]] || 0);
        lab.appendChild(von); lab.appendChild(top); lab.appendChild(bis);
      }
    }

    // Befund: die Fortschreibung im Klartext. Erscheint nur, wenn die Aktion läuft.
    var box = el('befund');
    if (box && t.rest > 0){
      var prognose = Math.round(total + t.tempo * t.rest);
      box.hidden = false;
      var txt = el('befundText'); txt.innerHTML = '';
      txt.appendChild(document.createTextNode('Bei diesem Tempo endet die Aktion bei rund '));
      var b1 = document.createElement('b'); b1.textContent = fmt(prognose) + ' Abos'; txt.appendChild(b1);
      txt.appendChild(document.createTextNode('. '));
      if (prognose < ziel){
        txt.appendChild(document.createTextNode('Das Ziel ' + fmt(ziel) + ' ist nur erreichbar, wenn ein Impuls von der Grösse der stärksten bisherigen Welle kommt – '));
        var b2 = document.createElement('b'); b2.textContent = 'mehrfach'; txt.appendChild(b2);
        txt.appendChild(document.createTextNode('.'));
      } else {
        txt.appendChild(document.createTextNode('Das Ziel ' + fmt(ziel) + ' ist bei diesem Tempo in Reichweite.'));
      }
      el('befundMeta').textContent = 'Fortschreibung des Schnitts der letzten drei Tage (' +
        t.tempo.toFixed(1).replace('.', ',') + '/Tag) auf die restlichen ' + t.rest + ' Tage. Kein Versprechen – eine Rechnung.';
    } else if (box) { box.hidden = true; }
  }

  // Ströme (Produkt × Sprache × Format) – aus eigener Sektion in den Aufklapp.
  function streamValue(rows, s){
    return rows.reduce(function(sum, r){
      if(r.produkt === s.produkt && r.sprache === s.sprache && r.format === s.format) return sum + Number(r.n);
      return sum;
    }, 0);
  }
  function renderStroeme(rows, total){
    if (!el('stroemeBody')) return;
    var body = el('stroemeBody'); body.innerHTML = '';
    var items = STREAMS.map(function(s){
      return { name:(s.panel === 'gtv' ? 'goetheanum.tv · ' : 'Wochenschrift · ') + s.name,
               n:streamValue(rows, s), ziel:CONFIG.ziele[s.key] || 0 };
    }).sort(function(a, b){ return b.n - a.n; });
    var sz = 0;
    items.forEach(function(x){
      sz += x.ziel;
      var tr = document.createElement('tr');
      tr.innerHTML = '<td></td><td class="num"></td><td class="num"></td><td class="num"></td>';
      tr.children[0].textContent = x.name;
      tr.children[1].textContent = fmt(x.n);
      tr.children[2].textContent = x.ziel ? fmt(x.ziel) : '–';
      tr.children[3].textContent = x.ziel ? (Math.round(x.n / x.ziel * 100) + ' %') : '–';
      body.appendChild(tr);
    });
    var foot = el('stroemeFoot');
    if (foot){
      foot.innerHTML = '<tr><td>Summe</td><td class="num"></td><td class="num"></td><td class="num"></td></tr>';
      var td = foot.querySelector('tr').children;
      td[1].textContent = fmt(total); td[2].textContent = fmt(sz);
      td[3].textContent = sz ? (Math.round(total / sz * 100) + ' %') : '–';
    }
    if (el('stroemeKopf')) el('stroemeKopf').textContent = 'Woraus sich die ' + fmt(total) + ' Abos zusammensetzen';
  }

  // ── 2 · Gebiete: eine Liste, jede Zeile die ganze Kette ───────────────────
  // Löst «Woher», Wirkungskette, «Nach Motiv», «Kanäle» und «Aktivität →
  // Abschlüsse» in EINER Ansicht auf – dieselben Messwerte, einmal statt fünfmal.
  function renderGebiete(attribution, links, massnahmen, kanaele){
    if (!el('gebieteListe')) return;
    var host = el('gebieteListe'); host.innerHTML = '';
    var ab = {}, kl = {}, rw = {}, motive = {}, akte = {}, linkN = {}, ohne = 0;
    var add = function(o, k, v){ o[k] = (o[k] || 0) + v; };

    (attribution || []).forEach(function(r){
      var n = Number(r.n) || 0;
      if (!r.utm_source && !r.utm_content){ ohne += n; return; }
      var g = gebietVonSpur(r.utm_source, r.utm_medium);
      add(ab, g, n);
      var label = r.utm_content || r.utm_source;
      var key = g + '|' + label + '|' + (r.utm_source || '');
      (motive[g] = motive[g] || {});
      motive[g][key] = motive[g][key] || { label:label, quelle:r.utm_source || '', ab:0, kl:0 };
      motive[g][key].ab += n;
    });
    (links || []).forEach(function(l){
      var g = gebietVonSpur(l.utm_source, l.utm_medium);
      add(linkN, g, 1);
      var k = Number(l.klicks) || 0;
      if (k) add(kl, g, k);
      var label = l.utm_content || l.utm_source;
      var key = g + '|' + label + '|' + (l.utm_source || '');
      (motive[g] = motive[g] || {});
      motive[g][key] = motive[g][key] || { label:label, quelle:l.utm_source || '', ab:0, kl:0 };
      motive[g][key].kl += k;
    });
    (massnahmen || []).forEach(function(m){
      var g = gebietVonMassnahme(m);
      var r = Number(m.reichweite) || 0, k = Number(m.klicks) || 0;
      if (r) add(rw, g, r);
      if (k) add(kl, g, k);
      if (r || k) (akte[g] = akte[g] || []).push({ name:m.massnahme || '—', tag:m.tag, reichweite:r, klicks:k });
    });

    var dunkel = dunkelVerteilen(ohne);
    var total = ohne; Object.keys(ab).forEach(function(k){ total += ab[k]; });
    var keys = {}; [ab, kl, rw, dunkel, linkN].forEach(function(o){ Object.keys(o).forEach(function(k){ keys[k] = true; }); });
    var items = Object.keys(keys).map(function(g){
      return { g:g, ab:ab[g] || 0, kl:kl[g] || 0, rw:rw[g] || 0, du:dunkel[g] || 0,
               links:linkN[g] || 0, gesamt:(ab[g] || 0) + (dunkel[g] || 0) };
    }).filter(function(x){ return x.gesamt > 0 || x.rw > 0 || x.kl >= 3 || (x.links >= 2 && x.g !== 'andere'); })
      .sort(function(a, b){ return b.gesamt - a.gesamt || b.kl - a.kl; });
    if (!items.length){ host.innerHTML = '<div class="empty">Noch keine Aktivität erfasst.</div>'; return; }
    var max = items.reduce(function(m, x){ return Math.max(m, x.gesamt); }, 0) || 1;

    items.forEach(function(x){
      var det = document.createElement('details'); det.className = 'geb';
      var sum = document.createElement('summary');
      var kopf = document.createElement('div'); kopf.className = 'geb-kopf';
      var nm = document.createElement('span'); nm.className = 'geb-name';
      var car = document.createElement('span'); car.className = 'car'; car.setAttribute('aria-hidden', 'true');
      nm.appendChild(car); nm.appendChild(document.createTextNode(gebietLabel(x.g)));
      // Merkzeichen: ein Wort, das sagt, was diese Zeile bedeutet.
      var z = null;
      if (x.kl >= 40 && x.ab <= 1) z = ['leck', 'viel Klick, kaum Abschluss'];
      else if (total > 0 && x.gesamt >= total * 0.3) z = ['traegt', 'trägt die Aktion'];
      else if (x.kl === 0 && x.gesamt === 0 && x.links > 0) z = ['still', 'nie ausgespielt'];
      else if (x.kl >= 20 && x.ab === 0) z = ['still', 'ohne messbaren Ertrag'];
      else if (x.du >= 10 && x.du > x.ab * 2) z = ['dunkel', 'grösstenteils dunkel'];
      if (z){ var zs = document.createElement('span'); zs.className = 'zeichen ' + z[0]; zs.textContent = z[1]; nm.appendChild(zs); }
      var wert = document.createElement('span'); wert.className = 'geb-wert';
      wert.appendChild(document.createTextNode(fmt(x.ab)));
      if (x.du){ var du = document.createElement('span'); du.className = 'du';
        du.textContent = ' · ≈' + fmt(x.gesamt) + ' mit Dunkelfeld'; wert.appendChild(du); }
      kopf.appendChild(nm); kopf.appendChild(wert);
      var kette = document.createElement('div'); kette.className = 'geb-kette';
      var teil = function(l, v){ var s2 = document.createElement('span');
        s2.appendChild(document.createTextNode(l + ' '));
        var b = document.createElement('b'); b.textContent = v; s2.appendChild(b); kette.appendChild(s2); };
      teil('Reichweite', x.rw ? fmt(x.rw) : '–');
      teil('Klicks', x.kl ? fmt(x.kl) : '–');
      teil('Abschlüsse', fmt(x.ab));
      if (x.rw && x.kl) teil('Klickquote', (x.kl / x.rw * 100).toFixed(1).replace('.', ',') + ' %');
      var track = document.createElement('div'); track.className = 'track';
      var tb = document.createElement('span'); tb.style.width = Math.max(3, Math.round(x.gesamt / max * 100)) + '%';
      track.appendChild(tb);
      sum.appendChild(kopf); sum.appendChild(kette); sum.appendChild(track);
      det.appendChild(sum);

      var tief = document.createElement('div'); tief.className = 'geb-tief';
      var mots = Object.keys(motive[x.g] || {}).map(function(k){ return motive[x.g][k]; })
        .filter(function(m){ return m.ab > 0 || m.kl > 0; })
        .sort(function(a, b){ return b.ab - a.ab || b.kl - a.kl; }).slice(0, 10);
      mots.forEach(function(m){
        var row = document.createElement('div'); row.className = 'motrow';
        var mc = document.createElement('span'); mc.className = 'mc'; mc.textContent = m.label;
        if (m.quelle && m.quelle !== m.label){ var ms = document.createElement('span'); ms.className = 'ms'; ms.textContent = m.quelle; mc.appendChild(ms); }
        var mn = document.createElement('span'); mn.className = 'mn';
        mn.textContent = (m.kl ? fmt(m.kl) + ' Klicks' : '') + (m.kl && m.ab ? ' · ' : '') + (m.ab ? fmt(m.ab) + ' Abos' : (m.kl ? '' : '0'));
        row.appendChild(mc); row.appendChild(mn); tief.appendChild(row);
      });
      (akte[x.g] || []).sort(function(a, b){ return b.reichweite - a.reichweite; }).slice(0, 8).forEach(function(a){
        var row = document.createElement('div'); row.className = 'motrow';
        var mc = document.createElement('span'); mc.className = 'mc'; mc.textContent = a.name;
        if (a.tag){ var ms = document.createElement('span'); ms.className = 'ms';
          ms.textContent = new Date(a.tag + 'T00:00:00').toLocaleDateString('de-CH', { day:'numeric', month:'numeric' }); mc.appendChild(ms); }
        var mn = document.createElement('span'); mn.className = 'mn';
        mn.textContent = (a.reichweite ? fmt(a.reichweite) + ' erreicht' : '') +
                         (a.reichweite && a.klicks ? ' · ' : '') + (a.klicks ? fmt(a.klicks) + ' Klicks' : '');
        row.appendChild(mc); row.appendChild(mn); tief.appendChild(row);
      });
      if (!mots.length && !(akte[x.g] || []).length){
        var leer = document.createElement('div'); leer.className = 'qz-hint';
        leer.textContent = 'Keine Einzelposten erfasst.'; tief.appendChild(leer);
      }
      if (x.du){
        var dh = document.createElement('div'); dh.className = 'qz-hint';
        dh.textContent = '+ ≈' + fmt(x.du) + ' Abos ohne UTM-Spur, diesem Gebiet nach der Lesart zugeordnet (Stand ' +
          ((CONFIG.dunkel && CONFIG.dunkel.stand) || '–') + ') – Schätzung, keine Messung.';
        tief.appendChild(dh);
      }
      if (x.g === 'social' && CONFIG.quelleSocial){
        var ql = document.createElement('div'); ql.className = 'qz-hint';
        ql.appendChild(document.createTextNode('Quelle der Zahlen: '));
        var qa = document.createElement('a'); qa.href = CONFIG.quelleSocial.url;
        qa.target = '_blank'; qa.rel = 'noopener'; qa.textContent = CONFIG.quelleSocial.label;
        ql.appendChild(qa); tief.appendChild(ql);
      }
      det.appendChild(tief);
      host.appendChild(det);
    });

    // Kontrollzeile: das Dunkelfeld als Ganzes – ohne Balken, es ist oben schon verteilt.
    if (ohne > 0){
      var det2 = document.createElement('details'); det2.className = 'geb';
      var s3 = document.createElement('summary');
      var k3 = document.createElement('div'); k3.className = 'geb-kopf';
      var n3 = document.createElement('span'); n3.className = 'geb-name';
      var c3 = document.createElement('span'); c3.className = 'car'; c3.setAttribute('aria-hidden', 'true');
      n3.appendChild(c3); n3.appendChild(document.createTextNode('Ohne UTM-Spur'));
      var z3 = document.createElement('span'); z3.className = 'zeichen dunkel'; z3.textContent = 'Lesart, keine Messung';
      n3.appendChild(z3);
      var w3 = document.createElement('span'); w3.className = 'geb-wert';
      w3.appendChild(document.createTextNode(fmt(ohne)));
      var d3 = document.createElement('span'); d3.className = 'du';
      d3.textContent = ' · ' + (total > 0 ? Math.round(ohne / total * 100) : 0) + ' % aller Abos';
      w3.appendChild(d3);
      k3.appendChild(n3); k3.appendChild(w3);
      var kt = document.createElement('div'); kt.className = 'geb-kette';
      var kts = document.createElement('span'); kts.textContent = 'oben bereits auf die Gebiete verteilt'; kt.appendChild(kts);
      s3.appendChild(k3); s3.appendChild(kt); det2.appendChild(s3);
      var t3 = document.createElement('div'); t3.className = 'geb-tief';
      var p3 = document.createElement('div'); p3.className = 'qz-hint';
      p3.textContent = 'Diese Anmeldungen kamen ohne UTM-Parameter an und sind in den Zeilen oben als «≈ mit Dunkelfeld» bereits eingerechnet – hier stehen sie noch einmal als Ganzes, damit sichtbar bleibt, wie viel Lesart in der Rangfolge steckt. Herleitung unter Belege.';
      t3.appendChild(p3); det2.appendChild(t3);
      host.appendChild(det2);
    }
    if (el('gebieteNote')){
      el('gebieteNote').textContent = '«Abschlüsse» ist die harte UTM-Zählung. «≈ mit Dunkelfeld» verteilt die ' +
        fmt(ohne) + ' Anmeldungen ohne Spur nach der datierten Lesart (±30 %). Die Summe der Zeilen ergibt wieder ' + fmt(total) + '.';
    }
  }

  // ── 3 · Nächste Züge: was noch möglich ist, aus den Daten gelesen ─────────
  // Nichts hiervon ist erfunden: der Plan steht bereits im Link-Register (jeder
  // registrierte Link ist eine Absicht) und im Aktivitäten-Protokoll. Gelesen
  // wird die LÜCKE – was vorbereitet ist, aber nie einen Klick gesehen hat.
  var ZUG_QUELLE = [
    { test:/mailing|mailer/, titel:'Mail-Welle senden',        warum:'vorbereitet, aber nie ausgespielt' },
    { test:/news|\bnl\b|nl-|weekly/, titel:'Newsletter-Phasen ausspielen', warum:'Links liegen bereit, null Klicks' },
    { test:/popup/,          titel:'Popup scharf schalten',    warum:'registriert, aber nie ein Klick' },
    { test:/inserat|print|\bqr\b/, titel:'Print-Weg prüfen',   warum:'QR und Inserat ohne einen Scan' },
    { test:/insta|face|\bfb\b|linkedin|youtube|tiktok|social/, titel:'Social-Motive ausspielen', warum:'fertig verlinkt, nie gepostet' },
    { test:null,             titel:'Vorbereitete Links ausspielen', warum:'registriert, aber nie ein Klick' }
  ];
  function renderZuege(links, massnahmen, attribution, timeline, total){
    if (!el('zuegeListe')) return;
    var host = el('zuegeListe'); host.innerHTML = '';
    var zuege = [], ohneSpur = 0;
    (attribution || []).forEach(function(r){ if (!r.utm_source && !r.utm_content) ohneSpur += Number(r.n) || 0; });

    // (a) Stumme Motive: registrierte Links ohne Klick UND ohne Abschluss.
    var ab = {};
    (attribution || []).forEach(function(r){
      if (r.utm_source || r.utm_content) ab[(r.utm_content || '') + '|' + (r.utm_source || '')] = Number(r.n) || 0;
    });
    var grp = {};
    (links || []).forEach(function(l){
      var k = (l.utm_content || '') + '|' + (l.utm_source || '');
      grp[k] = grp[k] || { content:l.utm_content || '', source:l.utm_source || '', med:l.utm_medium || '',
                           landing:l.landing || '', kl:0, n:0 };
      grp[k].kl += Number(l.klicks) || 0; grp[k].n++;
      if (l.landing) grp[k].landing = l.landing;
    });
    var stumm = {};
    Object.keys(grp).forEach(function(k){
      var g = grp[k];
      if (g.kl === 0 && !(ab[k] > 0)){
        var s = (g.source + ' ' + g.med).toLowerCase();
        var art = ZUG_QUELLE.filter(function(q){ return q.test && q.test.test(s); })[0] || ZUG_QUELLE[ZUG_QUELLE.length - 1];
        stumm[art.titel] = stumm[art.titel] || { art:art, motive:[], links:0, src:g.source, med:g.med };
        stumm[art.titel].motive.push(g.content || g.source);
        stumm[art.titel].links += g.n;
      }
    });
    // Anker für die Erwartung: die stärkste bisher gemessene Welle desselben Gebiets.
    var jeGebiet = {};
    (attribution || []).forEach(function(r){
      if (!r.utm_source && !r.utm_content) return;
      var g = gebietVonSpur(r.utm_source, r.utm_medium);
      jeGebiet[g] = (jeGebiet[g] || 0) + (Number(r.n) || 0);
    });
    // Rangfolge über KATEGORIEN, nicht über Rohzahlen: Klicks und Links sind
    // nicht vergleichbar. Was neue Abos schafft, steht über dem, was bestehende
    // nur sichtbar macht; danach kommt Verlust stoppen, zuletzt die Grundlage.
    //   3 = schafft Abos · 2 = macht sichtbar · 1 = stoppt Verlust · 0 = Grundlage
    Object.keys(stumm).forEach(function(titel){
      var s2 = stumm[titel];
      var g = gebietVonSpur(s2.src, s2.med);
      var anker = jeGebiet[g] || 0;
      zuege.push({
        titel: titel, art: 3, mass: anker,
        warum: s2.links + ' Links registriert, null Klicks · ' + s2.motive.slice(0, 4).join(', ') +
               (s2.motive.length > 4 ? ' und weitere' : ''),
        hebel: anker > 0 ? ('≈ ' + fmt(anker) + ' Abos') : 'unerprobt',
        text: 'Vorbereitet, aber nie gezündet: ' + s2.motive.length + ' Motiv-Gruppen mit zusammen ' + s2.links +
              ' Links liegen im Register und haben bis heute keinen einzigen Klick. ' +
              (anker > 0
                ? ('Dasselbe Gebiet hat bisher ' + fmt(anker) + ' Abschlüsse gemessen getragen – das ist der Massstab für die Erwartung.')
                : 'Dieses Gebiet hat bisher nichts getragen; die Erwartung ist entsprechend offen.')
      });
    });

    // (b) Viel Klick, (fast) kein gemessener Abschluss. Bis zum 24. Juli stand
    // hier EINE gemeinsame Ursache (der Uscreen-Checkout trage die Spur nicht) –
    // das ist widerlegt: die Kette Landing → Checkout → user_created ist geprüft
    // und trägt die UTM. Bleibt der Befund selbst: diese Wege werden geklickt und
    // münden kaum in Abos. Darum ein Zug, der misst statt umbaut.
    // Herleitung: docs/wirkungs-lesart-24-07.md.
    var leck = { kl:0, motive:[] };
    Object.keys(grp).forEach(function(k){
      var g = grp[k], a2 = ab[k] || 0;
      if (g.kl < 20 || a2 > 1) return;
      var tv = /tv|gtv/.test((g.landing || '').toLowerCase());
      var geb = gebietVonSpur(g.source, g.med);
      if (tv || geb === 'bezahlt'){
        leck.kl += g.kl; leck.motive.push((g.content || g.source) + ' (' + fmt(g.kl) + ')');
      } else if (a2 === 0) {
        // Nur echte Nullen melden: ein Motiv mit einer brauchbaren Quote ist
        // keine Schwäche, auch wenn die absolute Zahl klein ist.
        zuege.push({ titel:'Prüfen oder einstellen · ' + (g.content || g.source), art:1, mass:g.kl,
          warum:fmt(g.kl) + ' Klicks, kein einziger Abschluss',
          hebel:'Verlust stoppen',
          text:'Wird geklickt, aber niemand meldet sich an. Entweder führt der Link auf die falsche Seite, oder das Versprechen deckt sich nicht mit der Landingpage. Ein Blick auf den Ziel-Link genügt; bis dahin lohnt weitere Produktion in diesem Motiv nicht.' });
      }
    });
    if (leck.kl > 0){
      zuege.push({ titel:'Bezahlte Anzeige 3–4 Tage aussetzen und vergleichen', art:2, mass:leck.kl,
        warum:fmt(leck.kl) + ' Klicks auf TV-Wege führen zu fast keinem Abschluss',
        hebel:'Klarheit',
        text:'Betroffen: ' + leck.motive.slice(0, 5).join(', ') + (leck.motive.length > 5 ? ' und weitere' : '') +
             '. Die Spur ist geprüft und intakt: die Landingpages hängen die UTM an die Checkout-URL, Uscreen liefert sie im user_created-Event, die Ingestion verheftet sie. ' +
             'Die organischen Wege über dieselbe Seite und dieselben In-App-Browser werden mit 3 bis 5 Prozent ihrer Klicks messbar, die bezahlte Anzeige mit 0,4 Prozent – die Klicks werden also nicht verloren, sie werden kaum zu Abos. ' +
             'Darum zuerst messen statt umbauen: die Anzeige aussetzen, solange die Grundlinie sauber ist (Mailing abgeklungen, nächste Welle später), und die Anmeldungen je Tag vergleichen. ' +
             'Soll sie danach weiterlaufen, macht ein eigenes Uscreen-Angebot je bezahltem Weg sie hart messbar (offer_id kommt serverseitig im Webhook an): services/sommer-zaehler/uscreen-angebot-attribution-auftrag.md.' });
    }

    // (c) Datengrundlage: Aktivitäten ohne Reichweite und ohne Klicks.
    var offen = (massnahmen || []).filter(function(m){ return !m.reichweite && !m.klicks; });
    if (offen.length){
      zuege.push({ titel:offen.length + ' Aktivitäten ohne Zahlen nachtragen', art:0, mass:offen.length,
        warum:'von ' + (massnahmen || []).length + ' Einträgen fehlen ' + offen.length + ' Reichweite und Klicks',
        hebel:'Grundlage',
        text:'Ohne diese Zahlen bleibt die Kette oben an mehreren Stellen leer – und die Kosten je Abo lassen sich nicht ehrlich rechnen. Nachtragen im Protokoll über «Bearbeiten».' });
    }

    zuege.sort(function(a, b){ return b.art - a.art || b.mass - a.mass; });

    if (!zuege.length){ host.innerHTML = '<div class="empty">Nichts liegt brach – alles Vorbereitete ist ausgespielt.</div>'; return; }
    zuege.slice(0, 8).forEach(function(z, i){
      var det = document.createElement('details'); det.className = 'zug';
      if (i === 0) det.open = true;
      var sum = document.createElement('summary');
      var t = document.createElement('span'); t.className = 'zug-t';
      var car = document.createElement('span'); car.className = 'car'; car.setAttribute('aria-hidden', 'true');
      t.appendChild(car); t.appendChild(document.createTextNode(z.titel));
      var w = document.createElement('span'); w.className = 'warum'; w.textContent = z.warum; t.appendChild(w);
      var h = document.createElement('span'); h.className = 'zug-h';
      h.textContent = z.hebel;
      sum.appendChild(t); sum.appendChild(h); det.appendChild(sum);
      var tief = document.createElement('div'); tief.className = 'zug-tief';
      var p = document.createElement('p'); p.textContent = z.text; tief.appendChild(p);
      det.appendChild(tief);
      host.appendChild(det);
    });
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

  // ── Dunkelfeld-Tabelle (Belege): wie die Abos ohne Spur verteilt wurden ───
  // Zeigt die ANTEILE der datierten Lesart und was sie auf dem heutigen Stand
  // bedeuten. Die Verteilung selbst steckt in dunkelVerteilen() – hier wird sie
  // nur offengelegt, damit die Rangfolge oben nachprüfbar bleibt.
  function renderDunkelfeld(kanaele, attribution){
    if (!el('dunkelBody')) return;
    var ohne = 0;
    (attribution || []).forEach(function(r){ if (!r.utm_source && !r.utm_content) ohne += Number(r.n) || 0; });
    var verteilt = dunkelVerteilen(ohne);
    var anteile = (CONFIG.dunkel && CONFIG.dunkel.anteile) || {};
    var body = el('dunkelBody'); body.innerHTML = '';
    var keys = Object.keys(anteile).sort(function(a, b){ return anteile[b] - anteile[a]; });
    keys.forEach(function(k){
      var tr = document.createElement('tr');
      tr.innerHTML = '<td></td><td class="num"></td><td class="num"></td>';
      tr.children[0].textContent = gebietLabel(k);
      tr.children[1].textContent = Math.round(anteile[k] * 100) + ' %';
      tr.children[2].textContent = '≈' + fmt(verteilt[k] || 0);
      body.appendChild(tr);
    });
    var foot = el('dunkelFoot');
    if (foot){
      foot.innerHTML = '<tr><td>Summe</td><td class="num">100 %</td><td class="num"></td></tr>';
      foot.querySelector('tr').children[2].textContent = fmt(ohne);
    }
    if (el('dunkelNote')){
      el('dunkelNote').textContent = 'Die Anteile stammen aus der datierten Lesart (Stand ' +
        ((CONFIG.dunkel && CONFIG.dunkel.stand) || '–') + ', ±30 %) und werden auf den heutigen Stand von ' +
        fmt(ohne) + ' Anmeldungen ohne Spur angewandt. Herleitung: ' +
        ((CONFIG.dunkel && CONFIG.dunkel.doc) || '') + ' im Werkzeug-Repo. Die Messwerte bleiben unangetastet.';
    }
  }

  // ── Vermutete Herkunft der dunklen Anmeldungen (Live-Aggregat) ──────────────
  // Das Live-Fundament unter der Schätzung: je dunkler Anmeldung der letzten 14
  // Tage der zeitlich nächste Kurzlink-Klick (aus sommer2026_ereignisse) – ein
  // Indiz, keine Messung. Atmet mit dem 60-Sekunden-Takt. Ordnet die Klicks nach
  // vermuteter Aktivität, plus die Zahl der dunklen ohne zeitnahen Klick.
  function renderVermutet(rows){
    if (!el('vermutetList')) return;
    var host = el('vermutetList'); host.innerHTML = '';
    var dunkel = (rows || []).filter(function(r){ return !r.utm_source && !r.utm_content; });
    var mitHinweis = dunkel.filter(function(r){ return r.vermutet_code; });
    var agg = {};
    mitHinweis.forEach(function(r){
      var label = [r.vermutet_source, r.vermutet_content].filter(Boolean).join(' · ') || r.vermutet_code;
      agg[label] = (agg[label] || 0) + 1;
    });
    var items = Object.keys(agg).map(function(k){ return { label:k, n:agg[k] }; })
      .sort(function(a, b){ return b.n - a.n; });
    if (el('vermutetKopf')){
      el('vermutetKopf').textContent = 'Vermutete Herkunft der ' + fmt(dunkel.length) +
        ' Anmeldungen ohne UTM der letzten 14 Tage – Indiz, keine Messung';
    }
    if (!dunkel.length){
      host.innerHTML = '<div class="empty">In den letzten 14 Tagen kam keine Anmeldung ohne UTM.</div>';
      return;
    }
    items.forEach(function(x){
      var row = document.createElement('div'); row.className = 'motrow';
      row.innerHTML = '<span class="mc"></span><span class="mn"></span>';
      row.querySelector('.mc').textContent = x.label;
      row.querySelector('.mn').textContent = fmt(x.n);
      host.appendChild(row);
    });
    var ohneHinweis = dunkel.length - mitHinweis.length;
    if (ohneHinweis > 0){
      var row = document.createElement('div'); row.className = 'motrow qz-rest';
      row.innerHTML = '<span class="mc"></span><span class="mn"></span>';
      row.querySelector('.mc').textContent = 'ohne zeitnahen Klick · Direkt oder Organik';
      row.querySelector('.mn').textContent = fmt(ohneHinweis);
      host.appendChild(row);
    }
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
          // Reichweite und Klicks fliessen in die Gebiete – darum Zeitband, Protokoll
          // UND (auf dem Cockpit) die Gebiete-Liste neu laden. Die Renderer sind
          // element-gewächtert; auf der Aktivitäten-Seite greift nur das Erste.
          Promise.all([rpc('sommer2026_massnahmen_public'), rpc('sommer2026_links_public'), rpc('sommer2026_attribution')])
            .then(function(res){
              var rows = res[0] || [];
              renderZeitband(rows); renderMassnahmen(rows);
              renderGebiete(res[2] || [], res[1] || [], rows, []);
            })
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
      '«vermutet» = der zeitlich nächste Kurzlink-Klick (bis 90 Minuten davor) auf einen passenden Kampagnen-Link – ein Indiz, keine Messung; gezählt wird es nirgends. ' +
      'Bei einem Weg, der fast alle Klicks stellt, steht dieses Indiz zufällig daneben und trägt nichts.';
    host.appendChild(note);
  }

  // ── Laden ──────────────────────────────────────────────────────────────────
  // Der Trichter-RPC wird nicht mehr abgerufen: seine vier Summen stehen jetzt
  // je Gebiet in der Gebiete-Liste, wo sie etwas aussagen. Alles andere bleibt.
  function load(){
    renderQuelleSocial();
    // Ereignis-Protokoll separat laden: fällt der RPC aus, bleibt der Rest des
    // Cockpits vollständig – nur die Liste meldet sich als nicht ladbar. Speist
    // sowohl «Was ist passiert?» als auch das Live-Aggregat der vermuteten Herkunft.
    if (el('evList') || el('vermutetList')) rpc('sommer2026_ereignisse')
      .then(function(rows){ renderEreignisse(rows); renderVermutet(rows); })
      .catch(function(){
        if (el('evList')) el('evList').innerHTML = '<div class="err">nicht ladbar</div>';
        if (el('vermutetList')) el('vermutetList').innerHTML = '<div class="err">nicht ladbar</div>';
      });
    if(CONFIG.zahlenProvisorisch && el('provisorisch')){
      el('provisorisch').textContent = 'Zielmarken, Preise und die Bleibe-Quote sind vorläufig hinterlegt – sobald die echten Werte gesetzt sind, rechnet das Cockpit unverändert weiter.';
    }
    Promise.all([ rpc('sommer2026_stats'), rpc('sommer2026_timeline'), rpc('sommer2026_kohorten'), rpc('sommer2026_kanaele'),
                  rpc('sommer2026_attribution'), rpc('sommer2026_massnahmen_public'), rpc('sommer2026_kosten_public'),
                  rpc('sommer2026_multi_liste'), rpc('sommer2026_multi_protokoll'), rpc('sommer2026_links_public') ])
      .then(function(res){
        var stats = res[0] || [], timeline = res[1] || [], kohorten = res[2] || [], kanaele = res[3] || [];
        var attribution = res[4] || [], massnahmen = res[5] || [], kostenPosten = res[6] || [];
        muListe = res[7] || []; muProto = res[8] || [];
        var links = res[9] || [];
        var total = stats.reduce(function(s, r){ return s + Number(r.n); }, 0);
        var revenue = projectRevenue(stats);
        // 1 Stand · 2 Gebiete · 3 Züge · 4 Belege – in dieser Reihenfolge gelesen.
        renderStand(total, timeline);
        renderStroeme(stats, total);
        renderGebiete(attribution, links, massnahmen, kanaele);
        renderZuege(links, massnahmen, attribution, timeline, total);
        renderDunkelfeld(kanaele, attribution);
        renderMotive(attribution);
        renderTarif(stats);
        renderCohort(kohorten, revenue);
        // Schwesterseiten (element-gewächtert, hier ohne Wirkung).
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
        ['gebieteListe','zuegeListe'].forEach(function(id){ var e = el(id); if (e) e.innerHTML = '<div class="err">nicht ladbar</div>'; });
      });
  }

  load();
  setInterval(load, REFRESH);
