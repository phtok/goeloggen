// =============================================================================
// go · Supabase Edge Function — Kurzlink-Weiterleitung mit Scan-Zählung
// Öffentlicher Redirect: /go/<code> (oder ?c=<code>) → 302 auf die hinterlegte
// URL. Aufgelöst wird über die RPC kurzlink_aufloesen (nur service_role): sie
// liest BEIDE Register — public.sommer2026_links (Kampagne) und public.qr_links
// (QR-Generator) — und zählt den Aufruf in public.link_hits (nur Zeitpunkt +
// Code, keine Personendaten). Ein Rundgang, der Redirect bleibt gleich schnell.
// Kein API-Key nötig (öffentliche Weiterleitung).
//
// Fällt ein Code ins Leere, geht es freundlich auf die Übersichts-Landingpage.
// Schema: services/qr-generator/schema.sql (Migration «qr_links_und_scans»).
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const FALLBACK = "https://global-sommer2026.goetheanum.online";

function redirect(to: string): Response {
  return new Response(null, { status: 302, headers: { Location: to, "Cache-Control": "no-store" } });
}

Deno.serve(async (req) => {
  const u = new URL(req.url);
  // Code aus dem letzten Pfadsegment (…/go/<code>) oder aus ?c=.
  const seg = u.pathname.split("/").filter(Boolean).pop() || "";
  const code = (u.searchParams.get("c") || (seg && seg !== "go" ? seg : "")).trim();
  if (!code) return redirect(FALLBACK);

  const target = await fetch(`${SB}/rest/v1/rpc/kurzlink_aufloesen`, {
    method: "POST",
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ p_code: code }),
  }).then((r) => r.json()).catch(() => null);

  return redirect(typeof target === "string" && target ? target : FALLBACK);
});
