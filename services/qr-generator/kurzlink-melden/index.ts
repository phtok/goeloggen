// =============================================================================
// kurzlink-melden · Supabase Edge Function
// Vorbild: services/schmiede/schmiede-melden/index.ts (Resend + Config-Tabelle).
//
// Aufruf: POST { code, url, domain, quelle, key } – ausgelöst vom Trigger
// kurzlink_neue_domain() (services/werkzeug-schluessel/umkehrbar.sql), wenn
// ein Kurzlink auf eine Domain zeigt, die noch nie verwendet wurde. Prüft key
// gegen kurzlink_config.melde_key und schickt EINE kurze Mail an
// kurzlink_config.empfaenger. Absender + Resend-Key aus marketing_config.
// Das Ziel steht als Text in der Mail, nicht als Link (Phishing-Verdacht).
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };

async function configVon(tabelle: string): Promise<Record<string, string>> {
  const r = await fetch(`${SB}/rest/v1/${tabelle}?select=key,value`, { headers: H });
  const rows = r.ok ? await r.json() : [];
  const c: Record<string, string> = {};
  for (const row of rows) c[row.key] = row.value;
  return c;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return new Response("nein", { status: 405 });
  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { return new Response("bad", { status: 400 }); }

  const kc = await configVon("kurzlink_config");
  if (!kc.melde_key || String(body.key ?? "") !== kc.melde_key) return new Response("nein", { status: 403 });

  const mc = await configVon("marketing_config");
  if (!mc.resend_api_key || !mc.absender || !kc.empfaenger) {
    return new Response(JSON.stringify({ ok: false, grund: "unkonfiguriert" }), { status: 200 });
  }

  const code = String(body.code ?? "").slice(0, 60);
  const ziel = String(body.url ?? "").slice(0, 500);
  const domain = String(body.domain ?? "").slice(0, 200);
  const werkzeug = body.quelle === "sommer2026_links" ? "UTM-Generator" : "QR-Generator";
  const html = `<!doctype html><html lang="de-CH"><body style="margin:0;background:#faf8f4">
  <div style="max-width:520px;margin:0 auto;padding:32px 20px;font-family:Georgia,serif;color:#23272b;font-size:17px;line-height:1.6">
    <p style="color:#8a6728;font-size:14px;margin:0 0 8px">Kurzlinks · ${esc(werkzeug)}</p>
    <p style="font-size:20px;margin:0 0 16px"><strong>Ein Kurzlink zeigt auf eine neue Domain.</strong></p>
    <p style="margin:0">Domain: ${esc(domain)}</p>
    <p style="margin:0">Code: ${esc(code || "–")}</p>
    <p style="margin:0 0 16px;word-break:break-all">Ziel: ${esc(ziel)}</p>
    <p>Ist das in Ordnung, ist nichts zu tun. Sonst den Kurzlink im ${esc(werkzeug)} löschen – er landet im Archiv und lässt sich zurückholen.</p>
  </div></body></html>`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${mc.resend_api_key}` },
    body: JSON.stringify({ from: mc.absender, to: [kc.empfaenger], subject: "Kurzlink auf neue Domain: " + domain, html }),
  });
  if (!r.ok) { console.error("resend", r.status, await r.text()); return new Response(JSON.stringify({ ok: false }), { status: 200 }); }
  return new Response(JSON.stringify({ ok: true }), { status: 200 });
});
