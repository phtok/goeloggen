"use strict";

/* Campusplan — was Auswahl (index.html) und Telefon (plan.html) teilen:
   Texte, Zustand, Orte, Öffnungs-Ausnahmen, Link-Kodierung, Abhaken.
   Der Plan ist die URL (#p=…), Abhaken lebt im localStorage des Geräts.
   Katalog und Karte kommen aus dem Kartentool (apps/karten-generator/). */

const AUSNAHMEN_URL = "https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/campusplan-ausnahmen";
const SPEICHER_PRAEFIX = "campusplan:";
const PLAN_SEITE = "plan.html";

/* ---------- Texte ---------- */

const UI = {
  "s3-titel": { de: "Dein Plan", en: "Your plan" },
  "s1-frage": { de: "Was zieht dich an?", en: "What draws you in?" },
  "s1-hilfe": { de: "Eines oder mehrere wählen. Der Plan füllt sich daraus von selbst.",
                en: "Pick one or more. The plan fills itself from your choice." },
  "s2-frage": { de: "Wie viel Zeit hast du?", en: "How much time do you have?" },
  "s2-hilfe": { de: "Die Zeit entscheidet, wie viele Orte auf den Plan kommen.",
                en: "Time decides how many places make the plan." },
  link: { de: "Link kopieren", en: "Copy link" },
  qr: { de: "QR-Code", en: "QR code" },
  "link-lab": { de: "Dein Link, zum Weitergeben oder aufs Telefon", en: "Your link, to share or to open on your phone" },
  "plan-aendern": { de: "Plan ändern", en: "Change plan" },
  "plan-hint": { de: "Abgehakt wird nur auf diesem Gerät gespeichert. Der Link bleibt gleich.",
                 en: "Ticks are stored on this device only. The link stays the same." },
  titel: { de: "Mein Campusplan", en: "My Campus Plan" },
  lede: { de: "Interessen und Zeit wählen – der Plan kommt als A4-Blatt zum Ausdrucken und als Link fürs Telefon.",
          en: "Pick your interests and your time – the plan comes as an A4 sheet to print and as a link for your phone." },
  besuch: { de: "Mein Besuch", en: "My visit" },
  stationen: { de: "Stationen", en: "stops" },
  etwa: { de: "etwa", en: "about" },
  besucht: { de: "besucht", en: "visited" },
  von: { de: "von", en: "of" },
  dabei: { de: "dabei", en: "included" },
  "mehr-orte": { de: "Mehr Orte", en: "More places" },
  "karte-knopf": { de: "Karte", en: "Map" },
  "s1-leer": { de: "Ohne Thema zeigt der Plan nur Eingang, Empfang und Anreise.",
               en: "Without a theme the plan shows only entrance, reception and arrival." },
  kopiert: { de: "Kopiert.", en: "Copied." },
  "kopieren-hand": { de: "Link markieren und von Hand kopieren.", en: "Select the link and copy it by hand." },
  anreise: { de: "Anreise und Service", en: "Arrival and service" },
  min: { de: "Min.", en: "min" },
  std: { de: "Std.", en: "h" },
  "wc": { de: "Toiletten", en: "Toilets" },
  pdf: { de: "PDF herunterladen", en: "Download PDF" },
  "pdf-laeuft": { de: "PDF wird erzeugt …", en: "Creating PDF …" },
  "pdf-fehler": { de: "PDF konnte nicht erzeugt werden.", en: "The PDF could not be created." },
  "stationen-titel": { de: "Die Stationen", en: "The stops" },
  "pdf-link-hint": { de: "Derselbe Plan auf dem Telefon: Link öffnen oder QR-Code scannen, unterwegs abhaken.",
                     en: "The same plan on your phone: open the link or scan the QR code, tick off as you go." },
  "datum-lab": { de: "Besuchstag, wenn du ihn schon kennst", en: "Day of your visit, if you know it" },
  "geschlossen-am": { de: "am Besuchstag geschlossen", en: "closed on your visit day" },
  "heute-zu": { de: "heute geschlossen", en: "closed today" },
  ausnahmen: { de: "aktuelle Ausnahmen", en: "current exceptions" },
  "an-diesem-tag": { de: "an diesem Tag", en: "on this day" },
  "orte-zu": { de: "Orte sind an diesem Tag zu und nicht im Plan", en: "places are closed that day and left out" },
  "ort-zu": { de: "Ort ist an diesem Tag zu und nicht im Plan", en: "place is closed that day and left out" },
  "fuehrung-hint": { de: "Mit einer Führung ist alles zugänglich, auch die Häuser der Architektursammlung.", en: "With a guided tour everything is accessible, including the houses of the architecture collection." },
  "fuehrung-link": { de: "Führungen buchen", en: "Book a guided tour" },
  "nummer-hint": { de: "Ein Tipp auf eine Nummer in der Liste zeigt den Ort auf der Karte – und umgekehrt.",
                   en: "Tap a number in the list to see the place on the map – and the other way round." },
  "pause-bis": { de: "Pause bis", en: "Break until" },
  "ausserhalb": { de: "passt an diesem Tag nicht in die Öffnungszeiten", en: "does not fit the opening hours that day" },
  "ankunft-lab": { de: "Ankunft", en: "Arrival" },
  "ankunft-hint": { de: "Mit Besuchstag schlägt der Plan einen Zeitplan vor, nach den aktuellen Öffnungszeiten.",
                    en: "With a visit day the plan suggests a schedule, based on the current opening hours." },
  mitnehmen: { de: "Mitnehmen", en: "Take it along" },
  "a4-titel": { de: "A4 zum Ausdrucken", en: "A4 to print" },
  "a4-hint": { de: "Die Campus-Karte mit deinen Stationen, dazu ein Blatt mit allen Orten und dem Link.",
               en: "The campus map with your stops, plus a sheet with every place and the link." },
  "telefon-titel": { de: "Aufs Telefon", en: "On your phone" },
  "telefon-hint": { de: "QR-Code scannen oder den Link schicken – unterwegs Karte und Stationen zum Abhaken.",
                    en: "Scan the QR code or send the link – map and stops to tick off as you go." },
  "plan-oeffnen": { de: "Ansehen", en: "View" },
  zeitplan: { de: "Zeitplan", en: "Schedule" },
  "nicht-bestaetigt": { de: "Zeiten heute nicht bestätigt", en: "hours not confirmed today" },
  pruefen: { de: "vor dem Besuch prüfen", en: "check before you go" },
  "zeiten-live": { de: "Öffnungszeiten heute von den Websites der Orte gelesen.", en: "Opening hours read today from the places’ own websites." },
  "zeiten-offen-1": { de: "Ort: Öffnungszeiten heute nicht bestätigt – bitte vor dem Besuch prüfen.", en: "place: opening hours not confirmed today – please check before you go." },
  "zeiten-offen": { de: "Orte: Öffnungszeiten heute nicht bestätigt – bitte vor dem Besuch prüfen.", en: "places: opening hours not confirmed today – please check before you go." },
  ausstellung: { de: "Ausstellung", en: "Exhibition" },
  bis: { de: "bis", en: "until" },
  "ausstellung-wechselnd": { de: "Wechselnde Ausstellungen der Sektion für Bildende Künste.", en: "Changing exhibitions of the Section for Visual Arts." },
  "karte-laedt": { de: "Karte wird geladen …", en: "Loading map …" },
  "karte-fehlt": { de: "Die Karte konnte nicht geladen werden. Die Liste gilt trotzdem.", en: "The map could not be loaded. The list still works." },
  "plan-leer": { de: "Dieser Link enthält keinen Plan.", en: "This link holds no plan." },
  "plan-erstellen": { de: "Eigenen Plan zusammenstellen", en: "Put together your own plan" }
};

/* ---------- Zustand ---------- */

const state = {
  sprache: "de",
  modus: "erstellen",         // ‹erstellen› (Auswahl) | ‹plan› (Telefon)
  schritt: 1,
  themen: new Set(),
  umstaende: { kinder: false, barrierefrei: false },
  zeit: "halb",
  an: new Set(),              // Ort-IDs im Plan
  besucht: new Set(),         // Ort-IDs abgehakt (nur Telefon)
  code: "",                   // Plan-Code aus dem Link
  datum: "",                  // Besuchstag ISO (optional)
  ankunft: "10:00",           // Ankunftszeit für den Zeitplan
  ausnahmen: null,            // Antwort der Edge Function (zeiten, saal, glashaus, ausstellungen) oder null
  zeitenStand: "laedt",       // ‹laedt› | ‹live› (Antwort da) | ‹fehler› (Function nicht erreichbar)
  fokus: null
};

/* ---------- Orte ---------- */

const ORTE_ALLE = ORTE.concat(NEUE_ORTE);
const ORT_NACH_ID = {};
ORTE_ALLE.forEach((o) => { ORT_NACH_ID[o.id] = o; });
const GAST_NACH_ID = {};
GAESTE.forEach((g) => { GAST_NACH_ID[g.id] = g; });

// Text von fremden Websites (Ausstellungen, Tagesausnahmen) kommt nur maskiert ins HTML.
function esc(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function t(wert) {
  if (wert && typeof wert === "object") return wert[state.sprache] || wert.de;
  return wert;
}
function ui(schluessel) { return t(UI[schluessel]) || schluessel; }
function ort(id) { return ORT_NACH_ID[id]; }
function gast(id) { return GAST_NACH_ID[id]; }
function ortName(id) {
  const o = ort(id);
  if (!o) return id;
  if (id === "wc-goetheanum") return ui("wc");
  const g = gast(id);
  if (g && g.name) return t(g.name);
  if (o.teile) return t(o.teile[0]);
  return t(o.label);
}
function ortPosition(id) {
  const o = ort(id);
  if (o.positionen && o.positionen.length) return o.positionen[0];
  if (o.badges && o.badges.length) return [o.badges[0].x, o.badges[0].y];
  return [KARTE.blatt.breite / 2, KARTE.blatt.hoehe / 2];
}
function ortGebaeude(id) {
  const g = gast(id), o = ort(id);
  if (g && g.gebaeude) return g.gebaeude;
  if (o && o.gebaeudeTeile) return o.gebaeudeTeile;
  if (o && o.gebaeude) return [o.gebaeude];
  return [];
}
function ortMarker(id) {
  const o = ort(id);
  return o && o.marker && /^[A-Z]{1,2}$/.test(o.marker) ? o.marker : "";
}

function stationen() {
  // Nummerierte Stationen in Gehreihenfolge; Anreise separat, ohne Nummer.
  // Gibt es einen Zeitplan (Besuchstag bekannt), zählen die Nummern in
  // seiner Reihenfolge — Karte, Liste und Uhrzeiten laufen dann gleich;
  // was an dem Tag nicht in die Öffnungszeiten passt, folgt am Ende.
  // Grabsteine (thema ‹aus›) und unbekannte IDs aus alten Links fallen still weg.
  const liste = [...state.an].map((id) => gast(id)).filter((g) => g && g.thema !== "aus" && ort(g.id));
  let nummeriert = liste.filter((g) => g.thema !== "anreise").sort((a, b) => a.gehfolge - b.gehfolge);
  const anreise = liste.filter((g) => g.thema === "anreise");
  const plan = zeitplan(nummeriert);
  if (plan) {
    const rang = {};
    plan.eintraege.forEach((e, i) => { if (e.id) rang[e.id] = i; });
    nummeriert = nummeriert.map((g, i) => ({ g, i }))
      .sort((a, b) => (rang[a.g.id] ?? 1e3 + a.i) - (rang[b.g.id] ?? 1e3 + b.i)).map(({ g }) => g);
  }
  return { nummeriert, anreise, plan };
}

/* ---------- Tage und Öffnungs-Ausnahmen ---------- */

function heuteIso() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// Der Tag, für den der Plan gilt: der Besuchstag, am Telefon ohne Datum der heutige.
function planTag() {
  return state.datum || (state.modus === "plan" ? heuteIso() : "");
}

async function ausnahmenLaden(danach) {
  try {
    const r = await fetch(AUSNAHMEN_URL);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    state.ausnahmen = await r.json();
    state.zeitenStand = "live";
  } catch (fehler) {
    state.ausnahmen = null;   // ohne Live-Daten: Rückfallwerte, offen als «nicht bestätigt»
    state.zeitenStand = "fehler";
  }
  if (danach) danach();
}

// Tagesaktuelle Ausnahme eines Orts (Grosser Saal, Glashaus) für einen Tag.
function ausnahmeAm(g, iso) {
  if (!g.live || !iso || !state.ausnahmen) return null;
  const liste = state.ausnahmen[g.live] || [];
  return liste.find((e) => e.datum === iso) || null;
}

// Zu ist ein Ort, den man betritt, wenn er an dem Tag kein Zeitfenster hat
// (oder die Tagesausnahme ihn schliesst). Was man von aussen sieht, ist nie zu.
function ortGeschlossenAm(g, iso) {
  if (!iso) return false;
  const a = ausnahmeAm(g, iso);
  if (a && a.zu) return true;
  if (g.zugang === "aussen") return false;
  const f = fensterAm(g, iso);
  return Boolean(f && !f.length);
}

/* ---------- Öffnungszeiten: live von goetheanum.ch, sonst Rückfall ---------- */

// Der Block der Öffnungszeiten-Seite zu einem Teil: gleicher Titel, sonst
// Titel enthält die Quelle (Ausstellungstitel), sonst Kontext (Ortszeile davor).
function liveBlock(teil) {
  const seite = teil.seite || "zeiten";
  const liste = state.ausnahmen && Array.isArray(state.ausnahmen.zeiten)
    ? state.ausnahmen.zeiten.filter((b) => (b.seite || "zeiten") === seite) : [];
  if (!teil.quelle || !liste.length) return null;
  return liste.find((b) => b.titel === teil.quelle)
    || liste.find((b) => b.titel.includes(teil.quelle))
    || liste.find((b) => (b.kontext || []).includes(teil.quelle)) || null;
}

function teilZeiten(teil) {
  const live = liveBlock(teil);
  if (live && live.fenster.length) {
    return { fenster: live.fenster, ersterImMonat: Boolean(live.ersterImMonat), zuMonate: live.zuMonate || [],
      zuZeitraeume: live.zuZeitraeume || [], live: true };
  }
  return { fenster: teil.fenster || [], ersterImMonat: Boolean(teil.ersterImMonat), zuMonate: teil.zuMonate || [],
    zuZeitraeume: [], live: false };
}

// Sind die Zeiten eines Orts heute live von der Website bestätigt? null =
// der Ort hat keine Zeiten (draussen, auf Anfrage) oder die Antwort steht noch aus.
function zeitenBestaetigt(g) {
  if (!g.oeffnung || state.zeitenStand === "laedt") return null;
  return g.oeffnung.every((teil) => !teil.quelle || teilZeiten(teil).live);
}

// Website, auf der ein Ort seine Zeiten pflegt (für «vor dem Besuch prüfen»).
function zeitenSeite(g) {
  const teil = g.oeffnung && g.oeffnung.find((x) => x.quelle) || {};
  return ZEITEN_SEITEN[teil.seite || "zeiten"];
}

// Laufende Ausstellung der Galerie am Plantag (sonst heute): der Teil, der
// an dem Tag läuft, sonst die Ausstellung selbst.
function ausstellungAm(iso) {
  const liste = state.ausnahmen && Array.isArray(state.ausnahmen.ausstellungen) ? state.ausnahmen.ausstellungen : [];
  const tag = iso || heuteIso();
  const a = liste.find((x) => x.von <= tag && x.bis >= tag);
  if (!a) return null;
  const teil = (a.teile || []).find((x) => x.von <= tag && x.bis >= tag);
  return { titel: teil ? teil.titel : a.titel, reihe: teil ? a.titel : a.untertitel, bis: teil ? teil.bis : a.bis, link: a.link };
}

function kurzDatum(iso) {
  const [j, m, tag] = iso.split("-").map(Number);
  return new Date(j, m - 1, tag).toLocaleDateString(state.sprache === "en" ? "en-GB" : "de-CH", { day: "numeric", month: "long" });
}

// Die Zeile unter dem Namen: bei der Galerie die laufende Ausstellung, sonst der Einzeiler.
function einzeilerText(g) {
  if (g.ausstellung) {
    const a = ausstellungAm(planTag());
    if (a) return `${ui("ausstellung")}: ${a.titel}${a.reihe ? ` (${a.reihe})` : ""}, ${ui("bis")} ${kurzDatum(a.bis)}`;
    return state.zeitenStand === "laedt" ? "" : ui("ausstellung-wechselnd");
  }
  return g.einzeiler ? t(g.einzeiler) : "";
}

function minuten(hhmm) {
  const [h, m] = String(hhmm).split(/[:.]/).map(Number);
  return h * 60 + (m || 0);
}

// Uhrzeit: volle Stunde ohne Minuten («10», G22), sonst «13.30»; englisch «10:00».
function uhrText(min) {
  const h = Math.floor(min / 60), m = min % 60;
  if (state.sprache === "en") return `${h}:${String(m).padStart(2, "0")}`;
  return m ? `${h}.${String(m).padStart(2, "0")}` : String(h);
}

// Einheit nach schmalem geschütztem Leerzeichen (U+202F, G20): «10 Uhr», «20 Min.».
function einheit(zahl, wort) {
  return wort ? `${zahl}\u202f${wort}` : String(zahl);
}

// «13.30 Uhr» (englisch ohne Einheit).
function uhrZeit(min) {
  return einheit(uhrText(min), state.sprache === "en" ? "" : "Uhr");
}

// Zeitfenster des massgeblichen Teils an einem Tag, in Minuten:
// null = keine Angabe (immer zugänglich), [] = an dem Tag zu.
// Eine Tagesausnahme (Grosser Saal «14.00–14.20») ersetzt das Fenster.
function fensterAm(g, iso) {
  if (!g.oeffnung || !g.oeffnung.length || !iso) return null;
  const a = ausnahmeAm(g, iso);
  if (a && a.zu) return [];
  if (a && a.zeit) {
    const m = a.zeit.match(/(\d{1,2})[.:](\d{2})\s*[–-]\s*(\d{1,2})[.:](\d{2})/);
    if (m) return [{ von: minuten(`${m[1]}:${m[2]}`), bis: minuten(`${m[3]}:${m[4]}`) }];
  }
  const z = teilZeiten(g.oeffnung[0]);
  const [j, mo, tag] = iso.split("-").map(Number);
  const wochentag = new Date(j, mo - 1, tag).getDay();
  if (z.zuMonate.includes(mo)) return [];
  if (z.zuZeitraeume.some((r) => r.von <= iso && r.bis >= iso)) return [];
  if (z.ersterImMonat && tag > 7) return [];
  return z.fenster.filter((f) => f.tage.includes(wochentag))
    .map((f) => ({ von: minuten(f.von), bis: minuten(f.bis) })).sort((x, y) => x.von - y.von);
}

const TAG_KURZ = { de: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"], en: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] };
const MONAT_NAME = {
  de: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
  en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
};

// Tage als Text: alle sieben = täglich, Läufe ab drei Tagen mit Bis-Strich
// (Mo–Do, Di–So über den Sonntag), sonst aufgezählt.
function tageText(tage) {
  const sp = state.sprache === "en" ? "en" : "de";
  if (tage.length === 7) return sp === "en" ? "daily" : "täglich";
  const folge = [1, 2, 3, 4, 5, 6, 0].filter((d) => tage.includes(d));
  const laeufe = [];
  folge.forEach((d, i) => {
    const vorher = folge[i - 1];
    if (i && (vorher + 1) % 7 === d) laeufe[laeufe.length - 1].push(d); else laeufe.push([d]);
  });
  const und = sp === "en" ? " and " : " und ";
  const teile = laeufe.flatMap((l) => (l.length >= 3 ? [`${TAG_KURZ[sp][l[0]]}\u2060–\u2060${TAG_KURZ[sp][l[l.length - 1]]}`] : l.map((d) => TAG_KURZ[sp][d])));
  return teile.length === 2 ? teile.join(und) : teile.join(", ");
}

// Öffnungszeiten eines Orts als Text, aus den (live gelesenen) Fenstern.
function zeitenText(g) {
  if (!g.oeffnung) return "";
  const sp = state.sprache === "en" ? "en" : "de";
  const und = sp === "en" ? " and " : " und ";
  const uhr = sp === "en" ? "" : "\u202fUhr";
  const text = g.oeffnung.map((teil) => {
    const z = teilZeiten(teil);
    const gruppen = [];
    z.fenster.forEach((f) => {
      const schluessel = [...f.tage].sort().join(",");
      const gr = gruppen.find((x) => x.schluessel === schluessel);
      // Wortverbinder (U+2060) um den Bis-Strich: die Spanne bricht nicht um.
      const spanne = `${uhrText(minuten(f.von))}\u2060–\u2060${uhrText(minuten(f.bis))}`;
      if (gr) gr.spannen.push(spanne); else gruppen.push({ schluessel, tage: f.tage, spannen: [spanne] });
    });
    let tageTeil = gruppen.map((gr) => `${z.ersterImMonat ? (sp === "en" ? "first Friday of the month" : "jeden ersten Freitag im Monat") : tageText(gr.tage)} ${gr.spannen.join(und)}`).join(", ");
    if (tageTeil) tageTeil += uhr;
    if (z.zuMonate.length) {
      const namen = z.zuMonate.map((m) => MONAT_NAME[sp][m - 1]);
      tageTeil += `, ${namen.join(und)} ${sp === "en" ? "closed" : "geschlossen"}`;
    }
    return [teil.vor ? t(teil.vor) : "", tageTeil].filter(Boolean).join(" ");
  }).join(", ");
  return g.hinweis ? `${text}; ${t(g.hinweis)}` : text;
}

/* ---------- Zeitplan ---------- */

// Vorschlag für den Tag: ab der Ankunft durch die Stationen, mit WEGZEIT
// dazwischen. Dran ist, was jetzt offen ist, in Gehfolge — aber nur, wenn
// danach das Fenster, das als nächstes schliesst, noch erreichbar bleibt;
// sonst geht dieses vor. Ist nichts offen, wird gewartet (Pause bis zur
// nächsten Öffnung). Was an dem Tag nicht passt, steht in ‹ausserhalb›.
// Ohne Besuchstag kein Zeitplan.
function zeitplan(liste) {
  const iso = planTag();
  if (!iso || !liste.length) return null;
  let jetzt = minuten(state.ankunft || "10:00");
  if (state.modus === "plan" && !state.datum) {
    // Am Telefon ohne Besuchstag gilt heute — und frühestens jetzt.
    const d = new Date();
    jetzt = Math.max(jetzt, Math.ceil((d.getHours() * 60 + d.getMinutes()) / 5) * 5);
  }
  const offen = liste.map((g) => ({ g, fenster: g.zugang === "aussen" ? null : fensterAm(g, iso) }));
  const eintraege = [];
  const ausserhalb = [];
  // Frühester Beginn ab t in einem Fenster, mit Dauer (bei kurzem Fenster
  // dessen Länge); null = heute nicht mehr.
  const beginn = (o, t) => {
    if (!o.fenster) return { von: t, dauer: o.g.dauer };
    for (const f of o.fenster) {
      const dauer = Math.min(o.g.dauer, f.bis - f.von);
      const von = Math.max(t, f.von);
      if (von + dauer <= f.bis) return { von, dauer, schluss: f.bis - dauer };
    }
    return null;
  };
  let rest = offen.slice();
  while (rest.length) {
    rest = rest.filter((o) => { if (beginn(o, jetzt)) return true; ausserhalb.push(o.g.id); return false; });
    if (!rest.length) break;
    const mit = rest.map((o) => ({ o, b: beginn(o, jetzt) }));
    const gebunden = mit.filter((x) => x.b.schluss != null).sort((x, y) => x.b.schluss - y.b.schluss);
    const offenJetzt = mit.filter((x) => x.b.von === jetzt);
    const passt = (x) => {
      const ende = jetzt + x.b.dauer + (x.o.g.dauer ? WEGZEIT : 0);
      const knapp = gebunden.find((y) => y.o !== x.o);
      return !knapp || ende <= knapp.b.schluss;
    };
    const wahl = offenJetzt.find(passt)
      || (offenJetzt.length ? gebunden[0] || offenJetzt[0]
        : mit.slice().sort((x, y) => x.b.von - y.b.von)[0]);
    if (wahl.b.von > jetzt) eintraege.push({ pause: true, von: jetzt, bis: wahl.b.von });
    eintraege.push({ id: wahl.o.g.id, von: wahl.b.von, bis: wahl.b.von + wahl.b.dauer });
    jetzt = wahl.b.von + wahl.b.dauer + (wahl.o.g.dauer ? WEGZEIT : 0);
    rest = rest.filter((o) => o !== wahl.o);
  }
  return { eintraege, ausserhalb, ende: eintraege.length ? eintraege[eintraege.length - 1].bis : jetzt };
}

// «13.30–14 Uhr» für einen Eintrag des Zeitplans.
function spanneText(e) {
  const spanne = e.bis > e.von ? `${uhrText(e.von)}\u2060–\u2060${uhrText(e.bis)}` : uhrText(e.von);
  return einheit(spanne, state.sprache === "en" ? "" : "Uhr");
}

function zeitplanVon(plan, id) {
  return plan ? plan.eintraege.find((e) => e.id === id) || null : null;
}

function datumText(iso) {
  if (!iso) return "";
  const [j, m, tag] = iso.split("-").map(Number);
  return new Date(j, m - 1, tag).toLocaleDateString(state.sprache === "en" ? "en-GB" : "de-CH",
    { weekday: "long", day: "numeric", month: "long" });
}

function planMinuten() {
  let summe = 0;
  state.an.forEach((id) => { const g = gast(id); if (g && g.thema !== "anreise" && g.thema !== "aus") summe += g.dauer + WEGZEIT; });
  return summe;
}

function dauerText(minuten) {
  if (minuten < 60) return einheit(minuten, ui("min"));
  const h = Math.floor(minuten / 60), m = minuten % 60;
  return m ? `${einheit(h, ui("std"))} ${einheit(m, ui("min"))}` : einheit(h, ui("std"));
}

/* ---------- Link: der Plan ist die URL ---------- */

function kodieren() {
  const bytes = new Uint8Array(Math.ceil(GAESTE.length / 8));
  GAESTE.forEach((g, i) => { if (state.an.has(g.id)) bytes[i >> 3] |= 128 >> (i & 7); });
  let bin = "";
  bytes.forEach((b) => { bin += String.fromCharCode(b); });
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function dekodieren(code) {
  const an = new Set();
  try {
    const bin = atob(code.replace(/-/g, "+").replace(/_/g, "/"));
    GAESTE.forEach((g, i) => {
      const b = bin.charCodeAt(i >> 3) || 0;
      if (b & (128 >> (i & 7))) an.add(g.id);
    });
  } catch (fehler) { /* kaputter Code → leerer Plan */ }
  return an;
}

function planHash() {
  const teile = [`p=${kodieren()}`, `s=${state.sprache}`, `z=${state.zeit}`];
  if (state.umstaende.kinder) teile.push("k=1");
  if (state.umstaende.barrierefrei) teile.push("b=1");
  if (state.datum) teile.push(`d=${state.datum}`);
  if (state.ankunft && state.ankunft !== "10:00") teile.push(`a=${state.ankunft.replace(":", "")}`);
  return `#${teile.join("&")}`;
}

// Der Link führt immer auf die Telefonansicht (plan.html), gleich von welcher Seite.
function planLink() {
  return new URL(PLAN_SEITE, window.location.href.split("#")[0]).href + planHash();
}

function hashLesen() {
  const roh = window.location.hash.replace(/^#/, "");
  const werte = {};
  roh.split("&").forEach((paar) => {
    const [k, v] = paar.split("=");
    if (k) werte[decodeURIComponent(k)] = decodeURIComponent(v || "");
  });
  return werte;
}

// Sprache, Zeit, Umstände und Besuchstag aus dem Hash in den Zustand.
function hashAnwenden(h) {
  if (h.s === "en") state.sprache = "en";
  if (h.z && ZEITEN.some((z) => z.id === h.z)) state.zeit = h.z;
  state.umstaende.kinder = h.k === "1";
  state.umstaende.barrierefrei = h.b === "1";
  if (/^\d{4}-\d{2}-\d{2}$/.test(h.d || "")) state.datum = h.d;
  if (/^\d{4}$/.test(h.a || "")) state.ankunft = `${h.a.slice(0, 2)}:${h.a.slice(2)}`;
}

/* ---------- Abhaken (nur dieses Gerät) ---------- */

function besuchtLaden() {
  state.besucht = new Set();
  if (!state.code) return;
  try {
    const roh = localStorage.getItem(SPEICHER_PRAEFIX + state.code);
    if (roh) JSON.parse(roh).forEach((id) => state.besucht.add(id));
  } catch (fehler) { /* privater Modus: dann eben ohne Gedächtnis */ }
}

function besuchtSpeichern() {
  if (!state.code) return;
  try { localStorage.setItem(SPEICHER_PRAEFIX + state.code, JSON.stringify([...state.besucht])); }
  catch (fehler) { /* egal */ }
}

/* ---------- Zeile eines Orts: Zugang, Dauer, Zeiten, Tageslage ---------- */

function metaMarkup(g) {
  const zugang = g.zugang ? t(ZUGANG[g.zugang]) : "";
  const tag = planTag();
  const zu = ortGeschlossenAm(g, tag);
  const live = ausnahmeAm(g, tag);
  const zuText = state.modus === "plan" && !state.datum ? ui("heute-zu") : ui("geschlossen-am");
  return [zugang, g.dauer ? dauerText(g.dauer) : "", zeitenText(g)].filter(Boolean).join(" · ")
    + (zu ? ` · <span class="stn-zu">${zuText}</span>` : "")
    + (live && !live.zu ? ` · <span class="stn-live">${ui("an-diesem-tag")} ${esc(live.text)}</span>` : "")
    + (g.ausnahmen && !state.ausnahmen ? ` · <a href="${g.ausnahmen}" target="_blank" rel="noopener">${ui("ausnahmen")}</a>` : "")
    + (zeitenBestaetigt(g) === false
      ? ` · <span class="stn-zu">${ui("nicht-bestaetigt")}</span>, <a href="${zeitenSeite(g)}" target="_blank" rel="noopener">${ui("pruefen")}</a>` : "");
}

// Ein Satz über den Stand der Öffnungszeiten aller Orte des Plans.
function zeitenHinweis(liste) {
  if (state.zeitenStand === "laedt") return "";
  const offen = liste.filter((g) => zeitenBestaetigt(g) === false).length;
  if (!offen) return liste.some((g) => g.oeffnung) ? ui("zeiten-live") : "";
  return `${offen} ${ui(offen === 1 ? "zeiten-offen-1" : "zeiten-offen")}`;
}
