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

  // E-Mail für Entdopplung (aus rohem Body, vor Redaktion).
  const emailMatch = JSON.stringify(body).match(EMAIL_RE);
  const email = emailMatch ? emailMatch[0].toLowerCase() : "";
  const salt = cfg["hash_salt"] || "";
  const subId = body?.submission_id || body?.id || body?.data?.submission_id || "";
  const dedupKey = email ? `wos:${await sha256Hex(salt + email)}` : `paperform:${subId || (await sha256Hex(blob)).slice(0, 24)}`;

  const row = {
    signed_up_at: new Date().toISOString(), produkt: "wos", sprache, format,
    tarif, intervall, status: "neu", kanal: "andere", source: "paperform", ext_id: String(subId || ""), dedup_key: dedupKey,
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
  return json({ ok: true, produkt: "wos", sprache, format, tarif, intervall });
});
