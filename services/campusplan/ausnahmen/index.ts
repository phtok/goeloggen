// =============================================================================
// campusplan-ausnahmen · Supabase Edge Function — Öffnungszeiten, live
// Liest drei Seiten von goetheanum.ch und liefert sie als JSON an den
// Campusplan (apps/campusplan/):
//  · die Öffnungszeiten-Seite (/de/campus/oeffnungszeiten) als Zeitfenster je
//    Ort — «Grosser Saal / Täglich: 13.30 - 14.30 Uhr» → { tage, von, bis };
//    der Plan rechnet damit seinen Zeitplan, immer mit dem Stand der Website
//    (Auftrag 18. Oktober 2026), die Werte in gaeste.js sind nur der Rückfall;
//  · die Einschränkungen des Grossen Saals (Veranstaltungen, Proben) und die
//    Schliesstage der Glashaus-Ausstellung — reine Textlisten wie
//    «Do. 17.9. 14.00-14.20 Uhr» oder «So. 13.9.» unter «Geschlossen am:».
//
// Öffentlich, ohne Schlüssel, ohne Personendaten: es geht nur die Anfrage
// nach goetheanum.ch hinaus, nichts wird gespeichert. Antwort eine Stunde
// cachebar; im Isolat zusätzlich ein Gedächtnis, damit nicht jeder Aufruf
// beide Seiten neu zieht. Fällt eine Seite aus, bleibt ihr Teil leer und
// `fehler` nennt sie — der Plan zeigt dann den Link statt der Zeile.
// Referenzkopie: services/campusplan/ausnahmen/index.ts (README daneben).
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const QUELLEN = {
  zeiten: "https://goetheanum.ch/de/campus/oeffnungszeiten",
  saal: "https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal",
  glashaus: "https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe",
};
const CACHE_SEK = 3600;

type Eintrag = { datum: string; zu: boolean; zeit?: string; text: string };
type Fenster = { tage: number[]; von: string; bis: string };
type Zeiten = { titel: string; kontext: string[]; fenster: Fenster[]; ersterImMonat?: boolean; zuMonate?: number[] };
type Antwort = {
  stand: string;
  quellen: typeof QUELLEN;
  zeiten: Zeiten[];
  saal: Eintrag[];
  glashaus: Eintrag[];
  fehler: string[];
};

let gedaechtnis: { bis: number; antwort: Antwort } | null = null;

// Sichtbaren Text der Seite als Zeilen: Skripte und Stile weg, Tags zu
// Zeilenumbrüchen, Entitäten aufgelöst, Fusszeile («Goetheanum / Rüttiweg 45»)
// abgeschnitten.
function zeilen(htmlText: string): string[] {
  let t = htmlText.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, "");
  const main = t.match(/<main[\s\S]*?<\/main>/i);
  if (main) t = main[0];
  t = t.replace(/<[^>]+>/g, "\n");
  t = t.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
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

// Öffnungszeiten-Seite → Zeitfenster je Ort. Eine Zeitzeile heisst
// «Mo. bis Do.: 14.30 - 15.30 Uhr» (auch «Täglich:», «Sa. und So.:»,
// «Jeden ersten Freitag im Monat:»), eine Folgezeile «und 14.00 - 16.00 Uhr»
// gilt für dieselben Tage, «Juli und August 2026 geschlossen» schliesst
// Monate. Der Ort ist die letzte Zeile ohne Zeit davor; die zwei Zeilen
// davor stehen als Kontext dabei (Glashaus → Ausstellungstitel). Kommt ein
// Ort zweimal vor (Vital-Café), gilt der erste Block.
const TAG_NR: Record<string, number> = { So: 0, Mo: 1, Di: 2, Mi: 3, Do: 4, Fr: 5, Sa: 6 };
const MONAT_NR: Record<string, number> = {
  januar: 1, februar: 2, märz: 3, april: 4, mai: 5, juni: 6, juli: 7, july: 7,
  august: 8, september: 9, oktober: 10, november: 11, dezember: 12,
};
const UHR = String.raw`(\d{1,2})[.:](\d{2})\s*[-–]\s*(\d{1,2})[.:](\d{2})\s*Uhr`;
const ZEITZEILE = new RegExp(String.raw`^(Täglich|Jeden ersten Freitag im Monat|(Mo|Di|Mi|Do|Fr|Sa|So)\.?(?:\s+(bis|und)\s+(Mo|Di|Mi|Do|Fr|Sa|So)\.?)?)\s*:\s*` + UHR + "$", "i");
const FOLGEZEILE = new RegExp("^und\\s+" + UHR + "$", "i");
const MONATE_ZU = /^([A-Za-zÄÖÜäöü]+)(?:\s+(und|bis)\s+([A-Za-zÄÖÜäöü]+))?(?:\s+\d{4})?\s+geschlossen$/i;

function uhr(h: string, m: string): string {
  return `${h.padStart(2, "0")}:${m}`;
}

function tageAus(text: string, a?: string, art?: string, b?: string): { tage: number[]; ersterImMonat: boolean } {
  if (/^täglich/i.test(text)) return { tage: [0, 1, 2, 3, 4, 5, 6], ersterImMonat: false };
  if (/ersten freitag/i.test(text)) return { tage: [5], ersterImMonat: true };
  const von = TAG_NR[a ?? ""];
  if (!b) return { tage: [von], ersterImMonat: false };
  const bis = TAG_NR[b];
  if (art === "und") return { tage: [von, bis], ersterImMonat: false };
  const tage: number[] = [];
  for (let d = von; ; d = (d + 1) % 7) { tage.push(d); if (d === bis) break; }
  return { tage, ersterImMonat: false };
}

function zeitenParsen(liste: string[]): Zeiten[] {
  const aus: Zeiten[] = [];
  const gesehen = new Set<string>();
  let block: Zeiten | null = null;
  let letzteTage: number[] = [];
  const ohneZeit: string[] = [];
  for (const zeile of liste) {
    const z = zeile.match(ZEITZEILE);
    const f = zeile.match(FOLGEZEILE);
    if (z) {
      if (!block) {
        const titel = ohneZeit[ohneZeit.length - 1] ?? "";
        block = { titel, kontext: ohneZeit.slice(-3, -1), fenster: [] };
        if (!gesehen.has(titel)) { gesehen.add(titel); aus.push(block); }
      }
      const { tage, ersterImMonat } = tageAus(z[1], z[2], z[3]?.toLowerCase(), z[4]);
      letzteTage = tage;
      if (ersterImMonat) block.ersterImMonat = true;
      block.fenster.push({ tage, von: uhr(z[5], z[6]), bis: uhr(z[7], z[8]) });
      continue;
    }
    if (f && block) {
      block.fenster.push({ tage: letzteTage, von: uhr(f[1], f[2]), bis: uhr(f[3], f[4]) });
      continue;
    }
    const zu = zeile.match(MONATE_ZU);
    if (zu && block && MONAT_NR[zu[1].toLowerCase()]) {
      const a = MONAT_NR[zu[1].toLowerCase()], b = MONAT_NR[(zu[3] ?? "").toLowerCase()];
      block.zuMonate = !b ? [a] : zu[2].toLowerCase() === "und" ? [a, b]
        : Array.from({ length: (b - a + 12) % 12 + 1 }, (_, i) => (a + i - 1) % 12 + 1);
      continue;
    }
    block = null;
    ohneZeit.push(zeile);
  }
  return aus.filter((b) => b.titel && b.fenster.length);
}

async function laden(): Promise<Antwort> {
  const fehler: string[] = [];
  const hole = async (url: string): Promise<string[]> => {
    try {
      const r = await fetch(url, { headers: { "User-Agent": "goetheanum-campusplan/1.0 (werkzeuge.goetheanum.ch)" } });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return zeilen(await r.text());
    } catch (e) {
      fehler.push(`${url}: ${(e as Error).message}`);
      return [];
    }
  };
  const [zeiten, saal, glashaus] = await Promise.all([hole(QUELLEN.zeiten), hole(QUELLEN.saal), hole(QUELLEN.glashaus)]);
  return {
    stand: new Date().toISOString(),
    quellen: QUELLEN,
    zeiten: zeitenParsen(zeiten),
    saal: parsen(saal, false),
    glashaus: parsen(glashaus, true),
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
