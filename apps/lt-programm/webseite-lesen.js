/* Tagungsprogramm · die Webseite lesen
   ---------------------------------------------------------------------------
   Macht aus den HTML-Seiten von agriculture-conference.org die Datei
   webseite.json: Plenum je Tag, Arbeitsgruppen am Vor- und Nachmittag,
   dazu Motto und Datum von der Startseite.

   EIN Leser für beide Wege – im Browser hinter dem Knopf «Von der Webseite
   holen» (über die Edge Function lt-programm-quelle, die CORS erlaubt) und
   in Node über holen.mjs. Kein zweiter Weg, keine zweite Wahrheit.

   Aufbau der Programmseite (Stand September 2026):
     <h4>Mittwoch, 3. Februar</h4>
       <p><strong>15:00</strong> • <strong>Opening</strong> • <strong>Eröffnung</strong></p>
       <p>Ueli Hurter, Eduardo Rincon • DE, EN</p>
       <br>                                    ← trennt die Veranstaltungen
     <h4>01 • Titel der Arbeitsgruppe</h4>
       <p>Namen • DE, EN • Raum</p> …
   Fett = Titel, mager = Art («Michaelbrief · Michael Letter») oder Mitwirkende.
   ------------------------------------------------------------------------- */

export const URL_PROGRAMM = 'https://www.agriculture-conference.org/programm';
export const URL_START = 'https://www.agriculture-conference.org/';

const SPRACHCODE = /^(DE|EN|FR|ES|IT|NL|RU|PT|CN|ZH|TR|FI|PL|SV|NO|DA|中文)$/;
const ZEIT = /^(\d{1,2})[:.](\d{2})$/;
const WOCHENTAG = /^(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag),\s*(\d{1,2})\.\s*(\S+)/;
const AG_KOPF = /^(\d{1,2})\s*•\s*(.+)$/;
const PLATZHALTER = /^(titel|title|n\.?n\.?|tba|tbd|folgt)$/i;

/* Art der Veranstaltung in beiden Sprachen – damit «Michaelbrief · Michael
   Letter» als Art erkannt wird und nicht als Titel, und damit die fehlende
   Sprache ergänzt werden kann. */
export const ART = [
  ['Opening', 'Eröffnung'], ['Closing', 'Abschluss'], ['Lecture', 'Vortrag'],
  ['Lectures', 'Vorträge'], ['Presentation', 'Präsentation'], ['Presentations', 'Präsentationen'],
  ['Michael Letter', 'Michaelbrief'], ['Panel Conversation', 'Panelgespräch'],
  ['Panel Conversation', 'Podiumsgespräch'], ['Conversation', 'Gespräch'],
  ['Eurythmy Performance', 'Eurythmie-Aufführung'], ['Eurythmy', 'Eurythmie'],
  ['Festive evening', 'Festlicher Abend'], ['Workshop', 'Arbeitsgruppe'],
  ['Guided tour', 'Führung'], ['Class Lesson', 'Klassenstunde'],
];
const ART_EN = new Map(ART.map(([en, de]) => [de.toLowerCase(), en]));
const ART_DE = new Map(ART.map(([en, de]) => [en.toLowerCase(), de]));

export function sauber(text) {
  return String(text).replace(/\u200e|\u200f/g, '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
}

/* Benannte Entitäten: die häufigen ausgeschrieben, die akzentuierten über die
   Regel «Buchstabe + Akzentname» (&iacute; &uuml; &ntilde; …) – die Tagungsseite
   liefert sie in vielen Sprachen. */
const ENTITAETEN = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: '\u00a0',
  szlig: 'ß', bull: '•', ndash: '–', mdash: '—', hellip: '…', middot: '·', deg: '°',
  rsquo: '\u2019', lsquo: '\u2018', ldquo: '\u201c', rdquo: '\u201d', laquo: '«', raquo: '»',
  lrm: '\u200e', rlm: '\u200f', shy: '\u00ad', ensp: '\u2002', emsp: '\u2003', thinsp: '\u2009' };

const AKZENT = { acute: '\u0301', grave: '\u0300', circ: '\u0302', tilde: '\u0303',
  uml: '\u0308', ring: '\u030a', cedil: '\u0327', slash: '\u0338', caron: '\u030c', macr: '\u0304' };

/* «&iacute;» → «í»: Buchstabe plus kombinierendes Zeichen, dann zusammengesetzt. */
function akzent(name) {
  const m = /^([a-zA-Z])(acute|grave|circ|tilde|uml|ring|cedil|slash|caron|macr)$/.exec(name);
  if (!m) return null;
  return (m[1] + AKZENT[m[2]]).normalize('NFC');
}

function entschluesseln(s) {
  return s.replace(/&(#x?[0-9a-fA-F]+|[a-zA-Z]+);/g, (ganz, e) => {
    if (e[0] === '#') return String.fromCodePoint(Number(e[1] === 'x' || e[1] === 'X' ? `0${e.slice(1)}` : e.slice(1)));
    if (ENTITAETEN[e] !== undefined) return ENTITAETEN[e];
    const a = akzent(e);
    return a !== null ? a : ganz;
  });
}

/* Die Seite in eine flache Folge von Blöcken zerlegen. Ein Block ist eine
   Überschrift, ein Absatz (mit seinen Teilen: fett oder mager), ein <br>
   (trennt Veranstaltungen) oder eine Listengrenze. Kein DOM nötig – derselbe
   Code läuft im Browser und in Node. */
export function bloecke(html) {
  const ohne = html.replace(/<(script|style|noscript|svg)\b[\s\S]*?<\/\1>/gi, '');
  const aus = [];
  let offen = null;
  let fett = 0;
  const STRUKTUR = new Set(['h1', 'h2', 'h3', 'h4', 'p']);
  const schliessen = () => {
    if (!offen) return;
    offen.segmente = offen.segmente.map((s) => ({ ...s, text: sauber(s.text) })).filter((s) => s.text);
    offen.text = sauber(offen.segmente.map((s) => s.text).join(' '));
    if (offen.text) aus.push(offen);
    offen = null; fett = 0;
  };
  const marke = /<\/?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>|([^<]+)/g;
  let m;
  while ((m = marke.exec(ohne))) {
    if (m[2] !== undefined) {
      if (!offen) continue;
      const text = entschluesseln(m[2]);
      const letzte = offen.segmente[offen.segmente.length - 1];
      if (letzte && letzte.laut === fett > 0) letzte.text += text;
      else offen.segmente.push({ text, laut: fett > 0 });
      continue;
    }
    const roh = m[0];
    const tag = m[1].toLowerCase();
    const zu = roh[1] === '/';
    if (tag === 'br' && !zu) {
      if (offen) offen.segmente.push({ text: ' ', laut: fett > 0 });
      else aus.push({ art: 'br', segmente: [], text: '' });
      continue;
    }
    if (tag === 'li') { schliessen(); aus.push({ art: zu ? '/li' : 'li', segmente: [], text: '' }); continue; }
    if (STRUKTUR.has(tag)) {
      schliessen();
      if (!zu) offen = { art: tag, segmente: [], text: '' };
      continue;
    }
    if ((tag === 'strong' || tag === 'b') && offen) fett += zu ? -1 : 1;
  }
  schliessen();
  return aus;
}

/* «DE, EN» → ['DE','EN']; sonst []. Der erste Eintrag muss ein Sprachcode
   sein, die weiteren dürfen ausgeschriebene Namen sein («EN, Māori»). */
export function sprachliste(teil) {
  const codes = teil.split(',').map(sauber).filter(Boolean);
  if (!codes.length || !SPRACHCODE.test(codes[0])) return [];
  return codes.every((c) => c.length <= 8) ? codes : [];
}

/* Einen Absatz an den Aufzählungspunkten in Teile schneiden, Fett/Mager je Teil
   erhalten: «15:00 • Opening • Eröffnung» → drei Teile. */
function teile(segmente) {
  const aus = [];
  for (const seg of segmente) {
    const stuecke = seg.text.split('•');
    stuecke.forEach((s, i) => {
      const text = sauber(s);
      if (i > 0 || !aus.length) aus.push({ text, laut: seg.laut });
      else if (text) {
        const letzter = aus[aus.length - 1];
        if (letzter.laut === seg.laut) letzter.text = sauber(`${letzter.text} ${text}`);
        else aus.push({ text, laut: seg.laut });
      }
    });
  }
  return aus.filter((t) => t.text);
}

/* Eine Veranstaltung aus ihren Absätzen bauen. */
function veranstaltung(absaetze) {
  const alle = absaetze.flatMap((p) => teile(p.segmente));
  const v = { zeit: null, titel_en: '', titel_de: '', art_en: '', art_de: '', sprachen: [], mitwirkende: [] };
  let i = 0;
  if (alle[0] && ZEIT.test(alle[0].text)) {
    const [, h, min] = alle[0].text.match(ZEIT);
    v.zeit = `${h.padStart(2, '0')}:${min}`;
    i = 1;
  }
  const rest = alle.slice(i);
  // Von hinten: Sprachliste, dann die mageren Teile = Mitwirkende.
  let ende = rest.length;
  if (ende && !rest[ende - 1].laut && sprachliste(rest[ende - 1].text).length) {
    v.sprachen = sprachliste(rest[ende - 1].text);
    ende -= 1;
  }
  const mit = [];
  while (ende > 0 && !rest[ende - 1].laut && !ART_EN.has(rest[ende - 1].text.toLowerCase())
         && !ART_DE.has(rest[ende - 1].text.toLowerCase())) {
    mit.unshift(rest[ende - 1].text);
    ende -= 1;
  }
  v.mitwirkende = mit.flatMap((z) => z.split(',').map(sauber)).filter(Boolean);
  // Was bleibt: fette Teile = Titel, magere = Art der Veranstaltung.
  const titel = [];
  for (const t of rest.slice(0, ende)) {
    if (t.laut && !ART_EN.has(t.text.toLowerCase()) && !ART_DE.has(t.text.toLowerCase())) titel.push(t.text);
    else if (ART_EN.has(t.text.toLowerCase())) { v.art_de = t.text; v.art_en = v.art_en || ART_EN.get(t.text.toLowerCase()); }
    else if (ART_DE.has(t.text.toLowerCase())) { v.art_en = t.text; v.art_de = v.art_de || ART_DE.get(t.text.toLowerCase()); }
    else if (t.text) titel.push(t.text);
  }
  // Titel: englisch zuerst, deutsch danach (so setzt die Seite es).
  v.titel_en = titel[0] || '';
  v.titel_de = titel[1] || '';
  if (PLATZHALTER.test(v.titel_en)) { v.titel_offen = true; v.titel_en = ''; }
  if (PLATZHALTER.test(v.titel_de)) { v.titel_offen = true; v.titel_de = ''; }
  if (!v.titel_en && !v.titel_de && !v.art_en && !v.art_de && !v.titel_offen) v.leer = true;
  if (v.mitwirkende.some((n) => /^N\.?\s?N\.?$/i.test(n))) v.namen_offen = true;
  return v;
}

export function plenumLesen(bl) {
  const tage = [];
  for (let i = 0; i < bl.length; i++) {
    const m = bl[i].art === 'h4' && WOCHENTAG.exec(bl[i].text);
    if (!m) continue;
    const tag = { wochentag: m[1], tag: Number(m[2]), monat: m[3], kopf: bl[i].text, veranstaltungen: [] };
    let gruppe = [];
    let letzteZeit = null;
    const abschliessen = () => {
      if (!gruppe.length) return;
      const v = veranstaltung(gruppe);
      gruppe = [];
      if (v.leer) return;
      if (!v.zeit) { v.zeit = letzteZeit; v.gleicher_block = true; }
      letzteZeit = v.zeit;
      tag.veranstaltungen.push(v);
    };
    for (i += 1; i < bl.length && !['h4', 'h2', '/li'].includes(bl[i].art); i++) {
      if (bl[i].art === 'br') abschliessen();
      else if (bl[i].art === 'p') gruppe.push(bl[i]);
    }
    abschliessen();
    i -= 1;
    if (tag.veranstaltungen.length) tage.push(tag);
  }
  return tage;
}

/* «Julia Wright, Stefan Doeblin • DE, EN • Raum» → Mitwirkende, Sprachen, Ort. */
function agKopfzeile(text) {
  const stuecke = text.split('•').map(sauber).filter(Boolean);
  const aus = { mitwirkende: [], sprachen: [], ort: '' };
  if (stuecke.length) aus.mitwirkende = stuecke.shift().split(',').map(sauber).filter(Boolean);
  for (const s of stuecke) {
    const sp = sprachliste(s);
    if (sp.length) aus.sprachen = sp; else aus.ort = s;
  }
  return aus;
}

export function arbeitsgruppenLesen(bl) {
  const bloecke_ag = { vormittag: [], nachmittag: [] };
  const fenster = {};
  let block = null;
  for (let i = 0; i < bl.length; i++) {
    const b = bl[i];
    if (b.art === 'h2') {
      const t = b.text.toLowerCase();
      block = t.includes('arbeitsgruppen') || t.includes('workshops')
        ? (t.includes('vormittag') || t.includes('morning') ? 'vormittag'
          : (t.includes('nachmittag') || t.includes('afternoon') ? 'nachmittag' : null)) : null;
      if (block) {
        for (let j = Math.max(0, i - 3); j < Math.min(bl.length, i + 4); j++) {
          if (bl[j].art === 'p' && /\d{1,2}[:.]\d{2}/.test(bl[j].text) && bl[j].text.includes('•')) {
            fenster[block] = bl[j].text; break;
          }
        }
      }
      continue;
    }
    const m = block && b.art === 'h4' && AG_KOPF.exec(b.text);
    if (!m) continue;
    const ag = { nr: Number(m[1]), block, titel_1: sauber(m[2]), titel_2: '',
      mitwirkende: [], sprachen: [], ort: '', text_1: [], text_2: [] };
    let erste = true;
    let zweite = false;
    for (i += 1; i < bl.length && !['h4', 'h2', '/li'].includes(bl[i].art); i++) {
      const p = bl[i];
      if (p.art !== 'p') continue;
      if (erste) { Object.assign(ag, agKopfzeile(p.text)); erste = false; continue; }
      const ganzFett = p.segmente.length && p.segmente.every((s) => s.laut);
      if (ganzFett && !zweite) { ag.titel_2 = p.text; zweite = true; continue; }
      if (p.text === p.text.toUpperCase() && p.text.length < 40) continue; // «PREPARE ONLINE»
      ag[zweite ? 'text_2' : 'text_1'].push(p.text);
    }
    i -= 1;
    bloecke_ag[block].push(ag);
  }
  for (const [b, liste] of Object.entries(bloecke_ag)) {
    for (const ag of liste) {
      ag.fenster = fenster[b] || '';
      const sp = ag.sprachen;
      ag.titel = {};
      if (sp.length) {
        ag.titel[sp[0]] = ag.titel_1;
        if (ag.titel_2) ag.titel[sp[1] || '?'] = ag.titel_2;
      } else {
        ag.titel['?'] = ag.titel_1;
      }
    }
  }
  return bloecke_ag;
}

export function startLesen(html) {
  const bl = bloecke(html);
  const aus = { motto: '', datum: '' };
  for (const b of bl) {
    if (b.art === 'h1' && !aus.motto) {
      aus.motto = sauber(b.text.split(/Landwirtschaftliche Tagung|Agriculture Conference/)[0]);
    }
  }
  const m = /(\d{1,2})\.\s*(?:bis|–|-)\s*(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]+)\s*(\d{4})/.exec(html);
  if (m) {
    aus.datum = `${m[1]}. bis ${m[2]}. ${m[3]} ${m[4]}`;
    aus.von = Number(m[1]); aus.bis = Number(m[2]);
    aus.monat = m[3]; aus.jahr = Number(m[4]);
  }
  // «… werden nach Deutsch, Englisch, … und Chinesisch gedolmetscht.»
  const nur = entschluesseln(html.replace(/<[^>]+>/g, ' '));
  const d = /werden nach ([^.]{3,160}?) gedolmetscht/.exec(nur);
  if (d) aus.dolmetsch = sauber(d[1]).replace(/\s+und\s+/g, ', ').split(',').map(sauber).filter(Boolean);
  return aus;
}

/* Beide Seiten → die Struktur, die webseite.json ablegt. */
export function webseiteLesen(programmHtml, startHtml) {
  const bl = bloecke(programmHtml);
  const ag = arbeitsgruppenLesen(bl);
  const daten = {
    quelle: URL_PROGRAMM,
    tagung: startHtml ? startLesen(startHtml) : {},
    plenum: plenumLesen(bl),
    arbeitsgruppen: [...ag.vormittag, ...ag.nachmittag],
  };
  daten.pruefsumme = pruefsumme(JSON.stringify(daten));
  return daten;
}

/* Kurze, stabile Prüfsumme (FNV-1a) – sagt nur, ob sich etwas geändert hat. */
export function pruefsumme(text) {
  let h1 = 0x811c9dc5, h2 = 0x01000193;
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 0x01000193) >>> 0;
    h2 = Math.imul(h2 ^ (c + i), 0x85ebca6b) >>> 0;
  }
  return (h1.toString(16).padStart(8, '0') + h2.toString(16).padStart(8, '0'));
}
