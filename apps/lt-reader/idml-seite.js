/* Tagungs-Reader · IDML-Seiten zeichnen
   ---------------------------------------------------------------------------
   Zeichnet eine Seite einer InDesign-Vorlage (IDML) als SVG ins Blatt: Flächen,
   Pfade, Ovale, Linien, Bilder (mit Rahmen-Beschnitt und Spiegelung), Deckkraft,
   Mischmodus, weiche Kanten (Verlaufs-Feder, angenähert) und Textrahmen mit
   Absatz- und Zeichenformaten, Spalten, Einzügen und Zeilenabständen.
   Die Vorlage ist die Wahrheit; getauscht werden nur Texte (opts.texte) und
   Bilder (opts.bilder). Koordinaten: 1 SVG-Einheit = 1 pt, wie im IDML.
   Zip-Leser aus apps/lt-programm/idml-export.js (DecompressionStream).
   ------------------------------------------------------------------------- */
import { zipLesen } from '../lt-programm/idml-export.js';

const td = new TextDecoder('utf-8');
const PT = 72 / 25.4;
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const n3 = (v) => Math.round(v * 1000) / 1000;
let laufId = 0;

// ------------------------------------------------------------- Laden

export async function idmlLaden(url) {
  const bytes = new Uint8Array(await (await fetch(url)).arrayBuffer());
  const dateien = await zipLesen(bytes);
  const xml = (name) => new DOMParser().parseFromString(td.decode(dateien.get(name)), 'application/xml');
  const doc = { url, farben: {}, tints: {}, pstile: {}, cstile: {}, stories: {}, seiten: {}, spreads: [], bleed: 8.5 };

  const g = xml('Resources/Graphic.xml');
  for (const c of g.getElementsByTagName('Color')) doc.farben[c.getAttribute('Self')] = farbeHex(c.getAttribute('Space'), c.getAttribute('ColorValue'));
  doc.farben['Color/Paper'] = '#ffffff'; doc.farben['Color/Black'] = '#000000';
  for (const t of g.getElementsByTagName('Tint')) doc.tints[t.getAttribute('Self')] = { basis: t.getAttribute('BaseColor'), tint: +t.getAttribute('TintValue') };

  const st = xml('Resources/Styles.xml');
  for (const ps of st.getElementsByTagName('ParagraphStyle')) doc.pstile[ps.getAttribute('Self')] = stilLesen(ps);
  for (const cs of st.getElementsByTagName('CharacterStyle')) doc.cstile[cs.getAttribute('Self')] = stilLesen(cs);
  // BasedOn auflösen (flach: Kette bis zur Wurzel)
  for (const [tab, key] of [[doc.pstile, 'ParagraphStyle'], [doc.cstile, 'CharacterStyle']]) {
    for (const id of Object.keys(tab)) tab[id] = stilAufloesen(tab, id);
  }

  const pref = xml('Resources/Preferences.xml').getElementsByTagName('DocumentPreference')[0];
  if (pref) doc.bleed = +pref.getAttribute('DocumentBleedTopOffset') || 8.5;

  for (const name of dateien.keys()) {
    if (name.startsWith('Stories/')) { const s = xml(name); const story = s.getElementsByTagName('Story')[0]; if (story) doc.stories[story.getAttribute('Self')] = story; }
  }
  const map = xml('designmap.xml');
  const reihenfolge = [...map.documentElement.children].filter((e) => e.localName === 'Spread').map((e) => e.getAttribute('src'));
  for (const src of reihenfolge) {
    if (!dateien.has(src)) continue;
    const sp = xml(src).getElementsByTagName('Spread')[0];
    const eintrag = { el: sp, seiten: [] };
    for (const p of sp.getElementsByTagName('Page')) {
      const it = matrix(p.getAttribute('ItemTransform'));
      const gb = (p.getAttribute('GeometricBounds') || '0 0 595.28 419.53').split(' ').map(Number);
      const seite = { name: p.getAttribute('Name'), spread: eintrag, x: it[4] + gb[1], y: it[5] + gb[0], w: gb[3] - gb[1], h: gb[2] - gb[0] };
      doc.seiten[seite.name] = seite; eintrag.seiten.push(seite);
    }
    doc.spreads.push(eintrag);
  }
  return doc;
}

function stilLesen(el) {
  const s = { _basedOn: null };
  for (const a of el.attributes) s[a.name] = a.value;
  const props = el.getElementsByTagName('Properties')[0];
  if (props && props.parentNode === el) for (const c of props.children) {
    if (c.localName === 'BasedOn') s._basedOn = c.textContent;
    else if (c.localName === 'Leading' || c.localName === 'AppliedFont') s[c.localName] = c.textContent;
    else if (c.localName === 'TabList') s.TabList = tabsLesen(c);
  }
  return s;
}
function stilAufloesen(tab, id, tiefe = 0) {
  const s = tab[id]; if (!s || tiefe > 10) return s || {};
  const basis = s._basedOn && tab[s._basedOn] && s._basedOn !== id ? stilAufloesen(tab, s._basedOn, tiefe + 1) : {};
  const aus = { ...basis };
  for (const k of Object.keys(s)) if (!['Self', 'Name', 'NextStyle', 'KeyboardShortcut', '_basedOn'].includes(k)) aus[k] = s[k];
  aus.Name = s.Name; aus.Self = s.Self;
  return aus;
}
function tabsLesen(tl) {
  return [...tl.getElementsByTagName('ListItem')].map((li) => ({ pos: +(li.getElementsByTagName('Position')[0] || {}).textContent || 0, align: (li.getElementsByTagName('Alignment')[0] || {}).textContent || 'LeftAlign' }));
}

// CMYK/RGB/LAB → Hex (CMYK naiv, LAB grob)
function farbeHex(space, wert) {
  const v = String(wert || '').split(' ').map(Number);
  const h = (r, g, b) => '#' + [r, g, b].map((x) => Math.round(Math.max(0, Math.min(255, x))).toString(16).padStart(2, '0')).join('');
  if (space === 'RGB') return h(v[0], v[1], v[2]);
  if (space === 'CMYK') { const [c, m, y, k] = v.map((x) => x / 100); return h(255 * (1 - c) * (1 - k), 255 * (1 - m) * (1 - k), 255 * (1 - y) * (1 - k)); }
  if (space === 'LAB') { const [L, a, b] = v; const Y = (L + 16) / 116, X = a / 500 + Y, Z = Y - b / 200; const f = (t) => (t ** 3 > 0.008856 ? t ** 3 : (t - 16 / 116) / 7.787); const [xr, yr, zr] = [0.95047 * f(X), f(Y), 1.08883 * f(Z)]; const g = (c) => (c > 0.0031308 ? 1.055 * c ** (1 / 2.4) - 0.055 : 12.92 * c); return h(255 * g(3.2406 * xr - 1.5372 * yr - 0.4986 * zr), 255 * g(-0.9689 * xr + 1.8758 * yr + 0.0415 * zr), 255 * g(0.0557 * xr - 0.204 * yr + 1.057 * zr)); }
  return '#888888';
}
function mischen(hex, anteil, mit = '#ffffff') {
  const a = [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16)), b = [1, 3, 5].map((i) => parseInt(mit.substr(i, 2), 16));
  return '#' + a.map((v, i) => Math.round(v * anteil + b[i] * (1 - anteil)).toString(16).padStart(2, '0')).join('');
}
export function farbe(doc, ref, tint) {
  if (!ref || ref === 'Swatch/None' || ref === 'n') return null;
  let hex = doc.farben[ref];
  if (!hex && doc.tints[ref]) { const t = doc.tints[ref]; hex = mischen(doc.farben[t.basis] || '#000000', t.tint / 100); }
  if (!hex) return '#888888';
  const tv = tint == null || tint === '' ? 100 : +tint;
  return tv >= 0 && tv < 100 ? mischen(hex, tv / 100) : hex;
}

const matrix = (s) => (s || '1 0 0 1 0 0').split(' ').map(Number);
const mul = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
const mStr = (m) => `matrix(${m.map(n3).join(' ')})`;

function pfadD(el) {
  const geo = [...el.children].find((c) => c.localName === 'Properties');
  const pg = geo && geo.getElementsByTagName('GeometryPathType')[0];
  if (!pg) return { d: '', pts: [] };
  const pts = [...pg.getElementsByTagName('PathPointType')].map((p) => ({ a: p.getAttribute('Anchor').split(' ').map(Number), l: (p.getAttribute('LeftDirection') || p.getAttribute('Anchor')).split(' ').map(Number), r: (p.getAttribute('RightDirection') || p.getAttribute('Anchor')).split(' ').map(Number) }));
  if (!pts.length) return { d: '', pts: [] };
  const offen = pg.getAttribute('PathOpen') === 'true';
  let d = `M${n3(pts[0].a[0])} ${n3(pts[0].a[1])}`;
  const seg = (p, q) => ` C${n3(p.r[0])} ${n3(p.r[1])} ${n3(q.l[0])} ${n3(q.l[1])} ${n3(q.a[0])} ${n3(q.a[1])}`;
  for (let i = 1; i < pts.length; i++) d += seg(pts[i - 1], pts[i]);
  if (!offen) d += seg(pts[pts.length - 1], pts[0]) + ' Z';
  return { d, pts };
}
function bbox(pts) {
  const xs = pts.map((p) => p.a[0]), ys = pts.map((p) => p.a[1]);
  return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
}

// ----------------------------------------------------------- Zeichnen

/* opts: { texte: {storyId: absaetze}, bilder: {basename: url}, bearbeitbar: bool,
           stories: {storyId: true} (nur diese Stories zeigen), ausblenden: Set(Self) } */
export function seiteZeichnen(doc, name, opts = {}) {
  const seite = doc.seiten[name];
  if (!seite) throw new Error(`Seite ${name} fehlt in ${doc.url}`);
  const b = doc.bleed;
  const el = document.createElement('article');
  el.className = 'seite idml-seite'; el.dataset.seite = name;
  const defs = [];
  const ctx = { doc, opts, defs, seite };
  const inhalt = [...seite.spread.el.children].filter((c) => !['Page', 'Properties', 'FlattenerPreference'].includes(c.localName)).map((c) => itemZeichnen(ctx, c, [1, 0, 0, 1, 0, 0])).join('');
  // opts.haelfte: 'links' | 'rechts' – eine Doppelseite (z. B. Faltblatt-Rückseite) als zwei Blätter
  let x0 = seite.x, w = seite.w;
  if (opts.haelfte === 'links') w = seite.w / 2; else if (opts.haelfte === 'rechts') { x0 = seite.x + seite.w / 2; w = seite.w / 2; }
  el.innerHTML = `<svg class="blatt-svg" xmlns="http://www.w3.org/2000/svg" viewBox="${n3(x0 - b)} ${n3(seite.y - b)} ${n3(w + 2 * b)} ${n3(seite.h + 2 * b)}" width="${n3((w + 2 * b) / PT)}mm" height="${n3((seite.h + 2 * b) / PT)}mm">
    <defs>${defs.join('')}</defs><rect x="${n3(x0 - b)}" y="${n3(seite.y - b)}" width="${n3(w + 2 * b)}" height="${n3(seite.h + 2 * b)}" fill="#ffffff"/>${inhalt}</svg>`;
  return el;
}

function itemZeichnen(ctx, el, eltern) {
  const t = el.localName;
  if (['Properties', 'FlattenerPreference', 'TransparencySetting', 'TextFramePreference', 'FrameFittingOption', 'Link', 'ClippingPathSettings', 'ImageIOPreference', 'ContentTransparencySetting', 'StrokeTransparencySetting', 'FillTransparencySetting', 'TextWrapPreference', 'ObjectExportOption', 'InCopyExportOption', 'AnchoredObjectSetting', 'MetadataPacketPreference', 'Guide', 'Page', 'GraphicLayer'].includes(t)) return '';
  if (el.getAttribute('Visible') === 'false' || el.getAttribute('ItemLayer') === 'hidden') return '';
  if (ctx.opts.ausblenden && ctx.opts.ausblenden.has(el.getAttribute('Self'))) return '';
  const m = mul(eltern, matrix(el.getAttribute('ItemTransform')));
  switch (t) {
    case 'Group': return `<g>${[...el.children].map((c) => itemZeichnen(ctx, c, m)).join('')}</g>`;
    case 'Rectangle': case 'Polygon': case 'Oval': case 'GraphicLine': return formZeichnen(ctx, el, m);
    case 'TextFrame': return textRahmen(ctx, el, m);
    default: return '';
  }
}

function transparenz(ctx, el, geoPts) {
  const ts = [...el.children].find((c) => c.localName === 'TransparencySetting');
  let stil = '', maske = '';
  if (!ts) return { stil, maske };
  const bs = ts.getElementsByTagName('BlendingSetting')[0];
  if (bs) {
    const op = bs.getAttribute('Opacity'); if (op != null && op !== '' && +op < 100) stil += `opacity:${(+op / 100).toFixed(2)};`;
    const bm = bs.getAttribute('BlendMode'); if (bm && bm !== 'Normal') stil += `mix-blend-mode:${bm.toLowerCase()};`;
  }
  const gf = ts.getElementsByTagName('GradientFeatherSetting')[0];
  if (gf && gf.getAttribute('Applied') === 'true' && geoPts.length) {
    // Verlaufs-Feder: entlang Angle ab GradientStart über Length von deckend zu durchsichtig (Annäherung)
    const start = (gf.getAttribute('GradientStart') || '0 0').split(' ').map(Number);
    const len = +gf.getAttribute('Length') || 100, ang = (+gf.getAttribute('Angle') || 0) * Math.PI / 180;
    const id = `feder${++laufId}`;
    const bb = bbox(geoPts);
    ctx.defs.push(`<linearGradient id="${id}-g" gradientUnits="userSpaceOnUse" x1="${n3(start[0])}" y1="${n3(start[1])}" x2="${n3(start[0] + Math.cos(ang) * len)}" y2="${n3(start[1] + Math.sin(ang) * len)}"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
      <mask id="${id}" maskUnits="userSpaceOnUse" x="${n3(bb.x - 10)}" y="${n3(bb.y - 10)}" width="${n3(bb.w + 20)}" height="${n3(bb.h + 20)}"><rect x="${n3(bb.x - 10)}" y="${n3(bb.y - 10)}" width="${n3(bb.w + 20)}" height="${n3(bb.h + 20)}" fill="url(#${id}-g)"/></mask>`);
    maske = ` mask="url(#${id})"`;
  }
  return { stil, maske };
}

function formZeichnen(ctx, el, m) {
  const { doc, opts } = ctx;
  const { d, pts } = pfadD(el);
  if (!d) return '';
  const fill = farbe(doc, el.getAttribute('FillColor'), el.getAttribute('FillTint'));
  const stroke = farbe(doc, el.getAttribute('StrokeColor'), el.getAttribute('StrokeTint'));
  const sw = el.getAttribute('StrokeWeight');
  const strokeAttr = stroke && (sw == null || +sw > 0) ? ` stroke="${stroke}" stroke-width="${sw == null ? 1 : n3(+sw)}"` : '';
  const { stil, maske } = transparenz(ctx, el, pts);
  const bild = [...el.children].find((c) => ['Image', 'SVG', 'EPS', 'PDF', 'ImportedPage'].includes(c.localName));
  let inner = '';
  if (bild) {
    const link = bild.getElementsByTagName('Link')[0];
    const uri = link ? decodeURIComponent(link.getAttribute('LinkResourceURI') || '') : '';
    const basename = uri.split('/').pop();
    const url = (opts.bilder || {})[basename] || (opts.bilder || {})['*' + basename.split('.').pop()] || null;
    const gb = bild.getElementsByTagName('GraphicBounds')[0];
    const bm = matrix(bild.getAttribute('ItemTransform'));
    const bb = bbox(pts);
    const clipId = `clip${++laufId}`;
    ctx.defs.push(`<clipPath id="${clipId}"><path d="${d}"/></clipPath>`);
    if (url && gb) {
      const L = +gb.getAttribute('Left'), T = +gb.getAttribute('Top'), R = +gb.getAttribute('Right'), B = +gb.getAttribute('Bottom');
      inner = `<g clip-path="url(#${clipId})"><image href="${esc(url)}" x="${n3(L)}" y="${n3(T)}" width="${n3(R - L)}" height="${n3(B - T)}" preserveAspectRatio="none" transform="${mStr(bm)}"/></g>`;
    } else if (url) {
      inner = `<g clip-path="url(#${clipId})"><image href="${esc(url)}" x="${n3(bb.x)}" y="${n3(bb.y)}" width="${n3(bb.w)}" height="${n3(bb.h)}" preserveAspectRatio="xMidYMid meet"/></g>`;
    } else {
      inner = `<g clip-path="url(#${clipId})"><rect x="${n3(bb.x)}" y="${n3(bb.y)}" width="${n3(bb.w)}" height="${n3(bb.h)}" fill="#eeefee"/><text x="${n3(bb.x + bb.w / 2)}" y="${n3(bb.y + bb.h / 2)}" font-size="${n3(Math.min(9, bb.w / 12))}" text-anchor="middle" fill="#6b7177" font-family="sans-serif">${esc(basename)}</text></g>`;
    }
    return `<g transform="${mStr(m)}" style="${stil}"${maske}>${fill ? `<path d="${d}" fill="${fill}"/>` : ''}${inner}${strokeAttr ? `<path d="${d}" fill="none"${strokeAttr}/>` : ''}</g>`;
  }
  if (!fill && !strokeAttr) return '';
  return `<path d="${d}" transform="${mStr(m)}" fill="${fill || 'none'}"${strokeAttr} style="${stil}"${maske}/>`;
}

// ----------------------------------------------------------- Text

const GEWICHT = { 'Flüstern': 190, Leise: 265, Ruhig: 350, Klar: 440, Deutlich: 580, Laut: 680, Schreien: 725, Deutsch: 580, Englisch: 350,
  Thin: 200, 'Thin Upright': 200, Light: 300, 'Light Upright': 300, Regular: 400, 'Regular Upright': 400, Normal: 400, R: 400, Medium: 500, Semibold: 600, SemiBold: 600, 'Semibold Upright': 600, Bold: 700, 'Bold Upright': 700, Black: 800, B: 700, M: 500, L: 300 };
const HAUS = /^Goetheanum/;
function fontCss(familie, schnitt) {
  const fam = familie || 'Goetheanum Variabel';
  const w = GEWICHT[schnitt] ?? (/Bold|Laut|Deutsch/.test(schnitt || '') ? 680 : /Semi/.test(schnitt || '') ? 600 : /Light|Leise/.test(schnitt || '') ? 300 : 440);
  const ff = HAUS.test(fam) ? 'var(--font-display)' : /Han|PingFang|Kozuka/.test(fam) ? "'PingFang SC','Source Han Sans','Noto Sans CJK SC',var(--font-text)" : /Titillium/.test(fam) ? "'Titillium Web',var(--font-text)" : 'var(--font-text)';
  // Kalibrierung der Laufweite gegen InDesign (gemessen am Reader-PDF 2026):
  // Titillium Web (Google) läuft ~7 % weiter als das Titillium der Vorlage (9 pt),
  // die Goetheanum-Webfont ~10 % weiter als der Satz in InDesign (9,76 pt,
  // ‹of the First Class – Free rendering› 130,9 pt dort, 144,8 px hier) –
  // InDesign setzt mit optischem Kerning und 98 % Breite. Angeglichen, damit die
  // Zeilen fallen wie im Blatt; verbindlich bleibt das IDML.
  const lauf = /Titillium/.test(fam) ? 'letter-spacing:-0.03em;' : HAUS.test(fam) ? 'letter-spacing:-0.045em;' : '';
  return `font-family:${ff};font-weight:${w};${lauf}`;
}
const SPRACHE = { 'English: USA': 'en', 'English: UK': 'en-GB', 'German: Swiss': 'de-CH', 'German: Swiss 2006 Reform': 'de-CH', 'German: Traditional': 'de', 'German: Reformed': 'de', 'French': 'fr', 'Spanish': 'es', 'Spanish: Castilian': 'es', 'Italian': 'it', 'Dutch: 2005 Reform': 'nl', 'Dutch': 'nl', 'Chinese: Simplified': 'zh', 'Russian': 'ru' };
const AUSRICHTUNG = { LeftAlign: 'left', RightAlign: 'right', CenterAlign: 'center', LeftJustified: 'justify', RightJustified: 'justify', CenterJustified: 'justify', FullyJustified: 'justify' };

/* Absätze einer Story als Modell: [{stil (Self), attrs {…}, runs:[{text, attrs}]}] */
export function storyAbsaetze(doc, story) {
  const aus = [];
  let abs = null;
  for (const psr of story.getElementsByTagName('ParagraphStyleRange')) {
    const pattrs = attrsVon(psr);
    const stil = psr.getAttribute('AppliedParagraphStyle');
    if (!abs) abs = { stil, attrs: pattrs, runs: [] };
    else if (!abs.runs.length) { abs.stil = stil; abs.attrs = pattrs; }
    for (const csr of psr.children) {
      if (csr.localName !== 'CharacterStyleRange') continue;
      const cattrs = attrsVon(csr);
      cattrs.cstil = csr.getAttribute('AppliedCharacterStyle');
      for (const k of csr.children) {
        if (k.localName === 'Content') abs.runs.push({ text: k.textContent, attrs: cattrs });
        else if (k.localName === 'Br') {
          abs.attrs = { ...abs.attrs, umbruch: csr.getAttribute('ParagraphBreakType') || '' };
          if (!abs.runs.length) abs.runs.push({ text: '', attrs: cattrs });
          aus.push(abs); abs = { stil, attrs: pattrs, runs: [] };
        }
      }
    }
  }
  if (abs && abs.runs.length) aus.push(abs);
  return aus;
}
function attrsVon(el) {
  const a = {};
  for (const k of ['PointSize', 'FontStyle', 'FillColor', 'FillTint', 'Tracking', 'BaselineShift', 'Capitalization', 'HorizontalScale', 'Justification', 'LeftIndent', 'RightIndent', 'FirstLineIndent', 'SpaceAfter', 'SpaceBefore', 'Hyphenation', 'SpanColumnType', 'AppliedLanguage', 'ParagraphBreakType']) { const v = el.getAttribute(k); if (v != null) a[k] = v; }
  const props = [...el.children].find((c) => c.localName === 'Properties');
  if (props) for (const c of props.children) { if (c.localName === 'Leading' || c.localName === 'AppliedFont') a[c.localName] = c.textContent; if (c.localName === 'TabList') a.TabList = tabsLesen(c); }
  return a;
}

function absatzHtml(doc, abs, basisGroesse) {
  const ps = doc.pstile[abs.stil] || {};
  const g = (k) => abs.attrs[k] ?? ps[k];
  // Grundwerte des Absatzes = Absatzformat (+ Absatz-Überschreibungen); Läufe überschreiben nur, was sie selbst tragen.
  const erster = abs.runs[0] ? abs.runs[0].attrs : {};
  const cs0 = erster.cstil && doc.cstile[erster.cstil] || {};
  // Grad des Absatzkastens = wirksamer Grad des ersten Laufs (Lauf > Zeichenformat > Absatz); Schrift und Farbe des Kastens = Absatz
  const size = +(erster.PointSize ?? cs0.PointSize ?? g('PointSize') ?? basisGroesse ?? 12);
  const leadRoh = g('Leading') ?? erster.Leading ?? cs0.Leading;
  const lead = leadRoh && leadRoh !== 'Auto' ? +leadRoh : (+(erster.PointSize ?? size)) * 1.2;
  const fam = g('AppliedFont') || 'Goetheanum Variabel';
  const schnitt = g('FontStyle') || 'Klar';
  const farbeP = farbe(doc, g('FillColor'), g('FillTint')) || '#000000';
  let css = `font-size:${n3(size)}px;line-height:${n3(lead)}px;${fontCss(fam, schnitt)}color:${farbeP};`;
  const just = AUSRICHTUNG[g('Justification')]; if (just) css += `text-align:${just};`;
  if (g('LeftIndent')) css += `margin-left:${n3(+g('LeftIndent'))}px;`;
  if (g('RightIndent')) css += `margin-right:${n3(+g('RightIndent'))}px;`;
  if (g('FirstLineIndent')) css += `text-indent:${n3(+g('FirstLineIndent'))}px;`;
  if (g('SpaceAfter')) css += `margin-bottom:${n3(+g('SpaceAfter'))}px;`;
  if (g('SpaceBefore')) css += `margin-top:${n3(+g('SpaceBefore'))}px;`;
  if (g('Hyphenation') === 'false') css += 'hyphens:manual;';
  if (g('SpanColumnType') === 'SpanColumns') css += 'column-span:all;';
  if (abs.attrs.umbruch === 'NextColumn' || abs.attrs.umbruch === 'NextFrame') css += 'break-after:column;';
  const tabs = abs.attrs.TabList || ps.TabList;
  let html = '';
  let ersterTab = true;
  for (const r of abs.runs) {
    const cs = r.attrs.cstil && doc.cstile[r.attrs.cstil] || {};
    const rg = (k) => r.attrs[k] ?? cs[k];
    let s = '';
    const rs = rg('PointSize'); if (rs && +rs !== size) s += `font-size:${n3(+rs)}px;`;
    const rf = rg('AppliedFont') || fam, rsch = rg('FontStyle') || schnitt; if (rf !== fam || rsch !== schnitt) s += fontCss(rf, rsch);
    const rc = rg('FillColor'); if (rc) { const h = farbe(doc, rc, rg('FillTint')); if (h && h !== farbeP) s += `color:${h};`; }
    const rl = rg('Leading'); if (rl && rl !== 'Auto' && +rl !== lead) s += `line-height:${n3(+rl)}px;`;
    const tr = rg('Tracking'); if (tr) s += `letter-spacing:${n3(+tr / 1000)}em;`;
    const bl = rg('BaselineShift'); if (bl) s += `position:relative;top:${n3(-bl)}px;`;
    const cap = rg('Capitalization'); if (cap === 'AllCaps') s += 'text-transform:uppercase;'; else if (cap === 'SmallCaps') s += 'font-variant:small-caps;';
    const hs = rg('HorizontalScale'); if (hs && +hs !== 100) s += Math.abs(+hs - 100) > 6 ? `display:inline-block;transform:scaleX(${(+hs / 100).toFixed(2)});transform-origin:left;` : `letter-spacing:${n3((+hs - 100) / 100 * 0.5)}em;`;
    const text = String(r.text).split(' ').map((z) => esc(z).replace(/\t/g, (m, i) => {
      if (ersterTab && tabs && tabs.length && i === 0) { ersterTab = false; return `<span class="tab" style="display:inline-block;width:${n3(tabs[0].pos)}px"></span>`; }
      return '<span class="tab" style="display:inline-block;width:1.4em"></span>';
    })).join('<br>');
    const ra = { ...r.attrs }; delete ra.TabList;
    html += `<span${s ? ` style="${s}"` : ''} data-run="${esc(JSON.stringify(ra))}">${text}</span>`;
  }
  const p1 = abs._erster ? `margin-top:${n3(-(lead - size * 1.15) / 2)}px;` : '';
  const pa = { ...abs.attrs }; delete pa.TabList; delete pa.umbruch;
  const sprache = SPRACHE[String(erster.AppliedLanguage || cs0.AppliedLanguage || g('AppliedLanguage') || '').replace(/^\$ID\//, '')] || '';
  return `<p style="${css}${p1}"${sprache ? ` lang="${sprache}"` : ''} data-stil="${esc(abs.stil || '')}" data-pattrs="${esc(JSON.stringify(pa))}">${html || '<br>'}</p>`;
}

function textRahmen(ctx, el, m) {
  const { doc, opts } = ctx;
  const sid = el.getAttribute('ParentStory');
  if (opts.stories && !opts.stories[sid]) return '';
  const { d, pts } = pfadD(el);
  if (!pts.length) return '';
  const bb = bbox(pts);
  const pref = [...el.children].find((c) => c.localName === 'TextFramePreference');
  const cols = pref ? +(pref.getAttribute('TextColumnCount') || 1) : 1;
  const gap = pref ? +(pref.getAttribute('TextColumnGutter') || 12) : 12;
  const vj = pref ? pref.getAttribute('VerticalJustification') : '';
  let inset = [0, 0, 0, 0];
  const ip = pref && [...pref.children].find((c) => c.localName === 'Properties');
  const isp = ip && [...ip.children].find((c) => c.localName === 'InsetSpacing');
  if (isp) inset = [...isp.children].map((c) => +c.textContent);
  else if (pref && pref.getAttribute('InsetSpacing')) inset = Array(4).fill(+pref.getAttribute('InsetSpacing'));
  const story = doc.stories[sid];
  const absaetze = (opts.texte && opts.texte[sid]) || (story ? storyAbsaetze(doc, story) : []);
  // Verkettete Rahmen: dieser Rahmen zeigt die Spalten nach den Vorgängern (gleiche Spaltengeometrie)
  let versatz = 0;
  let prev = el.getAttribute('PreviousTextFrame');
  const spaltenBreite = (bb.w - inset[1] - inset[3] - (cols - 1) * gap) / cols;
  while (prev && prev !== 'n') {
    const pe = doc.spreads.map((s) => s.el.querySelector(`TextFrame[Self="${prev}"]`)).find(Boolean);
    if (!pe) break;
    const pp = [...pe.children].find((c) => c.localName === 'TextFramePreference');
    versatz += +(pp && pp.getAttribute('TextColumnCount') || 1);
    prev = pe.getAttribute('PreviousTextFrame');
  }
  const fill = farbe(doc, el.getAttribute('FillColor'), el.getAttribute('FillTint'));
  const { stil } = transparenz(ctx, el, pts);
  const flex = vj === 'CenterAlign' ? 'display:flex;flex-direction:column;justify-content:center;' : vj === 'BottomAlign' ? 'display:flex;flex-direction:column;justify-content:flex-end;' : vj === 'JustifyAlign' ? 'display:flex;flex-direction:column;justify-content:space-between;' : '';
  const spalten = cols > 1 ? `column-count:${cols};column-gap:${n3(gap)}px;column-fill:auto;` : '';
  const weiter = el.getAttribute('NextTextFrame') && el.getAttribute('NextTextFrame') !== 'n';
  const innen = `<div xmlns="http://www.w3.org/1999/xhtml" class="tf" data-story="${esc(sid)}" ${weiter ? 'data-weiter="1"' : ''} ${opts.bearbeitbar ? 'contenteditable="true" spellcheck="false"' : ''} style="box-sizing:border-box;width:${n3(bb.w)}px;height:${n3(bb.h)}px;padding:${inset.map((v) => n3(v) + 'px').join(' ')};${flex}${spalten}overflow:visible;margin-left:${versatz ? n3(-versatz * (spaltenBreite + gap)) + 'px' : '0'}">${absaetze.map((a, i) => absatzHtml(doc, i ? a : { ...a, _erster: true })).join('')}</div>`;
  return `<g transform="${mStr(m)}" style="${stil}">${fill ? `<path d="${d}" fill="${fill}"/>` : ''}<foreignObject x="${n3(bb.x)}" y="${n3(bb.y)}" width="${n3(bb.w)}" height="${n3(bb.h + 24)}" style="overflow:hidden">${innen}</foreignObject></g>`;
}

/* Stories einer Seite (für Slot-Zuordnung): [{story, text}] */
export function seitenStories(doc, name) {
  const seite = doc.seiten[name]; if (!seite) return [];
  const aus = [];
  for (const tf of seite.spread.el.getElementsByTagName('TextFrame')) {
    const m = matrix(tf.getAttribute('ItemTransform'));
    const { pts } = pfadD(tf); if (!pts.length) continue;
    const bb = bbox(pts); const cx = m[0] * (bb.x + bb.w / 2) + m[2] * (bb.y + bb.h / 2) + m[4];
    if (cx < seite.x || cx > seite.x + seite.w) continue;
    const story = doc.stories[tf.getAttribute('ParentStory')];
    aus.push({ story: tf.getAttribute('ParentStory'), text: story ? storyAbsaetze(doc, story).map((a) => a.runs.map((r) => r.text).join('')).join('¶') : '' });
  }
  return aus;
}

/* Übersatz prüfen: Rahmen, deren Text nicht in die Spalten passt (nach dem Einhängen ins DOM aufrufen). */
export function uebersatzPruefen(el) {
  const aus = [];
  for (const tf of el.querySelectorAll('.tf')) {
    // Luft: eine Zeile im grössten Zeilenabstand des Rahmens (InDesign lässt Unterlängen über den Rand)
    const lead = Math.max(12, ...[...tf.querySelectorAll('p')].map((p) => parseFloat(p.style.lineHeight) || 0));
    // Verkettete Rahmen geben ihren Überlauf an den nächsten Rahmen weiter – nur der letzte zählt
    const breit = !tf.dataset.weiter && tf.scrollWidth > tf.clientWidth + 2;
    const hoch = tf.scrollHeight > tf.clientHeight + lead * 1.1;
    tf.classList.toggle('uebersatz', breit || hoch);
    if (breit || hoch) aus.push(tf.dataset.story);
  }
  return aus;
}
