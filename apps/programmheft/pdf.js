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

function marke(doc, x, y, r, n, farbe) {
  doc.setFillColor(farbe); doc.setDrawColor(WEISS); doc.setLineWidth(0.4);
  doc.circle(x, y, r, 'FD');
  doc.setTextColor(WEISS); doc.setFont('SourceFett', 'normal'); doc.setFontSize(r * 1.1 * PT);
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
export async function bauePdf(S, f, bilder, orte, lage, grad, logoSvg, druck = false) {
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

  const lw1 = svgLogo(logoSvg, WEISS), lh = 11, lw = lh * lw1.verh;
  await doc.svg(lw1.el, { x: (SB - lw) / 2, y: 20, width: lw, height: lh });

  doc.setTextColor(WEISS); doc.setFont('GDeutlich', 'normal'); doc.setFontSize(34);
  // Ausgeglichen umbrechen wie text-wrap: balance
  let titel = doc.splitTextToSize(text(S.titel), SB - 24);
  for (let b = SB - 24; b > 40; b -= 2) { const t = doc.splitTextToSize(text(S.titel), b); if (t.length > titel.length) break; titel = t; }
  const wann = String(S.wann).split('\n');
  const tz = 34 * 1.05 / PT, wz = 15 * 1.3 / PT;
  const blockH = titel.length * tz + 7 + wann.length * wz;
  let y = 40 + (fh - k - 40 - blockH) / 2 + tz * 0.8;
  doc.text(titel, SB / 2, y, { align: 'center', lineHeightFactor: 1.05 });
  y += (titel.length - 1) * tz + 7 + wz;
  doc.setFontSize(15);
  doc.text(wann, SB / 2, y, { align: 'center', lineHeightFactor: 1.3 });
  if (S.credit) { doc.setFont('Source', 'normal'); doc.setFontSize(6.5); doc.text(text(S.credit), SB - 4, SH - 3, { align: 'right' }); }

  /* ---------- Seiten 2–3: Programm ---------- */
  const zab = grad * 1.4 / PT, zeitB = 31, tx = 9 + 3 + zeitB + 3, tb = SB - 9 - 3 - tx;
  const nr = (o) => orte.indexOf((o || '').trim()) + 1;
  S.seiten.forEach((L, s) => {
    neueSeite();
    let y0 = 13;
    if (s === 0) { doc.setFont('GDeutlich', 'normal'); doc.setFontSize(22); doc.setTextColor(f.kopf); doc.text('Programm', 11, y0 + 7); y0 += 14; }
    const laeufeVon = (z) => {
      const l = [];
      String(z.text).split(/(<b>.*?<\/b>)/g).filter(Boolean).forEach((t) =>
        l.push({ t: text(t.replace(/<\/?b>/g, '')), font: /^<b>/.test(t) ? 'SourceFett' : 'Source', farbe: f.tinte }));
      if (z.ort) l.push({ t: ' ', font: 'Source', farbe: f.tinte }, { t: nr(z.ort) ? nr(z.ort) + ' ' : '', font: 'SourceFett', farbe: f.ort }, { t: z.ort.replace(/ /g, ' '), font: 'Source', farbe: f.ort });
      return l;
    };
    // Zeilenabstand wie im Heft: Rest der Seite gleichmässig verteilen, 3–7 mm.
    const hoehen = L.map((z) => laeufeSetzen(doc, laeufeVon(z), 0, 0, tb, grad, zab) * zab);
    const frei = SH - 10 - y0 - hoehen.reduce((a, b) => a + b, 0);
    const pad = Math.max(3, Math.min(7, frei / (L.length * 2)));
    let yy = y0;
    L.forEach((z, i) => {
      const h = hoehen[i] + 2 * pad;
      if (z.pause) { doc.setFillColor(f.pause); doc.rect(9, yy, SB - 18, h, 'F'); }
      const base = yy + pad + grad / PT * 0.8;
      doc.setFont('SourceFett', 'normal'); doc.setFontSize(grad); doc.setTextColor(f.tinte);
      doc.text(z.zeit, 12, base);
      laeufeSetzen(doc, laeufeVon(z), tx, base, tb, grad, zab);
      yy += h;
      doc.setDrawColor(f.linie); doc.setLineWidth(0.3); doc.line(9, yy, SB - 9, yy);
    });
  });

  /* ---------- Seite 4: Campus ---------- */
  neueSeite();
  doc.setFont('GDeutlich', 'normal'); doc.setFontSize(22); doc.setTextColor(f.kopf);
  doc.text(text(S.info), 11, 13 + 7);
  const spalten = Math.ceil(orte.length / 2), legZ = 6.5;
  const legY = SH - 10 - 14 - spalten * legZ;
  const kastenY = 27, kastenH = legY - 5 - kastenY;
  const kb = Math.min(SB - 22, kastenH * 192 / 210), kh = kb * 210 / 192, kx = (SB - kb) / 2;
  doc.addImage(bilder.plan.url, bilder.plan.url.startsWith('data:image/png') ? 'PNG' : 'JPEG', kx, kastenY, kb, kh, 'plan', 'SLOW');
  orte.forEach((o, i) => { const p = lage(o); if (p) marke(doc, kx + p[0] / 100 * kb, kastenY + p[1] / 100 * kh, 3.25, i + 1, f.gold); });
  orte.forEach((o, i) => {
    const sp = i < spalten ? 0 : 1, zy = legY + (i % spalten) * legZ;
    const x = 11 + sp * (SB - 22 + 6) / 2;
    marke(doc, x + 3, zy + 3, 3, i + 1, f.gold);
    doc.setFont('Source', 'normal'); doc.setFontSize(11); doc.setTextColor(f.tinte);
    doc.text(o, x + 8, zy + 3, { baseline: 'middle' });
  });
  doc.setFont('Source', 'normal'); doc.setFontSize(9); doc.setTextColor(f.tinte);
  doc.text(String(S.kontakt).split('\n'), 11, SH - 10 - 5, { lineHeightFactor: 1.45 });
  const lw2 = svgLogo(logoSvg), bl = 5, bw = bl * lw2.verh;
  await doc.svg(lw2.el, { x: SB - 11 - bw, y: SH - 10 - bl, width: bw, height: bl });

  return doc;
}
