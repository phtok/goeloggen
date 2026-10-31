/* Tagungs-Reader · IDML-Export
   ---------------------------------------------------------------------------
   Die Vorlage (vorlage/LT27-Reader.idml) bleibt das Dokument. Geändert werden
   nur: Stories (Ersetzungen je <Content>, überschriebene Rahmen per
   Textvergleich mit der Vorlage), Farbwerte der Jahrgangsfarben und der
   Druckbogen der Seiten 2–3: die alte Karte fliegt, die Karte des
   Kartentools kommt als native Objekte (kartenObjekte aus
   apps/karten-generator/idml.js) auf eigene Ebenen.
   Geliefert wird ein ZIP: <name>.idml, Links/ (Grundkarte, Logo als PDF),
   Document fonts/ (Hausschrift, OFL).
   Spezifikation: docs/specs/lt-reader-idml.md
   ------------------------------------------------------------------------- */
import { zipLesen, zipSchreiben } from '../lt-programm/idml-export.js';
import { kartenObjekte, farbfeldXml, ebeneXml } from '../karten-generator/idml.js?v=2026-10-31';

const te = new TextEncoder();
const td = new TextDecoder('utf-8');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const escA = (s) => esc(s).replace(/"/g, '&quot;');
const ent = (s) => String(s).replace(/&(lt|gt|quot|apos|amp|#x([0-9a-fA-F]+)|#(\d+));/g, (m, k, h, d) =>
  h ? String.fromCodePoint(parseInt(h, 16)) : d ? String.fromCodePoint(+d) : { lt: '<', gt: '>', quot: '"', apos: "'", amp: '&' }[k]);

const SEITENOBJEKTE = new Set(['Group', 'Polygon', 'Rectangle', 'Oval', 'GraphicLine', 'TextFrame', 'Button', 'MultiStateObject', 'EPSText', 'FormField', 'CheckBox', 'ComboBox', 'ListBox', 'RadioButton', 'TextBox', 'SignatureField', 'HtmlItem']);

/* ------------------------------------------------------------ XML-Lesen */

// Öffnende, schliessende und leere Tags mit Tiefe – genug für die
// wohlgeformten Teile eines IDML (Attributwerte stehen in "…").
const TAG = /<(\/?)([\w:]+)((?:\s+[\w:]+="[^"]*")*)\s*(\/?)>/g;

// Direkte Kinder eines Elements (start/ende im Text, Name, Kopf-Tag).
function kinder(xml, von, bis) {
  const aus = [];
  let tiefe = 0, offen = null;
  TAG.lastIndex = von;
  let m;
  while ((m = TAG.exec(xml)) && m.index < bis) {
    const [ganz, zu, name, , leer] = m;
    if (zu) { tiefe--; if (tiefe === 0 && offen) { aus.push({ ...offen, ende: m.index + ganz.length }); offen = null; } continue; }
    if (tiefe === 0) {
      if (leer) aus.push({ name, start: m.index, ende: m.index + ganz.length, kopf: ganz });
      else { offen = { name, start: m.index, kopf: ganz }; tiefe = 1; }
    } else if (!leer) tiefe++;
  }
  return aus;
}

/* ------------------------------------------------------------ Stories

   Überschriebene Rahmen werden nicht neu aufgebaut, sondern mit dem Text
   der Vorlage verglichen (zeichengenau, Myers-Diff): nur die Änderungen
   wandern in die <Content>-Knoten. So bleibt alles, was die Vorschau nicht
   zeigt und das Absatzmodell nicht trägt – verankerte Objekte, Hyperlinks,
   Spalten- und Rahmenumbrüche, Kerning, Sonderzeichen –, wie es war.
   Gelesen wird wie in der Vorschau (storyAbsaetze in idml-seite.js): Text
   aus <Content> und <Br/>, die direkt in einem CharacterStyleRange unter
   einem ParagraphStyleRange stehen. */

// Text-Stellen der Story in Lesereihenfolge: { start, ende, text } – Br als «\n».
function textStellen(xml) {
  const stellen = [], stapel = [];
  TAG.lastIndex = 0;
  let m;
  while ((m = TAG.exec(xml))) {
    const [ganz, zu, name, , leer] = m;
    if (zu) { stapel.pop(); continue; }
    const imLauf = stapel[stapel.length - 1] === 'CharacterStyleRange' && stapel[stapel.length - 2] === 'ParagraphStyleRange';
    if (imLauf && name === 'Br') stellen.push({ start: m.index, ende: m.index + ganz.length, text: '\n' });
    else if (imLauf && name === 'Content' && !leer) {
      const zuTag = xml.indexOf('</Content>', m.index);
      stellen.push({ start: m.index, ende: zuTag + 10, text: ent(xml.slice(m.index + ganz.length, zuTag)) });
      TAG.lastIndex = zuTag + 10;
      continue;
    } else if (imLauf && name === 'Content') stellen.push({ start: m.index, ende: m.index + ganz.length, text: '' });
    if (!leer) stapel.push(name);
  }
  return stellen;
}

// Myers-Diff über Zeichen: [['=', text] | ['-', text] | ['+', text]].
function diff(a, b) {
  let p = 0;
  while (p < a.length && p < b.length && a[p] === b[p]) p++;
  let s = 0;
  while (s < a.length - p && s < b.length - p && a[a.length - 1 - s] === b[b.length - 1 - s]) s++;
  const A = a.slice(p, a.length - s), B = b.slice(p, b.length - s);
  const n = A.length, m = B.length, max = n + m, off = max + 1;
  const v = new Int32Array(2 * max + 3), spur = [];
  let fertig = n === 0 && m === 0;
  for (let d = 0; d <= max && !fertig; d++) {
    spur.push(v.slice());
    for (let k = -d; k <= d; k += 2) {
      let x = k === -d || (k !== d && v[off + k - 1] < v[off + k + 1]) ? v[off + k + 1] : v[off + k - 1] + 1;
      let y = x - k;
      while (x < n && y < m && A[x] === B[y]) { x++; y++; }
      v[off + k] = x;
      if (x >= n && y >= m) { fertig = true; break; }
    }
  }
  const ops = [];
  let x = n, y = m;
  for (let d = spur.length - 1; d >= 0 && (x > 0 || y > 0); d--) {
    const w = spur[d], k = x - y;
    const vonOben = k === -d || (k !== d && w[off + k - 1] < w[off + k + 1]);
    const pk = vonOben ? k + 1 : k - 1;
    const px = w[off + pk], py = px - pk;
    while (x > px && y > py) { ops.push(['=', A[--x]]); y--; }
    if (d > 0) { if (vonOben) ops.push(['+', B[--y]]); else ops.push(['-', A[--x]]); }
  }
  ops.reverse();
  const aus = [];
  const dazu = (t, c) => { if (aus.length && aus[aus.length - 1][0] === t) aus[aus.length - 1][1] += c; else aus.push([t, c]); };
  if (p) dazu('=', a.slice(0, p));
  ops.forEach(([t, c]) => dazu(t, c));
  if (s) dazu('=', a.slice(a.length - s));
  return aus;
}

// Text einer Stelle als XML: «\n» wird <Br />, leere Stücke fallen weg.
const stelleXml = (t) => t.split('\n').map((teil) => (teil ? `<Content>${esc(teil)}</Content>` : '')).join('<Br />');

/* Eine überschriebene Story auf den Text des Absatzmodells bringen. */
export function storyNeu(xml, absaetze) {
  const stellen = textStellen(xml);
  if (!stellen.length) return xml;
  const alt = stellen.map((st) => st.text).join('');
  let neu = absaetze.map((a) => (a.runs || []).map((r) => r.text).join('')).join('\n');
  // Die Vorschau zeigt keinen leeren Absatz nach einem letzten Umbruch.
  if (alt.endsWith('\n') && !neu.endsWith('\n')) neu += '\n';
  if (alt === neu) return xml;
  // Jedes Zeichen von «alt» gehört einer Stelle; Neues hängt an der Stelle
  // des Zeichens davor (am Anfang: an der ersten Stelle).
  const besitz = [];
  stellen.forEach((st, i) => { for (let k = 0; k < st.text.length; k++) besitz.push(i); });
  const ziel = stellen.map(() => '');
  let i = 0;
  for (const [typ, text] of diff(alt, neu)) {
    if (typ === '+') { ziel[i > 0 ? besitz[i - 1] : 0] += text; continue; }
    for (const c of text) { if (typ === '=') ziel[besitz[i]] += c; i++; }
  }
  let aus = '', pos = 0;
  stellen.forEach((st, k) => {
    aus += xml.slice(pos, st.start) + (ziel[k] === st.text ? xml.slice(st.start, st.ende) : stelleXml(ziel[k]));
    pos = st.ende;
  });
  return aus + xml.slice(pos);
}

/* Ersetzungen je <Content> (die Vorschau ersetzt je Lauf, ein Lauf ist ein
   <Content>). Gibt null zurück, wenn sich nichts ändert. */
export function storyErsetzen(xml, ersetzen) {
  let anders = false;
  const neu = xml.replace(/<Content>([^<]*)<\/Content>/g, (ganz, roh) => {
    const alt = ent(roh), text = ersetzen(alt);
    if (text === alt) return ganz;
    anders = true;
    return `<Content>${esc(text)}</Content>`;
  });
  return anders ? neu : null;
}

/* ------------------------------------------------------------ Farben */

const rgbWert = (hex) => [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16)).join(' ');

function farbenSetzen(dateien, swatches, protokoll) {
  const eintraege = Object.entries(swatches || {}).filter(([, hex]) => /^#[0-9a-f]{6}$/i.test(hex));
  if (!eintraege.length) return;
  let graphic = td.decode(dateien.get('Resources/Graphic.xml'));
  const umhaengen = new Map();                       // Tint/… → neues Farbfeld
  for (const [ref, hex] of eintraege) {
    const self = escA(ref);
    const farbe = new RegExp(`<Color Self="${self.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"[^>]*>`);
    const m = graphic.match(farbe);
    if (m) {
      const kopf = m[0].replace(/\sSpace="[^"]*"/, ' Space="RGB"').replace(/\sColorValue="[^"]*"/, ` ColorValue="${rgbWert(hex)}"`)
        .replace(/\sModel="[^"]*"/, ' Model="Process"');
      graphic = graphic.replace(m[0], kopf);
      protokoll.push(`Farbfeld ${ref.slice(6)} → ${hex}`);
    } else if (ref.startsWith('Tint/')) {
      const tm = graphic.match(new RegExp(`<Tint Self="${self.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"[^>]*Name="([^"]*)"`));
      const name = `${tm ? ent(tm[1]) : ref.slice(5)} Jahrgang`;
      const neu = `Color/${name}`;
      graphic = graphic.replace(/(<Color\b[^>]*\/>|<\/Color>)(?![\s\S]*(<Color\b[^>]*\/>|<\/Color>))/, (g) => `${g}\n\t${farbfeldXml(hex.toLowerCase(), neu)}`);
      umhaengen.set(self, escA(neu));
      protokoll.push(`Tönung → neues Farbfeld ${name} ${hex}`);
    }
  }
  dateien.set('Resources/Graphic.xml', te.encode(graphic));
  if (!umhaengen.size) return;
  for (const name of dateien.keys()) {
    if (!/^(Spreads|MasterSpreads|Stories)\//.test(name)) continue;
    let s = td.decode(dateien.get(name)), anders = false;
    for (const [alt, neu] of umhaengen) {
      if (!s.includes(`"${alt}"`)) continue;
      s = s.split(`"${alt}"`).join(`"${neu}"`); anders = true;
    }
    if (anders) dateien.set(name, te.encode(s));
  }
}

/* ------------------------------------------------------------ Karte */

/* Druckbogen der Seite 2: alte Objekte entfernen, Karten-Objekte einsetzen.
   Gibt die Stories der entfernten Rahmen zurück. */
function karteEinsetzen(dateien, spreadPfad, objekte) {
  const xml = td.decode(dateien.get(spreadPfad));
  const huelle = kinder(xml, 0, xml.length).find((k) => k.name === 'idPkg:Spread');
  const spread = kinder(xml, huelle.start + huelle.kopf.length, huelle.ende).find((k) => k.name === 'Spread');
  const innen = kinder(xml, spread.start + spread.kopf.length, spread.ende);
  const weg = innen.filter((k) => SEITENOBJEKTE.has(k.name));
  const stories = new Set();
  weg.forEach((k) => { for (const m of xml.slice(k.start, k.ende).matchAll(/<TextFrame\b[^>]*\sParentStory="([^"]*)"/g)) stories.add(m[1]); });
  let aus = '', pos = 0;
  for (const k of weg) { aus += xml.slice(pos, k.start); pos = k.ende; }
  const schluss = xml.lastIndexOf('</Spread>');
  aus += xml.slice(pos, schluss).replace(/\s+$/, '') + '\n' + objekte.join('\n') + '\n\t' + xml.slice(schluss);
  // Leere Zeilen, die die entfernten Objekte hinterlassen, zusammenziehen.
  dateien.set(spreadPfad, te.encode(aus.replace(/\n(?:[ \t]*\n)+/g, '\n')));
  return { stories, entfernt: weg.length };
}

/* ------------------------------------------------------------ Export

   e: { vorlage (Uint8Array), dateiname (…idml), ueberschrieben {story: absaetze},
        ersetzen(text, story) → text, swatches {ref: hex},
        karte: { seite: '2', teile (Kartentool.idmlTeile), sprache, schriften [{name, bytes}] } }
   → { bytes (ZIP), protokoll [] } */
export async function readerIdml(e) {
  const dateien = await zipLesen(e.vorlage);
  const protokoll = [];
  const lies = (name) => td.decode(dateien.get(name));
  let designmap = lies('designmap.xml');

  // --- Druckbogen der Karte finden (Spread mit der Seite «2»)
  const spreadPfade = [...designmap.matchAll(/<idPkg:Spread src="([^"]*)"/g)].map((m) => m[1]);
  const seite = (e.karte && e.karte.seite) || '2';
  const spreadPfad = spreadPfade.find((p) => dateien.has(p) && new RegExp(`<Page\\b[^>]*\\sName="${seite}"`).test(lies(p)));

  // --- Karte: alte Objekte raus, neue rein
  let neueStories = [];
  const alteStories = new Set();
  if (e.karte && spreadPfad) {
    const t = e.karte.teile;
    const sprache = e.karte.sprache === 'de' ? 'German: Swiss' : 'English: UK';
    const obj = kartenObjekte({ ...t, praefix: 'k', namen: 'Karte ', sprache });
    const { stories, entfernt } = karteEinsetzen(dateien, spreadPfad, obj.inhalt);
    stories.forEach((s) => alteStories.add(s));
    neueStories = obj.stories;
    protokoll.push(`Seiten 2–3: ${entfernt} Objekte der alten Karte entfernt (${stories.size} Rahmen), ${obj.inhalt.length} Objekte des Kartentools eingesetzt`);
    for (const s of stories) dateien.delete(`Stories/Story_${s}.xml`);
    for (const [sid, xml] of obj.stories) dateien.set(`Stories/Story_${sid}.xml`, te.encode(xml));

    // Formate, Farbfelder, Ebenen
    let styles = lies('Resources/Styles.xml');
    const ende = styles.indexOf('</RootParagraphStyleGroup>');
    styles = `${styles.slice(0, ende).replace(/\s+$/, '')}\n\t\t${obj.absatzformate.split('\n').join('\n\t\t')}\n\t${styles.slice(ende)}`;
    dateien.set('Resources/Styles.xml', te.encode(styles));
    let graphic = lies('Resources/Graphic.xml');
    const neueFarben = obj.farben.filter(([, self]) => !graphic.includes(`Self="${escA(self)}"`));
    graphic = graphic.replace(/(<Color\b[^>]*\/>|<\/Color>)(?![\s\S]*(<Color\b[^>]*\/>|<\/Color>))/, (g) => `${g}\n\t${neueFarben.map(([hex, self]) => farbfeldXml(hex, self)).join('\n\t')}`);
    dateien.set('Resources/Graphic.xml', te.encode(graphic));
    const letzteEbene = [...designmap.matchAll(/<Layer\b[^>]*(?:\/>|>[\s\S]*?<\/Layer>)/g)].pop();
    const ebenen = obj.ebenen.map(ebeneXml).join('\n');
    designmap = letzteEbene
      ? designmap.slice(0, letzteEbene.index + letzteEbene[0].length) + '\n' + ebenen + designmap.slice(letzteEbene.index + letzteEbene[0].length)
      : designmap.replace(/(<idPkg:MasterSpread\b)/, `${ebenen}\n$1`);
  }

  // --- Stories: Liste und Verweise nachführen
  if (alteStories.size || neueStories.length) {
    designmap = designmap.replace(/\sStoryList="([^"]*)"/, (m, liste) =>
      ` StoryList="${[...liste.split(/\s+/).filter((s) => s && !alteStories.has(s)), ...neueStories.map(([s]) => s)].join(' ')}"`);
    designmap = designmap.replace(/[ \t]*<idPkg:Story src="Stories\/Story_([^"]*)\.xml"\s*\/>\r?\n?/g, (m, s) => (alteStories.has(s) ? '' : m));
    const letzte = [...designmap.matchAll(/<idPkg:Story src="[^"]*"\s*\/>/g)].pop();
    const neu = neueStories.map(([s]) => `<idPkg:Story src="Stories/Story_${s}.xml" />`).join('\n\t');
    designmap = letzte
      ? designmap.slice(0, letzte.index + letzte[0].length) + '\n\t' + neu + designmap.slice(letzte.index + letzte[0].length)
      : designmap.replace('</Document>', `\t${neu}\n</Document>`);
  }
  dateien.set('designmap.xml', te.encode(designmap));

  // --- Texte
  let ersetzt = 0, neuGeschrieben = 0;
  for (const name of [...dateien.keys()]) {
    const m = name.match(/^Stories\/Story_(.+)\.xml$/);
    if (!m || neueStories.some(([s]) => s === m[1])) continue;
    const sid = m[1];
    const ueber = e.ueberschrieben && e.ueberschrieben[sid];
    if (ueber) { dateien.set(name, te.encode(storyNeu(lies(name), ueber))); neuGeschrieben++; continue; }
    if (!e.ersetzen) continue;
    const neu = storyErsetzen(lies(name), (t) => e.ersetzen(t, sid));
    if (neu != null) { dateien.set(name, te.encode(neu)); ersetzt++; }
  }
  protokoll.push(`Texte: ${ersetzt} Rahmen mit Ersetzungen, ${neuGeschrieben} Rahmen neu geschrieben`);

  // --- Farben
  farbenSetzen(dateien, e.swatches, protokoll);

  // --- Paket
  const idml = await zipSchreiben(dateien);
  const paket = new Map([[e.dateiname, idml]]);
  const links = (e.karte && e.karte.teile && e.karte.teile.links) || {};
  Object.values(links).filter((l) => l && l.bytes).forEach((l) => paket.set(`Links/${l.name}`, l.bytes));
  ((e.karte && e.karte.schriften) || []).forEach((f) => paket.set(`Document fonts/${f.name}`, f.bytes));
  return { bytes: await zipSchreiben(paket), protokoll };
}
