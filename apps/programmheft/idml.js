/* Programmheft · IDML-Export
   ---------------------------------------------------------------------------
   Baut aus dem Zustand des Live-Editors ein InDesign-Dokument (IDML) mit vier
   A5-Seiten, frei von einer Vorlage. Geliefert wird ein ZIP:
     Programmheft.idml
     Links/  Titelbild, Campusplan mit Nummern, Logo (PNG, 300 ppi)
   InDesign sucht fehlende Verknüpfungen selbst im Ordner «Links» neben dem
   Dokument. Absatzformate (Titel, Datum, Programm, Pause, Legende, Kontakt)
   sind angelegt, damit das Heft in InDesign weiterbearbeitet werden kann.
   ------------------------------------------------------------------------- */

import { zipSchreiben } from '../lt-programm/idml-export.js';

const te = new TextEncoder();
const MM = 72 / 25.4;
const B = 148 * MM, H = 210 * MM;          // A5 in pt
const OX = -B / 2, OY = -H / 2;            // Seite liegt mittig auf dem Druckbogen

const x = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const n = (v) => Math.round(v * 1000) / 1000;
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16)).join(' ');

let zaehler = 0;
const id = (p) => `${p}${(++zaehler).toString(36)}`;

function pfad(xmm, ymm, wmm, hmm) {
  const [l, t, r, b] = [OX + xmm * MM, OY + ymm * MM, OX + (xmm + wmm) * MM, OY + (ymm + hmm) * MM].map(n);
  const p = (a, c) => `<PathPointType Anchor="${a} ${c}" LeftDirection="${a} ${c}" RightDirection="${a} ${c}"/>`;
  return `<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>${p(l, t)}${p(l, b)}${p(r, b)}${p(r, t)}</PathPointArray></GeometryPathType></PathGeometry></Properties>`;
}

function flaeche(xmm, ymm, wmm, hmm, farbe, polygon) {
  let geo = pfad(xmm, ymm, wmm, hmm);
  if (polygon) {
    const pts = polygon.map(([a, c]) => [n(OX + a * MM), n(OY + c * MM)]);
    geo = `<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>${pts.map(([a, c]) => `<PathPointType Anchor="${a} ${c}" LeftDirection="${a} ${c}" RightDirection="${a} ${c}"/>`).join('')}</PathPointArray></GeometryPathType></PathGeometry></Properties>`;
  }
  return `<Polygon Self="${id('p')}" ContentType="Unassigned" FillColor="${farbe}" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0">${geo}</Polygon>`;
}

// Bild in einen Rahmen: füllt proportional (wie object-fit: cover) oder passt ein (contain).
function bild(xmm, ymm, wmm, hmm, datei, pxB, pxH, fuellen) {
  const gb = pxB * 72 / 300, gh = pxH * 72 / 300;        // Bild mit 300 ppi
  const fw = wmm * MM, fh = hmm * MM;
  const s = (fuellen ? Math.max : Math.min)(fw / gb, fh / gh);
  const tx = OX + xmm * MM + (fw - gb * s) / 2, ty = OY + ymm * MM + (fh - gh * s) / 2;
  return `<Rectangle Self="${id('r')}" ContentType="GraphicType" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0">${pfad(xmm, ymm, wmm, hmm)}
  <Image Self="${id('i')}" ItemTransform="${n(s)} 0 0 ${n(s)} ${n(tx)} ${n(ty)}"><Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="${n(gb)}" Bottom="${n(gh)}"/></Properties>
  <Link Self="${id('l')}" LinkResourceURI="file:Links/${x(datei)}" LinkResourceFormat="$ID/${datei.endsWith('.png') ? 'PNG' : 'JPEG'}" StoredState="Normal" LinkClassID="35906" LinkClientID="257"/></Image></Rectangle>`;
}

function rahmen(xmm, ymm, wmm, hmm, story, spalten = 1, vertikal = 'TopAlign') {
  return `<TextFrame Self="${id('t')}" ParentStory="${story}" ContentType="TextType" ItemTransform="1 0 0 1 0 0">${pfad(xmm, ymm, wmm, hmm)}
  <TextFramePreference TextColumnCount="${spalten}" TextColumnGutter="${n(6 * MM)}" VerticalJustification="${vertikal}"/></TextFrame>`;
}

// Fett aus dem Editor (<b>) wird zum Zeichenformat «Fett».
function laeufe(html, extra = '') {
  const teile = String(html).split(/(<b>.*?<\/b>)/g).filter(Boolean);
  return teile.map((t) => {
    const fett = /^<b>/.test(t);
    const txt = t.replace(/<\/?b>/g, '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');
    return `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/${fett ? 'Fett' : '$ID/[No character style]'}"${extra}><Content>${x(txt)}</Content></CharacterStyleRange>`;
  }).join('');
}

function story(sid, absaetze) {
  const inhalt = absaetze.map(([stil, lauf], i) =>
    `<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/${stil}">${lauf}${i < absaetze.length - 1 ? '<Br/>' : ''}</ParagraphStyleRange>`).join('');
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Story Self="${sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
${inhalt}</Story></idPkg:Story>`;
}

const schrift = (familie, schnitt) => `<Properties><AppliedFont type="string">${familie}</AppliedFont></Properties>`;
function absatzformat(name, a) {
  const { font = 'Goetheanum Schrift', schnitt = 'Klar', grad = 11, zab = 14, farbe = 'Color/Black', attr = '', tabs = '' } = a;
  return `<ParagraphStyle Self="ParagraphStyle/${name}" Name="${name}" FontStyle="${schnitt}" PointSize="${grad}" FillColor="${farbe}" Hyphenation="false" ${attr}>
  <Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><AppliedFont type="string">${font}</AppliedFont><Leading type="unit">${zab}</Leading>${tabs}</Properties></ParagraphStyle>`;
}

/* S: Zustand des Editors · farben: {akzent, ort, pause} als #rrggbb
   bilder: {titel:{name,bytes,b,h}, plan:{…}, logo:{…}} · orte: Liste der Legende */
export async function baueIdml(S, farben, bilder, orte) {
  zaehler = 0;
  const stories = [];
  const neueStory = (absaetze) => { const sid = id('u'); stories.push([sid, story(sid, absaetze)]); return sid; };
  const esc1 = (t) => x(t);

  // Seite 1 – Titel
  const kante = { schraege: [[0, 0], [148, 0], [148, 112], [0, 126]],
    trapez: [[0, 0], [148, 0], [148, 112], [115.4, 126], [32.6, 126], [0, 112]],
    gerade: [[0, 0], [148, 0], [148, 126], [0, 126]] }[S.kante] || null;
  const sTitel = neueStory([
    ['Titel', `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>${esc1(S.titel)}</Content></CharacterStyleRange>`],
    ...String(S.wann).split('\n').map((z) => ['Datum', `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>${esc1(z)}</Content></CharacterStyleRange>`])]);
  const sCredit = neueStory([['Bildnachweis', laeufe(esc1(S.credit || ''))]]);
  // Schrift: «alles» setzt auch Daten, Legende und Kontakt in die Hausschrift
  const nurHaus = S.stimme === 'alles';
  const TX = nurHaus ? { font: 'Goetheanum Schrift', schnitt: 'Klar' } : { font: 'Source Sans 3', schnitt: 'Regular' };
  const FETT = nurHaus ? 'Laut' : 'Bold';
  const seite1 = [
    bild(0, 110, 148, 100, bilder.titel.name, bilder.titel.b, bilder.titel.h, true),
    flaeche(0, 0, 148, 126, 'Color/Akzent', kante),
    bild(54.6, 20, 38.8, 6.5, bilder.logo.name, bilder.logo.b, bilder.logo.h, false),
    rahmen(12, 32, 124, 64, sTitel, 1, 'CenterAlign'),
    rahmen(70, 202, 74, 5, sCredit, 1, 'BottomAlign')];

  // Seiten 2–3 – Programm
  const NR = (o) => orte.indexOf((o || '').trim()) + 1;
  const programm = (L, kopf) => neueStory([
    ...(kopf ? [['Programm Kopf', `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>Programm</Content></CharacterStyleRange>`]] : []),
    ...L.map((z) => [z.pause ? 'Programm Pause' : 'Programm',
      `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/Fett"><Content>${esc1(z.zeit)}</Content></CharacterStyleRange>`
      + `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>\t</Content></CharacterStyleRange>`
      + laeufe(z.text)
      + (z.ort ? `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/Ort"><Content>  ${NR(z.ort) ? NR(z.ort) + ' ' : ''}${esc1(z.ort)}</Content></CharacterStyleRange>` : '')])]);
  const seite2 = [rahmen(9, 13, 130, 187, programm(S.seiten[0], true))];
  const seite3 = [rahmen(9, 13, 130, 187, programm(S.seiten[1], false))];

  // Seite 4 – Campus
  const sInfo = neueStory([['Programm Kopf', `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>${esc1(S.info)}</Content></CharacterStyleRange>`]]);
  const sLeg = neueStory(orte.map((o, k) => ['Legende',
    `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/Nummer"><Content>${k + 1}</Content></CharacterStyleRange><CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>\t${esc1(o)}</Content></CharacterStyleRange>`]));
  const sKontakt = neueStory(String(S.kontakt).split('\n').map((z) => ['Kontakt', `<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Content>${esc1(z)}</Content></CharacterStyleRange>`]));
  const legH = Math.ceil(orte.length / 3) * 6 + 2;
  const seite4 = [
    rahmen(11, 13, 126, 12, sInfo),
    bild(11, 28, 126, 170 - 28 - legH - 14, bilder.plan.name, bilder.plan.b, bilder.plan.h, false),
    rahmen(11, 170 - legH, 126, legH + 10, sLeg, 3),
    rahmen(11, 183, 90, 17, sKontakt, 1, 'BottomAlign'),
    bild(107, 194, 30, 6, bilder.logoBlau.name, bilder.logoBlau.b, bilder.logoBlau.h, false)];

  const seiten = [seite1, seite2, seite3, seite4];
  const spreads = seiten.map((inhalt, i) => {
    const sid = `sp${i + 1}`;
    return [sid, `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Spread Self="${sid}" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 ${n(i * (H + 40))}" ShowMasterItems="true" SpreadHidden="false" PageTransitionType="None">
<Page Self="pg${i + 1}" Name="${i + 1}" AppliedMaster="ms" GeometricBounds="0 0 ${n(H)} ${n(B)}" ItemTransform="1 0 0 1 ${n(OX)} ${n(OY)}" MasterPageTransform="1 0 0 1 0 0">
<MarginPreference ColumnCount="1" ColumnGutter="12" Top="${n(13 * MM)}" Bottom="${n(10 * MM)}" Left="${n(9 * MM)}" Right="${n(9 * MM)}"/></Page>
${inhalt.join('\n')}
</Spread></idPkg:Spread>`];
  });

  const graphic = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Graphic xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Akzent" Model="Process" Space="RGB" ColorValue="${rgb(farben.akzent)}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="${x(farben.name)}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Ort" Model="Process" Space="RGB" ColorValue="${rgb(farben.ort)}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="${x(farben.name)} Schrift" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Pause" Model="Process" Space="RGB" ColorValue="${rgb(farben.pause)}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="${x(farben.name)} Tönung" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Color Self="Color/Gold" Model="Process" Space="RGB" ColorValue="${rgb(farben.gold)}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Gold dunkel" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="n"/>
<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>
</idPkg:Graphic>`;

  const tab = (mm, al = 'LeftAlign') => `<TabList type="list"><ListItem type="record"><Alignment type="enumeration">${al}</Alignment><AlignmentCharacter type="string">.</AlignmentCharacter><Leader type="string"></Leader><Position type="unit">${n(mm * MM)}</Position></ListItem></TabList>`;
  const zeileAttr = `LeftIndent="${n(31 * MM)}" FirstLineIndent="${n(-31 * MM)}" SpaceBefore="${n(3 * MM)}" SpaceAfter="${n(3 * MM)}" RuleBelow="true" RuleBelowColor="Color/Black" RuleBelowTint="12" RuleBelowWeight="0.85" RuleBelowOffset="${n(3 * MM)}" RuleBelowLeftIndent="${n(-31 * MM)}"`;
  const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Styles xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<RootCharacterStyleGroup Self="rcsg">
<CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/>
<CharacterStyle Self="CharacterStyle/Fett" Name="Fett" FontStyle="${FETT}"/>
<CharacterStyle Self="CharacterStyle/Ort" Name="Ort" FillColor="Color/Ort"/>
<CharacterStyle Self="CharacterStyle/Nummer" Name="Nummer" FontStyle="${FETT}" FillColor="Color/Gold"/>
</RootCharacterStyleGroup>
<RootParagraphStyleGroup Self="rpsg">
<ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false" FontStyle="Regular" PointSize="12" FillColor="Color/Black"><Properties><AppliedFont type="string">Minion Pro</AppliedFont><Leading type="enumeration">Auto</Leading></Properties></ParagraphStyle>
<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>
${absatzformat('Titel', { schnitt: 'Deutlich', grad: 34, zab: 36, farbe: 'Color/Paper', attr: `Justification="CenterAlign" SpaceAfter="${n(7 * MM)}"` })}
${absatzformat('Datum', { schnitt: 'Deutlich', grad: 15, zab: 19.5, farbe: 'Color/Paper', attr: 'Justification="CenterAlign"' })}
${absatzformat('Bildnachweis', { ...TX, grad: 6.5, zab: 8, farbe: 'Color/Paper', attr: 'Justification="RightAlign"' })}
${absatzformat('Programm Kopf', { schnitt: 'Deutlich', grad: 22, zab: 26, farbe: 'Color/Ort', attr: `SpaceAfter="${n(6 * MM)}"` })}
${absatzformat('Programm', { ...TX, grad: 12, zab: 16.8, attr: zeileAttr, tabs: tab(31) })}
<ParagraphStyle Self="ParagraphStyle/Programm Pause" Name="Programm Pause" ParagraphShadingOn="true" ParagraphShadingColor="Color/Pause" ParagraphShadingTopOffset="${n(3 * MM)}" ParagraphShadingBottomOffset="${n(3 * MM)}" ParagraphShadingLeftOffset="${n(31 * MM + 3 * MM)}" ParagraphShadingRightOffset="0"><Properties><BasedOn type="object">ParagraphStyle/Programm</BasedOn></Properties></ParagraphStyle>
${absatzformat('Legende', { ...TX, grad: 10, zab: 17, tabs: tab(6) })}
${absatzformat('Kontakt', { ...TX, grad: 9, zab: 13 })}
</RootParagraphStyleGroup>
<RootObjectStyleGroup Self="rosg"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>
</idPkg:Styles>`;

  // Musterseite A5: ohne sie legt InDesign eine Standard-Musterseite (Letter) samt eigener Seiten an.
  const master = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:MasterSpread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<MasterSpread Self="ms" Name="A-Musterseite" NamePrefix="A" BaseName="Musterseite" ShowMasterItems="true" PageCount="1" PrimaryTextFrame="n" ItemTransform="1 0 0 1 0 0">
<Page Self="msp" Name="A" AppliedMaster="n" GeometricBounds="0 0 ${n(H)} ${n(B)}" ItemTransform="1 0 0 1 ${n(OX)} ${n(OY)}" MasterPageTransform="1 0 0 1 0 0">
<MarginPreference ColumnCount="1" ColumnGutter="12" Top="${n(13 * MM)}" Bottom="${n(10 * MM)}" Left="${n(9 * MM)}" Right="${n(9 * MM)}"/></Page>
</MasterSpread></idPkg:MasterSpread>`;
  const prefs = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<idPkg:Preferences xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0">
<DocumentPreference PageHeight="${n(H)}" PageWidth="${n(B)}" PagesPerDocument="1" FacingPages="false" AllowPageShuffle="true" Intent="PrintIntent" CreatePrimaryTextFrame="false" DocumentBleedTopOffset="${n(3 * MM)}" DocumentBleedBottomOffset="${n(3 * MM)}" DocumentBleedInsideOrLeftOffset="${n(3 * MM)}" DocumentBleedOutsideOrRightOffset="${n(3 * MM)}" DocumentBleedUniformSize="true" PageBinding="LeftToRight"/>
<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters"/>
</idPkg:Preferences>`;

  const designmap = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="16.0(0)" ?>
<Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="16.0" Self="d" StoryList="${stories.map(([s]) => s).join(' ')}" ZeroPoint="0 0" ActiveLayer="ly1" CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">
<Language Self="Language/$ID/German%3a Swiss 2006 Reform" Name="$ID/German: Swiss 2006 Reform" SingleQuotes="‹›" DoubleQuotes="«»" PrimaryLanguageName="$ID/German" SublanguageName="$ID/Swiss 2006 Reform" Id="2310" HyphenationVendor="Duden" SpellingVendor="Duden"/>
<idPkg:Graphic src="Resources/Graphic.xml"/>
<idPkg:Styles src="Resources/Styles.xml"/>
<idPkg:Preferences src="Resources/Preferences.xml"/>
<Layer Self="ly1" Name="Ebene 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"/>
<idPkg:MasterSpread src="MasterSpreads/MasterSpread_ms.xml"/>
${spreads.map(([s]) => `<idPkg:Spread src="Spreads/Spread_${s}.xml"/>`).join('\n')}
<Section Self="sec1" Length="4" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStart="1" Marker="" PageStart="pg1" SectionPrefix=""/>
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
  spreads.forEach(([s, xml]) => t(`Spreads/Spread_${s}.xml`, xml));
  stories.forEach(([s, xml]) => t(`Stories/Story_${s}.xml`, xml));
  const idml = await zipSchreiben(dateien);

  const paket = new Map([['Programmheft.idml', idml]]);
  Object.values(bilder).forEach((b) => paket.set(`Links/${b.name}`, b.bytes));
  return zipSchreiben(paket);
}
