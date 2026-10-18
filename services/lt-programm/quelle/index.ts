// =============================================================================
// lt-programm-quelle · Supabase Edge Function — das Fenster zur Tagungsseite
// -----------------------------------------------------------------------------
// Holt die Programm- und die Startseite von agriculture-conference.org und gibt
// sie an die Vorschau apps/lt-programm/ weiter. Mehr tut sie nicht: gelesen wird
// im Browser, mit demselben Modul, das auch die gespeicherte Fassung schreibt
// (apps/lt-programm/webseite-lesen.js) — eine Wahrheit, kein zweiter Leser.
//
// Nötig ist sie nur wegen der Herkunftsregel des Browsers: eine Seite auf
// werkzeuge.goetheanum.ch darf agriculture-conference.org nicht selbst lesen.
// Diese Funktion darf es und setzt die passenden CORS-Kopfzeilen.
//
// Skripte, Stile und Kommentare werden vorher entfernt — das ist genau das, was
// der Leser ohnehin wegwirft, und macht aus ~640 KB rund 80 KB.
//
// Ohne Schlüssel, ohne Personendaten, nichts wird gespeichert. Antwort zehn
// Minuten cachebar, im Isolat ein kleines Gedächtnis dazu; `?frisch` umgeht es.
// Herkunfts-Sperre wie im Haus üblich (ERLAUBT) — eine Hürde gegen fremde
// Seiten, kein Schloss; die Wirkfläche ist ein öffentlicher Lesezugriff.
// Quelle im Repo: services/lt-programm/quelle/index.ts
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const QUELLEN: Record<string, string> = {
  programm: "https://www.agriculture-conference.org/programm",
  start: "https://www.agriculture-conference.org/",
};
const CACHE_SEK = 600;

const ERLAUBT = [
  "https://werkzeuge.goetheanum.ch",
  "https://phtok.github.io",
];
function erlaubt(origin: string): boolean {
  return ERLAUBT.includes(origin) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
}
function kopfzeilen(origin: string): Record<string, string> {
  return {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": `public, max-age=${CACHE_SEK}`,
    "Access-Control-Allow-Origin": erlaubt(origin) ? origin : ERLAUBT[0],
    "Vary": "Origin",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
  };
}

// Was der Leser ohnehin wegwirft, fliegt schon hier raus.
function entschlacken(html: string): string {
  return html
    .replace(/<(script|style|noscript|svg)\b[\s\S]*?<\/\1>/gi, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/[ \t]{2,}/g, " ");
}

type Antwort = { stand: string; quellen: typeof QUELLEN; seiten: Record<string, string>; fehler: string[] };
let gedaechtnis: { bis: number; antwort: Antwort } | null = null;

async function laden(): Promise<Antwort> {
  const fehler: string[] = [];
  const seiten: Record<string, string> = {};
  await Promise.all(Object.entries(QUELLEN).map(async ([name, url]) => {
    try {
      const r = await fetch(url, {
        headers: { "User-Agent": "goetheanum-werkzeuge/lt-programm (werkzeuge.goetheanum.ch)" },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      seiten[name] = entschlacken(await r.text());
    } catch (e) {
      fehler.push(`${url}: ${(e as Error).message}`);
    }
  }));
  return { stand: new Date().toISOString(), quellen: QUELLEN, seiten, fehler };
}

Deno.serve(async (req) => {
  const origin = req.headers.get("origin") || "";
  const kopf = kopfzeilen(origin);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: kopf });
  if (req.method !== "GET") return new Response(JSON.stringify({ fehler: ["nur GET"] }), { status: 405, headers: kopf });

  const jetzt = Date.now();
  if (!gedaechtnis || gedaechtnis.bis < jetzt || new URL(req.url).searchParams.has("frisch")) {
    const antwort = await laden();
    // Nur ein voller Erfolg wird behalten; ein Fehlschlag darf nicht festfrieren.
    gedaechtnis = { bis: antwort.fehler.length ? jetzt : jetzt + CACHE_SEK * 1000, antwort };
  }
  const a = gedaechtnis.antwort;
  return new Response(JSON.stringify(a), { status: a.fehler.length && !Object.keys(a.seiten).length ? 502 : 200, headers: kopf });
});
