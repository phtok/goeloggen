// =============================================================================
// go · Supabase Edge Function — Kurzlink-Weiterleitung
// Öffentlicher Redirect: /go/<code> (oder ?c=<code>) → 302 auf die volle UTM-URL
// aus public.sommer2026_links. So bleiben veröffentlichte Links kurz und
// aufgeräumt; die UTM-Parameter reisen erst beim Redirect mit (302 auf die
// Landingpage inkl. ?utm_*). Kein API-Key nötig (öffentliche Weiterleitung).
//
// Fällt ein Code ins Leere, geht es freundlich auf die Übersichts-Landingpage.
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

  const rows = await fetch(
    `${SB}/rest/v1/sommer2026_links?code=eq.${encodeURIComponent(code)}&select=url&limit=1`,
    { headers: { apikey: KEY, Authorization: `Bearer ${KEY}` } },
  ).then((r) => r.json()).catch(() => []);

  const target = Array.isArray(rows) && rows[0] && typeof rows[0].url === "string" ? rows[0].url : "";
  return redirect(target || FALLBACK);
});
