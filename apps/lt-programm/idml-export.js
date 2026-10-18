/* Tagungsprogramm · IDML-Export
   ---------------------------------------------------------------------------
   Schreibt das Blattmodell (programm.js) in die InDesign-Vorlage
   vorlage/LT27.idml. Es werden NUR die Textrahmen aus vorlage/slots.json
   neu befüllt – und auch von denen nicht die mit `nur_pruefen` (von Hand
   gesetzte Rahmen wie die unterschnittene Plakatzeile). Geometrie, Farben,
   Bilder, Absatz- und Zeichenformate und alles Übrige bleiben unangetastet. Die Formatierung jedes
   Rahmens wird aus seinem bisherigen Inhalt geklont: erster «Deutlich»-Lauf
   = laut, erster «Ruhig»-Lauf = ruhig, Absatzattribute je Position bzw.
   je Absatzformat-Name.

   IDML ist ein Zip. Damit die Seite ohne Fremdpaket auskommt, steckt hier
   ein kleiner Zip-Leser/-Schreiber (Store + Deflate über die Web-Streams
   CompressionStream/DecompressionStream – Browser und Node ≥ 18).

   Browser:  const idml = await exportIdml(vorlageBytes, modell, slots);
   Node:     node apps/lt-programm/idml-export.js [--ziel LT27-2027.idml]
   ------------------------------------------------------------------------- */

import { komponieren, abgleichen } from './programm.js';

// ---------------------------------------------------------------- Zip lesen

const td = new TextDecoder('utf-8');
const te = new TextEncoder();

async function pipe(bytes, stream) {
  const rs = new Blob([bytes]).stream().pipeThrough(stream);
  return new Uint8Array(await new Response(rs).arrayBuffer());
}
const inflateRaw = (b) => pipe(b, new DecompressionStream('deflate-raw'));
const deflateRaw = (b) => pipe(b, new CompressionStream('deflate-raw'));

export async function zipLesen(bytes) {
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  let eocd = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 70000); i--) {
    if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('Kein Zip-Endverzeichnis – ist das ein IDML?');
  const anzahl = dv.getUint16(eocd + 10, true);
  let p = dv.getUint32(eocd + 16, true);
  const eintraege = [];
  for (let n = 0; n < anzahl; n++) {
    if (dv.getUint32(p, true) !== 0x02014b50) throw new Error('Zip-Verzeichnis beschädigt');
    const methode = dv.getUint16(p + 10, true);
    const compSize = dv.getUint32(p + 20, true);
    const nameLen = dv.getUint16(p + 28, true);
    const extraLen = dv.getUint16(p + 30, true);
    const commentLen = dv.getUint16(p + 32, true);
    const lokal = dv.getUint32(p + 42, true);
    const name = td.decode(bytes.subarray(p + 46, p + 46 + nameLen));
    const lNameLen = dv.getUint16(lokal + 26, true);
    const lExtraLen = dv.getUint16(lokal + 28, true);
    const start = lokal + 30 + lNameLen + lExtraLen;
    const roh = bytes.subarray(start, start + compSize);
    eintraege.push({ name, methode, roh });
    p += 46 + nameLen + extraLen + commentLen;
  }
  const dateien = new Map();
  for (const e of eintraege) {
    if (e.name.endsWith('/')) continue;
    const daten = e.methode === 8 ? await inflateRaw(e.roh) : e.methode === 0 ? e.roh : null;
    if (!daten) throw new Error(`Zip-Methode ${e.methode} nicht unterstützt (${e.name})`);
    dateien.set(e.name, daten);
  }
  return dateien;
}

// ------------------------------------------------------------- Zip schreiben

const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
function crc32(b) {
  let c = 0xffffffff;
  for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function dosZeit(d = new Date()) {
  const zeit = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
  const datum = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  return { zeit, datum };
}

/* dateien: Map name → Uint8Array. «mimetype» wird als erster Eintrag
   unkomprimiert abgelegt, wie es IDML verlangt. */
export async function zipSchreiben(dateien) {
  const namen = [...dateien.keys()].sort((a, b) => (a === 'mimetype' ? -1 : b === 'mimetype' ? 1 : 0));
  const teile = [];
  const zentral = [];
  let offset = 0;
  const { zeit, datum } = dosZeit();
  for (const name of namen) {
    const daten = dateien.get(name);
    const stored = name === 'mimetype';
    const inhalt = stored ? daten : await deflateRaw(daten);
    const nameB = te.encode(name);
    const crc = crc32(daten);
    const lokal = new Uint8Array(30 + nameB.length);
    const dv = new DataView(lokal.buffer);
    dv.setUint32(0, 0x04034b50, true);
    dv.setUint16(4, 20, true);
    dv.setUint16(6, 0x0800, true);          // UTF-8-Namen
    dv.setUint16(8, stored ? 0 : 8, true);
    dv.setUint16(10, zeit, true); dv.setUint16(12, datum, true);
    dv.setUint32(14, crc, true);
    dv.setUint32(18, inhalt.length, true);
    dv.setUint32(22, daten.length, true);
    dv.setUint16(26, nameB.length, true);
    dv.setUint16(28, 0, true);
    lokal.set(nameB, 30);
    teile.push(lokal, inhalt);
    const z = new Uint8Array(46 + nameB.length);
    const zv = new DataView(z.buffer);
    zv.setUint32(0, 0x02014b50, true);
    zv.setUint16(4, 20, true); zv.setUint16(6, 20, true);
    zv.setUint16(8, 0x0800, true);
    zv.setUint16(10, stored ? 0 : 8, true);
    zv.setUint16(12, zeit, true); zv.setUint16(14, datum, true);
    zv.setUint32(16, crc, true);
    zv.setUint32(20, inhalt.length, true);
    zv.setUint32(24, daten.length, true);
    zv.setUint16(28, nameB.length, true);
    zv.setUint32(42, offset, true);
    z.set(nameB, 46);
    zentral.push(z);
    offset += lokal.length + inhalt.length;
  }
  const zStart = offset;
  let zLen = 0;
  for (const z of zentral) { teile.push(z); zLen += z.length; }
  const ende = new Uint8Array(22);
  const ev = new DataView(ende.buffer);
  ev.setUint32(0, 0x06054b50, true);
  ev.setUint16(8, namen.length, true); ev.setUint16(10, namen.length, true);
  ev.setUint32(12, zLen, true); ev.setUint32(16, zStart, true);
  teile.push(ende);
  const gesamt = teile.reduce((n, t) => n + t.length, 0);
  const aus = new Uint8Array(gesamt);
  let o = 0;
  for (const t of teile) { aus.set(t, o); o += t.length; }
  return aus;
}

// ------------------------------------------------------- Story neu schreiben

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const attr = (tag, name) => (tag.match(new RegExp(`\\s${name}="([^"]*)"`)) || [])[1];

/* Vorlage eines Rahmens zerlegen: Absätze mit Öffnungs-Tag und Läufen
   (Öffnungs-Tag ohne Spaltenumbruch + Properties-Block). */
function vorlageLesen(xml) {
  const psrRe = /<ParagraphStyleRange\b[^>]*>[\s\S]*?<\/ParagraphStyleRange>/g;
  const absaetze = [];
  let erste = -1; let letzteEnde = -1; let m;
  while ((m = psrRe.exec(xml))) {
    if (erste < 0) erste = m.index;
    letzteEnde = m.index + m[0].length;
    const psr = m[0];
    const open = psr.slice(0, psr.indexOf('>') + 1);
    const laeufe = [];
    const csrRe = /<CharacterStyleRange\b([^>]*)>([\s\S]*?)<\/CharacterStyleRange>/g;
    let c;
    while ((c = csrRe.exec(psr))) {
      const attrs = c[1].replace(/\sParagraphBreakType="[^"]*"/, '');
      const props = (c[2].match(/<Properties>[\s\S]*?<\/Properties>/) || [''])[0];
      laeufe.push({ attrs, props, schnitt: attr(c[1], 'FontStyle') || '' });
    }
    absaetze.push({ open, stil: (attr(open, 'AppliedParagraphStyle') || '').replace('ParagraphStyle/', ''), laeufe });
  }
  if (erste < 0) throw new Error('Rahmen ohne Absatz – kann die Vorlage nicht klonen');
  return { prefix: xml.slice(0, erste), suffix: xml.slice(letzteEnde), absaetze };
}

/* Ob ein Absatz über alle Spalten läuft, ist eine Aussage über den Inhalt
   (eine Überschrift spannt, eine Namenszeile nicht) – darum sagt es das Modell
   und nicht die Stelle, an der der Absatz in der Vorlage zufällig stand. */
function spanneSetzen(open, spanne) {
  if (!spanne) return open;
  const wert = spanne === 'alle' ? 'SpanColumns' : 'SingleColumn';
  return /SpanColumnType="/.test(open)
    ? open.replace(/SpanColumnType="[^"]*"/, `SpanColumnType="${wert}"`)
    : open.replace(/^<ParagraphStyleRange/, `<ParagraphStyleRange SpanColumnType="${wert}"`);
}

const istLaut = (l) => /Deutlich|Laut|Bold|Semibold/i.test(l.schnitt);
const istRuhig = (l) => /Ruhig|Klar|Leise|Regular|Light|Book/i.test(l.schnitt);

/* Schriftgrad und Zeilenabstand gehören dem Absatz, nicht dem Rahmen: fehlt dem
   Absatz der gesuchte Schnitt, wird der Lauf aus dem Rahmen geholt – aber auf
   die Grösse DIESES Absatzes gebracht. Sonst bekäme der Untertitel die 35 Punkt
   der Schlagzeile darüber. */
function angleichen(lauf, vorbild) {
  if (!lauf || !vorbild || lauf === vorbild) return lauf;
  const grad = (vorbild.attrs.match(/\sPointSize="([^"]*)"/) || [])[1];
  const zeilen = (vorbild.props.match(/<Leading type="unit">([^<]*)<\/Leading>/) || [])[1];
  let attrs = lauf.attrs;
  if (grad !== undefined) {
    attrs = /\sPointSize="/.test(attrs)
      ? attrs.replace(/\sPointSize="[^"]*"/, ` PointSize="${grad}"`)
      : `${attrs} PointSize="${grad}"`;
  }
  let props = lauf.props;
  if (zeilen !== undefined && /<Leading type="unit">/.test(props)) {
    props = props.replace(/<Leading type="unit">[^<]*<\/Leading>/, `<Leading type="unit">${zeilen}</Leading>`);
  }
  return { ...lauf, attrs, props };
}

function laufXml(lauf, text, br, typ) {
  const inhalt = text ? `<Content>${esc(text).replace(/\n/g, '\u2028')}</Content>` : '';
  return `\t\t\t<CharacterStyleRange${lauf.attrs}${typ ? ` ParagraphBreakType="${typ}"` : ''}>${lauf.props ? '\n\t\t\t\t' + lauf.props : ''}${inhalt ? '\n\t\t\t\t' + inhalt : ''}${br ? '\n\t\t\t\t<Br />' : ''}\n\t\t\t</CharacterStyleRange>\n`;
}

/* Absatzfolge (programm.js) in den Rahmen schreiben; gibt das neue Story-XML zurück. */
export function storySchreiben(xml, absaetze) {
  const v = vorlageLesen(xml);
  const alle = v.absaetze.flatMap((a) => a.laeufe);
  const storyLaut = alle.find(istLaut) || alle[0];
  const storyRuhig = alle.find(istRuhig) || alle.find((l) => l !== storyLaut) || alle[0];
  const nachStil = new Map();
  v.absaetze.forEach((a) => { if (!nachStil.has(a.stil)) nachStil.set(a.stil, a); });

  let aus = '';
  absaetze.forEach((roh, i) => {
    const a = typeof roh === 'string' ? { text: roh } : roh;
    const tpl = (a.stil && nachStil.get(a.stil)) || v.absaetze[Math.min(i, v.absaetze.length - 1)];
    const basis = tpl.laeufe.length ? tpl.laeufe : alle;
    // Erst die Läufe DIESES Absatzes, dann erst die des Rahmens – und die nur
    // auf die Grösse des Absatzes gebracht.
    const vorbild = basis[0];
    const laut = basis.find(istLaut) || angleichen(storyLaut, vorbild);
    const ruhig = basis.find(istRuhig) || basis.find((l) => l !== laut) || angleichen(storyRuhig, vorbild);
    let runs = [];
    if (a.runs) runs = a.runs.map((r) => ({ lauf: r.laut ? laut : ruhig, text: r.text || '' }));
    else if (a.text !== undefined) runs = [{ lauf: basis[0], text: a.text }];
    else {
      const beide = a.laut && a.ruhig;
      if (a.laut !== undefined) runs.push({ lauf: laut, text: beide ? `${a.laut}\u2002` : a.laut });
      if (a.ruhig !== undefined) runs.push({ lauf: ruhig, text: a.ruhig });
    }
    runs = runs.filter((r) => r.text !== '');
    if (!runs.length) runs = [{ lauf: basis[0] || storyRuhig, text: '' }];
    const folgt = i < absaetze.length - 1;          // danach kommt noch ein Absatz
    const umbruch = a.umbruch || null;                // Spaltenumbruch statt einfachem Absatzende
    let inner = '';
    // Ein Spaltenumbruch VOR dem Absatz: leerer Lauf, der in die nächste Spalte schiebt.
    if (a.umbruch_vor) inner += laufXml(runs[0].lauf, '', true, a.umbruch_vor);
    runs.forEach((r, k) => {
      const brHier = folgt && !umbruch && k === runs.length - 1;
      inner += laufXml(r.lauf, r.text, brHier, '');
    });
    if (umbruch && folgt) inner += laufXml(runs[runs.length - 1].lauf, '', true, umbruch);
    aus += `\t\t${spanneSetzen(tpl.open, a.spanne)}\n${inner}\t\t</ParagraphStyleRange>\n`;
  });
  return `${v.prefix}${aus.trimEnd()}${v.suffix}`;
}

// ------------------------------------------------------------------ Export

/* vorlageBytes: Uint8Array des IDML · modell: aus komponieren() · slots: vorlage/slots.json */
export async function exportIdml(vorlageBytes, modell, slots) {
  const dateien = await zipLesen(vorlageBytes);
  const protokoll = [];
  for (const [name, slot] of Object.entries(slots.slots)) {
    if (slot.nur_pruefen) { protokoll.push(`· ${name}: von Hand gesetzt – bleibt unangetastet`); continue; }
    const absaetze = modell.slots[name];
    if (absaetze === undefined) { protokoll.push(`· ${name}: kein Inhalt im Modell – Vorlage bleibt`); continue; }
    const pfad = `Stories/Story_${slot.story}.xml`;
    const alt = dateien.get(pfad);
    if (!alt) { protokoll.push(`✗ ${name}: ${pfad} fehlt in der Vorlage`); continue; }
    const liste = Array.isArray(absaetze) ? absaetze : [absaetze];
    dateien.set(pfad, te.encode(storySchreiben(td.decode(alt), liste)));
    protokoll.push(`✓ ${name}: ${liste.length} Absätze → ${slot.story}`);
  }
  const bytes = await zipSchreiben(dateien);
  return { bytes, protokoll };
}

// ---------------------------------------------------------------- Node-CLI

const istNode = typeof process !== 'undefined' && process.versions?.node;
if (istNode) {
  const [{ pathToFileURL }, fs, path] = await Promise.all([import('node:url'), import('node:fs'), import('node:path')]);
  if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
    const hier = path.dirname(new URL(import.meta.url).pathname);
    const argv = process.argv.slice(2);
    const arg = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
    const lies = (p) => JSON.parse(fs.readFileSync(path.join(hier, p), 'utf8'));
    const webseite = lies(arg('--webseite', 'webseite.json'));
    const blatt = lies(arg('--blatt', 'blatt.json'));
    const slots = lies('vorlage/slots.json');
    const vorlage = new Uint8Array(fs.readFileSync(path.join(hier, 'vorlage', slots.vorlage)));
    const modell = komponieren(webseite, blatt);
    const { bytes, protokoll } = await exportIdml(vorlage, modell, slots);
    const ziel = arg('--ziel', path.join(hier, `LT-${modell.tagung.jahr}-export.idml`));
    fs.writeFileSync(ziel, bytes);
    protokoll.forEach((z) => console.log(z));
    modell.hinweise.forEach((h) => console.log(`! ${h.art}: ${h.text}`));
    abgleichen(modell, slots).filter((a) => !a.stimmt).forEach((a) => console.log(`! abgleich: ${a.text}`));
    console.log(`geschrieben: ${ziel} (${bytes.length} Bytes)`);
  }
}
