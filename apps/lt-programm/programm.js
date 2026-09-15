/* Tagungsprogramm · Komposition
   ---------------------------------------------------------------------------
   Aus webseite.json (was agriculture-conference.org sagt) und blatt.json (was
   nur auf dem Faltblatt steht) wird EIN Blattmodell gebaut. Die Vorschau
   (index.html) zeigt es, der Export (idml-export.js) schreibt es in die
   InDesign-Vorlage. Gleiche Quelle, gleiche Regeln – kein zweiter Weg.

   Blattmodell:
     { tagung, tage:[{en,de,datum_en,datum_de}], slots:{name:[Absatz…]},
       arbeitsgruppen:[{nr,block,sprachen,titel_1,titel_2,titel_2_stil,namen}],
       hinweise:[{art,text}] }
   Absatz: "Text"  |  {laut, ruhig, text, stil, umbruch}  |  {runs:[{laut|ruhig:true, text}…]}
   (\n = Zeilenumbruch im Absatz; laut = Schnitt Deutlich, ruhig = Schnitt Ruhig).
   ES-Modul ohne Abhängigkeiten – läuft im Browser und in Node.
   ------------------------------------------------------------------------- */

const WOCHENTAG_EN = { Montag: 'Monday', Dienstag: 'Tuesday', Mittwoch: 'Wednesday', Donnerstag: 'Thursday',
  Freitag: 'Friday', Samstag: 'Saturday', Sonntag: 'Sunday' };
const MONAT_EN = { Januar: 'January', Februar: 'February', März: 'March', April: 'April', Mai: 'May', Juni: 'June',
  Juli: 'July', August: 'August', September: 'September', Oktober: 'October', November: 'November', Dezember: 'December' };
const ART_EN = { 'Eröffnung': 'Opening', 'Abschluss': 'Closing', 'Vortrag': 'Lecture', 'Vorträge': 'Lectures',
  'Präsentationen': 'Presentations', 'Präsentation': 'Presentation', 'Michaelbrief': 'Michael Letter',
  'Panelgespräch': 'Panel Conversation', 'Podiumsgespräch': 'Panel Conversation', 'Eurythmie-Aufführung': 'Eurythmy Performance',
  'Eurythmie': 'Eurythmy', 'Festlicher Abend': 'Festive evening', 'Gespräch': 'Conversation' };
const SPRACHE_LABEL = { CN: '中文', ZH: '中文' };

/* Welche Veranstaltungen der Webseite in welchen Rahmen des Blatts fliessen.
   tag = Index des Tagungstags (0 = Mittwoch), zeit wie auf der Webseite.
   «teile» = mehrspaltiger Rahmen, ein Teil je Spalte. */
export const PLENUM_SLOTS = [
  { slot: 'mi_1500', teile: [{ tag: 0, zeit: '15:00' }] },
  { slot: 'mi_1700', teile: [{ tag: 0, zeit: '17:00' }] },
  { slot: 'mi_do_2000', teile: [{ tag: 0, zeit: '20:00' }, { tag: 1, zeit: '20:00' }] },
  { slot: 'morgen_0830', art: 'morgen', teile: [{ tag: 1, zeit: '08:30' }, { tag: 2, zeit: '08:30' }, { tag: 3, zeit: '08:30' }] },
  { slot: 'do_1700', teile: [{ tag: 1, zeit: '17:00' }] },
  { slot: 'fr_1700', teile: [{ tag: 2, zeit: '17:00' }] },
  { slot: 'fr_1900', teile: [{ tag: 2, zeit: '19:00' }] },
  { slot: 'sa_1430', teile: [{ tag: 3, zeit: '14:30' }] },
];

const KURZ = { 0: 'Mi', 1: 'Do', 2: 'Fr', 3: 'Sa' };

function zeitNorm(z) { return (z || '').replace('.', ':').replace(/^(\d):/, '0$1:'); }

export function komponieren(webseite, blatt) {
  const hinweise = [];
  const merken = (art, text) => hinweise.push({ art, text });

  // ---- Tagung und Tage ---------------------------------------------------
  const t = webseite.tagung || {};
  const monatDe = t.monat || 'Februar';
  const monatEn = MONAT_EN[monatDe] || monatDe;
  const tage = (webseite.plenum || []).map((tag) => ({
    de: tag.wochentag,
    en: WOCHENTAG_EN[tag.wochentag] || tag.wochentag,
    datum_de: `${tag.tag}. ${monatDe}`,
    datum_en: `${monatEn} ${tag.tag}`,
    tag: tag.tag,
  }));
  if (tage.length !== 4) merken('struktur', `Die Webseite nennt ${tage.length} Tagungstage, das Blatt hat Platz für 4.`);
  const datumEn = t.von ? `${t.von}–${t.bis} ${monatEn} ${t.jahr}` : '';
  const datumDe = t.datum || '';
  const tagung = {
    jahr: t.jahr || blatt.jahr,
    motto_de: blatt.kopf.motto_de || t.motto || '',
    motto_en: blatt.kopf.motto_en || '',
    datum_de: datumDe,
    datum_en: datumEn,
    stand: webseite.stand || '',
  };
  if (t.motto && blatt.kopf.motto_de && t.motto !== blatt.kopf.motto_de.replace(/\n/g, ' ')) {
    merken('abgleich', `Motto auf der Webseite: «${t.motto}» – in blatt.json steht «${blatt.kopf.motto_de.replace(/\n/g, ' ')}».`);
  }

  // ---- Slots -------------------------------------------------------------
  const slots = {};
  for (const [name, wert] of Object.entries(blatt.feste_slots || {})) slots[name] = wert;

  slots.tage = [];
  tage.forEach((tag, i) => {
    slots.tage.push({ laut: tag.en, ruhig: tag.de });
    slots.tage.push({ stil: 'Daten', text: `${tag.datum_en}\t${tag.datum_de}`, umbruch: i < tage.length - 1 ? 'NextColumn' : undefined });
  });

  slots.kopf_en = [
    { laut: '' },
    { laut: blatt.kopf.motto_en },
    { laut: blatt.kopf.untertitel_en, ruhig: `\n${blatt.kopf.tagung_en}\n${datumEn}` },
  ];
  slots.kopf_de = [
    { ruhig: blatt.kopf.motto_de },
    { runs: [{ ruhig: true, text: blatt.kopf.untertitel_de }, { laut: true, text: `\n${blatt.kopf.tagung_de}\n${datumDe}` }] },
  ];
  slots.stand = [
    { laut: `${blatt.stand.en}\nVisit our website for\nnews and registration` },
    { ruhig: `${blatt.stand.de}\nBesuchen Sie unsere Webseite\nfür Aktuelles und Anmeldung:` },
    { laut: 'www.agriculture-conference.org' },
  ];
  slots.einleitung = [{ laut: blatt.einleitung.en }, { laut: '' }, { ruhig: blatt.einleitung.de }];
  slots.malerei = blatt.malerei;
  slots.sprachen_hinweis = blatt.sprachen_hinweis;

  // ---- Plenum → Rahmen ---------------------------------------------------
  const plenum = webseite.plenum || [];
  const benutzt = new Set();
  const ueber = blatt.plenum || {};
  const eventsBei = (tag, zeit) => (plenum[tag]?.veranstaltungen || []).filter((v) => zeitNorm(v.zeit) === zeitNorm(zeit));

  const zeilenFuer = (v, key) => {
    const o = ueber[key] || {};
    const artEn = ART_EN[v.art] || ART_EN[v.titel] || '';
    let en = o.titel_en || '';
    let de = o.titel_de || '';
    if (!de) de = v.titel_offen ? (v.art || v.titel) : v.titel;
    if (!en) en = v.titel_offen ? (artEn || ART_EN[v.titel] || '') : (ART_EN[v.titel] || '');
    if (v.titel_offen && !o.titel_de) merken('offen', `${key}: Titel auf der Webseite noch «${v.titel}» (${v.art || 'ohne Art'}) – Platzhalter.`);
    if (!en && !v.titel_offen && !o.titel_en) merken('uebersetzung', `${key}: kein englischer Titel für «${v.titel}» – in blatt.json › plenum › ${key} › titel_en eintragen.`);
    const namen = o.namen !== undefined ? o.namen : (v.mitwirkende || []).join(' · ');
    const aus = [{ laut: en, ruhig: de, offen: !!v.titel_offen }];
    if (namen) aus.push({ ruhig: namen });
    return aus;
  };

  for (const regel of PLENUM_SLOTS) {
    const absaetze = [];
    if (regel.art === 'morgen') {
      // Ein Titel über alle drei Vormittage, dann die Mitwirkenden je Tag in eigener Spalte.
      const o = ueber[regel.slot] || {};
      const erste = eventsBei(regel.teile[0].tag, regel.teile[0].zeit)[0];
      const de = o.titel_de || (erste ? (erste.titel_offen ? erste.art : erste.titel) : '');
      const en = o.titel_en || (erste ? ART_EN[erste.art] || '' : '');
      absaetze.push({ laut: en, ruhig: de });
      regel.teile.forEach((teil, i) => {
        const evs = eventsBei(teil.tag, teil.zeit);
        evs.forEach((v) => benutzt.add(v));
        const namen = evs.map((v) => (v.mitwirkende || []).join(' · ')).filter(Boolean).join('\n') || '–';
        if (evs.some((v) => v.titel_offen)) merken('offen', `${regel.slot} (${KURZ[teil.tag]}): Beitrag zum Michaelbrief noch ohne Titel.`);
        absaetze.push({ ruhig: namen, umbruch: i < regel.teile.length - 1 ? 'NextColumn' : undefined });
      });
      if (o.zusatz) absaetze.push(...o.zusatz);
    } else {
      regel.teile.forEach((teil, i) => {
        const evs = eventsBei(teil.tag, teil.zeit);
        if (!evs.length) merken('struktur', `${regel.slot}: keine Veranstaltung ${KURZ[teil.tag]} ${teil.zeit} auf der Webseite.`);
        evs.forEach((v, n) => {
          benutzt.add(v);
          absaetze.push(...zeilenFuer(v, n ? `${regel.slot}#${n + 1}` : regel.slot));
        });
        if (i < regel.teile.length - 1 && absaetze.length) absaetze[absaetze.length - 1].umbruch = 'NextColumn';
      });
    }
    slots[regel.slot] = absaetze;
  }
  plenum.forEach((tag, ti) => (tag.veranstaltungen || []).forEach((v) => {
    if (!benutzt.has(v)) merken('struktur', `Kein Rahmen im Blatt für ${KURZ[ti] || tag.wochentag} ${v.zeit} «${v.titel}» – Vorlage in InDesign ergänzen.`);
  }));

  // ---- Arbeitsgruppen ----------------------------------------------------
  const ueberAg = blatt.arbeitsgruppen || {};
  const arbeitsgruppen = (webseite.arbeitsgruppen || []).map((ag) => {
    const o = ueberAg[String(ag.nr)] || {};
    const sprachen = o.sprachen || ag.sprachen || [];
    const titel = ag.titel || {};
    const s1 = sprachen[0]; const s2 = sprachen[1];
    let titel_1 = o.titel_1 || (s1 && titel[s1]) || ag.titel_1 || '';
    let titel_2 = o.titel_2 || (s2 && titel[s2]) || '';
    const chinesisch = /^(CN|ZH|中文)$/i.test(s2 || '');
    const namen = o.namen !== undefined ? o.namen : (ag.mitwirkende || []).join('\n');
    if (sprachen.length > 1 && !titel_2) merken('uebersetzung', `AG ${ag.nr} (${sprachen.join(' · ')}): nur ein Titel auf der Webseite – Zweitsprache fehlt.`);
    if (!sprachen.length) merken('offen', `AG ${ag.nr}: keine Sprachangabe auf der Webseite.`);
    if (!ag.text_1?.length && !ag.text_2?.length) merken('offen', `AG ${ag.nr} «${titel_1}»: noch ohne Beschreibung auf der Webseite – vermutlich Platzhalter.`);
    return {
      nr: ag.nr, block: ag.block, sprachen,
      sprachen_label: sprachen.map((s) => SPRACHE_LABEL[s] || s),
      titel_1, titel_2, titel_2_stil: chinesisch ? 'chinesisch' : 'zweitsprache',
      namen, ort: ag.ort || '',
    };
  });
  const nVor = arbeitsgruppen.filter((a) => a.block === 'vormittag').length;
  const nNach = arbeitsgruppen.length - nVor;
  if (arbeitsgruppen.length > 55) merken('struktur', `${arbeitsgruppen.length} Arbeitsgruppen – 2026 fasste der Rahmen 55. Satz in InDesign prüfen.`);
  slots.arbeitsgruppen = arbeitsgruppenAbsaetze(arbeitsgruppen);

  return { tagung, tage, slots, arbeitsgruppen, zaehler: { vormittag: nVor, nachmittag: nNach }, hinweise };
}

/* Die Arbeitsgruppen als Absatzfolge für den 11-spaltigen Rahmen – mit den
   Absatzformaten der Vorlage (Namen in vorlage/slots.json › absatzformate_arbeitsgruppen). */
export function arbeitsgruppenAbsaetze(liste, formate) {
  const f = Object.assign({ kopf: 'AG_Header', sprache: 'AG_Sprache', titel_vormittag: 'AG-26', titel_nachmittag: 'AG-26 Afternoon',
    titel_zweitsprache: 'AG-26_grau', titel_chinesisch: 'AG-Chinese', namen: 'AG_Namen' }, formate || {});
  const aus = [];
  let block = null;
  for (const ag of liste) {
    if (ag.block !== block) {
      block = ag.block;
      aus.push(block === 'vormittag' ? { stil: f.kopf, laut: 'Morning ', ruhig: 'Vormittag' } : { stil: f.kopf, laut: 'Afternoon ', ruhig: 'Nachmittag' });
    }
    aus.push({ stil: f.sprache, text: [ag.nr, ...ag.sprachen_label].join(' · ') });
    aus.push({ stil: block === 'vormittag' ? f.titel_vormittag : f.titel_nachmittag, text: ag.titel_1 });
    if (ag.titel_2) aus.push({ stil: ag.titel_2_stil === 'chinesisch' ? f.titel_chinesisch : f.titel_zweitsprache, text: ag.titel_2 });
    aus.push({ stil: f.namen, text: ag.namen });
  }
  return aus;
}

/* Absatz → reiner Text (für Vorschau und Tests). */
export function absatzText(a) {
  if (typeof a === 'string') return a;
  if (a.runs) return a.runs.map((r) => r.text || '').join('');
  const teile = [];
  if (a.laut) teile.push(a.laut);
  if (a.ruhig) teile.push(a.ruhig);
  if (a.text) teile.push(a.text);
  return teile.join(a.laut && a.ruhig ? ' ' : '');
}

/* Tagesansicht für die Vorschau: je Tag die Zeilen des Rasters (blatt.tagesraster)
   mit den Absätzen des jeweiligen Slots. Mehrspaltige Slots werden am
   Spaltenumbruch geteilt: teil = Index der Spalte, «tag» = Spalte je Tag. */
export function tagesansicht(modell, blatt) {
  const spalten = (absaetze) => {
    const aus = [[]];
    for (const a of absaetze) {
      aus[aus.length - 1].push(a);
      if (a && a.umbruch === 'NextColumn') aus.push([]);
    }
    return aus;
  };
  return modell.tage.map((tag, ti) => {
    const zeilen = [];
    for (const z of (blatt.tagesraster?.zeilen || [])) {
      if (!z.tag.includes(ti)) continue;
      const absaetze = modell.slots[z.slot];
      if (absaetze === undefined) continue;
      let liste = Array.isArray(absaetze) ? absaetze : [absaetze];
      if (z.teil !== undefined) {
        const teile = spalten(liste);
        if (z.teil === 'tag') {
          // Rahmen mit Titel über allen Spalten: teile[0] = [Titel, Namen Spalte 1],
          // teile[1..] = Namen der weiteren Spalten. Titel je Tag wiederholen.
          const idx = z.tag.indexOf(ti);
          liste = idx === 0 ? teile[0] : [teile[0][0], ...(teile[idx] || [])];
        } else {
          liste = teile[z.teil] || [];
        }
      }
      zeilen.push({ zeit: z.zeit, slot: z.slot, absaetze: liste });
    }
    return { ...tag, zeilen };
  });
}
