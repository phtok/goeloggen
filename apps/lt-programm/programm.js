/* Tagungsprogramm · Komposition
   ---------------------------------------------------------------------------
   Aus webseite.json (was agriculture-conference.org sagt) und blatt.json (was
   nur auf dem Faltblatt steht) wird EIN Blattmodell gebaut. Die Vorschau
   (index.html) zeigt es, der Export (idml-export.js) schreibt es in die
   InDesign-Vorlage. Gleiche Quelle, gleiche Regeln – kein zweiter Weg.

   Blattmodell:
     { tagung, tage:[{en,de,datum_en,datum_de}], slots:{name:[Absatz…]},
       arbeitsgruppen:[…], hinweise:[{art,text}] }
   Absatz: "Text"  |  {laut, ruhig, text, stil, umbruch}  |  {runs:[{laut|ruhig, text}…]}
   laut = Schnitt Deutlich, ruhig = Schnitt Ruhig; \n = Zeilenumbruch im Absatz.
   ES-Modul ohne Abhängigkeiten – läuft im Browser und in Node.
   ------------------------------------------------------------------------- */

const WOCHENTAG_EN = { Montag: 'Monday', Dienstag: 'Tuesday', Mittwoch: 'Wednesday', Donnerstag: 'Thursday',
  Freitag: 'Friday', Samstag: 'Saturday', Sonntag: 'Sunday' };
const MONAT_EN = { Januar: 'January', Februar: 'February', 'März': 'March', April: 'April', Mai: 'May', Juni: 'June',
  Juli: 'July', August: 'August', September: 'September', Oktober: 'October', November: 'November', Dezember: 'December' };
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

const KURZ = ['Mi', 'Do', 'Fr', 'Sa'];

/* Text ohne Leerraum und Umbrüche – zum Vergleichen von Hand gesetzter
   Fassungen mit dem, was die Webseite sagt. */
const nackt = (s) => String(s || '').replace(/[\s\u2028\u2002]+/g, '').trim();
const zeitNorm = (z) => (z || '').replace('.', ':').replace(/^(\d):/, '0$1:');
const namenZeile = (liste) => (liste || []).join(' · ');

/* Titelzeile: Englisch laut, Deutsch ruhig. Beide auf einer Zeile (Geviert
   dazwischen), sobald sie kurz genug sind – sonst untereinander, wie es die
   schmalen Spalten des Blatts brauchen. Schwelle in blatt.json (`umbruch_ab`). */
function titelzeile(en, de, schwelle, eineZeile) {
  if (!en && !de) return { ruhig: '\u2039Titel folgt\u203a' };
  if (!en) return { ruhig: de };
  if (!de) return { laut: en };
  const zusammen = eineZeile === true || (eineZeile !== false && en.length + de.length <= schwelle);
  return zusammen ? { laut: en, ruhig: de } : { runs: [{ laut: true, text: `${en}\n` }, { ruhig: true, text: de }] };
}

export function komponieren(webseite, blatt) {
  const hinweise = [];
  const merken = (art, text) => hinweise.push({ art, text });
  const schwelle = blatt.umbruch_ab || 30;

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
    quelle: webseite.quelle || '',
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

  // Kopf des Blatts: Motto, Untertitel, Tagungszeile – drei Absätze, wie gesetzt.
  slots.kopf_en = [
    { laut: blatt.kopf.motto_en },
    { ruhig: blatt.kopf.untertitel_en },
    { laut: `${blatt.kopf.tagung_en}\n${datumEn}` },
  ];
  slots.kopf_de = [
    { ruhig: blatt.kopf.motto_de },
    { ruhig: blatt.kopf.untertitel_de },
    { laut: `${blatt.kopf.tagung_de}\n${datumDe}` },
  ];
  slots.stand = [
    { laut: `${blatt.stand.en}\nVisit our website for\nnews and registration` },
    { ruhig: `${blatt.stand.de}\nBesuchen Sie unsere Webseite\nfür Aktuelles und Anmeldung:` },
    { laut: 'www.agriculture-conference.org' },
  ];
  slots.einleitung = [{ laut: blatt.einleitung.en }, { laut: '' }, { ruhig: blatt.einleitung.de }];
  slots.sprachen_hinweis = blatt.sprachen_hinweis;

  // Bild auf dem Umschlag – eine Angabe, zwei Stellen (Plakat und Rückseite).
  const mal = blatt.malerei || {};
  slots.malerei = [
    { laut: 'Painting on Cover' },
    { ruhig: `Malerei auf dem Cover\n‹${mal.titel || 'Titel folgt'}›` },
    { ruhig: mal.name || 'Name folgt' },
  ];
  slots.plakat_malerei = [{ laut: `Painting: ${mal.name || 'Name folgt'}, ‹${mal.titel || 'Titel folgt'}›` }];
  if (!mal.name || !mal.titel) merken('offen', 'Bild auf dem Umschlag: Name oder Titel fehlt – in blatt.json › malerei eintragen (steht auf Plakat und Rückseite).');

  // ---- Plenum → Rahmen ---------------------------------------------------
  const plenum = webseite.plenum || [];
  const benutzt = new Set();
  const ueber = blatt.plenum || {};
  const eventsBei = (tag, zeit) => (plenum[tag]?.veranstaltungen || []).filter((v) => zeitNorm(v.zeit) === zeitNorm(zeit));

  /* Eine Überschreibung aus blatt.json gilt, solange sie inhaltlich noch zum
     Text der Webseite passt (sie trägt meist nur Zeilenumbrüche). Hat sich der
     Text geändert, gewinnt die Webseite – und der Umbruch ist neu zu setzen. */
  const gueltig = (hand, web, wo, feld) => {
    if (hand === undefined) return web;
    if (!web || nackt(hand) === nackt(web)) return hand;
    merken('abgleich', `${wo}: ${feld} in blatt.json («${nackt(hand).slice(0, 40)}…») passt nicht mehr zur Webseite – die Webseite gilt, der Umbruch ist neu zu setzen.`);
    return web;
  };

  const zeilenFuer = (v, key, wo) => {
    // `key` ist zugleich der Schlüssel in blatt.json › plenum.
    const o = ueber[key] || {};
    const en = gueltig(o.titel_en, v.titel_en || v.art_en || '', wo, 'titel_en');
    const de = gueltig(o.titel_de, v.titel_de || v.art_de || '', wo, 'titel_de');
    if (v.titel_offen && o.titel_de === undefined && o.titel_en === undefined) {
      merken('offen', `${wo}: Titel steht auf der Webseite noch als Platzhalter${v.art_de ? ` («${v.art_de}»)` : ''}.`);
    }
    if (en && !de) merken('uebersetzung', `${wo}: «${en}» hat keine deutsche Fassung auf der Webseite.`);
    if (de && !en) merken('uebersetzung', `${wo}: «${de}» hat keine englische Fassung auf der Webseite.`);
    if (v.namen_offen) merken('offen', `${wo}: bei den Mitwirkenden steht noch N.N.`);
    const namen = o.namen !== undefined ? o.namen : namenZeile(v.mitwirkende);
    const zeile = { ...titelzeile(en, de, schwelle, o.eine_zeile), offen: !!v.titel_offen, quelle: { schluessel: key, feld: 'titel' } };
    // Manche Rahmen sind knapp: dort hängen die Namen mit Mittelpunkt an den Titel.
    if (namen && o.namen_anhaengen) {
      if (zeile.runs) zeile.runs[zeile.runs.length - 1].text += ` · ${namen}`;
      else if (zeile.ruhig) zeile.ruhig += ` · ${namen}`;
      else zeile.ruhig = namen;
      return [zeile];
    }
    const aus = [zeile];
    if (namen) aus.push({ ruhig: namen, quelle: { schluessel: key, feld: 'namen' } });
    return aus;
  };

  for (const regel of PLENUM_SLOTS) {
    const absaetze = [];
    if (regel.art === 'morgen') {
      // Titel und Art laufen über alle Spalten, darunter die Mitwirkenden je Tag
      // in eigener Spalte. Was spannt und was nicht, sagt das Modell – sonst
      // erbt eine Namenszeile den Spaltenlauf der Überschrift und schiebt die
      // folgenden Tage aus dem Rahmen.
      const o = ueber[regel.slot] || {};
      const erste = eventsBei(regel.teile[0].tag, regel.teile[0].zeit)[0] || {};
      const en = gueltig(o.titel_en, erste.titel_en || erste.art_en || '', regel.slot, 'titel_en');
      const de = gueltig(o.titel_de, erste.titel_de || erste.art_de || '', regel.slot, 'titel_de');
      absaetze.push({ ...titelzeile(en, de, schwelle, o.eine_zeile), spanne: 'alle', quelle: { schluessel: regel.slot, feld: 'titel' } });
      // Die Art («Michaelbrief · Michael Letter») steht als eigene Zeile darunter,
      // wenn die Webseite sie neben dem Titel nennt.
      const artEn = o.art_en !== undefined ? o.art_en : (erste.art_en || '');
      const artDe = o.art_de !== undefined ? o.art_de : (erste.art_de || '');
      if ((artEn || artDe) && (en || de) && `${artEn}${artDe}` !== `${en}${de}`) {
        absaetze.push({ ...titelzeile(artEn, artDe, schwelle, o.art_eine_zeile !== false), spanne: 'alle' });
      }
      const titelGleich = new Set();
      regel.teile.forEach((teil, i) => {
        const evs = eventsBei(teil.tag, teil.zeit);
        evs.forEach((v) => { benutzt.add(v); titelGleich.add(`${v.titel_en}|${v.titel_de}`); });
        const namen = evs.map((v) => namenZeile(v.mitwirkende)).filter(Boolean).join('\n') || '–';
        if (evs.some((v) => v.titel_offen)) merken('offen', `${regel.slot} (${KURZ[teil.tag]}): Beitrag am Vormittag noch ohne Titel.`);
        if (evs.some((v) => v.namen_offen)) merken('offen', `${regel.slot} (${KURZ[teil.tag]}): Mitwirkende am Vormittag noch offen (N.N.).`);
        absaetze.push({ ruhig: namen, spanne: 'keine', umbruch: i < regel.teile.length - 1 ? 'NextColumn' : undefined });
      });
      if (titelGleich.size > 1) merken('struktur', 'Die drei Vormittage haben verschiedene Titel – der Rahmen im Blatt trägt nur einen. In blatt.json › plenum › morgen_0830 einen gemeinsamen Titel setzen.');
    } else {
      regel.teile.forEach((teil, i) => {
        const evs = eventsBei(teil.tag, teil.zeit);
        if (!evs.length) merken('struktur', `${regel.slot}: keine Veranstaltung ${KURZ[teil.tag]} ${teil.zeit} auf der Webseite.`);
        evs.forEach((v, n) => {
          benutzt.add(v);
          // Schlüssel in blatt.json: @2 = zweite Spalte des Rahmens,
          // #2 = zweite Veranstaltung in derselben Spalte.
          const key = `${regel.slot}${i ? `@${i + 1}` : ''}${n ? `#${n + 1}` : ''}`;
          absaetze.push(...zeilenFuer(v, key, `${KURZ[teil.tag]} ${teil.zeit}`));
        });
        if (i < regel.teile.length - 1 && absaetze.length) absaetze[absaetze.length - 1].umbruch = 'NextColumn';
      });
    }
    slots[regel.slot] = absaetze;
  }
  plenum.forEach((tag, ti) => (tag.veranstaltungen || []).forEach((v) => {
    if (!benutzt.has(v)) {
      merken('struktur', `Kein Rahmen im Blatt für ${KURZ[ti] || tag.wochentag} ${v.zeit} «${v.titel_de || v.titel_en || v.art_de}» – Rahmen in InDesign anlegen und in slots.json eintragen.`);
    }
  }));

  // ---- Arbeitsgruppen ----------------------------------------------------
  const ueberAg = blatt.arbeitsgruppen || {};
  const arbeitsgruppen = (webseite.arbeitsgruppen || []).map((ag) => {
    const o = ueberAg[String(ag.nr)] || {};
    const sprachen = o.sprachen || ag.sprachen || [];
    const titel = ag.titel || {};
    const s1 = sprachen[0]; const s2 = sprachen[1];
    const titel_1 = gueltig(o.titel_1, (s1 && titel[s1]) || ag.titel_1 || '', `AG ${ag.nr}`, 'titel_1');
    const titel_2 = gueltig(o.titel_2, (s2 && titel[s2]) || '', `AG ${ag.nr}`, 'titel_2');
    const chinesisch = /^(CN|ZH|中文)$/i.test(s2 || '');
    const namen = gueltig(o.namen, (ag.mitwirkende || []).join('\n'), `AG ${ag.nr}`, 'namen');
    if (sprachen.length > 1 && !titel_2) merken('uebersetzung', `AG ${ag.nr} (${sprachen.join(' · ')}): nur ein Titel auf der Webseite – Zweitsprache fehlt.`);
    if (!sprachen.length) merken('offen', `AG ${ag.nr}: keine Sprachangabe auf der Webseite.`);
    if (!ag.text_1?.length && !ag.text_2?.length) merken('offen', `AG ${ag.nr} «${titel_1}»: noch ohne Beschreibung auf der Webseite – vermutlich Platzhalter.`);
    return {
      nr: ag.nr, block: ag.block, sprachen,
      sprachen_label: sprachen.map((s) => SPRACHE_LABEL[s] || s),
      titel_1, titel_2, titel_2_stil: chinesisch ? 'chinesisch' : 'zweitsprache',
      namen, ort: ag.ort || '', hand: Object.keys(o).length > 0,
    };
  });
  const nVor = arbeitsgruppen.filter((a) => a.block === 'vormittag').length;
  slots.arbeitsgruppen = arbeitsgruppenAbsaetze(arbeitsgruppen, blatt.ag_formate);

  return {
    tagung, tage, slots, arbeitsgruppen,
    zaehler: { vormittag: nVor, nachmittag: arbeitsgruppen.length - nVor, plenum: plenum.reduce((n, t2) => n + t2.veranstaltungen.length, 0) },
    hinweise,
  };
}

/* Die Arbeitsgruppen als Absatzfolge für den elfspaltigen Rahmen – mit den
   Absatzformaten der Vorlage. */
export function arbeitsgruppenAbsaetze(liste, formate) {
  const f = Object.assign({ kopf: 'AG_Header', sprache: 'AG_Sprache', titel_vormittag: 'AG-26', titel_nachmittag: 'AG-26 Afternoon',
    titel_zweitsprache: 'AG-26_grau', titel_chinesisch: 'AG-Chinese', namen: 'AG_Namen' }, formate || {});
  const aus = [];
  let block = null;
  let ersteImBlock = false;
  for (const ag of liste) {
    if (ag.block !== block) {
      const nachmittag = ag.block === 'nachmittag';
      block = ag.block;
      ersteImBlock = true;
      aus.push({
        stil: f.kopf,
        runs: [{ laut: true, text: nachmittag ? 'Afternoon\n' : 'Morning\n' }, { ruhig: true, text: nachmittag ? 'Nachmittag' : 'Vormittag' }],
        // Der Nachmittag beginnt in einer frischen Spalte.
        umbruch_vor: nachmittag ? 'NextColumn' : undefined,
      });
    }
    // Nach der Blocküberschrift ein leerer Absatz als Luft, dann die erste Nummer.
    if (ersteImBlock) aus.push({ stil: f.sprache, text: '' });
    aus.push({ stil: f.sprache, text: [ag.nr, ...ag.sprachen_label].join(' · ') });
    ersteImBlock = false;
    aus.push({ stil: block === 'vormittag' ? f.titel_vormittag : f.titel_nachmittag, text: ag.titel_1 });
    if (ag.titel_2) aus.push({ stil: ag.titel_2_stil === 'chinesisch' ? f.titel_chinesisch : f.titel_zweitsprache, text: ag.titel_2 });
    aus.push({ stil: f.namen, text: ag.namen });
  }
  return aus;
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
          // teile[1…] = Namen der weiteren Spalten. Titel je Tag wiederholen.
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

/* Absatz → reiner Text (für Vorschau, Abgleich und Tests). */
export function absatzText(a) {
  if (typeof a === 'string') return a;
  if (a.runs) return a.runs.map((r) => r.text || '').join('');
  const teile = [];
  if (a.laut) teile.push(a.laut);
  if (a.ruhig) teile.push(a.ruhig);
  if (a.text) teile.push(a.text);
  return teile.join(a.laut && a.ruhig ? '\u2002' : '');
}

/* Abgleich der von Hand gesetzten Rahmen (slots.json › nur_pruefen): stimmt
   das, was in der Vorlage steht, noch mit den Daten überein? Verglichen wird
   ohne Rücksicht auf Zeilenumbrüche und Leerraum. */
export function abgleichen(modell, slots) {
  const nackt = (s) => String(s || '').replace(/[\s\u2028\u2002\u2009]+/g, ' ').replace(/[–—]/g, '-').trim().toLowerCase();
  const soll = {
    motto: `${modell.tagung.motto_en} ${modell.tagung.motto_de}`,
    datum: `${modell.tagung.datum_en} ${modell.tagung.datum_de}`,
  };
  const aus = [];
  for (const [name, slot] of Object.entries(slots.slots || {})) {
    if (!slot.nur_pruefen) continue;
    const ist = slot.vorlage || '';
    const woerter = nackt(soll[slot.feld] || '').split(' ').filter((w) => w.length > 3);
    const fehlt = woerter.filter((w) => !nackt(ist).includes(w));
    aus.push({ slot: name, ist, soll: soll[slot.feld] || '', stimmt: fehlt.length === 0, fehlt });
  }
  return aus;
}
