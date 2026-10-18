// =============================================================================
// campusplan-ausnahmen · Supabase Edge Function — Öffnungszeiten, live
// Liest bei jedem Aufruf (eine Stunde zwischengespeichert) die Seiten, auf
// denen die Orte des Campusplans ihre Zeiten pflegen, und liefert sie als
// JSON an den Campusplan (apps/campusplan/). Auftrag 18. Oktober 2026:
// «Alle Öffnungszeiten aktuell abgleichen! … nach spezifischer Planung vor
// einer verschlossenen Tür zu stehen — da dürfen wir umsichtig sein.»
//
//  · zeiten        — jeder Ort als Zeitfenster { tage, von, bis }, aus:
//                    goetheanum.ch (Öffnungszeiten-Seite), Buchhandlung,
//                    Bibliothek (samt Ferien), Rudolf Steiner Archiv,
//                    Vital Speisehaus. Jeder Block nennt seine Seite (`seite`).
//  · saal/glashaus — tagesaktuelle Einschränkungen von Grossem Saal und
//                    Glashaus-Ausstellung («Do. 17.9. 14.00-14.20 Uhr»).
//  · ausstellungen — laufende Ausstellungen der Sektion für Bildende Künste
//                    (Kunstgalerie im Goetheanum), mit ihren Teilen und Daten.
//
// Was eine Seite nicht hergibt (nicht erreichbar, nichts erkannt), steht in
// `fehler` — der Plan sagt dann offen «nicht bestätigt» statt still auf
// alte Werte zu bauen. Öffentlich, ohne Schlüssel, ohne Personendaten: nur
// Anfragen an die Websites, nichts wird gespeichert.
// Referenzkopie: services/campusplan/ausnahmen/index.ts (README daneben).
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const QUELLEN = {
  zeiten: "https://goetheanum.ch/de/campus/oeffnungszeiten",
  saal: "https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal",
  glashaus: "https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe",
  buchhandlung: "https://www.goetheanum-buchhandlung.ch/pages/oeffnungszeiten",
  bibliothek: "https://goetheanum.ch/de/dokumentation/bibliothek",
  archiv: "https://www.rudolf-steiner.com/",
  speisehaus: "https://www.speisehaus.ch/",
  ausstellungen: "https://sbk.goetheanum.org/veranstaltungen/ausstellungen",
};
const ZEITEN_SEITEN = ["zeiten", "buchhandlung", "bibliothek", "archiv", "speisehaus"] as const;
const CACHE_SEK = 3600;

type Eintrag = { datum: string; zu: boolean; zeit?: string; text: string };
type Fenster = { tage: number[]; von: string; bis: string };
type Zeitraum = { von: string; bis: string };
type Zeiten = {
  seite: string; titel: string; kontext: string[]; fenster: Fenster[];
  ersterImMonat?: boolean; zuMonate?: number[]; zuZeitraeume?: Zeitraum[];
};
type Teil = { titel: string; von: string; bis: string };
type Ausstellung = { titel: string; untertitel: string; von: string; bis: string; link: string; teile: Teil[]; fenster: Fenster[] };
type Antwort = {
  stand: string;
  quellen: typeof QUELLEN;
  zeiten: Zeiten[];
  saal: Eintrag[];
  glashaus: Eintrag[];
  ausstellungen: Ausstellung[];
  fehler: string[];
};

let gedaechtnis: { bis: number; antwort: Antwort } | null = null;

// Sichtbaren Text der Seite als Zeilen: Skripte, Stile und Grafiken weg,
// Tags zu Zeilenumbrüchen, Entitäten aufgelöst. Mit `nurMain` nur der
// <main>-Teil und ohne die Fusszeile von goetheanum.ch.
function zeilen(htmlText: string, nurMain = true): string[] {
  let t = htmlText.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<svg[\s\S]*?<\/svg>/gi, "");
  const main = nurMain ? t.match(/<main[\s\S]*?<\/main>/i) : null;
  if (main) t = main[0];
  t = t.replace(/<[^>]+>/g, "\n");
  t = t.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&ndash;/g, "–").replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)))
    .replace(/&(auml|ouml|uuml|Auml|Ouml|Uuml|szlig);/g, (_, e) =>
      ({ auml: "ä", ouml: "ö", uuml: "ü", Auml: "Ä", Ouml: "Ö", Uuml: "Ü", szlig: "ß" })[e] ?? "");
  const alle = t.split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean);
  const ende = alle.findIndex((l, i) => l === "Goetheanum" && /^Rüttiweg/.test(alle[i + 1] ?? ""));
  return ende > 0 ? alle.slice(0, ende) : alle;
}

// Zeile «Do. 17.9. 14.00-14.20 Uhr» → Eintrag. Das Jahr kommt aus einer
// «2026»-Zeile davor, sonst aus dem Datum des Aufrufs; ein Monat kleiner als
// der aktuelle deutet auf das nächste Jahr (Listen laufen über den Jahreswechsel).
function parsen(liste: string[], geschlossenModus: boolean): Eintrag[] {
  const heute = new Date();
  let jahr = heute.getFullYear();
  let zuAbschnitt = false;
  const aus: Eintrag[] = [];
  for (const zeile of liste) {
    const j = zeile.match(/^(20\d{2})$/);
    if (j) { jahr = Number(j[1]); continue; }
    if (/^geschlossen am/i.test(zeile)) { zuAbschnitt = true; continue; }
    const m = zeile.match(/^(Mo|Di|Mi|Do|Fr|Sa|So)\.?\s*(\d{1,2})\.(\d{1,2})\.?\s*(.*)$/);
    if (!m) continue;
    const tag = Number(m[2]), monat = Number(m[3]);
    let j2 = jahr;
    if (!liste.some((l) => /^20\d{2}$/.test(l)) && monat < heute.getMonth() + 1 - 6) j2 = jahr + 1;
    const rest = m[4].trim();
    const zu = geschlossenModus || zuAbschnitt || /geschlossen/i.test(rest);
    const zeit = zu ? undefined : rest.replace(/\s*Uhr\s*$/i, "").replace(/-/g, "–").trim() || undefined;
    aus.push({
      datum: `${j2}-${String(monat).padStart(2, "0")}-${String(tag).padStart(2, "0")}`,
      zu,
      zeit,
      text: zu ? "geschlossen" : (zeit ? `${zeit} Uhr` : rest),
    });
  }
  return aus;
}

/* ---------- Öffnungszeiten: ein Parser für alle Seiten ----------
   Alle Quellen setzen dasselbe Muster, nur verschieden umbrochen:
     «Grosser Saal / Täglich: 13.30 - 14.30 Uhr»           (goetheanum.ch)
     «Allgemeine Öffnungszeiten / Di-Fr 10.00-18.00 Uhr»   (Buchhandlung)
     «Öffnungszeiten / Dienstag / 14 – 18 Uhr»             (Bibliothek)
     «Lesesaal & Shop: Mo-Fr 15 bis 18 Uhr»                (Archiv)
     «Laden / Mo – Fr: / 8.00–18.30»                       (Speisehaus)
   Ein Block beginnt mit einer Zeile ohne Tage und Zeit (dem Ort); Tage und
   Zeit stehen in einer Zeile oder in zwei aufeinander; «und 14.00 - 16.00 Uhr»
   gilt für dieselben Tage; «Juli und August 2026 geschlossen» schliesst
   Monate; ein Datumsbereich («27. Juli 2026 – 31. August 2026») unter
   «Ferien» schliesst einen Zeitraum. Kommt ein Ort zweimal vor, gilt der erste. */

const TAG_WORT: Record<string, number> = {
  so: 0, mo: 1, di: 2, mi: 3, do: 4, fr: 5, sa: 6,
  sonntag: 0, montag: 1, dienstag: 2, mittwoch: 3, donnerstag: 4, freitag: 5, samstag: 6,
  sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6,
  sunday: 0, monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5, saturday: 6,
};
const MONAT_NR: Record<string, number> = {
  januar: 1, februar: 2, märz: 3, april: 4, mai: 5, juni: 6, juli: 7, july: 7,
  august: 8, september: 9, oktober: 10, november: 11, dezember: 12,
};
const TAG = "(?:" + Object.keys(TAG_WORT).sort((a, b) => b.length - a.length).join("|") + ")\\.?";
const TAGE = `(?:täglich|daily|jeden ersten freitag im monat|${TAG}(?:\\s*(?:-|–|bis|und|to|and|,)\\s*${TAG})*)`;
const ZEIT = String.raw`(\d{1,2})(?:[.:](\d{2}))?\s*(am|pm)?\s*(?:-|–|bis|to)\s*(\d{1,2})(?:[.:](\d{2}))?\s*(am|pm)?(?:\s*Uhr)?`;
const R_TAGE_ZEIT = new RegExp(`^(?:([^:]{2,40}):\\s*)?(${TAGE})\\s*:?\\s+${ZEIT}$`, "i");
const R_TAGE = new RegExp(`^(${TAGE})\\s*:?$`, "i");
const R_ZEIT = new RegExp(`^(?:und\\s+)?${ZEIT}$`, "i");
const R_MONATE_ZU = /^([A-Za-zÄÖÜäöü]+)(?:\s+(und|bis)\s+([A-Za-zÄÖÜäöü]+))?(?:\s+\d{4})?\s+geschlossen$/i;
const R_DATUM = String.raw`(\d{1,2})\.\s*([A-Za-zÄÖÜäöü]+)\s*(\d{4})?`;
const R_ZEITRAUM = new RegExp(`^${R_DATUM}\\s*(?:–|-|bis)\\s*${R_DATUM}$`, "i");

function uhr(h: string, m: string | undefined, ampm?: string): string {
  let stunde = Number(h);
  if (ampm && /pm/i.test(ampm) && stunde < 12) stunde += 12;
  return `${String(stunde).padStart(2, "0")}:${m ?? "00"}`;
}

function tageAus(text: string): { tage: number[]; ersterImMonat: boolean } {
  const t = text.toLowerCase().replace(/\./g, "");
  if (/^(täglich|daily)/.test(t)) return { tage: [0, 1, 2, 3, 4, 5, 6], ersterImMonat: false };
  if (/ersten freitag/.test(t)) return { tage: [5], ersterImMonat: true };
  const teile = t.split(/\s*(-|–|bis|to|und|and|,)\s*/).filter(Boolean);
  const tage: number[] = [];
  for (let i = 0; i < teile.length; i++) {
    const d = TAG_WORT[teile[i]];
    if (d == null) continue;
    if (/^(-|–|bis|to)$/.test(teile[i - 1] ?? "") && tage.length) {
      for (let x = (tage[tage.length - 1] + 1) % 7; ; x = (x + 1) % 7) { tage.push(x); if (x === d) break; }
    } else tage.push(d);
  }
  return { tage: [...new Set(tage)], ersterImMonat: false };
}

function datumIso(tag: string, monat: string, jahr: string | undefined, ersatzJahr: number): string {
  const m = MONAT_NR[monat.toLowerCase()] ?? 0;
  return `${jahr ?? ersatzJahr}-${String(m).padStart(2, "0")}-${String(Number(tag)).padStart(2, "0")}`;
}

function zeitenParsen(liste: string[], seite: string): Zeiten[] {
  const aus: Zeiten[] = [];
  const gesehen = new Set<string>();
  let block: Zeiten | null = null;
  let offeneTage: { tage: number[]; ersterImMonat: boolean } | null = null;
  let letzteTage: number[] = [];
  let ferien = false;
  const zuZeitraeume: Zeitraum[] = [];
  const ohneZeit: string[] = [];
  const neuerBlock = (titel: string) => {
    const b: Zeiten = { seite, titel, kontext: ohneZeit.slice(-3, -1), fenster: [] };
    if (!gesehen.has(titel)) { gesehen.add(titel); aus.push(b); }
    return b;
  };
  const fenster = (tage: number[], z: RegExpMatchArray, i: number) => {
    block!.fenster.push({ tage, von: uhr(z[i], z[i + 1], z[i + 2] || z[i + 5]), bis: uhr(z[i + 3], z[i + 4], z[i + 5]) });
  };
  for (const zeile of liste) {
    const tz = zeile.match(R_TAGE_ZEIT);
    if (tz) {
      const label = tz[1] && !R_TAGE.test(tz[1]) ? tz[1].trim() : "";
      if (label) block = neuerBlock(label);
      else if (!block) block = neuerBlock(ohneZeit[ohneZeit.length - 1] ?? "");
      const t = tageAus(tz[2]);
      if (t.ersterImMonat) block.ersterImMonat = true;
      letzteTage = t.tage;
      fenster(t.tage, tz, 3);
      offeneTage = null;
      continue;
    }
    const nurTage = zeile.match(R_TAGE);
    if (nurTage) {
      if (!block) block = neuerBlock(ohneZeit[ohneZeit.length - 1] ?? "");
      offeneTage = tageAus(nurTage[1]);
      continue;
    }
    const nurZeit = zeile.match(R_ZEIT);
    if (nurZeit && block && (offeneTage || /^und\s/i.test(zeile))) {
      const tage = offeneTage ? offeneTage.tage : letzteTage;
      if (offeneTage?.ersterImMonat) block.ersterImMonat = true;
      letzteTage = tage;
      fenster(tage, nurZeit, 1);
      offeneTage = null;
      continue;
    }
    const zu = zeile.match(R_MONATE_ZU);
    if (zu && block && MONAT_NR[zu[1].toLowerCase()]) {
      const a = MONAT_NR[zu[1].toLowerCase()], b = MONAT_NR[(zu[3] ?? "").toLowerCase()];
      block.zuMonate = !b ? [a] : zu[2].toLowerCase() === "und" ? [a, b]
        : Array.from({ length: (b - a + 12) % 12 + 1 }, (_, i) => (a + i - 1) % 12 + 1);
      continue;
    }
    if (/^ferien/i.test(zeile)) ferien = true;
    const zr = zeile.match(R_ZEITRAUM);
    if (zr && ferien) {
      const jahr = Number(zr[6] ?? new Date().getFullYear());
      zuZeitraeume.push({ von: datumIso(zr[1], zr[2], zr[3], jahr), bis: datumIso(zr[4], zr[5], zr[6], jahr) });
      continue;
    }
    if (/geschlossen$/i.test(zeile) && !block) continue;
    block = null;
    offeneTage = null;
    ohneZeit.push(zeile);
  }
  const ergebnis = aus.filter((b) => b.titel && b.fenster.length);
  if (zuZeitraeume.length) ergebnis.forEach((b) => { b.zuZeitraeume = zuZeitraeume; });
  return ergebnis;
}

/* ---------- Ausstellungen der Sektion für Bildende Künste ----------
   Liste: «Walther Roggenkamp 1926 bis 1995 / 18.09.2026 – 01.03.2027 /
   Drei Ausstellungen im Goetheanum / Weiterlesen». Die Einzelseite nennt die
   Teile: «Kosmische Botanik / … / 18. September bis 22. November 2026»,
   «Olav Åsteson / … / 4. Dezember 2026 bis März 2027» (ohne Tag = Monatsende). */

const R_LISTE_DATUM = /^(\d{2})\.(\d{2})\.(\d{4})\s*[–-]\s*(\d{2})\.(\d{2})\.(\d{4})$/;
const R_TEIL_DATUM = /^(?:(\d{1,2})\.\s*)?([A-Za-zÄÖÜäöü]+)\.?(?:\s+(\d{4}))?\s+bis\s+(?:(\d{1,2})\.\s*)?([A-Za-zÄÖÜäöü]+)\.?\s+(\d{4})$/;

function teilDatum(tag: string | undefined, monat: string, jahr: number, ende: boolean): string {
  const m = MONAT_NR[monat.toLowerCase()] ?? MONAT_NR[Object.keys(MONAT_NR).find((k) => k.startsWith(monat.toLowerCase().slice(0, 3))) ?? ""] ?? 1;
  const t = tag ? Number(tag) : (ende ? new Date(jahr, m, 0).getDate() : 1);
  return `${jahr}-${String(m).padStart(2, "0")}-${String(t).padStart(2, "0")}`;
}

// Der Titel eines Teils ist die erste Zeile seines Abschnitts; beim ersten
// Teil beginnt der Abschnitt erst nach dem Untertitel der Ausstellung.
function teileParsen(liste: string[], kopf: string): Teil[] {
  const teile: Teil[] = [];
  let seitLetztem: string[] = [];
  for (const zeile of liste) {
    const d = zeile.match(R_TEIL_DATUM);
    if (d && MONAT_NR[d[5].toLowerCase()] != null) {
      const bisJahr = Number(d[6]);
      const vonJahr = d[3] ? Number(d[3]) : bisJahr;
      const ab = kopf ? seitLetztem.lastIndexOf(kopf) + 1 : 0;
      const titel = seitLetztem.slice(ab).find((z) => z.length > 3 && !/^(Wann|Wer|Wo)\?$/.test(z)) ?? "";
      teile.push({ titel, von: teilDatum(d[1], d[2], vonJahr, false), bis: teilDatum(d[4], d[5], bisJahr, true) });
      seitLetztem = [];
      continue;
    }
    seitLetztem.push(zeile);
  }
  return teile;
}

async function ausstellungenLaden(hole: (url: string, nurMain?: boolean) => Promise<{ text: string; zeilen: string[] }>): Promise<Ausstellung[]> {
  const liste = await hole(QUELLEN.ausstellungen);
  const links = [...liste.text.matchAll(/href="([^"]*\/einzelansicht\/[^"]+)"/g)].map((m) => new URL(m[1], QUELLEN.ausstellungen).href);
  const aus: Ausstellung[] = [];
  const z = liste.zeilen;
  for (let i = 1; i < z.length; i++) {
    const m = z[i].match(R_LISTE_DATUM);
    if (!m) continue;
    aus.push({
      titel: z[i - 1], untertitel: z[i + 1] && z[i + 1] !== "Weiterlesen" ? z[i + 1] : "",
      von: `${m[3]}-${m[2]}-${m[1]}`, bis: `${m[6]}-${m[5]}-${m[4]}`,
      link: links[aus.length] ?? QUELLEN.ausstellungen, teile: [], fenster: [],
    });
  }
  const heute = new Date().toISOString().slice(0, 10);
  await Promise.all(aus.filter((a) => a.bis >= heute).map(async (a) => {
    if (a.link === QUELLEN.ausstellungen) return;
    try {
      const seite = (await hole(a.link, false)).zeilen;
      a.teile = teileParsen(seite, a.untertitel)
        .map((t) => ({ ...t, bis: t.bis > a.bis ? a.bis : t.bis }));
      // Öffnungszeiten der Ausstellung, sobald die Seite sie nennt (Stand
      // 18. 10. 2026 noch nicht) — dann gelten sie für die Galerie statt der
      // Zeiten des Baus.
      a.fenster = zeitenParsen(seite, "ausstellung").find((b) => b.fenster.length)?.fenster ?? [];
    } catch { /* Teile fehlen, die Ausstellung bleibt */ }
  }));
  return aus.filter((a) => a.bis >= heute);
}

async function laden(): Promise<Antwort> {
  const fehler: string[] = [];
  const holeRoh = async (url: string, nurMain = true) => {
    let letzter: Error | null = null;
    for (let versuch = 0; versuch < 2; versuch++) {
      try {
        const r = await fetch(url, { headers: { "User-Agent": "goetheanum-campusplan/1.1 (werkzeuge.goetheanum.ch)" } });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const text = await r.text();
        return { text, zeilen: zeilen(text, nurMain) };
      } catch (e) { letzter = e as Error; }
    }
    throw letzter ?? new Error("unbekannt");
  };
  const hole = async (url: string, nurMain = true): Promise<string[]> => {
    try { return (await holeRoh(url, nurMain)).zeilen; }
    catch (e) { fehler.push(`${url}: ${(e as Error).message}`); return []; }
  };
  // Speisehaus und Archiv führen die Zeiten ausserhalb von <main>.
  const nurMain: Record<string, boolean> = { zeiten: true, buchhandlung: true, bibliothek: true, archiv: false, speisehaus: false };
  const [saal, glashaus, ...seiten] = await Promise.all([
    hole(QUELLEN.saal), hole(QUELLEN.glashaus),
    ...ZEITEN_SEITEN.map((s) => hole(QUELLEN[s], nurMain[s])),
  ]);
  const zeiten: Zeiten[] = [];
  ZEITEN_SEITEN.forEach((s, i) => {
    const bloecke = zeitenParsen(seiten[i], s);
    if (seiten[i].length && !bloecke.length) fehler.push(`${QUELLEN[s]}: keine Öffnungszeiten erkannt`);
    zeiten.push(...bloecke);
  });
  let ausstellungen: Ausstellung[] = [];
  try { ausstellungen = await ausstellungenLaden(holeRoh); }
  catch (e) { fehler.push(`${QUELLEN.ausstellungen}: ${(e as Error).message}`); }
  return {
    stand: new Date().toISOString(),
    quellen: QUELLEN,
    zeiten,
    saal: parsen(saal, false),
    glashaus: parsen(glashaus, true),
    ausstellungen,
    fehler,
  };
}

Deno.serve(async (req) => {
  const kopf = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": `public, max-age=${CACHE_SEK}`,
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
  };
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: kopf });
  const jetzt = Date.now();
  if (!gedaechtnis || gedaechtnis.bis < jetzt || new URL(req.url).searchParams.has("frisch")) {
    const antwort = await laden();
    // Nur ein voller Erfolg wird für die Stunde behalten.
    gedaechtnis = { bis: antwort.fehler.length ? jetzt : jetzt + CACHE_SEK * 1000, antwort };
  }
  return new Response(JSON.stringify(gedaechtnis.antwort), { headers: kopf });
});
