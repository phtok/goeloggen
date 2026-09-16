#!/usr/bin/env node
/* Tagungsprogramm · Webseite holen (Kommandozeile)
   ---------------------------------------------------------------------------
   Holt die Programmseite von agriculture-conference.org und schreibt den Stand
   nach webseite.json. Genau das macht auch der Knopf «Von der Webseite holen»
   in der Vorschau – mit demselben Leser (webseite-lesen.js), nur ohne Browser.

     node apps/lt-programm/holen.mjs              # holen und schreiben
     node apps/lt-programm/holen.mjs --pruefen    # nur vergleichen (Exit 1 = geändert)
     node apps/lt-programm/holen.mjs --datei p.html [--start s.html]   # aus Dateien lesen
     node apps/lt-programm/holen.mjs --umbrueche LT-gesetzt.idml
         Von Hand gesetzte Zeilenumbrüche aus einem InDesign-Export zurück in
         blatt.json holen – damit sie den nächsten Export überleben.

   Ohne Fremdpakete; braucht Node ≥ 18.
   ------------------------------------------------------------------------- */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';
import { webseiteLesen, URL_PROGRAMM, URL_START } from './webseite-lesen.js';
import { komponieren, absatzText } from './programm.js';

const HIER = path.dirname(fileURLToPath(import.meta.url));
const ZIEL = path.join(HIER, 'webseite.json');
const argv = process.argv.slice(2);
const arg = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const lies = (p) => JSON.parse(fs.readFileSync(path.join(HIER, p), 'utf8'));

async function holen(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'goetheanum-werkzeuge/lt-programm' } });
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return r.text();
}

// --------------------------------------------------------- Umbrüche ernten

/* Liest die Slot-Rahmen aus einem von Hand gesetzten IDML und vergleicht sie
   mit dem, was die Daten ergeben würden. Wo sich beide nur durch Zeilenumbrüche
   unterscheiden, wandert die gesetzte Fassung als Überschreibung in blatt.json –
   der nächste Export bringt sie dann von selbst mit. */
function umbrueche(idmlPfad) {
  const bytes = fs.readFileSync(idmlPfad);
  const dateien = zipLesenNode(bytes);
  const slots = lies('vorlage/slots.json');
  const modell = komponieren(lies('webseite.json'), lies('blatt.json'));
  const blatt = lies('blatt.json');
  const nackt = (s) => String(s).replace(/[\s\u2028\u2002]+/g, '').trim();
  const gefunden = [];

  const storyText = (sid) => {
    const xml = dateien.get(`Stories/Story_${sid}.xml`);
    if (!xml) return null;
    const absaetze = [];
    for (const psr of xml.split('<ParagraphStyleRange').slice(1)) {
      const stil = (psr.match(/AppliedParagraphStyle="ParagraphStyle\/([^"]*)"/) || [])[1] || '';
      let t = '';
      for (const stueck of psr.split(/<CharacterStyleRange/).slice(1)) {
        const roh = stueck.split('</ParagraphStyleRange>')[0];
        for (const m of roh.matchAll(/<Content>([\s\S]*?)<\/Content>|<Br \/>/g)) {
          t += m[1] !== undefined ? m[1].replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>') : '';
        }
      }
      absaetze.push({ stil, text: t.replace(/\u2028/g, '\n') });
    }
    return absaetze;
  };

  // Arbeitsgruppen: Titel und Namen je Nummer
  const ag = storyText(slots.slots.arbeitsgruppen.story) || [];
  const proNr = new Map();
  let nr = null;
  for (const a of ag) {
    const m = /^(\d{1,2}) · /.exec(a.text.trim());
    if (a.stil.includes('Sprache') && m) { nr = m[1]; proNr.set(nr, []); continue; }
    if (nr) proNr.get(nr).push(a);
  }
  blatt.arbeitsgruppen = blatt.arbeitsgruppen || {};
  for (const gruppe of modell.arbeitsgruppen) {
    const gesetzt = proNr.get(String(gruppe.nr));
    if (!gesetzt) continue;
    const felder = [['titel_1', 0], ['titel_2', gruppe.titel_2 ? 1 : -1], ['namen', gruppe.titel_2 ? 2 : 1]];
    for (const [feld, i] of felder) {
      if (i < 0 || !gesetzt[i]) continue;
      const soll = gruppe[feld];
      const ist = gesetzt[i].text.replace(/\n+$/, '');
      if (soll !== ist && nackt(soll) === nackt(ist)) {
        blatt.arbeitsgruppen[String(gruppe.nr)] = { ...(blatt.arbeitsgruppen[String(gruppe.nr)] || {}), [feld]: ist };
        gefunden.push(`AG ${gruppe.nr} · ${feld}`);
      }
    }
  }

  // Plenum: erster Absatz je Rahmen (die Titelzeile)
  blatt.plenum = blatt.plenum || {};
  for (const [name, slot] of Object.entries(slots.slots)) {
    if (slot.art !== 'zeitplan' || slot.nur_pruefen) continue;
    const gesetzt = storyText(slot.story);
    const soll = modell.slots[name];
    if (!gesetzt || !soll || !soll.length) continue;
    const ist = gesetzt[0].text.replace(/\n+$/, '');
    const sollText = absatzText(soll[0]);
    if (ist !== sollText && nackt(ist) === nackt(sollText)) {
      const [en, de] = ist.split('\n');
      if (en && de) {
        blatt.plenum[name] = { ...(blatt.plenum[name] || {}), titel_en: en, titel_de: de };
        gefunden.push(`${name} · Titel`);
      }
    }
  }

  if (!gefunden.length) { console.log('  = keine von Hand gesetzten Umbrüche gefunden, die den Daten entsprechen'); return 0; }
  fs.writeFileSync(path.join(HIER, 'blatt.json'), `${JSON.stringify(blatt, null, 2)}\n`);
  console.log(`  ✓ ${gefunden.length} Umbrüche in blatt.json übernommen:`);
  gefunden.forEach((g) => console.log(`      ${g}`));
  return 0;
}

/* Kleiner Zip-Leser für Node (der Browser-Weg steht in idml-export.js). */
function zipLesenNode(bytes) {
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  let eocd = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 70000); i--) {
    if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('Kein Zip-Endverzeichnis – ist das ein IDML?');
  const anzahl = dv.getUint16(eocd + 10, true);
  let p = dv.getUint32(eocd + 16, true);
  const aus = new Map();
  for (let n = 0; n < anzahl; n++) {
    const methode = dv.getUint16(p + 10, true);
    const compSize = dv.getUint32(p + 20, true);
    const nameLen = dv.getUint16(p + 28, true);
    const extraLen = dv.getUint16(p + 30, true);
    const commentLen = dv.getUint16(p + 32, true);
    const lokal = dv.getUint32(p + 42, true);
    const name = new TextDecoder().decode(bytes.subarray(p + 46, p + 46 + nameLen));
    const start = lokal + 30 + dv.getUint16(lokal + 26, true) + dv.getUint16(lokal + 28, true);
    const roh = bytes.subarray(start, start + compSize);
    if (!name.endsWith('/')) {
      aus.set(name, new TextDecoder().decode(methode === 8 ? zlib.inflateRawSync(roh) : roh));
    }
    p += 46 + nameLen + extraLen + commentLen;
  }
  return aus;
}

// ------------------------------------------------------------------ Ablauf

async function main() {
  if (argv.includes('--umbrueche')) return umbrueche(arg('--umbrueche'));

  const pruefen = argv.includes('--pruefen');
  const [programmHtml, startHtml] = argv.includes('--datei')
    ? [fs.readFileSync(arg('--datei'), 'utf8'), argv.includes('--start') ? fs.readFileSync(arg('--start'), 'utf8') : null]
    : await Promise.all([holen(URL_PROGRAMM), holen(URL_START)]);

  const neu = webseiteLesen(programmHtml, startHtml);
  const nPl = neu.plenum.reduce((n, t) => n + t.veranstaltungen.length, 0);
  console.log(`  Webseite: ${nPl} Plenumsveranstaltungen an ${neu.plenum.length} Tagen, ${neu.arbeitsgruppen.length} Arbeitsgruppen`);
  if (!nPl || !neu.arbeitsgruppen.length) {
    console.log('  ! Seite nicht wie erwartet aufgebaut – nichts geschrieben');
    return 2;
  }
  const alt = fs.existsSync(ZIEL) ? JSON.parse(fs.readFileSync(ZIEL, 'utf8')) : {};
  if (alt.pruefsumme === neu.pruefsumme) { console.log('  = unverändert gegenüber dem Stand'); return 0; }
  if (alt.pruefsumme) console.log('  ≠ die Webseite hat sich gegenüber dem Stand geändert');
  if (!neu.tagung.jahr && alt.tagung) neu.tagung = alt.tagung;
  neu.stand = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  fs.writeFileSync(ZIEL, `${JSON.stringify(neu, null, 1)}\n`);
  console.log(`  ✓ geschrieben: apps/lt-programm/webseite.json`);
  return pruefen ? 1 : 0;
}

process.exit(await main());
