// =============================================================================
// campusplan-ausnahmen · Supabase Edge Function — tagesaktuelle Ausnahmen
// Liest die beiden Seiten von goetheanum.ch, auf denen das Haus die
// Einschränkungen des Grossen Saals (Veranstaltungen, Proben) und die
// Schliesstage der Glashaus-Ausstellung pflegt — reine Textlisten wie
// «Do. 17.9. 14.00-14.20 Uhr» oder «So. 13.9.» unter «Geschlossen am:» —
// und liefert sie als JSON an den Campusplan (apps/campusplan/).
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
  saal: "https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal",
  glashaus: "https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe",
};
const CACHE_SEK = 3600;

type Eintrag = { datum: string; zu: boolean; zeit?: string; text: string };
type Antwort = {
  stand: string;
  quellen: typeof QUELLEN;
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
  const [saal, glashaus] = await Promise.all([hole(QUELLEN.saal), hole(QUELLEN.glashaus)]);
  return {
    stand: new Date().toISOString(),
    quellen: QUELLEN,
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
