/* Programmheft · PDF-Export
   ---------------------------------------------------------------------------
   Wie im Campusplan (apps/campusplan/pdf.js): jsPDF zeichnet das Heft selbst,
   die Schriften sind als TTF eingebettet, Text bleibt Text. Kein Druckdialog.
   Vier A5-Seiten. Titelbild und Campusplan kommen als Bild (300 ppi und mehr),
   Farbflächen, Logo (svg2pdf), Nummern und Linien sind Vektor.
   jsPDF und svg2pdf liegen im Kartenwerkzeug (apps/karten-generator/vendor).
   ------------------------------------------------------------------------- */

const PT = 72 / 25.4;
const SB = 148, SH = 210;
const SCHRIFTEN = [
  ['GDeutlich', '../../assets/fonts/goetheanum/Office/GoetheanumSchriftDeutlich.ttf'],
  ['GKlar', '../../assets/fonts/goetheanum/Office/GoetheanumSchriftKlar.ttf'],
  ['GRuhig', '../../assets/fonts/goetheanum/Office/GoetheanumSchriftRuhig.ttf'],
  ['GLaut', '../../assets/fonts/goetheanum/Office/GoetheanumSchriftLaut.ttf'],
  ['Source', '../../assets/fonts/goetheanum/Fallback/SourceSans3-Regular.ttf'],
  ['SourceFett', '../karten-generator/assets/fonts/SourceSans3-SemiBold.ttf'],
];
const WEISS = '#ffffff'; // # ds-ok Druck

let schriftenV = null;
async function base64(pfad) {
  const a = await fetch(pfad);
  if (!a.ok) throw new Error(`${pfad}: ${a.status}`);
  const b = new Uint8Array(await a.arrayBuffer());
  let s = '';
  for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000));
  return btoa(s);
}
const schriften = () => (schriftenV ||= Promise.all(SCHRIFTEN.map(async ([n, p]) => [n, await base64(p)]))
  .catch((e) => { schriftenV = null; throw e; }));

const text = (html) => String(html).replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');

/* Zeile aus Läufen setzen, mit Umbruch: läufe = [{t, font, farbe}] */
function laeufeSetzen(doc, laeufe, x, y, breite, grad, zab) {
  const woerter = [];
  laeufe.forEach((l) => String(l.t).split(/([ \t\n]+)/).filter((w) => w !== '').forEach((w) => woerter.push({ ...l, t: w })));
  const zeilen = [[]];
  let b = 0;
  doc.setFontSize(grad);
  woerter.forEach((w) => {
    doc.setFont(w.font, 'normal');
    const wb = doc.getTextWidth(w.t);
    if (/^[ \t\n]+$/.test(w.t)) { if (b) { zeilen.at(-1).push({ ...w, wb }); b += wb; } return; }
    if (b + wb > breite && b > 0) {
      const z = zeilen.at(-1); while (z.length && /^\s+$/.test(z.at(-1).t)) z.pop();
      // Was mit geschütztem Leerzeichen endet (Ortsnummer), wandert mit in die neue Zeile.
      const mit = [];
      while (z.length && /\u00a0$/.test(z.at(-1).t)) mit.unshift(z.pop());
      zeilen.push(mit); b = mit.reduce((a, m) => a + m.wb, 0);
    }
    zeilen.at(-1).push({ ...w, wb }); b += wb;
  });
  if (!y) return zeilen.length;
  zeilen.forEach((z, i) => {
    let xx = x;
    z.forEach((w) => { doc.setFont(w.font, 'normal'); doc.setTextColor(w.farbe); doc.text(w.t, xx, y + i * zab); xx += w.wb; });
  });
  return zeilen.length;
}

const binden = (t) => String(t || '').replace(/(^|\s)(am|im|an|in|zu|zum|zur|und|für|von|vom|mit|bei|auf|aus|um|der|die|das|des|dem|den|ein|eine) /gi, '$1$2\u00a0');
let FS = 'Source', FF = 'SourceFett'; // Daten-Schrift, je nach Wahl
function marke(doc, x, y, r, n, farbe) {
  doc.setFillColor(farbe); doc.setDrawColor(WEISS); doc.setLineWidth(0.4);
  doc.setFont(FF, 'normal'); doc.setFontSize(r * 1.1 * PT);
  const w = Math.max(0, doc.getTextWidth(String(n)) + r * 0.5 - 2 * r); // «1–3»: Pille statt Kreis
  if (w > 0) doc.roundedRect(x - w / 2 - r, y - r, w + 2 * r, 2 * r, r, r, 'FD'); else doc.circle(x, y, r, 'FD');
  doc.setTextColor(WEISS);
  doc.text(String(n), x, y + r * 0.04, { align: 'center', baseline: 'middle' });
}

function svgLogo(svgText, farbe) {
  const t = farbe ? svgText.replace(/fill="#[0-9a-fA-F]{3,6}"/g, `fill="${farbe}"`) : svgText;
  const el = new DOMParser().parseFromString(t, 'image/svg+xml').documentElement;
  const vb = (el.getAttribute('viewBox') || '0 0 5 1').split(/[\s,]+/).map(Number);
  return { el, verh: vb[2] / vb[3] };
}

/* S: Zustand · f: Farben (#rrggbb) · bilder: {titel:{url,b,h}, plan:{url,b,h}}
   orte: Legende · lage(o): [x%, y%] oder null · grad: Programmgrad in pt */
/* Schnittmarken wie im Kartenwerkzeug: 3 mm Beschnitt, 5 mm Markenlänge. */
function schnittmarken(doc, b, l) {
  const e = b + l;
  doc.setDrawColor('#000000'); doc.setLineWidth(0.088); // # ds-ok Registerschwarz
  [[-e, 0, -b, 0], [0, -e, 0, -b], [SB + b, 0, SB + e, 0], [SB, -e, SB, -b],
    [-e, SH, -b, SH], [0, SH + b, 0, SH + e], [SB + b, SH, SB + e, SH], [SB, SH + b, SB, SH + e]]
    .forEach(([a, c, d, g]) => doc.line(a, c, d, g));
}

/* druck: true → 3 mm Beschnitt, Schnittmarken, TrimBox/BleedBox (wie das Kartenwerkzeug).
   Die Seite wird um den Rand grösser; ein Versatz am Seitenanfang hält alle
   Koordinaten im Endformat, Flächen am Rand laufen bis in den Beschnitt. */
export async function bauePdf(S, f, bilder, orte, lage, grad, logoSvg, druck = false, sektLogoSvg = '') {
  if (S.stimme === 'alles') { FS = 'GKlar'; FF = 'GLaut'; } else { FS = 'Source'; FF = 'SourceFett'; }
  const B3 = druck ? 3 : 0, R = druck ? 8 : 0;
  const doc = new jspdf.jsPDF({ unit: 'mm', format: [SB + 2 * R, SH + 2 * R], orientation: 'portrait', compress: true });
  const seiteAnfangen = () => {
    if (!R) return;
    doc.internal.write(`1 0 0 1 ${(R * PT).toFixed(3)} ${(-R * PT).toFixed(3)} cm`);
    const ctx = doc.internal.getCurrentPageInfo().pageContext, z = (v) => v * PT;
    ctx.trimBox = { bottomLeftX: z(R), bottomLeftY: z(R), topRightX: z(R + SB), topRightY: z(R + SH) };
    ctx.bleedBox = { bottomLeftX: z(R - B3), bottomLeftY: z(R - B3), topRightX: z(R + SB + B3), topRightY: z(R + SH + B3) };
    schnittmarken(doc, B3, R - B3);
  };
  const neueSeite = () => { doc.addPage([SB + 2 * R, SH + 2 * R], 'portrait'); seiteAnfangen(); };
  seiteAnfangen();
  (await schriften()).forEach(([n, b]) => { doc.addFileToVFS(`${n}.ttf`, b); doc.addFont(`${n}.ttf`, n, 'normal'); });
  doc.setProperties({ title: S.titel, creator: 'Goetheanum Werkzeuge · Programmheft' });

  /* ---------- Seite 1: Titel ---------- */
  const bildY = 110, bildH = SH - bildY;
  doc.addImage(bilder.titel.url, 'JPEG', -B3, bildY, SB + 2 * B3, bildH + B3, 'titel', 'SLOW');
  const k = 14, fh = 126;
  // Die Kante läuft über den Rand hinaus in den Beschnitt (Steigung fortgesetzt).
  const L = -B3, Rr = SB + B3, T = -B3, st = k / SB * B3;
  const kante = { schraege: [[L, T], [Rr, T], [Rr, fh - k - st], [L, fh + st]],
    trapez: [[L, T], [Rr, T], [Rr, fh - k - B3 * k / (SB * 0.22)], [SB * 0.78, fh], [SB * 0.22, fh], [L, fh - k - B3 * k / (SB * 0.22)]],
    gerade: [[L, T], [Rr, T], [Rr, fh - k], [L, fh - k]] }[S.kante] || [[L, T], [Rr, T], [Rr, fh], [L, fh]];
  if (S.kante === 'gerade') { doc.setFillColor(WEISS); doc.rect(L, bildY, SB + 2 * B3, fh - k - bildY, 'F'); }
  doc.setFillColor(f.akzent);
  const [p0, ...rest] = kante;
  doc.lines(rest.map((p, i) => [p[0] - (i ? rest[i - 1][0] : p0[0]), p[1] - (i ? rest[i - 1][1] : p0[1])]), p0[0], p0[1], [1, 1], 'F', true);

  // Titel-Logo: Sektionslogo (weiss, zweizeilig) oder die Goetheanum-Marke
  const lw1 = svgLogo(bilder.titelLogo || logoSvg, WEISS);
  let lh = bilder.titelLogo ? 11 : 6.5, lw = lh * lw1.verh;
  if (lw > 118) { lw = 118; lh = lw / lw1.verh; }
  await doc.svg(lw1.el, { x: (SB - lw) / 2, y: 20, width: lw, height: lh });
  const logoUnten = 20 + lh;

  doc.setTextColor(WEISS);
  const wann = String(S.wann).split('\n');
  const Z = bilder.zweit || null; // zweite Sprache: {programm, legende[]} – Hauptsprache Deutlich, zweite Ruhig
  const wann2 = Z && S.wann2 ? String(S.wann2).split('\n') : [];
  const unten = 126 - (S.kante === 'gerade' ? 10 : 16), wz = 15 * 1.3 / PT;
  // Ausgeglichen umbrechen wie text-wrap: balance
  const umbrechen = (t, schnitt, g) => { doc.setFont(schnitt, 'normal'); doc.setFontSize(g); if (!t) return [];
    // eigener Umbruch nur an normalen Leerzeichen: «am\u00a0Goetheanum» bleibt zusammen (splitTextToSize trennt auch dort)
    const woerter = text(binden(t)).split(' '), breit = (w) => doc.getTextWidth(w.replace(/\u00a0/g, ' '));
    const brechen = (b) => woerter.reduce((z, w) => { const k = z.length ? z.at(-1) + ' ' + w : w; if (z.length && breit(k) <= b) z[z.length - 1] = k; else z.push(w); return z; }, []);
    let z = brechen(SB - 24);
    for (let b = SB - 24; b > 40; b -= 2) { const u = brechen(b); if (u.length > z.length) break; z = u; }
    return z.map((l) => l.replace(/\u00a0/g, ' ')); };
  const mitte = { schraege: 119, trapez: 126, gerade: 112 }[S.kante] || 126; // Farbkante in der Seitenmitte
  // Titelgrad: 34 pt; reicht das Farbfeld nicht (zweisprachig, Sektionslogo), wird der Titel kleiner, nie unter 22 pt.
  let g = 34, titel, titel2, tz, blockH;
  for (; g >= 22; g -= 1) {
    titel = umbrechen(S.titel, 'GDeutlich', g); titel2 = Z ? umbrechen(S.titel2, 'GRuhig', g) : []; tz = g * 1.05 / PT;
    blockH = titel.length * tz + 7 + wann.length * wz + (titel2.length ? 7 + titel2.length * tz : 0) + (wann2.length ? (titel2.length ? 5 : 2) + wann2.length * wz : 0);
    if (blockH <= mitte - 4 - logoUnten - 5) break;
  }
  g = Math.max(g, 22);
  // Mittig zwischen Logo und dem Innenrand über der Kante – wie im Editor.
  let y = logoUnten + Math.max(5, Math.min((unten - logoUnten - blockH) / 2, mitte - 4 - logoUnten - blockH)) + tz * 0.8;
  doc.setFont('GDeutlich', 'normal'); doc.setFontSize(g);
  doc.text(titel, SB / 2, y, { align: 'center', lineHeightFactor: 1.05 });
  y += (titel.length - 1) * tz + 7 + wz;
  doc.setFontSize(15);
  doc.text(wann, SB / 2, y, { align: 'center', lineHeightFactor: 1.3 });
  y += (wann.length - 1) * wz;
  if (titel2.length) { y += 7 + tz; doc.setFont('GRuhig', 'normal'); doc.setFontSize(g); doc.text(titel2, SB / 2, y, { align: 'center', lineHeightFactor: 1.05 }); y += (titel2.length - 1) * tz; }
  if (wann2.length) { y += (titel2.length ? 5 : 2) + wz; doc.setFont('GRuhig', 'normal'); doc.setFontSize(15); doc.text(wann2, SB / 2, y, { align: 'center', lineHeightFactor: 1.3 }); }
  if (S.credit) { doc.setFont(FS, 'normal'); doc.setFontSize(6.5); doc.text(text(S.credit), SB - 4, SH - 3, { align: 'right' }); }

  /* ---------- Seiten 2–3: Programm ---------- */
  const zab = grad * 1.4 / PT, zeitB = 40, tx = 9 + 3 + zeitB + 3, tb = SB - 9 - 3 - tx;
  const nr = (o) => orte.indexOf((o || '').trim()) + 1;
  S.seiten.forEach((L, s) => {
    neueSeite();
    let y0 = 13;
    const art = (S.art || [])[s] || 'zeiten';
    if (art === 'text') { // Freie Textseite: Überschrift (optional), Absätze in Klar, fett = Laut
      if (String((S.kopf || [])[s] || '').trim()) { doc.setFont('GDeutlich', 'normal'); doc.setFontSize(22); doc.setTextColor(f.kopf); doc.text(text(S.kopf[s]), 11, y0 + 7); y0 += 14; }
      const fz = 13 * 1.5 / PT, breite = SB - 22;
      const absatz = (html, schnitt, fett) => String(html || '').split('\n').forEach((abs) => {
        if (!abs.trim()) { y0 += fz; return; }
        const l = abs.split(/(<b>.*?<\/b>)/g).filter(Boolean).map((t) => ({ t: text(t.replace(/<\/?b>/g, '')), font: /^<b>/.test(t) ? fett : schnitt, farbe: f.tinte }));
        y0 += laeufeSetzen(doc, l, 11, y0 + 13 / PT * 0.8, breite, 13, fz) * fz;
      });
      absatz((S.frei || [])[s], 'GKlar', 'GLaut');
      if (Z && (S.frei2 || [])[s]) { y0 += fz * 0.5; absatz(S.frei2[s], 'GRuhig', 'GLaut'); }
      return;
    }
    if (false) { /* Kopf «Programm» entfällt: die Zeittafel erklärt sich selbst */ doc.setFont('GDeutlich', 'normal'); doc.setFontSize(22); doc.setTextColor(f.kopf); doc.text('Programm', 11, y0 + 7); if (Z) { const w = doc.getTextWidth('Programm '); doc.setFont('GRuhig', 'normal'); doc.text(Z.programm, 11 + w, y0 + 7); } y0 += 14; }
    const laeufeVon = (z) => {
      const l = [];
      String(z.text).split(/(<b>.*?<\/b>)/g).filter(Boolean).forEach((t) =>
        l.push({ t: text(t.replace(/<\/?b>/g, '')), font: /^<b>/.test(t) ? (Z || S.stimme ? 'GLaut' : FF) : (Z ? 'GDeutlich' : S.stimme ? 'GKlar' : FS), farbe: f.tinte }));
      return l;
    };
    // Zeilenabstand wie im Heft: Rest der Seite gleichmässig verteilen, 3–7 mm.
    // Ort rechtsbündig in eigener Spalte: Nummer fett, Name normal; der Programmtext weicht ihm aus.
    const ortB = (z) => { if (!z.ort) return 0; doc.setFontSize(grad); doc.setFont(FF, 'normal'); const a = nr(z.ort) ? doc.getTextWidth(nr(z.ort) + ' ') : 0; doc.setFont(FS, 'normal'); return a + doc.getTextWidth(z.ort) + 3; };
    const zweitVon = (z) => (Z && z.text2 ? String(z.text2).split(/(<b>.*?<\/b>)/g).filter(Boolean).map((t) => ({ t: text(t.replace(/<\/?b>/g, '')), font: 'GRuhig', farbe: f.tinte })) : []);
    const n1 = L.map((z) => laeufeSetzen(doc, laeufeVon(z), 0, 0, tb - ortB(z), grad, zab));
    const hoehen = L.map((z, i) => (n1[i] + (zweitVon(z).length ? laeufeSetzen(doc, zweitVon(z), 0, 0, tb - ortB(z), grad, zab) : 0)) * zab);
    const frei = SH - 10 - y0 - hoehen.reduce((a, b) => a + b, 0);
    const pad = Math.max(3, Math.min(4.5, frei / (L.length * 2)));
    let yy = y0;
    L.forEach((z, i) => {
      const h = hoehen[i] + 2 * pad;
      if (z.pause) { doc.setFillColor(f.pause); doc.rect(9, yy, SB - 18, h, 'F'); }
      const base = yy + pad + grad / PT * 0.8;
      doc.setFont(FF, 'normal'); doc.setFontSize(grad); doc.setTextColor(f.tinte);
      doc.text(z.zeit, 12, base);
      laeufeSetzen(doc, laeufeVon(z), tx, base, tb - ortB(z), grad, zab);
      if (zweitVon(z).length) laeufeSetzen(doc, zweitVon(z), tx, base + n1[i] * zab, tb - ortB(z), grad, zab);
      if (z.ort) {
        const rechts = tx + tb; doc.setFontSize(grad); doc.setTextColor(f.ort);
        doc.setFont(FS, 'normal'); doc.text(z.ort, rechts, base, { align: 'right' });
        if (nr(z.ort)) { const w = doc.getTextWidth(z.ort); doc.setFont(FF, 'normal'); doc.text(nr(z.ort) + ' ', rechts - w, base, { align: 'right' }); }
      }
      yy += h;
      doc.setDrawColor(f.linie); doc.setLineWidth(0.3); doc.line(9, yy, SB - 9, yy);
    });
  });

  /* ---------- Seite 4: Campus ---------- */
  neueSeite();
  const spalten = Math.ceil(orte.length / 3), legZ = 6;
  const legY = SH - 10 - 14 - spalten * legZ;
  // Karte randabfallend (oben und seitlich bis in den Beschnitt), harte Kante unten über der Legende.
  const kx = -B3, kb = SB + 2 * B3, kh = kb * 210 / 192, kastenY = -B3 - (bilder.versatz || 0) * kh, unterkante = legY - 5;
  doc.saveGraphicsState(); doc.rect(kx, -B3, kb, unterkante + B3, null); doc.clip(); doc.discardPath();
  doc.addImage(bilder.plan.url, bilder.plan.url.startsWith('data:image/png') ? 'PNG' : 'JPEG', kx, kastenY, kb, kh, 'plan', 'SLOW');
  doc.restoreGraphicsState();
  (bilder.marker || []).filter((m) => { const y = kastenY + m.y / 100 * kh; return y < unterkante - 2.4 && y > -B3 + 2.4; }).forEach((m) => {
    const px = kx + m.x / 100 * kb, py = kastenY + m.y / 100 * kh;
    if (m.linie) { const ax = kx + m.ax / 100 * kb, ay = kastenY + m.ay / 100 * kh; doc.setDrawColor(f.gold); doc.setLineWidth(0.3); doc.line(ax, ay, px, py); doc.setFillColor(f.gold); doc.circle(ax, ay, 0.7, 'F'); }
    marke(doc, px, py, 2.4, m.t, f.gold);
  });
  orte.forEach((o, i) => {
    const sp = Math.floor(i / spalten), zy = legY + (i % spalten) * legZ;
    const x = 11 + sp * (SB - 22 + 4) / 3;
    marke(doc, x + 2.5, zy + 3, 2.5, i + 1, f.gold);
    doc.setFont(FS, 'normal'); doc.setFontSize(10); doc.setTextColor(f.tinte);
    doc.text(o, x + 7, zy + 3, { baseline: 'middle' });
    if (Z && Z.legende[i]) { const w = doc.getTextWidth(o + ' '); doc.setFont('GRuhig', 'normal'); doc.text(Z.legende[i], x + 7 + w, zy + 3, { baseline: 'middle' }); }
  });
  // Rückseite unten rechts: das Logo der gewählten Sektion (Logo-Maschine)
  const lw2 = svgLogo(sektLogoSvg || logoSvg), bw = Math.min(9 * lw2.verh, 80), bl = bw / lw2.verh;
  // Kontakt links daneben, umbrochen nur an normalen Leerzeichen: PLZ und Ort bleiben zusammen.
  const kzab = 9 * 1.45 / PT, kbr = SB - 22 - bw - 4;
  const kl = String(S.kontakt).replace(/\b(\d{4,5}) (?=\S)/g, '$1\u00a0').replace(/ · /g, '\u00a0· ').split('\n').map((z) => [{ t: text(z), font: FS, farbe: f.tinte }]);
  const kn = kl.reduce((a, l) => a + laeufeSetzen(doc, l, 0, 0, kbr, 9, kzab), 0);
  let ky = SH - 10 - 1 - (kn - 1) * kzab;
  kl.forEach((l) => { ky += laeufeSetzen(doc, l, 11, ky, kbr, 9, kzab) * kzab; });
  await doc.svg(lw2.el, { x: SB - 11 - bw, y: SH - 10 - bl, width: bw, height: bl });

  return doc;
}
