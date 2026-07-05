// =============================================================================
// ingest-paperform · Supabase Edge Function
// Nimmt Paperform-Webhooks der Wochenschrift-Aktion entgegen und schreibt jede
// Einreichung als Aktions-Anmeldung nach public.sommer2026_signups (produkt='wos').
// Das Formular IST die Aktion – jede Einreichung zählt als 'neu'.
//
// Sprache/Format pro Formular über die URL steuerbar:
//   …/ingest-paperform?key=<secret>&sprache=de&format=papier
// Tarif/Intervall werden aus den Feldern erraten; jeder Payload wird
// PII-redigiert (E-Mail/Name/Adresse) in sommer2026_ingest_raw geloggt, um das
// Mapping am ersten echten Formular zu verfeinern.
//
// Entdopplung: dedup_key = wos:<gesalzener E-Mail-Hash> (Person je Produkt, auch
// über Paperform UND Zoho hinweg), Fallback paperform:<submission_id>.
//
// Scharf nur wenn sommer2026_config.aktion_aktiv = 'true'. Auth: ?key=<secret>.
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };
const EMAIL_RE = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i;

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// UTM-Tupel + Landingpage aus einer im Body eingebetteten URL (Paperform trägt die
// Herkunfts-URL mit; die Anmelde-Links tragen die UTM-Parameter der Massnahme).
function utmFromBody(body: any): { src: string | null; med: string | null; camp: string | null; cont: string | null; land: string | null } {
  const out = { src: null as string | null, med: null as string | null, camp: null as string | null, cont: null as string | null, land: null as string | null };
  const urls = (JSON.stringify(body).match(/https?:\/\/[^\s"'<>\\]+/gi) || []);
  for (const u of urls) {
    try {
      const url = new URL(u);
      const q = url.searchParams;
      out.src = out.src || q.get("utm_source"); out.med = out.med || q.get("utm_medium");
      out.camp = out.camp || q.get("utm_campaign"); out.cont = out.cont || q.get("utm_content");
      if ((q.get("utm_source") || q.get("utm_campaign")) && !out.land) out.land = url.pathname;
    } catch { /* keine URL */ }
  }
  return out;
}

// PII entfernen: nach Schlüsselname UND E-Mail-artige Werte.
function redact(o: any): any {
  if (typeof o === "string") return EMAIL_RE.test(o) ? "***" : o;
  if (Array.isArray(o)) return o.map(redact);
  if (o && typeof o === "object") {
    const r: any = {};
    for (const k of Object.keys(o)) r[k] = /(email|name|phone|address|\bip\b|vorname|nachname|strasse)/i.test(k) ? "***" : redact(o[k]);
    return r;
  }
  return o;
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("ok", { status: 200 });

  const u = new URL(req.url);
  const key = u.searchParams.get("key") || req.headers.get("x-webhook-key") || "";
  const cfgRows = await fetch(`${SB}/rest/v1/sommer2026_config?key=in.(webhook_secret,hash_salt,aktion_aktiv)&select=key,value`, { headers: H })
    .then((r) => r.json()).catch(() => []);
  const cfg: Record<string, string> = {};
  if (Array.isArray(cfgRows)) for (const r of cfgRows) cfg[r.key] = r.value;
  const secret = cfg["webhook_secret"] || null;
  if (!secret || key !== secret) return new Response("unauthorized", { status: 401 });

  let body: any = {};
  try { body = await req.json(); } catch { /* leer */ }

  await fetch(`${SB}/rest/v1/sommer2026_ingest_raw`, {
    method: "POST", headers: { ...H, Prefer: "return=minimal" },
    body: JSON.stringify({ source: "paperform", event: "submission", ok: true, note: "empfangen", payload: redact(body) }),
  }).catch(() => {});

  if ((cfg["aktion_aktiv"] || "").toLowerCase() !== "true") return json({ ok: true, mode: "log" });

  const blob = JSON.stringify(body).toLowerCase();

  // Sprache/Format: URL-Vorgabe je Formular hat Vorrang, sonst aus Inhalt geraten.
  const sprache = (u.searchParams.get("sprache") || (/english|englisch/.test(blob) ? "en" : "de")).toLowerCase() === "en" ? "en" : "de";
  const formatQ = (u.searchParams.get("format") || "").toLowerCase();
  const format = formatQ === "papier" || formatQ === "digital" ? formatQ
    : /digital|online|e-?paper|\bpdf\b/.test(blob) ? "digital"
    : /papier|print|gedruckt|\bpaper\b|frei haus/.test(blob) ? "papier" : "papier";
  const tarif = /erm(ä|ae)ss|reduc|student|reduziert/.test(blob) ? "ermaessigt" : "standard";
  const intervall = /(monat|month|mensuel)/.test(blob) ? "monatlich" : /(jähr|jahr|year|annual)/.test(blob) ? "jaehrlich" : "jaehrlich";
  const waehrungQ = (u.searchParams.get("waehrung") || "").toLowerCase();
  const waehrung = waehrungQ === "eur" || waehrungQ === "chf" ? waehrungQ : (/\bchf\b|fr\.?\b/.test(blob) ? "chf" : /\beur\b|€/.test(blob) ? "eur" : null);

  // E-Mail für Entdopplung (aus rohem Body, vor Redaktion).
  const emailMatch = JSON.stringify(body).match(EMAIL_RE);
  const email = emailMatch ? emailMatch[0].toLowerCase() : "";
  const salt = cfg["hash_salt"] || "";
  const subId = body?.submission_id || body?.id || body?.data?.submission_id || "";
  const dedupKey = email ? `wos:${await sha256Hex(salt + email)}` : `paperform:${subId || (await sha256Hex(blob)).slice(0, 24)}`;

  const utm = utmFromBody(body);
  const row = {
    signed_up_at: new Date().toISOString(), produkt: "wos", sprache, format,
    tarif, intervall, waehrung, status: "neu", kanal: "andere", source: "paperform", ext_id: String(subId || ""), dedup_key: dedupKey,
    kampagne: utm.camp || "summer26_trial",
    utm_source: utm.src, utm_medium: utm.med, utm_campaign: utm.camp, utm_content: utm.cont,
    landing_path: utm.land ? utm.land.slice(0, 200) : null,
  };
  const res = await fetch(`${SB}/rest/v1/sommer2026_signups?on_conflict=dedup_key`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    await fetch(`${SB}/rest/v1/sommer2026_ingest_raw`, {
      method: "POST", headers: { ...H, Prefer: "return=minimal" },
      body: JSON.stringify({ source: "paperform", event: "submission", ok: false, note: `upsert ${res.status}`, payload: redact(body) }),
    }).catch(() => {});
    return json({ ok: false }, 200);
  }
  return json({ ok: true, produkt: "wos", sprache, format, tarif, intervall, waehrung });
});
