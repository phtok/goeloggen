// =============================================================================
// seelenkalender · Supabase Edge Function (Lead-Schleife 1B)
// Vier Wege über ?aktion= :
//   anmelden    POST {email, sprache?, utm?, website?}  → Double-Opt-in-Mail
//   bestaetigen GET  ?t=<token>                         → Status aktiv
//   ende        GET  ?t=<token>                         → Status beendet (1 Klick)
//   versand     GET/POST ?key=<versand_key>             → Wochenspruch an alle Aktiven
//
// Versand über Resend (API-Key in seelenkalender_config, nie im Repo).
// Grundsätze: kein Nutzer-Enumerieren (Antwort immer gleich), Honeypot-Feld
// «website», Zweckbindung (E-Mail nur für den Versand), Ein-Klick-Abmeldung,
// List-Unsubscribe-Header. Woche 1 = Osterwoche (Gauss-Formel, wie Frontend).
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };
const FUNKTION_URL = `${SB}/functions/v1/seelenkalender`;

const EMAIL_RE = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function tokenNeu(): string {
  const b = new Uint8Array(24); crypto.getRandomValues(b);
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function config(): Promise<Record<string, string>> {
  const r = await fetch(`${SB}/rest/v1/seelenkalender_config?select=key,value`, { headers: H });
  const rows = await r.json();
  const c: Record<string, string> = {};
  for (const row of rows) c[row.key] = row.value;
  return c;
}

// --- Woche (Ostern nach Gauss, Woche 1 = Osterwoche) -------------------------
function ostern(j: number): Date {
  const a = j % 19, b = Math.floor(j / 100), c = j % 100, d = Math.floor(b / 4), e = b % 4,
    f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3),
    h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4,
    l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451),
    mo = Math.floor((h + l - 7 * m + 114) / 31), ta = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(Date.UTC(j, mo - 1, ta, 12));
}
function wocheJetzt(): { jahr: number; nr: number } {
  const heute = new Date();
  let o = ostern(heute.getUTCFullYear());
  if (heute < o) o = ostern(heute.getUTCFullYear() - 1);
  const w = Math.floor((heute.getTime() - o.getTime()) / (7 * 24 * 3600 * 1000)) + 1;
  return { jahr: o.getUTCFullYear(), nr: Math.min(Math.max(w, 1), 52) };
}

// --- Mail-Bausteine (schlicht, textnah — Mail-Clients laden keine Hausschrift)
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function mailHtml(inhalt: string, fussHtml: string): string {
  return `<!doctype html><html lang="de"><body style="margin:0;padding:0;background:#faf8f4">
  <div style="max-width:560px;margin:0 auto;padding:32px 20px;font-family:Georgia,'Times New Roman',serif;color:#23272b;font-size:17px;line-height:1.65">
  ${inhalt}
  <hr style="border:none;border-top:1px solid #d9d4c9;margin:32px 0 16px">
  <p style="font-size:13px;color:#6b7177;line-height:1.6">${fussHtml}</p>
  </div></body></html>`;
}

async function resendBatch(cfg: Record<string, string>, mails: unknown[]): Promise<number> {
  let fehler = 0;
  for (let i = 0; i < mails.length; i += 100) {
    const teil = mails.slice(i, i + 100);
    const r = await fetch("https://api.resend.com/emails/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${cfg.resend_api_key}` },
      body: JSON.stringify(teil),
    });
    if (!r.ok) { fehler += teil.length; console.error("resend", r.status, await r.text()); }
    if (i + 100 < mails.length) await new Promise((res) => setTimeout(res, 600));
  }
  return fehler;
}

// --- Aktionen ----------------------------------------------------------------
async function anmelden(req: Request, cfg: Record<string, string>): Promise<Response> {
  const ok = new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { return ok; }
  const email = String(body.email ?? "").trim().toLowerCase();
  const honeypot = String(body.website ?? "");
  if (honeypot !== "" || !EMAIL_RE.test(email) || email.length > 200) return ok; // still, kein Enumerieren
  const sprache = body.sprache === "en" ? "en" : "de";
  const hash = await sha256Hex(cfg.hash_salt + email);
  const token = tokenNeu();
  const herkunft = (body.utm && typeof body.utm === "object") ? body.utm : null;

  // Upsert über email_hash; Wiederanmeldung nach Abmeldung erlaubt.
  const up = await fetch(`${SB}/rest/v1/seelenkalender_abo?on_conflict=email_hash`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=representation" },
    body: JSON.stringify([{ email, email_hash: hash, sprache, status: "angemeldet", token, herkunft, beendet_am: null }]),
  });
  if (!up.ok) { console.error("upsert", up.status, await up.text()); return ok; }
  const row = (await up.json())[0];
  if (row?.status === "aktiv") return ok; // schon dabei — keine zweite Mail

  const bestaetigen = `${FUNKTION_URL}?aktion=bestaetigen&t=${row?.token ?? token}`;
  const inhalt = `
    <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">Seelenkalender – Das Goetheanum</p>
    <p style="font-size:20px;margin:0 0 16px"><strong>Nur noch ein Schritt.</strong></p>
    <p>Damit der Wochenspruch Sie erreicht, bestätigen Sie bitte Ihre Anmeldung:</p>
    <p style="margin:24px 0"><a href="${bestaetigen}" style="background:#0061a9;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;display:inline-block">Anmeldung bestätigen</a></p>
    <p>Kein Wunsch von Ihnen? Dann lassen Sie diese Nachricht einfach unbeantwortet — es geschieht nichts weiter.</p>`;
  const fuss = `Sie erhalten diese Nachricht, weil diese Adresse auf werkzeuge.goetheanum.ch/apps/seelenkalender eingetragen wurde.`;
  const fehler = await resendBatch(cfg, [{
    from: cfg.absender, to: [email],
    subject: "Bitte bestätigen: der Wochenspruch",
    html: mailHtml(inhalt, fuss),
  }]);
  if (fehler) console.error("bestaetigungs-mail fehlgeschlagen");
  return ok;
}

async function statusPerToken(t: string, neu: "aktiv" | "beendet", cfg: Record<string, string>): Promise<Response> {
  const ziel = cfg.seite_url || "https://werkzeuge.goetheanum.ch/apps/seelenkalender/";
  if (!/^[0-9a-f]{48}$/.test(t)) return Response.redirect(ziel + "#fehler", 303);
  const patch: Record<string, unknown> = { status: neu };
  if (neu === "aktiv") patch.bestaetigt_am = new Date().toISOString();
  else patch.beendet_am = new Date().toISOString();
  const r = await fetch(`${SB}/rest/v1/seelenkalender_abo?token=eq.${t}`, {
    method: "PATCH", headers: { ...H, Prefer: "return=representation" }, body: JSON.stringify(patch),
  });
  const rows = r.ok ? await r.json() : [];
  const anker = rows.length ? (neu === "aktiv" ? "#bestaetigt" : "#beendet") : "#fehler";
  return Response.redirect(ziel + anker, 303);
}

async function versand(url: URL, cfg: Record<string, string>): Promise<Response> {
  if (!cfg.versand_key || url.searchParams.get("key") !== cfg.versand_key) {
    return new Response("nein", { status: 403 });
  }
  if (!cfg.resend_api_key) return new Response(JSON.stringify({ ok: false, grund: "resend_api_key fehlt" }), { status: 200 });

  const { jahr, nr } = wocheJetzt();
  // Schon versandt? (eine Zeile je jahr+woche)
  const log = await fetch(`${SB}/rest/v1/seelenkalender_versand?jahr=eq.${jahr}&woche=eq.${nr}&select=id`, { headers: H });
  if ((await log.json()).length) return new Response(JSON.stringify({ ok: true, uebersprungen: true, woche: nr }), { status: 200 });

  const vr = await fetch(`${SB}/rest/v1/seelenkalender_sprueche?nr=eq.${nr}&select=vers,stimmung`, { headers: H });
  const spruch = (await vr.json())[0];
  if (!spruch) return new Response(JSON.stringify({ ok: false, grund: "spruch fehlt" }), { status: 500 });

  const ar = await fetch(`${SB}/rest/v1/seelenkalender_abo?status=eq.aktiv&select=email,token`, { headers: H });
  const abos: { email: string; token: string }[] = await ar.json();

  // Vertiefung im Wechsel: gerade Woche → goetheanum.tv, ungerade → Wochenschrift
  const utm = `utm_source=seelenkalender&utm_medium=email&utm_campaign=evergreen&utm_content=vers_${String(nr).padStart(2, "0")}`;
  const tiefe = nr % 2 === 0
    ? { url: `https://goetheanum.tv/?${utm}`, text: "Zur Vertiefung auf goetheanum.tv" }
    : { url: `https://dasgoetheanum.com/?${utm}`, text: "Zur Vertiefung in der Wochenschrift" };

  const versHtml = esc(spruch.vers).replace(/\n/g, "<br>");
  const stim = spruch.stimmung ? ` · ${esc(spruch.stimmung)}` : "";
  const mails = abos.map((a) => {
    const ende = `${FUNKTION_URL}?aktion=ende&t=${a.token}`;
    const inhalt = `
      <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">Seelenkalender · ${nr}. Woche${stim}</p>
      <blockquote style="margin:20px 0;padding:0;border:none;font-size:19px;line-height:1.7">${versHtml}</blockquote>
      <p style="color:#6b7177;font-size:14px;margin:0 0 24px">Rudolf Steiner · Anthroposophischer Seelenkalender</p>
      <p><a href="${tiefe.url}" style="color:#0061a9">${tiefe.text} →</a></p>`;
    const fuss = `Wöchentlicher Gruss des Goetheanum. <a href="${ende}" style="color:#6b7177">Abmelden mit einem Klick</a> — ohne Rückfrage, ohne Umweg.`;
    return {
      from: cfg.absender, to: [a.email],
      subject: `${nr}. Woche — der Spruch`,
      html: mailHtml(inhalt, fuss),
      headers: { "List-Unsubscribe": `<${ende}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
    };
  });

  const fehler = abos.length ? await resendBatch(cfg, mails) : 0;
  await fetch(`${SB}/rest/v1/seelenkalender_versand`, {
    method: "POST", headers: H,
    body: JSON.stringify([{ jahr, woche: nr, empfaenger: abos.length - fehler, fehler }]),
  });
  return new Response(JSON.stringify({ ok: true, woche: nr, empfaenger: abos.length, fehler }), { status: 200 });
}

// --- Router --------------------------------------------------------------------
Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  const aktion = url.searchParams.get("aktion") ?? "";
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type" } });
  }
  const cfg = await config();
  try {
    if (aktion === "anmelden" && req.method === "POST") return await anmelden(req, cfg);
    if (aktion === "bestaetigen") return await statusPerToken(url.searchParams.get("t") ?? "", "aktiv", cfg);
    if (aktion === "ende") return await statusPerToken(url.searchParams.get("t") ?? "", "beendet", cfg);
    if (aktion === "versand") return await versand(url, cfg);
  } catch (e) {
    console.error("seelenkalender", aktion, e);
    return new Response("fehler", { status: 500 });
  }
  return new Response("unbekannte aktion", { status: 404 });
});
