#!/usr/bin/env node
/* Passt der Text in die Rahmen? — Platzprüfung für das Tagungsprogramm
   ---------------------------------------------------------------------------
   Setzt den Text jedes Rahmens mit der echten Hausschrift in Chromium und misst,
   wie hoch er baut — einmal für den neuen Export, einmal für die gesetzte
   Vorlage. Gemeldet wird, was WÄCHST: ein Rahmen, der mehr Höhe braucht als in
   der Fassung, die auf dem Blatt nachweislich funktioniert, schiebt Text aus
   dem Rahmen, und das sieht niemand, weil InDesign dazu nichts sagt.

     node tools/lt-programm-passt.mjs LT-2027.idml           # Export gegen die Vorlage
     node tools/lt-programm-passt.mjs neu.idml --gegen alt.idml
     node tools/lt-programm-passt.mjs LT-2027.idml --alle    # ganze Tabelle

   Warum verglichen und nicht absolut gerechnet: die gezeichnete Rahmenhöhe ist
   in diesem Dokument keine Schranke — viele Rahmen sind kleiner als ihre eigene
   Zeile und werden trotzdem gesetzt. Belastbar ist darum die Veränderung, nicht
   der absolute Wert.

   Grenzen: ohne Silbentrennung, ohne optischen Randausgleich, ohne
   Laufweiten-Feinheiten. Absatzabstände und Spaltenumbrüche sind drin. Die Zahl
   ist eine Warnung, kein Beweis — was wächst, gehört ins Blatt geschaut.
   ------------------------------------------------------------------------- */

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SLOTS = path.join(REPO, 'apps/lt-programm/vorlage/slots.json');
const SCHRIFTEN = path.join(REPO, 'assets/fonts/goetheanum/Fonts');
const argv = process.argv.slice(2);
const freie = argv.filter((a) => !a.startsWith('--'));
const datei = freie[0] || path.join(REPO, 'apps/lt-programm/vorlage/LT27.idml');
const referenz = argv.includes('--gegen')
  ? argv[argv.indexOf('--gegen') + 1]
  : (freie[0] ? path.join(REPO, 'apps/lt-programm/vorlage/LT27.idml') : null);
const alle = argv.includes('--alle');

// ------------------------------------------------------------------ Zip lesen
function zipLesen(bytes) {
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  let eocd = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 70000); i--) {
    if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('Kein Zip-Endverzeichnis – ist das ein IDML?');
  let p = dv.getUint32(eocd + 16, true);
  const aus = new Map();
  for (let n = 0; n < dv.getUint16(eocd + 10, true); n++) {
    const methode = dv.getUint16(p + 10, true);
    const gross = dv.getUint32(p + 20, true);
    const nameLen = dv.getUint16(p + 28, true);
    const lokal = dv.getUint32(p + 42, true);
    const name = new TextDecoder().decode(bytes.subarray(p + 46, p + 46 + nameLen));
    const start = lokal + 30 + dv.getUint16(lokal + 26, true) + dv.getUint16(lokal + 28, true);
    const roh = bytes.subarray(start, start + gross);
    if (!name.endsWith('/')) aus.set(name, new TextDecoder().decode(methode === 8 ? zlib.inflateRawSync(roh) : roh));
    p += 46 + nameLen + dv.getUint16(p + 30, true) + dv.getUint16(p + 32, true);
  }
  return aus;
}

const attr = (s, n) => (s.match(new RegExp(`\\s${n}="([^"]*)"`)) || [])[1];
const zahl = (s, n) => (attr(s, n) !== undefined ? Number(attr(s, n)) : undefined);

// --------------------------------------------------- Rahmen und Absätze lesen
function rahmenLesen(dateien) {
  const aus = new Map();
  for (const [name, xml] of dateien) {
    if (!name.startsWith('Spreads/')) continue;
    for (const roh of xml.split('<TextFrame ').slice(1)) {
      const kopf = roh.slice(0, roh.indexOf('>'));
      const sid = attr(kopf, 'ParentStory');
      const it = (attr(kopf, 'ItemTransform') || '1 0 0 1 0 0').split(' ').map(Number);
      const block = roh.split('</TextFrame>')[0];
      const punkte = [...block.matchAll(/Anchor="([-\d.e ]+)"/g)].map((m) => m[1].split(' ').map(Number));
      if (!punkte.length) continue;
      const xs = punkte.map((p) => p[0]); const ys = punkte.map((p) => p[1]);
      const pref = (block.match(/<TextFramePreference[^>]*>/) || [''])[0];
      const inset = (block.match(/<InsetSpacing[\s\S]*?<\/InsetSpacing>/) || [''])[0]
        .match(/>([-\d.\s]+)</g)?.map((s) => Number(s.replace(/[><]/g, '').trim())) || [0, 0, 0, 0];
      aus.set(sid, {
        breite: Math.max(...xs) - Math.min(...xs),
        hoehe: Math.max(...ys) - Math.min(...ys),
        spalten: zahl(pref, 'TextColumnCount') || 1,
        steg: zahl(pref, 'TextColumnGutter') || 0,
        // InsetSpacing: oben, links, unten, rechts
        innen: { oben: inset[0] || 0, links: inset[1] || 0, unten: inset[2] || 0, rechts: inset[3] || 0 },
        skalierung: Math.abs(it[0]) || 1,
      });
    }
  }
  return aus;
}

/* Absatzformate: Schriftgrad und Zeilenabstand, die ein Absatz erbt. */
function formateLesen(xml) {
  const aus = new Map();
  for (const roh of (xml || '').split('<ParagraphStyle ').slice(1)) {
    const kopf = roh.slice(0, roh.indexOf('>'));
    const name = (attr(kopf, 'Self') || '').replace('ParagraphStyle/', '');
    const block = roh.split('</ParagraphStyle>')[0];
    aus.set(name, {
      grad: zahl(kopf, 'PointSize') ?? zahl(block, 'PointSize'),
      zeilen: Number((block.match(/<Leading type="unit">([\d.]+)<\/Leading>/) || [])[1]) || undefined,
      danach: zahl(kopf, 'SpaceAfter') ?? 0,
      davor: zahl(kopf, 'SpaceBefore') ?? 0,
      schnitt: attr(kopf, 'FontStyle'),
    });
  }
  return aus;
}

/* Eine Story in Absätze zerlegen – mit Grad, Zeilenabstand, Schnitt, Abständen,
   Spaltenlauf und Spaltenumbruch. Getrennt wird am Absatzende (<Br/>). */
function absaetzeLesen(xml, formate) {
  const aus = [];
  for (const block of xml.split('<ParagraphStyleRange').slice(1)) {
    const kopf = block.slice(0, block.indexOf('>'));
    const stil = (attr(kopf, 'AppliedParagraphStyle') || '').replace('ParagraphStyle/', '');
    const f = formate.get(stil) || {};
    const psr = block.split('</ParagraphStyleRange>')[0];
    const spanne = attr(kopf, 'SpanColumnType') === 'SpanColumns';
    const danach = zahl(kopf, 'SpaceAfter') ?? f.danach ?? 0;
    const davor = zahl(kopf, 'SpaceBefore') ?? f.davor ?? 0;
    let laufend = { stuecke: [], grad: f.grad || 10, zeilen: f.zeilen, spanne, danach, davor, umbruch: false };
    const ablegen = (umbruch) => {
      laufend.umbruch = umbruch;
      aus.push(laufend);
      laufend = { stuecke: [], grad: laufend.grad, zeilen: laufend.zeilen, spanne, danach, davor: 0, umbruch: false };
    };
    for (const csrRoh of psr.split('<CharacterStyleRange').slice(1)) {
      const ckopf = csrRoh.slice(0, csrRoh.indexOf('>'));
      const grad = zahl(ckopf, 'PointSize') ?? f.grad ?? 10;
      const zeilen = Number((csrRoh.match(/<Leading type="unit">([\d.]+)<\/Leading>/) || [])[1]) || f.zeilen;
      const schnitt = attr(ckopf, 'FontStyle') || f.schnitt || 'Klar';
      const spalte = attr(ckopf, 'ParagraphBreakType') === 'NextColumn';
      laufend.grad = grad; if (zeilen) laufend.zeilen = zeilen;
      for (const m of csrRoh.matchAll(/<Content>([\s\S]*?)<\/Content>|<Br \/>/g)) {
        if (m[1] === undefined) ablegen(spalte);
        else {
          const text = m[1].replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');
          laufend.stuecke.push({ text, grad, schnitt });
        }
      }
    }
    if (laufend.stuecke.length) ablegen(false);
  }
  return aus.filter((a) => a.stuecke.length || a.umbruch);
}

// ------------------------------------------------------------------- Messen
const SCHNITT_DATEI = {
  Leise: 'Goetheanum-Schrift-v2.7-Leise.otf', Ruhig: 'Goetheanum-Schrift-v2.7-Ruhig.otf',
  Klar: 'Goetheanum-Schrift-v2.7-Klar.otf', Deutlich: 'Goetheanum-Schrift-v2.7-Deutlich.otf',
  Laut: 'Goetheanum-Schrift-v2.7-Laut.otf',
};
function schriftDatei(schnitt) {
  if (SCHNITT_DATEI[schnitt]) return SCHNITT_DATEI[schnitt];
  if (/Semibold|Bold/i.test(schnitt)) return SCHNITT_DATEI.Deutlich;
  return SCHNITT_DATEI.Klar;
}

async function messen(auftraege) {
  const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs')
    .catch(() => import('playwright'));
  const browser = await chromium.launch();
  const seite = await browser.newPage();
  const faces = Object.entries(SCHNITT_DATEI).map(([name, f]) => {
    const b64 = fs.readFileSync(path.join(SCHRIFTEN, f)).toString('base64');
    return `@font-face{font-family:"G-${name}";src:url(data:font/otf;base64,${b64}) format("opentype")}`;
  }).join('\n');
  await seite.setContent(`<!doctype html><meta charset="utf-8"><style>
    ${faces}
    body{margin:0}
    .spalte{position:absolute;left:-9999px;top:0;white-space:pre-wrap;word-wrap:break-word;hyphens:none}
    .spalte p{margin:0}
  </style><body></body>`);
  await seite.evaluate(() => document.fonts.ready);
  const ergebnis = await seite.evaluate((auftraege2) => {
    const aus = [];
    for (const a of auftraege2) {
      const box = document.createElement('div');
      box.className = 'spalte';
      box.style.width = `${a.breite}px`;
      for (const abs of a.absaetze) {
        const p = document.createElement('p');
        p.style.lineHeight = `${abs.zeilen || abs.grad * 1.2}px`;
        p.style.marginTop = `${abs.davor}px`;
        p.style.marginBottom = `${abs.danach}px`;
        if (!abs.stuecke.length) p.append(document.createTextNode(' '));
        for (const st of abs.stuecke) {
          const s = document.createElement('span');
          s.style.fontFamily = `"G-${st.schnitt}"`;
          s.style.fontSize = `${st.grad}px`;
          s.textContent = st.text;
          p.append(s);
        }
        box.append(p);
      }
      document.body.append(box);
      aus.push(box.getBoundingClientRect().height);
      box.remove();
    }
    return aus;
  }, auftraege);
  await browser.close();
  return ergebnis;
}

// ------------------------------------------------------------------- Ablauf
const slots = JSON.parse(fs.readFileSync(SLOTS, 'utf8'));

/* Eine Datei in Messaufträge zerlegen: je Rahmen und Spalte ein Auftrag. */
function auftraegeFuer(pfad) {
  const dateien = zipLesen(new Uint8Array(fs.readFileSync(pfad)));
  const rahmen = rahmenLesen(dateien);
  const formate = formateLesen(dateien.get('Resources/Styles.xml'));
  const auftraege = [];
  const zuordnung = [];
  for (const [name, slot] of Object.entries(slots.slots)) {
    const r = rahmen.get(slot.story);
    const xml = dateien.get(`Stories/Story_${slot.story}.xml`);
    if (!r || !xml) continue;
    const spalten = [[]];
    for (const a of absaetzeLesen(xml, formate)) {
      spalten[spalten.length - 1].push(a);
      if (a.umbruch) spalten.push([]);
    }
    const nutzBreite = r.breite - r.innen.links - r.innen.rechts;
    const spaltenBreite = (nutzBreite - r.steg * (r.spalten - 1)) / r.spalten;
    spalten.forEach((abs, i) => {
      if (!abs.length) return;
      const spannend = abs.filter((a) => a.spanne);
      const normale = abs.filter((a) => !a.spanne);
      if (spannend.length) {
        auftraege.push({ breite: nutzBreite, absaetze: spannend });
        zuordnung.push({ name, art: 'spannend' });
      }
      if (normale.length) {
        auftraege.push({ breite: spaltenBreite, absaetze: normale });
        zuordnung.push({ name, art: 'spalte' });
      }
    });
  }
  return { auftraege, zuordnung, rahmen };
}

/* Gemessene Höhen je Rahmen zusammenfassen: gespannte Absätze kosten alle
   Spalten Höhe, die Spalten selbst zählen mit der höchsten. */
function proSlot(zuordnung, hoehen) {
  const aus = new Map();
  zuordnung.forEach((z, i) => {
    const e = aus.get(z.name) || { spannend: 0, spalten: [] };
    if (z.art === 'spannend') e.spannend += hoehen[i];
    else e.spalten.push(hoehen[i]);
    aus.set(z.name, e);
  });
  return new Map([...aus].map(([n, e]) => [n, e.spannend + Math.max(0, ...e.spalten)]));
}

const neu = auftraegeFuer(datei);
const ref = referenz && fs.existsSync(referenz) ? auftraegeFuer(referenz) : null;
const alleAuftraege = [...neu.auftraege, ...(ref ? ref.auftraege : [])];
const alleHoehen = await messen(alleAuftraege);
const hoehenNeu = proSlot(neu.zuordnung, alleHoehen.slice(0, neu.auftraege.length));
const hoehenRef = ref ? proSlot(ref.zuordnung, alleHoehen.slice(neu.auftraege.length)) : null;

const zeilen = [...hoehenNeu].map(([name, hoehe]) => {
  const vorher = hoehenRef ? hoehenRef.get(name) : undefined;
  const r = neu.rahmen.get(slots.slots[name].story);
  return { name, hoehe, vorher, wachstum: vorher === undefined ? null : hoehe - vorher, rahmen: r ? r.hoehe : 0 };
}).sort((a, b) => (b.wachstum ?? -Infinity) - (a.wachstum ?? -Infinity));

const waechst = zeilen.filter((z) => z.wachstum !== null && z.wachstum > 0.5);
const neuDazu = zeilen.filter((z) => z.wachstum === null);

console.log(`${path.basename(datei)}${ref ? ` gegen ${path.basename(referenz)}` : ''} · ${zeilen.length} Rahmen mit der Hausschrift gemessen\n`);
if (ref) {
  console.log('  Rahmen             gesetzt   jetzt   Veränderung');
  for (const z of (alle ? zeilen : waechst)) {
    const v = z.wachstum === null ? 'neu' : `${z.wachstum > 0 ? '+' : ''}${z.wachstum.toFixed(1)}`;
    const marke = z.wachstum > 0.5 ? '  ← braucht mehr Platz' : '';
    console.log(`  ${z.name.padEnd(18)} ${(z.vorher ?? 0).toFixed(1).padStart(7)} ${z.hoehe.toFixed(1).padStart(7)}   ${v.padStart(7)}${marke}`);
  }
  if (!waechst.length && !alle) console.log('  (kein Rahmen braucht mehr Platz als in der gesetzten Fassung)');
  for (const z of neuDazu) console.log(`  ${z.name.padEnd(18)} – in der Vergleichsfassung nicht vorhanden`);
  console.log(`\n${waechst.length} Rahmen brauchen mehr Platz als vorher.`);
} else {
  console.log('  Rahmen             Texthöhe   Rahmenhöhe');
  for (const z of zeilen.sort((a, b) => b.hoehe - a.hoehe)) {
    console.log(`  ${z.name.padEnd(18)} ${z.hoehe.toFixed(1).padStart(8)} ${z.rahmen.toFixed(1).padStart(12)}`);
  }
}
process.exit(waechst.length ? 1 : 0);
