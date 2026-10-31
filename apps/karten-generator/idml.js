/* Kartentool · IDML-Export
   ---------------------------------------------------------------------------
   Schreibt die Campus-Karte als InDesign-Dokument (IDML), frei von einer
   Vorlage. Die Grundkarte (Gelände, Aquarell, Kompass) kommt als verknüpftes
   PDF; Marken, Schriftzüge, Titel und Legende sind native Objekte mit Farb-
   feldern und Absatzformaten — dieselben Formen, aus denen die Vorschau ihr
   SVG zeichnet (szeneModell() in app.js). Geliefert wird ein ZIP:
     <name>.idml
     Links/           grundkarte.pdf, logo.pdf, ggf. titellogo.pdf
     Document fonts/  Hausschrift (Variable, OFL) — InDesign aktiviert sie
                      beim Öffnen selbst
   Die Objekt-Erzeugung (kartenObjekte) ist eigenständig: der Tagungs-Reader
   setzt mit ihr die Karte in seine eigene Vorlage (apps/lt-reader/
   idml-export.js), mit Präfix für IDs, Formate, Farbfelder und Ebenen.
   Spezifikation: docs/specs/campus-karte-idml.md, docs/specs/lt-reader-idml.md
   ------------------------------------------------------------------------- */

import { zipSchreiben } from '../lt-programm/idml-export.js';

const te = new TextEncoder();
const MM = 72 / 25.4;
const KAPPA = 0.5522847498;

const x = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const n = (v) => Math.round(v * 1000) / 1000;
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16)).join(' ');

// Ebenen von unten nach oben — so stehen sie in designmap.xml.
const EBENEN = [['grundkarte', 'Grundkarte'], ['marken', 'Marken'], ['beschriftung', 'Beschriftung'], ['legende', 'Legende']];

// Absatzformate je Rolle der Textformen; Grad, Farbe und Zeilenabstand
// kommen aus der ersten Form der Rolle, Abweichungen setzt der Lauf.
const ROLLEN = {
  titel: { name: 'Titel', schrift: 'sprache' },
  untertitel: { name: 'Untertitel', schrift: 'sprache' },
  gebaeude: { name: 'Gebäude', schrift: 'sprache', mitte: true },
  kopf: { name: 'Legende Gruppe', schrift: 'sprache' },
  eintrag: { name: 'Legende Eintrag', schrift: 'sprache' },
  notiz: { name: 'Legende Notiz', schrift: 'sprache' },
  ziffer: { name: 'Ziffer', schrift: 'zahl', mitte: true }
};

/* Pfad-Daten (absolut M/L/H/V/C/Z, wie die Icons und Badges) in Teilpfade
   mit Bézier-Griffen: je Punkt Anker, Griff davor (links), Griff danach. */
export function pfadLesen(d) {
  const teile = String(d).match(/[A-Za-z]|-?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?/g) || [];
  const pfade = [];
  let pfad = null, befehl = null, i = 0, aktuell = [0, 0];
  const zahl = () => parseFloat(teile[i++]);
  const punkt = (a) => ({ a, l: a, r: a });
  while (i < teile.length) {
    if (/[A-Za-z]/.test(teile[i])) befehl = teile[i++];
    if (befehl === 'M') {
      aktuell = [zahl(), zahl()];
      pfad = { punkte: [punkt(aktuell)], offen: true };
      pfade.push(pfad);
      befehl = 'L';   // weitere Paare nach M sind Linien
    } else if (befehl === 'L') {
      aktuell = [zahl(), zahl()]; pfad.punkte.push(punkt(aktuell));
    } else if (befehl === 'H') {
      aktuell = [zahl(), aktuell[1]]; pfad.punkte.push(punkt(aktuell));
    } else if (befehl === 'V') {
      aktuell = [aktuell[0], zahl()]; pfad.punkte.push(punkt(aktuell));
    } else if (befehl === 'C') {
      const c1 = [zahl(), zahl()], c2 = [zahl(), zahl()];
      aktuell = [zahl(), zahl()];
      pfad.punkte[pfad.punkte.length - 1].r = c1;
      pfad.punkte.push({ a: aktuell, l: c2, r: aktuell });
    } else if (befehl === 'Z' || befehl === 'z') {
      pfad.offen = false;
      // Endet der Pfad auf seinem Anfang, verschmelzen beide Punkte.
      const p = pfad.punkte, erst = p[0], letzt = p[p.length - 1];
      if (p.length > 1 && Math.abs(erst.a[0] - letzt.a[0]) < 1e-6 && Math.abs(erst.a[1] - letzt.a[1]) < 1e-6) {
        erst.l = letzt.l; p.pop();
      }
      aktuell = erst.a;
      befehl = null;
    } else {
      throw new Error(`Pfadbefehl «${befehl}» wird nicht gelesen`);
    }
  }
  return pfade;
}

/* Die Karte als IDML-Objekte, ohne Dokument drumherum. Nullpunkt ist die
   Mitte des Blatts (so liegen Seite und Doppelseite im IDML um 0 0).
   e: { modell, geometrie, farbnamen, textBreite, links, immerFarben,
        praefix (vor jeder Self-ID), namen (vor Format- und Ebenennamen),
        sprache (Sprache der Absatzformate, InDesign-Name) }
   Gibt { inhalt: [Spread-Objekte], stories: [[Self, XML]], absatzformate:
   XML, farben: [[hex, Self]], ebenen: [{ self, name, gesperrt }],
   aktiveEbene } zurück. */
export function kartenObjekte(e) {
  const { modell, geometrie: g, farbnamen = {}, textBreite, links = {}, praefix = '', namen = '', sprache = 'German: Swiss 2006 Reform' } = e;
  const k = g.skala;                                    // Blatt-mm → Endformat-mm
  const B = g.trimBreite * MM, H = g.trimHoehe * MM;
  const OX = -B / 2, OY = -H / 2;                       // Seite mittig auf dem Druckbogen
  const P = (xmm, ymm) => [OX + xmm * k * MM, OY + ymm * k * MM];
  const pt = (mm) => mm * k * MM;

  let zaehler = 0;
  const id = (p) => `${praefix}${p}${(++zaehler).toString(36)}`;

  /* ---------- Farbfelder ---------- */
  const felder = new Map();                            // hex → Self
  const feld = (hex) => {
    if (!hex) return 'Swatch/None';
    const h = hex.toLowerCase();
    if (h === '#ffffff') return 'Color/Paper';
    if (!felder.has(h)) {
      let name = farbnamen[h] || `${namen}Farbe ${h.slice(1)}`;
      while ([...felder.values()].includes(`Color/${name}`)) name += ' ·';
      felder.set(h, `Color/${name}`);
    }
    return felder.get(h);
  };

  /* ---------- Geometrie ---------- */
  const punktXml = ({ a, l, r }) => `<PathPointType Anchor="${n(a[0])} ${n(a[1])}" LeftDirection="${n(l[0])} ${n(l[1])}" RightDirection="${n(r[0])} ${n(r[1])}"/>`;
  const geometrie = (pfade) => `<Properties><PathGeometry>${pfade.map((p) =>
    `<GeometryPathType PathOpen="${p.offen ? 'true' : 'false'}"><PathPointArray>${p.punkte.map(punktXml).join('')}</PathPointArray></GeometryPathType>`).join('')}</PathGeometry></Properties>`;
  const rechteckPfad = (l, t, r, b) => ({ offen: false, punkte: [[l, t], [l, b], [r, b], [r, t]].map((a) => ({ a, l: a, r: a })) });
  const umBlatt = (pfade, m) => {                       // lokale Koordinaten (Matrix m) → Druckbogen
    const tr = ([px, py]) => P(m[0] * px + m[2] * py + m[4], m[1] * px + m[3] * py + m[5]);
    return pfade.map((p) => ({ offen: p.offen, punkte: p.punkte.map(({ a, l, r }) => ({ a: tr(a), l: tr(l), r: tr(r) })) }));
  };
  const kreisPfad = (cx, cy, r) => {
    const h = r * KAPPA;
    const pkt = (ax, ay, lx, ly, rx, ry) => ({ a: [ax, ay], l: [lx, ly], r: [rx, ry] });
    return { offen: false, punkte: [
      pkt(cx, cy - r, cx - h, cy - r, cx + h, cy - r),
      pkt(cx + r, cy, cx + r, cy - h, cx + r, cy + h),
      pkt(cx, cy + r, cx + h, cy + r, cx - h, cy + r),
      pkt(cx - r, cy, cx - r, cy + h, cx - r, cy - h)] };
  };
  // Rundrechteck (Pillen): Ecken als Viertelkreise.
  const rundPfad = (l, t, w, h, rad) => {
    const r = Math.min(rad, w / 2, h / 2), c = r * KAPPA;
    const R = l + w, U = t + h;
    const pkt = (ax, ay, lx, ly, rx, ry) => ({ a: [ax, ay], l: [lx, ly], r: [rx, ry] });
    return { offen: false, punkte: [
      pkt(l + r, t, l + r - c, t, l + r, t), pkt(R - r, t, R - r, t, R - r + c, t),
      pkt(R, t + r, R, t + r - c, R, t + r), pkt(R, U - r, R, U - r, R, U - r + c),
      pkt(R - r, U, R - r + c, U, R - r, U), pkt(l + r, U, l + r, U, l + r - c, U),
      pkt(l, U - r, l, U - r + c, l, U - r), pkt(l, t + r, l, t + r, l, t + r - c)] };
  };

  const strich = (f) => (f.stroke
    ? `StrokeColor="${feld(f.stroke)}" StrokeWeight="${n(pt(f.sw))}" StrokeAlignment="CenterAlignment" EndCap="ButtEndCap" EndJoin="MiterEndJoin"`
    : 'StrokeColor="Swatch/None" StrokeWeight="0"');
  const flaeche = (art, f, pfade, ebene) => `<${art} Self="${id('f')}" ContentType="Unassigned"${ebene} FillColor="${feld(f.fill)}" ${strich(f)} ItemTransform="1 0 0 1 0 0">${geometrie(pfade)}</${art}>`;

  /* ---------- Text ---------- */
  const stories = [];
  const formate = new Map();                           // rolle → erste Form
  const textRahmen = (f, ebene) => {
    const rolle = ROLLEN[f.rolle] ? f.rolle : 'eintrag';
    if (!formate.has(rolle)) formate.set(rolle, f);
    const basis = formate.get(rolle);
    const mitte = f.anker === 'mitte';
    // Grundlinie der ersten Zeile liegt fest auf y (FixedHeight); der
    // Rahmen wächst mit dem Text (Breite automatisch, keine Umbrüche).
    const grad = pt(f.groesse);
    const breite = Math.max(...f.zeilen.map((z) => textBreite(z, f.schrift, f.groesse))) * k * MM;
    const w = breite * 1.15 + 4;
    const oben = -grad, unten = (f.zeilen.length - 1) * pt(f.zab || 0) + grad * 0.4;
    const l = mitte ? -w / 2 : 0;
    const w0 = (f.winkel || 0) * Math.PI / 180;
    const [ax, ay] = P(f.x, f.y);
    const m = [Math.cos(w0), Math.sin(w0), -Math.sin(w0), Math.cos(w0), ax, ay];
    // Die Ausrichtung folgt dem Anker der Form, nicht nur dem Format.
    const ausrichtung = mitte !== Boolean(ROLLEN[rolle].mitte) ? ` Justification="${mitte ? 'CenterAlign' : 'LeftAlign'}"` : '';
    const abw = [];
    if (Math.abs(f.groesse - basis.groesse) > 1e-6) abw.push(`PointSize="${n(grad)}"`);
    if ((f.farbe || '').toLowerCase() !== (basis.farbe || '').toLowerCase()) abw.push(`FillColor="${feld(f.farbe)}"`);
    const sid = id('u');
    const absaetze = f.zeilen.map((z, i) => `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"${abw.length ? ' ' + abw.join(' ') : ''}><Content>${x(z)}</Content>${i < f.zeilen.length - 1 ? '<Br/>' : ''}</CharacterStyleRange>`).join('');
    stories.push([sid, `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Story Self="${sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/${x(namen + ROLLEN[rolle].name)}"${ausrichtung}>${absaetze}</ParagraphStyleRange></Story></idPkg:Story>`]);
    const referenz = mitte ? 'TopCenterPoint' : 'TopLeftPoint';
    return `<TextFrame Self="${id('t')}" ParentStory="${sid}" ContentType="TextType"${ebene} FillColor="Swatch/None" StrokeColor="Swatch/None" ItemTransform="${m.map(n).join(' ')}">${geometrie([rechteckPfad(n(l), n(oben), n(l + w), n(unten))])}
<TextFramePreference TextColumnCount="1" FirstBaselineOffset="FixedHeight" MinimumFirstBaselineOffset="${n(grad)}" VerticalJustification="TopAlign" AutoSizingType="HeightAndWidth" AutoSizingReferencePoint="${referenz}" UseNoLineBreaksForAutoSizing="true"><Properties><InsetSpacing type="list"><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem><ListItem type="unit">0</ListItem></InsetSpacing></Properties></TextFramePreference></TextFrame>`;
  };

  /* ---------- Formen → Objekte ---------- */
  const objekt = (f, ebene) => {
    if (f.form === 'text') return textRahmen(f, ebene);
    if (f.form === 'kreis') { const [cx, cy] = P(f.cx, f.cy); return flaeche('Oval', f, [kreisPfad(cx, cy, pt(f.r))], ebene); }
    if (f.form === 'rechteck') { const [l, t] = P(f.x, f.y); return flaeche('Polygon', f, [rundPfad(l, t, pt(f.b), pt(f.h), pt(f.rx || 0))], ebene); }
    if (f.form === 'pfad') return flaeche('Polygon', f, umBlatt(pfadLesen(f.d), f.m), ebene);
    return '';
  };
  // Ein Element (Marke samt Ziffer, Eintrag) wird eine Gruppe; nur die
  // Gruppe trägt die Ebene.
  const element = (el, ebene) => {
    const attr = ` ItemLayer="${ebene}"`;
    if (el.formen.length === 1) return objekt(el.formen[0], attr);
    return `<Group Self="${id('g')}"${attr} ItemTransform="1 0 0 1 0 0">${el.formen.map((f) => objekt(f, '')).join('\n')}</Group>`;
  };

  // Verknüpftes PDF in einem Rahmen (Blatt-mm), Seite 1, Medienrahmen.
  const pdfRahmen = (link, lmm, tmm, wmm, hmm, ebene) => {
    const [l, t] = P(lmm, tmm);
    const w = pt(wmm), h = pt(hmm);
    const gb = link.breite * MM, gh = link.hoehe * MM;   // PDF-Seite in pt (Endformat-mm)
    return `<Rectangle Self="${id('r')}" ContentType="GraphicType" ItemLayer="${ebene}" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0">${geometrie([rechteckPfad(n(l), n(t), n(l + w), n(t + h))])}
<PDF Self="${id('i')}" ItemTransform="${n(w / gb)} 0 0 ${n(h / gh)} ${n(l)} ${n(t)}"><Properties><GraphicBounds Left="0" Top="0" Right="${n(gb)}" Bottom="${n(gh)}"/></Properties>
<PDFAttribute PageNumber="1" PDFCrop="CropMedia" TransparentBackground="true"/>
<Link Self="${id('l')}" LinkResourceURI="file:Links/${x(link.name)}" LinkResourceFormat="$ID/Adobe Portable Document Format (PDF)" StoredState="Normal" LinkClassID="35906" LinkClientID="257"/></PDF></Rectangle>`;
  };

  /* ---------- Druckbogen ---------- */
  const ly = Object.fromEntries(EBENEN.map(([schluessel]) => [schluessel, `${praefix}ly_${schluessel}`]));
  const inhalt = [];
  if (links.grundkarte) {
    const b = g.beschnitt / k;                          // Beschnitt in Blatt-mm
    inhalt.push(pdfRahmen(links.grundkarte, -b, -b, links.grundkarte.breite / k, links.grundkarte.hoehe / k, ly.grundkarte));
  }
  modell.marken.forEach((el) => inhalt.push(element(el, ly.marken)));
  modell.gebaeude.forEach((el) => inhalt.push(element(el, ly.beschriftung)));
  modell.titel.forEach((el) => inhalt.push(element(el, ly.beschriftung)));
  if (links.titellogo && modell.titelLogo) {
    const t = modell.titelLogo;
    inhalt.push(pdfRahmen(links.titellogo, t.x, t.y, t.breite, t.hoehe, ly.beschriftung));
  }
  if (links.logo && modell.logo) {
    const o = modell.logo;
    inhalt.push(pdfRahmen(links.logo, o.x, o.y, o.breite, o.hoehe, ly.beschriftung));
  }
  modell.legende.forEach((el) => inhalt.push(element(el, ly.legende)));
  /* ---------- Formate ---------- */
  const schriftVon = (f) => (ROLLEN[f.rolle] && ROLLEN[f.rolle].schrift === 'zahl'
    ? ['Goetheanum Variabel', 'Laut'] : ['Goetheanum Variabel', 'Deutlich']);
  const absatzformate = [...formate.entries()].map(([rolle, f]) => {
    const [familie, schnitt] = schriftVon(f);
    const grad = pt(f.groesse);
    const zab = f.zab ? pt(f.zab) : grad * 1.2;
    const ausrichtung = ROLLEN[rolle].mitte ? ' Justification="CenterAlign"' : '';
    const name = namen + ROLLEN[rolle].name;
    return `<ParagraphStyle Self="ParagraphStyle/${x(name)}" Name="${x(name)}" FontStyle="${schnitt}" PointSize="${n(grad)}" FillColor="${feld(f.farbe)}" Hyphenation="false" AppliedLanguage="$ID/${x(sprache)}"${ausrichtung}>
<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><AppliedFont type="string">${familie}</AppliedFont><Leading type="unit">${n(zab)}</Leading></Properties></ParagraphStyle>`;
  }).join('\n');

  // Tinte und leise Tinte stehen immer im Dokument, auch ohne Text.
  (e.immerFarben || []).forEach(feld);

  return {
    inhalt, stories, absatzformate,
    farben: [...felder.entries()],
    ebenen: EBENEN.map(([schluessel, name]) => ({ self: ly[schluessel], name: namen + name, gesperrt: schluessel === 'grundkarte' })),
    aktiveEbene: ly.marken
  };
}

/* Ein RGB-Farbfeld (Self = 'Color/<Name>'). */
export const farbfeldXml = (hex, self) => `<Color Self="${x(self)}" Model="Process" Space="RGB" ColorValue="${rgb(hex)}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="${x(self.slice(6))}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>`;

/* Eine Ebene für designmap.xml. */
export const ebeneXml = (eb) => `<Layer Self="${eb.self}" Name="${x(eb.name)}" Visible="true" Locked="${eb.gesperrt ? 'true' : 'false'}" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"/>`;

export async function baueIdml(e) {
  const { geometrie: g, dateiname, links = {}, schriften = [] } = e;
  const B = g.trimBreite * MM, H = g.trimHoehe * MM;
  const OX = -B / 2, OY = -H / 2;
  const { inhalt, stories, absatzformate, farben, ebenen, aktiveEbene } = kartenObjekte(e);

  const marginalien = '<MarginPreference ColumnCount="1" ColumnGutter="12" Top="0" Bottom="0" Left="0" Right="0"/>';
  const spread = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Spread Self="sp1" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" ShowMasterItems="true" SpreadHidden="false" PageTransitionType="None">
<Page Self="pg1" Name="1" AppliedMaster="ms" GeometricBounds="0 0 ${n(H)} ${n(B)}" ItemTransform="1 0 0 1 ${n(OX)} ${n(OY)}" MasterPageTransform="1 0 0 1 0 0">
${marginalien}</Page>
${inhalt.join('\n')}
</Spread></idPkg:Spread>`;

  const graphic = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Graphic xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
${farben.map(([hex, self]) => farbfeldXml(hex, self)).join('\n')}
<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>
</idPkg:Graphic>`;

  const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Styles xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<RootCharacterStyleGroup Self="rcsg">
<CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/>
</RootCharacterStyleGroup>
<RootParagraphStyleGroup Self="rpsg">
<ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false" FontStyle="Regular" PointSize="12" FillColor="Color/Black"><Properties><AppliedFont type="string">Minion Pro</AppliedFont><Leading type="enumeration">Auto</Leading></Properties></ParagraphStyle>
<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>
${absatzformate}
</RootParagraphStyleGroup>
<RootObjectStyleGroup Self="rosg"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>
</idPkg:Styles>`;

  const master = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:MasterSpread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<MasterSpread Self="ms" Name="A-Musterseite" NamePrefix="A" BaseName="Musterseite" ShowMasterItems="true" PageCount="1" PrimaryTextFrame="n" ItemTransform="1 0 0 1 0 0">
<Page Self="msp" Name="A" AppliedMaster="n" GeometricBounds="0 0 ${n(H)} ${n(B)}" ItemTransform="1 0 0 1 ${n(OX)} ${n(OY)}" MasterPageTransform="1 0 0 1 0 0">
${marginalien}</Page>
</MasterSpread></idPkg:MasterSpread>`;

  const bl = n(g.beschnitt * MM);
  const prefs = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Preferences xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<DocumentPreference PageHeight="${n(H)}" PageWidth="${n(B)}" PagesPerDocument="1" FacingPages="false" AllowPageShuffle="true" Intent="PrintIntent" CreatePrimaryTextFrame="false" DocumentBleedTopOffset="${bl}" DocumentBleedBottomOffset="${bl}" DocumentBleedInsideOrLeftOffset="${bl}" DocumentBleedOutsideOrRightOffset="${bl}" DocumentBleedUniformSize="true" PageBinding="LeftToRight" PageOrientation="Landscape"/>
<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" LineMeasurementUnits="Millimeters" TextSizeMeasurementUnits="Points" TypographicMeasurementUnits="Points"/>
</idPkg:Preferences>`;

  const designmap = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="16.0(0)" ?>
<Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0" Self="d" StoryList="${stories.map(([s]) => s).join(' ')}" ZeroPoint="0 0" ActiveLayer="${aktiveEbene}" CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">
<Language Self="Language/$ID/German%3a Swiss 2006 Reform" Name="$ID/German: Swiss 2006 Reform" SingleQuotes="‹›" DoubleQuotes="«»" PrimaryLanguageName="$ID/German" SublanguageName="$ID/Swiss 2006 Reform" Id="2310" HyphenationVendor="Duden" SpellingVendor="Duden"/>
<idPkg:Graphic src="Resources/Graphic.xml"/>
<idPkg:Styles src="Resources/Styles.xml"/>
<idPkg:Preferences src="Resources/Preferences.xml"/>
${ebenen.map(ebeneXml).join('\n')}
<idPkg:MasterSpread src="MasterSpreads/MasterSpread_ms.xml"/>
<idPkg:Spread src="Spreads/Spread_sp1.xml"/>
<Section Self="sec1" Length="1" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStart="1" Marker="" PageStart="pg1" SectionPrefix=""/>
<idPkg:BackingStory src="XML/BackingStory.xml"/>
${stories.map(([s]) => `<idPkg:Story src="Stories/Story_${s}.xml"/>`).join('\n')}
</Document>`;

  const dateien = new Map();
  const t = (name, s) => dateien.set(name, te.encode(s));
  t('mimetype', 'application/vnd.adobe.indesign-idml-package');
  t('META-INF/container.xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>`);
  t('designmap.xml', designmap);
  t('Resources/Graphic.xml', graphic);
  t('Resources/Styles.xml', styles);
  t('Resources/Preferences.xml', prefs);
  t('MasterSpreads/MasterSpread_ms.xml', master);
  t('XML/BackingStory.xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:BackingStory xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0"><XmlStory Self="bs" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n"><ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle"><CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"/></ParagraphStyleRange></XmlStory></idPkg:BackingStory>`);
  t('Spreads/Spread_sp1.xml', spread);
  stories.forEach(([s, xml]) => t(`Stories/Story_${s}.xml`, xml));
  const idml = await zipSchreiben(dateien);

  const paket = new Map([[dateiname, idml]]);
  Object.values(links).filter((l) => l && l.bytes).forEach((l) => paket.set(`Links/${l.name}`, l.bytes));
  schriften.forEach((f) => paket.set(`Document fonts/${f.name}`, f.bytes));
  return zipSchreiben(paket);
}
