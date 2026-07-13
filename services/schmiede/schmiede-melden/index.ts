// =============================================================================
// schmiede-melden · Supabase Edge Function (Info-Ping der Werkzeug-Schmiede)
// Vorbild: services/lead-agent/lead-fang/index.ts (Resend + Config-Tabelle).
//
// Aufruf: POST { titel, key }  – ausgelöst von schmiede_auftrag_anlegen()
// über net.http_post. Prüft key gegen schmiede_config.melde_key und schickt
// EINE kurze Info-Mail an schmiede_config.empfaenger: „etwas Neues ist da".
// Absender + Resend-Key liegen in marketing_config (wie beim Lead-Agent),
// nie im Repo. Der Inhalt des Wunsches steht NICHT in der Mail – der wohnt
// im Cockpit hinter dem Schlüssel (Zweckbindung).
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

  const sc = await configVon("schmiede_config");
  // Gemeinsames Geheimnis DB ⇄ Function – kein offener Trigger.
  if (!sc.melde_key || String(body.key ?? "") !== sc.melde_key) {
    return new Response("nein", { status: 403 });
  }

  const mc = await configVon("marketing_config");   // resend_api_key + absender (schon gesetzt)
  const empfaenger = sc.empfaenger || "";
  if (!mc.resend_api_key || !mc.absender || !empfaenger) {
    // Nichts konfiguriert: still ok, damit der Insert nicht als Fehler erscheint.
    return new Response(JSON.stringify({ ok: false, grund: "unkonfiguriert" }), { status: 200 });
  }

  const titel = String(body.titel ?? "ohne Namen").slice(0, 140);
  const cockpit = sc.cockpit_url || "https://werkzeuge.goetheanum.ch/apps/schmiede-eingang/";
  const html = `<!doctype html><html lang="de-CH"><body style="margin:0;background:#faf8f4">
  <div style="max-width:520px;margin:0 auto;padding:32px 20px;font-family:Georgia,serif;color:#23272b;font-size:17px;line-height:1.6">
    <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">Werkzeug-Schmiede</p>
    <p style="font-size:20px;margin:0 0 16px"><strong>Ein neuer Wunsch ist da.</strong></p>
    <p>Titel: ${esc(titel)}</p>
    <p style="margin:24px 0"><a href="${esc(cockpit)}" style="background:#0061a9;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;display:inline-block">Im Cockpit ansehen</a></p>
    <p style="font-size:13px;color:#6b7177">Der Inhalt steht im Cockpit hinter dem Schlüssel – nicht in dieser Mail.</p>
  </div></body></html>`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${mc.resend_api_key}` },
    body: JSON.stringify({ from: mc.absender, to: [empfaenger], subject: "Neuer Wunsch: " + titel, html }),
  });
  if (!r.ok) { console.error("resend", r.status, await r.text()); return new Response(JSON.stringify({ ok: false }), { status: 200 }); }
  return new Response(JSON.stringify({ ok: true }), { status: 200 });
});
